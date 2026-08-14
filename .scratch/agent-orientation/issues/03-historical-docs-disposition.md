# 03 - Archive or rewrite historical docs so they cannot trap agents

Type: grilling
Status: resolved
Blocked by: none

## Question

Q8 chose **dispose historical docs** so later agents do not treat them as live. Which files, and what disposition?

Candidates (confirm, add, or drop):

- `Dev Plan.md`
- `design_decisions.md`
- `digest.md`
- `CHANGELOG.md`
- `issues/` (completed maps 001–019; distinct from `.scratch/`)

Disposition options per file:

1. **Banner** — keep in place; first lines state they are historical and point at `docs/agents/orientation.md`.
2. **Move** — relocate under `.trash/` or `.scratch/agent-orientation/historical/`, leave a stub pointer at the old path.
3. **Rewrite** — replace with a short pointer-only file.

Constraints already settled: `CONTEXT.md` and `docs/agents/` process docs stay. `Paper_Writing/` is not this list unless added here. The orientation pack remains canonical.

Resolve with a per-file table (path → disposition → new location if moved).

## Answer

Per-file disposition (stubs and the changelog banner point at `docs/agents/orientation.md`):

| Path | Disposition | After |
|---|---|---|
| `Dev Plan.md` | Move + stub at old path | `.scratch/agent-orientation/historical/Dev Plan.md` |
| `design_decisions.md` | Move + stub | `.scratch/agent-orientation/historical/design_decisions.md` |
| `digest.md` | Move + stub | `.scratch/agent-orientation/historical/digest.md` |
| `CHANGELOG.md` | Banner in place | stays at root |
| `issues/` | Move tree; `issues/README.md` only at old path | `.scratch/agent-orientation/historical/issues/` |

Untouched: live `digest/` dashboard, `CONTEXT.md`, `AGENTS.md`, `docs/agents/`, `Paper_Writing/`, `.scratch/` maps. Execution is [Apply the historical-docs disposition](05-apply-historical-docs-disposition.md), after the orientation pack exists.
