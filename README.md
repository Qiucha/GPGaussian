# Phys4DGS

GitHub: [Qiucha/GPGaussian](https://github.com/Qiucha/GPGaussian) (BlendED NVIDIA project, 2026).

Heterogeneous MPM on trained 3D Gaussian Splatting (3DGS) scenes. A **Material Tag Tensor** labels each Gaussian; those labels become per-particle Lamé parameters; the [PhysGaussian](https://github.com/XPandora/PhysGaussian) **PhysGaussian MPM Solver** steps the particles in time; frames are re-rasterized 3DGS. This repository is the **delta** (PartSAM tagging, LLM config, Lamé overlay, Digest Dashboard). It does **not** vendor PhysGaussian, 3DGS, FlashSplat, or PartSAM.

The intended tagger is PartSAM (`src/segmentation/partsam` → `material_tags.pt`). Heuristic Primitives and the Segmenter Agent remain for digest/tests. FlashSplat source is kept but is not on the intended runner.

Cite PhysGaussian (Xie et al., arXiv:2311.12198). Nested 3DGS (and optional FlashSplat) trees use the [Inria/MPII Gaussian-Splatting license](https://raw.githubusercontent.com/graphdeco-inria/gaussian-splatting/main/LICENSE.md) (research / non-commercial). A PartSAM clone is MIT for original code; `partfield/` is NVIDIA PartField [§3.3](https://raw.githubusercontent.com/nv-tlabs/PartField/main/LICENSE) (non-commercial research and educational purposes only).

Agent-facing current state and next steps: [docs/agents/orientation.md](docs/agents/orientation.md).

## Architecture

1. Load a trained 3DGS checkpoint (scene directory with `point_cloud/`).
2. Produce a Material Tag Tensor `(N,)` — intended: PartSAM three stages (surface sample → click groups → masks, merge, lift).
3. Map tag IDs → `E`, `nu`, `density` → Lamé.
4. Step the PhysGaussian MPM Solver (Warp).
5. Rasterize moved Gaussians. Inspect tags and frames in the **Digest Dashboard** (`digest/`).

The “4D” in the name is time-varying 3DGS particles under physics, not a Yang-style 4D Gaussian trainer.

## Upstream clones (gitignored)

Clones live under `third_party/` (also honored: `PHYSGAUSSIAN_ROOT`, `PARTSAM_ROOT`). See `src/upstream.py`. `FLASHSPLAT_ROOT` and `GAUSSIAN_SPLATTING_ROOT` are unused by `./scripts/run_pipeline.sh`. `third_party/` is gitignored; do not publish `partfield/` or the PartSAM weights.

**Required** for `./scripts/run_pipeline.sh`:

```shell
git clone --recurse-submodules https://github.com/XPandora/PhysGaussian.git third_party/PhysGaussian
git -C third_party/PhysGaussian checkout 8339ed6

git clone https://github.com/czvvd/PartSAM.git third_party/PartSAM
git -C third_party/PartSAM checkout b16d3e8
huggingface-cli download Czvvd/PartSAM model.safetensors --local-dir third_party/PartSAM/pretrained
```

PhysGaussian’s nested `gaussian-splatting` submodule is enough for simulation. Follow that clone’s README to install rasterizer extensions (`pip install -e …/diff-gaussian-rasterization`, `simple-knn`). PhysGaussian env notes: Python 3.9+, PyTorch, `pip install -r third_party/PhysGaussian/requirements.txt`. This repo: `pip install -e .` into the Warp env (and `pip install trimesh` there for Stage 1 sampling).

```shell
export PHYSGAUSSIAN_ROOT="$PWD/third_party/PhysGaussian"
export PARTSAM_ROOT="$PWD/third_party/PartSAM"
```

Trained 3DGS checkpoints stay in local `data/` (not in git). The default scene path is `data/models/ficus_whitebg`.

## Two conda envs

Do not merge these. `./scripts/run_pipeline.sh` calls them by name.

| Env | Role |
| --- | --- |
| `physgauss` | Stage 1 surface, Stage 2 clicks, PhysGaussian MPM Solver (Warp, pymeshlab, `trimesh`) |
| `PartSAM` | Stage 3 `predict_masks` / lift only (Python 3.11, PyTorch 2.4.1+cu124, `torch-scatter`; follow the PartSAM repo pip list) |

Inference uses this repo’s FPS stand-in (seed index 0), not a compiled torkit3d. Checkpoint: `third_party/PartSAM/pretrained/model.safetensors` (~859MB).

## Run the delta

From the repo root, with those two envs and a local 3DGS scene:

```shell
./scripts/run_pipeline.sh
```

That is PartSAM (or reuse existing tags) → PhysGaussian MPM Solver. Defaults: `--model_path data/models/ficus_whitebg`, tags `data/outputs/tags/material_tags.pt`, config `configs/ficus.json`. If `material_tags.pt` already exists, tagging is skipped.

**Clicks:** Stage 2 skip-if-exists needs a complete `data/outputs/partsam/clicks.json` (`frame: world`, `source` present, groups `pot` / `trunk` / `leaves`, each with at least one positive and a negatives list). Otherwise the stage writes `click_candidates.json` / `click_candidates.png` and stops; an MLLM or human must write `clicks.json` (accept / swap / resample labeled candidates). Geometry propose lives in `src/`.

A short solver run after tags exist is the intended check. This README does not claim a currently-good live ficus Material Tag Tensor occupancy or a full-length wind campaign.

Or invoke the solver directly:

```shell
python -m src.simulation.runner --model_path <3dgs-dir> --output_path <out> --config configs/ficus.json --tags_path data/outputs/tags/material_tags.pt
```

## Optional: FlashSplat clone

Not required for `run_pipeline.sh`. Source `src/segmentation/flashsplat.py` remains; the intended tagging path does not call it.

```shell
git clone --recurse-submodules https://github.com/florinshen/FlashSplat.git third_party/FlashSplat
git -C third_party/FlashSplat checkout 3e3b147
export FLASHSPLAT_ROOT="$PWD/third_party/FlashSplat"
```

Install FlashSplat’s `flashsplat-rasterization` only if you run that module. Do not put FlashSplat and 3DGS on the same global `sys.path`. A second graphdeco 3DGS clone (`GAUSSIAN_SPLATTING_ROOT`) is optional; PhysGaussian’s submodule is enough.

## Optional: Motion Critique Loop

After a first solver run, a separate driver can retune JSON config from required human text. It is **not** folded into `run_pipeline.sh`. The CLI uses a mock identity `critique`; live `translate` / `critique` raise `NotImplementedError`.

```shell
python -m src.llm.critique_loop \
  --config configs/ficus.json \
  --model_path data/models/ficus_whitebg \
  --tags_path data/outputs/tags/material_tags.pt \
  --text "the trunk should rebound more"
```

Default mode is human-gated. Policy: [Motion Critique Loop spec](.scratch/mpm-critique-loop/spec.md).

## Digest Dashboard

Open `digest/index.html` (serve `digest/` as static files if `fetch("data/manifest.json")` must work). Exported frames are not in git.

Multi-material example config: `configs/vasedeck_multi_material.json`.
