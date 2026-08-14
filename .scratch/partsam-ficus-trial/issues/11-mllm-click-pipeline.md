# 11 - LLM/MLLM pipeline for three click groups

Type: grilling
Status: resolved
Blocked by: 04, 10

## Question

[Place three click groups on the ficus surface](05-place-click-groups.md) was HITL: a human fills world-xyz JSON. The human now wants **LLMs, with visual / MLLM help**, to propose those clicks instead of picking xyz by hand.

What is the pipeline for this trial (not a production tagger)? Who proposes 3D points, how vision is used, how that stays compatible with [How the human supplies three click groups](10-click-capture-method.md) (`clicks.json`, world frame, positives first), and when a human still steps in.

## Answer

Geometry on `ficus_100k.npz` proposes on-cloud candidates (pot / trunk / leaves). MLLM only **accept / swap / resample** from labeled markers on an annotated 3-view PNG — no free-form xyz. Snap nearest neighbor; write `clicks.json` (ticket 10 contract). Human only after two failed annotated rounds. Spec: [CLICK_PIPELINE.md](../CLICK_PIPELINE.md).
