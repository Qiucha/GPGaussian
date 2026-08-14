# 01 — Intended clone, env, license, and run facts (wired delta)

Primary sources (2026-08-14): [README.md](../../../README.md) (stale baseline); [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh); [`src/upstream.py`](../../../src/upstream.py); [`src/__init__.py`](../../../src/__init__.py); [`src/segmentation/partsam/clicks.py`](../../../src/segmentation/partsam/clicks.py), [`__main__.py`](../../../src/segmentation/partsam/__main__.py), [`infer.py`](../../../src/segmentation/partsam/infer.py), [`merge.py`](../../../src/segmentation/partsam/merge.py); [`src/llm/critique_loop.py`](../../../src/llm/critique_loop.py); [`src/llm/translator.py`](../../../src/llm/translator.py); [`src/segmentation/flashsplat.py`](../../../src/segmentation/flashsplat.py); [`setup_env.sh`](../../../setup_env.sh); [`setup_phase2.sh`](../../../setup_phase2.sh); [`.gitignore`](../../../.gitignore); [PartSAM spec](../../partsam-as-tagger/spec.md); [Motion Critique Loop spec](../../mpm-critique-loop/spec.md); [`docs/agents/orientation.md`](../../../docs/agents/orientation.md); official [PhysGaussian README](https://raw.githubusercontent.com/XPandora/PhysGaussian/master/README.md); [PartSAM LICENSE.md](https://raw.githubusercontent.com/czvvd/PartSAM/main/LICENSE.md) and [README](https://raw.githubusercontent.com/czvvd/PartSAM/main/README.md); [Inria 3DGS LICENSE.md](https://raw.githubusercontent.com/graphdeco-inria/gaussian-splatting/main/LICENSE.md); [NVIDIA PartField LICENSE](https://raw.githubusercontent.com/nv-tlabs/PartField/main/LICENSE). Pins checked against leftover clones (not published trees). Prior tickets in `.scratch/partsam-src-wiring/` and `.scratch/github-ready-working-tree/` used only as pointers to verify. Does not rewrite `README.md`.

## 0. What the current README gets wrong

[README.md](../../../README.md) still opens as “a Segmenter Agent and heuristic primitives assign a material tag tensor” and lists FlashSplat as a required clone plus `./setup_env.sh` then `./setup_phase2.sh` (conda `physgauss_v2`). The wired runner is PartSAM → PhysGaussian MPM Solver; FlashSplat is unhooked from that runner; `physgauss_v2` is not the env name the runner uses. ([`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh) header and `conda run -n`; [PartSAM spec](../../partsam-as-tagger/spec.md) Intended producer; [`docs/agents/orientation.md`](../../../docs/agents/orientation.md) Pipeline as built.)

Keep from the current README: GitHub remote line; “this repo is the delta; do not vendor PhysGaussian / 3DGS / FlashSplat / PartSAM”; cite PhysGaussian; Inria/MPII on nested 3DGS; PartSAM MIT + NVIDIA `partfield/`; clone pins `8339ed6` / `3e3b147` / `b16d3e8`; Hugging Face `Czvvd/PartSAM` → `pretrained/`; two conda envs `physgauss` + `PartSAM`; trained checkpoints stay in local `data/`; `./scripts/run_pipeline.sh`. Drop or demote: Segmenter Agent as the intended tagger; required FlashSplat clone; `setup_env.sh` / `physgauss_v2` as intended bootstrap; exporting `FLASHSPLAT_ROOT` as if the intended run needed it.

## 1. Required vs optional clones

**Required — PhysGaussian (recurse-submodules).** Official clone:

```shell
git clone --recurse-submodules git@github.com:XPandora/PhysGaussian.git
```

HTTPS equivalent is the same URL over `https://github.com/XPandora/PhysGaussian.git`. The tree is a script root (`gs_simulation.py`, `mpm_solver_warp`), not a pip package. Nested `gaussian-splatting` is a submodule. ([PhysGaussian README](https://raw.githubusercontent.com/XPandora/PhysGaussian/master/README.md) Cloning the Repository; [`src/upstream.py`](../../../src/upstream.py) `get_physgaussian_root` error text and `_PHYSGAUSSIAN_MARKERS`.)

[`src/upstream.py`](../../../src/upstream.py) looks for `PHYSGAUSSIAN_ROOT`, then `third_party/PhysGaussian`, then `.trash/PhysGaussian`. Markers: `gs_simulation.py` and `mpm_solver_warp`. Simulation path insert (`ensure_simulation_path`) puts that root then its `gaussian-splatting` on `sys.path`. Called from [`src/simulation/runner.py`](../../../src/simulation/runner.py), [`src/simulation/config.py`](../../../src/simulation/config.py), [`src/rendering/rasterize.py`](../../../src/rendering/rasterize.py), [`src/rendering/camera.py`](../../../src/rendering/camera.py), [`src/rendering/transforms.py`](../../../src/rendering/transforms.py). Checkpoint load uses `get_gaussian_splatting_root()` ([`src/rendering/checkpoint.py`](../../../src/rendering/checkpoint.py)). [`src/__init__.py`](../../../src/__init__.py) does **not** prepend vendor paths.

**Pin `8339ed6`.** Documented in [README.md](../../../README.md). Leftover clone `.trash/PhysGaussian` is `8339ed6` (`8339ed6aa2cd5d50e1001a254a3d95aea678a956`, message `plane example`). Official `master` is not asserted to equal that pin; the visitor README should keep the workspace pin.

**Required — PartSAM + Hugging Face weights.** Clone `https://github.com/czvvd/PartSAM.git` into gitignored `third_party/PartSAM`. `get_partsam_root()` requires a `partfield/` directory; order is `PARTSAM_ROOT` then `third_party/PartSAM`. ([`src/upstream.py`](../../../src/upstream.py).) Weights: `root / "pretrained" / "model.safetensors"` or `FileNotFoundError`. ([`src/segmentation/partsam/infer.py`](../../../src/segmentation/partsam/infer.py) `_load_partsam_model`.) Official Hub command:

```shell
huggingface-cli download Czvvd/PartSAM --local-dir ./pretrained
```

([PartSAM README](https://raw.githubusercontent.com/czvvd/PartSAM/main/README.md).) Current Phys4DGS README downloads only `model.safetensors` into `third_party/PartSAM/pretrained`; that matches what `_load_partsam_model` opens. Spec: gitignored clone + Hub `Czvvd/PartSAM`; do not publish `partfield/` or the ~859MB file; inference uses this repo’s FPS stand-in (`src/segmentation/partsam/fps.py` `install()`), not torkit3d/apex. ([PartSAM spec](../../partsam-as-tagger/spec.md) Constraints / Stage 3.)

**Pin `b16d3e8`.** Documented in [README.md](../../../README.md). Trial clone `.scratch/partsam-ficus-trial/vendor/PartSAM` is `b16d3e8` (`b16d3e8f1b7f1af100df4a9e61dcd4f1788045b5`, message `update`).

**`.gitignore`:** `data/`, `.trash/`, `vendor/`, `third_party/` — clones and checkpoints are not published. ([`.gitignore`](../../../.gitignore).)

**Optional — FlashSplat.** `get_flashsplat_root()` exists (`FLASHSPLAT_ROOT`, then `third_party/FlashSplat`, then `vendor/FlashSplat`; needs `gaussian_renderer/__init__.py`). Only [`src/segmentation/flashsplat.py`](../../../src/segmentation/flashsplat.py) imports it. [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh): “FlashSplat / color_heuristic are not on this runner.” Spec: FlashSplat **retired** as a tagging path. ([PartSAM spec](../../partsam-as-tagger/spec.md).) Pin `3e3b147` is in [README.md](../../../README.md); leftover `vendor/FlashSplat` is `3e3b147` (`3e3b14786333bf0163ba1b8541e86a3765112d7d`). A visitor can omit the clone unless they run `python -m src.segmentation.flashsplat`.

**Optional — extra graphdeco 3DGS.** `get_gaussian_splatting_root()` prefers PhysGaussian’s nested `gaussian-splatting` (directory containing `scene/`). Only if that is missing: `GAUSSIAN_SPLATTING_ROOT`, then `third_party/gaussian-splatting`, then `vendor/gaussian-splatting`. ([`src/upstream.py`](../../../src/upstream.py).) Recurse-submodules on PhysGaussian is enough for `run_pipeline.sh`. Do not put FlashSplat and 3DGS on the same global `sys.path` (current [`src/__init__.py`](../../../src/__init__.py) already does not).

## 2. Env vars vs `run_pipeline.sh`

| Var | Resolver | Needed for `./scripts/run_pipeline.sh`? |
| --- | --- | --- |
| `PARTSAM_ROOT` | `get_partsam_root()` | **Yes** for Stage 3 unless `data/outputs/tags/material_tags.pt` already exists. The script `export`s default `$PROJECT_ROOT/third_party/PartSAM`. |
| `PHYSGAUSSIAN_ROOT` | `get_physgaussian_root()` | **Yes** for the solver (and for Stage 1 if it loads Gaussians via 3DGS). Script does **not** export it; default `third_party/PhysGaussian` (then leftover `.trash`). Visitor should clone there or export. |
| `GAUSSIAN_SPLATTING_ROOT` | `get_gaussian_splatting_root()` fallback | **No** if PhysGaussian was cloned with `--recurse-submodules`. |
| `FLASHSPLAT_ROOT` | `get_flashsplat_root()` | **No.** Unused by this runner. |

([`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh); [`src/upstream.py`](../../../src/upstream.py).)

## 3. Conda env names

**Intended runner** ([`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh)):

- `conda run -n physgauss` — Stage 1 surface, Stage 2 clicks, `src.simulation.runner`
- `conda run -n PartSAM` — Stage 3 lift only

**`setup_env.sh` / `setup_phase2.sh` do not create those names.** `setup_env.sh` creates `physgauss_v2` (Python 3.10, PyTorch 2.3.1 + CUDA 12.1, ninja/cxx). `setup_phase2.sh` activates `physgauss_v2` and pip-installs Grounding DINO + Segment Anything 2 — not PartSAM, not Warp. Official PartSAM env is `conda create -n PartSAM python=3.11` + torch 2.4.1+cu124. Official PhysGaussian env is `conda create -n PhysGaussian python=3.9` (different name from `physgauss`). Visitor bootstrap should document existing envs `physgauss` + `PartSAM`, not `./setup_env.sh`.

## 4. Stage 2 `clicks.json` and default paths

**Pipeline skip is tags, not clicks.** If `data/outputs/tags/material_tags.pt` exists, tagging (all three stages) is skipped and the solver runs. Else four `conda run`s. ([`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh).)

**Defaults in the runner:**

- `--model_path` → `$PROJECT_ROOT/data/models/ficus_whitebg`
- PartSAM artifacts → `$PROJECT_ROOT/data/outputs/partsam`
- `--tags_path` → `$PROJECT_ROOT/data/outputs/tags/material_tags.pt`
- `--config` → `$PROJECT_ROOT/configs/ficus.json`
- `--output_path` → `$PROJECT_ROOT/data/outputs/simulated_video`

`data/` is gitignored. A visitor must supply a local 3DGS scene dir with `point_cloud/` (README already says this; [`src/segmentation/partsam/__main__.py`](../../../src/segmentation/partsam/__main__.py) help text). Checkpoints are not in git.

**Stage 2 skip-if-exists** ([`src/segmentation/partsam/clicks.py`](../../../src/segmentation/partsam/clicks.py) `run_stage_clicks`, default `skip_if_exists=True`; CLI does not pass a flag — [`__main__.py`](../../../src/segmentation/partsam/__main__.py)):

1. Destination is `{output_dir}/clicks.json` (`CLICKS_NAME`). For the intended runner that is `data/outputs/partsam/clicks.json`.
2. If the file exists **and** `clicks_are_complete` (validate: `frame == "world"`, `source` present, groups `pot` / `trunk` / `leaves`, each with ≥1 positive and a negatives list), return that path without proposing.
3. Otherwise load Stage 1 `sample_100k.npz`, write `click_candidates.json` and optional `click_candidates.png`, then if a complete `clicks.json` is now present, return it.
4. Else `RuntimeError`: MLLM or human must write `clicks.json` (accept / swap / resample labeled candidates only, no free-form xyz). Human after two failed annotated rounds.

**Visitor contract:** place a complete `clicks.json` at `data/outputs/partsam/clicks.json` **before** Stage 2, or Stage 2 will stop after writing candidates. Spec JSON shape (same groups) is in [PartSAM spec](../../partsam-as-tagger/spec.md) Stage 2. Spec also says skip only when clicks belong to **this** 100k sample; **wired code does not check sample identity** — only file existence + completeness. Tests: `tests/test_partsam_clicks.py` (`test_stage_clicks_skips_when_every_group_has_a_positive`).

Stage 3 lift always `validate_clicks` on that file; `--reuse-tags` is the CLI skip for tags, equivalent to the shell’s existing-`material_tags.pt` branch. ([`infer.py`](../../../src/segmentation/partsam/infer.py) `run_stage_lift`.)

## 5. Critique-loop CLI

Not on `run_pipeline.sh`. Orientation: optional `python -m src.llm.critique_loop`; live `critique` still `NotImplementedError`. ([`docs/agents/orientation.md`](../../../docs/agents/orientation.md).)

Visitor can type (required: previous `--config` JSON, `--model_path`, non-empty human text):

```shell
python -m src.llm.critique_loop \
  --config configs/ficus.json \
  --model_path data/models/ficus_whitebg \
  --tags_path data/outputs/tags/material_tags.pt \
  --text "the trunk should rebound more"
```

Optional: `--text-file`, piped stdin (TTY without `--text`/`--text-file` exits), `--output_dir` default `data/outputs/critique`, `--mode human-gated|auto` (default human-gated), `--max-runs` default 3, `--reasoning`. ([`src/llm/critique_loop.py`](../../../src/llm/critique_loop.py) `main`.)

**Mock vs live:** CLI always constructs `MotionTranslator(mock_llm=True)`. Mock `critique` is identity after `validate_physgaussian_config(..., previous=previous_config)`; canned reasoning `"identity mock critique"`; if `frame_paths` set, appends `; visual channel skipped (mock)`. Empty/whitespace human text is `ValueError`. `mock_llm=False` raises `NotImplementedError("Live LLM API endpoint call requires API key configuration.")` for both `translate` and `critique`. ([`src/llm/translator.py`](../../../src/llm/translator.py); spec Mock in [Motion Critique Loop spec](../../mpm-critique-loop/spec.md).) Driver subprocesses `python -m src.simulation.runner` with `--render_img` (needs PhysGaussian + Warp). Human-gated: one solver run then `waiting`. Auto: same human text until N solver runs.

## 6. License / cite lines that must stay

1. **PhysGaussian — cite, no LICENSE file.** Official README Citation bibtex `xie2023physgaussian` / arXiv:2311.12198. `https://raw.githubusercontent.com/XPandora/PhysGaussian/master/LICENSE` is HTTP 404. Keep “Cite PhysGaussian (Xie et al., arXiv:2311.12198).”

2. **Inria/MPII Gaussian-Splatting** on the nested (and optional extra) 3DGS tree: research / non-commercial; redistribution must keep the license. ([LICENSE.md](https://raw.githubusercontent.com/graphdeco-inria/gaussian-splatting/main/LICENSE.md) §§3–5.) FlashSplat, if mentioned as optional, uses the same license file in-tree (prior GS/FlashSplat research); naming Inria on “nested 3DGS / optional FlashSplat” remains accurate.

3. **PartSAM original code — MIT.** [PartSAM LICENSE.md](https://raw.githubusercontent.com/czvvd/PartSAM/main/LICENSE.md): original PartSAM is MIT (`LICENSES/MIT.txt`).

4. **`partfield/` — NVIDIA PartField, non-commercial research/education.** Same LICENSE.md: complete inference pipeline must comply. NVIDIA LICENSE §3.3: Work and derivatives “only may be used or intended for use non-commercially” = “non-commercial research and educational purposes only.” ([nv-tlabs/PartField LICENSE](https://raw.githubusercontent.com/nv-tlabs/PartField/main/LICENSE).) Spec: public academic clone is in grant; commercial use is outside; do not publish `partfield/` or weights. ([PartSAM spec](../../partsam-as-tagger/spec.md) License.)

This repo has no root `LICENSE` and `pyproject.toml` has no `license` field. Phys4DGS remains the delta; cloners receive upstream licenses with the clones.

## 7. What a visitor README must state (checklist)

- Intended tagger is PartSAM (`material_tags.pt`), not Segmenter Agent / FlashSplat. Heuristic Primitives / Segmenter Agent remain for digest/tests.
- Required clones: PhysGaussian `--recurse-submodules` pin `8339ed6`; PartSAM pin `b16d3e8` + Hub weights into `pretrained/model.safetensors`. Both under gitignored `third_party/`.
- Optional: FlashSplat pin `3e3b147`; extra graphdeco 3DGS. `run_pipeline.sh` imports neither FlashSplat nor a second GS clone.
- Env: `PHYSGAUSSIAN_ROOT` / `PARTSAM_ROOT` (defaults under `third_party/`). `FLASHSPLAT_ROOT` / `GAUSSIAN_SPLATTING_ROOT` not required for the intended run.
- Two conda envs `physgauss` + `PartSAM`. Do not document `setup_env.sh` → `physgauss_v2` as the bootstrap.
- Run `./scripts/run_pipeline.sh` from repo root. Defaults: `data/models/ficus_whitebg`, tags `data/outputs/tags/material_tags.pt`, config `configs/ficus.json`.
- Honesty: local 3DGS checkpoint; Stage 2 needs a complete `data/outputs/partsam/clicks.json` or the stage errors after writing candidates; existing tags skip tagging.
- Optional critique: `python -m src.llm.critique_loop ... --text "..."` is mock identity; live `translate` / `critique` are `NotImplementedError`.
- Licenses: PhysGaussian cite; Inria 3DGS; PartSAM MIT; NVIDIA PartField §3.3.
- One pointer to [`docs/agents/orientation.md`](../../../docs/agents/orientation.md).
