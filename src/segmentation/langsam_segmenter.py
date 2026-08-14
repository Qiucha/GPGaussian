import os
import cv2
import numpy as np
import torch
from PIL import Image

try:
    from lang_sam import LangSAM
except ImportError:
    LangSAM = None
    print("Warning: lang_sam is not installed. Please install it using 'pip install lang-sam' to use text-prompted SAM.")

class Segmenter2D:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        if LangSAM is not None:
            # LangSAM uses groundingDINO and SAM
            self.model = LangSAM()
        else:
            self.model = None

    def segment_image(self, image_path: str, text_prompts: list, box_threshold=0.3, text_threshold=0.25):
        image_pil = Image.open(image_path).convert("RGB")
        masks_dict = {}
        
        for prompt in text_prompts:
            if self.model is None:
                masks_dict[prompt] = np.zeros((image_pil.height, image_pil.width), dtype=bool)
                continue
                
            # lang_sam 0.2.1 expects lists (some versions take single objects, we will use the single object predict if available)
            try:
                results = self.model.predict(image_pil, prompt, box_threshold=box_threshold, text_threshold=text_threshold)
                if isinstance(results, tuple):
                    masks, _, _, _ = results
                else:
                    masks = results.get("masks", [])
            except:
                results = self.model.predict([image_pil], [prompt], box_threshold=box_threshold, text_threshold=text_threshold)
                result = results[0]
                masks = result.get("masks", [])
            
            if len(masks) > 0:
                # Combine all detected masks (N, H, W) into a single (H, W) boolean mask
                if isinstance(masks, list):
                    masks = np.array(masks)
                mask = np.any(masks, axis=0)
                masks_dict[prompt] = mask.astype(bool)
            else:
                masks_dict[prompt] = np.zeros((image_pil.height, image_pil.width), dtype=bool)
                
        return masks_dict


    def process_directory(self, input_dir: str, output_dir: str, text_prompts: list):
        """
        Process a directory of images and save the resulting masks.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        valid_exts = {".jpg", ".jpeg", ".png"}
        
        for filename in os.listdir(input_dir):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in valid_exts:
                continue
                
            image_path = os.path.join(input_dir, filename)
            print(f"Segmenting {image_path}...")
            
            masks = self.segment_image(image_path, text_prompts)
            
            base_name = os.path.splitext(filename)[0]
            
            for prompt, mask in masks.items():
                if not mask.any():
                    continue
                
                # Save mask as grayscale image
                mask_image = (mask * 255).astype(np.uint8)
                
                out_name = f"{base_name}_{prompt}.png"
                out_path = os.path.join(output_dir, out_name)
                cv2.imwrite(out_path, mask_image)
                
        print(f"Segmentation completed. Masks saved to {output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--prompts", nargs="+", required=True)
    args = parser.parse_args()
    
    segmenter = Segmenter2D()
    segmenter.process_directory(args.input_dir, args.output_dir, args.prompts)
