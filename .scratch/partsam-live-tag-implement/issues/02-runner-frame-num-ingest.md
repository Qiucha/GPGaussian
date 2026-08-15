# 02 - How the runner ingests frame_num

Type: research
Status: resolved
Blocked by: none

## Question

Where does `src/simulation/runner.py` get `frame_num`, and what is the smallest override seam for a one-off `frame_num` 5 without editing `configs/ficus.json`?

Cover, from primary sources only (`src/simulation/runner.py`, `src/simulation/config.py` / `decode_param_json`, `configs/ficus.json`, `scripts/run_pipeline.sh`):

1. How `frame_num` is loaded and used (loop bound).
2. Whether any CLI already overrides time params.
3. What `configs/ficus.json` currently sets for `frame_num`.

Write findings to `.scratch/partsam-live-tag-implement/research/02-runner-frame-num-ingest.md`. Every claim needs a source. Do **not** implement the CLI.

## Answer

`frame_num` comes only from `--config` JSON via `decode_param_json` → `time_params["frame_num"]`, then `for frame in range(frame_num)` (`step_per_frame` from `frame_dt/substep_dt`). Runner argparse and `run_pipeline.sh` do not override time keys; `configs/ficus.json` is `"frame_num": 125`. Smallest one-off seam without editing that file: set `time_params["frame_num"]` after decode (new runner CLI); do not retarget `run_pipeline.sh` at a smoke JSON. Findings: [research/02-runner-frame-num-ingest.md](../research/02-runner-frame-num-ingest.md).

## Comments
