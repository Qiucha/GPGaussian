# PartSAM vs Phys4DGS tagging path

Sources retrieved 2026-08-14. Claims cite the paper, official repo, or this tree. Persisted by the parent wayfinder session after the research subagent completed investigation but could not write files (execution backend down).

## 1. What PartSAM takes and emits

**Paper:** Zhu et al., *PartSAM: A Scalable Promptable Part Segmentation Model Trained on Native 3D Data*, [arXiv:2509.21965](https://arxiv.org/abs/2509.21965) ([HTML](https://arxiv.org/html/2509.21965)). Project page: https://czvvd.github.io/PartSAMPage/ .

**Official code:** https://github.com/czvvd/PartSAM . Weights: `huggingface-cli download Czvvd/PartSAM --local-dir ./pretrained`.

### Input

Not a 3DGS model. Shape is a **point cloud** \(P_{in}\) with **3D coordinates, surface normals, and optional RGB** (\(d_{in}=9\)) (paper §3). Eval uniformly samples **\(N=100{,}000\)** surface points from meshes (`.glb` / `.ply` / `.obj`); untextured shapes get default gray (A.1.1; `utils/ValDataset.py`; `configs/partsam.yaml` `num_points: 100000`).

### Prompts

**3D click points**, positive and negative (paper §3). **No text prompt** in the stated I/O. Multi-round interaction concatenates previous mask logits (A.1.2).

### Outputs

- **Interactive:** binary per-point mask; three candidates + IoU; highest IoU selected (A.1.1).
- **Segment-Every-Part:** FPS prompts → candidate masks → drop low-IoU → NMS → labels on mesh faces (paper §3.4). Released eval writes a colored `.ply` (`evaluation/eval_everypart.py`).
- **Class-agnostic:** “cannot directly produce semantic labels for these masks” (A.2.8). Paper applications are part editing and amodal completion, not physics.

## 2. This repo’s Material Tag Tensor producers

A **Material Tag Tensor** is a 1D `(N,)` integer tensor on Gaussians (`CONTEXT.md`). The **PhysGaussian MPM Solver** derives per-particle Lamé params from it (`src/simulation/lame_params.py`, `src/simulation/runner.py`).

### Heuristic Primitive

Rules on 3D Gaussians (`xyz`, SH DC, scales) returning tags `(N,)` (`src/segmentation/heuristics.py`). Standalone rewriters of `material_tags.pt`: `color_heuristic.py`, `trunk_heuristic.py`, `tag_filter.py`, `vasedeck_heuristic.py`.

Thin Ficus trunk (`design_decisions.md`, verified in those scripts): LangSAM found ~10–100 trunk Gaussians; cylinder failed; SH `R>G and R>B` claimed 36,058 trunk Gaussians.

### Segmenter Agent

`src/llm/segmenter_agent.py` plans Heuristic Primitive chains from scene metadata. Digest export uses `SegmenterAgent(mock_llm=True)` (`scripts/export_pipeline_data.py`). This path **never calls LangSAM or FlashSplat**.

### LangSAM

`src/segmentation/langsam_segmenter.py`: 2D text + Grounding DINO + **SAM** (not SAM 2) → PNG masks. Missing install → empty masks. `scripts/run_pipeline.py` Step 2 projection is commented out; writes empty `material_tags.pt`. `src/segmentation/projection.py` is geometric 2D→3D vote (area order), **not** FlashSplat.

### FlashSplat

`src/segmentation/flashsplat.py` + `vendor/FlashSplat`: 2D masks → Gaussian labels via linear programming; semantic Z-priority; writes `material_tags.pt`. Default prompts `["pot", "trunk", "leaves"]`.

### Grounded SAM 2

Abandoned (`design_decisions.md`): Grounding DINO CUDA vs `PyTorch >= 2.3.1` / SAM 2. **No** Grounded SAM 2 module in `src/`.

### Solver ingest

`src/simulation/runner.py --tags_path` loads `material_tags.pt`; JSON `materials` maps tag IDs → `E`, `nu`, `density`; `MPM_Simulator_WARP`.

## 3. Gap PartSAM would fill vs would not

**Would fill:** native-3D promptable part decomposition without multi-view SAM lift — the family this repo’s LangSAM + FlashSplat / projection path belongs to (paper §1–2; `langsam_segmenter.py`, `flashsplat.py`). Automatic part sets (Segment-Every-Part) without a hand-authored Heuristic Primitive chain.

**Would not:** run MPM; replace the PhysGaussian MPM Solver; emit a Material Tag Tensor (outputs are class-agnostic part IDs on sampled points / mesh faces, not material IDs on Gaussians); assign `E`/`nu`/`density`; consume 3DGS as a first-class representation. Mapping parts → material IDs is outside PartSAM. Treating Gaussian means as \(P_{in}\) is **not specified** by the paper or their eval code.

## 4. Confusions to forbid

| Name | What it is | Do not say |
| --- | --- | --- |
| **LangSAM** | 2D text + SAM on images | Not PartSAM. Not SAM 2. Does not write a Material Tag Tensor by itself. |
| **SAM2 2D lift** | Abandoned Grounded SAM 2; FlashSplat TODO | Not PartSAM. PartSAM is trained against 2D-lift, not as a SAM2 lift. |
| **FlashSplat** | 2D-mask → 3D Gaussian labels (LP) | Not a part foundation model. Not native 3D segmentation. Not MPM. |
| **PartField** | Feature-field clustering; PartSAM’s frozen encoder / curation | Not PartSAM. Not in Phys4DGS `src/`. |

Also forbid: calling PartSAM a Segmenter Agent, calling its masks a Material Tag Tensor, or implying it replaces `MPM_Simulator_WARP`.

## 5. Practical constraints (stated only)

- Code + weights released: GitHub `czvvd/PartSAM`, HF `Czvvd/PartSAM`. README pins **PyTorch 2.4.1 + CUDA 12.4**.
- ~118M trainable params; automatic segmentation ~12s on one NVIDIA H20 (paper Table 5).
- Eval sample count 100,000; graph-cut optional and slow on large face counts (`configs/partsam.yaml`).
- License: PartSAM code **MIT**; `partfield/` NVIDIA **non-commercial research/education**; full inference pipeline must comply (`LICENSE.md`).
- No semantic labels (A.2.8).
- This repo’s Grounded SAM 2 attempt already collided with PyTorch ≥ 2.3.1 (`design_decisions.md`) — env history, not a PartSAM claim about Phys4DGS.
