import torch
import os
import sys
import argparse
import numpy as np

from src.rendering.checkpoint import load_checkpoint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to the model directory")
    parser.add_argument("--tags_path", type=str, required=True, help="Path to input tags file")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save heuristic tags file")
    args = parser.parse_args()

    out_tags_path = args.output_path
    gaussians = load_checkpoint(args.model_path)
    xyz = gaussians.get_xyz.detach().cpu().numpy()
    tags = torch.load(args.tags_path).cpu().numpy()

    # Find pot center and bounds
    pot_mask = tags == 1
    if not np.any(pot_mask):
        print("No pot found!")
        return

    pot_pts = xyz[pot_mask]
    pot_center = pot_pts.mean(axis=0)
    pot_z_max = pot_pts[:, 2].max()

    print(f"Pot center: {pot_center}")
    print(f"Pot Z max: {pot_z_max}")

    # We want points that are currently tagged as Leaves (3) or Stem (2)
    plant_mask = (tags == 3) | (tags == 2)

    dx = xyz[:, 0] - pot_center[0]
    dy = xyz[:, 1] - pot_center[1]
    dist_sq = dx**2 + dy**2

    trunk_radius = 0.05

    trunk_mask = plant_mask & (dist_sq < trunk_radius**2) & (xyz[:, 2] > pot_z_max - 0.1) & (xyz[:, 2] < 0.4)

    num_trunk = np.sum(trunk_mask)
    print(f"Found {num_trunk} trunk points via geometric heuristic!")

    tags[tags == 2] = 3  # Reset old trunk points to leaves
    tags[trunk_mask] = 2

    out_tensor = torch.from_numpy(tags)
    torch.save(out_tensor, out_tags_path)
    print(f"Saved heuristic tags to {out_tags_path}")


if __name__ == "__main__":
    main()
