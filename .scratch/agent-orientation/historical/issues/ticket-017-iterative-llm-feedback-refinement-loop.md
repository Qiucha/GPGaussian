# Ticket 017: Iterative LLM Feedback & Self-Correction Refinement Loop

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we implement `SegmenterAgent.run_iterative_refinement()` in `src/llm/segmenter_agent.py` to ingest quantitative diagnostic metrics, critique candidate plans, and autonomously self-correct heuristic steps over up to 3 refinement iterations?

## Technical Plan

1. Update `SegmenterAgent` with `build_refinement_prompt()` presenting candidate plan, resulting tags breakdown, and `SegmentationMetrics` feedback report.
2. Implement `run_iterative_refinement()` looping through generation $\to$ execution $\to$ evaluation $\to$ prompt feedback correction until convergence or max iterations (default 3).
3. Extend unit tests in `tests/test_segmenter_agent.py` verifying multi-turn refinement behavior.

## Resolution

- Implemented `build_refinement_prompt()` and `execute_with_iterative_refinement()` in `src/llm/segmenter_agent.py`.
- Ingests quantitative `SegmentationMetrics` reports (Silhouette score, intra-material spatial/color variances, speckle noise percentage, component fragmentation counts) to generate multi-turn LLM prompts.
- Autonomously critique candidate plans and self-corrects heuristic parameters/primitives over multi-turn refinement loops until reaching `EXCELLENT` quality or max iterations (default 3).
- Verified full test suite (`test_hybrid_segmentation.py`, `test_segmentation_metrics.py`, `test_segmenter_agent.py`, `test_multi_model_benchmark.py`, `test_schema_and_cfl.py`) passing 24/24 tests.
