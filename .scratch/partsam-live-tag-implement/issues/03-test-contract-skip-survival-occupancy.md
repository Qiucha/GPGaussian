# 03 - Test contract for skip, survival, and occupancy

Type: grilling
Status: resolved
Blocked by: none

## Question

What always-on unittests must this map add for sample-id skip, survival restore, and tag occupancy — given `predict_masks`, weights, and Warp stay out of CI?

Cover: which files (`tests/test_partsam_clicks.py`, `tests/test_partsam_merge.py`, new); synthetic survival case (empty after first lift, non-empty after restore); sample-id match vs mismatch vs missing; occupancy helper; what is explicitly not a test in this map.

## Answer

Always-on unittests (no `predict_masks`, no weights, no PhysGaussian MPM Solver). Tag IDs **1 = pot / 2 = trunk / 3 = leaves**. Tiny synthetic arrays and temp dirs only — not live `data/outputs/` goldens.

**Files.** Skip / sample-id: extend `tests/test_partsam_clicks.py`. Survival: extend `tests/test_partsam_merge.py`. Occupancy: same file as the helper once [Rematerialize env and occupancy helper seam](04-rematerialize-env-and-occupancy-seam.md) places it; add `tests/test_partsam_occupancy.py` only if that helper is a new module.

**Skip.** Rewrite `test_stage_clicks_skips_when_every_group_has_a_positive` into the match case (complete clicks + same sample id on `sample_100k.npz` and `clicks.json` → `clicks.json` bytes unchanged). Keep incomplete-groups as no-skip. Add: complete + mismatched ids → no skip; complete + missing id on clicks **or** on the sample persist → no skip. Tests go through Python helpers, not a JSON key-name golden (the implement ticket names the field).

**Survival.** Three cases on a Python rematerialize/survival function (not `--stage lift`, not the PartSAM env): (1) first lift leaves a prompted ID empty; restoring that group’s full raw mask on the 100k then lifting makes its tag count > 0 (overlap lost on IoU; exclusive points NN to another part); (2) two empty prompted IDs restore in increasing chosen IoU; (3) empty raw mask → skip that group (no restore). No fourth “loop bound” test.

**Occupancy.** Three cases on a fake `(N,)` int32 Material Tag Tensor: length ≠ *N* fails; length *N* but tag 2 count 0 fails; length *N* and tags 1/2/3 all count > 0 passes. Prompted IDs from Stage 2 groups with positives (all three here). Not a bash histogram.

**Not in this map’s tests.** `predict_masks`; weights; solver / `frame_num` 5 ([Prove the 5-frame solver bar](09-prove-the-5-frame-solver-bar.md)); live ficus occupancy as CI golden; conda env; `run_pipeline.sh` end-to-end; Heuristic Primitive rewrite; `CONTEXT.md`.

## Comments
