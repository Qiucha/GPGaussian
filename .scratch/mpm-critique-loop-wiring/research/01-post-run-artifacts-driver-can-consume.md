# Post-run artifacts a critique driver can consume

Primary sources (2026-08-14): [`src/simulation/runner.py`](../../../src/simulation/runner.py); [`src/llm/translator.py`](../../../src/llm/translator.py); [`src/llm/schema.py`](../../../src/llm/schema.py); [`configs/ficus.json`](../../../configs/ficus.json); [`configs/vasedeck_multi_material.json`](../../../configs/vasedeck_multi_material.json); [Motion Critique Loop spec](../../mpm-critique-loop/spec.md); [research/01-config-json-vs-runner-ingest.md](../../mpm-critique-loop/research/01-config-json-vs-runner-ingest.md); [research/02-post-run-frames-visual-channel.md](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md). Does not choose `src/` filenames or the module tree. No implementation.

`MotionTranslator.critique` is specified, not present in `translator.py`. The spec **In** payload is previous `--config` JSON, previous CoT, required human text, optional `frame_paths`. **Out** is `(config, reasoning)` — the same pair as `translate`. ([spec.md](../../mpm-critique-loop/spec.md), Seam.) This note maps that payload onto what exists after `python -m src.simulation.runner`.

## 1. Previous `--config` JSON

**Path the runner reads.** `--config` is a required CLI string. The process loads it with `decode_param_json(args.config)` after checking `os.path.exists(args.config)` (failed existence currently constructs `AssertionError` and does not raise it). ([`runner.py`](../../../src/simulation/runner.py), argparse and “load scene config”.) There is no JSON field that names a tag tensor; `--tags_path` is a separate CLI argument. ([`runner.py`](../../../src/simulation/runner.py); [research/01](../../mpm-critique-loop/research/01-config-json-vs-runner-ingest.md) §2.)

Runnable scene files in-tree include [`configs/ficus.json`](../../../configs/ficus.json) (`"frame_num": 125`) and [`configs/vasedeck_multi_material.json`](../../../configs/vasedeck_multi_material.json) (`"frame_num": 75`). Those are ordinary paths a caller can pass as `--config`; the runner does not hard-code `configs/`.

**Whether the runner writes a copy under `--output_path`.** It does not. After decode, `args.config` is unused. There is no `json.dump`, `shutil.copy`, or other write of the scene JSON into `args.output_path`. ([`runner.py`](../../../src/simulation/runner.py), full `__main__`.) Writes under `--output_path` are: optional `{output_path}/simulation_ply` (`--output_ply` / `--output_h5`); optional `{output_path}/{NNNN}.png` (`--render_img`); optional `{output_path}/output.mp4` (`--render_img` and `--compile_video`). ([`runner.py`](../../../src/simulation/runner.py) frame loop and ffmpeg block; [research/02](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md) §1–§2, §4.)

A driver that needs “previous `--config` JSON” for `critique` must keep the path (or bytes) it already passed in. The spec requires the **complete** next `--config`: every key on the previous file must appear on the new object. ([spec.md](../../mpm-critique-loop/spec.md), Revision.) Translator-shaped first-shot dicts are not a drop-in replacement for ficus-shaped scene JSON. ([research/01](../../mpm-critique-loop/research/01-config-json-vs-runner-ingest.md) §6.)

## 2. Previous CoT / `reasoning`

**`translate` return value is in memory only.** `MotionTranslator.translate` returns `Tuple[Dict[str, Any], str]` — `(config, reasoning)`. With `mock_llm=True` those come from the retrieved exemplar; live `translate` is `NotImplementedError`. There is no `open(...)` / `json.dump` of either value. ([`translator.py`](../../../src/llm/translator.py), `translate`.) The system prompt asks the model to put CoT in a `<reasoning>` block before JSON; that is prompt text, not a file contract. ([`translator.py`](../../../src/llm/translator.py), `SYSTEM_PROMPT_TEMPLATE`.)

**Schema has no CoT field.** `PhysGaussianLLMConfig` fields are timesteps, grid, `g`, damping, `opacity_threshold`, `materials`, `material_segmentation_rules`, `boundary_conditions`. No `reasoning` / CoT attribute and no serializer. ([`schema.py`](../../../src/llm/schema.py), class `PhysGaussianLLMConfig`; [research/01](../../mpm-critique-loop/research/01-config-json-vs-runner-ingest.md) §1.)

**The runner never sees CoT.** [`runner.py`](../../../src/simulation/runner.py) does not import the translator or write a reasoning sidecar.

**`critique` is specified to take previous CoT anyway.** Seam **In** includes previous CoT; **Out** is `(config, reasoning)` like `translate`. Mock identity returns `(previous_config, canned_reasoning)`. ([spec.md](../../mpm-critique-loop/spec.md), Seam and Mock.) Nothing in today’s `translate` or solver run persists that string; a driver must hold it from the last `translate`/`critique` call (or start the first critique without a disk artifact).

## 3. `--render_img` PNG glob vs `frame_num`

Only if `--render_img`. The loop is `for frame in tqdm(range(frame_num))` with `frame_num = time_params["frame_num"]` from the decoded `--config`. After that iteration’s `p2g2p` substeps, rasterize then:

```text
os.path.join(args.output_path, f"{frame}.png".rjust(8, "0"))
```

That is a **flat** directory (`args.output_path`), four-digit zero-pad + `.png` for `frame` 0–999 (`0000.png`, `0001.png`, …). `assert args.output_path is not None`. Count is **exactly `frame_num`**, indices `0 .. frame_num-1`. No rest-pose extra frame before the first `frame_dt` of physics. Without `--render_img`, Warp still steps and writes **no** images. `--output_path` argparse default is `None`. ([`runner.py`](../../../src/simulation/runner.py); [research/02](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md) §2.)

Ficus JSON `"frame_num": 125` → 125 PNGs (`0000.png` … `0124.png`). Vasedeck JSON `"frame_num": 75` → 75 PNGs. ([`configs/ficus.json`](../../../configs/ficus.json); [`configs/vasedeck_multi_material.json`](../../../configs/vasedeck_multi_material.json); [research/02](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md) §2.)

Spec visual channel: optional `frame_paths` inside `critique`; frames are runner `--render_img` `{output_path}/{NNNN}.png` for `0 .. frame_num-1`. Digest JPEGs, optional `output.mp4`, and eval scalars are **other** artifacts. Absent paths: skip describe. ([spec.md](../../mpm-critique-loop/spec.md), Visual channel.) `output.mp4` exists only if **both** `--render_img` and `--compile_video`; it is not a guaranteed post-run file and is not the spec’s `frame_paths` input. ([`runner.py`](../../../src/simulation/runner.py), ffmpeg `os.system`; [research/02](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md) §4.)

PLY/H5 under `{output_path}/simulation_ply` are particle archives, not the visual channel. ([`runner.py`](../../../src/simulation/runner.py); [research/02](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md) §1.)

## 4. How the runner is invoked (CLI the driver must pass through)

[`runner.py`](../../../src/simulation/runner.py) argparse when `__name__ == "__main__"`:

| Flag | Required? | Default | Role for a critique driver |
| --- | --- | --- | --- |
| `--model_path` | yes | — | 3DGS checkpoint directory (`point_cloud/iteration_*/point_cloud.ply`). Same path on replay. |
| `--config` | yes | — | Scene JSON path (previous file, then next complete JSON). Not copied to output. |
| `--output_path` | no | `None` | PNG/mp4/ply parent. Required if `--render_img`. |
| `--tags_path` | no | `None` | `material_tags.pt`. Frozen for the loop; same path on replay. Missing/nonexistent → all-zero tags. |
| `--render_img` | no | off | Must be on if `critique` should receive `frame_paths`. |
| `--compile_video` | no | off | Optional ffmpeg `output.mp4`; not a `critique` input. |
| `--output_ply` / `--output_h5` | no | off | Optional particle dumps. |
| `--white_bg` / `--debug` | no | off | Background color; debug PLYs under `./log`. |

Spec: `--tags_path` is CLI-only; the loop retunes JSON `materials` / BCs / timesteps, not tensor membership. ([spec.md](../../mpm-critique-loop/spec.md), Frozen Material Tag Tensor.) Ingest replay: same `--model_path`, same `--tags_path`, a `--config` whose `materials` integer keys match tensor IDs. ([research/01](../../mpm-critique-loop/research/01-config-json-vs-runner-ingest.md) §6.)

A driver that wants solver PNGs for optional `frame_paths` must pass `--render_img` and a non-`None` `--output_path` in addition to the four named args. A bare `python -m src.simulation.runner` without `--render_img` leaves no rasterized sequence. ([research/02](../../mpm-critique-loop/research/02-post-run-frames-visual-channel.md) §4.)

## 5. What can actually be passed into `critique` after a run

| Spec **In** | After `python -m src.simulation.runner` today |
| --- | --- |
| Previous `--config` JSON | On disk at the **input** `--config` path only. No copy under `--output_path`. |
| Previous CoT | **Not on disk.** Only the in-memory `str` from the last `translate` (or later `critique`). Runner does not produce it. |
| Human text | Not a runner artifact (CLI `--text` / `--text-file` is a later driver concern). ([spec.md](../../mpm-critique-loop/spec.md), Human text.) |
| Optional `frame_paths` | On disk iff `--render_img` and `--output_path`: `{output_path}/{NNNN}.png`, count = JSON `frame_num`, indices `0 .. frame_num-1`. |

`critique` itself is not implemented; `translate` is mock-or-`NotImplementedError`. ([`translator.py`](../../../src/llm/translator.py); [spec.md](../../mpm-critique-loop/spec.md), Handoff / Mock.)
