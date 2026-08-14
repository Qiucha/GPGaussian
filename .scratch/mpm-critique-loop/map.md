# Map: Motion Critique Loop spec

## Destination

A written spec at [spec.md](spec.md) for the **Motion Critique Loop**: after a PhysGaussian MPM Solver run, revise JSON config (materials table / tag-ID→Lamé mapping, boundary conditions, timesteps) from **required** human text and an **optional** visual-token channel over rasterized frames. Default next run is human-gated; CFL still auto-rejects invalid JSON. One-line pointer in orientation. Not wiring `src/`. `CONTEXT.md` unchanged.

## Notes

- Effort slug: `mpm-critique-loop`
- Domain: Phys4DGS glossary in `CONTEXT.md`. Parent RFC: [Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian](../llm-motion-physgaussian/map.md) ([spec.md](../llm-motion-physgaussian/spec.md)). Orientation: [docs/agents/orientation.md](../../docs/agents/orientation.md). In-repo “refinement” is Segmenter Agent plan metrics — not this loop.
- Skills: `/research`, `/grilling`, `/domain-modeling`; `/writing-for-agents` when writing the spec and the orientation pointer.
- This effort **writes** `spec.md` and the orientation one-liner (overrides plan-only). No `src/` wiring. No live first-shot `MotionTranslator` API. No `CONTEXT.md` term (loop is not in the pipeline yet).
- Research notes: `.scratch/mpm-critique-loop/research/` (local-markdown tracker; not a git `research/` branch).
- Standing:
  - Name is **Motion Critique Loop** (spec-local). Do not call it refinement.
  - Material Tag Tensor is frozen (PartSAM is the intended producer). The loop may retune which tag IDs map to which materials, plus forces and timesteps.
  - Human text is required; optional visual channel describes runner PNGs inside `critique` and does not propose JSON.
  - Observables: previous JSON + CoT + human text + rasterized frames (or paths). Not stubbed FVD/KVD.
  - Spec both human-gated and auto-rerun; **default human-gated**.
  - `MotionTranslator` is an assumed seam (`mock_llm` exists; live `translate` is `NotImplementedError`). This spec does not implement that live call.

## Decisions so far

<!-- the index — one line per closed ticket -->
- [Config JSON vs runner ingest for a Motion Critique Loop](issues/01-config-json-vs-runner-ingest.md) — JSON `materials`/BCs/timesteps are patchable; tags are CLI-only (`material_tags.pt`), so membership changes need a new tensor. Findings: [research/01-config-json-vs-runner-ingest.md](research/01-config-json-vs-runner-ingest.md).
- [Post-run frames a visual channel can see](issues/02-post-run-frames-visual-channel.md) — Solver `--render_img` writes `frame_num` 3DGS PNGs under `--output_path`; Digest plays a separate 30-frame PIL JPEG clip; `output.mp4` and FVD/KVD are not guaranteed. Findings: [research/02-post-run-frames-visual-channel.md](research/02-post-run-frames-visual-channel.md).
- [Critique-entry seam on MotionTranslator](issues/03-critique-entry-seam.md) — New `MotionTranslator.critique` (not `translate`); in: previous JSON, CoT, human text, optional frame paths; out: `(config, reasoning)`.
- [Revision shape for Motion Critique Loop JSON](issues/04-revision-shape.md) — Full next `--config` (not a patch); omit of a previous key is invalid; `materials` key set frozen to the previous table; tensor unchanged.
- [Visual channel’s job in the Motion Critique Loop](issues/05-visual-channel-job.md) — Describe runner PNGs inside `critique` (optional with frame paths); no JSON from the visual channel; Digest mock frames are not this channel.
- [Auto-path stop for the Motion Critique Loop](issues/06-auto-path-stop.md) — Auto loop reuses last human text; stop at N solver runs (default 3), CFL/schema after one inner retry, or user interrupt. No eval/visual auto-stop.
- [Human text contract for the Motion Critique Loop](issues/07-human-text-contract.md) — Freeform NL only (non-empty); no intent enum or JSON fields; watch runner PNGs; Digest optional and not solver evidence.
- [Mock/test contract for the Motion Critique Loop spec](issues/08-mock-test-contract.md) — `mock_llm=True` identity `critique` (previous JSON + canned reasoning, CFL still runs, no VLM/library retrieve); live still `NotImplementedError`.
- [Write the Motion Critique Loop spec](issues/09-write-spec.md) — [spec.md](spec.md): `critique` seam, full `--config`, frozen `materials` keys, describe-only visual, freeform human text, human-gated default + auto stops, identity mock.
- [Point orientation at the Motion Critique Loop spec](issues/10-orientation-pointer.md) — Orientation **Potential → Live LLM** points at [spec.md](spec.md).

## Not yet specified

_(none — destination reached; VLM vendor/prompts, eval-in-loop, and `src/` layout belong to a later wiring map)_

## Out of scope

- Wiring the loop into `src/` (a later map).
- Implementing the live first-shot `MotionTranslator` API (orientation Potential; not this leftover).
- Longer GitHub README (later map, not this destination).
- Custom CUDA / Warp kernels for per-particle material decoding (still leftover on the LLM-motion map).
- PartSAM wiring; changing the Material Tag Tensor in the loop.
- Expanding `CONTEXT.md` with Motion Critique Loop.
- Digest Dashboard feature work beyond using existing frames as watch surface.
- Gold-standard eval implementation (FVD/KVD/etc.).
