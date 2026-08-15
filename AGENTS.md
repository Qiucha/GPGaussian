## Agent skills

### Orientation

**Orientation** — purpose, current state, and next steps (including PartSAM): [docs/agents/orientation.md](docs/agents/orientation.md). Reach when starting work, choosing the next experiment, or judging whether a markdown file is live instruction.

### Issue tracker

Issues live as markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical roles map 1:1 onto `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Cursor Cloud specific instructions

The cloud VM is **CPU-only with no CUDA/GPU and no conda**. The repo's `setup_env.sh` / `setup_phase2.sh` (conda `physgauss_v2`, CUDA toolkit, GroundingDINO/SAM2) do **not** apply here and should not be run. The update script instead installs CPU deps into a gitignored venv at `.venv` (`torch` CPU wheel, `numpy`, `scipy`, `scikit-learn`, `plyfile`, `pillow`). Run everything with `.venv/bin/python` (or `source .venv/bin/activate`).

**What runs here (the offline "delta" surface):**
- Unit tests — the 11 offline modules listed in `docs/agents/orientation.md` ("How to run what exists"). They need `PYTHONPATH=src` because of mixed `from llm.*` vs `from src.*` imports. Run from the repo root: `PYTHONPATH=src .venv/bin/python -m unittest tests.test_hybrid_segmentation tests.test_segmenter_agent tests.test_segmentation_metrics tests.test_schema_and_cfl tests.test_motion_critique tests.test_metadata tests.test_multi_model_benchmark tests.test_partsam_fps tests.test_partsam_surface tests.test_partsam_clicks tests.test_partsam_merge`. The core Segmenter-Agent → Material-Tag-Tensor path (`SegmenterAgent(mock_llm=True).execute_with_iterative_refinement`) is fully CPU/offline.
- Digest Dashboard — static app under `digest/`; serve with `.venv/bin/python -m http.server 8000` from `digest/` and open `http://localhost:8000/`. It loads Three.js/Font Awesome from CDNs (needs outbound network) and reads `digest/data/` (gitignored, not present until generated).

**Gotchas / can't-run-here (needs CUDA and/or gitignored 3DGS checkpoints):** the PhysGaussian MPM solver + runner (`src/simulation/`), rasterization (`src/rendering/rasterize.py`, imports the absent `vendor/gaussian-splatting`), PartSAM lift, and the `scripts/run_*.sh` pipelines. `scripts/export_pipeline_data.py` is CPU-only in principle but imports the vendor 3DGS rasterizer at module load and expects real checkpoints under `data/models/*/point_cloud`, so it does not run as-is; `scripts/verify_digest_assets.py` hard-requires the 6 canonical exported scenes. To demo the dashboard without checkpoints, populate `digest/data/` by calling the real `extract_scene_metadata` + `SegmenterAgent` + `SegmentationEvaluator` on a synthetic point cloud (do **not** import `scripts/export_pipeline_data` directly — it fails on the missing vendor rasterizer). Do not run the stale entry points called out in the orientation doc (`scripts/run_pipeline.py`, `scripts/run_experiment.sh`, `tests/test_pipeline.py`, `tests/test_projection.py`).
