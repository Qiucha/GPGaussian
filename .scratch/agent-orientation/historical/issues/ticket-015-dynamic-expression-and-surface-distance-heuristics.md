# Ticket 015: Dynamic Tensor Expression & Surface Boundary Distance Heuristics

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we design and implement `DynamicExpressionHeuristic` (evaluating arbitrary mathematical/logical tensor expressions over coordinates, colors, surface normals, and anisotropy) and `SurfaceDistanceHeuristic` (evaluating distance to object surface hull vs internal core) in `src/segmentation/heuristics.py`?

## Technical Plan

1. Implement `DynamicExpressionHeuristic` in `src/segmentation/heuristics.py` using AST/numexpr safe parsing over variables (`x, y, z, r, g, b, h, s, v, nx, ny, nz, curvature, anisotropy`).
2. Implement `SurfaceDistanceHeuristic` in `src/segmentation/heuristics.py` calculating point-to-convex-hull distance transform.
3. Register `dynamic_expression` and `surface_distance` in `HeuristicRegistry`.
4. Add unit test suite in `tests/test_hybrid_segmentation.py`.

## Resolution

- Implemented `DynamicExpressionHeuristic` in `src/segmentation/heuristics.py` enabling dynamic execution of mathematical/boolean conditions over `(x, y, z, r, g, b, h, s, v, nx, ny, nz, curvature, anisotropy)` with automatic operator pre-processing.
- Implemented `SurfaceDistanceHeuristic` in `src/segmentation/heuristics.py` calculating distance transform from particle centroids to 3D convex boundary hulls via `scipy.spatial.ConvexHull` and `KDTree`.
- Registered `dynamic_expression` and `surface_distance` in `HeuristicRegistry`.
- Added unit tests `test_dynamic_expression_heuristic` and `test_surface_distance_heuristic` in `tests/test_hybrid_segmentation.py` passing 10/10 tests cleanly.
