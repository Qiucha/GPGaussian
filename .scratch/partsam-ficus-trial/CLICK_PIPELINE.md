# Click pipeline (ficus trial)

Fills [clicks.template.json](clicks.template.json) for [Place three click groups on the ficus surface](issues/05-place-click-groups.md). I/O contract from [How the human supplies three click groups](issues/10-click-capture-method.md) is unchanged: **world xyz**, **one or more positives** per pot / trunk / leaves, **negatives empty** until a retry.

Do **not** ask a VLM to read 3D coordinates off a 2D scatter. Orthographic views are ambiguous; invented numbers miss the cloud.

## Roles

| Step | Actor |
| --- | --- |
| Candidate xyz | Deterministic geometry + color on `ficus_100k.npz` |
| Accept / reject / “sample again” | MLLM (this Cursor agent with vision on an annotated preview) |
| Snap onto the 100k sample | Nearest neighbor in `coords` |
| Write `clicks.json` | Agent |
| Human | Only if the MLLM cannot accept any candidate after two annotated rounds |

## 1. Geometric candidates

From `ficus_100k.npz` (`coords`, `colors` uint8):

- **Pot:** low \(z\) and low luminance (dark ceramic blob under the stem).
- **Leaves:** high \(z\) and green-dominant RGB (canopy).
- **Trunk:** mid \(z\), small \(xy\) radius around the stem axis (median \(xy\) of mid-height points), not in the pot or canopy color bins.

For each group, take the **centroid of that bin**, then **K nearest sample points** (K=5) as the candidate set. One primary = the point closest to the centroid.

## 2. Annotated preview

Draw the three primary candidates (and optional extras) on copies of the existing xy / xz / yz preview: labeled markers, world xyz in the legend. Path: `ficus_100k_click_candidates.png`.

## 3. MLLM pass

The vision model sees that PNG plus a one-line bbox. It may only:

- **accept** the three primaries, or
- **swap** a primary for another labeled extra in the same group, or
- **reject a group** and ask geometry to resample (e.g. higher \(z\) for leaves).

It must not emit free-form xyz.

## 4. Snap and write

Each accepted point → `argmin ‖p − coords‖`. Write `.scratch/partsam-ficus-trial/clicks.json` (`frame: world`).

## 5. Into masks (ticket 05)

ValDataset bbox-normalize those xyz with the 100k cloud; `predict_masks` per group; pick argmax IoU. If a mask is empty or covers most of the cloud, **retry** with one extra positive from that group’s leftover candidates, then one negative on another part (ticket 10 retry rule).

## Out of this pipeline

- A separate hosted VLM API.
- Human-drawn polygons.
- Using `eval_everypart.py` instead of three named clicks.
