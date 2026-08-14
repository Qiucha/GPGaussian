# 04 - Replace in-tree PhysGaussian copies with upstream imports

Type: task
Status: resolved
Blocked by: 01

## Question

(Nothing to decide: the destination forbids dumping PhysGaussian sources.) Perform the work to stop shipping copied PhysGaussian files from `src/` and `configs/` where they are upstream copies; keep only the Phys4DGS delta (e.g. materials/segmentation extensions); wire imports to a documented clone path from How to consume PhysGaussian as upstream instead of in-tree copies.

## Answer

Wired clones via `src/upstream.py` (`PHYSGAUSSIAN_ROOT` / `third_party/PhysGaussian`, fallback `.trash/PhysGaussian` in this workspace; 3DGS from the PhysGaussian submodule or `vendor/gaussian-splatting`; FlashSplat via `FLASHSPLAT_ROOT` / `vendor/FlashSplat`).

Removed in-tree copies: `src/simulation/mpm_solver/*`, `src/simulation/particle_filling/filling.py`, and identical scene JSONs (`pillow2sofa`, `plane`, `tear_bread`, `vasedeck`, `wolf`). Kept overlay: `src/simulation/config.py` (`materials`), `lame_params.py`, thin `src/rendering/camera.py` (`gt_depth`), `checkpoint.py`, `configs/ficus.json`, `configs/vasedeck_multi_material.json`. `runner.py` now imports `mpm_solver_warp` / `particle_filling` from the clone. `src/__init__.py` no longer prepends both GS and FlashSplat onto `sys.path`.
