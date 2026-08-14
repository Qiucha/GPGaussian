# 07 - FPS stand-in in src/

Type: task
Status: resolved
Blocked by: 03

## Question

Put this repo’s supported three-click FPS stand-in in `src/` at the path chosen in [Persist filenames and src/segmentation module tree](03-filenames-and-module-tree.md).

Contract: deterministic PyTorch FPS; first seed index 0; trial source [torkit3d_stub.py](../../partsam-ficus-trial/torkit3d_stub.py). Compile neither torkit3d nor apex/pointops. Do not call it PartSAM-official.

## Answer

In-package stand-in: [`src/segmentation/partsam/fps.py`](../../../src/segmentation/partsam/fps.py) (`sample_farthest_points` first seed index 0; `install()` registers `torkit3d` for later `predict_masks`). Not PartSAM-official. Unittest: [`tests/test_partsam_fps.py`](../../../tests/test_partsam_fps.py).

## Comments
