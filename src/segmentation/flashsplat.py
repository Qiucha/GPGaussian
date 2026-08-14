import os
import torch
import numpy as np
import cv2
import json
import argparse
import importlib.util

from src.upstream import get_flashsplat_root

_flashsplat_renderer_path = os.path.join(
    get_flashsplat_root(), "gaussian_renderer", "__init__.py"
)
spec = importlib.util.spec_from_file_location("flashsplat_renderer", _flashsplat_renderer_path)
flash_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flash_module)
flashsplat_render = flash_module.flashsplat_render

import torch.nn.functional as F

from src.rendering.checkpoint import load_checkpoint, PipelineParamsNoparse
from src.rendering.camera import get_camera_view

def multi_instance_opt(all_contrib, gamma=0.):
    all_contrib_sum = all_contrib.sum(dim=0)
    all_obj_labels = torch.zeros_like(all_contrib).bool()
    for obj_idx, obj_contrib in enumerate(all_contrib):
        obj_contrib = torch.stack([all_contrib_sum - obj_contrib, obj_contrib], dim=0)
        obj_contrib = F.normalize(obj_contrib, dim=0)
        obj_contrib[0, :] += gamma
        obj_label = torch.argmax(obj_contrib, dim=0)
        all_obj_labels[obj_idx] = obj_label
    return all_obj_labels

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--masks_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--prompts", nargs="+", default=["pot", "trunk", "leaves"])
    args = parser.parse_args()
    
    model_path = args.model_path
    masks_dir = args.masks_dir
    workspace = args.output_dir
    prompts = args.prompts
    
    gaussians = load_checkpoint(model_path)
    pipeline = PipelineParamsNoparse()
    background = torch.tensor([1, 1, 1], dtype=torch.float32, device="cuda")
    
    cameras_json = os.path.join(model_path, "cameras.json")
    with open(cameras_json, "r") as f:
        cameras_data = json.load(f)
        
    num_views = len(cameras_data)
    print(f"Found {num_views} cameras.")
    
    all_counts = None
    obj_num = len(prompts) + 1  # 0=none, 1=pot, 2=trunk, 3=leaves
    
    with torch.no_grad():
        for idx in range(num_views):
            view = get_camera_view(model_path, default_camera_index=idx)
            img_name = f"view_{idx:04d}"
            
            # Load masks
            masks = {}
            for p_idx, prompt in enumerate(prompts):
                mask_path = os.path.join(masks_dir, f"{img_name}_{prompt}.png")
                if os.path.exists(mask_path):
                    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                    if mask is not None:
                        masks[prompt] = mask > 128
                        
            if not masks:
                continue
                
            # Hardcoded Semantic Priority: stem > wooden branch > leaves > pot
            # The prompt later in the list will overwrite the earlier ones in the 2D label map.
            # So the list should be ordered from least priority (bottom) to highest priority (top).
            priority_order = []
            for p in prompts:
                if "pot" in p.lower():
                    priority_order.append(p)
            for p in prompts:
                if "leaves" in p.lower():
                    priority_order.append(p)
            for p in prompts:
                if "wood" in p.lower() or "stem" in p.lower() or "branch" in p.lower() or "trunk" in p.lower():
                    priority_order.append(p)
                    
            # If any prompts were not matched above, append them at the end just in case
            for p in prompts:
                if p not in priority_order:
                    priority_order.append(p)
            
            gt_mask_np = np.zeros((view.image_height, view.image_width), dtype=np.float32)
            for prompt in priority_order:
                if prompt in masks:
                    mask_values = masks[prompt]
                    prompt_idx = prompts.index(prompt) + 1
                    gt_mask_np[mask_values] = prompt_idx
                
            gt_mask = torch.from_numpy(gt_mask_np).cuda()
                    
            # Render and get used_count
            render_pkg = flashsplat_render(view, gaussians, pipeline, background, gt_mask=gt_mask, obj_num=obj_num)
            used_count = render_pkg["used_count"]
            
            if all_counts is None:
                all_counts = used_count
            else:
                all_counts += used_count
                
            if idx % 10 == 0:
                print(f"Processed {idx}/{num_views}")
            
    # FlashSplat LP Optimization
    print("Running FlashSplat optimization...")
    all_obj_labels = multi_instance_opt(all_counts, gamma=0.0)
    
    # Extract labels
    final_labels = torch.zeros(gaussians.get_xyz.shape[0], dtype=torch.int32)
    for obj_idx in range(1, obj_num):
        is_obj = all_obj_labels[obj_idx]
        final_labels[is_obj] = obj_idx
        
    tags_path = os.path.join(workspace, "material_tags.pt")
    torch.save(final_labels, tags_path)
    print(f"Saved {tags_path}")

if __name__ == "__main__":
    main()
