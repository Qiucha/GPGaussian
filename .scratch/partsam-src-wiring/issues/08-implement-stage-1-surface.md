# 08 - Implement Stage 1 surface sample in src/

Type: task
Status: resolved
Blocked by: 01, 03, 04

## Question

Implement Stage 1 in `src/`: trained 3DGS PLY → Screened Poisson from Gaussian means → area-sample 100k with face normals → bake SH RGB from nearest mean via `sh_dc_to_rgb`. Persist the 100k \(P_{in}\). Throw away the Poisson mesh (not solver input).

Use the library from [Screened Poisson available in this checkout](01-screened-poisson-in-checkout.md), paths from [Persist filenames and src/segmentation module tree](03-filenames-and-module-tree.md), tests from [Test contract for the PartSAM seam without publishing weights](04-test-contract-without-weights.md). Ball pivoting only if that mesh is unclickable — not required for ficus. Trial scripts under `.scratch/partsam-ficus-trial/` stay trial.

## Answer

`src/segmentation/partsam/surface.py` is Stage 1: Gaussian means from the checkpoint PLY → pymeshlab Screened Poisson (`compute_normal_for_point_clouds` then `generate_surface_reconstruction_screened_poisson`) → trimesh area-sample 100k (seed 666) with face normals → nearest-mean `sh_dc_to_rgb` bake. Persist `data/outputs/partsam/sample_100k.npz` (`coords`, `normals`, `colors` uint8, `point_to_face`). Throwaway debug mesh: `poisson_mesh.ply` in the same dir (not solver input). Skip if `sample_100k.npz` already exists.

CLI: `python -m src.segmentation.partsam --model_path <3dgs-dir> --stage surface` (`--output_dir` default `data/outputs/partsam/`). Clicks/lift still `NotImplementedError`. Always-on tests: `tests/test_partsam_surface.py` (fixture writer + skip-if-exists; no Poisson). Live sample still needs `pip install trimesh` in `physgauss` (not in that env today). Ball pivoting not implemented (ficus did not need it).

## Comments
