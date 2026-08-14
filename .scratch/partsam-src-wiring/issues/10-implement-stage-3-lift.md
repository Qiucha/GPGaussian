# 10 - Implement Stage 3 masks, merge, and lift in src/

Type: task
Status: resolved
Blocked by: 03, 04, 05, 06, 07, 08

## Question

Implement Stage 3 in `src/`: `predict_masks` per named group via gitignored clone + `Czvvd/PartSAM` + FPS stand-in; persist three 100k masks and one chosen-mask predicted IoU scalar per group; merge highest IoU (smaller mask on ties); unlabeled 100k do not vote; NN onto every Gaussian; write `material_tags.pt` `(N,)` int32 1/2/3.

Clicks may already exist on disk (do not block on Stage 2). No Heuristic Primitive rewrite after lift. Inference env as in [PartSAM conda env vs physgauss on the intended runner](05-partsam-env-vs-physgauss.md).

## Answer

`src/segmentation/partsam/merge.py`: highest chosen-mask predicted IoU wins; smaller mask on ties; unlabeled 100k do not vote; NN onto every Gaussian; `material_tags.pt` `(N,)` int32 **1=pot / 2=trunk / 3=leaves**. Persist `part_masks.npz` + `chosen_iou.json` under `--output_dir`; solver tags default `data/outputs/tags/material_tags.pt`.

`src/segmentation/partsam/infer.py`: `--stage lift` in the `PartSAM` env (`get_partsam_root()`, FPS `install()`, `Czvvd/PartSAM` `model.safetensors`, `predict_masks` per group from on-disk `clicks.json`). No Heuristic Primitive rewrite. Skip tags only with `--reuse-tags`. Unittest: `tests/test_partsam_merge.py` (fake masks; no weights/GPU).

## Comments
