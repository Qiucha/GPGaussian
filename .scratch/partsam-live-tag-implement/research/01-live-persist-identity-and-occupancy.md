# Live persist identity and occupancy now

Primary sources (measured 2026-08-14): live artifacts `data/outputs/partsam/{sample_100k.npz,clicks.json,part_masks.npz,chosen_iou.json}` and `data/outputs/tags/material_tags.pt`; default ficus PLY via [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh) `MODEL_PATH=data/models/ficus_whitebg` and [`src/segmentation/partsam/surface.py`](../../../src/segmentation/partsam/surface.py) `resolve_checkpoint_ply` / `load_gaussian_means_rgb`; [`src/segmentation/partsam/clicks.py`](../../../src/segmentation/partsam/clicks.py) `validate_clicks`; [`src/segmentation/partsam/merge.py`](../../../src/segmentation/partsam/merge.py) `write_sample` contract in `surface.write_sample_100k` / `write_part_masks`; Stage 3 I/O in [`src/segmentation/partsam/infer.py`](../../../src/segmentation/partsam/infer.py) `run_stage_lift`; solver-facing *N* in [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md). Recomputed with `conda run -n physgauss` (numpy + torch + plyfile + `validate_clicks` + `load_gaussian_means_rgb`). This note does **not** choose a sample-id field name and does **not** implement skip or rematerialize.

**Gist:** All five named persist files exist on the live ficus path. `clicks.json` is complete under today’s `validate_clicks` (`source` is the spec string); neither clicks nor `sample_100k.npz` stores a sample identity, so a later sample-id skip would see a **missing id** on this pair. `material_tags.pt` length **203 930** equals checkpoint *N* (iteration_60000 PLY vertex count, no opacity filter); tag **2 = 0**. Raw `part_masks.npz` trunk sum is **569**, so rematerialize has a non-empty raw trunk mask. Backfill would consume this 100k + clicks pair in place; rematerialize would consume those masks + `chosen_iou.json` + 100k `coords` + PLY means and overwrite `material_tags.pt`. `run_stage_lift` today always calls `predict_masks`; it does not rematerialize.

## 1. Which named files exist

[`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh) writes PartSAM under `data/outputs/partsam/` and solver tags at `data/outputs/tags/material_tags.pt`. All five named files are present (stat + load, 2026-08-14). UTC mtimes: `clicks.json` 2026-08-14T22:32:30Z; `sample_100k.npz` 22:38:14Z; `part_masks.npz` and `chosen_iou.json` 22:38:28Z; `material_tags.pt` 22:38:29Z.

Also on that directory (not in the ticket’s named set): `poisson_mesh.ply`, `live_run.log`. Spec Stage 1 calls the Poisson mesh throwaway.

### 1.1 `data/outputs/partsam/sample_100k.npz`

Exists, 3 101 014 bytes. Keys from `np.load`: `coords`, `normals`, `colors`, `point_to_face` — the same four arrays [`write_sample_100k`](../../../src/segmentation/partsam/surface.py) writes. No extra array.

| Key | dtype | shape |
| --- | --- | --- |
| `coords` | float32 | `(100000, 3)` |
| `normals` | float32 | `(100000, 3)` |
| `colors` | uint8 | `(100000, 3)` |
| `point_to_face` | int32 | `(100000,)` |

### 1.2 `data/outputs/partsam/clicks.json`

Exists, 660 bytes. Top-level keys: `frame`, `source`, `groups`, `mllm`. See §2.

### 1.3 `data/outputs/partsam/part_masks.npz`

Exists, 28 579 bytes (compressed). Keys: `pot`, `trunk`, `leaves`. Each `uint8` shape `(100000,)`, values `{0, 1}`. Matches [`write_part_masks`](../../../src/segmentation/partsam/merge.py). Raw sums in §4.

### 1.4 `data/outputs/partsam/chosen_iou.json`

Exists, 94 bytes. Keys `pot`, `trunk`, `leaves` (floats). On-disk scalars:

| Group | Chosen-mask predicted IoU |
| --- | ---: |
| pot | 0.685440719127655 |
| trunk | 0.26535850763320923 |
| leaves | 0.2942025065422058 |

### 1.5 `data/outputs/tags/material_tags.pt`

Exists, 816 890 bytes. `torch.load(..., weights_only=True)`: `torch.int32` shape `(203930,)`. Occupancy in §3.

## 2. `clicks.json` keys, sample identity, `validate_clicks`

Live file top-level keys (load JSON): `frame`, `source`, `groups`, `mllm`.

- `frame`: `"world"`
- `source`: `"100k sample before ValDataset bbox-normalize"` — same string as the Stage 2 persist example in [spec.md](../../partsam-as-tagger/spec.md)
- `groups`: `pot`, `trunk`, `leaves`; each has `positives` (one xyz list) and `negatives` (`[]`)
- `mllm`: extra blob (`round`, `decision`, `candidates`, `preview`); [`validate_clicks`](../../../src/segmentation/partsam/clicks.py) does not forbid extra keys

No top-level key whose name contains `id`, `hash`, or `sample`. Group objects have only `positives` / `negatives`. `sample_100k.npz` likewise has no identity array (§1.1). There is **no sample id on disk today**.

[`validate_clicks`](../../../src/segmentation/partsam/clicks.py) requires `frame == "world"`, key `source` present (any value), `groups` mapping with `pot`/`trunk`/`leaves`, each with a `positives` list of length ≥ 1 and a `negatives` list. Calling it on the live doc: no exception. `clicks_are_complete` is `True`. Completeness today does **not** include a sample id.

[`run_stage_clicks`](../../../src/segmentation/partsam/clicks.py) skips when `clicks.json` exists and `clicks_are_complete` — still identity-unaware.

## 3. `material_tags.pt` occupancy vs checkpoint *N*

[`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh) default `MODEL_PATH` is `data/models/ficus_whitebg`. [`resolve_checkpoint_ply`](../../../src/segmentation/partsam/surface.py) picks the highest `iteration_*` directory: `point_cloud/iteration_60000/point_cloud.ply`. [`load_gaussian_means_rgb`](../../../src/segmentation/partsam/surface.py) reads every PLY vertex (`x,y,z` + SH DC); it does **not** apply an opacity filter. [`run_stage_lift`](../../../src/segmentation/partsam/infer.py) lifts onto that `gaussian_xyz`. Spec solver-facing output: `(N,)` int32, *N* = checkpoint Gaussian count **before** opacity filter ([spec.md](../../partsam-as-tagger/spec.md)). Opacity filter lives later in [`src/simulation/runner.py`](../../../src/simulation/runner.py) (`init_opacity > opacity_threshold`), after tags are loaded.

PLY vertex counts (`PlyData` `vertex` length, 2026-08-14):

| Checkpoint | *N* (vertices) |
| --- | ---: |
| `iteration_7000/point_cloud.ply` | 189 685 |
| `iteration_30000/point_cloud.ply` | 203 930 |
| `iteration_60000/point_cloud.ply` | **203 930** |

`load_gaussian_means_rgb(data/models/ficus_whitebg)`: `xyz` shape `(203930, 3)` float32.

Live `material_tags.pt` length **203 930** equals that *N*. Unique values and counts (`torch.unique`):

| ID | Count |
| --- | ---: |
| 1 pot | 32 476 |
| 2 trunk | **0** (absent from unique) |
| 3 leaves | 171 454 |
| 0 unlabeled | 0 |

Every Gaussian is labeled 1 or 3; none is trunk. Sum of counts = 203 930.

## 4. Raw `part_masks.npz` sums (rematerialize trunk)

Recompute on live arrays:

| Group | Positive count (`sum`) | Exclusive (no other group) |
| --- | ---: | ---: |
| pot | 11 633 | 10 513 |
| trunk | **569** | 16 |
| leaves | 43 267 | 41 594 |

| Pair | Intersection |
| --- | ---: |
| pot ∩ trunk | 0 |
| pot ∩ leaves | 1 120 |
| trunk ∩ leaves | 553 |
| pot ∩ trunk ∩ leaves | 0 |
| any group | 53 796 |
| none | 46 204 |

Raw trunk mask is **non-empty** (569). Rematerialize from this file therefore has a non-empty raw trunk mask to merge (and, under the spec survival rule, to restore if tag 2 is empty after lift).

Highest-IoU merge on these same arrays + live `chosen_iou.json` (arithmetic from the overlap table; leaves IoU 0.294 > trunk 0.265; pot IoU highest): unlabeled 46 204, pot 11 633, trunk **16**, leaves 42 147. That is the 100k histogram `merge_masks` would emit **before** survival. Current lifted tensor still has tag 2 = 0 (§3).

## 5. What backfill + rematerialize would consume

**Sample-id backfill (consume, not implement):** the live pair `data/outputs/partsam/sample_100k.npz` (`coords` `(100000, 3)` float32 as the hash input named in the effort map) and `data/outputs/partsam/clicks.json` (already `validate_clicks`-complete). Neither file currently holds a sample identity. Spec Stage 2: clicks JSON bound to this sample; missing id means no skip (effort map). This note does not name the field to write. Do not rebuild the 100k or re-click: the on-disk xyz and clicks are already this persist.

**Rematerialize (consume, not implement):** live `part_masks.npz` + `chosen_iou.json` + `sample_100k.npz` `coords` + Gaussian means from `load_gaussian_means_rgb` on the default ficus model path; overwrite `data/outputs/tags/material_tags.pt`. Raw trunk 569 is enough to know the raw trunk mask is non-empty. [`run_stage_lift`](../../../src/segmentation/partsam/infer.py) today always loads PartSAM weights and `predict_masks`, then merge + lift; it does not take a masks-already-on-disk path.

Secondary only (re-measured live files above): [Live-run occupancy vs trial](../../partsam-live-tag-fix/research/01-live-run-occupancy-vs-trial.md) reported the same mask sums, IoU scalars, tag histogram, and `(203930,)` tags on 2026-08-14; this recompute matches those live numbers.
