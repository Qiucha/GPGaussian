# Ticket 012: Superpoint Graph Spatial Connectivity Heuristic

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we construct a Superpoint Region Adjacency Graph (RAG) and spatial connectivity constraint heuristic to eliminate isolated speckle noise and enforce spatially contiguous material region boundaries?

## Technical Plan

1. Implement `SuperpointGraphHeuristic` in `src/segmentation/heuristics.py` building a k-NN spatial graph over 3D Gaussian centroids.
2. Group point clouds into local superpoint voxels/clusters and propagate majority material tags across adjacent superpoints.
3. Prune small disconnected tag components below a configurable minimum size percentage.
4. Register `superpoint_graph` in `HeuristicRegistry`.
5. Add unit test suite in `tests/test_hybrid_segmentation.py`.

## Resolution

- Implemented `SuperpointGraphHeuristic` in `src/segmentation/heuristics.py` performing voxel grid superpoint quantization and Region Adjacency Graph (RAG) connected component analysis using `scipy.sparse.csgraph`.
- Added automatic pruning of small disconnected tag component islands smaller than `min_component_ratio`.
- Registered `superpoint_graph`, `superpoint_rag`, and `spatial_connectivity` in `HeuristicRegistry`.
- Added unit test `test_superpoint_graph_heuristic` in `tests/test_hybrid_segmentation.py` passing cleanly (8/8 tests passing).
