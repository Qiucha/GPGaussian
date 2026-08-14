# 04 - Surface construction for the generic PartSAM recipe

Type: grilling
Status: resolved
Blocked by: none

## Question

For a **generic** scene (ficus is evidence, not the only scene the spec describes), how does this repo produce PartSAM’s 100k xyz+normals+RGB \(P_{in}\) from a trained 3DGS PLY?

The trial used Screened Poisson in `physgauss` from Gaussian means, then baked SH RGB ([Choose the external ficus mesher](../../partsam-ficus-trial/issues/09-choose-external-mesher.md), [SURFACE.md](../../partsam-ficus-trial/SURFACE.md)). Paper/eval sample a triangle mesh, not Gaussian means.

Decide the lasting recipe the spec will write: keep Poisson-from-means, name a different mesher, or treat Gaussian means as \(P_{in}\) (not specified by PartSAM). Do not run another mesher in this ticket.

## Answer

Generic \(P_{in}\): **Screened Poisson from Gaussian means** → area-sample 100k with face normals → **bake SH RGB** from the nearest mean via `sh_dc_to_rgb`. The mesh is a throwaway adapter into PartSAM, not a Material Tag Tensor and not solver input.

The spec names the **algorithm**, not pymeshlab/`physgauss` (ficus trial is evidence). **Ball pivoting** is the only fallback if Poisson is unclickable; do not run it in this effort. Rejected: Gaussian means as \(P_{in}\); a different mesher family; requiring a pre-existing scene mesh.

