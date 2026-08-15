# 08 - Backfill live clicks sample id

Type: task
Status: resolved
Blocked by: 01, 05

## Question

Write the sample id onto the live ficus `sample_100k.npz` and `clicks.json` pair so Stage 2 skip matches, using facts from [Live persist identity and occupancy now](01-live-persist-identity-and-occupancy.md) and the skip implementation from [Implement sample-id skip and survival rematerialize](05-implement-sample-id-skip-and-survival.md).

Do not force a human click round. Do not rebuild the 100k. Do not run `predict_masks`.

## Answer

Wrote `sample_id` `f92f062f0e7eff989a8083dc344ea3b17e4f27fffefae26a367f167e6eb68f56` (SHA-256 of the existing live `coords`) onto `data/outputs/partsam/sample_100k.npz` and `data/outputs/partsam/clicks.json`. Coords and click groups were not rebuilt. `clicks_are_complete` stays true; Stage 2 skip now binds (`_clicks_bound_to_sample`). Did not run `predict_masks`.

## Comments
