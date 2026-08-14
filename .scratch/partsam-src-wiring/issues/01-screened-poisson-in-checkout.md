# 01 - Screened Poisson available in this checkout

Type: research
Status: resolved
Blocked by: none

## Question

Which library and call in **this checkout** actually runs Screened Poisson from Gaussian means for Stage 1, and what can `src/` invoke without switching mesher family?

Cover, from primary sources only (trial notes and scripts, `physgauss` / `PartSAM` env usage, in-tree Python):

1. What the ficus trial ran (library, env, input = Gaussian means vs mesh) — [SURFACE.md](../../partsam-ficus-trial/SURFACE.md), [Choose the external ficus mesher](../../partsam-ficus-trial/issues/09-choose-external-mesher.md), build scripts.
2. Whether that library is importable from the env `run_pipeline.sh` uses (`physgauss`) vs only from `PartSAM`.
3. Ball-pivoting availability in the same stack (spec: only if Poisson is unclickable; do not require implementing it).
4. SH RGB bake: trial `sh_dc_to_rgb` + nearest mean — where that code lives.

Write findings to `.scratch/partsam-src-wiring/research/01-screened-poisson-in-checkout.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** choose `src/` filenames or the module tree.

## Answer

Screened Poisson in this checkout is pymeshlab 2023.12.post1 in conda `physgauss` (`run_pipeline.sh`’s env): `MeshSet.compute_normal_for_point_clouds()` then `generate_surface_reconstruction_screened_poisson()` on Gaussian means (ficus trial `build_poisson_mesh.py`; not Open3D; `pymeshlab` is not importable from `PartSAM`). Same-library ball pivoting is `generate_surface_reconstruction_ball_pivoting` (unclickable fallback only; not run). SH RGB bake is `src.segmentation.heuristics.sh_dc_to_rgb` plus nearest-mean `torch.cdist` in `sample_and_color.py`. Findings: [research/01-screened-poisson-in-checkout.md](../research/01-screened-poisson-in-checkout.md).

## Comments
