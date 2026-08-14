# 03 - Spec vs trial vs src merge

Type: research
Status: resolved
Blocked by: none

## Question

What merge rule is currently **specified**, what did the **trial** actually run, and what does **`src/`** implement?

Primary sources: [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md); [Overlap and merge policy without another trial](../../partsam-as-tagger/issues/06-overlap-merge-policy.md); trial merge in `.scratch/partsam-ficus-trial/` (scripts + [Merge masks and lift to Material Tag Tensor](../../partsam-ficus-trial/issues/06-merge-and-lift-tags.md)); `src/segmentation/partsam/merge.py`.

Quote the comparator (named order vs chosen IoU vs mask size). Note what is persisted (`chosen_iou.json`). Do **not** choose the new rule.

Write findings to `.scratch/partsam-live-tag-fix/research/03-spec-vs-trial-vs-src-merge.md`.

## Answer

Specified merge (as-tagger spec / 06): **highest chosen-mask predicted IoU** wins; names are labels, not the comparator; **smaller mask** on ties. Persist one IoU scalar per group (ficus trial did not). Not named order trunk > leaves > pot.

Trial: **named order trunk > leaves > pot** in `merge_and_lift.py` (last-write-wins). IoU only `argmax` among three candidates per group in `run_predict_clicks.py`; scalar not persisted (no `chosen_iou.json`).

`src/`: `merge_masks` uses **highest IoU**, then **smaller mask**, then lexicographic name. `run_stage_lift` writes **`chosen_iou.json`** and merges with those scalars.

Full citations: [research/03-spec-vs-trial-vs-src-merge.md](../research/03-spec-vs-trial-vs-src-merge.md).
