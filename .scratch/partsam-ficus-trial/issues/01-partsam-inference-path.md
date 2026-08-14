# 01 - PartSAM official inference path for three-click masks

Type: research
Status: resolved
Blocked by: none

## Question

From PartSAM primary sources (https://github.com/czvvd/PartSAM, README, eval scripts, Hugging Face `Czvvd/PartSAM`), what is the **actual** way to obtain three binary masks from **positive/negative 3D clicks** on a 100k-point cloud?

Cover: conda/PyTorch/CUDA pin, weight download, the script or notebook that accepts click prompts (vs `eval_everypart.py` only), input file format, output mask format, license constraints that apply to a research trial.

Write a **short** findings file (aim < 120 lines) to `.scratch/partsam-ficus-trial/research/01-partsam-inference-path.md`. Then resolve this ticket with a gist + pointer. Do not install or run PartSAM.

## Answer

No click UI. Three binary masks come from `PartSAM.predict_masks()` with three 3D clicks (label 1/0) on a normalized 100k xyz+normal+RGB cloud, picking the best of three IoU candidates per prompt. `eval_everypart.py` is FPS auto-decompose → colored mesh PLY only. Env: py3.11, torch 2.4.1+cu124, plus torkit3d/apex/pointops; weights `Czvvd/PartSAM` → `./pretrained/model.safetensors`. MIT code + NVIDIA-noncommercial `partfield/` on the inference path.

Findings: [.scratch/partsam-ficus-trial/research/01-partsam-inference-path.md](../research/01-partsam-inference-path.md)
