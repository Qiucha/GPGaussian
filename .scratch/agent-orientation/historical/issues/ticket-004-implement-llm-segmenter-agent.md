# Ticket 004: Implement LLM Segmenter Agent Pipeline

**Type**: `wayfinder:task`
**Status**: Closed (Resolved)
**Blocks**: [Multi-Model Verification & MPM Simulation Benchmark](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-005-multi-model-verification-and-mpm-benchmark.md)

## Question

How do we construct the LLM Segmenter Agent that ingests `SceneMetadata` and object category description, generates a validated `SegmenterExecutionPlan`, and executes the plan to produce `material_tags.pt`?

## Resolution

- Implemented `SegmenterAgent` in `src/llm/segmenter_agent.py`:
  1. `SEGMENTER_SYSTEM_PROMPT`: Directs the LLM on available heuristic primitives (Chromatic, Spatial, Structural, Topological) and physical property mapping guidance.
  2. `build_prompt()`: Combines object category prompt and `SceneMetadata.format_prompt_summary()`.
  3. `generate_plan()`: Parses LLM responses (or rule-based fallback generator for offline testing) into validated `SegmenterExecutionPlan`.
  4. `execute_segmentation()`: Integrates `extract_scene_metadata`, `generate_plan`, and `HeuristicRegistry.apply_pipeline` to return particle material tag tensors `(N,)` and execution plans.
- Implemented unit tests in `tests/test_segmenter_agent.py` (4/4 tests passing).
