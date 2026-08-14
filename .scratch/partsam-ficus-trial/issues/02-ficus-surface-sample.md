# 02 - Ficus Gaussians to a 100k ValDataset-style sample

Type: research
Status: resolved
Blocked by: none

## Question

How can this repo’s **ficus_whitebg** Gaussians become a PartSAM `ValDataset`-style input (mesh or point cloud, ~100k points, normals + color) without guessing?

Cover from **this tree** plus PartSAM `ValDataset.py` / `configs/partsam.yaml`: where the ficus PLY/checkpoint lives, what attributes Gaussians have (xyz, SH, scales), any existing mesh/export, and the **smallest** reconstruction path that yields 100k samples with normals and color. Cite paths. If no mesher exists in-repo, say so and list the minimum external step (still a fact about what’s missing, not a design essay).

Write a **short** findings file (< 120 lines) to `.scratch/partsam-ficus-trial/research/02-ficus-surface-sample.md`. Resolve with gist + pointer. Do not build the surface.

## Answer

ValDataset needs a **triangle mesh** (faces) sampled to 100k with face normals + color (`num_points: 100000`). Ficus Gaussians live at `data/models/ficus_whitebg/point_cloud/iteration_60000/point_cloud.ply` (203 930 verts; xyz, zero `nx*`, SH, opacity, scale, rot — no faces). This repo has **no mesher**. Smallest path: external mesh from those Gaussians, optional `sh_dc_to_rgb` bake, then ValDataset `sample_surface`. `input.ply` is a 100k SfM cloud, not that sample.

Findings: [02-ficus-surface-sample.md](../research/02-ficus-surface-sample.md)
