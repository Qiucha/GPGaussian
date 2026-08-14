# Automatic PartSAM prompts vs named material IDs

Sources retrieved 2026-08-14. Primary: Zhu et al., [arXiv:2509.21965](https://arxiv.org/abs/2509.21965) ([HTML](https://arxiv.org/html/2509.21965)); official repo [czvvd/PartSAM](https://github.com/czvvd/PartSAM) (vendored at `.scratch/partsam-ficus-trial/vendor/PartSAM`); owner on [#5](https://github.com/czvvd/PartSAM/issues/5). Trial: [CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md), [RESULT.md](../../partsam-ficus-trial/RESULT.md). Prior note re-checked: [PartSAM tagging gap](../../agent-orientation/research/02-partsam-tagging-gap.md). Not installed or run.

**Verdict:** No. Segment-Every-Part (SEP) and the only shipped auto script emit **class-agnostic instance IDs** on points/faces. They do not name pot / trunk / leaves. Mapping those IDs to materials is outside PartSAM. The ficus trial used **named 3D clicks** (geometry candidates + MLLM accept), not SEP.

## 1. What SEP emits

Paper **§3.4** (“Automatic Segmentation” / “Segment Every Part”): FPS-sample \(N_f\) points as independent prompts → \(3N_f\) candidate masks + predicted IoU → drop low-IoU → NMS on point-level IoU → **assign labels to mesh faces** from the surviving point masks. NMS threshold \(T\) is a **granularity** knob, not a name.

Paper **§4.2** evaluates this as **class-agnostic part segmentation**. Figure 7: “each segmented part is visualized with a distinct color.” No material vocabulary.

Paper **§3**: prompts are **3D click points**, positive and negative. No text prompt in the stated I/O.

Released code is the same pipeline, not a named-part API:

- README **Usage** is only `python evaluation/eval_everypart.py`.
- `evaluation/eval_everypart.py`: FPS `fps_point_number: 512` on the 100k coords (`configs/partsam.yaml`); `prompt_labels` all **1**; `predict_masks` in batches of 32; keep `iou_threshold: 0.65`; NMS `0.3`; sequential integer labels `0..k-1` in area order (`labels[sorted_masks[i]] = i`); vote onto **mesh faces**; `post_processing` colors faces from CSS4 palette (`utils/infer_utils.py`); write `results/{id}.ply`.
- `PartSAM/model/prompt_encoder.py` `PointEncoder`: **two** embeddings, `labels == 0` / `1` (neg / pos). No class id, no text token.

Owner ([#5](https://github.com/czvvd/PartSAM/issues/5#issuecomment-5200465800)): the released script is **auto-segmentation** via `predict_masks()` with **sampled positive** points, NMS, and post-processing. Interactive use is the same API with user pos/neg clicks. No other automatic prompt mode is shipped (GitHub issues 1–6: only #5 is interactive vs auto).

## 2. Path from those parts to semantic labels

Paper **A.2.8** (limitations), quote: PartSAM “cannot directly produce semantic labels for these masks, which are important for some downstream tasks.” Proposed future work is **new training data** with semantic labels, possibly via **interactive** user feedback on segmented parts — not an inference-time namer.

Paper **A.3** (3DCoMPaT++): GT there is **semantic-level**; they still score **automatic class-agnostic** masks by IoU against those names. That is eval matching to GT, not the model emitting “pot” / “trunk” / “leaves”.

Related-work **§2.2** text-driven methods (PartSLIP, Find3D) are **other** papers. PartSAM’s I/O remains clicks → binary / instance masks.

Repo: no semantic head, no CLIP/text encoder, no part-name table on the colored PLY. Tagging-gap note §1 / §3 holds on re-read: mapping parts → Material Tag Tensor is this repo’s seam, not PartSAM.

## 3. What the ficus trial used instead

Trial **did not** run `eval_everypart.py`. [CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md) lists that script under **Out of this pipeline**.

Instead: deterministic geometry+color bins on `ficus_100k.npz` propose on-cloud xyz for **named** groups pot / trunk / leaves; MLLM only **accept / swap / resample** from labeled markers on an annotated 3-view PNG; snap nearest neighbor; write `clicks.json`; then `predict_masks` **once per named group**. [RESULT.md](../../partsam-ficus-trial/RESULT.md): “three click groups (geometry + MLLM accept of P0) → `predict_masks`.” Names come from the **click groups**, not from SEP IDs.

## Implication for this effort

Automatic PartSAM prompts cannot replace per-scene named clicks (or an equivalent external namer) for tag IDs **1=pot / 2=trunk / 3=leaves**. Choosing how the generic recipe supplies those named clicks is ticket 05, not this note.
