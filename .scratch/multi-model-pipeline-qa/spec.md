# Multi-model pipeline QA (render quality + stability)

Status: ready-for-agent

## Goal

Run the full Phys4DGS pipeline (Material Tag Tensor → PhysGaussian MPM → rasterize) across the six multi-material digest scenes, then verify:

1. **Stability** — process exit 0, expected PNG count, finite particle/frame values, no all-black / all-NaN frames.
2. **Render quality** — PSNR / SSIM / LPIPS of simulated frames vs static 3DGS reference views at the same camera policy, plus a machine-readable report.

## Scenes

| id | `data/models/` folder | config | tagger |
| --- | --- | --- | --- |
| ficus | `ficus_whitebg` | `configs/ficus.json` | PartSAM (tags 1–3) |
| vasedeck | `vasedeck_whitebg` | `configs/vasedeck_multi_material.json` | `vasedeck_heuristic` |
| bread | `bread-trained` | `configs/tear_bread_multi_material.json` | Segmenter Agent |
| plane | `plane-trained` | `configs/plane_multi_material.json` | Segmenter Agent |
| pillow2sofa | `pillow2sofa_whitebg-trained` | `configs/pillow2sofa_multi_material.json` | Segmenter Agent |
| wolf | `wolf_whitebg-trained` | `configs/wolf_multi_material.json` | Segmenter Agent |

Upstream PhysGaussian single-material configs are restored and overlaid with a heterogeneous `materials` map aligned to the tagger’s tag ids.

## Harness

- Registry: `src/eval/scene_registry.py`
- Batch driver: `scripts/run_multi_model_pipeline.py` (CUDA host; `conda run -n physgauss` / PartSAM env for ficus lift)
- Metrics: `src/eval/evaluate_realism.py` (`compute_psnr`, `compute_ssim`, `compute_lpips`, frame sanity)
- Report writer: `scripts/verify_render_quality.py` → `data/outputs/multi_model_qa/<scene>/report.json` + aggregate `summary.json`

## Smoke vs full

- `--smoke-frames N` overrides runner `--frame_num` for a short crash/smoke pass before optional full `frame_num`.
- Default QA path: smoke (5 frames) for all six, then full run when `--full` is set.

## Environment

Requires a CUDA machine with checkpoints under `data/models/`, PhysGaussian + PartSAM clones, and the `physgauss` / `PartSAM` conda envs. The Cloud CPU VM cannot execute MPM/rasterize; unit tests cover metrics and registry offline.

## Non-goals

- Live Motion Critique Loop / LLM translate.
- FVD/KVD video metrics.
- Digest Dashboard fake-frame export as a substitute for Warp frames.
