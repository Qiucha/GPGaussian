# 04 - Test contract for the PartSAM seam without publishing weights

Type: grilling
Status: resolved
Blocked by: none

## Question

What tests must this map add, given weights and `partfield/` are not in git and `predict_masks` needs the PartSAM env/GPU?

Cover: unittest vs local integration; merge/lift/IoU with fake masks; JSON schema; Stage 1 persist shape; whether CI may skip inference; what is explicitly not a test in this map.

## Answer

Always-on `python -m unittest` only. Tests never need the PartSAM clone, Hugging Face weights, `partfield/`, or a GPU. No opt-in `predict_masks` unittest and no GPU/CI job in this map. Live inference is the local ficus `run_pipeline.sh` path after clone/env/weights exist.

This map adds unittests for:

- **Merge / lift / IoU** on synthetic 100k + overlapping fake masks + fake per-group IoU scalars: highest chosen-mask predicted IoU wins; smaller mask on ties; unlabeled 100k do not vote; NN onto every Gaussian; `(N,)` int32 IDs **1=pot / 2=trunk / 3=leaves**.
- **Clicks JSON**: spec shape (required keys; reject empty/partial groups); skip-if-exists only when every group has ≥1 positive; geometry bins on a tiny synthetic cloud. No MLLM/VLM in Python.
- **Stage 1 persist**: `sample_100k.npz` keys/dtypes/shapes (`coords`, `normals`, `colors` uint8, `point_to_face`) from a fixture writer. Do not run Screened Poisson in default unittest.
- **FPS stand-in**: deterministic on a small tensor; first seed index 0; no torkit3d compile.

Explicitly not a test in this map: live `predict_masks`, downloading weights, MLLM accept/swap, ball pivoting, a second scene, FlashSplat/LangSAM regression, full-length MPM, Digest Dashboard, overlap retune, a GPU CI workflow. If CI appears later, it runs only these always-on unittests.

## Comments
