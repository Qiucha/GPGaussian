# Specification: Motion Critique Loop

Status: ready-for-agent

## Handoff

After a PhysGaussian MPM Solver run, revise the next runner `--config` from **required** freeform human text and an **optional** visual describe over `--render_img` PNGs. Default next run is **human-gated**. CFL/schema still refuse Warp on invalid JSON.

This spec is the handoff. A later map wires `src/`. This effort does not implement live `translate`, live `critique`, or the mock body.

**Done** when a later map can implement `MotionTranslator.critique`, the two run modes, and the mock contract without inventing payload, revision, visual, stop, or human-text policy.

Name is **Motion Critique Loop** (spec-local). Segmenter Agent plan-metric iteration stays that agent’s loop. Parent RFC: [Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian](../llm-motion-physgaussian/spec.md). Glossary in `CONTEXT.md` is unchanged.

## Frozen Material Tag Tensor

`--tags_path` (`material_tags.pt`) is CLI-only. The loop retunes JSON `materials` / BCs / timesteps. Membership (which Gaussian holds which ID) is a new tensor, outside this loop. PartSAM remains the intended producer.

Ingest facts: [Config JSON vs runner ingest for a Motion Critique Loop](issues/01-config-json-vs-runner-ingest.md), [research/01-config-json-vs-runner-ingest.md](research/01-config-json-vs-runner-ingest.md).

## Seam

`MotionTranslator.critique` — a new method. `translate(query, scene_bounds)` stays first-shot only.

| | |
| --- | --- |
| **In** | previous `--config` JSON, previous CoT, required human text, optional `frame_paths` |
| **Out** | `(config, reasoning)` — same pair as `translate` |
| **Not in** | first-shot `query`, `scene_bounds`, motion-library retrieve from the first-shot string |

Source: [Critique-entry seam on MotionTranslator](issues/03-critique-entry-seam.md).

## Revision

`config` is the **complete next `--config`**. Every key on the previous file appears on the new object. Prompt may seed the previous JSON so the model echoes camera, rotation, opacity, top-level `"material"`. Omit of a previous key is invalid (validator), not copy-through and not PhysGaussian clone defaults.

**`materials`:** string-int keys → `{E, nu, density}` plus keys already on that row. **Key set frozen** to the previous table: every previous row; no new rows (including unlabeled `"0"`). IDs absent from the tensor are invalid. Tensor IDs with no previous row keep runner scalar fill. Ficus table keys `"1"`/`"2"`/`"3"`; an exemplar `"0"`/`"1"`/`"2"` table is invalid against that tensor.

Source: [Revision shape for Motion Critique Loop JSON](issues/04-revision-shape.md).

## Visual channel

Optional, **inside** `critique` when `frame_paths` is set. Describes observed motion as text (may appear in `reasoning`). `critique` is the only JSON author. Absent paths: skip the channel. Human types without waiting on a caption.

**Frames:** runner `--render_img` `{output_path}/{NNNN}.png` for `0 .. frame_num-1` (3DGS rasterize after Warp). Digest `frame_NN.jpg` PIL clip, optional `output.mp4`, and eval scalars are other artifacts.

Human watch: runner PNGs. Digest playback is optional watch surface, not solver evidence.

Source: [Visual channel’s job in the Motion Critique Loop](issues/05-visual-channel-job.md), [Post-run frames a visual channel can see](issues/02-post-run-frames-visual-channel.md).

## Human text

Non-empty **freeform natural language**. Empty or whitespace is not a critique turn. User interrupt is a separate control.

Source: [Human text contract for the Motion Critique Loop](issues/07-human-text-contract.md).

## Modes

**Human-gated (default):** after a passing `critique`, wait for the human before the next PhysGaussian MPM Solver run.

**Auto-rerun:** after a human `critique` that passes CFL/schema, loop Warp → `critique` with the **same** human text and new `--render_img` paths.

Stops: **N** completed solver runs (parameter, **default 3**; first auto Warp is 1; after N, last frames wait for a new human-gated turn); CFL/schema reject (no Warp) then **one** inner `critique` retry with the validator error string, same human text, previous JSON, no new frames — fail again and the auto path ends; **user interrupt**. Inner retries do not count toward N. Missing `frame_paths` skips describe and continues.

CFL/schema: `validate_physgaussian_config` (`ValueError` on `nu` / CFL) plus omit-invalid and frozen `materials` key set.

Source: [Auto-path stop for the Motion Critique Loop](issues/06-auto-path-stop.md).

## Mock (later map tests)

`MotionTranslator(mock_llm=True).critique`: identity. Non-empty human text; return `(previous_config, canned_reasoning)` after `validate_physgaussian_config`. No motion-library retrieve. No PNG/VLM I/O. If `frame_paths` is set, canned reasoning records that the visual channel was skipped under mock.

`mock_llm=False`: `critique` raises `NotImplementedError` (same as live `translate`).

Omit-invalid / frozen `materials` key set are validator tests, not this mock’s job.

Source: [Mock/test contract for the Motion Critique Loop spec](issues/08-mock-test-contract.md).

## Out of this spec

- Wiring `src/` (the later map).
- Live first-shot `MotionTranslator.translate` API.
- Live or mock `critique` code (contract only).
- Changing the Material Tag Tensor; PartSAM wiring.
- Adding Motion Critique Loop to `CONTEXT.md`.
- Digest Dashboard features beyond existing frames as optional watch surface.
- FVD/KVD/PSNR/SSIM/LPIPS (or using them as loop stops).
- VLM vendor, API, and prompt templates (later-map fog).
- `src/` module layout (later-map fog).
- Custom CUDA / Warp kernels for per-particle material decoding.
- GitHub README / remote.
