# Ticket 001: Expand Modular Heuristic Primitives Suite

**Type**: `wayfinder:task`
**Status**: Closed (Resolved)
**Blocks**: [Implement LLM Segmenter Agent Pipeline](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-004-implement-llm-segmenter-agent.md)

## Question

How can we extend `src/segmentation/heuristics.py` into a standardized, modular library of 3D Gaussian segmentation primitives across four distinct categories (Chromatic/SH, Spatial/Geometric, Anisotropic/Structural, Topological/Graph)?

## Resolution

- Extended `src/segmentation/heuristics.py` with multi-modal primitives across 4 categories:
  1. **Chromatic / SH**: `ColorSHHeuristic` with RGB dominance, HSV channel thresholding, LAB color filtering, and 0th-order SH DC energy conversion (`sh_dc_to_rgb`, `rgb_to_hsv`).
  2. **Spatial / Geometric**: `SpatialBoundingHeuristic` with AABB bounding box, axis cutoffs/percentiles, radial cylinders, and PCA principal axis alignment projection.
  3. **Anisotropic / Structural**: `AnisotropicStructuralHeuristic` with scale tensor ratio ($s_{max} / s_{min}$ anisotropy), scale magnitude, and local KD-Tree point density thresholding.
  4. **Topological / Graph**: `TopologicalGraphHeuristic` with DBSCAN noise cluster purging and KNN spatial tag voting smoothing.
- Provided `HeuristicRegistry` factory for registering, instantiating, and applying sequential heuristic pipelines via `apply_pipeline(xyz, sh_dc, tags, steps, scales)`.
- Implemented unit test suite in `tests/test_hybrid_segmentation.py` (5/5 tests passing).
