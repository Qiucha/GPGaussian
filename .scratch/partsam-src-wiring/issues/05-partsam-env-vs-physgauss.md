# 05 - PartSAM conda env vs physgauss on the intended runner

Type: grilling
Status: resolved
Blocked by: none

## Question

How does the intended path invoke `predict_masks` relative to `physgauss` (the env `run_pipeline.sh` uses today) and the trial conda env `PartSAM`?

Cover: one env vs two; subprocess vs import; Stage 1 Poisson and Stage 3 lift vs inference; what `run_pipeline.sh` must `conda run`. Do not implement the `.sh` in this ticket.

## Answer

Keep **two** conda envs. Do not merge: `physgauss` is Python 3.10 / torch 2.7+cu118 / Warp / pymeshlab; `PartSAM` is Python 3.11 / torch 2.4.1+cu124 / trimesh / `predict_masks`. Do not `import` `partfield` or PartSAM from `physgauss`.

| Stage | Env | How |
| --- | --- | --- |
| 1 surface (Poisson + 100k sample + SH bake) | `physgauss` | `conda run -n physgauss python -m src.segmentation.partsam --stage surface`. Add `trimesh` to `physgauss` (not in that env today). |
| 2 clicks | `physgauss` | `conda run -n physgauss python -m src.segmentation.partsam --stage clicks` |
| 3 lift (`predict_masks` + merge + `material_tags.pt`) | `PartSAM` | `conda run -n PartSAM python -m src.segmentation.partsam --stage lift` |
| PhysGaussian MPM Solver | `physgauss` | unchanged `conda run -n physgauss python -m src.simulation.runner …` |

`run_pipeline.sh` is that sequence (skip-if-exists still per stage). One CLI invocation per env-role — not a single all-stages process. Docs for clone / `PARTSAM_ROOT` / weights / `trimesh` belong to [Clone, PARTSAM_ROOT, and weights docs](06-clone-env-weights-docs.md); this ticket does not edit the shell.

## Comments
