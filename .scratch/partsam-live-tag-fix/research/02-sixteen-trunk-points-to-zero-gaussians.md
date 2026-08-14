# Why 16 merged trunk samples lift to zero tag-2 Gaussians

Primary sources (2026-08-14): [`src/segmentation/partsam/merge.py`](../../../src/segmentation/partsam/merge.py) (`merge_masks`, `lift_tags`, `write_material_tags`, `TAG_*`); [`src/segmentation/partsam/infer.py`](../../../src/segmentation/partsam/infer.py) `run_stage_lift`; [`src/segmentation/partsam/surface.py`](../../../src/segmentation/partsam/surface.py) `load_gaussian_means_rgb`; [`tests/test_partsam_merge.py`](../../../tests/test_partsam_merge.py); live [`data/outputs/partsam/part_masks.npz`](../../../data/outputs/partsam/part_masks.npz), [`sample_100k.npz`](../../../data/outputs/partsam/sample_100k.npz), [`chosen_iou.json`](../../../data/outputs/partsam/chosen_iou.json); live [`data/outputs/tags/material_tags.pt`](../../../data/outputs/tags/material_tags.pt); Gaussian means from `data/models/ficus_whitebg` via `load_gaussian_means_rgb`. Numbers below recomputed in `physgauss` (numpy 1.26.4, scipy `cKDTree`, torch 2.7.1). This note does not choose a merge rule.

`lift_tags` does not drop tag 2 by dtype, empty-mask, or wrong id. The live merge leaves **16** tag-2 samples. Every Gaussian’s nearest **labeled** 100k sample is pot or leaves. No Gaussian is closer to those 16 points than to a non-trunk labeled sample.

## 1. Merged-100k count for tag 2

`merge.py`: `TAG_POT = 1`, `TAG_TRUNK = 2`, `TAG_LEAVES = 3`. `merge_masks` writes `np.int32` zeros, then for each sample with one or more group masks sets `merged[i] = GROUP_TAGS[winner]`. Winner is `min` of claimants by `(-chosen_iou[name], sizes[name], name)`.

Live `chosen_iou.json`: pot `0.685440719127655`, trunk `0.26535850763320923`, leaves `0.2942025065422058`. Leaves IoU > trunk IoU, so on trunk∩leaves the winner is leaves.

Live `part_masks.npz` (`uint8`, length 100 000): pot 11 633, trunk 569, leaves 43 267. Pairwise: pot∩trunk 0, pot∩leaves 1 120, trunk∩leaves 553, all-three 0. Exclusive trunk (`trunk & ~pot & ~leaves`) = **16**. Trunk points that also have another group = 553.

Recomputed `merge_masks(pot, trunk, leaves, chosen_iou)` histogram:

| merged id | count |
| --- | ---: |
| 0 unlabeled | 46 204 |
| 1 pot | 11 633 |
| **2 trunk** | **16** |
| 3 leaves | 42 147 |

Those 16 are exactly the exclusive-trunk mask points (`merged==2` with no trunk mask = 0; trunk mask but `merged!=2` = 553). Tag 2 is present on the 100k cloud after merge. It is not an empty class at lift input.

## 2. Unlabeled 100k are excluded from the NN reference

`lift_tags` (`merge.py`):

```python
labeled = np.asarray(sample_tags) != 0
if not np.any(labeled):
    raise RuntimeError("no labeled 100k samples to lift")
ref_xyz = np.asarray(sample_xyz, dtype=np.float32)[labeled]
ref_tags = np.asarray(sample_tags, dtype=np.int64)[labeled]
```

Then each Gaussian chunk is `torch.cdist` against `ref` only; `argmin` indexes `ref_tags`. Unlabeled (`0`) samples are not in `ref`. The empty-`labeled` branch raises; it does not return zeros.

`run_stage_lift` (`infer.py`) calls `lift_tags(gaussian_xyz, sample["coords"], merged)` after `merge_masks`. Same exclusion.

`tests/test_partsam_merge.py` `test_unlabeled_samples_do_not_vote_nn_lifts_every_gaussian`: sample tags `[1, 2, 0, 3]`; a query nearer the unlabeled `0` sample than the leaves sample still lifts to leaves.

Counterfactual on the live arrays (KDTree over **all** 100k, including unlabeled): lifted histogram `{0: 43963, 1: 27748, 3: 132219}` — still **zero** tag 2. Excluding unlabeled is not what zeros trunk.

## 3. Geometry: 16 trunk samples vs Gaussian NN

100k `sample_100k.npz` `coords`: `(100000, 3)` float32, finite, bbox about `[-1.11,-1.34,-1.14]`–`[0.89,1.06,1.25]`. The 16 merged tag-2 indices: `3407, 10445, 10781, 30714, 34984, 46228, 52626, 55736, 61397, 72874, 73233, 73936, 78394, 79555, 88375, 96702`. Their xyz sit in a small patch (`x` about −0.027…0.052, `y` 0.067…0.093, `z` 0.028…0.061).

They are a clump, not 16 isolated sprinkles: for 14 of 16, the nearest **other labeled** 100k point is also tag 2 (self-NN distance 0; second-NN 0.0028–0.0127). For the other two, the nearest other labeled point is tag 3 (leaves) at 0.00664 and 0.00834.

Every one of the 16 has its nearest **non-trunk** labeled neighbor as **leaves (3)**. Distances trunk→nearest leaves-labeled sample: min 0.00664, median 0.01717, max 0.02509. Non-trunk labeled points among themselves (every 50th, 2nd-NN) have median spacing 0.00672 (p10 0.00252) — denser than the gap from the trunk clump to leaves.

Gaussian means from `load_gaussian_means_rgb("data/models/ficus_whitebg")`: `(203930, 3)` float32, bbox `[-0.37,-0.86,-1.03]`–`[0.55,0.58,1.14]`.

NN of every Gaussian onto **labeled** 100k only (same rule as `lift_tags`; scipy `cKDTree`):

| nearest labeled tag | count |
| --- | ---: |
| 1 pot | 32 476 |
| 2 trunk | **0** |
| 3 leaves | 171 454 |

That assignment equals the on-disk Material Tag Tensor (`torch.load(..., weights_only=True)`: shape `(203930,)`, `torch.int32`, unique counts `{1: 32476, 3: 171454}`). Live `lift_tags` and this recompute agree; tag 2 is absent after lift, not lost in `write_material_tags`.

No Gaussian is closer to any of the 16 trunk samples than to a non-trunk labeled sample (0 strict, 0 ties). Min Gaussian→nearest trunk-sample distance is **0.02263** (median 0.771). That is larger than every trunk→leaves gap above, and larger than every half-gap Voronoi radius (0.00332–0.01255). Zero Gaussians fall inside those balls. Trunk appears among the 5 nearest labeled samples for 1 Gaussian and among the 10 nearest for 13; it is never nearest.

So the 16 points are surrounded, in the lift metric, by denser leaves-labeled 100k samples that sit between the trunk clump and every Gaussian mean.

## 4. Bug vs geometry

Checked against `lift_tags` / `write_material_tags` / live tensors:

- **Wrong tag id:** `TAG_TRUNK` is 2; merge histogram key 2 has 16; lift copies `ref_tags` with no remapping; `write_material_tags` is `torch.from_numpy(..., dtype=np.int32)` and requires 1-D.
- **Empty labeled set:** 53 796 labeled samples; the `RuntimeError` branch did not run (tags file exists with 1 and 3).
- **Dtype wipe:** merge `int32`, lift `ref_tags` `int64` then `astype(np.int32)`; saved tensor `int32`; 2 is representable.
- **NaNs:** none in 100k coords or Gaussian means.
- **Unlabeled in the reference:** they are excluded (code + test). Including them still yields zero tag 2.
- **Write ≠ lift:** saved histogram equals recomputed NN histogram.

What zeros trunk is nearest-labeled-sample lift on a 16-point trunk class whose Voronoi cells (vs 53 780 non-trunk labeled samples) contain no Gaussian means. The 553 trunk-mask points that lost the IoU contest never enter `ref_tags` as 2; that is `merge_masks`, not a lift defect. This note does not pick a replacement merge or lift rule.
