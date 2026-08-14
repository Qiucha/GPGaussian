# 05 - Place three click groups on the ficus surface

Type: task
Status: resolved
Blocked by: 03, 04, 10, 11

## Question

Run the click pipeline in [CLICK_PIPELINE.md](../CLICK_PIPELINE.md): geometric candidates on the 100k cloud from [Build the ficus 100k-point surface](04-build-ficus-surface.md), MLLM accept/swap on an annotated preview, snap to nearest sample, write `clicks.json` (contract from [How the human supplies three click groups](10-click-capture-method.md)). Then `predict_masks` for pot / trunk / leaves.

Human only if the MLLM cannot accept candidates after two annotated rounds. Do not invent free-form xyz.

Save `clicks.json` and three raw binary masks under `.scratch/partsam-ficus-trial/`.

Done when three masks exist on disk, one per material.

## Answer

Round-1 primaries in [clicks.json](../clicks.json) (P0 pot / trunk / leaves). `predict_masks` via [run_predict_clicks.py](../run_predict_clicks.py) (torkit3d stub, no apex/pointops). No empty / covers-most retry.

Masks on the 100k sample: [mask_pot.npy](../mask_pot.npy) 11 842, [mask_trunk.npy](../mask_trunk.npy) 26 722, [mask_leaves.npy](../mask_leaves.npy) 42 794; also [part_masks.npz](../part_masks.npz). Preview [ficus_100k_part_masks.png](../ficus_100k_part_masks.png): pot at the base, trunk mid-stem, leaves canopy. Trunk∩leaves = 23 038 (priority merge in [Merge masks and lift to Material Tag Tensor](06-merge-and-lift-tags.md) will give those points to trunk). Counts: [mask_stats.json](../mask_stats.json).

## Comments

- Unclaimed when click placement moved from human JSON to the MLLM pipeline ([LLM/MLLM pipeline for three click groups](11-mllm-click-pipeline.md)).
- Geometry + MLLM round 1: accepted primaries P0 (pot bottom, trunk mid-stem, leaves canopy). Wrote [clicks.json](../clicks.json), [click_candidates.json](../click_candidates.json), [ficus_100k_click_candidates.png](../ficus_100k_click_candidates.png). Runner [run_predict_clicks.py](../run_predict_clicks.py) (PyTorch FPS stub, no apex/pointops) not yet executed — masks still missing.
- Installed `torch-scatter` + `loguru` into conda `PartSAM`; FPS stub starts at index 0. Preview PNG needed matplotlib after the first successful mask write.
