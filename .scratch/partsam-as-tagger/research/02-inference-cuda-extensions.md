# CUDA extensions on three-click `predict_masks`

Primary sources (2026-08-14): vendor clone `.scratch/partsam-ficus-trial/vendor/PartSAM` (`README.md`, `evaluation/eval_everypart.py`, `utils/infer_utils.py`, `PartSAM/model/{pc_sam,pc_encoder,prompt_encoder,common,build}.py`, `PartSAM/utils/torch_utils.py`, `configs/model/PartSAM.yaml`, `partfield/`), trial `ENV.md`, `torkit3d_stub.py`, `run_predict_clicks.py`, `RESULT.md`. Re-checked [ficus research 01](../../partsam-ficus-trial/research/01-partsam-inference-path.md); do not copy its “import both” line (see below).

Two drivers call `PartSAM.predict_masks`. Hydra `_target_` is `PartSAM.model.pc_sam.PartSAM` (`configs/model/PartSAM.yaml`). Official Usage is `python evaluation/eval_everypart.py` (`README.md`). The ficus three-click driver is `run_predict_clicks.py` (same instantiate; no `eval_everypart`).

## README vs import-time vs `predict_masks`

README Installation §2 lists **torkit3d** and **apex** (via Point-SAM) and **pointops** (via SAMPart3D) as required third-party installs. It does not split train vs eval vs `predict_masks`.

| Package | README | Import-time on hydra `cfg.model` | Runtime in `predict_masks` | `eval_everypart.py` extra |
| --- | --- | --- | --- | --- |
| **torkit3d** | required | yes | yes (FPS + gather) | same (via model) |
| **apex** | required | no (on this target) | no | yes (`FusedLayerNorm`) |
| **pointops** | required | no | no | yes (prompt FPS + face kNN) |

**torkit3d.** `common.py` top-level-imports `batch_index_select`, `sample_farthest_points`, `chamfer_distance`. That module is imported by `pc_sam.py`, `pc_encoder.py`, `prompt_encoder.py`, `mask_decoder.py`. `prompt_encoder.py` also `from torkit3d.nn.functional import batch_index_select` (unused in that file). Instantiating the YAML model therefore imports torkit3d before any forward.

Runtime: `PatchEmbed.forward` → `KNNGrouper` (`pc_encoder.py`; YAML `patch_embed` is `PatchEmbed`, `num_patches: 2000`). `KNNGrouper.forward` default `use_fps=True` calls `sample_farthest_points` then `batch_index_select` (`common.py`). `predict_masks` always runs `self.pc_encoder(...)` on first call (`pc_sam.py`). Neighbor search in `knn_points` is `torch.cdist` / `topk`, not torkit3d. `chamfer_distance` is only used in training prompt helpers (`_minimum_squared_distances`, `sample_*_from_border`, `sample_PC`); `pc_sam.forward` calls `sample_triplets` / `sample_interaction_prompts`; `predict_masks` does not. The symbol is still imported at load.

**apex.** `build.py` does `from apex.normalization import FusedLayerNorm` inside `build_sam`. Nothing in the vendor tree imports `build.py` / `build_sam`. Hydra does not use it. `torch_utils.replace_with_fused_layernorm` lazy-imports `apex.normalization.FusedLayerNorm`. `eval_everypart.py` imports that helper and `model.apply(replace_with_fused_layernorm)` after instantiate. `run_predict_clicks.py` does neither. `partfield/` has no `apex` / `torkit3d` / `pointops` imports.

**pointops.** Only `eval_everypart.py` (module import; `pointops.farthest_point_sampling` for `fps_point_number: 512` auto-prompts; `pointops.knn_query` to fill unlabeled faces) and `utils/infer_utils.py` (`import pointops` with no later `pointops.` use). Model files under `PartSAM/model/` do not import it. Three-click `run_predict_clicks.py` does not import it; clicks come from `clicks.json`.

Correction to ficus research 01: `eval_everypart.py` does **not** import torkit3d or apex directly; it imports **pointops** and **torch_utils** (apex on `apply`). `prompt_encoder.py` imports **torkit3d** only.

## What the trial stub replaces

`ENV.md`: torkit3d not compiled; PyTorch stub `torkit3d_stub.py` (deterministic FPS from index 0); apex / pointops not compiled and not imported on the `predict_masks` path.

`torkit3d_stub.py` installs `sys.modules` for `torkit3d.nn.functional.batch_index_select`, `torkit3d.ops.sample_farthest_points.sample_farthest_points` (iterative FPS, first seed index 0), and `torkit3d.ops.chamfer_distance.chamfer_distance` (`NotImplementedError` if called). Module docstring: stub so PartSAM can run without compiling apex/torkit3d.

`run_predict_clicks.py` docstring and body: `import torkit3d_stub; torkit3d_stub._install()` **before** hydra instantiate / `predict_masks`. `RESULT.md`: trial passed with that stub; “apex/pointops were not compiled (`predict_masks` does not import them).”

So the stub replaces **encoder FPS + `batch_index_select`** (needed). It also fake-provides chamfer (import-only on this path). It does not replace apex or pointops; those packages are absent from this driver.

## Official docs vs stub (facts only)

Official install is “compile these extensions” (`README.md` §2). Official Usage names only `eval_everypart.py`, which import-uses **pointops** and apply-uses **apex**, and still needs **torkit3d** because it instantiates the same YAML model.

There is no stub in `vendor/PartSAM`. `torkit3d_stub.py` exists only under `.scratch/partsam-ficus-trial/`. A write-up of official inference therefore names compiling torkit3d, apex, and pointops. A write-up of the trial three-click driver names that local stub for torkit3d only. Whether a lasting documented path may name the stub is out of scope ([ticket 07](../issues/07-documented-inference-stubs.md)).
