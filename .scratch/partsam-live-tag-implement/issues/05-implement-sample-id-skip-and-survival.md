# 05 - Implement sample-id skip and survival rematerialize

Type: task
Status: resolved
Blocked by: 03, 04

## Question

Implement sample-id Stage 2 skip and Stage 3 IoU + survival rematerialize in `src/segmentation/partsam/` per the spec and this map’s standing notes, with the always-on tests from [Test contract for skip, survival, and occupancy](03-test-contract-skip-survival-occupancy.md), on the seam from [Rematerialize env and occupancy helper seam](04-rematerialize-env-and-occupancy-seam.md).

Do not run `predict_masks` when masks and IoU exist. Do not edit `CONTEXT.md`. Do not run the 5-frame solver here.

## Answer

`src/segmentation/partsam/` now implements sample-bound Stage 2 skip, Stage 3 survival rematerialize, occupancy helper, and `--check-occupancy`.

- Sample id field: `sample_id` — SHA-256 hex of C-contiguous float32 `coords`, stored on `sample_100k.npz` (via `write_sample_100k`) and on `clicks.json` (`stamp_clicks_sample_id`). Skip only when clicks are complete **and** both stored ids exist and match. Missing or mismatch proposes candidates and does not accept the unbound clicks.
- `apply_survival` in `merge.py`: after IoU merge + lift, restore full raw masks for prompted IDs empty on the Material Tag Tensor, increasing chosen IoU, skip empty raw, one pass per group. `run_stage_lift` rematerializes from `part_masks.npz` + `chosen_iou.json` without loading PartSAM; `predict_masks` only if those files are missing; both paths run survival.
- `occupancy_ok` / `check_occupancy`; CLI `--check-occupancy` exits 0/1.
- Tests: `tests/test_partsam_clicks.py`, `tests/test_partsam_merge.py` (plus surface persist key `sample_id`). Always-on unittests pass under physgauss.

Live ficus backfill, `run_pipeline.sh` occupancy gate, and the 5-frame solver are later tickets. `CONTEXT.md` unchanged.

## Comments
