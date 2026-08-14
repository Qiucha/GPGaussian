# 12 - Point orientation at the wired PartSAM path

Type: task
Status: resolved
Blocked by: 11

## Question

Update [docs/agents/orientation.md](../../../docs/agents/orientation.md) so Next steps (and Current state / How to run, as needed) describe PartSAM in `src/` as the intended Material Tag Tensor producer and `run_pipeline.sh` as PartSAM → solver. Do not add PartSAM to `CONTEXT.md`. `/writing-for-agents`: one pointer, not a restatement of the spec.

## Answer

[docs/agents/orientation.md](../../../docs/agents/orientation.md): pipeline step 2 and Current state name PartSAM in `src/segmentation/partsam` and `run_pipeline.sh` as PartSAM → PhysGaussian MPM Solver. Next steps is one policy pointer at [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md). `CONTEXT.md` unchanged.

## Comments
