# 03 - Persist filenames and src/llm module tree

Type: grilling
Status: resolved
Blocked by: 01

## Question

What persist filenames and Python module tree under `src/` does this map implement for `MotionTranslator.critique` and the new driver?

Cover: package vs new module; CLI (`python -m …`); where next `--config` and CoT are written; frame-path list/glob the driver passes; default N; `--text` / `--text-file`. Not merge/validator physics, not live LLM.

Use facts from [Post-run artifacts a critique driver can consume](01-post-run-artifacts-driver-can-consume.md).

## Answer

`MotionTranslator.critique` stays on [`src/llm/translator.py`](../../../src/llm/translator.py). Driver is [`src/llm/critique_loop.py`](../../../src/llm/critique_loop.py); CLI **`python -m src.llm.critique_loop`**. Validator stays `src/llm/validator.py`. Do not nest a `src/llm/critique/` package. Do not rewrite `run_pipeline.sh`.

`--output_dir` default **`data/outputs/critique/`**. Each solver run is `run_{ii}/` (`run_00`, `run_01`, …) containing:

| File | Role |
| --- | --- |
| `config.json` | Complete `--config` for that run |
| `reasoning.txt` | CoT from the `critique` (or first-shot `translate`) that produced this config |
| `{NNNN}.png` | Runner `--render_img` into this directory (`--output_path` = `run_{ii}/`) |

First `--config` is the CLI input path (not mutated). After a passing `critique`, write the next run’s `config.json` + `reasoning.txt` before the next solve. `frame_paths` is the `{NNNN}.png` list in the run that just finished; skip the visual channel if none.

CLI (standing): `--text` / `--text-file`; `--max-runs` default **3**; human-gated default vs auto. Pass through `--model_path`, `--tags_path`.

## Comments
