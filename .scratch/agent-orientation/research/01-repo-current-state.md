# 01 — Repo current state (as built)

Primary sources: `src/`, `scripts/`, `tests/`, `configs/`, `digest/`, `data/experiments/`, `vendor/`, `pyproject.toml`, `CONTEXT.md`. Not used as authority: `Dev Plan.md`, paper drafts. Glossary: Heuristic Primitive, Segmenter Agent, Material Tag Tensor, PhysGaussian MPM Solver, Digest Dashboard, Dual-Mode Frame Player.

Persisted by the parent wayfinder session after research subagents completed the investigation but could not write files (execution backend down).

## 1. Purpose in code

The pipeline **loads a trained 3DGS PLY**, assigns a **Material Tag Tensor**, maps tags to per-particle `E` / `nu` / `density`, **advances particles with Warp MPM**, then **re-rasterizes moved Gaussians**. Time variation is MPM motion. There is **no 4DGS trainer** in `src/` (no deformation-field / HexPlane / Yang-style optimization loop).

- Packaging name only: `pyproject.toml` (description “Physics-based 4D Gaussian Splatting”).
- Load PLY: `src/rendering/checkpoint.py` (`GaussianModel.load_ply`); duplicate in `src/simulation/runner.py`.
- Tags: `src/simulation/runner.py` (`material_tags.pt` / `init_tags`); Lamé: `src/simulation/lame_params.py`.
- Solver: `src/simulation/mpm_solver/solver.py` (`MPM_Simulator_WARP`); `p2g2p` in `src/simulation/runner.py`.
- Rasterize: `src/rendering/rasterize.py` (`diff_gaussian_rasterization`); optional ffmpeg in the runner.
- Segmenter Agent → Material Tag Tensor `(N,)`: `src/llm/segmenter_agent.py`.

## 2. Working vs stubs / broken

**Working (wired in `src/` and/or tested):**

- Heuristic Primitives + `HeuristicRegistry`: `src/segmentation/heuristics.py`; `tests/test_hybrid_segmentation.py`.
- Segmenter Agent with default `mock_llm=True` and rule-based fallback: `src/llm/segmenter_agent.py`; `tests/test_segmenter_agent.py`.
- Scene metadata: `src/segmentation/metadata.py`.
- Plan schema + CFL validator: `src/llm/schema.py`, `src/llm/validator.py`.
- Segmentation quality metrics: `src/segmentation/metrics.py`.
- Motion library + mock MotionTranslator: `src/llm/motion_library.py`, `src/llm/translator.py`.
- Eval: Kabsch trajectory MSE + 2AFC: `src/eval/evaluate_realism.py`. Effort timer (wall-clock, LOC, iterations — not NASA-TLX subscales): `src/eval/evaluate_effort.py`.
- Per-particle Lamé + PhysGaussian MPM Solver + runner CLI: `src/simulation/lame_params.py`, `src/simulation/mpm_solver/solver.py`, `src/simulation/runner.py`.
- Digest Dashboard UI: `digest/index.html`, `digest/app.js`, `digest/style.css`.
- Digest export: `scripts/export_pipeline_data.py` (mock Segmenter Agent + **PIL 2D fake “MPM” frames**, not Warp).
- Ficus / vasedeck heuristic CLIs; `scripts/run_pipeline.sh` (FlashSplat → color heuristic → runner); `scripts/run_simulation.sh`; `scripts/run_vasedeck.sh`; `scripts/test_all_models.py`.

**Stubs / incomplete:**

- Live MotionTranslator: `mock_llm=False` raises `NotImplementedError` (`src/llm/translator.py`).
- `ConfigGenerator` always wraps `MotionTranslator(mock_llm=True)` (`src/utils/llm_generator.py`).
- LangSAM: missing `lang_sam` → empty masks (`src/segmentation/langsam_segmenter.py`).
- FVD / KVD / PSNR / SSIM / LPIPS: named in `evaluate_realism.py` docstring; **not implemented** as functions.
- Dual-Mode Frame Player: glossary says canvas + HTML5 video; UI is `<img>` + slider only (`digest/index.html`).
- `scripts/run_pipeline.py`: 3D projection commented out; writes empty `material_tags.pt`.
- `src/simulation/runner.py` calls `ti.init` without importing taichi in that module.

**Broken / stale:**

- `scripts/run_pipeline.py` and `tests/test_pipeline.py` import top-level `bbox_extraction`, `llm_generator`, etc. (`bbox_extraction` lives under `.trash/`).
- `tests/test_projection.py` points at `tests/PhysGaussian` and `model/ficus_whitebg-trained`.
- `scripts/run_experiment.sh` calls `pipeline.py` / `run_flashsplat.py` at CWD (those names live under `.trash/`).
- Mixed test imports: `from llm.translator` vs `from src.*`.

## 3. Vendor

- **`vendor/gaussian-splatting` is load-bearing:** `src/__init__.py` puts it on `sys.path`; `GaussianModel` and `diff_gaussian_rasterization` are imported from `src/rendering/checkpoint.py`, `src/rendering/rasterize.py`, `src/simulation/runner.py`.
- **`vendor/FlashSplat` is tagging-only:** executed from `src/segmentation/flashsplat.py` and `scripts/run_pipeline.sh`. MPM frames use 3DGS `GaussianRasterizer`, not FlashSplat.

## 4. Experiments and digest

**`data/experiments/`:** four note files plus `exp_4_stiffer_trunk_finer_dt/ficus_config.json`. Notes record ficus wind/sway; exp 4 still “trunk does not fully rebound”. **No `output.mp4` in the tree** (`scripts/run_simulation.sh` would copy one after a successful run).

**`digest/`:** app + `digest/data/manifest.json` and per-model JSON for six scenes (bread, ficus, pillow2sofa, plane, vasedeck, wolf). Manifest quality numbers are mock-agent export. Trajectory images, if present, are the exporter’s PIL animation, not Warp renders. Frame JPEGs may be missing even when the verifier expects 30 frames (`scripts/verify_digest_assets.py`).

**`configs/`:** `ficus.json`, `vasedeck.json`, `vasedeck_multi_material.json`, `wolf.json`, `plane.json`, `pillow2sofa.json`, `tear_bread.json`.

## 5. How to run what exists

```bash
python -m unittest tests.test_hybrid_segmentation tests.test_segmenter_agent tests.test_segmentation_metrics tests.test_schema_and_cfl tests.test_metadata tests.test_multi_model_benchmark
# tests using llm./eval./simulation. need PYTHONPATH=src
python scripts/test_all_models.py
python scripts/export_pipeline_data.py
python scripts/verify_digest_assets.py
# serve digest/ so fetch("data/manifest.json") works
./scripts/run_pipeline.sh          # ficus FlashSplat + MPM + ffmpeg
./scripts/run_simulation.sh ficus <exp>
./scripts/run_vasedeck.sh
python -m src.segmentation.flashsplat --model_path ... --masks_dir ... --output_dir ... --prompts ...
```

Do **not** run `python scripts/run_pipeline.py` or `./scripts/run_experiment.sh`.

## 6. Candidate next steps after PartSAM (unranked)

- **Tagging:** heuristics + Segmenter Agent already tag without 2D lift; LangSAM/voting path unfinished; FlashSplat is a separate CUDA CLI; digest speckle/silhouette leftovers; RFC hybrid LangSAM+SH+DBSCAN is not one production path.
- **Live LLM:** `MotionTranslator` live API unimplemented; exporters force mock; LLM-motion map leftover “LLM Real-Time Feedback Loop”; in-repo refinement is segmentation-plan mock insert of `superpoint_graph`, not video critique of MPM params.
- **Eval:** Kabsch/2AFC/effort exist; FVD/KVD/PSNR/SSIM/LPIPS and NASA-TLX subscales do not; no real sim-vs-GT tests.
- **Pipeline hygiene:** retire/fix stale scripts/tests; unify imports; `ti.init`; digest frames ≠ Warp; Dual-Mode missing video; map leftover custom CUDA per-particle decode.

LLM-motion map leftovers cited from `.scratch/llm-motion-physgaussian/map.md` only as fog, not as this repo’s current `src/` behavior.
