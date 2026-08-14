# 01 - How to consume PhysGaussian as upstream instead of in-tree copies

Type: research
Status: resolved
Blocked by: none

## Question

Given that Phys4DGS currently runs on path-rewritten copies of PhysGaussian (`src/simulation/mpm_solver/*`, `src/simulation/particle_filling/filling.py`, `src/simulation/runner.py`, `src/simulation/config.py`, `src/rendering/*`, `configs/*.json`) rather than a git submodule: what does the official [XPandora/PhysGaussian](https://github.com/XPandora/PhysGaussian) repository specify for license, layout, and intended use, and what is the concrete consume-as-upstream pattern for this repo (clone location, import path, which of our files are identical copies vs a real delta we must keep)?

Primary sources: the official GitHub repo (README, LICENSE, layout), plus a file-level diff against `.trash/PhysGaussian/` and `src/`. Do not recommend re-uploading the clone.

## Answer

Official PhysGaussian has **no LICENSE file** on GitHub (cite Xie et al.). It is a script-root clone (`git clone --recurse-submodules`) with `gs_simulation.py`, `mpm_solver_warp/`, `particle_filling/`, `utils/`, and a `gaussian-splatting` submodule — not a pip package. Consume via a gitignored clone at `third_party/PhysGaussian` (workspace pin `8339ed6`); put that root and its `gaussian-splatting` submodule on `sys.path` for simulation only. Drop identical/import-rewritten copies (`mpm_solver/*`, `filling.py`, rendering utils, `runner.py` as a fork of `gs_simulation.py`). Keep overlay: `materials` in config decode, `lame_params.py`, tiny helpers such as `gt_depth` on the camera path, Phys4DGS-only configs. Do not re-upload `.trash/PhysGaussian` or `vendor/`.

Full map: [research/physgaussian-upstream.md](../research/physgaussian-upstream.md)
