# 09 - Choose the external ficus mesher

Type: grilling
Status: resolved
Blocked by: none

## Question

[Ficus Gaussians to a 100k ValDataset-style sample](02-ficus-surface-sample.md) found this repo has **no mesher**. PartSAM `ValDataset` needs a **triangle mesh** (faces) before sampling 100k points with face normals and color. Ficus Gaussians are a vertex-only PLY at `data/models/ficus_whitebg/point_cloud/iteration_60000/point_cloud.ply` (203 930 points; dummy normals; SH color via `sh_dc_to_rgb`).

Which **external** reconstruction should [Build the ficus 100k-point surface](04-build-ficus-surface.md) use for this trial?

Options to confirm, replace, or reject:

- Poisson / Screened Poisson from Gaussian means (Open3D or similar)
- 2DGS / SuGaR / other Gaussian-to-mesh tool
- Marching cubes / TSDF from rendered depth
- Something already on this machine

Also: bake SH RGB onto the mesh, or let ValDataset default gray 192?

Resolve with: tool + one-line command/path + color yes/no. Findings: [02-ficus-surface-sample.md](../research/02-ficus-surface-sample.md).

## Answer

**Tool:** pymeshlab 2023.12.post1 Screened Poisson in conda env `physgauss` (`/home/q/miniforge3/envs/physgauss`). Not Open3D, 2DGS/SuGaR, or TSDF. Thin-leaf blobbing is acceptable if pot / trunk / canopy stay clickable; if the mesh is unclickable, [Build the ficus 100k-point surface](04-build-ficus-surface.md) may fall back to the same library’s ball pivoting.

**Command** (source: `data/models/ficus_whitebg/point_cloud/iteration_60000/point_cloud.ply`; dummy Gaussian normals must be replaced before Poisson):

```bash
/home/q/miniforge3/envs/physgauss/bin/python -c "
import pymeshlab
ms = pymeshlab.MeshSet()
ms.load_new_mesh('data/models/ficus_whitebg/point_cloud/iteration_60000/point_cloud.ply')
ms.compute_normal_for_point_clouds()
ms.generate_surface_reconstruction_screened_poisson()
ms.save_current_mesh('.scratch/partsam-ficus-trial/ficus_surface.ply')
"
```

**Color: yes.** After ValDataset-style 100k surface sample, bake SH RGB from the nearest Gaussian mean via this repo’s `sh_dc_to_rgb`. Do not use ValDataset gray 192.
