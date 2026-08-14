# 03 - Provision PartSAM environment and weights

Type: task
Status: resolved
Blocked by: 01

## Question

Stand up the PartSAM env and weights as specified in [PartSAM official inference path for three-click masks](01-partsam-inference-path.md): conda pin, clone or path, `huggingface-cli download Czvvd/PartSAM` (or the documented equivalent). Record install location and any license acknowledgement in `.scratch/partsam-ficus-trial/`.

Done when a later ticket can invoke inference without rediscovering the env. Agent drives this. If a human must accept a license click-through, leave a one-line checklist for them.


## Answer

Clone at `.scratch/partsam-ficus-trial/vendor/PartSAM`. Weights at `vendor/PartSAM/pretrained/model.safetensors`. Conda env `PartSAM` (`/home/q/miniforge3/envs/PartSAM`), torch `2.4.1+cu124` with CUDA available. License: MIT + NVIDIA-noncommercial `partfield/` acknowledged in [ENV.md](../ENV.md).

Leftover: compile torkit3d, apex, and pointops (README §2) before `predict_masks` will import.
