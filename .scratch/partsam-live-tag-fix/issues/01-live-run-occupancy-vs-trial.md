# 01 - Live-run occupancy vs trial

Type: research
Status: resolved
Blocked by: none

## Question

What are the primary-source occupancy numbers for the live `run_pipeline.sh` PartSAM path versus the ficus trial, and do they support “clicks missed the trunk” or “merge wiped the trunk”?

Cover, from artifacts and code only:

1. Live `data/outputs/partsam/part_masks.npz` sums, pairwise overlaps, `chosen_iou.json`, merged 100k histogram (recompute with `src/segmentation/partsam/merge.py`), `data/outputs/tags/material_tags.pt` unique counts.
2. Trial [RESULT.md](../../partsam-ficus-trial/RESULT.md), [tag_lift_stats.json](../../partsam-ficus-trial/tag_lift_stats.json), trial mask npy / merge notes.
3. Live `clicks.json` vs 100k `sample_100k.npz`: nearest-neighbor distance per group primary.
4. Trial merge rule (named priority) vs live `merge_masks` (highest IoU, smaller mask on ties).

Write findings to `.scratch/partsam-live-tag-fix/research/01-live-run-occupancy-vs-trial.md`. Every claim needs a source. Do **not** choose the new merge rule.

## Answer

Live 100k masks: pot 11 633, trunk **569**, leaves 43 267; trunk∩leaves **553**, trunk-only **16**. `chosen_iou` pot 0.685 > leaves 0.294 > trunk 0.265. `merge_masks` leaves **16** trunk samples; `material_tags.pt` is `(203930,)` with **zero** tag-2. Trial: raw trunk 26 722, merged trunk 26 722, lifted trunk 79 053 (named priority trunk > leaves > pot). Live clicks are byte-identical to the trial and sit millimetres from the new 100k; the trunk primary’s NN is trunk-positive (and leaf-positive). Occupancy supports **merge wiping the remaining live trunk**, not a geometric click miss; the live **raw** trunk mask is already ~47× smaller than the trial’s. Findings: [research/01-live-run-occupancy-vs-trial.md](../research/01-live-run-occupancy-vs-trial.md).
