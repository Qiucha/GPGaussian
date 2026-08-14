# 07 - Implement human-gated and auto-rerun driver

Type: task
Status: resolved
Blocked by: 03, 04, 06

## Question

Implement the new Motion Critique Loop driver (not `run_pipeline.sh`): **human-gated default** (after a passing `critique`, wait before the next PhysGaussian MPM Solver run); **auto-rerun** (same human text, new `--render_img` paths) with injectable solver step.

Stops: N completed solver runs (default 3); CFL/schema reject then one inner `critique` retry with the validator error string (no new frames; inner retries do not count toward N); user interrupt. Missing `frame_paths` skips describe and continues. `--text` / `--text-file`; empty is not a turn.

Unittests use a fake runner. Live driver may call `python -m src.simulation.runner`; a full ficus campaign is not this ticket’s bar.

## Answer

Driver is [`src/llm/critique_loop.py`](../../../src/llm/critique_loop.py); CLI `python -m src.llm.critique_loop`. `run_critique_loop` injects `translator` + `solver(config, output_path) -> frame_paths`. Persist `--output_dir` default `data/outputs/critique/`; each solve writes `run_{ii}/config.json` then the next run’s `config.json` + `reasoning.txt`. Human-gated: one solver run then `waiting`. Auto: same human text until N solver runs (`--max-runs` default 3). Inner `critique` `ValueError` retries once with the original text plus the validator error (same `frame_paths`; retry does not increment N). Injectable `stop_flag` stops without another solve (live CLI maps SIGINT onto it). Empty `--text` / `--text-file` / stdin is not a turn. Live solver may subprocess `python -m src.simulation.runner` with `--render_img`; tests fake Warp. Tests in `tests/test_motion_critique.py`. `run_pipeline.sh` unchanged.

## Comments
