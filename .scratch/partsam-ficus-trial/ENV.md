# PartSAM trial environment

Non-commercial research trial. PartSAM original code is MIT; inference uses `partfield/` under the NVIDIA PartField license (research/education only). See `vendor/PartSAM/LICENSE.md`.

## Locations

- Clone: `.scratch/partsam-ficus-trial/vendor/PartSAM` (https://github.com/czvvd/PartSAM)
- Weights: `.scratch/partsam-ficus-trial/vendor/PartSAM/pretrained/model.safetensors` (Hugging Face `Czvvd/PartSAM`, ~859MB)
- Conda env: `PartSAM` at `/home/q/miniforge3/envs/PartSAM` (Python 3.11.15)
- Activate: `conda activate PartSAM`
- Smoke: `python -c "import torch; print(torch.__version__, torch.cuda.is_available())"` → `2.4.1+cu124 True`

Config checkpoint path: `eval_params.ckpt_path: ./pretrained/model.safetensors` (run from the clone root).

## Installed (this ticket)

PyTorch 2.4.1+cu124, torchvision 0.19.1, torchaudio 2.4.1, lightning 2.2, trimesh, hydra-core, omegaconf, safetensors, accelerate, einops, plyfile, and matching NVIDIA cu12 wheels (including `nvidia-cudnn-cu12==9.1.0.70` via PyPI, not the cu124 wheel index).

## Added for `predict_masks` ([Place three click groups on the ficus surface](issues/05-place-click-groups.md))

- `torch-scatter==2.1.2+pt24cu124` (PyG cu124 wheel)
- `loguru`, `matplotlib`, `yacs`, `h5py`, `scikit-image`
- **torkit3d** not compiled: PyTorch stub [torkit3d_stub.py](torkit3d_stub.py) (deterministic FPS from index 0)
- **apex** / **pointops** not compiled and not imported on the `predict_masks` path (eval-only `FusedLayerNorm` / FPS)

```bash
conda activate PartSAM
python .scratch/partsam-ficus-trial/run_predict_clicks.py
```
