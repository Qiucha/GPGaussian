# 07 - Occupancy gate in run_pipeline.sh

Type: task
Status: resolved
Blocked by: 04, 05

## Question

Change `scripts/run_pipeline.sh` so it reuses `material_tags.pt` only when length is *N* and every prompted Stage 2 id has count > 0; otherwise enter Stage 3 (rematerialize path). Use the helper seam from [Rematerialize env and occupancy helper seam](04-rematerialize-env-and-occupancy-seam.md).

Keep `configs/ficus.json` as the visitor solver config. Do not point the shell at a smoke config. Do not run the 5-frame bar here.

## Answer

`scripts/run_pipeline.sh` reuses `material_tags.pt` only when physgauss `--check-occupancy` exits 0 (length *N* and every prompted Stage 2 id occupied). Otherwise it enters Stage 3: rematerialize in physgauss when `part_masks.npz` and `chosen_iou.json` exist (no Stage 2, so no click round); `predict_masks` in the PartSAM env only when those files are missing (Stage 2 first). `configs/ficus.json` stays `frame_num` 125; the solver invocation is unchanged. The 5-frame bar is not run here.

## Comments
