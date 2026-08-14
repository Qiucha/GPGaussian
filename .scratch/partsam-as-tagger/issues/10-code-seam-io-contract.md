# 10 - Code seam I/O contract for a later implementation map

Type: grilling
Status: resolved
Blocked by: 04, 05, 06, 08

## Question

What I/O contract would a later `src/` map implement (or explicitly **not** implement, if NO)?

Cover: inputs (PLY / 100k sample / clicks JSON), outputs (`material_tags.pt` length = Gaussian count, tag IDs 1/2/3), env/weights as documented clone-not-vendor, and what stays throwaway vs becomes the seam. Not the Python file tree (fog). If the go/no-go is NO, the contract is “do not integrate; trial artifacts stay under `.scratch/partsam-ficus-trial/`.”

## Answer

Go/no-go is YES ([Go/no-go: PartSAM as the lasting Material Tag Tensor source](08-go-no-go-partsam-as-tagger.md)), so this is an integrate contract, not leave-as-trial. A later `src/` map implements **three named stages**. Exact filenames, conda layout, and the Python file tree remain fog.

**Stage 1 — surface sample.** In: trained 3DGS checkpoint PLY. Persist: 100k \(P_{in}\) with xyz, face normals, baked SH RGB ([Surface construction for the generic PartSAM recipe](04-surface-construction-generic-recipe.md)). Throwaway: Screened Poisson mesh (ball pivoting only if unclickable; not run here).

**Stage 2 — clicks.** In: that 100k sample. Persist: world-xyz clicks JSON (`frame: world`, source = 100k before ValDataset bbox-normalize; groups pot / trunk / leaves; one or more positives each; negatives empty until mask retry). Geometry proposes in code; MLLM or human only **writes** that JSON (no free-form xyz, not a Python import) ([Click path for the generic PartSAM recipe](05-click-path-generic-recipe.md)). Skip if clicks already exist. Throwaway: annotated PNG previews.

**Stage 3 — masks, merge, lift.** In: 100k sample, clicks, Gaussian xyz from the same PLY; gitignored PartSAM clone + Hugging Face `Czvvd/PartSAM` weights; this repo’s PyTorch FPS stand-in; no apex/pointops ([May the documented inference path use the trial stubs](07-documented-inference-stubs.md), [NVIDIA-noncommercial partfield vs this repo's intended use](01-partfield-license-vs-intended-use.md)). Persist: three part masks over the 100k samples; one chosen-mask predicted IoU scalar per named group; `material_tags.pt`. Merge: highest IoU wins; names are labels not the comparator; smaller mask on ties; unlabeled 100k do not vote; nearest labeled sample onto every Gaussian ([Overlap and merge policy without another trial](06-overlap-merge-policy.md)).

**Solver-facing output.** `(N,)` int32, `N` = checkpoint Gaussian count **before** opacity filter; values only **1=pot / 2=trunk / 3=leaves**. Consumed as today: `--tags_path` → `material_tags.pt`. Glossary 0/1/2 examples are not this file.

**Not published.** `partfield/`, the 859MB weights, the PartSAM clone. Trial scripts under `.scratch/partsam-ficus-trial/` stay trial, not the seam.
