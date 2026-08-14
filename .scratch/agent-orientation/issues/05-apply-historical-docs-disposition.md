# 05 - Apply the historical-docs disposition

Type: task
Status: resolved
Blocked by: 03, 04

## Question

Carry out the per-file disposition decided in [Archive or rewrite historical docs so they cannot trap agents](03-historical-docs-disposition.md), after the orientation pack exists so every stub/banner can point at `docs/agents/orientation.md`.

Done when every listed file matches the table (moved, bannered, or rewritten) and a later agent opening an old path either reaches the pack or cannot mistake the file for live instruction.

## Answer

Moved `Dev Plan.md`, `design_decisions.md`, `digest.md`, and root `issues/` to `.scratch/agent-orientation/historical/`. Left stubs at the old paths (one `issues/README.md`). Bannered `CHANGELOG.md`. Live `digest/` dashboard untouched. Orientation pointers updated to match.
