# Map: Spec the live ficus PartSAM tagging fix

## Destination

A written spec that names the allowed change to the PartSAM seam so a later session can produce a ficus Material Tag Tensor with non-trivial **1=pot / 2=trunk / 3=leaves** and a **short** PhysGaussian MPM Solver run that does not explode. This map does not implement. `CONTEXT.md` unchanged.

## Notes

- Effort slug: `partsam-live-tag-fix`
- Domain: Phys4DGS glossary in `CONTEXT.md` (Material Tag Tensor, PhysGaussian MPM Solver). Policy being amended: [PartSAM as Material Tag Tensor source](../partsam-as-tagger/spec.md). Wired producer: [Wire PartSAM as Material Tag Tensor producer in src/](../partsam-src-wiring/map.md). Live evidence: `data/outputs/partsam/`, `data/outputs/tags/material_tags.pt`. Trial: [Ficus PartSAM trial](../partsam-ficus-trial/map.md) ([RESULT.md](../partsam-ficus-trial/RESULT.md)).
- Skills: `/research`, `/grilling`, `/domain-modeling`; `/writing-for-agents` on the spec.
- This effort **writes** `spec.md` (and, if the spec-home ticket says so, a patch to the PartSAM-as-tagger spec). No `src/` change. No full-length `configs/ficus.json` (125-frame) campaign. No `CONTEXT.md` PartSAM term.
- Research notes: `.scratch/partsam-live-tag-fix/research/`
- Standing:
  - The object of the fix is the **Material Tag Tensor**, not a PhysGaussian MPM Solver rewrite. CUDA 700 at frame 95 is a symptom of a plant that lifted with **zero** trunk tags.
  - Merge: highest chosen-mask IoU (smaller mask on ties), plus prompted-ID **survival after lift** (full raw-mask restore, increasing IoU if several empty). Not named part order.
  - Success bar for a later execution map: *N* match; every prompted Stage 2 ID non-empty after lift; `frame_num` 5 finite / no CUDA 700; not 125-frame wind. No per-part count floors.
  - Stage 2: skip-if-exists only when clicks belong to **this** 100k sample. No new negatives rule in this spec.

## Decisions so far

- [Live-run occupancy vs trial](issues/01-live-run-occupancy-vs-trial.md) — Clicks did not miss the trunk (same world-xyz, millimetres from the new 100k). Highest-IoU merge left 16 trunk samples and zero tag-2 Gaussians; live raw trunk mask is also ~47× smaller than the trial’s. Findings: [research/01-live-run-occupancy-vs-trial.md](research/01-live-run-occupancy-vs-trial.md).
- [Sixteen trunk-only points to zero Gaussians](issues/02-sixteen-trunk-points-to-zero-gaussians.md) — Not a `lift_tags` bug: 16 merged tag-2 samples sit in a leaves-labeled neighborhood, so every Gaussian’s nearest labeled sample is pot or leaves. Findings: [research/02-sixteen-trunk-points-to-zero-gaussians.md](research/02-sixteen-trunk-points-to-zero-gaussians.md).
- [Spec vs trial vs src merge](issues/03-spec-vs-trial-vs-src-merge.md) — Spec and `src/` use highest chosen-mask IoU, then smaller mask on ties; the trial used named order trunk > leaves > pot. `src/` persists `chosen_iou.json`. Findings: [research/03-spec-vs-trial-vs-src-merge.md](research/03-spec-vs-trial-vs-src-merge.md).
- [Later execution success bar](issues/07-later-execution-success-bar.md) — Generic: *N* matches; every prompted Stage 2 ID is non-empty on the lifted Material Tag Tensor; 5-frame solver exit 0, finite, no CUDA 700; 125-frame wind stays out. No trunk > 1 000.
- [Which merge rule now](issues/04-which-merge-rule-now.md) — IoU merge stays; if a prompted ID is empty after lift, restore that group’s full raw mask (several empties: increasing IoU). Not named trunk > leaves > pot.
- [Is Stage 2 in the fix](issues/05-is-stage-2-in-the-fix.md) — In: sample-bound skip (no reuse of another 100k’s xyz). No new negatives rule.

## Not yet specified

- A later implementation map (`src/segmentation/partsam/merge.py`, `run_pipeline.sh` re-run).
- Orientation one-liner once the spec exists.

## Out of scope

- Implementing the fix in `src/`.
- Full-length ficus wind (`frame_num` 125) as this effort’s bar.
- Treating CUDA 700 as a PhysGaussian MPM Solver bug to patch.
- A second scene.
- Expanding `CONTEXT.md` with PartSAM.
- Re-running to chase a thinner trunk as a success bar.
- Digest Dashboard work.
