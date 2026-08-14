# Specification: PartSAM as Material Tag Tensor source

Status: ready-for-agent

## Go/no-go

**YES.** PartSAM is the lasting **intended producer** of the Material Tag Tensor. A later map wires `src/`. This spec is that handoff. Ficus is the only evidence; leftover caveats below are constraints, not a leave-as-trial.

Source: [Go/no-go: PartSAM as the lasting Material Tag Tensor source](issues/08-go-no-go-partsam-as-tagger.md). Trial pass: [RESULT.md](../partsam-ficus-trial/RESULT.md) (ingest bar only).

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
- **Evidence.** One scene (ficus). Trunk mask on the trial was oversized; do not treat that as a NO, and do not retune overlap in this spec.
- **Vocabulary.** PartSAM emits class-agnostic part masks. Mapping parts → Material Tag Tensor is this seam.

Fog for the later map (not this spec): conda/weights packaging for a new checkout; Python module layout under `src/segmentation/`; overlap retune after wiring.

## Recipe (three stages)

Generic recipe. Ficus trial scripts under `.scratch/partsam-ficus-trial/` stay trial, not the seam. Exact persist filenames and the `src/` tree are later-map fog except `material_tags.pt`.

**Done** when a later map can implement each stage’s persist/throwaway split without inventing merge, click, or tag-ID policy.

### Stage 1 — surface sample

**In:** trained 3DGS checkpoint PLY.

**Do:** Screened Poisson from Gaussian means → area-sample 100k with face normals → bake SH RGB from the nearest mean via `sh_dc_to_rgb`. Name the **algorithm**, not a mesher library. **Ball pivoting** only if that mesh is unclickable.

**Persist:** 100k \(P_{in}\) (xyz, face normals, baked SH RGB).

**Throwaway:** the Poisson mesh. It is not a Material Tag Tensor and not PhysGaussian MPM Solver input.

Rejected: Gaussian means as \(P_{in}\); another mesher family; requiring a pre-existing scene mesh.

Source: [Surface construction for the generic PartSAM recipe](issues/04-surface-construction-generic-recipe.md).

### Stage 2 — clicks

**In:** that 100k sample.

**Do (happy path):** geometry proposes on-cloud candidates; MLLM only **accept / swap / resample** from labeled markers (no free-form xyz); snap nearest neighbor onto the 100k. Human only after **two** failed annotated rounds. Skip this stage if clicks already exist.

Geometry bins for this tag vocabulary: low-\(z\) dark = pot; mid-\(z\) thin stem = trunk; high-\(z\) green = leaves. Segment-Every-Part / `eval_everypart` does not name pot/trunk/leaves — do not use it for this seam.

**Persist:** world-xyz clicks JSON. Shape:

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

One or more positives per group. Negatives empty until a mask retry. MLLM or human **writes** this JSON; they are not a Python import.

**Throwaway:** annotated PNG previews.

Source: [Click path for the generic PartSAM recipe](issues/05-click-path-generic-recipe.md). Trial walkthrough (evidence, not the seam): [CLICK_PIPELINE.md](../partsam-ficus-trial/CLICK_PIPELINE.md).

### Stage 3 — masks, merge, lift

**In:** 100k sample, clicks JSON, Gaussian xyz from the same PLY; gitignored PartSAM clone + `Czvvd/PartSAM` weights; this repo’s FPS stand-in.

**Do:** `predict_masks` per named group. Persist **one chosen-mask predicted IoU scalar per group** (the ficus trial did not). Merge on overlap: **highest IoU wins**; names are labels, not the comparator; **smaller mask** on ties; unlabeled 100k samples do not vote; nearest labeled sample onto **every** Gaussian. Not the trial’s named order trunk > leaves > pot. Heuristic Primitives do not rewrite after lift.

**Persist:** three part masks over the 100k; those three IoU scalars; `material_tags.pt` as in Solver-facing output.

Source: [Overlap and merge policy without another trial](issues/06-overlap-merge-policy.md), [Code seam I/O contract for a later implementation map](issues/10-code-seam-io-contract.md).

## Out of this spec

- Wiring `src/` (the later map).
- A second scene trial.
- Full-length ficus wind campaign.
- Adding PartSAM to `CONTEXT.md`.
- Replacing the PhysGaussian MPM Solver.
- Digest Dashboard work.
- GitHub remote or push.
