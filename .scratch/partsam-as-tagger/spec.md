# Specification: PartSAM as Material Tag Tensor source

Status: ready-for-agent

## Go/no-go

**YES.** PartSAM is the lasting **intended producer** of the Material Tag Tensor. `src/segmentation/partsam` is the wired producer. This spec is the seam contract (including the live-run skip and survival amendments). Ficus is the only evidence; leftover caveats below are constraints, not a leave-as-trial.

Source: [Go/no-go: PartSAM as the lasting Material Tag Tensor source](issues/08-go-no-go-partsam-as-tagger.md). Trial pass: [RESULT.md](../partsam-ficus-trial/RESULT.md) (ingest bar only). Live-run amendments: [Spec the live ficus PartSAM tagging fix](../partsam-live-tag-fix/map.md).

## Intended producer

One producer. None of the others are fallback.

| Path | Spec |
| --- | --- |
| PartSAM recipe (this document) | Intended producer of `material_tags.pt` |
| FlashSplat | **Retired** as a tagging path (including `run_pipeline.sh` starting there) |
| LangSAM | **Retired** (no tagging-path consumer once FlashSplat is unhooked) |
| Heuristic Primitives | **Unchanged-but-not-intended** (digest/tests; not a rewriter on this seam) |
| Segmenter Agent | **Unchanged-but-not-intended** (plans those primitives) |

Source: [What happens to the current Material Tag Tensor producers](issues/09-current-taggers-if-yes.md).

## Solver-facing output

`material_tags.pt`: `(N,)` int32, `N` = checkpoint Gaussian count **before** opacity filter. Values only **1 = pot / 2 = trunk / 3 = leaves**. Consumed as today (`--tags_path`). Glossary examples `0/1/2` are not this file.

## Constraints

- **License.** `predict_masks` imports NVIDIA-noncommercial `partfield/`. Public academic GitHub is in grant if PartSAM is a **gitignored upstream clone** (or any vendored `partfield/` carries the NVIDIA license). Commercial use is outside the grant. Do not publish `partfield/`, the 859MB weights, or the clone. [NVIDIA-noncommercial partfield vs this repo's intended use](issues/01-partfield-license-vs-intended-use.md).
- **Inference.** Supported three-click path is this repo’s **PyTorch FPS stand-in** (deterministic; first seed index 0; trial file [torkit3d_stub.py](../partsam-ficus-trial/torkit3d_stub.py)) plus Hugging Face `Czvvd/PartSAM` weights. Compile neither torkit3d nor apex/pointops. Do not call this PartSAM-official. [May the documented inference path use the trial stubs](issues/07-documented-inference-stubs.md).
- **Evidence.** One scene (ficus). Trial trunk mask was oversized; live IoU-only merge emptied a prompted ID after lift. Survival (below) is the generic rule, not a thinner-trunk retune and not named part order.
- **Vocabulary.** PartSAM emits class-agnostic part masks. Mapping parts → Material Tag Tensor is this seam.

## Recipe (three stages)

Generic recipe. Ficus trial scripts under `.scratch/partsam-ficus-trial/` stay trial, not the seam. Exact persist filenames and the `src/` tree live under `src/segmentation/partsam/` except solver tags stay `material_tags.pt`.

### Stage 1 — surface sample

**In:** trained 3DGS checkpoint PLY.

**Do:** Screened Poisson from Gaussian means → area-sample 100k with face normals → bake SH RGB from the nearest mean via `sh_dc_to_rgb`. Name the **algorithm**, not a mesher library. **Ball pivoting** only if that mesh is unclickable.

**Persist:** 100k \(P_{in}\) (xyz, face normals, baked SH RGB).

**Throwaway:** the Poisson mesh. It is not a Material Tag Tensor and not PhysGaussian MPM Solver input.

Rejected: Gaussian means as \(P_{in}\); another mesher family; requiring a pre-existing scene mesh.

Source: [Surface construction for the generic PartSAM recipe](issues/04-surface-construction-generic-recipe.md).

### Stage 2 — clicks

**In:** that 100k sample.

**Do (happy path):** geometry proposes on-cloud candidates; MLLM only **accept / swap / resample** from labeled markers (no free-form xyz); snap nearest neighbor onto the 100k. Human only after **two** failed annotated rounds.

**Skip** only when persisted clicks **belong to this 100k sample** (same persist identity). Otherwise run the happy path on this cloud. Clicks world-xyz are valid for one sample, not a later rebuild.

Geometry bins for this tag vocabulary: low-\(z\) dark = pot; mid-\(z\) thin stem = trunk; high-\(z\) green = leaves. Segment-Every-Part / `eval_everypart` does not name pot/trunk/leaves — do not use it for this seam.

**Persist:** world-xyz clicks JSON, bound to this sample. Shape:

```json
{
  "frame": "world",
  "source": "100k sample before ValDataset bbox-normalize",
  "groups": {
    "pot": { "positives": [], "negatives": [] },
    "trunk": { "positives": [], "negatives": [] },
    "leaves": { "positives": [], "negatives": [] }
  }
}
```

One or more positives per group. Negatives empty until a mask retry. MLLM or human **writes** this JSON; they are not a Python import. No extra negatives policy beyond that retry.

**Throwaway:** annotated PNG previews.

Source: [Click path for the generic PartSAM recipe](issues/05-click-path-generic-recipe.md); [Is Stage 2 in the fix](../partsam-live-tag-fix/issues/05-is-stage-2-in-the-fix.md). Trial walkthrough (evidence, not the seam): [CLICK_PIPELINE.md](../partsam-ficus-trial/CLICK_PIPELINE.md).

### Stage 3 — masks, merge, lift

**In:** 100k sample, clicks JSON, Gaussian xyz from the same PLY; gitignored PartSAM clone + `Czvvd/PartSAM` weights; this repo’s FPS stand-in.

**Do:** `predict_masks` per named group. Persist **one chosen-mask predicted IoU scalar per group**. Merge on overlap: **highest IoU wins**; names are labels, not the comparator; **smaller mask** on IoU ties; unlabeled 100k samples do not vote; nearest labeled sample onto **every** Gaussian.

**Survival:** after that lift, every Stage 2 group that had a non-empty raw mask and at least one positive click must have a non-empty tag ID on the Material Tag Tensor (count the lifted tensor, not the 100k merge). If a prompted ID is empty, restore that group’s **full raw mask** on the 100k (overlap included) and lift again. If several prompted IDs are empty, restore in **increasing chosen IoU** (lowest first) so a later restore overwrites overlap. Skip a group whose raw mask was empty. At most one restore pass per prompted group.

Heuristic Primitives do not rewrite after lift.

**Persist:** three part masks over the 100k; those three IoU scalars; `material_tags.pt` as in Solver-facing output.

Source: [Overlap and merge policy without another trial](issues/06-overlap-merge-policy.md), [Which merge rule now](../partsam-live-tag-fix/issues/04-which-merge-rule-now.md), [Code seam I/O contract for a later implementation map](issues/10-code-seam-io-contract.md).

## Later implementation map — done

[Implement the live ficus PartSAM tagging fix](../partsam-live-tag-implement/map.md) met this bar:

1. `material_tags.pt` length equals checkpoint Gaussian count *N* (before opacity filter).
2. Every Stage 2 group with at least one positive click has its tag ID **non-empty on the lifted Material Tag Tensor** (count > 0).
3. PhysGaussian MPM Solver: `frame_num` **5**, exit 0, finite positions, no CUDA 700.

125-frame `configs/ficus.json` is not this bar. Per-part count floors (e.g. trunk > 1 000) are not this bar.

Source: [Later execution success bar](../partsam-live-tag-fix/issues/07-later-execution-success-bar.md); [Prove the 5-frame solver bar](../partsam-live-tag-implement/issues/09-prove-the-5-frame-solver-bar.md).

## Out of this spec

- A second scene trial.
- Full-length ficus wind campaign.
- Adding PartSAM to `CONTEXT.md`.
- Replacing the PhysGaussian MPM Solver.
- Digest Dashboard work.
- GitHub remote or push.
