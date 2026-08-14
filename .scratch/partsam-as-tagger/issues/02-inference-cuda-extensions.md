# 02 - Which CUDA extensions PartSAM inference actually needs

Type: research
Status: resolved
Blocked by: none

## Question

On the **inference** path used for three-click `predict_masks` (not training), which of **torkit3d**, **apex**, and **pointops** are actually imported or required, and what did the ficus trial substitute?

Cover, from primary sources (PartSAM README, Python imports on the eval/`predict_masks` path, trial [ENV.md](../../partsam-ficus-trial/ENV.md), [torkit3d_stub.py](../../partsam-ficus-trial/torkit3d_stub.py), [PartSAM official inference path](../../partsam-ficus-trial/research/01-partsam-inference-path.md)):

1. README-required vs import-time vs unused on `predict_masks`.
2. What the trial stub replaces (FPS?) and whether `apex`/`pointops` appear on that path.
3. Whether a documented path can name the stub, or official inference is “compile these extensions.”

Write findings to `.scratch/partsam-as-tagger/research/02-inference-cuda-extensions.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** decide whether documenting the stub is acceptable (that is [May the documented inference path use the trial stubs](07-documented-inference-stubs.md)).

## Answer

On three-click `predict_masks`, only **torkit3d** is imported and used (encoder FPS + `batch_index_select`); the trial replaced it with a PyTorch stub. **apex** and **pointops** are README-required and used by `eval_everypart.py`, but do not appear on that driver. Official docs say compile all three; there is no upstream stub. Findings: [02-inference-cuda-extensions.md](../research/02-inference-cuda-extensions.md).
