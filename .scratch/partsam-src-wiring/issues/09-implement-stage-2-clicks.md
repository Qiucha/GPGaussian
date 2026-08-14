# 09 - Implement Stage 2 geometry and click JSON in src/

Type: task
Status: resolved
Blocked by: 02, 03, 04

## Question

Implement Stage 2 in `src/`: geometry proposes on-cloud candidates; persist/consume spec-shaped world-xyz clicks JSON; skip if clicks already exist; throwaway annotated preview PNG. MLLM or human **writes** the JSON (accept/swap/resample; no free-form xyz; not a Python VLM import). Human after two failed annotated rounds.

Port facts from [Trial click loop vs spec JSON to port](02-trial-click-loop-to-port.md). Ficus producer bar may use on-disk clicks without a live MLLM round.

## Answer

`src/segmentation/partsam/clicks.py`: geometry bins + K=5 centroid-KNN (same as the ficus trial proposer); persist `click_candidates.json` and throwaway `click_candidates.png`. Consume spec `clicks.json` (`frame: world`, groups pot/trunk/leaves with ≥1 positive each; extra keys such as trial `mllm` allowed). Skip-if-exists only when that file is complete; empty/partial groups re-propose. Python does not import a VLM — if clicks are missing after propose, raise telling MLLM/human to write JSON (accept/swap/resample; human after two failed annotated rounds). Ficus can drop an on-disk `clicks.json` and skip. CLI: `--stage clicks`. Tests: `tests/test_partsam_clicks.py`.

## Comments
