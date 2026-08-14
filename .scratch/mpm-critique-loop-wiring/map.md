# Map: Wire Motion Critique Loop in src/

## Destination

`src/` implements the [Motion Critique Loop spec](../mpm-critique-loop/spec.md): `MotionTranslator.critique` (identity mock; live `NotImplementedError`), omit-invalid / frozen-`materials` validator, human-gated default and auto-rerun (N default 3) on a **new driver**. Driver takes `--text` / `--text-file`; injectable solver step (unittests fake the PhysGaussian MPM Solver). `run_pipeline.sh` stays PartSAM → first solver run. Orientation Next steps points at the wired path. `CONTEXT.md` unchanged.

## Notes

- Effort slug: `mpm-critique-loop-wiring`
- Domain: Phys4DGS glossary in `CONTEXT.md`. Policy: [spec.md](../mpm-critique-loop/spec.md). Parent RFC: [Few-Shot LLM Motion Library](../llm-motion-physgaussian/map.md). Orientation: [docs/agents/orientation.md](../../docs/agents/orientation.md).
- Skills: `/research`, `/grilling`, `/domain-modeling`; `/tdd` on implement tickets; `/writing-for-agents` on the orientation pointer.
- This effort **writes** `src/` (translator, validator, new driver module), always-on tests, and the orientation pointer (overrides plan-only). No `run_pipeline.sh` rewrite. No `CONTEXT.md` term. No live `translate` / live `critique` / VLM. No Material Tag Tensor rewrite.
- Research notes: `.scratch/mpm-critique-loop-wiring/research/` (local-markdown tracker; not a git `research/` branch).
- Standing:
  - Name is **Motion Critique Loop** (spec-local). Do not call it refinement. Segmenter Agent plan-metric iteration stays that agent’s loop.
  - Material Tag Tensor is frozen; PartSAM remains the intended producer. The loop retunes JSON `materials` / BCs / timesteps only.
  - Human text: required freeform NL via `--text` or `--text-file`; empty/whitespace is not a turn; stdin only if those are absent. No extra JSON fields.
  - `mock_llm=True` identity `critique`; if `frame_paths` is set, canned reasoning contains `visual channel skipped (mock)`. `mock_llm=False` → `NotImplementedError`.
  - Auto-rerun reuses the same human text; stops at N solver runs (default 3), CFL/schema after one inner retry, or user interrupt (injectable stop flag; live driver may map SIGINT onto it). Inner retries do not count toward N.
  - Orchestrator injects the solver step; unittests never call Warp. A full N=3 ficus campaign is not a success bar.

## Decisions so far

- [Post-run artifacts a critique driver can consume](issues/01-post-run-artifacts-driver-can-consume.md) — Previous `--config` stays at the input path (no output copy); CoT is in-memory only; `--render_img` writes `frame_num` `{NNNN}.png` files; pass through `--model_path`, `--tags_path`, `--config`, `--output_path`. Findings: [research/01-post-run-artifacts-driver-can-consume.md](research/01-post-run-artifacts-driver-can-consume.md).
- [Validator vs omit-invalid and frozen materials keys](issues/02-validator-vs-omit-and-frozen-materials.md) — Current validator raises only on `nu`/CFL (empty `materials` → synthetic `"0"`); omit and frozen `materials` keys need previous-vs-candidate checks, not new physics. Findings: [research/02-validator-vs-omit-and-frozen-materials.md](research/02-validator-vs-omit-and-frozen-materials.md).
- [Test contract for the Motion Critique Loop without Warp](issues/04-test-contract-without-warp.md) — `tests/test_motion_critique.py` for mock `critique` + fake-runner driver; omit/frozen cases in `test_schema_and_cfl.py`; canned skip string `visual channel skipped (mock)`; injectable interrupt flag; no Warp/LLM/VLM.
- [Persist filenames and src/llm module tree](issues/03-filenames-and-module-tree.md) — `critique` on `translator.py`; CLI `python -m src.llm.critique_loop`; persist `data/outputs/critique/run_{ii}/{config.json,reasoning.txt,NNNN.png}`.
- [Implement omit-invalid and frozen materials validator](issues/05-implement-validator-omit-frozen.md) — `validate_physgaussian_config(..., previous=)` omit + frozen `materials` keys; CFL/`nu` unchanged when `previous` is omitted.
- [Implement MotionTranslator.critique mock](issues/06-implement-critique-mock.md) — identity mock `critique`; empty text rejected; visual-skip canned string; live `NotImplementedError`; `translate` unchanged.
- [Implement human-gated and auto-rerun driver](issues/07-implement-critique-driver.md) — `python -m src.llm.critique_loop`; injectable solver; human-gated wait after one run; auto N; inner retry does not count toward N; injectable stop flag.
- [Point orientation at the wired Motion Critique Loop](issues/08-orientation-wired-pointer.md) — orientation names mock `critique` + driver; live still stubbed; `run_pipeline.sh` still PartSAM → solver; spec pointer; `CONTEXT.md` unchanged.

## Not yet specified

_(none — canned skip wording and interrupt observation are decided on [Test contract for the Motion Critique Loop without Warp](issues/04-test-contract-without-warp.md).)_

## Out of scope

- Live `MotionTranslator.translate` or live `critique` / VLM vendor / prompt templates.
- Folding the loop into `scripts/run_pipeline.sh`.
- Adding Motion Critique Loop to `CONTEXT.md`.
- Changing the Material Tag Tensor; PartSAM retune.
- Digest Dashboard features; using Digest JPEGs as solver evidence.
- FVD/KVD/PSNR/SSIM/LPIPS as loop stops.
- A full-length ficus wind campaign as the done check.
- GitHub remote or README clone paragraphs (no new upstream).
