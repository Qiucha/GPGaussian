# Map: Agent orientation pack for Phys4DGS

## Destination

A written agent orientation pack at `docs/agents/orientation.md` covering purpose, current state (pipeline, vendor, experiments), how to run what exists, sequenced next steps with PartSAM (arXiv 2509.21965) as the immediate experiment, and unranked potential work. Historical docs are disposed so they cannot trap later agents. `CONTEXT.md` stays a glossary.

## Notes

- Effort slug: `agent-orientation`
- Domain: Phys4DGS — heterogeneous MPM on 3DGS scenes; tags produce a Material Tag Tensor for the PhysGaussian MPM Solver.
- Skills every session should consult: `/research`, `/grilling`, `/domain-modeling`, `/writing-for-agents`
- This effort **writes** (overrides wayfinder default plan-only): the orientation pack, plus historical-doc disposition.
- Standing preferences:
  - Outline: Purpose → Pipeline as built → Current state → Vendor & experiments → How to run what exists → Next steps → Pointers.
  - PartSAM in the pack is why-it-is-next, the tagging gap, and what not to confuse it with. Integration design and a trial recipe are later efforts; research findings are linked, not swallowed.
  - `CONTEXT.md` is edited only if a term in the pack conflicts with the glossary. Do not add PartSAM to the glossary until it is in the pipeline. The 3DGS-vs-4DGS name trap lives in Purpose, not the glossary.
  - Write-scope: `docs/agents/orientation.md`. A single `AGENTS.md` context pointer is in scope so later agents can reach the pack. No root README.
  - Potential next steps: unranked, grouped by theme, with a pointer at leftover fog on [Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian](../llm-motion-physgaussian/map.md). That RFC is a parallel track; this pack does not supersede it.
  - Research findings live under `.scratch/agent-orientation/research/` (local-markdown tracker; not a git `research/` branch).
- Glossary terms to use: Heuristic Primitive, Segmenter Agent, Material Tag Tensor, PhysGaussian MPM Solver, Digest Dashboard, Dual-Mode Frame Player.

## Decisions so far

- [Archive or rewrite historical docs so they cannot trap agents](issues/03-historical-docs-disposition.md) — Move `Dev Plan.md`, `design_decisions.md`, `digest.md`, and `issues/` to `.scratch/agent-orientation/historical/` with stubs (`issues/README.md` only); banner `CHANGELOG.md` in place.
- [Current state of the Phys4DGS pipeline, vendor, and experiments](issues/01-repo-current-state.md) — 3DGS + Warp MPM over time (no 4DGS trainer); heuristics/mock agent/digest/Warp runner work; live LLM, LangSAM, `run_pipeline.py`, FVD/KVD stubbed. Findings in [research/01-repo-current-state.md](research/01-repo-current-state.md).
- [PartSAM as a Material Tag Tensor source](issues/02-partsam-tagging-gap.md) — Native-3D click-prompted parts on 100k-point clouds; not a Material Tag Tensor and not MPM. Findings in [research/02-partsam-tagging-gap.md](research/02-partsam-tagging-gap.md).
- [Write the agent orientation pack](issues/04-write-orientation-pack.md) — `docs/agents/orientation.md` plus an `AGENTS.md` Orientation pointer.
- [Apply the historical-docs disposition](issues/05-apply-historical-docs-disposition.md) — Historical files archived under `.scratch/agent-orientation/historical/` with stubs; `CHANGELOG.md` bannered.
- [PartSAM trial design (scene, I/O, success)](issues/06-partsam-trial-design.md) — Ficus; 100k-point surface from Gaussians; three clicks (pot/trunk/leaves) → `material_tags.pt`; pass = ingest + short MPM run.

## Not yet specified

- Whether a later effort should add a root README that only points at the pack.

## Out of scope

- Running or integrating PartSAM in this effort.
- Full PartSAM API/code-seam spec.
- Expanding `CONTEXT.md` with PartSAM or paper-only terms.
- Merging or replacing the LLM-motion RFC map.
- Yang-style 4D Gaussian fields; in-browser CUDA MPM.
