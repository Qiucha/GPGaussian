import sys
import os
import torch
import torchvision
import numpy as np
import json
from PIL import Image

physgaussian_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "PhysGaussian"))
sys.path.append(physgaussian_path)
sys.path.append(os.path.join(physgaussian_path, "gaussian-splatting"))

from render_views import load_checkpoint, PipelineParamsNoparse
from utils.camera_view_utils import get_camera_view
from plyfile import PlyData

def main():
    model_path = "/home/q/Projects/mit/PBL/Phys4DGS/model/ficus_whitebg-trained"
    gaussians = load_checkpoint(model_path)
    points = gaussians.get_xyz.detach().cpu().numpy()
    
    view = get_camera_view(model_path, default_camera_index=0)
    
    W2C = view.world_view_transform.transpose(0, 1).cpu().numpy()
    K = view.projection_matrix.transpose(0, 1).cpu().numpy()
    full_proj = view.full_proj_transform.transpose(0, 1).cpu().numpy()
    width = view.image_width
    height = view.image_height
    
    pts_h = np.hstack((points, np.ones((len(points), 1))))
    
    # Method 1: W2C then K
    pts_c = (W2C @ pts_h.T).T
    pts_ndc_h = (K @ pts_c.T).T
    pts_ndc = pts_ndc_h[:, :3] / pts_ndc_h[:, 3:]
    pts_2d_1 = np.zeros((len(points), 2))
    pts_2d_1[:, 0] = (pts_ndc[:, 0] + 1.0) * width * 0.5
    pts_2d_1[:, 1] = (1.0 - pts_ndc[:, 1]) * height * 0.5 
    
    # Method 2: full_proj
    pts_ndc_h2 = (full_proj @ pts_h.T).T
    pts_ndc2 = pts_ndc_h2[:, :3] / pts_ndc_h2[:, 3:]
    pts_2d_2 = np.zeros((len(points), 2))
    pts_2d_2[:, 0] = (pts_ndc2[:, 0] + 1.0) * width * 0.5
    pts_2d_2[:, 1] = (1.0 - pts_ndc2[:, 1]) * height * 0.5 

    print("Error between Method 1 and Method 2:", np.max(np.abs(pts_2d_1 - pts_2d_2)))

    # Draw pts on image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    valid_depth = pts_c[:, 2] > 0
    u = np.round(pts_2d_1[:, 0]).astype(int)
    v = np.round(pts_2d_1[:, 1]).astype(int)
    
    valid_uv = (u >= 0) & (u < width) & (v >= 0) & (v < height)
    valid = valid_depth & valid_uv
    
    img[v[valid], u[valid]] = [255, 255, 255]
    Image.fromarray(img).save("output/config/test_proj.png")
    print("Saved test_proj.png")

if __name__ == "__main__":
    main()
