# 04 - Write the agent orientation pack

Type: task
Status: resolved
Blocked by: 01, 02, 03

## Question

Write `docs/agents/orientation.md` for later agents, using `/writing-for-agents`. Also add **one** context pointer in `AGENTS.md` so agents load the pack when they need purpose, current state, or next steps.

Required sections (settled outline):

1. Purpose — heterogeneous MPM on 3DGS (time-varying particles, not Yang-style 4DGS)
2. Pipeline as built — Gaussians → tags → per-particle Lamé → PhysGaussian MPM Solver → render / Digest Dashboard
3. Current state — working vs stubbed, from [Current state of the Phys4DGS pipeline, vendor, and experiments](01-repo-current-state.md)
4. Vendor & experiments
5. How to run what exists
6. Next steps — PartSAM as immediate (why, tagging gap, what not to confuse it with) from [PartSAM as a Material Tag Tensor source](02-partsam-tagging-gap.md); then unranked potential work by theme; pointer at the LLM-motion map
7. Pointers — `CONTEXT.md`, LLM-motion map, historical docs per [Archive or rewrite historical docs so they cannot trap agents](03-historical-docs-disposition.md)

Link research files; do not paste them. Do not edit `CONTEXT.md` unless a term conflicts. Do not add a root README. Do not implement PartSAM.

## Answer

Wrote `docs/agents/orientation.md` (settled outline) and one `AGENTS.md` **Orientation** pointer. `CONTEXT.md` unchanged. Research files linked, not pasted. Graduated PartSAM trial design into [PartSAM trial design (scene, I/O, success)](06-partsam-trial-design.md).
