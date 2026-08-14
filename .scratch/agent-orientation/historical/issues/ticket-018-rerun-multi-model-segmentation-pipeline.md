# Ticket 018: Rerun Multi-Model Segmentation Pipeline with Iterative Refinement & Metrics Export

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we update `scripts/export_pipeline_data.py` to run `SegmenterAgent.execute_with_iterative_refinement()`, compute and export `metrics.json` and iterative refinement history for all 6 dataset models (`bread-trained`, `ficus_whitebg`, `pillow2sofa_whitebg-trained`, `plane-trained`, `vasedeck_whitebg`, `wolf_whitebg-trained`), and regenerate all `particles.json`, `metadata.json`, `plan.json`, `reference.jpg`, and 30 trajectory frame images per model?

## Technical Plan

1. Update `scripts/export_pipeline_data.py` to import `SegmentationEvaluator` and call `agent.execute_with_iterative_refinement(xyz, sh_dc, scales, object_category=model_name)`.
2. Save `metrics.json` into each model output folder in `digest/data/`.
3. Update `manifest.json` generation to include quality ratings, Silhouette scores, and refinement iteration counts per model.
4. Execute `scripts/export_pipeline_data.py` with python environment `physgauss`.
5. Verify export completeness via unit tests and file existence checks in `digest/data/`.

## Resolution

- Updated `scripts/export_pipeline_data.py` to execute `SegmenterAgent.execute_with_iterative_refinement(xyz, sh_dc, scales, object_category=model_name, max_iterations=3)`.
- Exported `metrics.json` for all 6 models containing quantitative Silhouette scores, spatial/color variances, speckle noise percentages, connected component counts, and multi-turn refinement loop history (`refinement_history`).
- Updated `manifest.json` to summarize `quality_rating`, `silhouette_score`, `speckle_total_pct`, and `refinement_iterations` per dataset model.
- Regenerated all particle assets, metadata, reference render images, and 180 trajectory simulation frames (30 per model) into `digest/data/`.
- Verified export integrity via `scripts/verify_digest_assets.py`.
