# 04 - Rematerialize env and occupancy helper seam

Type: grilling
Status: resolved
Blocked by: none

## Question

When `part_masks.npz` and `chosen_iou.json` exist, which conda env runs rematerialize (merge + survival + lift), and where does the occupancy gate live so `run_pipeline.sh` can reuse or re-enter Stage 3 without a bash histogram?

Cover: `physgauss` vs `PartSAM` for rematerialize vs `predict_masks`; Python helper vs shell; whether `--stage lift` grows a no-model path or a new stage name. Do not implement.

## Answer

Rematerialize (merge + survival + lift from persisted `part_masks.npz` + `chosen_iou.json`) runs in **physgauss**. The **PartSAM** env is only for `predict_masks` when those files are missing.

`--stage lift` stays the Stage 3 name (no `--stage rematerialize`). `run_stage_lift` short-circuits: masks + IoU present → rematerialize, do not load the model; otherwise `predict_masks` then merge + survival + lift. The shell chooses env from that (physgauss when masks exist, PartSAM when they do not).

Occupancy gate: Python helper in `src/segmentation/partsam/merge.py` (tests in `tests/test_partsam_merge.py`). Inputs: `material_tags.pt`, checkpoint `--model_path` (*N* from existing Gaussian-means load, before opacity filter), `clicks.json` (prompted IDs = Stage 2 groups with ≥1 positive). Pass iff length is *N* and every prompted ID has count > 0. Shell invokes it under physgauss via `--check-occupancy` on `python -m src.segmentation.partsam` (exit 0 = reuse tags, non-zero = enter Stage 3). Not a bash histogram and not a fourth `--stage`.

## Comments
