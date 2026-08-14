# 03 - 3D Point-Cloud Material Segmentation & Generalized Heuristics

Type: research
Status: resolved
Blocked by: none

## Question

How can 3D point-cloud segmentation algorithms (SAM3D/LangSAM) be combined with generalized 3D heuristics (SH color filtering, spatial bounding, geometric curvature) to automatically assign heterogeneous MPM material parameters per particle, and how does the LLM interface with these heuristic selectors?

## Answer

### Key Findings & Architectural Decision

1. **Hybrid Segmentation Strategy:**
   - **Base Level (2D LangSAM / SAM3D Projection):** Uses 2D unprojection with hardcoded semantic priority (`stem/trunk > leaves > pot`) for large base objects (pot, ground).
   - **Fine Structure (3D SH RGB Dominance):** Converts 0th-order SH DC components to RGB ($C_{RGB} = f_{dc} \cdot 0.282095 + 0.5$) and applies chromatic dominance rules (e.g. $R>G \land R>B$ for wood, $G>R \land G>B$ for leaves) to capture thin, sub-pixel structures (capturing ~36,000 trunk Gaussians vs 10-100 via 2D masks alone).
   - **Post-Processing (DBSCAN Clustering):** Removes floating misclassified noise points from specular reflections or cross-color boundary kernels.

2. **Heterogeneous MPM Solver Parameterization:**
   - Evaluates Lamé parameters $\mu_p = \frac{E_p}{2(1 + \nu_p)}$ and $\lambda_p = \frac{E_p \nu_p}{(1 + \nu_p)(1 - 2\nu_p)}$ per particle in Nvidia Warp CUDA kernels (`wp.array(dtype=wp.float32)` for `mu`, `lambda`, `density`).

3. **LLM Orchestration Interfaces:**
   - Defined declarative Pydantic/JSON schema for `LLMSegmentationPipelineConfig`, standardized Python abstract base classes (`ColorSHHeuristic`, `SpatialBoundingHeuristic`, `DBSCANFilterHeuristic`), and OpenAI/AGY tool declarations (`inspect_point_cloud_stats`, `apply_segmentation_heuristics`, `generate_simulation_config`).
