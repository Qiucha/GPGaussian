# Ticket 010: Surface Normal & Curvature Heuristic Primitive

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we estimate local 3D surface normals and surface curvature (via local k-NN covariance eigenvalue decomposition) to differentiate planar, cylindrical, and highly curved components (e.g. table surface vs vase body, aircraft wings vs fuselage)?

## Technical Plan

1. Implement `SurfaceNormalCurvatureHeuristic` in `src/segmentation/heuristics.py` deriving local covariance matrices from k-NN point neighborhoods.
2. Extract principal components (normal vector = smallest eigenvector) and surface variation / curvature ($c = \lambda_0 / (\lambda_0 + \lambda_1 + \lambda_2)$).
3. Support filtering by normal orientation (e.g., vertical $\pm Z$, horizontal planar) and curvature threshold.
4. Register `surface_normal_curvature` in `HeuristicRegistry`.
5. Add unit test suite in `tests/test_hybrid_segmentation.py`.

## Resolution

- Implemented `SurfaceNormalCurvatureHeuristic` in `src/segmentation/heuristics.py` performing k-NN local covariance decomposition ($\mathbf{C} = \frac{1}{k}\sum (x_i - \bar{x})(x_i - \bar{x})^T$) for 3D surface normal vector and curvature calculation.
- Registered `surface_normal_curvature`, `surface_normal`, and `curvature` in `HeuristicRegistry`.
- Added unit test `test_surface_normal_and_curvature_heuristic` in `tests/test_hybrid_segmentation.py` passing cleanly (6/6 tests passing).
