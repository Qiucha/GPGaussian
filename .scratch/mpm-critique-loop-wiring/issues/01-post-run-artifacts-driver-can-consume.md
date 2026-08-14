# 01 - Post-run artifacts a critique driver can consume

Type: research
Status: resolved
Blocked by: none

## Question

After a PhysGaussian MPM Solver `python -m src.simulation.runner` invocation, what artifacts exist on disk (or only in memory) that a Motion Critique Loop driver can pass into `MotionTranslator.critique`?

Cover, from primary sources only (`src/simulation/runner.py`, `src/llm/translator.py`, `src/llm/schema.py`, configs, [spec.md](../../mpm-critique-loop/spec.md), [research/01-config-json-vs-runner-ingest.md](../../mpm-critique-loop/research/01-config-json-vs-runner-ingest.md), [research/02-post-run-frames-visual-channel.md](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md)):

1. Previous `--config` JSON: path the runner reads; whether it writes a copy under `--output_path`.
2. Previous CoT / `reasoning`: whether anything persists today after `translate` or a run.
3. `--render_img` PNG glob (`{output_path}/{NNNN}.png`, count vs `frame_num`).
4. How the runner is invoked (CLI args the driver must pass through: `--model_path`, `--tags_path`, `--config`, `--output_path`).

Write findings to `.scratch/mpm-critique-loop-wiring/research/01-post-run-artifacts-driver-can-consume.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** choose `src/` filenames or the module tree.

## Answer

After `python -m src.simulation.runner`, the previous `--config` stays at the input path (no copy under `--output_path`); CoT/`reasoning` is in-memory from `translate` only; `--render_img` writes exactly `frame_num` `{output_path}/{NNNN}.png` files (`0 .. frame_num-1`). The driver must pass through `--model_path`, `--tags_path`, `--config`, `--output_path` (plus `--render_img` for `frame_paths`). Findings: [research/01-post-run-artifacts-driver-can-consume.md](../research/01-post-run-artifacts-driver-can-consume.md).

## Comments
