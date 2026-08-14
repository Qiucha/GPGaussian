# 03 - What besides first-party code ships in the GitHub-ready tree

Type: grilling
Status: resolved
Blocked by: none

## Question

Aside from `src/` (Phys4DGS delta only), `tests/`, `configs/`, `scripts/`, `pyproject.toml`, `CONTEXT.md`, and `docs/agents/`: which of the following belong in the published tree, and which stay gitignored as local-only?

- `.agents/` and `.claude/` skill copies, `AGENTS.md`, `skills-lock.json`
- `.scratch/` (already tracked) and `issues/`
- `Paper_Writing/`, `CHANGELOG.md`, `design_decisions.md`, `Dev Plan.md`
- `digest/` (dashboard + ~12M exported frames), `digest.md`, `digest.pdf`, `walkthrough.pdf`

The destination already excludes `data/`, `.trash/`, and third-party clones.

## Answer

Publish vs local-only (human confirmed “as recommended”):

**Publish:** `AGENTS.md`, `docs/agents/`, `skills-lock.json`, `.agents/`, `.scratch/`, `CHANGELOG.md`, `design_decisions.md`, `digest.md`, dashboard source (`digest/index.html`, `digest/app.js`, `digest/style.css`).

**Gitignore (local-only):** `.claude/` (duplicate skills), `issues/` (parallel leftover tracker), `Paper_Writing/`, `Dev Plan.md`, `digest/data/` (exported frames/JSON), `digest.pdf`, `walkthrough.pdf`.
