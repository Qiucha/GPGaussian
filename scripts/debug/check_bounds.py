import torch
import os
import sys
import numpy as np

physgaussian_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "PhysGaussian"))
sys.path.append(physgaussian_path)
sys.path.append(os.path.join(physgaussian_path, "gaussian-splatting"))

from render_views import load_checkpoint

def main():
    model_path = "/home/q/Projects/mit/PBL/Phys4DGS/model/ficus_whitebg-trained"
    tags_path = "output/config/material_tags.pt"
    
    gaussians = load_checkpoint(model_path)
    xyz = gaussians.get_xyz.detach().cpu().numpy()
    tags = torch.load(tags_path).cpu().numpy()
    
    for tag_id, tag_name in zip([1, 3], ["Pot", "Leaves"]):
        pts = xyz[tags == tag_id]
        if len(pts) == 0:
            print(f"{tag_name} has 0 points.")
            continue
        min_vals = pts.min(axis=0)
        max_vals = pts.max(axis=0)
        mean_vals = pts.mean(axis=0)
        print(f"--- {tag_name} ---")
        print(f"X: {min_vals[0]:.3f} to {max_vals[0]:.3f} (Mean: {mean_vals[0]:.3f})")
        print(f"Y: {min_vals[1]:.3f} to {max_vals[1]:.3f} (Mean: {mean_vals[1]:.3f})")
        print(f"Z: {min_vals[2]:.3f} to {max_vals[2]:.3f} (Mean: {mean_vals[2]:.3f})")

if __name__ == "__main__":
    main()
