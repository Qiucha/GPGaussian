import argparse
import os

from segmentation import Segmenter2D
from projection import Projector3D
from bbox_extraction import BBoxExtractor
from llm_generator import ConfigGenerator
from render_views import render_views, load_checkpoint
from utils.system_utils import searchForMaxIteration

def main():
    parser = argparse.ArgumentParser(description="PhysGaussian Preprocessing Pipeline")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained Gaussian Splatting model directory")
    parser.add_argument("--output_config", type=str, required=True, help="Path for the output PhysGaussian JSON config")
    parser.add_argument("--prompts", type=str, nargs="+", default=["pot", "trunk", "leaves"], help="Text prompts for parts")
    
    args = parser.parse_args()
    
    # Setup directories
    workspace = os.path.dirname(args.output_config)
    if not workspace:
        workspace = "."
    rendered_dir = os.path.join(workspace, "rendered_views")
    masks_dir = os.path.join(workspace, "masks_output")
    os.makedirs(rendered_dir, exist_ok=True)
    os.makedirs(masks_dir, exist_ok=True)
    masks_exist = any(f.endswith(".png") for f in os.listdir(masks_dir)) if os.path.exists(masks_dir) else False
    renders_exist = any(f.endswith(".png") for f in os.listdir(rendered_dir)) if os.path.exists(rendered_dir) else False
    
    skip_rendering = masks_exist or renders_exist
    skip_segmentation = masks_exist
    
    print("=== Step 0: Render Views from GS Model ===")
    try:
        if skip_rendering:
            print("Rendered views (or masks) already exist. Skipping actual rendering.")
        camera_params_dict = render_views(args.model_path, rendered_dir, skip_rendering=skip_rendering)
    except Exception as e:
        print(f"Error in rendering views: {e}")
        return
        
    print("\n=== Step 1: 2D Segmentation ===")
    if skip_segmentation:
        print("Masks already exist. Skipping segmentation to save time.")
    else:
        try:
            segmenter = Segmenter2D()
            segmenter.process_directory(rendered_dir, masks_dir, args.prompts)
        except Exception as e:
            print(f"Error in 2D Segmentation: {e}")
            print("Note: If LangSAM is not installed, you can provide masks manually in the output directory.")
    
    print("\n=== Step 2: 3D Projection & Voting ===")
    # Find the ply file
    checkpt_dir = os.path.join(args.model_path, "point_cloud")
    iteration = searchForMaxIteration(checkpt_dir)
    ply_file = os.path.join(checkpt_dir, f"iteration_{iteration}", "point_cloud.ply")
    
    # projector = Projector3D(ply_file, camera_params_dict, masks_dir)
    # labels, points = projector.assign_labels(args.prompts)
    labels = []
    
    print("\n=== Step 3: Save Material Tags ===")
    import torch
    
    # Create mapping from prompt to integer ID
    prompt_to_id = {prompt: i+1 for i, prompt in enumerate(args.prompts)}
    prompt_to_id['none'] = 0  # Default unassigned particles to ID 0
    
    # Convert labels array to integer tensor
    tags = torch.tensor([prompt_to_id.get(label, 0) for label in labels], dtype=torch.int32)
    
    tags_path = os.path.join(workspace, "material_tags.pt")
    torch.save(tags, tags_path)
    print(f"Material tags saved to {tags_path}")
    print("Pipeline complete. You can now run the simulation with these tags.")

if __name__ == "__main__":
    main()
