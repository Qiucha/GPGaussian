# Phys4DGS

GitHub: [Qiucha/GPGaussian](https://github.com/Qiucha/GPGaussian) (BlendED NVIDIA project, 2026).

Multi-material physical simulation on 3D Gaussian Splatting scenes: a Segmenter Agent and heuristic primitives assign a material tag tensor, then the [PhysGaussian](https://github.com/XPandora/PhysGaussian) MPM solver steps the motion. This repository is the **delta** (segmentation, LLM config, Lamé overlay, digest dashboard). It does **not** vendor PhysGaussian, 3DGS, FlashSplat, or PartSAM.

Cite PhysGaussian (Xie et al., arXiv:2311.12198). Nested 3DGS / FlashSplat trees use the [Inria/MPII Gaussian-Splatting license](https://raw.githubusercontent.com/graphdeco-inria/gaussian-splatting/main/LICENSE.md) (research / non-commercial). A PartSAM clone is MIT for original code; `partfield/` is NVIDIA PartField (non-commercial research/education).

## Upstream clones (gitignored)

Clones live under `third_party/` (also honored: `PHYSGAUSSIAN_ROOT`, `FLASHSPLAT_ROOT`, `GAUSSIAN_SPLATTING_ROOT`, `PARTSAM_ROOT`). See `src/upstream.py`.

```shell
git clone --recurse-submodules https://github.com/XPandora/PhysGaussian.git third_party/PhysGaussian
git -C third_party/PhysGaussian checkout 8339ed6

git clone --recurse-submodules https://github.com/florinshen/FlashSplat.git third_party/FlashSplat
git -C third_party/FlashSplat checkout 3e3b147

git clone https://github.com/czvvd/PartSAM.git third_party/PartSAM
git -C third_party/PartSAM checkout b16d3e8
huggingface-cli download Czvvd/PartSAM model.safetensors --local-dir third_party/PartSAM/pretrained
```

PhysGaussian’s `gaussian-splatting` submodule is enough for simulation. A second graphdeco clone is optional (`GAUSSIAN_SPLATTING_ROOT`). Do not put FlashSplat and 3DGS on the same global `sys.path`.

Follow each upstream README to install rasterizer submodules (`pip install -e …/diff-gaussian-rasterization`, `simple-knn`, and FlashSplat’s `flashsplat-rasterization`). PhysGaussian’s env notes: Python 3.9+, PyTorch, `pip install -r third_party/PhysGaussian/requirements.txt`.

This repo: `./setup_env.sh` then `./setup_phase2.sh` (conda `physgauss_v2`), or `pip install -e .` into an env that already has those CUDA extensions.

**Two conda envs** (do not merge). `physgauss`: Warp, pymeshlab, Stage 1–2, solver; `pip install trimesh` into that env. `PartSAM`: Python 3.11, PyTorch 2.4.1+cu124, `predict_masks` / `--stage lift`; follow the PartSAM repo’s pip list plus `torch-scatter` for that torch build. Inference uses this repo’s FPS stand-in (seed index 0). Checkpoint: `third_party/PartSAM/pretrained/model.safetensors` (~859MB). Leave `partfield/` and the weights in the gitignored clone.

```shell
export PHYSGAUSSIAN_ROOT="$PWD/third_party/PhysGaussian"
export FLASHSPLAT_ROOT="$PWD/third_party/FlashSplat"
export PARTSAM_ROOT="$PWD/third_party/PartSAM"
```

Trained 3DGS checkpoints stay in local `data/` (not in git). Point `--model_path` at a scene directory that contains `point_cloud/`.

## Run the delta

From the repo root, with the conda env that has Warp / rasterizers:

```shell
./scripts/run_pipeline.sh
# or: python -m src.simulation.runner --model_path <3dgs-dir> --output_path <out> --config configs/ficus.json
```

Multi-material example config: `configs/vasedeck_multi_material.json`. Digest dashboard (no exported frames in git): open `digest/index.html`.
