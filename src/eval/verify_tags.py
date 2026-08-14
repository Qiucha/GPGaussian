import sys
import os
import torch
import torchvision
import argparse

# Add PhysGaussian path to import its modules

from src.rendering.checkpoint import load_checkpoint, PipelineParamsNoparse
import src  # noqa: F401
from src.rendering.camera import get_camera_view
from gaussian_renderer import render

def color_to_sh(color):
    C0 = 0.28209479177387814
    return (torch.tensor(color) - 0.5) / C0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--tags_path", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading model from {args.model_path}")
    gaussians = load_checkpoint(args.model_path)
    
    print(f"Loading tags from {args.tags_path}")
    tags = torch.load(args.tags_path).cuda()
    
    shs = gaussians.get_features
    # Zero out higher order SH to just show base color
    shs[:, 1:, :] = 0.0
    
    # 0 = none -> Gray
    # 1 = pot -> Blue
    # 2 = trunk -> Red
    # 3 = leaves -> Green
    colors = {
        0: [0.5, 0.5, 0.5],
        1: [0.0, 0.0, 1.0],
        2: [1.0, 0.0, 0.0],
        3: [0.0, 1.0, 0.0]
    }
    
    for tag_id, color in colors.items():
        mask = (tags == tag_id)
        if mask.sum() > 0:
            shs[mask, 0, :] = color_to_sh(color).cuda()
            
    # Update the features
    gaussians._features_dc = shs[:, 0:1, :]
    gaussians._features_rest = shs[:, 1:, :]

    pipeline = PipelineParamsNoparse()
    pipeline.compute_cov3D_python = True
    background = torch.tensor([0, 0, 0], dtype=torch.float32, device="cuda")

    print(f"Rendering first 5 views...")
    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float32)
    
    with torch.no_grad():
        for i in range(5):
            view = get_camera_view(args.model_path, default_camera_index=i)
            
            view.world_view_transform = view.world_view_transform.float()
            view.projection_matrix = view.projection_matrix.float()
            view.full_proj_transform = view.full_proj_transform.float()
            view.camera_center = view.camera_center.float()
            
            rendering = render(view, gaussians, pipeline, background)["render"]
            
            image_name = f"view_{i:04d}.png"
            output_image_path = os.path.join(args.output_dir, image_name)
            torchvision.utils.save_image(rendering, output_image_path)
            print(f"Saved {output_image_path}")
            
    torch.set_default_dtype(old_dtype)

if __name__ == "__main__":
    main()
