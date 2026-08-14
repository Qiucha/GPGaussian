import sys
import os
import torch
import torchvision
import argparse

# Add PhysGaussian path to import its modules

from src.rendering.camera import get_camera_view
import src  # noqa: F401
from scene.gaussian_model import GaussianModel
from gaussian_renderer import render
from utils.system_utils import searchForMaxIteration
from utils.graphics_utils import focal2fov

class PipelineParamsNoparse:
    def __init__(self):
        self.convert_SHs_python = False
        self.compute_cov3D_python = False
        self.debug = False

def load_checkpoint(model_path, sh_degree=3, iteration=-1):
    checkpt_dir = os.path.join(model_path, "point_cloud")
    if iteration == -1:
        iteration = searchForMaxIteration(checkpt_dir)
    checkpt_path = os.path.join(
        checkpt_dir, f"iteration_{iteration}", "point_cloud.ply"
    )
    gaussians = GaussianModel(sh_degree)
    gaussians.load_ply(checkpt_path)
    return gaussians

def render_first_frame(model_path, output_image_path):
    print(f"Loading Gaussian model from {model_path}...")
    gaussians = load_checkpoint(model_path)
    
    print("Loading camera view...")
    # This gets the 0-th camera from cameras.json
    view = get_camera_view(model_path, default_camera_index=0)
    
    pipeline = PipelineParamsNoparse()
    pipeline.compute_cov3D_python = True
    background = torch.tensor([0, 0, 0], dtype=torch.float32, device="cuda")
    
    print("Rendering...")
    with torch.no_grad():
        rendering = render(view, gaussians, pipeline, background)["render"]
    
    # Save image
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    torchvision.utils.save_image(rendering, output_image_path)
    print(f"Saved rendered frame to {output_image_path}")
    
    # Extract camera parameters to pass to projection
    camera_params = {
        "width": view.image_width,
        "height": view.image_height,
        "W2C": view.world_view_transform.transpose(0, 1).cpu().numpy(),
        "K": view.projection_matrix.transpose(0, 1).cpu().numpy() # This is a full projection matrix (NDC), we might need to adapt projection.py
    }
    
    return camera_params, view

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    render_first_frame(args.model_path, args.output)
