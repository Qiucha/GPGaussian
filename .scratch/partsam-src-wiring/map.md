# Map: Wire PartSAM as Material Tag Tensor producer in src/

## Destination

`src/` implements the three-stage PartSAM recipe from [PartSAM as Material Tag Tensor source](../partsam-as-tagger/spec.md). A ficus 3DGS PLY (clicks already on disk, or geometry→MLLM JSON) writes `material_tags.pt` `(N,)` int32 **1=pot / 2=trunk / 3=leaves**. `run_pipeline.sh` is PartSAM (or reuse tags) → PhysGaussian MPM Solver — not FlashSplat, and not a Heuristic Primitive rewrite. Gitignored clone + `PARTSAM_ROOT` + Hugging Face `Czvvd/PartSAM` + in-repo FPS stand-in. Orientation Next steps points at the wired path. `CONTEXT.md` unchanged.

## Notes

- Effort slug: `partsam-src-wiring`
- Domain: Phys4DGS glossary in `CONTEXT.md`. Policy: [spec.md](../partsam-as-tagger/spec.md). Trial evidence: [Ficus PartSAM trial](../partsam-ficus-trial/map.md) ([ENV.md](../partsam-ficus-trial/ENV.md), [CLICK_PIPELINE.md](../partsam-ficus-trial/CLICK_PIPELINE.md)). Orientation: [docs/agents/orientation.md](../../docs/agents/orientation.md).
- Skills: `/research`, `/grilling`, `/domain-modeling`; `/tdd` on implement tickets; `/writing-for-agents` on the orientation pointer and README clone/env lines.
- This effort **writes** `src/`, `scripts/run_pipeline.sh`, README clone/env, `.gitignore` only if a path is not already ignored, and the orientation pointer (overrides plan-only). No second scene. No overlap retune. No `CONTEXT.md` PartSAM term.
- Research notes: `.scratch/partsam-src-wiring/research/` (local-markdown tracker; not a git `research/` branch).
- Standing:
  - Material Tag Tensor stays the domain object; PartSAM is the intended producer (vendor + recipe), named in orientation and the spec.
  - Merge is **highest chosen-mask predicted IoU**; names are labels; **smaller mask** on ties; unlabeled 100k do not vote; NN onto every Gaussian. Do not retune for a thinner trunk; do not re-run a ficus trial as a success bar.
  - Stage 2: geometry proposer + JSON persist/consume in `src/`; skip-if-exists is enough to produce ficus tags. Port the trial accept/swap **loop** (MLLM or human writes JSON; not a Python import of a VLM). Human after two failed annotated rounds.
  - Heuristic Primitives and Segmenter Agent unchanged-but-not-intended; they do not rewrite after lift.
  - FlashSplat and LangSAM: **unhook** from the intended tagging path. Do not delete their source or scrub the FlashSplat clone paragraph in this map.
  - Clone-not-vendor: default `third_party/PartSAM` (already under gitignored `third_party/`), env `PARTSAM_ROOT`, no torkit3d/apex/pointops compile. Do not publish `partfield/`, weights, or the clone.
  - Tag IDs **1=pot / 2=trunk / 3=leaves**; `N` = checkpoint Gaussian count before opacity filter.

## Decisions so far

- [Screened Poisson available in this checkout](issues/01-screened-poisson-in-checkout.md) — pymeshlab 2023.12.post1 Screened Poisson in `physgauss` (`compute_normal_for_point_clouds` then `generate_surface_reconstruction_screened_poisson` on Gaussian means); not in `PartSAM`; same-library ball pivoting exists unused; SH bake is `sh_dc_to_rgb` + nearest mean. Findings: [research/01-screened-poisson-in-checkout.md](research/01-screened-poisson-in-checkout.md).
- [Trial click loop vs spec JSON to port](issues/02-trial-click-loop-to-port.md) — Geometry propose (bins, K=5) + PNG are portable; accept/swap stays a Cursor-agent/human JSON write (not a Python VLM); skip-if-exists is `clicks.json`. Findings: [research/02-trial-click-loop-to-port.md](research/02-trial-click-loop-to-port.md).
- [Persist filenames and src/segmentation module tree](issues/03-filenames-and-module-tree.md) — Package `src/segmentation/partsam/`; `python -m src.segmentation.partsam`; artifacts in `data/outputs/partsam/` (`sample_100k.npz`, `clicks.json`, `part_masks.npz`, `chosen_iou.json`, throwaway `poisson_mesh.ply`); solver tags stay `data/outputs/tags/material_tags.pt`.
- [Test contract for the PartSAM seam without publishing weights](issues/04-test-contract-without-weights.md) — Always-on unittest only (fake-mask merge/IoU/lift, clicks JSON + bins, npz persist shape, FPS seed 0); no `predict_masks`, weights, or GPU/CI job in this map.
- [PartSAM conda env vs physgauss on the intended runner](issues/05-partsam-env-vs-physgauss.md) — Two envs; no cross-import. `physgauss`: Stage 1 (add trimesh) + Stage 2 + solver. `PartSAM`: whole `--stage lift`. `run_pipeline.sh` is four `conda run`s.
- [Clone, PARTSAM_ROOT, and weights docs](issues/06-clone-env-weights-docs.md) — README clone pin `b16d3e8` + HF `model.safetensors` into gitignored `third_party/PartSAM`; `PARTSAM_ROOT`; `get_partsam_root()`; two-env pip notes; FlashSplat paragraph kept.
- [FPS stand-in in src/](issues/07-fps-stand-in-in-src.md) — `src/segmentation/partsam/fps.py`: deterministic PyTorch FPS, first seed index 0, `install()` for `torkit3d`; tests in `tests/test_partsam_fps.py`.
- [Implement Stage 1 surface sample in src/](issues/08-implement-stage-1-surface.md) — `surface.py`: Poisson from means → 100k `sample_100k.npz` + throwaway `poisson_mesh.ply`; `--stage surface`; skip-if-exists; unittest fixture writer only (no Poisson in CI). `physgauss` still needs `trimesh` for the live sample.
- [Implement Stage 2 geometry and click JSON in src/](issues/09-implement-stage-2-clicks.md) — `clicks.py`: bins + K=5 candidates + `click_candidates.png`; spec `clicks.json` skip-if-complete; no VLM import; `--stage clicks`.
- [Implement Stage 3 masks, merge, and lift in src/](issues/10-implement-stage-3-lift.md) — `merge.py` IoU merge + NN lift; `infer.py` `predict_masks` in `PartSAM` env; `--stage lift` / `--reuse-tags`; tags `data/outputs/tags/material_tags.pt`.
- [run_pipeline.sh PartSAM to solver](issues/11-run-pipeline-partsam-to-solver.md) — intended runner is PartSAM (or reuse `material_tags.pt`) → solver; FlashSplat/`color_heuristic` unhooked, sources kept.
- [Point orientation at the wired PartSAM path](issues/12-orientation-wired-path-pointer.md) — orientation pipeline / Current state / Next steps name the wired producer; policy pointer is the PartSAM spec; `CONTEXT.md` unchanged.

## Not yet specified

- Ball pivoting if a future PLY’s Poisson mesh is unclickable (ficus already produced a clickable surface).
- Digest Dashboard viz for PartSAM-produced tags (IDs 1/2/3).
- Making the FlashSplat clone optional in README (hygiene map).

## Out of scope

- A second scene trial; full-length ficus wind campaign.
- Overlap retune / thinner-trunk success bar.
- Adding PartSAM to `CONTEXT.md`.
- Deleting `flashsplat.py` / LangSAM or scrubbing FlashSplat from README.
- Live `MotionTranslator.translate`; [Motion Critique Loop spec](../mpm-critique-loop/map.md) wiring.
- GitHub remote or push.
- Replacing the PhysGaussian MPM Solver.
- GPU/CI runners for `predict_masks` (this map: always-on unittest only).
