# 11 - Write the PartSAM-as-tagger spec

Type: task
Status: resolved
Blocked by: 08, 09, 10

## Question

Write [spec.md](../spec.md): go/no-go at the top, then the seam (or leave-as-trial). Tag IDs **1=pot / 2=trunk / 3=leaves**. Generic recipe with ficus as the only evidence. Use `/writing-for-agents`. Do not wire `src/`. Do not edit `CONTEXT.md`.

## Answer

Wrote [spec.md](../spec.md): **YES** at the top; PartSAM the one intended producer; FlashSplat/LangSAM retired; Heuristic Primitives and Segmenter Agent unchanged-but-not-intended; three-stage seam (Poisson 100k → world-xyz clicks JSON → IoU merge + NN lift) to `material_tags.pt` `(N,)` int32 **1=pot / 2=trunk / 3=leaves**. No `src/` wiring. No `CONTEXT.md` edit.
