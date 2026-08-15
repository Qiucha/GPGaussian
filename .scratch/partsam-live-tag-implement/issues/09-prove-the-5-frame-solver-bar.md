# 09 - Prove the 5-frame solver bar

Type: task
Status: resolved
Blocked by: 06, 07, 08

## Question

Produce a live ficus Material Tag Tensor that meets the spec bar, then run the PhysGaussian MPM Solver with `frame_num` **5**: exit 0, finite positions, no CUDA 700. Record occupancy (every prompted ID count > 0; *N* matches).

Do not run 125 frames. Do not edit `configs/ficus.json`. Do not claim a currently-good wind campaign.

## Answer

Rematerialized live ficus `material_tags.pt` from persisted masks + IoU (no `predict_masks`). Occupancy: length **203 930** = checkpoint *N*; prompted IDs **1 / 2 / 3** counts **32 476 / 2 509 / 168 945** (all > 0). Survival restored trunk; the live-mask empty-ID fog did not happen.

One-off PhysGaussian MPM Solver: `python -m src.simulation.runner --config configs/ficus.json --frame_num 5 --tags_path data/outputs/tags/material_tags.pt` (plus `--output_ply --render_img`). Exit 0. Warp `cuda:0`. 171 553 particles after opacity filter. Five frames ~59 s. No CUDA 700. Ply positions finite, absmax 1.50 → 1.47, `exploded` false. `configs/ficus.json` still `frame_num` 125. Not a 125-frame wind campaign.

Log: [mpm_5frame.log](../mpm_5frame.log). Check: [mpm_5frame_check.json](../mpm_5frame_check.json). Ply/frames: [mpm_5frame/](../mpm_5frame/).

## Comments
