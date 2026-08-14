import cv2
import torch
import torchvision
import os
import sys

from src.rendering.checkpoint import load_checkpoint, PipelineParamsNoparse
import src  # noqa: F401
from src.rendering.camera import get_camera_view
from gaussian_renderer import render

def rgb_to_sh(rgb):
    SH_C0 = 0.28209479177387814
    return (rgb - 0.5) / SH_C0

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to the model directory")
    parser.add_argument("--tags_path", type=str, required=True, help="Path to input tags file")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save rendered image")
    args = parser.parse_args()

    model_path = args.model_path
    tags_path = args.tags_path
    output_path = args.output_path
    
    print("Loading model and tags...")
    gaussians = load_checkpoint(model_path)
    tags = torch.load(tags_path).cuda()
    
    colors = torch.zeros((gaussians.get_xyz.shape[0], 3), device="cuda", dtype=torch.float32)
    colors[tags == 1] = torch.tensor([0.0, 0.0, 1.0], device="cuda") # Pot: Blue
    colors[tags == 2] = torch.tensor([1.0, 0.0, 0.0], device="cuda") # Trunk: Red
    colors[tags == 3] = torch.tensor([0.0, 1.0, 0.0], device="cuda") # Leaves: Green
    colors[tags == 0] = torch.tensor([0.0, 0.0, 0.0], device="cuda") # Bg: Black
    
    sh = rgb_to_sh(colors).unsqueeze(1)
    gaussians._features_dc = torch.nn.Parameter(sh.contiguous())
    gaussians._features_rest = torch.nn.Parameter(torch.zeros_like(gaussians._features_rest))
    
    pipeline = PipelineParamsNoparse()
    pipeline.compute_cov3D_python = True
    background = torch.tensor([0, 0, 0], dtype=torch.float32, device="cuda")
    
    print("Rendering View 0 with solid colors...")
    view = get_camera_view(model_path, default_camera_index=0)
    view.world_view_transform = view.world_view_transform.float()
    view.projection_matrix = view.projection_matrix.float()
    view.full_proj_transform = view.full_proj_transform.float()
    view.camera_center = view.camera_center.float()
    
    rendering = render(view, gaussians, pipeline, background)["render"]
    
    torchvision.utils.save_image(rendering, output_path)
    print(f"Saved tag verification image to {output_path}")

if __name__ == "__main__":
    main()
