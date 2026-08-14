import sys
import os
import cv2  # Import cv2 before torch to fix libtiff/libjpeg symbol conflict
import torch
import torchvision
import argparse
import json

from src.rendering.camera import get_camera_view
from src.rendering.checkpoint import load_checkpoint, PipelineParamsNoparse
import src  # noqa: F401
from gaussian_renderer import render


def render_views(model_path, output_dir, skip_rendering=False):
    """
    Renders all available views from cameras.json in model_path.
    Returns a dictionary of camera parameters for each view.
    """
    print(f"Loading Gaussian model from {model_path}...")
    gaussians = None
    if not skip_rendering:
        gaussians = load_checkpoint(model_path)

    # Check how many cameras are in cameras.json
    cam_path = os.path.join(model_path, "cameras.json")
    with open(cam_path) as f:
        data = json.load(f)
    num_cameras = len(data)
    print(f"Found {num_cameras} cameras in cameras.json")

    pipeline = PipelineParamsNoparse()
    pipeline.compute_cov3D_python = True
    background = torch.tensor([0, 0, 0], dtype=torch.float32, device="cuda")

    os.makedirs(output_dir, exist_ok=True)

    camera_params_dict = {}

    if skip_rendering:
        print("Skipping actual rendering, only extracting camera parameters...")
    else:
        print("Rendering views...")

    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float32)
    with torch.no_grad():
        for i in range(num_cameras):
            view = get_camera_view(model_path, default_camera_index=i)

            # Explicitly cast to float32 because other modules (like lang_sam) might set default dtype to bfloat16
            view.world_view_transform = view.world_view_transform.float()
            view.projection_matrix = view.projection_matrix.float()
            view.full_proj_transform = view.full_proj_transform.float()
            view.camera_center = view.camera_center.float()

            image_name = f"view_{i:04d}.png"

            if not skip_rendering:
                rendering = render(view, gaussians, pipeline, background)["render"]
                output_image_path = os.path.join(output_dir, image_name)
                torchvision.utils.save_image(rendering, output_image_path)

            # Extract camera parameters to pass to projection
            camera_params_dict[image_name] = {
                "width": view.image_width,
                "height": view.image_height,
                "W2C": view.world_view_transform.transpose(0, 1).cpu().numpy(),
                "K": view.projection_matrix.transpose(0, 1).cpu().numpy(),  # 4x4 NDC projection matrix
            }

    if not skip_rendering:
        print(f"Saved {num_cameras} rendered frames to {output_dir}")

    torch.set_default_dtype(old_dtype)
    return camera_params_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()
    render_views(args.model_path, args.output_dir)
