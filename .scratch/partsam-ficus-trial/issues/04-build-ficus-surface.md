# 04 - Build the ficus 100k-point surface

Type: task
Status: resolved
Blocked by: 02, 09

## Question

Build the throwaway ficus surface sample using the path in [Ficus Gaussians to a 100k ValDataset-style sample](02-ficus-surface-sample.md). Write artifacts under `.scratch/partsam-ficus-trial/` (mesh/points + a short note of how they were made).

Done when a 100k-point cloud with normals and color exists on disk, ready for PartSAM.

## Answer

Throwaway surface is on disk. Screened Poisson (pymeshlab / `physgauss`) from iter-60000 means → `ficus_surface.ply` (159 020 verts, 318 800 faces, not watertight). 100k area-weighted sample with face normals + nearest-mean SH RGB → `ficus_100k.ply` / `ficus_100k.npz`. Preview shows pot / trunk / canopy; no ball-pivoting fallback.

Note: [SURFACE.md](../SURFACE.md). Preview: [ficus_100k_preview.png](../ficus_100k_preview.png).
