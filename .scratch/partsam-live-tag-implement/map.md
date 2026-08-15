# Map: Implement the live ficus PartSAM tagging fix

## Destination

`src/` implements sample-bound Stage 2 skip and Stage 3 IoU + prompted-ID **survival** from [PartSAM as Material Tag Tensor source](../partsam-as-tagger/spec.md). Live ficus writes a Material Tag Tensor with every prompted ID non-empty after lift (*N* matches checkpoint count) and a PhysGaussian MPM Solver run at `frame_num` **5** that exits 0, stays finite, and does not CUDA 700. `CONTEXT.md` unchanged.

## Notes

- Effort slug: `partsam-live-tag-implement`
- Domain: Phys4DGS glossary in `CONTEXT.md` (Material Tag Tensor, PhysGaussian MPM Solver). Policy: [PartSAM as Material Tag Tensor source](../partsam-as-tagger/spec.md). Spec map: [Spec the live ficus PartSAM tagging fix](../partsam-live-tag-fix/map.md). Wired producer: [Wire PartSAM as Material Tag Tensor producer in src/](../partsam-src-wiring/map.md).
- Skills: `/research`, `/grilling`, `/domain-modeling`; `/tdd` on implement tickets; `/writing-for-agents` on the orientation pointer.
- This effort **writes** `src/segmentation/partsam/`, `scripts/run_pipeline.sh`, a small runner `frame_num` CLI, live persist backfill, and the orientation pointer (overrides plan-only). It **runs** the 5-frame bar. No `CONTEXT.md` PartSAM term. No 125-frame campaign. No `configs/ficus.json` edit.
- Research notes: `.scratch/partsam-live-tag-implement/research/` (local-markdown tracker; not a git `research/` branch).
- Standing:
  - Merge stays highest chosen-mask IoU (smaller mask on ties). Survival: if a prompted ID is empty after lift, restore that group’s full raw mask on the 100k and lift again; several empties: increasing IoU. Skip a group whose raw mask was empty. At most one restore pass per prompted group.
  - Stage 2 skip: **sample id** = hash of `sample_100k.npz` coords, stored on the sample persist **and** `clicks.json`. Skip only when clicks are complete **and** ids match. Missing id means no skip. Backfill the live pair; do not force a human click round for this ficus.
  - Rematerialize from persisted `part_masks.npz` + `chosen_iou.json`; overwrite `material_tags.pt`. Call `predict_masks` only if those files are missing.
  - `configs/ficus.json` stays `frame_num` 125. Prove the bar with a one-off solver invocation that overrides `frame_num` to 5. `./scripts/run_pipeline.sh` does not point at a smoke config.
  - Reuse `material_tags.pt` only if length is *N* **and** every prompted Stage 2 id has count > 0. Otherwise enter Stage 3. No hand-delete as the lasting contract.
  - Tag IDs **1=pot / 2=trunk / 3=leaves**. Heuristic Primitives do not rewrite after lift.

## Decisions so far

- [Live persist identity and occupancy now](issues/01-live-persist-identity-and-occupancy.md) — All five named live files exist; clicks are complete with no sample id; tags length matches checkpoint *N* but tag 2 is 0; raw trunk mask sum 569. Findings: [research/01-live-persist-identity-and-occupancy.md](research/01-live-persist-identity-and-occupancy.md).
- [How the runner ingests frame_num](issues/02-runner-frame-num-ingest.md) — `frame_num` is `time_params["frame_num"]` from `--config` JSON (`ficus.json` 125); no time CLI today; smallest one-off is mutate that dict after decode (new runner flag), not a smoke config on `run_pipeline.sh`. Findings: [research/02-runner-frame-num-ingest.md](research/02-runner-frame-num-ingest.md).
- [Test contract for skip, survival, and occupancy](issues/03-test-contract-skip-survival-occupancy.md) — Always-on tests in `test_partsam_clicks.py` (rewrite skip to id-match; mismatch and missing id must not skip) and `test_partsam_merge.py` (three synthetic survival cases); occupancy next to its helper. No predict_masks, weights, solver, or live goldens.
- [Rematerialize env and occupancy helper seam](issues/04-rematerialize-env-and-occupancy-seam.md) — Rematerialize in physgauss; PartSAM env only for `predict_masks`. `--stage lift` grows a no-model branch (no fourth stage). Occupancy helper in `merge.py`; shell `--check-occupancy` exit 0/1.
- [Implement sample-id skip and survival rematerialize](issues/05-implement-sample-id-skip-and-survival.md) — `sample_id` SHA-256 of coords on npz + clicks; skip only on complete matching ids; `apply_survival` + lift rematerialize without `predict_masks`; `--check-occupancy`. Always-on tests green.
- [Add runner frame_num override](issues/06-add-runner-frame-num-override.md) — Optional `--frame_num` on the runner mutates `time_params` after decode; `ficus.json` 125 and `run_pipeline.sh` unchanged.
- [Occupancy gate in run_pipeline.sh](issues/07-occupancy-gate-in-run-pipeline.md) — Reuse tags only on `--check-occupancy` 0; else Stage 3 rematerialize in physgauss when masks+IoU exist, PartSAM `predict_masks` only if they do not. `ficus.json` 125 unchanged.
- [Backfill live clicks sample id](issues/08-backfill-live-clicks-sample-id.md) — Stamped the live 100k+clicks pair with `sample_id` `f92f062f0e7eff989a8083dc344ea3b17e4f27fffefae26a367f167e6eb68f56`; Stage 2 skip binds; no rebuild, no re-click, no `predict_masks`.
- [Prove the 5-frame solver bar](issues/09-prove-the-5-frame-solver-bar.md) — Live tags *N*=203 930, counts 1/2/3 = 32 476 / 2 509 / 168 945; `--frame_num` 5 exit 0, finite ply, no CUDA 700. `ficus.json` still 125. Log: [mpm_5frame.log](mpm_5frame.log). Check: [mpm_5frame_check.json](mpm_5frame_check.json).
- [Point orientation at the tagging fix](issues/10-point-orientation-at-the-tagging-fix.md) — Orientation occupancy-gated reuse + 5-frame bar held; spec later-map marked done; skip/survival no longer out of spec. `CONTEXT.md` unchanged.

## Not yet specified

- (none)

## Out of scope

- Full-length ficus wind (`frame_num` 125) as this effort’s bar; editing `configs/ficus.json`.
- Re-running `predict_masks` when masks and IoU already exist.
- Named order trunk > leaves > pot; thinner-trunk count floors.
- A second scene.
- Expanding `CONTEXT.md` with PartSAM.
- Live `MotionTranslator` / Motion Critique Loop.
- Digest Dashboard work.
- GitHub remote or push.
- Replacing the PhysGaussian MPM Solver.
