# Ticket 011: Color GMM / K-Means Spatial Clustering Heuristic

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we design a multi-component color & spatial clustering heuristic using Gaussian Mixture Models (GMM) or K-Means in HSV/LAB color space to segment complex multi-colored non-plant models (bread crust/crumb, wolf fur/eyes/nose)?

## Technical Plan

1. Implement `ColorClusteringHeuristic` in `src/segmentation/heuristics.py` accepting color space (`hsv`, `lab`, `rgb`) and target cluster count $K$.
2. Compute spatial-weighted color features combining normalized $(x, y, z)$ coordinates with color vectors to form cohesive multi-modal clusters.
3. Map resulting cluster IDs to target material tags based on color centroid criteria (e.g. darkest cluster = crust/eyes, lightest = crumb/fur).
4. Register `color_clustering` in `HeuristicRegistry`.
5. Add unit test suite in `tests/test_hybrid_segmentation.py`.

## Resolution

- Implemented `ColorClusteringHeuristic` in `src/segmentation/heuristics.py` supporting K-Means and GMM clustering in HSV/RGB color spaces combined with normalized spatial coordinates.
- Added automatic cluster selection criteria (`"darkest"`, `"lightest"`, `"highest_saturation"`, or explicit `cluster_index`).
- Registered `color_clustering`, `kmeans_color`, and `gmm_color` in `HeuristicRegistry`.
- Added unit test `test_color_clustering_heuristic` in `tests/test_hybrid_segmentation.py` passing cleanly (7/7 tests passing).
