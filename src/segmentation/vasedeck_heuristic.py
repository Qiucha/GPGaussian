import torch
import argparse
import os
import numpy as np

from src.rendering.checkpoint import load_checkpoint
from src.segmentation.heuristics import sh_dc_to_rgb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--output_path", required=True)
    args = parser.parse_args()

    model_path = args.model_path
    out_tags_path = args.output_path
    os.makedirs(os.path.dirname(out_tags_path), exist_ok=True)

    gaussians = load_checkpoint(model_path)

    xyz = gaussians._xyz.detach().cpu().numpy()
    features_dc = gaussians._features_dc.detach().cpu()
    rgb = sh_dc_to_rgb(features_dc).numpy().squeeze()  # Shape (N, 3)

    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    y = xyz[:, 1]  # y is usually down

    tags = np.zeros(xyz.shape[0], dtype=np.int32)

    # 0 = Unassigned/Background
    # 1 = Vase (White)
    # 2 = Deck (Brown)
    # 3 = Flowers/Leaves (Red/Green)

    is_brown = (r > g) & (g > b) & (r - b > 0.1)
    is_green = (g > r) & (g > b)
    is_red = (r > g) & (r > b) & (~is_brown)
    is_plant = is_green | is_red

    is_white = (r > 0.5) & (g > 0.5) & (b > 0.5) & (np.abs(r - g) < 0.15) & (np.abs(g - b) < 0.15)

    y_deck = np.percentile(y, 80)
    y_flowers = np.percentile(y, 30)

    tags[is_white] = 1
    tags[is_brown | (y > y_deck)] = 2
    tags[is_plant | (y < y_flowers)] = 3

    tags[(tags != 2) & (y > y_deck + 0.5)] = 2
    tags[(tags != 3) & (y < y_flowers - 0.5)] = 3

    num_vase = np.sum(tags == 1)
    num_deck = np.sum(tags == 2)
    num_flowers = np.sum(tags == 3)
    num_bg = np.sum(tags == 0)

    print(f"Assigned Tags: Vase(1)={num_vase}, Deck(2)={num_deck}, Flowers(3)={num_flowers}, Background(0)={num_bg}")

    out_tensor = torch.from_numpy(tags)
    torch.save(out_tensor, out_tags_path)
    print(f"Saved heuristic tags to {out_tags_path}")


if __name__ == "__main__":
    main()
