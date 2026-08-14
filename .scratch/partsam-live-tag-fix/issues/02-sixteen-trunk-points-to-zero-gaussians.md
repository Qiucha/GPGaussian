# 02 - Sixteen trunk-only points to zero Gaussians

Type: research
Status: resolved
Blocked by: none

## Question

After live merge, the 100k cloud has a handful of trunk-only samples. The lifted Material Tag Tensor has **zero** tag-2 Gaussians. Why does `lift_tags` fail to preserve any trunk?

Cover, from `src/segmentation/partsam/merge.py` `lift_tags` and the live arrays:

1. Exact merged-100k count for tag 2 (recompute; do not trust chat).
2. Whether unlabeled 100k are excluded from the NN reference (code).
3. Geometry: are the surviving trunk samples surrounded by leaves/pot labeled points so every Gaussian’s nearest labeled sample is not trunk?
4. Whether a bug (dtype, empty mask, wrong tag id) could zero the class without geometry.

Write findings to `.scratch/partsam-live-tag-fix/research/02-sixteen-trunk-points-to-zero-gaussians.md`. Every claim needs a source. Do **not** choose the new merge rule.

## Answer

`lift_tags` does not wipe tag 2 by dtype, empty mask, or wrong id. Recomputed merge on live `part_masks.npz` + `chosen_iou.json` has **16** tag-2 samples (the exclusive-trunk points; 553 trunk∩leaves went to leaves on IoU). Unlabeled 100k are excluded from the NN reference (`sample_tags != 0`). Those 16 form a small clump whose nearest non-trunk labeled neighbors are all leaves; no Gaussian mean is closer to them than to a non-trunk labeled sample, so the lifted tensor is `{1: 32476, 3: 171454}`. Geometry of NN lift, not a lift bug. Findings: [research/02-sixteen-trunk-points-to-zero-gaussians.md](../research/02-sixteen-trunk-points-to-zero-gaussians.md).
