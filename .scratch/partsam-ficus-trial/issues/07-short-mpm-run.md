# 07 - Short PhysGaussian MPM Solver run

Type: task
Status: resolved
Blocked by: 06

## Question

Run `src.simulation.runner` with `configs/ficus.json`, `--tags_path` pointing at the trial `material_tags.pt`, `frame_num` **5–10**. Log whether tags loaded and whether the run exploded. Artifacts/logs under `.scratch/partsam-ficus-trial/`.

Done when a log exists that a later ticket can score against the pass bar (load + no immediate explosion).

## Answer

Tags loaded: `material_tags.pt` `(203930,)` int32, counts 1/2/3 = 30 339 / 79 053 / 94 538. Runner `python -m src.simulation.runner` with [ficus_short.json](../ficus_short.json) (`configs/ficus.json` + `frame_num` 5), `--tags_path` the trial tensor. Exit 0. Opacity filter → 171 553 particles. Five frames in ~59 s, Warp on CUDA.

Did not explode: ply positions finite, bbox stayed ~[0.5, 1.5] (absmax 1.50 → 1.48). Frames [mpm_short/0000.png](../mpm_short/0000.png)–[0004.png](../mpm_short/0004.png) still show a coherent ficus. Log: [mpm_short.log](../mpm_short.log). Check: [mpm_short_check.json](../mpm_short_check.json).
