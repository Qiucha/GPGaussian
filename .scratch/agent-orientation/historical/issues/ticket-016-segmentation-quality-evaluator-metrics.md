# Ticket 016: Quantitative Segmentation Quality Evaluator

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we implement a `SegmentationEvaluator` in `src/segmentation/metrics.py` to calculate intra-material variance, Silhouette score, spatial contiguity index, and speckle noise ratio for feedback to the LLM agent?

## Technical Plan

1. Create `src/segmentation/metrics.py` with `SegmentationMetrics` dataclass and `SegmentationEvaluator.evaluate()` function.
2. Compute intra-class color & spatial variance ($\sigma_{\text{color}}^2, \sigma_{\text{spatial}}^2$).
3. Compute spatial contiguity ratio (connected components per tag) and speckle noise percentage.
4. Format diagnostic report string for LLM feedback prompt consumption.
5. Add unit tests in `tests/test_segmentation_metrics.py`.

## Resolution

- Created `src/segmentation/metrics.py` implementing `SegmentationEvaluator` and `SegmentationMetrics`.
- Computes per-tag spatial standard deviation, color standard deviation, voxel graph connected components, and isolated speckle particle counts.
- Computes global spatial-chromatic Silhouette proxy score and overall quality rating (`EXCELLENT`, `GOOD`, `NEEDS_REFINEMENT`, `POOR`).
- Formats structured text diagnostic report (`format_llm_feedback()`) for LLM agent self-correction feedback.
- Added unit tests in `tests/test_segmentation_metrics.py` passing 2/2 tests.
