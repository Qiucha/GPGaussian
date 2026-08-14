# Map: PartSAM as lasting Material Tag Tensor source

## Destination

A written go/no-go on PartSAM as the lasting Material Tag Tensor source, plus a seam spec at [spec.md](spec.md) that a later implementation map can execute — or a written leave-as-trial. Generic recipe (surface, clicks, merge/lift, tag IDs **1=pot / 2=trunk / 3=leaves**) with ficus as the only evidence. One-line pointer in orientation **Next steps**. Not wiring `src/`. `CONTEXT.md` unchanged.

## Notes

- Effort slug: `partsam-as-tagger`
- Domain: Phys4DGS glossary in `CONTEXT.md`. Trial: [Ficus PartSAM trial](../partsam-ficus-trial/map.md) ([RESULT.md](../partsam-ficus-trial/RESULT.md)). Recipe: [PartSAM trial design (scene, I/O, success)](../agent-orientation/issues/06-partsam-trial-design.md). Gap: [PartSAM tagging gap](../agent-orientation/research/02-partsam-tagging-gap.md). Orientation: [docs/agents/orientation.md](../../docs/agents/orientation.md).
- Skills: `/research`, `/grilling`, `/domain-modeling`; `/writing-for-agents` when writing the spec and the orientation pointer.
- This effort **writes** `spec.md` and the orientation one-liner (overrides plan-only). No `src/` wiring. No second scene. No `CONTEXT.md` PartSAM term (not in the pipeline yet).
- Research notes: `.scratch/partsam-as-tagger/research/` (local-markdown tracker; not a git `research/` branch).
- Standing:
  - Tag IDs follow `configs/ficus.json` / FlashSplat: **1=pot, 2=trunk, 3=leaves**. Glossary examples (`0/1/2`) are not the on-disk contract.
  - The spec names **one intended producer** of the Material Tag Tensor.
  - **NO** despite the trial pass if any of: `partfield/` NVIDIA non-commercial blocks intended GitHub/academic use; the generic seam still needs a human to place clicks every scene; inference depends on unreproducible stubs as if they were the official path; overlap policy cannot be stated without another trial.
  - PartSAM emits class-agnostic part masks; mapping parts → Material Tag Tensor is this repo’s seam, not PartSAM.

## Decisions so far

- [NVIDIA-noncommercial partfield vs this repo's intended use](issues/01-partfield-license-vs-intended-use.md) — NVIDIA §3.3 binds `predict_masks` (must import `partfield/`) to non-commercial research/education; public academic GitHub is allowed if PartSAM is gitignored upstream (or vendored with the NVIDIA license). Commercial use is outside the grant. Findings: [research/01-partfield-license-vs-intended-use.md](research/01-partfield-license-vs-intended-use.md).
- [Which CUDA extensions PartSAM inference actually needs](issues/02-inference-cuda-extensions.md) — Three-click `predict_masks` imports only torkit3d (trial used a PyTorch FPS stub); apex/pointops are README-required for `eval_everypart` but unused on that driver; no upstream stub. Findings: [research/02-inference-cuda-extensions.md](research/02-inference-cuda-extensions.md).
- [Can automatic PartSAM prompts replace per-scene clicks for material IDs](issues/03-automatic-prompts-vs-clicks.md) — No: SEP only emits unlabeled instance IDs; paper A.2.8 says it cannot produce semantic labels. Trial used geometry + MLLM accept, not `eval_everypart`. Findings: [research/03-automatic-prompts-vs-clicks.md](research/03-automatic-prompts-vs-clicks.md).
- [Surface construction for the generic PartSAM recipe](issues/04-surface-construction-generic-recipe.md) — Screened Poisson from Gaussian means → 100k area sample → bake SH RGB; spec names the algorithm not pymeshlab; ball pivoting only if unclickable.
- [Click path for the generic PartSAM recipe](issues/05-click-path-generic-recipe.md) — Geometry proposes; MLLM accept/swap/resample; human only after two failed rounds; ficus bins; world-xyz click contract. Not a standing NO.
- [Overlap and merge policy without another trial](issues/06-overlap-merge-policy.md) — Highest chosen-mask predicted IoU wins; names not in the comparator; smaller mask on ties; unlabeled 100k do not vote; NN onto every Gaussian. Not the trial’s trunk>leaves>pot order. Not a standing NO.
- [May the documented inference path use the trial stubs](issues/07-documented-inference-stubs.md) — Spec’s supported three-click path is the in-repo PyTorch FPS stand-in (contract; not PartSAM official); omit apex/pointops. Not a standing NO.
- [Go/no-go: PartSAM as the lasting Material Tag Tensor source](issues/08-go-no-go-partsam-as-tagger.md) — **YES.** PartSAM is the lasting intended producer; a later map wires `src/`. None of the four standing NO bars fired. Trial pass is not this bar.
- [What happens to the current Material Tag Tensor producers](issues/09-current-taggers-if-yes.md) — No fallback. FlashSplat and LangSAM **retired** as tagging paths. Heuristic Primitives and Segmenter Agent **unchanged-but-not-intended**. PartSAM recipe is merge+NN only (no heuristic rewrite).
- [Code seam I/O contract for a later implementation map](issues/10-code-seam-io-contract.md) — Three stages: PLY→100k (mesh throwaway); 100k→clicks JSON (MLLM/human writes JSON); 100k+clicks+xyz→masks+IoU+`material_tags.pt` `(N,)` int32 IDs 1/2/3. Clone-not-vendor + FPS stand-in. Filenames/tree fog.
- [Write the PartSAM-as-tagger spec](issues/11-write-spec.md) — [spec.md](spec.md): YES + three-stage seam; IDs 1/2/3; no `src/` wiring.
- [Point orientation Next steps at the spec](issues/12-orientation-next-steps-pointer.md) — Orientation Immediate block is one pointer at [spec.md](spec.md).

## Not yet specified

_(none — destination reached; conda/weights packaging, `src/segmentation/` layout, and overlap retune belong to a later wiring map)_

## Out of scope

- Wiring PartSAM into `src/` (a later map if the spec says YES).
- A second scene trial (vasedeck, etc.).
- Full-length ficus wind campaign.
- Expanding `CONTEXT.md` with PartSAM.
- GitHub remote or push ([GitHub-Ready Working Tree](../github-ready-working-tree/map.md)).
- Replacing the PhysGaussian MPM Solver.
- Re-running the trial to chase a thinner trunk (rejected as a NO bar).
- Live MotionTranslator, eval suite, pipeline hygiene (other maps).
- Digest Dashboard work.
