## Destination

Design, develop, and integrate an expanded suite of multi-modal segmentation heuristics (Surface Normal/Curvature, Color GMM/K-Means Clustering, Superpoint Region Adjacency Connectivity) into `HeuristicRegistry` and `SegmenterAgent` to achieve precise multi-material physics tag assignment across non-plant 3DGS models (bread, plane, wolf, pillow, vasedeck).

## Notes

- Domain: Phys4DGS 3D Gaussian semantic segmentation & multi-material physics properties assignment.
- Key Skills: `domain-modeling`, `codebase-design`, `diagnosing-bugs`, `tdd`.
- Standing Preferences: Pure PyTorch/NumPy tensor performance; strict Pydantic JSON schema validation for LLM execution plans; reproducible seed initialization.

## Decisions so far

- [Surface Normal & Curvature Heuristic Primitive](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-010-surface-normal-and-curvature-heuristic.md) — Implemented `SurfaceNormalCurvatureHeuristic` calculating 3D surface normals and curvature via k-NN covariance decomposition, registered in `HeuristicRegistry`, verified by unit tests.
- [Color GMM / K-Means Spatial Clustering Heuristic](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-011-color-gmm-kmeans-clustering-heuristic.md) — Implemented `ColorClusteringHeuristic` supporting K-Means/GMM spatial color clustering with brightness/saturation selection criteria, registered in `HeuristicRegistry`, verified by unit tests.
- [Superpoint Graph Spatial Connectivity Heuristic](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-012-superpoint-graph-spatial-connectivity-heuristic.md) — Implemented `SuperpointGraphHeuristic` performing RAG superpoint grid quantization and connected component speckle pruning, registered in `HeuristicRegistry`, verified by unit tests.
- [Segmenter Agent Schema Extension & Multi-Model Evaluation](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-013-agent-prompt-schema-and-benchmark-integration.md) — Extended `SegmenterExecutionPlan` Pydantic schemas, updated `SegmenterAgent` prompts and fallback plans, verified 11/11 agent & benchmark unit tests.

## Frontier Tickets

*(All 4 tickets resolved! Map destination reached.)*

## Not yet specified

- 2D multi-view image mask consensus voting (Grounded-SAM / CLIP projection).
- Iterative LLM self-correction feedback loop evaluating cluster Silhouette score and intra-material variance.

## Out of scope

- End-to-end neural network fine-tuning requiring full GPU gradient re-training per scene.
