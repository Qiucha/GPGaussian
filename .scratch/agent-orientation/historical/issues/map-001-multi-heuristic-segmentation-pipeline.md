## Destination

Build a generalizable multi-heuristic segmentation suite (Chromatic, Spatial, Anisotropic, Topological) and an LLM-driven Segmenter Agent selector producing structured JSON execution plans, fully integrated with PhysGaussian MPM simulation and verified across at least 3 distinct non-ficus 3DGS models.

## Notes

- Domain: Phys4DGS multi-material physics simulation and point-cloud semantic segmentation.
- Key Skills: `domain-modeling`, `codebase-design`, `diagnosing-bugs`, `tdd`.
- Standing Preferences: Maintain PyTorch tensor performance; avoid external unverified dependencies; strict Pydantic JSON schema validation for LLM agent outputs.

## Decisions so far

- [Round 1 Scope & Architecture Decisions](file:///home/q/Projects/mit/PBL/Phys4DGS/CONTEXT.md) — Established multi-modal heuristic taxonomy (Chromatic, Spatial, Anisotropic, Topological), single-prompt LLM agent selector with JSON schema validation, and discrete material tag tensor mapping to MPM solver parameters ($E, \nu, \rho$).
- [Expand Modular Heuristic Primitives Suite](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-001-expand-heuristic-primitives.md) — Implemented `ColorSHHeuristic` (RGB/HSV/LAB), `SpatialBoundingHeuristic` (AABB/percentile/cylinder/PCA), `AnisotropicStructuralHeuristic` (scale ratio/magnitude/density), `TopologicalGraphHeuristic` (DBSCAN/KNN), and unified `HeuristicRegistry`.
- [Design Segmenter Agent JSON Execution Plan Schema](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-002-design-agent-json-schema.md) — Defined `MaterialTagDefinition`, `HeuristicStepConfig`, and `SegmenterExecutionPlan` in `src/llm/schema.py` with strict schema validation enforcing tag consistency and physical bounds.
- [Build 3DGS Scene Metadata Extractor](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-003-build-3dgs-scene-metadata-extractor.md) — Implemented `extract_scene_metadata` in `src/segmentation/metadata.py` computing spatial extents, Y/Z percentiles, RGB/HSV color dominance, and anisotropy ratios for prompt formatting.
- [Implement LLM Segmenter Agent Pipeline](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-004-implement-llm-segmenter-agent.md) — Implemented `SegmenterAgent` in `src/llm/segmenter_agent.py` supporting scene prompt construction, plan generation/validation, and end-to-end `material_tags.pt` execution.
- [Multi-Model Verification & MPM Simulation Benchmark](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-005-multi-model-verification-and-mpm-benchmark.md) — Verified `SegmenterAgent` pipeline across 3 distinct object categories (potted plant, office chair, composite anisotropic toy) and validated PhysGaussian MPM simulation config binding under CFL conditions.

## Frontier Tickets

*(All 5 tickets resolved! Map destination reached.)*

## Not yet specified

- Automated cluster quality evaluation & iterative heuristic feedback loop (if single-prompt selection requires refinement).
- Neural 3D feature splatting / DINO feature distillation integration.

## Out of scope

- 2D video temporal tracking via Grounded SAM 2 (ruled out due to CUDA/PyTorch 2.3+ C++ extension compilation incompatibilities).
