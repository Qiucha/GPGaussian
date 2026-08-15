#!/usr/bin/env python3
"""Evaluate render stability + PSNR/SSIM/LPIPS for an existing frame directory."""

from __future__ import annotations

import argparse
import json
import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.eval.evaluate_realism import (
    assert_expected_frame_count,
    compare_image_pair,
    evaluate_render_directory,
    load_image_rgb,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sim-dir", required=True, help="Directory with %04d.png frames")
    parser.add_argument(
        "--reference-dir",
        default=None,
        help="Optional directory of same-named reference PNGs",
    )
    parser.add_argument(
        "--reference-image",
        default=None,
        help="Optional single reference image compared to the first sim frame",
    )
    parser.add_argument("--expected-frames", type=int, default=None)
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--output", default=None, help="Write JSON report path")
    args = parser.parse_args()

    report = evaluate_render_directory(
        args.sim_dir, reference_dir=args.reference_dir, max_frames=args.max_frames
    )
    if args.expected_frames is not None:
        ok, msg = assert_expected_frame_count(args.sim_dir, args.expected_frames)
        report["expected_frame_count"] = args.expected_frames
        report["frame_count_ok"] = ok
        report["frame_count_message"] = msg
        report["ok"] = bool(report.get("ok")) and ok

    if args.reference_image and os.path.isfile(args.reference_image):
        frames = sorted(
            f
            for f in os.listdir(args.sim_dir)
            if f.endswith(".png") and f[:4].isdigit()
        )
        if frames:
            import numpy as np
            from PIL import Image

            sim = load_image_rgb(os.path.join(args.sim_dir, frames[0]))
            ref = load_image_rgb(args.reference_image)
            if sim.shape != ref.shape:
                ref_pil = Image.fromarray((ref * 255).astype("uint8"))
                ref_pil = ref_pil.resize((sim.shape[1], sim.shape[0]), Image.BILINEAR)
                ref = np.asarray(ref_pil).astype(np.float64) / 255.0
            report["vs_static_reference"] = {
                "sim_frame": frames[0],
                "reference": args.reference_image,
                **compare_image_pair(sim, ref),
            }

    text = json.dumps(report, indent=2)
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(text)
        print(f"Wrote {args.output}")
    else:
        print(text)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
