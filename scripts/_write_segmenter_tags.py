#!/usr/bin/env python3
"""Write material_tags.pt for a scene using SegmenterAgent(mock_llm=True)."""

from __future__ import annotations

import argparse
import os
import sys

import torch

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--output_path", required=True)
    args = parser.parse_args()

    from src.rendering.checkpoint import load_checkpoint
    from src.llm.segmenter_agent import SegmenterAgent

    gaussians = load_checkpoint(args.model_path)
    xyz = gaussians._xyz.detach()
    sh_dc = (
        gaussians._features_dc.detach().squeeze(1)
        if gaussians._features_dc.dim() == 3
        else gaussians._features_dc.detach()
    )
    scales = gaussians._scaling.detach()
    agent = SegmenterAgent(mock_llm=True)
    tags, plan = agent.execute_segmentation(
        xyz, sh_dc, scales, object_category=args.category
    )
    os.makedirs(os.path.dirname(os.path.abspath(args.output_path)), exist_ok=True)
    # Runner expects a raw 1-D tag tensor: torch.load(path).to("cuda")
    torch.save(tags.cpu(), args.output_path)
    print(f"Wrote tags ({tags.shape[0]} particles) -> {args.output_path}")
    print(f"Plan scene={getattr(plan, 'scene_name', args.category)}")
    unique, counts = torch.unique(tags, return_counts=True)
    for tag_id, count in zip(unique.tolist(), counts.tolist()):
        print(f"  tag {tag_id}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
