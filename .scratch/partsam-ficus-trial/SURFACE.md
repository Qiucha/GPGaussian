# Ficus throwaway surface (trial)

Built for [Build the ficus 100k-point surface](issues/04-build-ficus-surface.md) using [Choose the external ficus mesher](issues/09-choose-external-mesher.md).

## How

1. Read `data/models/ficus_whitebg/point_cloud/iteration_60000/point_cloud.ply` (203 930 Gaussian means). Dummy `nx*` ignored. SH DC → RGB via `src.segmentation.heuristics.sh_dc_to_rgb`.
2. Screened Poisson in conda `physgauss` / pymeshlab 2023.12.post1: `compute_normal_for_point_clouds()` then `generate_surface_reconstruction_screened_poisson()` (defaults, `depth=8`). No ball-pivoting fallback — mesh shows pot / trunk / canopy.
3. Area-weighted 100k surface sample (`trimesh.sample.sample_surface`, seed 666) with face normals, in conda `PartSAM`.
4. Bake vertex RGB from nearest Gaussian mean (torch `cdist`). Not ValDataset gray 192.

Scripts: `build_poisson_mesh.py` (physgauss), `sample_and_color.py` (PartSAM).

## Artifacts

| File | What |
| --- | --- |
| `ficus_surface.ply` | Triangle mesh, 159 020 verts / 318 800 faces, not watertight |
| `ficus_100k.ply` | 100k xyz + normals + uchar RGB (PartSAM-ready) |
| `ficus_100k.npz` | `coords`, `normals`, `colors` (uint8), `point_to_face` |
| `ficus_100k_preview.png` | xy / xz / yz scatter of 12k points |
| `gaussian_xyz.npy` / `gaussian_rgb.npy` | Means + SH RGB used for the bake (and later NN lift) |

World-space (Gaussian frame). Bbox-normalize at inference the same way `ValDataset` does.
