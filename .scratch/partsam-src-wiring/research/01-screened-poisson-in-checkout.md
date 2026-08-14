# Screened Poisson available in this checkout

Primary sources (2026-08-14): trial [SURFACE.md](../../partsam-ficus-trial/SURFACE.md), [Choose the external ficus mesher](../../partsam-ficus-trial/issues/09-choose-external-mesher.md), [Build the ficus 100k-point surface](../../partsam-ficus-trial/issues/04-build-ficus-surface.md), `.scratch/partsam-ficus-trial/build_poisson_mesh.py`, `sample_and_color.py`; Stage 1 policy [spec.md](../../partsam-as-tagger/spec.md) and [Surface construction for the generic PartSAM recipe](../../partsam-as-tagger/issues/04-surface-construction-generic-recipe.md); `scripts/run_pipeline.sh`; `src/segmentation/heuristics.py`; local `conda run -n physgauss` / `conda run -n PartSAM` import checks. Does not choose `src/` filenames.

## 1. What the ficus trial ran

**Library:** pymeshlab **2023.12.post1**. **Env:** conda `physgauss`. **Input:** Gaussian **means** (xyz), not a pre-existing triangle mesh. [SURFACE.md](../../partsam-ficus-trial/SURFACE.md), [issue 09 Answer](../../partsam-ficus-trial/issues/09-choose-external-mesher.md).

Source PLY: `data/models/ficus_whitebg/point_cloud/iteration_60000/point_cloud.ply` (203 930 vertices). Dummy `nx*` ignored. Script loads xyz + SH DC with `plyfile`, then `pymeshlab.Mesh(vertex_matrix=xyz)` — not `load_new_mesh` of the full Gaussian PLY. [build_poisson_mesh.py](../../partsam-ficus-trial/build_poisson_mesh.py) lines 23–35; [SURFACE.md](../../partsam-ficus-trial/SURFACE.md) step 1–2.

**Calls on `pymeshlab.MeshSet`:**

1. `compute_normal_for_point_clouds()`
2. `generate_surface_reconstruction_screened_poisson()` (defaults; SURFACE.md records `depth=8`)

No ball-pivoting fallback. Mesh reported clickable (pot / trunk / canopy): 159 020 verts / 318 800 faces, not watertight. [SURFACE.md](../../partsam-ficus-trial/SURFACE.md); [issue 04 Answer](../../partsam-ficus-trial/issues/04-build-ficus-surface.md).

Issue 09 rejected Open3D, 2DGS/SuGaR, and TSDF for this trial. Its illustrative one-liner used `load_new_mesh` on the Gaussian PLY then the same two filters; the script that actually wrote `ficus_surface.ply` is `build_poisson_mesh.py` (xyz-only mesh + those filters).

**Downstream of Poisson (not the mesher):** area-weighted 100k sample in conda `PartSAM` via `trimesh.sample.sample_surface` (seed 666) with face normals. [SURFACE.md](../../partsam-ficus-trial/SURFACE.md) step 3; [sample_and_color.py](../../partsam-ficus-trial/sample_and_color.py). Spec Stage 1: algorithm is Screened Poisson from means; mesh is throwaway. [spec.md](../../partsam-as-tagger/spec.md) Stage 1.

## 2. `physgauss` vs `PartSAM` import

`scripts/run_pipeline.sh` runs tagging and the solver with `conda run -n physgauss python -m …` (FlashSplat, color heuristic, runner). Same env name as the trial Poisson step.

Checked locally:

```text
conda run -n physgauss python -c "import pymeshlab; …"
→ pymeshlab 2023.12.post1 at
  /home/q/miniforge3/envs/physgauss/lib/python3.10/site-packages/pymeshlab
  MeshSet has generate_surface_reconstruction_screened_poisson

conda run -n PartSAM python -c "import pymeshlab"
→ ModuleNotFoundError: No module named 'pymeshlab'
  (trimesh 5.0.0 is present; ENV.md lists trimesh, not pymeshlab)
```

`pymeshlab` does not appear in `pyproject.toml` or under `src/`. The checkout’s Screened Poisson call lives in the trial script plus the `physgauss` site-packages install. `src/` can invoke that call **without switching mesher family** by using the same pymeshlab filters in the env `run_pipeline.sh` already uses (`physgauss`). It cannot `import pymeshlab` from the `PartSAM` env as installed for the trial.

## 3. Ball pivoting in the same stack

Spec Stage 1: **ball pivoting only if** the Poisson mesh is unclickable; ficus did not need it. [spec.md](../../partsam-as-tagger/spec.md); [issue 04 (as-tagger)](../../partsam-as-tagger/issues/04-surface-construction-generic-recipe.md); [issue 09](../../partsam-ficus-trial/issues/09-choose-external-mesher.md) (“same library’s ball pivoting”).

In `physgauss` pymeshlab 2023.12.post1, `pymeshlab.filter_list()` includes `generate_surface_reconstruction_ball_pivoting` next to `generate_surface_reconstruction_screened_poisson`. `MeshSet` has both methods. That is the same library/family; no Open3D switch. The trial scripts never call the ball-pivoting filter. This note does not require implementing the fallback.

## 4. SH RGB bake — where the code lives

**SH DC → RGB:** `src.segmentation.heuristics.sh_dc_to_rgb` (`C = clamp(f_dc * SH_C0 + 0.5, 0, 1)`, `SH_C0 = 0.28209479177387814`). [heuristics.py](../../../src/segmentation/heuristics.py). Trial Poisson script imports it and writes `gaussian_xyz.npy` / `gaussian_rgb.npy` from PLY `f_dc_*`. [build_poisson_mesh.py](../../partsam-ficus-trial/build_poisson_mesh.py) lines 19–29; [SURFACE.md](../../partsam-ficus-trial/SURFACE.md) step 1.

**Nearest mean:** after 100k surface sample, `sample_and_color.py` `nearest_rgb` chunks query points and takes `torch.cdist(q, ref).argmin(dim=1)` onto those saved means/RGB (not ValDataset gray 192). [sample_and_color.py](../../partsam-ficus-trial/sample_and_color.py) lines 52–77; [SURFACE.md](../../partsam-ficus-trial/SURFACE.md) step 4; [issue 09](../../partsam-ficus-trial/issues/09-choose-external-mesher.md) Color: yes.

## What `src/` can invoke (no new mesher family)

Without leaving pymeshlab Screened Poisson: `MeshSet.compute_normal_for_point_clouds()` then `generate_surface_reconstruction_screened_poisson()` on Gaussian **means**, in `physgauss` (importable there today). Same-family unclickable fallback exists as `generate_surface_reconstruction_ball_pivoting` in that install; ficus did not use it. Color bake is already in-tree: `sh_dc_to_rgb` plus nearest-mean `cdist` as in the trial sample script. Do not treat Open3D / 2DGS / TSDF / Gaussian-means-as-\(P_{in}\) as this checkout’s Stage 1 path.
