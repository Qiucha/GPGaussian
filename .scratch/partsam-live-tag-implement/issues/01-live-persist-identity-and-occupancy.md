# 01 - Live persist identity and occupancy now

Type: research
Status: resolved
Blocked by: none

## Question

What is on disk **now** for the live ficus PartSAM persist, and what would a sample-id backfill plus rematerialize consume?

Cover, from artifacts and code only (`data/outputs/partsam/`, `data/outputs/tags/material_tags.pt`, `src/segmentation/partsam/`, [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md)):

1. Which of `sample_100k.npz`, `clicks.json`, `part_masks.npz`, `chosen_iou.json`, `material_tags.pt` exist (paths, shapes/keys).
2. `clicks.json` keys today — is there already a sample id? `source` value. Completeness per `validate_clicks`.
3. Occupancy of `material_tags.pt` (length vs checkpoint *N*; counts for tags 1/2/3).
4. Raw mask sums in `part_masks.npz` (enough to know rematerialize has a non-empty raw trunk mask).

Write findings to `.scratch/partsam-live-tag-implement/research/01-live-persist-identity-and-occupancy.md`. Every claim needs a source. Do **not** choose the sample-id field name or implement skip.

## Answer

All five named live files exist. `clicks.json` is `validate_clicks`-complete (`source` is the spec string) but has no sample identity; `sample_100k.npz` has only `coords`/`normals`/`colors`/`point_to_face`. `material_tags.pt` length 203930 equals checkpoint *N* (iteration_60000, no opacity filter); tag 2 is 0. Raw trunk mask sum is 569, so rematerialize has a non-empty raw trunk mask. Backfill would consume this 100k+clicks pair in place; rematerialize would consume masks + IoU + coords + PLY means and overwrite `material_tags.pt`. Findings: [research/01-live-persist-identity-and-occupancy.md](../research/01-live-persist-identity-and-occupancy.md).

## Comments
