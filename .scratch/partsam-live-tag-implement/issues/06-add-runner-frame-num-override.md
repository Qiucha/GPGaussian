# 06 - Add runner frame_num override

Type: task
Status: resolved
Blocked by: 02

## Question

Add a small CLI on `src/simulation/runner.py` so a one-off invocation can override `frame_num` to 5 without editing `configs/ficus.json`. Use the ingest facts from [How the runner ingests frame_num](02-runner-frame-num-ingest.md).

Do not change `./scripts/run_pipeline.sh`’s config path or the campaign `frame_num` 125. Do not run the solver here.

## Answer

`src/simulation/runner.py` takes optional `--frame_num INT`. After `decode_param_json`, `apply_frame_num_override` (`src/simulation/time_params.py`) writes `time_params["frame_num"]`; omitted flag leaves the JSON value. `configs/ficus.json` stays 125. `./scripts/run_pipeline.sh` still has no `--frame_num` and still points at that config. Solver not run here. Tests: `tests/test_simulation_time_params.py`.

One-off 5-frame invocation (later ticket): `python -m src.simulation.runner … --config configs/ficus.json --frame_num 5`.

## Comments
