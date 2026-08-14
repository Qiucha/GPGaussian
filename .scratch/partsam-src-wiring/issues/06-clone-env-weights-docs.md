# 06 - Clone, PARTSAM_ROOT, and weights docs

Type: task
Status: resolved
Blocked by: 05

## Question

Record how a new checkout gets a gitignored PartSAM clone, `PARTSAM_ROOT`, and Hugging Face `Czvvd/PartSAM` weights, without publishing `partfield/` or the 859MB file.

Do: README clone/env/weights lines (same shape as FlashSplat / `FLASHSPLAT_ROOT`); confirm `third_party/` already gitignores the clone; copy working facts from [ENV.md](../../partsam-ficus-trial/ENV.md) once [PartSAM conda env vs physgauss on the intended runner](05-partsam-env-vs-physgauss.md) is resolved. FPS stand-in stays in-repo (not this ticket’s code). No torkit3d/apex/pointops compile instructions as required.

## Answer

`.gitignore` already has `third_party/` (`git check-ignore` → `third_party/PartSAM`). No new ignore rule.

[README.md](../../../README.md): clone `https://github.com/czvvd/PartSAM.git` → `third_party/PartSAM`, pin **b16d3e8** (trial checkout), `huggingface-cli download Czvvd/PartSAM model.safetensors` into `pretrained/`. `export PARTSAM_ROOT`. Two-env lines: `trimesh` on `physgauss`; `PartSAM` env 3.11 / torch 2.4.1+cu124 / `torch-scatter`; FPS stand-in in this repo; weights ~859MB stay in the clone. FlashSplat clone paragraph kept. NVIDIA PartField named next to Inria.

`src/upstream.py` `get_partsam_root()`: `PARTSAM_ROOT` then `third_party/PartSAM` (requires a `partfield/` directory). Not on the simulation `sys.path`.

## Comments
