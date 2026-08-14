# 10 - How the human supplies three click groups

Type: grilling
Status: resolved
Blocked by: none

## Question

[PartSAM official inference path for three-click masks](01-partsam-inference-path.md) found **no official click UI**. Three binary masks require calling `PartSAM.predict_masks()` with 3D click coordinates on the normalized 100k cloud (positive/negative labels). `eval_everypart.py` cannot be used as-is.

How should the human in [Place three click groups on the ficus surface](05-place-click-groups.md) specify pot / trunk / leaves clicks?

A) A small **polyscope** (or similar) viewer the agent launches; human clicks; agent saves coords.
B) Human writes a **JSON** of world- or normalized-xyz clicks (agent provides a screenshot/preview of the cloud).
C) Something already on this machine.

Resolve with A/B/C plus whether negative clicks are required for the first trial. Findings: [01-partsam-inference-path.md](../research/01-partsam-inference-path.md).

## Answer

**B + positives first.** Human writes world-xyz JSON (100k sample before ValDataset bbox-normalize). Agent supplies orthographic PNG previews of that cloud and applies the stored transform before `predict_masks`. No viewer install.

Each of pot / trunk / leaves has **one or more** positives; negatives stay empty unless a later retry needs them. Template: [clicks.template.json](../clicks.template.json).

