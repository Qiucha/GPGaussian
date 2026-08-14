# 01 - Current state of the Phys4DGS pipeline, vendor, and experiments

Type: research
Status: resolved
Blocked by: none

## Question

What is true of this repo *as built*, citing primary sources (source, configs, tests, experiment folders — not `Dev Plan.md` or the paper draft as authority)?

Cover, with file paths:

1. **Purpose in code** — what the pipeline actually does (3DGS particles + MPM over time vs any 4DGS trainer).
2. **Working pieces** vs **stubs / broken entry points** (Segmenter Agent, live LLM / MotionTranslator, eval metrics, `scripts/run_pipeline.py`, LangSAM, FlashSplat, Warp MPM, Digest Dashboard).
3. **Vendor role** — `vendor/gaussian-splatting` and `vendor/FlashSplat`: load-bearing vs unused.
4. **Experiments** — what `data/experiments` and `digest/` actually contain and what they evidence.
5. **How to run what exists** — commands/scripts that work today (not a full environment cookbook).
6. **Candidate potential next steps** after PartSAM, grouped by theme (tagging, live LLM, eval, pipeline hygiene), including leftovers pointed at from the LLM-motion map — facts only, no ranking.

Write findings to `.scratch/agent-orientation/research/01-repo-current-state.md`. Every claim needs a source path. Then resolve this ticket with a short gist and a pointer at that file.

## Answer

As built, Phys4DGS loads trained 3DGS checkpoints, assigns a Material Tag Tensor, and steps particles with the PhysGaussian MPM Solver (Warp), then re-rasterizes. There is no 4DGS trainer. Heuristic tagging, mock Segmenter Agent, digest JSON, mock motion translation, and the Warp runner exist; live LLM, LangSAM, `scripts/run_pipeline.py`, FVD/KVD, and experiment videos are stubbed or absent.

Findings: [01-repo-current-state.md](../research/01-repo-current-state.md).
