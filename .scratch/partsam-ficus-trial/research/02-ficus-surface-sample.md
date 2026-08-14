# Ficus Gaussians → PartSAM ValDataset-style 100k sample

Sources: this tree plus PartSAM `utils/ValDataset.py` and `configs/partsam.yaml` (czvvd/PartSAM). Not a built surface.

## PartSAM contract

`configs/partsam.yaml`: `num_points: 100000`; `dataset.root_dir` is mesh files.

`ValDataset`: walks `.glb` / `.ply` / `.obj`; `trimesh.load(..., force='mesh')`; bbox-center and scale `2.0 * 0.9 / extent`; `_sample_points` → `sample_surface(mesh, count=num_points, sample_color=True)` (`utils/point.py`). Returns `coords`, `normal` = `mesh.face_normals[point_to_face]` (else ones), `color` (else uint8 gray 192), `point_to_face`, `vertices`, `faces`. Sampling needs **faces and area**.

Eval collate uses `prep_points_train(..., eval=True)` (center/normalize/color, no train aug).

## Where ficus lives

Canonical path used by `scripts/run_pipeline.sh` / `scripts/run_simulation.sh`:

`data/models/ficus_whitebg/` (`cameras.json`, `input.ply`, `point_cloud/`).

`src/rendering/checkpoint.py` `load_checkpoint(model_path)` → `point_cloud/iteration_{max}/point_cloud.ply` via `searchForMaxIteration` (`vendor/gaussian-splatting/utils/system_utils.py`). On disk: iterations **7000** (189 685 verts), **30000** and **60000** (both **203 930** verts, same size). Default load is **60000**. Nested copy: `data/models/ficus_whitebg/ficus_whitebg-trained/...`. Stale paths: `model/ficus_whitebg-trained` (`scripts/debug/*`, `tests/test_projection.py`). Gitignores `data/` and `*.ply`.

`input.ply`: 100 000 verts, `x,y,z,nx,ny,nz,red,green,blue`, **no faces**. SfM init, not a ValDataset mesh. Do not treat as the 100k sample.

## Gaussian attributes (trained PLY)

Header (iter 30000/60000): vertex-only `x,y,z`, `nx,ny,nz`, `f_dc_0..2`, `f_rest_*`, `opacity`, `scale_*`, `rot_*`. No `element face`.

`GaussianModel.load_ply` (`vendor/gaussian-splatting/scene/gaussian_model.py`) reads xyz, SH DC/rest, opacity, scales, rotations. **Ignores nx/ny/nz.** `save_ply` writes `normals = np.zeros_like(xyz)`.

This repo uses: `gaussians._xyz`, `_features_dc`, `_scaling` (`src/segmentation/color_heuristic.py`, `src/segmentation/metadata.py`). RGB: `sh_dc_to_rgb` — `C = clamp(f_dc * 0.28209479177387814 + 0.5, 0, 1)` (`src/segmentation/heuristics.py`). k-NN PCA normals exist only inside `SurfaceNormalCurvatureHeuristic` (tagging), not as an export.

## Mesh / export in this repo

**No mesher in `src/`.** No trimesh/Open3D/Poisson/TSDF/marching cubes. `scripts/export_pipeline_data.py` writes digest JSON (downsample to 8 000 means + SH RGB), not a mesh. Runner `--output_ply` is MPM particle dumps, not reconstruction. Vendor 3DGS SIBR mesh helpers are COLMAP/RC dataset preprocess, not 3DGS→surface. Ficus dir has no `.obj`/`.glb`/mesh.

Feeding the Gaussian PLY (or means) to `ValDataset` is not the eval path: `force='mesh'` + `sample_surface` need faces; PLY `nx*` are zeros; color is SH, not vertex RGB.

## Smallest path (facts, not a build)

1. Load latest Gaussians: `load_checkpoint("data/models/ficus_whitebg")` → iter 60000 `point_cloud.ply` (203 930).
2. **External** (missing here): reconstruct a triangle mesh from those Gaussians (or another surface recon). Optional: bake vertex/face RGB via `sh_dc_to_rgb`; else ValDataset uses gray 192.
3. Sample as ValDataset: `num_points=100000`, `sample_surface` + face normals + colors, then their bbox normalize.

That is the ValDataset-style input. Gaussian-mean subsample / `input.ply` / k-NN normals are not that contract.
