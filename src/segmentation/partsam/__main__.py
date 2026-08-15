"""CLI: python -m src.segmentation.partsam --model_path … [--stage surface|clicks|lift]."""
from __future__ import annotations

import argparse
from pathlib import Path

from src.segmentation.partsam.clicks import clicks_json_path, run_stage_clicks
from src.segmentation.partsam.merge import DEFAULT_TAGS_PATH, check_occupancy
from src.segmentation.partsam.surface import run_stage_surface

DEFAULT_OUTPUT_DIR = Path("data/outputs/partsam")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PartSAM Material Tag Tensor producer (three stages)."
    )
    parser.add_argument(
        "--model_path",
        required=True,
        help="Trained 3DGS scene directory (contains point_cloud/) or a checkpoint PLY.",
    )
    parser.add_argument(
        "--output_dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="PartSAM artifacts directory (default: data/outputs/partsam).",
    )
    parser.add_argument(
        "--tags_path",
        default=str(DEFAULT_TAGS_PATH),
        help="Solver-facing Material Tag Tensor (default: data/outputs/tags/material_tags.pt).",
    )
    parser.add_argument(
        "--reuse-tags",
        action="store_true",
        help="Skip Stage 3 when --tags_path already exists.",
    )
    parser.add_argument(
        "--check-occupancy",
        action="store_true",
        help="Exit 0 if tags length is N and every prompted Stage 2 id is occupied; else 1.",
    )
    parser.add_argument(
        "--stage",
        choices=("surface", "clicks", "lift"),
        default=None,
        help="Run one stage. Default runs surface then clicks then lift.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    if args.check_occupancy:
        ok = check_occupancy(
            args.tags_path, args.model_path, clicks_json_path(args.output_dir)
        )
        raise SystemExit(0 if ok else 1)
    from src.segmentation.partsam.infer import run_stage_lift

    stages = (args.stage,) if args.stage else ("surface", "clicks", "lift")
    for stage in stages:
        if stage == "surface":
            run_stage_surface(args.model_path, args.output_dir)
        elif stage == "clicks":
            run_stage_clicks(args.model_path, args.output_dir)
        else:
            run_stage_lift(
                args.model_path,
                args.output_dir,
                args.tags_path,
                reuse_tags=args.reuse_tags,
            )


if __name__ == "__main__":
    main()
