#!/usr/bin/env python3
"""
Batch multi-material Phys4DGS pipeline + render QA harness.

Runs Material Tag Tensor generation → PhysGaussian MPM → rasterize across the
canonical six digest scenes, then writes stability / PSNR / SSIM / LPIPS reports.

Requires a CUDA host with checkpoints under data/models/ and conda envs
``physgauss`` (solver + most tagging) and ``PartSAM`` (ficus lift only).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.eval.scene_registry import CANONICAL_SCENES, SceneSpec, select_scenes


def _env_python(conda_env: Optional[str]) -> List[str]:
    if conda_env:
        return ["conda", "run", "-n", conda_env, "--no-capture-output", "python"]
    return [sys.executable]


def _run(cmd: List[str], cwd: str) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=cwd, check=False)


def _model_path(scene: SceneSpec) -> str:
    return os.path.join(_PROJECT_ROOT, "data", "models", scene.model_dir)


def _config_path(scene: SceneSpec) -> str:
    return os.path.join(_PROJECT_ROOT, scene.config)


def ensure_prereqs(scenes: List[SceneSpec]) -> List[str]:
    missing: List[str] = []
    for scene in scenes:
        model = _model_path(scene)
        cfg = _config_path(scene)
        if not os.path.isdir(os.path.join(model, "point_cloud")):
            missing.append(f"{scene.id}: missing checkpoint at {model}/point_cloud")
        if not os.path.isfile(cfg):
            missing.append(f"{scene.id}: missing config {cfg}")
    return missing


def generate_tags(
    scene: SceneSpec,
    tags_path: str,
    physgauss_env: Optional[str],
    partsam_env: Optional[str],
    reuse: bool,
) -> Dict[str, Any]:
    os.makedirs(os.path.dirname(tags_path), exist_ok=True)
    if reuse and os.path.isfile(tags_path):
        return {"status": "reused", "tags_path": tags_path}

    model = _model_path(scene)
    if scene.tagger == "partsam":
        partsam_dir = os.path.join(os.path.dirname(tags_path), "partsam")
        os.makedirs(partsam_dir, exist_ok=True)
        for stage, env in (
            ("surface", physgauss_env),
            ("clicks", physgauss_env),
            ("lift", partsam_env),
        ):
            cmd = _env_python(env) + [
                "-m",
                "src.segmentation.partsam",
                "--model_path",
                model,
                "--output_dir",
                partsam_dir,
                "--stage",
                stage,
            ]
            if stage == "lift":
                cmd.extend(["--tags_path", tags_path])
            proc = _run(cmd, _PROJECT_ROOT)
            if proc.returncode != 0:
                return {
                    "status": "failed",
                    "stage": stage,
                    "returncode": proc.returncode,
                    "tags_path": tags_path,
                }
        return {"status": "ok", "tags_path": tags_path, "tagger": "partsam"}

    if scene.tagger == "vasedeck_heuristic":
        cmd = _env_python(physgauss_env) + [
            "-m",
            "src.segmentation.vasedeck_heuristic",
            "--model_path",
            model,
            "--output_path",
            tags_path,
        ]
        proc = _run(cmd, _PROJECT_ROOT)
        return {
            "status": "ok" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode,
            "tags_path": tags_path,
            "tagger": "vasedeck_heuristic",
        }

    # segmenter_agent — CPU-capable tagging path
    cmd = _env_python(physgauss_env) + [
        os.path.join(_PROJECT_ROOT, "scripts", "_write_segmenter_tags.py"),
        "--model_path",
        model,
        "--category",
        scene.category,
        "--output_path",
        tags_path,
    ]
    proc = _run(cmd, _PROJECT_ROOT)
    return {
        "status": "ok" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
        "tags_path": tags_path,
        "tagger": "segmenter_agent",
    }


def run_solver(
    scene: SceneSpec,
    tags_path: str,
    output_path: str,
    physgauss_env: Optional[str],
    frame_num: Optional[int],
    compile_video: bool,
) -> Dict[str, Any]:
    os.makedirs(output_path, exist_ok=True)
    cmd = _env_python(physgauss_env) + [
        "-m",
        "src.simulation.runner",
        "--model_path",
        _model_path(scene),
        "--output_path",
        output_path,
        "--config",
        _config_path(scene),
        "--tags_path",
        tags_path,
        "--render_img",
    ]
    if compile_video:
        cmd.append("--compile_video")
    if frame_num is not None:
        cmd.extend(["--frame_num", str(frame_num)])
    proc = _run(cmd, _PROJECT_ROOT)
    return {
        "status": "ok" if proc.returncode == 0 else "crashed",
        "returncode": proc.returncode,
        "output_path": output_path,
        "frame_num": frame_num,
    }


def render_reference(
    scene: SceneSpec,
    reference_path: str,
    physgauss_env: Optional[str],
) -> Dict[str, Any]:
    """Static 3DGS first-frame reference for quality comparison (camera index 0)."""
    os.makedirs(os.path.dirname(reference_path), exist_ok=True)
    cmd = _env_python(physgauss_env) + [
        "-m",
        "src.eval.render_first_frame",
        "--model_path",
        _model_path(scene),
        "--output",
        reference_path,
    ]
    proc = _run(cmd, _PROJECT_ROOT)
    return {
        "status": "ok" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
        "reference_path": reference_path,
    }


def evaluate_outputs(
    sim_dir: str,
    reference_png: Optional[str],
    expected_frames: Optional[int],
) -> Dict[str, Any]:
    # Local import keeps CUDA-only deps out of the metrics path
    from src.eval.evaluate_realism import (
        assert_expected_frame_count,
        compare_image_pair,
        evaluate_render_directory,
        load_image_rgb,
    )

    report = evaluate_render_directory(sim_dir, reference_dir=None)
    if expected_frames is not None:
        ok_count, msg = assert_expected_frame_count(sim_dir, expected_frames)
        report["expected_frame_count"] = expected_frames
        report["frame_count_ok"] = ok_count
        report["frame_count_message"] = msg
        report["ok"] = bool(report.get("ok")) and ok_count

    if reference_png and os.path.isfile(reference_png) and report.get("frame_count", 0) > 0:
        first = sorted(
            f for f in os.listdir(sim_dir) if f.endswith(".png") and f[:4].isdigit()
        )[0]
        sim_img = load_image_rgb(os.path.join(sim_dir, first))
        ref_img = load_image_rgb(reference_png)
        # Resize reference if camera resolution differs
        if sim_img.shape != ref_img.shape:
            try:
                from PIL import Image
                import numpy as np

                ref_pil = Image.fromarray((ref_img * 255).astype(np.uint8))
                ref_pil = ref_pil.resize((sim_img.shape[1], sim_img.shape[0]), Image.BILINEAR)
                ref_img = np.asarray(ref_pil).astype(np.float64) / 255.0
            except Exception as exc:
                report["reference_compare_error"] = str(exc)
                return report
        report["vs_static_reference"] = {
            "sim_frame": first,
            "reference": reference_png,
            **compare_image_pair(sim_img, ref_img),
        }
    return report


def run_scene(
    scene: SceneSpec,
    out_root: str,
    physgauss_env: Optional[str],
    partsam_env: Optional[str],
    smoke_frames: int,
    full: bool,
    reuse_tags: bool,
    compile_video: bool,
) -> Dict[str, Any]:
    scene_root = os.path.join(out_root, scene.id)
    tags_path = os.path.join(scene_root, "tags", "material_tags.pt")
    smoke_dir = os.path.join(scene_root, "smoke")
    full_dir = os.path.join(scene_root, "full")
    ref_path = os.path.join(scene_root, "reference", "0000.png")
    result: Dict[str, Any] = {
        "scene_id": scene.id,
        "model_dir": scene.model_dir,
        "config": scene.config,
        "tagger": scene.tagger,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result["tags"] = generate_tags(
            scene, tags_path, physgauss_env, partsam_env, reuse=reuse_tags
        )
        if result["tags"].get("status") == "failed":
            result["status"] = "tagging_failed"
            return result

        result["reference"] = render_reference(scene, ref_path, physgauss_env)

        result["smoke"] = run_solver(
            scene,
            tags_path,
            smoke_dir,
            physgauss_env,
            frame_num=smoke_frames,
            compile_video=False,
        )
        result["smoke_eval"] = evaluate_outputs(
            smoke_dir,
            ref_path if result["reference"].get("status") == "ok" else None,
            expected_frames=smoke_frames if result["smoke"]["status"] == "ok" else None,
        )

        if full and result["smoke"]["status"] == "ok":
            if os.path.isdir(full_dir):
                shutil.rmtree(full_dir)
            result["full"] = run_solver(
                scene,
                tags_path,
                full_dir,
                physgauss_env,
                frame_num=None,
                compile_video=compile_video,
            )
            with open(_config_path(scene)) as f:
                cfg_frame_num = int(json.load(f)["frame_num"])
            result["full_eval"] = evaluate_outputs(
                full_dir,
                ref_path if result["reference"].get("status") == "ok" else None,
                expected_frames=cfg_frame_num if result["full"]["status"] == "ok" else None,
            )

        crashed = result["smoke"].get("status") == "crashed" or (
            full and result.get("full", {}).get("status") == "crashed"
        )
        sanity_ok = bool(result.get("smoke_eval", {}).get("ok"))
        if full:
            sanity_ok = sanity_ok and bool(result.get("full_eval", {}).get("ok", True))
        result["status"] = "crashed" if crashed else ("ok" if sanity_ok else "quality_failed")
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()

    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    report_path = os.path.join(scene_root, "report.json")
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)
    result["report_path"] = report_path
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenes",
        nargs="*",
        default=None,
        help=f"Subset of scene ids (default: all). Known: {[s.id for s in CANONICAL_SCENES]}",
    )
    parser.add_argument(
        "--output-root",
        default=os.path.join(_PROJECT_ROOT, "data", "outputs", "multi_model_qa"),
    )
    parser.add_argument("--smoke-frames", type=int, default=5)
    parser.add_argument(
        "--full",
        action="store_true",
        help="After smoke passes, run full config frame_num",
    )
    parser.add_argument("--reuse-tags", action="store_true", default=True)
    parser.add_argument("--force-retag", action="store_true")
    parser.add_argument("--compile-video", action="store_true")
    parser.add_argument(
        "--physgauss-env",
        default=os.environ.get("PHYSGAUSS_CONDA_ENV", "physgauss"),
        help="Conda env for solver/rasterize (empty string = current python)",
    )
    parser.add_argument(
        "--partsam-env",
        default=os.environ.get("PARTSAM_CONDA_ENV", "PartSAM"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only check registry/prereqs and print the plan",
    )
    args = parser.parse_args()

    scenes = select_scenes(args.scenes)
    physgauss_env = args.physgauss_env or None
    partsam_env = args.partsam_env or None
    reuse_tags = args.reuse_tags and not args.force_retag

    print(f"Scenes ({len(scenes)}): {[s.id for s in scenes]}")
    missing = ensure_prereqs(scenes)
    if missing:
        print("Missing prerequisites:")
        for m in missing:
            print(" -", m)
        if not args.dry_run:
            return 2

    if args.dry_run:
        for scene in scenes:
            print(
                f"  {scene.id}: model={scene.model_dir} config={scene.config} "
                f"tagger={scene.tagger} smoke_frames={args.smoke_frames} full={args.full}"
            )
        return 0 if not missing else 2

    os.makedirs(args.output_root, exist_ok=True)
    summary: Dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "smoke_frames": args.smoke_frames,
        "full": args.full,
        "scenes": [],
    }
    exit_code = 0
    for scene in scenes:
        print("=" * 70)
        print(f"SCENE {scene.id}")
        print("=" * 70)
        scene_result = run_scene(
            scene,
            args.output_root,
            physgauss_env,
            partsam_env,
            smoke_frames=args.smoke_frames,
            full=args.full,
            reuse_tags=reuse_tags,
            compile_video=args.compile_video,
        )
        summary["scenes"].append(
            {
                "id": scene.id,
                "status": scene_result.get("status"),
                "report_path": scene_result.get("report_path"),
                "smoke_returncode": scene_result.get("smoke", {}).get("returncode"),
                "smoke_eval_ok": scene_result.get("smoke_eval", {}).get("ok"),
                "mean_psnr": (
                    scene_result.get("smoke_eval", {})
                    .get("vs_static_reference", {})
                    .get("psnr")
                ),
                "mean_ssim": (
                    scene_result.get("smoke_eval", {})
                    .get("vs_static_reference", {})
                    .get("ssim")
                ),
                "lpips": (
                    scene_result.get("smoke_eval", {})
                    .get("vs_static_reference", {})
                    .get("lpips")
                ),
            }
        )
        if scene_result.get("status") != "ok":
            exit_code = 1

    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(args.output_root, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote aggregate summary: {summary_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
