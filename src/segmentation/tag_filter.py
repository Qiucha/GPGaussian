import torch
import argparse
import sys
import os
import numpy as np
from sklearn.cluster import DBSCAN

# Add PhysGaussian path to import its modules

from src.rendering.checkpoint import load_checkpoint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--tags_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--target_tag", type=int, default=2)
    parser.add_argument("--eps", type=float, default=0.1)
    parser.add_argument("--min_samples", type=int, default=5)
    args = parser.parse_args()

    print(f"Loading model from {args.model_path}")
    gaussians = load_checkpoint(args.model_path)
    xyz = gaussians.get_xyz.detach().cpu().numpy()
    
    print(f"Loading tags from {args.tags_path}")
    tags = torch.load(args.tags_path).cpu().numpy()
    
    target_mask = (tags == args.target_tag)
    target_indices = np.where(target_mask)[0]
    
    print(f"Found {len(target_indices)} points with tag {args.target_tag}.")
    
    if len(target_indices) == 0:
        print("No points found. Saving original tags.")
        torch.save(torch.from_numpy(tags), args.output_path)
        return
        
    target_xyz = xyz[target_indices]
    
    # Run DBSCAN
    clustering = DBSCAN(eps=args.eps, min_samples=args.min_samples).fit(target_xyz)
    labels = clustering.labels_
    
    unique_labels, counts = np.unique(labels, return_counts=True)
    print(f"DBSCAN found {len(unique_labels)} clusters (including noise as -1).")
    
    # Find largest non-noise cluster
    best_cluster_id = -1
    best_cluster_size = 0
    
    for l, c in zip(unique_labels, counts):
        if l == -1:
            print(f"  Noise points (-1): {c}")
            continue
        print(f"  Cluster {l}: {c} points")
        if c > best_cluster_size:
            best_cluster_size = c
            best_cluster_id = l
            
    if best_cluster_id == -1:
        print("No valid clusters found (all noise)! Reassigning all to leaves (3).")
        tags[target_indices] = 3
    else:
        print(f"Selecting cluster {best_cluster_id} as the true trunk.")
        # Reassign outliers to leaves (3)
        for i, idx in enumerate(target_indices):
            if labels[i] != best_cluster_id:
                tags[idx] = 3
                
    out_tensor = torch.from_numpy(tags)
    torch.save(out_tensor, args.output_path)
    print(f"Saved filtered tags to {args.output_path}")
    
    # Print new distribution
    unique, new_counts = np.unique(tags, return_counts=True)
    print(f"New tags distribution:")
    for u, c in zip(unique, new_counts):
        print(f"  Tag {u}: {c}")

if __name__ == "__main__":
    main()
