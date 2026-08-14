# Orientation

Read this when starting work on Phys4DGS, choosing the next experiment, or judging whether a markdown file is live instruction. Glossary: [CONTEXT.md](../../CONTEXT.md). Sourced facts: [repo current state](../../.scratch/agent-orientation/research/01-repo-current-state.md), [PartSAM tagging gap](../../.scratch/agent-orientation/research/02-partsam-tagging-gap.md). This file is the cache of unwritten convention; commands and module paths live in the tree.

## Purpose

Phys4DGS runs **heterogeneous MPM on trained 3D Gaussian Splatting (3DGS) scenes**. A **Material Tag Tensor** labels each Gaussian; those labels become per-particle Lamé parameters; the **PhysGaussian MPM Solver** moves the particles in time; frames are re-rasterized 3DGS.

The “4D” in the name is **time-varying 3DGS particles under physics**. There is no Yang-style 4D Gaussian trainer in `src/` (no deformation field / HexPlane optimization loop). Packaging text in `pyproject.toml` is the name, not a trainer.

## Pipeline as built

1. Load a trained 3DGS PLY (`src/rendering/checkpoint.py`, `src/simulation/runner.py`).
2. Produce a Material Tag Tensor `(N,)` — Heuristic Primitives via the **Segmenter Agent**, or FlashSplat / scene heuristics writing `material_tags.pt`.
3. Map tags → `E`, `nu`, `density` → Lamé (`src/simulation/lame_params.py`).
4. Step the PhysGaussian MPM Solver (`src/simulation/mpm_solver/solver.py`, `MPM_Simulator_WARP`).
5. Rasterize moved Gaussians (`src/rendering/rasterize.py`). Inspect tags and (when present) frames in the **Digest Dashboard** (`digest/`).

## Current state

**Works offline:** Heuristic Primitives (`src/segmentation/heuristics.py`); Segmenter Agent with `mock_llm=True`; schema/CFL; mock MotionTranslator; Kabsch trajectory MSE and 2AFC; Warp runner; Digest Dashboard UI; `scripts/run_pipeline.sh` (FlashSplat → color heuristic → runner).

**Stubbed or incomplete:** live MotionTranslator (`NotImplementedError`); LangSAM empty without `lang_sam`; FVD/KVD/PSNR/SSIM/LPIPS named but unimplemented; Dual-Mode Frame Player is image scrubbing only (glossary also names HTML5 video); digest “MPM” frames from `scripts/export_pipeline_data.py` are PIL offsets, not Warp; `scripts/run_pipeline.py` writes an empty tag tensor.

**Stale entry points (use the `.sh` runners instead):** `scripts/run_pipeline.py`, `scripts/run_experiment.sh`, `tests/test_pipeline.py`, `tests/test_projection.py`.

Full tables and paths: [repo current state](../../.scratch/agent-orientation/research/01-repo-current-state.md).

## Vendor and experiments

- **`vendor/gaussian-splatting`** is load-bearing (checkpoint + rasterizer via `src/__init__.py`).
- **`vendor/FlashSplat`** is tagging-only (`src/segmentation/flashsplat.py`). MPM frames use 3DGS rasterization.

`data/experiments/` holds ficus wind/sway **notes** (trunk still does not fully rebound in exp 4). No archived `output.mp4` in the tree. `digest/data/` JSON for six scenes is mock-agent export, not Warp video. Configs live under `configs/`.

## How to run what exists

```bash
python -m unittest tests.test_hybrid_segmentation tests.test_segmenter_agent tests.test_segmentation_metrics tests.test_schema_and_cfl tests.test_metadata tests.test_multi_model_benchmark
python scripts/test_all_models.py
python scripts/export_pipeline_data.py
./scripts/run_pipeline.sh
./scripts/run_simulation.sh ficus <exp>
./scripts/run_vasedeck.sh
```

Serve `digest/` as static files so `fetch("data/manifest.json")` works. Tests that import `llm.*` / `eval.*` / `simulation.*` need `PYTHONPATH=src`.

## Next steps

**Immediate:** try **PartSAM** (arXiv:2509.21965, https://github.com/czvvd/PartSAM) as a **native-3D part decomposer** that could feed a Material Tag Tensor.

**Trial recipe** (execute in a later effort): [PartSAM trial design (scene, I/O, success)](../../.scratch/agent-orientation/issues/06-partsam-trial-design.md) — ficus; throwaway surface → 100k points with normals + color; three click groups (pot, trunk, leaves); priority merge + nearest-neighbor → `material_tags.pt`; pass = ingestible tags (trunk > 1 000) plus a short PhysGaussian MPM Solver run that does not immediately explode.

Why: 2D lift (LangSAM + FlashSplat / projection) is the tagging bottleneck; Grounded SAM 2 was abandoned; Heuristic Primitives are scene-specific. PartSAM takes a 100k-point cloud (xyz, normals, optional RGB) plus **3D clicks** and emits **class-agnostic part masks**.

Treat PartSAM as that decomposer. Map parts → material IDs and Lamé parameters in this repo. The PhysGaussian MPM Solver stays the solver. LangSAM is 2D text-SAM; FlashSplat assigns 2D masks onto Gaussians; PartField is clustering / PartSAM’s frozen encoder, not this repo’s tagger.

Constraints (stated by their repo/paper): weights on Hugging Face `Czvvd/PartSAM`; PyTorch 2.4.1 + CUDA 12.4; PartSAM code MIT, `partfield/` NVIDIA non-commercial. Detail: [PartSAM tagging gap](../../.scratch/agent-orientation/research/02-partsam-tagging-gap.md).

**Potential (unranked):**

- **Tagging:** finish or retire the LangSAM/voting path; FlashSplat remains a CUDA CLI; digest quality leftovers (plane/vasedeck speckle).
- **Live LLM:** implement `MotionTranslator` live API; exporters currently force mock. Closed-loop MPM critique from video is leftover fog on the LLM-motion map, not in-repo behavior (in-repo “refinement” is segmentation-plan metrics).
- **Eval:** implement FVD/KVD/PSNR/SSIM/LPIPS and real sim-vs-GT tests; NASA-TLX subscales vs the current effort timer.
- **Pipeline hygiene:** retire stale scripts/tests; unify imports; digest frames from Warp; Dual-Mode video; `ti.init` in the runner.

Parallel RFC (not superseded): [Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian](../../.scratch/llm-motion-physgaussian/map.md).

## Pointers

| Reach | For |
| --- | --- |
| [CONTEXT.md](../../CONTEXT.md) | Glossary only (Heuristic Primitive, Segmenter Agent, Material Tag Tensor, PhysGaussian MPM Solver, Digest Dashboard, Dual-Mode Frame Player) |
| [docs/agents/domain.md](domain.md) | How to consume the glossary and ADRs |
| [repo current state](../../.scratch/agent-orientation/research/01-repo-current-state.md) | Working vs stubbed, vendor, run commands |
| [PartSAM tagging gap](../../.scratch/agent-orientation/research/02-partsam-tagging-gap.md) | PartSAM I/O vs this tagging path |
| [LLM-motion map](../../.scratch/llm-motion-physgaussian/map.md) | Parallel motion-to-config RFC and its leftover fog |
| `.scratch/agent-orientation/historical/` | `Dev Plan.md`, `design_decisions.md`, `digest.md`, legacy `issues/` — sediment, not live instruction |

Root stubs (`Dev Plan.md`, `design_decisions.md`, `digest.md`, `issues/README.md`) point here. `CHANGELOG.md` stays at root as a log, not a task list. Live `digest/` is the dashboard. `Paper_Writing/` is a draft, not agent instructions.
