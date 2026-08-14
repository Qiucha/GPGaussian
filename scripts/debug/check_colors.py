import torch
import os
import sys
import numpy as np

physgaussian_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "PhysGaussian"))
sys.path.append(physgaussian_path)
sys.path.append(os.path.join(physgaussian_path, "gaussian-splatting"))

from render_views import load_checkpoint

def sh_to_rgb(sh):
    SH_C0 = 0.28209479177387814
    return sh * SH_C0 + 0.5

def main():
    model_path = "/home/q/Projects/mit/PBL/Phys4DGS/model/ficus_whitebg-trained"
    tags_path = "output/config/material_tags.pt"
    
    gaussians = load_checkpoint(model_path)
    # The base colors are stored in _features_dc
    features_dc = gaussians._features_dc.detach().cpu().numpy()
    rgb = sh_to_rgb(features_dc).squeeze() # Shape (N, 3)
    
    tags = torch.load(tags_path).cpu().numpy()
    
    # Let's look at the plant Gaussians (tags 2 and 3)
    plant_mask = (tags == 2) | (tags == 3)
    plant_rgb = rgb[plant_mask]
    
    print(f"Total plant Gaussians: {len(plant_rgb)}")
    
    # Calculate hue/saturation or just simple RGB rules
    # Brown is usually R > G > B
    # Green is usually G > R and G > B
    
    # Simple check: R > G
    r = plant_rgb[:, 0]
    g = plant_rgb[:, 1]
    b = plant_rgb[:, 2]
    
    is_brown = (r > g) & (r > b) & (g > b)
    is_green = (g > r) & (g > b)
    
    print(f"Number of 'brown' Gaussians (R>G>B): {np.sum(is_brown)}")
    print(f"Number of 'green' Gaussians (G>R & G>B): {np.sum(is_green)}")
    print(f"Unclassified plant Gaussians: {len(plant_rgb) - np.sum(is_brown) - np.sum(is_green)}")

if __name__ == "__main__":
    main()
