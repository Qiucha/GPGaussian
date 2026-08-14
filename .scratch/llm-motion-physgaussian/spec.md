# Specification: Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian

Status: ready-for-agent

## Problem Statement

Configuring physics-based 3D Gaussian Splatting simulations (PhysGaussian) requires manual specification of continuum mechanics parameters (Young's modulus E, Poisson's ratio nu, mass density rho, and spatio-temporal force fields) in raw JSON files. As physical animation fidelity increases, objects require granular multi-material point-cloud tagging (e.g. distinguishing a rigid pot, flexible trunk, and compliant leaves). Manually tuning parameters and tagging 3D point clouds is error-prone, time-consuming (>25 minutes per scene), and often leads to numerical solver explosions due to CFL condition violations or singular Poisson ratios.

## Solution

An end-to-end automated system combining a **Few-Shot LLM Motion Translator** with a **Hybrid 3D Point-Cloud Material Segmentation Engine**. Users specify desired motions in plain natural language (e.g. *"Blow a strong gust of wind from the left to sway the ficus leaves while keeping the pot anchored"*). The system retrieves exemplars from a curated **Motion Library**, uses Chain-of-Thought reasoning to generate a validated `PhysGaussianLLMConfig` JSON payload, automatically segments the 3D point cloud into heterogeneous material tags via 3D SH RGB dominance filtering and 2D/3D masks, and initializes per-particle Lamé parameters in Nvidia Warp MPM solver kernels.

## User Stories

1. As a 3D animator, I want to describe desired object motions in natural language, so that I don't have to manually edit JSON force vectors and time-step deltas.
2. As a graphics researcher, I want the LLM to output Chain-of-Thought physical reasoning before generating JSON, so that I can inspect the physical assumptions made by the model.
3. As a simulation engineer, I want an automated CFL stability guardrail to validate generated parameters, so that explicit MPM simulations never diverge or explode numerically.
4. As a user simulating complex multi-part objects, I want automatic 3D point-cloud segmentation based on 3D SH RGB color filtering and spatial bounds, so that discrete material properties (pot vs trunk vs leaves) are tagged without manual 3D selection tools.
5. As a developer, I want a vector-indexed Motion Library containing few-shot exemplars for core physical dynamics (wind drag, impulse impact, twisting torque, elastoplastic tearing), so that the LLM receives relevant context for diverse physical behaviors.
6. As a researcher benchmark coordinator, I want automated gold-standard evaluation scripts computing FVD, KVD, SVD-Kabsch Trajectory MSE, PSNR, SSIM, LPIPS, and user effort metrics, so that system improvements can be rigorously benchmarked against baseline PhysGaussian.

## Implementation Decisions

### 1. Configuration Schema (`PhysGaussianLLMConfig`)
- Extends standard PhysGaussian JSON format with a `materials` dictionary mapping string integer tags (`"0"`, `"1"`, `"2"`) to mechanical property objects (`E`, `nu`, `density`, `material_type`, `yield_stress`).
- Includes a `material_segmentation_rules` array for sequential point-cloud tagging.
- Supports a `boundary_conditions` array featuring `particle_impulse`, `cuboid`, `enforce_particle_velocity_rotation`, `surface_collider`, and `enforce_particle_translation`.

```json
{
  "substep_dt": 5e-05,
  "frame_dt": 0.04,
  "frame_num": 120,
  "n_grid": 120,
  "g": [0.0, 0.0, -9.81],
  "materials": {
    "0": { "E": 1.0e7, "nu": 0.30, "density": 1800.0 },
    "1": { "E": 5.0e5, "nu": 0.35, "density": 600.0 },
    "2": { "E": 2.0e3, "nu": 0.45, "density": 150.0 }
  },
  "boundary_conditions": [
    {
      "type": "particle_impulse",
      "force": [0.00025, 0.0, 0.00005],
      "point": [1.0, 1.0, 1.4],
      "size": [1.2, 1.2, 0.8],
      "num_dt": 30000,
      "start_time": 0.0
    }
  ]
}
```

### 2. Guardrails & Physical Transformations
- Automated pre-simulation Python validator (`validate_physgaussian_config`) checking nu <= 0.49 and CFL ratio (c_p * dt_sub) / dx <= 0.5, where elastic P-wave speed c_p = sqrt((E * (1 - nu)) / (rho * (1 + nu) * (1 - 2 * nu))).
- Evaluates Lamé parameters mu_p = E_p / (2 * (1 + nu_p)) and lambda_p = (E_p * nu_p) / ((1 + nu_p) * (1 - 2 * nu_p)) per particle in Warp CUDA arrays (`wp.array(dtype=wp.float32)`).

### 3. Motion Library & Vector Retrieval Engine
- Curates 4 physical dynamics exemplars (Wind/Fluid Drag, Impulse Impact/Drop, Bending/Twisting Torque, Elastoplastic Tearing).
- Dense-sparse hybrid vector store (`text-embedding-3-large` / `BGE-M3`) with Maximal Marginal Relevance (MMR) reranking (alpha=0.75) injecting k=2-3 exemplars into a 4096-token budget.

### 4. Hybrid Point-Cloud Tagger
- 2D LangSAM unprojection with hardcoded Z-stack priority (`stem/trunk > leaves > pot`) for base geometry.
- 0th-order SH DC conversion to RGB ($C_{RGB} = f_{dc} \cdot 0.282095 + 0.5$) with chromatic dominance rules (R > G and R > B for wood, G > R and G > B for foliage) for fine structures.
- DBSCAN density clustering (epsilon=0.1, min_samples=5) to purge specular reflection noise.

### 5. Evaluation Suite
- `src/eval/evaluate_realism.py`: Computes I3D FVD/KVD, SVD-Kabsch aligned particle trajectory MSE, PSNR, SSIM, and LPIPS.
- `src/eval/evaluate_effort.py`: Logs setup duration T_setup, manual lines of code LOC_manual, iteration count N_iter, and NASA-TLX workload scores.

## Testing Decisions

- **Testing Principles:** Test external module behaviors at high-level seams rather than internal state variables or private functions.
- **Seam A (Configuration Synthesis):** Test `src/llm/` by passing natural language prompts and scene bounding boxes, asserting that valid `PhysGaussianLLMConfig` payloads are produced and pass CFL/Poisson stability checks.
- **Seam B (Segmentation & MPM Parameters):** Test `src/segmentation/` and `src/simulation/config.py` by feeding sample `.ply` point clouds and JSON configs, asserting that output `material_tags.pt` arrays and Warp parameter arrays (`mu`, `lambda`, `density`) contain expected shape `(N,)` and values within physical tolerances.

## Out of Scope

- Real-time interactive UI rendering during physics solve steps.
- Retraining or fine-tuning underlying 3DGS neural network weights.
- Physical force feedback or haptic hardware integration.

## Further Notes

- Maintains environment compatibility with existing PhysGaussian CUDA extensions (avoiding PyTorch >= 2.3.1 Grounding DINO CUDA compile conflicts).
