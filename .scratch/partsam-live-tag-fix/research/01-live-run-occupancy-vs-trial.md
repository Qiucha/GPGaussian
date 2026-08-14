# Live-run occupancy vs ficus trial

Primary sources (2026-08-14): live artifacts `data/outputs/partsam/{part_masks.npz,chosen_iou.json,clicks.json,sample_100k.npz}` and `data/outputs/tags/material_tags.pt`; [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh); [`src/segmentation/partsam/merge.py`](../../../src/segmentation/partsam/merge.py) `merge_masks`; [`src/segmentation/partsam/infer.py`](../../../src/segmentation/partsam/infer.py); trial [RESULT.md](../../partsam-ficus-trial/RESULT.md), [tag_lift_stats.json](../../partsam-ficus-trial/tag_lift_stats.json), [mask_stats.json](../../partsam-ficus-trial/mask_stats.json), `mask_{pot,trunk,leaves}.npy`, [merge_and_lift.py](../../partsam-ficus-trial/merge_and_lift.py), [clicks.json](../../partsam-ficus-trial/clicks.json), `ficus_100k.npz`. Recomputed with `conda run -n physgauss` (numpy + torch + `merge_masks`). This note does **not** choose a merge rule.

**Gist:** Live PartSAM wrote a small trunk mask (569 / 100k) that almost entirely overlaps leaves (553). Highest chosen-IoU merge then left **16** trunk samples and **zero** tag-2 Gaussians. The same world-xyz clicks as the trial sit millimetres from the live 100k cloud; the trunk primary’s nearest sample is trunk-positive (and leaf-positive). Occupancy supports **merge wiping the remaining live trunk**, not a geometric “clicks missed the trunk.” A separate fact: the live **raw** trunk mask is already ~47× smaller than the trial’s, so merge is not the only occupancy gap.

## 1. Live `run_pipeline.sh` artifacts

[`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh) writes PartSAM under `data/outputs/partsam/` then solver tags at `data/outputs/tags/material_tags.pt`. On-disk timestamps for `part_masks.npz`, `chosen_iou.json`, `sample_100k.npz`, and `material_tags.pt` are 15 Aug 06:38; `clicks.json` is 15 Aug 06:32 (Stage 2 before Stage 3).

### 1.1 `part_masks.npz` sums and pairwise overlaps

File keys `pot`, `trunk`, `leaves`; each `uint8` shape `(100000,)`, values `{0,1}` (recompute).

| Group | Positive count | Exclusive (no other group) |
| --- | ---: | ---: |
| pot | 11 633 | 10 513 |
| trunk | **569** | **16** |
| leaves | 43 267 | 41 594 |

| Pair | Intersection |
| --- | ---: |
| pot ∩ trunk | **0** |
| pot ∩ leaves | 1 120 |
| trunk ∩ leaves | **553** |
| pot ∩ trunk ∩ leaves | 0 |
| any group | 53 796 |
| none | 46 204 |

Trunk is almost a subset of leaves (553 / 569). Pot and trunk do not overlap.

### 1.2 `chosen_iou.json`

On-disk scalars ([`data/outputs/partsam/chosen_iou.json`](../../../data/outputs/partsam/chosen_iou.json)):

| Group | Chosen-mask predicted IoU |
| --- | ---: |
| pot | 0.685440719127655 |
| trunk | 0.26535850763320923 |
| leaves | 0.2942025065422058 |

Ranking: pot > leaves > trunk. [`infer.py`](../../../src/segmentation/partsam/infer.py) `pick_best` takes `iou.argmax` among `multimask_output=True` candidates and returns that scalar; `run_stage_lift` persists it then calls `merge_masks(..., ious)`.

### 1.3 Merged 100k histogram (`merge_masks`)

[`merge.py`](../../../src/segmentation/partsam/merge.py) `merge_masks`: per sample, claimants with mask on; winner `min(claimants, key=lambda name: (-float(chosen_iou[name]), sizes[name], name))` — highest IoU, then smaller mask size, then name. Tag IDs: pot=1, trunk=2, leaves=3.

Recompute on live masks + live `chosen_iou.json`:

| Tag | Count |
| --- | ---: |
| 0 unlabeled | 46 204 |
| 1 pot | 11 633 |
| 2 trunk | **16** |
| 3 leaves | 42 147 |

That matches the overlap table: pot wins pot∩leaves (higher IoU, keeps all 11 633 pot positives); leaves wins trunk∩leaves (0.294 > 0.265), so 553 trunk positives become leaves; 16 trunk-only samples remain tag 2. No IoU tie, so the size comparator did not decide.

Counterfactual **named-priority paint on the same live masks** (trial `merge_priority` last-write trunk; not a recommendation): unlabeled 46 204, pot 10 513, **trunk 569**, leaves 42 714. Merge rule changes live trunk from 569 → 16; it does not create a trial-sized trunk.

### 1.4 `material_tags.pt` unique counts

`torch.load(..., weights_only=True)` in env `physgauss`: shape `(203930,)`, `torch.int32`.

| ID | Count |
| --- | ---: |
| 1 pot | 32 476 |
| 2 trunk | **0** |
| 3 leaves | 171 454 |
| 0 unlabeled | 0 |

Every Gaussian is labeled; none is trunk. Why 16 merged-100k trunk samples lift to zero Gaussians is out of this ticket (see issue 02).

## 2. Ficus trial occupancy

[RESULT.md](../../partsam-ficus-trial/RESULT.md): pass bar pot / trunk / leaves each non-trivial; **trunk > 1 000**. Lifted Gaussians: pot 30 339, **trunk 79 053**, leaves 94 538. Recipe: priority merge **trunk > leaves > pot**. Caveat: trunk∩leaves = 23 038 of 100k; merge gave those points to trunk.

[tag_lift_stats.json](../../partsam-ficus-trial/tag_lift_stats.json) (and recompute of `merge_priority` on the npy masks):

**Merged 100k:** n=100 000; unlabeled 42 543; pot 10 979; trunk 26 722; leaves 19 756.

**Lifted Gaussians:** n=203 930; unlabeled 0; pot 30 339; trunk 79 053; leaves 94 538. Reloaded trial `material_tags.pt` matches those unique counts (`int32`, shape `(203930,)`).

Trial raw masks (npy recompute; matches [mask_stats.json](../../partsam-ficus-trial/mask_stats.json)):

| Group | Positive | Exclusive |
| --- | ---: | ---: |
| pot | 11 842 | 10 979 |
| trunk | **26 722** | 3 418 |
| leaves | 42 794 | 19 241 |

| Pair | Intersection |
| --- | ---: |
| pot ∩ trunk | 348 |
| pot ∩ leaves | 597 |
| trunk ∩ leaves | **23 038** |
| pot ∩ trunk ∩ leaves | 82 |
| any / none | 57 457 / 42 543 |

Trial `merge_priority` ([merge_and_lift.py](../../partsam-ficus-trial/merge_and_lift.py)): paint pot, then leaves, then trunk — named order trunk > leaves > pot. Merged trunk count **equals** the raw trunk mask (26 722). Trial did not persist `chosen_iou.json`.

Live vs trial **raw** 100k positives: pot 11 633 vs 11 842 (similar); leaves 43 267 vs 42 794 (similar); trunk **569 vs 26 722**. Live and trial mask arrays are not equal. Live `sample_100k.npz` `coords` vs trial `ficus_100k.npz` `coords`: not equal; max abs diff ≈ 2.01 (different 100k clouds).

## 3. Live clicks vs live 100k (NN distance per group primary)

Live [`clicks.json`](../../../data/outputs/partsam/clicks.json) is **byte-identical** to trial [`clicks.json`](../../partsam-ficus-trial/clicks.json): `frame: world`, one positive per group, empty negatives, same xyz, same `mllm` accept-P0 blob.

Nearest neighbor of each primary on **live** `sample_100k.npz` `coords` (float32, shape `(100000, 3)`):

| Group | NN index | Euclidean distance | Mask at NN (pot, trunk, leaves) | Merged tag at NN |
| --- | ---: | ---: | --- | ---: |
| pot | 33 897 | 0.00447186731863 | (1, 0, 0) | 1 |
| trunk | 43 588 | 0.00737133086560 | (0, **1**, **1**) | **3** |
| leaves | 74 413 | 0.00819199647885 | (0, 0, 1) | 3 |

Distances are on the order of **10⁻³** scene units (millimetres if the ficus cloud is metre-scale). Primaries are on the live 100k, not off-cloud.

Same xyz vs **trial** `ficus_100k.npz` `coords`: distance **0** at indices 21 991 / 25 696 / 26 106 (on-cloud samples). Trial trunk primary NN is also trunk∩leaves `(0,1,1)`.

[`infer.py`](../../../src/segmentation/partsam/infer.py) feeds those world positives through `world_to_prompt` (mesh normalize + `clicks_through_prep`); it does not require the click to be an exact 100k row.

**“Clicks missed the trunk” (geometric miss):** not supported. The live trunk primary is ~0.007 from a 100k point that **is** trunk-positive. PartSAM did fire trunk at that neighborhood; the raw trunk mask is 569, not 0.

## 4. Trial merge vs live `merge_masks`

| | Trial | Live `src/` |
| --- | --- | --- |
| Rule | Named order trunk > leaves > pot ([merge_and_lift.py](../../partsam-ficus-trial/merge_and_lift.py) last-write trunk; [RESULT.md](../../partsam-ficus-trial/RESULT.md)) | Highest `chosen_iou` then smaller `sizes` then name ([`merge_masks`](../../../src/segmentation/partsam/merge.py); spec Stage 3) |
| IoU in merge | No. Trial used IoU only inside per-group `pick_best`, then discarded the scalar | Yes. Live persisted [`chosen_iou.json`](../../../data/outputs/partsam/chosen_iou.json) |
| Effect on this live overlap | Would keep all **569** live trunk positives | Leaves IoU > trunk IoU → **553** trunk∩leaves points become leaves; **16** trunk remain |
| Effect on trial overlap | Gave 23 038 trunk∩leaves points to trunk; merged trunk 26 722 | Not observed on trial (no trial IoU file). Do not apply live IoU scalars to trial masks as if they were measured there |

[`tests/test_partsam_merge.py`](../../../tests/test_partsam_merge.py) locks highest IoU on overlap and smaller mask on IoU tie.

## 5. Do the numbers support “clicks missed” or “merge wiped”?

**Merge wiped the live trunk (on the 100k, after inference):** supported. Live `chosen_iou` ranks leaves above trunk; 553 / 569 trunk positives are also leaves; `merge_masks` assigns them to leaves; merged trunk = 16; lifted tag 2 = 0.

**Clicks missed the trunk (prompt off the stem / off the cloud):** not supported by NN distances or by the trunk mask at the trunk primary’s nearest sample. Live clicks are the trial world xyz; they land millimetres from the new 100k; that NN is trunk-positive.

**Raw-mask occupancy is still unlike the trial.** Live trunk positives 569 vs trial 26 722, with similar pot/leaves sizes, on a **different** 100k sample. That gap exists **before** `merge_masks`. Named-priority on the live masks would still yield only 569 trunk samples, below the trial pass bar of trunk > 1 000 on **lifted Gaussians** ([RESULT.md](../../partsam-ficus-trial/RESULT.md)) and far below trial merged trunk 26 722. Occupancy therefore shows **two** stacked facts: a small live trunk prediction, then IoU merge reducing it to 16 / 0 Gaussians. This note does not pick which fact a later spec should change.
