# Orientation

Read this when starting work on Phys4DGS, choosing the next experiment, or judging whether a markdown file is live instruction. Glossary: [CONTEXT.md](../../CONTEXT.md). Sourced facts: [repo current state](../../.scratch/agent-orientation/research/01-repo-current-state.md). This file is the cache of unwritten convention; commands and module paths live in the tree.

## Purpose

Phys4DGS runs **heterogeneous MPM on trained 3D Gaussian Splatting (3DGS) scenes**. A **Material Tag Tensor** labels each Gaussian; those labels become per-particle Lamé parameters; the **PhysGaussian MPM Solver** moves the particles in time; frames are re-rasterized 3DGS.

The “4D” in the name is **time-varying 3DGS particles under physics**. There is no Yang-style 4D Gaussian trainer in `src/` (no deformation field / HexPlane optimization loop). Packaging text in `pyproject.toml` is the name, not a trainer.

## Pipeline as built

1. Load a trained 3DGS PLY (`src/rendering/checkpoint.py`, `src/simulation/runner.py`).
2. Produce a Material Tag Tensor `(N,)` — intended: PartSAM (`src/segmentation/partsam`, `material_tags.pt`). Heuristic Primitives via the **Segmenter Agent** remain for digest/tests.
3. Map tags → `E`, `nu`, `density` → Lamé (`src/simulation/lame_params.py`).
4. Step the PhysGaussian MPM Solver (`src/simulation/mpm_solver/solver.py`, `MPM_Simulator_WARP`).
5. Rasterize moved Gaussians (`src/rendering/rasterize.py`). Inspect tags and (when present) frames in the **Digest Dashboard** (`digest/`).

## Current state

**Works offline:** Heuristic Primitives (`src/segmentation/heuristics.py`); Segmenter Agent with `mock_llm=True`; schema/CFL; mock MotionTranslator (`translate` and `critique`); Motion Critique Loop driver (`src/llm/critique_loop.py`); Kabsch trajectory MSE and 2AFC; Warp runner; Digest Dashboard UI; `scripts/run_pipeline.sh` (PartSAM → PhysGaussian MPM Solver, or reuse `material_tags.pt`).

**Stubbed or incomplete:** live MotionTranslator `translate` / `critique` (`NotImplementedError`); LangSAM empty without `lang_sam`; FVD/KVD/PSNR/SSIM/LPIPS named but unimplemented; Dual-Mode Frame Player is image scrubbing only (glossary also names HTML5 video); digest “MPM” frames from `scripts/export_pipeline_data.py` are PIL offsets, not Warp; `scripts/run_pipeline.py` writes an empty tag tensor.

**Stale entry points (use the `.sh` runners instead):** `scripts/run_pipeline.py`, `scripts/run_experiment.sh`, `tests/test_pipeline.py`, `tests/test_projection.py`.

Working vs stubbed tables: [repo current state](../../.scratch/agent-orientation/research/01-repo-current-state.md).

## Upstream clones and experiments

Clones resolve through `src/upstream.py` (`third_party/` or `PHYSGAUSSIAN_ROOT` / `PARTSAM_ROOT`). Simulation 3DGS is PhysGaussian’s nested `gaussian-splatting`. FlashSplat leftover source (`src/segmentation/flashsplat.py`) is unused by `./scripts/run_pipeline.sh`.

`data/experiments/` holds ficus wind/sway **notes** (trunk still does not fully rebound in exp 4). No archived `output.mp4` in the tree. `digest/data/` JSON for six scenes is mock-agent export, not Warp video. Configs live under `configs/`.

## How to run what exists

```bash
python -m unittest tests.test_hybrid_segmentation tests.test_segmenter_agent tests.test_segmentation_metrics tests.test_schema_and_cfl tests.test_motion_critique tests.test_metadata tests.test_multi_model_benchmark tests.test_partsam_fps tests.test_partsam_surface tests.test_partsam_clicks tests.test_partsam_merge
python scripts/test_all_models.py
python scripts/export_pipeline_data.py
./scripts/run_pipeline.sh
./scripts/run_simulation.sh ficus <exp>
./scripts/run_vasedeck.sh
```

Serve `digest/` as static files so `fetch("data/manifest.json")` works. Tests that import `llm.*` / `eval.*` / `simulation.*` need `PYTHONPATH=src`.

## Next steps

**Material Tag Tensor / PartSAM:** intended producer is wired in `src/segmentation/partsam`; `./scripts/run_pipeline.sh` is PartSAM → PhysGaussian MPM Solver. Policy: [PartSAM as Material Tag Tensor source](../../.scratch/partsam-as-tagger/spec.md).

**Motion Critique Loop:** mock `critique` and driver are in `src/` (`python -m src.llm.critique_loop`); live `critique` is still `NotImplementedError`. `run_pipeline.sh` stays PartSAM → first solver run. Policy: [Motion Critique Loop spec](../../.scratch/mpm-critique-loop/spec.md). Segmenter Agent iteration is plan metrics.

**Potential (unranked):**

- **Tagging leftovers:** LangSAM/voting path; FlashSplat CUDA CLI; digest quality (plane/vasedeck speckle).
- **Live LLM:** implement `MotionTranslator` live `translate` / `critique`; exporters currently force mock.
- **Eval:** implement FVD/KVD/PSNR/SSIM/LPIPS and real sim-vs-GT tests; NASA-TLX subscales vs the current effort timer.
- **Pipeline hygiene:** retire stale scripts/tests; unify imports; digest frames from Warp; Dual-Mode video; `ti.init` in the runner.

Parallel RFC (not superseded): [Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian](../../.scratch/llm-motion-physgaussian/map.md).

## Pointers

| Reach | For |
| --- | --- |
| [README.md](../../README.md) | GitHub visitor clone/install (`third_party/`, `physgauss` + `PartSAM`, `run_pipeline.sh`; FlashSplat optional) |
| [CONTEXT.md](../../CONTEXT.md) | Glossary only (Heuristic Primitive, Segmenter Agent, Material Tag Tensor, PhysGaussian MPM Solver, Digest Dashboard, Dual-Mode Frame Player) |
| [docs/agents/domain.md](domain.md) | How to consume the glossary and ADRs |
| [repo current state](../../.scratch/agent-orientation/research/01-repo-current-state.md) | Working vs stubbed |
| [PartSAM as Material Tag Tensor source](../../.scratch/partsam-as-tagger/spec.md) | PartSAM tagging policy (reach on Material Tag Tensor / PartSAM / intended producer) |
| [Motion Critique Loop spec](../../.scratch/mpm-critique-loop/spec.md) | Post-run human-text retune of `--config` (reach on Motion Critique Loop / `critique` / `critique_loop`) |
| [LLM-motion map](../../.scratch/llm-motion-physgaussian/map.md) | Parallel motion-to-config RFC |
| `.scratch/agent-orientation/historical/` | `Dev Plan.md`, `design_decisions.md`, `digest.md`, legacy `issues/` — sediment, not live instruction |

Root stubs (`Dev Plan.md`, `design_decisions.md`, `digest.md`, `issues/README.md`) point here. `CHANGELOG.md` stays at root as a log, not a task list. Live `digest/` is the dashboard. `Paper_Writing/` is a draft, not agent instructions.
