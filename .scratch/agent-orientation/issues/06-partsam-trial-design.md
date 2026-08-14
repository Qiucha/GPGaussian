# 06 - PartSAM trial design (scene, I/O, success)

Type: grilling
Status: resolved
Blocked by: none

## Question

The orientation pack names PartSAM as the immediate next experiment. Design the **first trial** (not the full integration spec):

1. Which scene (ficus is the historical benchmark; confirm or pick another)?
2. What input representation for PartSAM (mesh vs Gaussian means as \(P_{in}\); normals/color)?
3. What output mapping to a Material Tag Tensor (Segment-Every-Part vs clicks; how parts become material IDs)?
4. What is a checkable success criterion for the trial (e.g. trunk/leaf/pot tags on ficus that the PhysGaussian MPM Solver can ingest)?

Use [PartSAM tagging gap](../research/02-partsam-tagging-gap.md) and [Orientation](../../../docs/agents/orientation.md). Stay inside a trial recipe; a full API/code-seam spec remains out of this map's original out-of-scope list unless this ticket explicitly enlarges it.

## Answer

First PartSAM trial recipe (execute in a later effort; not this map):

| Piece | Choice |
|---|---|
| Scene | Ficus (`ficus_whitebg`) |
| \(P_{in}\) | Throwaway surface from Gaussians → 100k samples with normals + color (`ValDataset` style) |
| Prompts | Three click groups: pot, trunk, leaves |
| To Material Tag Tensor | Priority merge of the three masks; nearest-neighbor onto Gaussian means; `material_tags.pt` shape `(N,)` |
| Pass | File length = Gaussian count; pot/trunk/leaves each non-trivial (trunk > 1 000 Gaussians); runner loads tags; a short PhysGaussian MPM Solver run (few frames) does not immediately explode |
