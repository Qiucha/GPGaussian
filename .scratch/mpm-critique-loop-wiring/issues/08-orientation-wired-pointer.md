# 08 - Point orientation at the wired Motion Critique Loop

Type: task
Status: resolved
Blocked by: 07

## Question

Update [docs/agents/orientation.md](../../../docs/agents/orientation.md) so Next steps (and Current state / How to run, as needed) describe the Motion Critique Loop as wired in `src/` (mock `critique` + new driver; live still `NotImplementedError`) and `run_pipeline.sh` as still PartSAM → solver. Do not add Motion Critique Loop to `CONTEXT.md`. `/writing-for-agents`: one pointer, not a restatement of the spec.

## Answer

[docs/agents/orientation.md](../../../docs/agents/orientation.md): Current state names mock `critique` and `src/llm/critique_loop.py`; live `translate` / `critique` stay stubbed. How to run includes `tests.test_motion_critique`. Next steps: one policy pointer at [Motion Critique Loop spec](../../mpm-critique-loop/spec.md); `run_pipeline.sh` stays PartSAM → first solver. Pointers table has the same reach condition. `CONTEXT.md` unchanged.

## Comments
