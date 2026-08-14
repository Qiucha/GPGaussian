# 11 - run_pipeline.sh PartSAM to solver

Type: task
Status: resolved
Blocked by: 10

## Question

Rewrite `scripts/run_pipeline.sh` so the intended path is PartSAM (or reuse existing `material_tags.pt`) → PhysGaussian MPM Solver. Stop starting at FlashSplat. Do not chain `color_heuristic` as a rewrite. Leave `src/segmentation/flashsplat.py` in the tree, uncalled by this runner.

## Answer

`scripts/run_pipeline.sh` is PartSAM → PhysGaussian MPM Solver. If `data/outputs/tags/material_tags.pt` exists, tagging is skipped (`--reuse-tags` equivalent). Otherwise four `conda run`s: `physgauss` `--stage surface`, `physgauss` `--stage clicks`, `PartSAM` `--stage lift`, then `physgauss` `src.simulation.runner`. Default `PARTSAM_ROOT` is `third_party/PartSAM`. FlashSplat and `color_heuristic` are not invoked; `src/segmentation/flashsplat.py` remains in the tree.

## Comments
