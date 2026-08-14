# 01 - Intended clone, env, and run facts for the visitor README

Type: research
Status: resolved
Blocked by: none

## Question

What clone, env, license, and run facts must the GitHub visitor README state so it matches the **wired** delta (not the current README’s Segmenter Agent / required FlashSplat / `physgauss_v2` story)?

Cover, from primary sources only (`README.md` as the stale baseline to correct; `scripts/run_pipeline.sh`; `src/upstream.py`; `src/segmentation/partsam/` including clicks skip-if-exists; `src/llm/critique_loop.py`; `setup_env.sh`; `setup_phase2.sh`; `.gitignore`; PartSAM spec; critique-loop spec; `docs/agents/orientation.md`):

1. Required clones and pins (PhysGaussian recurse-submodules, PartSAM + Hugging Face weights). Optional clones (FlashSplat, extra graphdeco 3DGS) and whether the intended runner imports them.
2. Env vars (`PHYSGAUSSIAN_ROOT`, `PARTSAM_ROOT`, `FLASHSPLAT_ROOT`, `GAUSSIAN_SPLATTING_ROOT`) and which are needed for `run_pipeline.sh`.
3. Conda env names the intended runner actually uses vs what `setup_env.sh` creates.
4. Stage 2 `clicks.json` skip-if-exists contract a visitor must satisfy; default `--model_path` / tags paths in `run_pipeline.sh`.
5. Critique-loop CLI a visitor can type; what is mock vs `NotImplementedError`.
6. License/cite lines that must stay (PhysGaussian, Inria 3DGS, PartSAM MIT, NVIDIA PartField).

Write findings to `.scratch/github-visitor-readme/research/01-intended-clone-env-run-facts.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** rewrite `README.md`.

## Answer

The visitor README must describe PartSAM → PhysGaussian MPM Solver via `./scripts/run_pipeline.sh`, not Segmenter Agent / required FlashSplat / `physgauss_v2`. Required clones are PhysGaussian `--recurse-submodules` pin `8339ed6` and PartSAM pin `b16d3e8` plus Hub `pretrained/model.safetensors`; FlashSplat (`3e3b147`) and a second graphdeco 3DGS tree are optional and unused by that runner. Export `PARTSAM_ROOT` / `PHYSGAUSSIAN_ROOT` (defaults under gitignored `third_party/`); `FLASHSPLAT_ROOT` is not needed. Use conda envs `physgauss` (stages 1–2 + solver) and `PartSAM` (lift only)—`setup_env.sh` creates `physgauss_v2` and is not the intended bootstrap. Stage 2 skip-if-exists needs a complete `data/outputs/partsam/clicks.json`; defaults are `data/models/ficus_whitebg` and `data/outputs/tags/material_tags.pt`. Optional `python -m src.llm.critique_loop` is mock identity; live `translate`/`critique` stay `NotImplementedError`. Keep PhysGaussian cite, Inria 3DGS, PartSAM MIT, NVIDIA PartField. Details: [research/01-intended-clone-env-run-facts.md](../research/01-intended-clone-env-run-facts.md).
