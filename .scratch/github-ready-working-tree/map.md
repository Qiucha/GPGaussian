# Map: GitHub-Ready Working Tree for Phys4DGS

## Destination

A GitHub-ready working tree: Phys4DGS-owned code only, third-party clones consumed as documented upstream pointers (not dumped in-tree), oversized/local artifacts ignored, history rewritten to a fresh root commit. Creating the GitHub remote and pushing is not part of this destination.

## Notes

- Effort slug: `github-ready-working-tree`
- Key skills: `/research`, `/grilling`, `/domain-modeling`
- Standing preferences:
  - No PhysGaussian, gaussian-splatting, or FlashSplat source trees in the published repo; README (or equivalent) tells people to clone those upstreams; keep only the Phys4DGS delta.
  - Do not create a remote or push until the human explicitly asks.
  - Fresh root commit so bytecode and any later accidents never ship in history.
  - This map **does** carry execution (gitignore, drop copies, orphan commit) once decisions unblock it.
- Inventory already known (workspace, not tickets): `data/` ~5G and `.trash/` stay local; published history is a small root commit plus follow-ups; remote is https://github.com/Qiucha/GPGaussian.git (`main`).

## Decisions so far

- [What besides first-party code ships in the GitHub-ready tree](issues/03-publish-surface.md) — Publish agent docs + `.agents/` + `.scratch/` + changelog/design notes + digest dashboard source/`digest.md`; gitignore `.claude/`, `issues/`, paper drafts, `Dev Plan.md`, `digest/data/`, and the PDFs.
- [How to consume PhysGaussian as upstream instead of in-tree copies](issues/01-physgaussian-upstream-consume.md) — Clone PhysGaussian with recurse-submodules into gitignored `third_party/`; drop copied Warp/render files; keep `materials` + `lame_params` as the delta.
- [How to consume Gaussian Splatting and FlashSplat as upstream](issues/02-gs-and-flashsplat-upstream-consume.md) — Simulation uses PhysGaussian’s 3DGS submodule; FlashSplat is a separate clone; do not dual-insert both on `sys.path`.
- [Replace in-tree PhysGaussian copies with upstream imports](issues/04-replace-physgaussian-copies-with-upstream.md) — `src/upstream.py` locates clones; Warp/filling/render copies removed; `materials` overlay and thin camera/checkpoint wrappers kept.
- [Ignore rules, drop bytecode, fresh root commit](issues/05-gitignore-and-orphan-commit.md) — `.gitignore` plus single root commit `8d2d74b` on `main`; 216 files; no data/vendor/bytecode in history; no remote.
- [Root README for upstream clones and the Phys4DGS delta](issues/06-root-readme-upstream-clone.md) — `README.md` documents `third_party/` clones (PhysGaussian `8339ed6`, FlashSplat `3e3b147`), env vars, and `run_pipeline.sh`.

## Not yet specified

- Longer README narrative (paper abstract, full architecture) if you want more than clone/install.

## Out of scope

- Git LFS or uploading `data/` checkpoints, `.ply`, or simulation outputs.
- The Few-Shot LLM Motion Library RFC (separate map under `.scratch/llm-motion-physgaussian/`).
