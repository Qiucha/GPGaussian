# Runbook: multi-model pipeline QA (CUDA host)

Status: ready-for-human

## Prerequisites

1. CUDA GPU + conda envs `physgauss` and `PartSAM` (see README / setup scripts).
2. Clones: `third_party/PhysGaussian` @ `8339ed6`, `third_party/PartSAM` @ `b16d3e8`.
3. Checkpoints under `data/models/<folder>/point_cloud/` for all six registry scenes.
4. Optional for LPIPS: `pip install lpips` inside the physgauss env.

## Commands

```bash
# Plan + prereq check only
python scripts/run_multi_model_pipeline.py --dry-run

# Smoke (5 frames) across all six scenes
python scripts/run_multi_model_pipeline.py --smoke-frames 5

# Subset + full config frame_num after smoke
python scripts/run_multi_model_pipeline.py --scenes ficus vasedeck --full --compile-video

# Re-score an existing output dir
python scripts/verify_render_quality.py \
  --sim-dir data/outputs/multi_model_qa/ficus/smoke \
  --reference-image data/outputs/multi_model_qa/ficus/reference/0000.png \
  --expected-frames 5 \
  --output data/outputs/multi_model_qa/ficus/quality.json
```

## Pass criteria

Per scene `report.json` / aggregate `summary.json`:

- `status` is `ok` (not `crashed` / `tagging_failed` / `quality_failed`).
- Smoke `returncode == 0` and `frame_count_ok`.
- Every PNG passes frame sanity (finite, not all-black / all-white).
- `vs_static_reference` records PSNR / SSIM / LPIPS (LPIPS may be null if package missing).

Note: frame `0000.png` is rendered after the first MPM frame’s substeps, so PSNR vs a static 3DGS reference is a pipeline quality signal, not identity.
