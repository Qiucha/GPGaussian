# PartSAM: three click masks on a 100k cloud

Primary sources (2026-08-14): [repo README](https://github.com/czvvd/PartSAM/blob/main/README.md), tree, `evaluation/eval_everypart.py`, `utils/ValDataset.py`, `PartSAM/model/pc_sam.py`, `PartSAM/model/prompt_encoder.py`, `configs/partsam.yaml`, [LICENSE.md](https://github.com/czvvd/PartSAM/blob/main/LICENSE.md), [HF `Czvvd/PartSAM`](https://huggingface.co/Czvvd/PartSAM), [arXiv HTML v3](https://arxiv.org/html/2509.21965v3), owner comments on issues [#5](https://github.com/czvvd/PartSAM/issues/5) and [#6](https://github.com/czvvd/PartSAM/issues/6). Not installed or run.

## Env pin

README: `conda create -n PartSAM python=3.11`; `torch==2.4.1` / `torchvision==0.19.1` / `torchaudio==2.4.1` from `cu124`; then lightning 2.2, trimesh, hydra, accelerate, `torchdata==0.8.0`, `torch-scatter` for `torch-2.4.1+cu124`, vtk, etc.

Also (README §2): **torkit3d** and **apex** via [Point-SAM](https://github.com/zyc00/Point-SAM); **pointops** via [SAMPart3D](https://github.com/Pointcept/SAMPart3D). `eval_everypart.py` and `prompt_encoder.py` import both. No click UI; `polyscope` is a pip dep only.

## Weights

`huggingface-cli download Czvvd/PartSAM --local-dir ./pretrained`. HF siblings: `.gitattributes`, **`model.safetensors`** (~225M F32 params). Config: `eval_params.ckpt_path: ./pretrained/model.safetensors`. Hub `gated: false`; README still runs `huggingface-cli login`. No model-card README/license on the Hub.

## Click UI vs `eval_everypart` only

**No notebook, demo, or 3D click UI** in the repo tree (only `evaluation/eval_everypart.py`, `train.py`, `scripts/curate_partfield_labels.py`).

Owner ([#5](https://github.com/czvvd/PartSAM/issues/5#issuecomment-5200465800)): interactive segmentation is **`model.predict_masks()`** with multiple **positive and negative** point prompts; the released script is auto-segmentation using that API plus sampled positives, NMS, and post-processing. Manual-prompt example is not shipped.

`eval_everypart.py` does **not** take user clicks: FPS `fps_point_number: 512` on the 100k coords, `prompt_labels` all **1**, `predict_masks` in batches of 32, keep `iou_threshold: 0.65`, NMS `0.3`, vote labels onto **mesh faces**, write `results/{id}.ply`. That is paper §3.4 “Segment Every Part,” not three named parts.

**For three binary masks from three 3D clicks:** load the same Hydra model + safetensors; **do not** run `eval_everypart` as-is. Call `predict_masks` once per part (or batch B=3) with `prompt_coords` `[B, Np, 3]` on the **normalized** cloud and `prompt_labels` 1=pos / 0=neg (`PointEncoder`). Default `multimask_output=True` → 3 candidates + IoU; pick `argmax` IoU (paper decoder; eval uses `masks>0`). Optional later rounds: pass previous logits as `prompt_masks` (training `forward` / paper A.1.2). Clicks must be in the **same** `[-1,1]` frame as `coords` (`PositionEmbeddingRandom` rejects out-of-range).

`predict_masks` lists `point_to_face` / `vertices` / `faces` but **does not use them**; they exist for the mesh eval path.

## I/O

**Official eval in:** meshes `.glb` / `.ply` / `.obj` under `dataset.root_dir` (`./data_eval`). `ValDataset` fits bbox to ~`[-0.9,0.9]`, samples **100000** surface points (`num_points`; paper A.1), colors (else gray 192), face normals, `point_to_face`. `collate_fn_eval` then `prep_points_train(..., eval=True)` (center/normalize/color). Config `num_points: 100000` is **not** passed into `ValDataset(...)` in the script; the class default is still 100k.

**Official eval out:** colored **mesh** PLY (`trimesh.export`), not `(N,)` bool tensors. Helpers: `visualize_mask` / `save_ply` ASCII xyz+uchar RGB.

**Raw 100k xyz+normal+RGB (no mesh):** no official loader. Feed tensors through the same normalize stack, then `predict_masks`. Untextured: gray (paper A.1 / ValDataset).

Paper encoder uses triplane **512**; released `configs/model/PartSAM.yaml` uses **128** + 2000 patches — pin the YAML to the weights.

## License (research trial)

`LICENSE.md`: original PartSAM **MIT**; `partfield/` from NVIDIA PartField is **NVIDIA License, non-commercial research/education only**. Inference imports that encoder (`pc_sam.py` → `sample_triplane_feat`). Owner ([#6](https://github.com/czvvd/PartSAM/issues/6#issuecomment-5200447202)): full pipeline must follow NVIDIA terms. Fine for a non-commercial trial; not a commercial-MIT stack.
