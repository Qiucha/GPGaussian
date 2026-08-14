# Ticket 013: Segmenter Agent Schema Extension & Multi-Model Evaluation

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we extend `src/llm/schema.py`, system prompts in `src/llm/segmenter_agent.py`, and scene metadata extraction to allow the LLM agent to select surface normal, color clustering, and superpoint graph heuristics, and benchmark precision across all 6 models?

## Technical Plan

1. Update `HeuristicStepConfig` in `src/llm/schema.py` to add `surface_normal_curvature`, `color_clustering`, and `superpoint_graph` to the allowed `primitive_type` enum.
2. Extend `src/segmentation/metadata.py` (`extract_scene_metadata`) to compute surface normal distribution and color variance stats for LLM prompt formatting.
3. Update `SegmenterAgent` system prompt to describe the new primitives and when to use them for non-plant object categories.
4. Run multi-model segmentation benchmarks across bread, plane, wolf, pillow, and vasedeck dataset models.

## Resolution

- Extended `valid_primitives` in `src/llm/schema.py` to support `surface_normal_curvature`, `color_clustering`, and `superpoint_graph` primitive types.
- Updated `SEGMENTER_SYSTEM_PROMPT` in `src/llm/segmenter_agent.py` detailing usage parameters for surface normals, K-Means/GMM color clustering, and superpoint RAG graph filtering.
- Extended `SegmenterAgent._rule_based_fallback_plan` with specialized heuristic rules for non-plant object categories (bread crust/crumb, aircraft wings/fuselage, furniture legs/cushion).
- Verified test suite (`test_segmenter_agent.py`, `test_multi_model_benchmark.py`, `test_schema_and_cfl.py`) passing 11/11 tests.
