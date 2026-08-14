# Map: GitHub visitor README for the wired delta

## Destination

A rewritten root `README.md` a GitHub visitor can follow: short architecture (Material Tag Tensor → Lamé → PhysGaussian MPM Solver → rasterize), clone/install for PhysGaussian + PartSAM (conda `physgauss` + `PartSAM`), FlashSplat clone **optional**, `./scripts/run_pipeline.sh` as the intended run. Honest about a local 3DGS checkpoint and Stage 2 `clicks.json`. Optional `python -m src.llm.critique_loop` (live `critique` unimplemented). One link to `docs/agents/orientation.md`. No `git push`. `CONTEXT.md` unchanged. This map **writes** the README (and an orientation one-liner only if the pack would fight it).

## Notes

- Effort slug: `github-visitor-readme`
- Domain: Phys4DGS glossary in `CONTEXT.md`. Prior GitHub map: [GitHub-Ready Working Tree](../github-ready-working-tree/map.md). Wired tagging: [Wire PartSAM as Material Tag Tensor producer in src/](../partsam-src-wiring/map.md). Critique driver: [Wire Motion Critique Loop in src/](../mpm-critique-loop-wiring/map.md). Do not implement [Spec the live ficus PartSAM tagging fix](../partsam-live-tag-fix/map.md).
- Skills: `/research`; `/grilling` / `/domain-modeling` if a ticket reopens a decision; `/writing-for-agents` on the orientation pointer only.
- This effort **writes** `README.md` and, if needed, one orientation line (overrides plan-only). No remote, no push, no `setup_env.sh` rewrite, no `src/` change, no `CONTEXT.md` PartSAM term.
- Research notes: `.scratch/github-visitor-readme/research/`
- Standing:
  - Intended producer is PartSAM (`run_pipeline.sh`). One sentence: Heuristic Primitives / Segmenter Agent remain for digest/tests; FlashSplat source is kept, unhooked, clone optional.
  - Architecture uses glossary terms (Material Tag Tensor, PhysGaussian MPM Solver, Digest Dashboard). Do not add PartSAM or Motion Critique Loop to `CONTEXT.md`.
  - Install: document `physgauss` + `PartSAM` only. Omit `setup_env.sh` / `setup_phase2.sh` / `physgauss_v2` from intended bootstrap.
  - Honesty: local `--model_path` (checkpoints not in git); Stage 2 needs `clicks.json`; do not claim a currently-good live ficus tensor or a full wind campaign.
  - Critique: short optional subsection; live `translate` / `critique` still `NotImplementedError`.
  - README sections: intro + architecture; required clones (PhysGaussian, PartSAM + weights); two envs; how to run; optional FlashSplat; optional critique; Digest Dashboard; licenses/cite; pointer at orientation.
  - No paper dump from `Paper_Writing/`. No Git LFS / `data/` upload.

## Decisions so far

- [Intended clone, env, and run facts](issues/01-intended-clone-env-run-facts.md) — README must match wired `run_pipeline.sh`: required PhysGaussian `8339ed6` + PartSAM `b16d3e8`/HF weights, optional FlashSplat, envs `physgauss`+`PartSAM` (not `physgauss_v2`), `clicks.json` skip-if-exists, mock critique CLI. [research](research/01-intended-clone-env-run-facts.md).
- [Write the GitHub visitor README](issues/02-write-github-visitor-readme.md) — Root `README.md` rewritten to that story; `setup_env.sh` omitted; orientation pointer only; no `CONTEXT.md` / `src/` / push.
- [Orientation one-liner vs the new README](issues/03-orientation-one-liner-vs-readme.md) — Fought on clone paths / FlashSplat-in-tree; orientation Vendor block replaced with `src/upstream.py` + README pointer. Segmenter Agent and setup scripts did not fight.

## Not yet specified

- Whether Digest Dashboard needs more than the current “open `digest/index.html`” line once Warp frames exist (pipeline hygiene, not this page).

## Out of scope

- `git push` / creating a different remote ([GitHub-Ready Working Tree](../github-ready-working-tree/map.md) already has `origin`).
- Rewriting `setup_env.sh` / `setup_phase2.sh` (pipeline hygiene).
- Implementing live `MotionTranslator` or the live ficus PartSAM tagging fix.
- Making FlashSplat optional in `src/` (this map is README only).
- Second scene, overlap retune, eval metrics, retiring stale scripts.
- Expanding `CONTEXT.md`.
