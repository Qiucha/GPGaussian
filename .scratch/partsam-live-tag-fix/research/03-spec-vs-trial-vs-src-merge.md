# Spec vs trial vs src merge rule

Primary sources (2026-08-14): [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md); [Overlap and merge policy without another trial](../../partsam-as-tagger/issues/06-overlap-merge-policy.md); [Code seam I/O contract](../../partsam-as-tagger/issues/10-code-seam-io-contract.md); trial [Merge masks and lift](../../partsam-ficus-trial/issues/06-merge-and-lift-tags.md), [merge_and_lift.py](../../partsam-ficus-trial/merge_and_lift.py), [run_predict_clicks.py](../../partsam-ficus-trial/run_predict_clicks.py); [`src/segmentation/partsam/merge.py`](../../../src/segmentation/partsam/merge.py), [`infer.py`](../../../src/segmentation/partsam/infer.py). This note does **not** choose a new merge rule.

**Comparator (quoted):** spec and `src/` use **chosen-mask predicted IoU** (highest wins), then **mask size** on IoU ties (smaller wins). Names are labels, not that comparator. The ficus trial merge used **named order trunk > leaves > pot**. The trial used IoU only to pick among three PartSAM candidates **per group**, then discarded the scalar.

## 1. Specified merge (as-tagger spec)

[spec.md](../../partsam-as-tagger/spec.md) Stage 3 **Do:** `predict_masks` per named group. Persist **one chosen-mask predicted IoU scalar per group** (the ficus trial did not). Merge on overlap: **highest IoU wins**; names are labels, not the comparator; **smaller mask** on ties; unlabeled 100k samples do not vote; nearest labeled sample onto **every** Gaussian. **Not** the trial’s named order trunk > leaves > pot.

That Stage 3 sentence cites [issues/06-overlap-merge-policy.md](../../partsam-as-tagger/issues/06-overlap-merge-policy.md). The resolved Answer there:

> On overlap, the point goes to the mask with the **highest chosen-mask predicted IoU** (the scalar PartSAM already returns when picking among three candidates per prompt). Names are labels on masks, not the comparator. A later map must **persist those IoU scalars** (the ficus trial did not). Ties: **smaller mask wins**. Unlabeled 100k samples do not vote; every Gaussian gets the nearest labeled sample after merge. Tag IDs remain 1=pot / 2=trunk / 3=leaves on the surviving unique regions.

[issues/10-code-seam-io-contract.md](../../partsam-as-tagger/issues/10-code-seam-io-contract.md) Stage 3 persist: three part masks over the 100k; **one chosen-mask predicted IoU scalar per named group**; `material_tags.pt`. Merge restated as highest IoU; names not the comparator; smaller mask on ties.

The spec does **not** name a persist filename for the IoU scalars (filenames were later-map fog in that spec). It does not add a third comparator after size.

## 2. What the ficus trial ran

[issues/06-merge-and-lift-tags.md](../../partsam-ficus-trial/issues/06-merge-and-lift-tags.md) asked for priority merge **trunk > leaves > pot**, then NN lift. Answer: that named order on the 100k, then nearest-neighbor onto Gaussian means (labeled samples only). Tag IDs 1=pot / 2=trunk / 3=leaves.

[merge_and_lift.py](../../partsam-ficus-trial/merge_and_lift.py) implements that as last-write-wins paint:

```python
merged[pot > 0] = TAG_POT      # 1
merged[leaves > 0] = TAG_LEAVES  # 3
merged[trunk > 0] = TAG_TRUNK    # 2
```

Trunk overwrites leaves and pot; leaves overwrites pot. No IoU argument. No mask-size comparison. Unlabeled samples (`0`) do not enter `nn_lift` (`labeled = merged != 0`); every Gaussian still gets a tag from the nearest labeled 100k point.

Trial persist from that script: `merged_100k_tags.npy`, `material_tags.pt`, `tag_lift_stats.json`, two PNGs. No `chosen_iou.json`. [tag_lift_stats.json](../../partsam-ficus-trial/tag_lift_stats.json) `files` lists those artifacts only.

IoU **did** appear in mask **selection**, not merge. [run_predict_clicks.py](../../partsam-ficus-trial/run_predict_clicks.py) `pick_best` takes `iou.argmax(dim=-1)` among `multimask_output=True` candidates and returns **only** the binary mask. It prints the IoU tensor; it does not return or write the chosen scalar. Persist is `mask_{pot,trunk,leaves}.npy`, `part_masks.npz`, `ficus_100k_part_masks.png`, `mask_stats.json` (counts / retries). There is no `*iou*` file under `.scratch/partsam-ficus-trial/`.

## 3. What `src/` implements

[`merge.py`](../../../src/segmentation/partsam/merge.py) `merge_masks(pot, trunk, leaves, chosen_iou)`: for each sample, claimants are groups whose mask is on; winner is `min(claimants, key=lambda name: (-float(chosen_iou[name]), sizes[name], name))`. That is:

| Rank | Key | Effect |
| --- | --- | --- |
| 1 | `-chosen_iou[name]` | **Highest chosen IoU wins** |
| 2 | `sizes[name]` (`mask.sum()`) | **Smaller mask** on IoU tie |
| 3 | `name` | Lexicographic (`leaves` < `pot` < `trunk`) if IoU **and** size also tie |

Rank 3 is in this function; the spec/06 Answer stop at smaller mask. Tests in `tests/test_partsam_merge.py` cover highest IoU on overlap and smaller mask on equal IoU; they do not assert the name key.

`lift_tags` matches trial/spec: unlabeled 100k (`!= 0`) are dropped from the NN reference; every Gaussian is labeled from the nearest remaining sample.

**`chosen_iou.json` persist:** `CHOSEN_IOU_NAME = "chosen_iou.json"`. `write_chosen_iou` writes JSON `{pot, trunk, leaves}` floats (key order `GROUP_NAMES`). [`infer.py`](../../../src/segmentation/partsam/infer.py) `pick_best` returns `(mask, chosen_iou)` from the same argmax as the trial. `run_stage_lift` writes `part_masks.npz` and **`chosen_iou.json`** under `--output_dir`, then `merge_masks(..., ious)` with those scalars, then `material_tags.pt`.

## 4. Side-by-side

| | Spec / 06 Answer | Ficus trial | `src/segmentation/partsam` |
| --- | --- | --- | --- |
| Overlap comparator | Highest **chosen-mask predicted IoU**; names are labels | **Named order** trunk > leaves > pot | Highest **chosen IoU**, then **smaller mask**, then name |
| IoU role | Merge comparator + persist | Only `argmax` among 3 candidates per group; scalar discarded | Same per-group pick **and** merge input |
| Size | Tie-break: smaller mask | Unused | Tie-break after IoU |
| Persist IoU | Required (filename fog in that spec) | **Not** persisted | **`chosen_iou.json`** next to `part_masks.npz` |
| Unlabeled / lift | No vote; NN onto every Gaussian | Same | Same |
| Tag IDs | 1 / 2 / 3 | Same | Same |

`src/` implements the spec’s IoU-then-size rule, not the trial named order, and it persists `chosen_iou.json`. This note does not pick a replacement rule.
