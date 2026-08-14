# 03 - Can automatic PartSAM prompts replace per-scene clicks for material IDs

Type: research
Status: resolved
Blocked by: none

## Question

Can Segment-Every-Part (or any other **automatic** prompt PartSAM ships) yield parts that map to **named materials** (pot / trunk / leaves) without a human or MLLM placing per-scene 3D clicks?

Cover, from primary sources (paper §3.4 and A.2.8, `evaluation/eval_everypart.py`, owner comments, [PartSAM tagging gap](../../agent-orientation/research/02-partsam-tagging-gap.md), trial [CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md)):

1. What SEP actually emits (class-agnostic parts on points/faces, not material names).
2. Whether the paper or repo describes any path from those parts to semantic labels.
3. What the trial used instead (geometry candidates + MLLM accept/swap).

Write findings to `.scratch/partsam-as-tagger/research/03-automatic-prompts-vs-clicks.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** pick the generic click path (that is [Click path for the generic PartSAM recipe](05-click-path-generic-recipe.md)).

## Answer

No: SEP (and the only shipped auto script) emit class-agnostic instance IDs on points/faces, not pot/trunk/leaves; paper A.2.8 says it cannot produce semantic labels. The ficus trial used geometry candidates + MLLM accept, not `eval_everypart`. Findings: [03-automatic-prompts-vs-clicks.md](../research/03-automatic-prompts-vs-clicks.md).
