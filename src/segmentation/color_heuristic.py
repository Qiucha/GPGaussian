import torch
import os
import sys
import argparse
import numpy as np

from src.rendering.checkpoint import load_checkpoint
from src.segmentation.heuristics import sh_dc_to_rgb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--tags_path", required=True)
    parser.add_argument("--output_path", required=True)
    args = parser.parse_args()

    model_path = args.model_path
    tags_path = args.tags_path
    out_tags_path = args.output_path

    gaussians = load_checkpoint(model_path)

    # Base colors
    features_dc = gaussians._features_dc.detach().cpu()
    rgb = sh_dc_to_rgb(features_dc).numpy().squeeze()  # Shape (N, 3)

    tags = torch.load(tags_path).cpu().numpy()

    # Plant mask (Tags 2 and 3)
    plant_mask = (tags == 2) | (tags == 3)

    r = rgb[:, 0]
    g = rgb[:, 1]
    b = rgb[:, 2]

    # Heuristic for Brown (Wood/Trunk) vs Green (Leaves)
    is_brown = (r > g) & (r > b)
    is_green = (g > r) & (g > b)

    # We want to re-tag the plant Gaussians
    # 1. Reset all plant points to Leaves (3)
    tags[plant_mask] = 3

    # 2. Assign Brown points to Trunk (2)
    trunk_mask = plant_mask & is_brown
    tags[trunk_mask] = 2

    num_trunk = np.sum(trunk_mask)
    num_leaves = np.sum(plant_mask & (~is_brown))
    print(f"Assigned {num_trunk} Gaussians to Trunk and {num_leaves} to Leaves using Color Heuristic!")

    out_tensor = torch.from_numpy(tags)
    torch.save(out_tensor, out_tags_path)
    print(f"Saved color tags to {out_tags_path}")


if __name__ == "__main__":
    main()
