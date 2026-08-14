# Historical log

This file is a **changelog**, not agent instructions and not a task list.

Live orientation (purpose, current state, next steps): [docs/agents/orientation.md](docs/agents/orientation.md)

---

# Project Changelog & Wayfinding Execution History

This document records the complete, high-density history of the **Phys4DGS / PhysGaussian Few-Shot LLM & Granular Material Assignment** effort. It is structured so that each section provides an at-a-glance summary alongside deep technical specifications.

---

## 📌 At-a-Glance Executive Summary

| Phase | Milestone | Primary Artifacts | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Wayfinder Research & Decisions** | [map.md](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/map.md), [issues/01-04](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/) | `Completed` |
| **Phase 2** | **Technical Specification (RFC)** | [spec.md](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/spec.md) | `Completed` |
| **Phase 3** | **Tracer-Bullet Implementation** | `src/llm/`, `src/segmentation/`, `src/simulation/`, `src/eval/` | `Completed (16/16 Tests PASS)` |
| **Phase 4** | **Codebase Refactoring** | `heuristics.py`, `checkpoint.py`, `llm_generator.py` | `Completed (Commit: a866485)` |
| **Phase 5** | **Interactive 3D Web Prototype** | [digest/index.html](file:///home/q/Projects/mit/PBL/Phys4DGS/digest/index.html), `app.js`, `style.css` | `Completed (Running on :8080)` |

---

## 🗺️ Detailed Phase History & Architectural Records

### Phase 1: Wayfinder Research & Frontier Mapping
* **Destination:** Formulate a comprehensive Research & Architecture Specification (RFC) for a Few-Shot LLM Motion-to-Configuration system with granular 3D point-cloud material segmentation heuristics and gold-standard evaluation protocols.
* **Key Decisions Resolved:**
  1. **[Ticket 01: LLM Schema & Prompt Design](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/01-llm-schema-and-prompt-design.md):** Extended PhysGaussian JSON with `materials`, `material_segmentation_rules`, and `boundary_conditions`; established Chain-of-Thought (CoT) system prompts and CFL wave speed stability checks ($c_p = \sqrt{\frac{E(1-\nu)}{\rho(1+\nu)(1-2\nu)}}$, $\Delta t_{\text{sub}} \le 0.5 \frac{\Delta x}{c_p}$).
  2. **[Ticket 02: Motion Library & Few-Shot Exemplars](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/02-motion-library-few-shot-examples.md):** Curated 4 core physical dynamics primitives (Wind Drag, Impact Drop, Twisting Torque, Elastoplastic Tearing) with dense-sparse vector search and MMR reranking ($\alpha=0.75$).
  3. **[Ticket 03: 3D Point-Cloud Material Segmentation](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/03-pointcloud-material-segmentation-heuristics.md):** Designed hybrid segmentation combining 2D LangSAM base unprojection (with Z-priority `stem > leaves > pot`) and 3D SH RGB dominance filtering ($R>G \land R>B$ for wood, $G>R \land G>B$ for foliage).
  4. **[Ticket 04: Gold-Standard Evaluation Protocol](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/04-gold-standard-evaluation-protocol.md):** Formulated quantitative realism metrics (I3D FVD/KVD, SVD-Kabsch Trajectory MSE, PSNR, SSIM, LPIPS) and setup effort metrics ($T_{\text{setup}}$, $LOC_{\text{manual}}$, $N_{\text{iter}}$, NASA-TLX).

---

### Phase 2: Technical Specification & Seams
* **Specification File:** [spec.md](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/spec.md)
* **Testing Seam Architecture:**
  - **Seam A (`src/llm/`):** Motion Library retrieval, CoT prompt synthesis, and CFL stability validator.
  - **Seam B (`src/segmentation/` & `src/simulation/`):** Point-cloud material tagger and per-particle Warp MPM CUDA array constructor ($\mu, \lambda, \rho$).

---

### Phase 3: Implementation & TDD Verification
* **Delivered Modules & Code Artifacts:**
  - `src/llm/schema.py` & `src/llm/validator.py`: Dataclass models and `validate_physgaussian_config` CFL guardrail.
  - `src/segmentation/heuristics.py`: Abstract `BaseHeuristic`, `ColorSHHeuristic`, `SpatialBoundingHeuristic`, `DBSCANFilterHeuristic`, and SH DC un-normalization ($C_{RGB} = f_{dc} \cdot 0.282095 + 0.5$).
  - `src/simulation/lame_params.py`: Lamé parameters $\mu_p = \frac{E_p}{2(1+\nu_p)}$ and $\lambda_p = \frac{E_p \nu_p}{(1+\nu_p)(1-2\nu_p)}$ calculator.
  - `src/llm/motion_library.py`: Curated exemplars & `MotionLibraryRetriever` with MMR reranking.
  - `src/llm/translator.py`: End-to-end `MotionTranslator` with CoT prompt formatting.
  - `src/eval/evaluate_realism.py` & `evaluate_effort.py`: SVD-Kabsch Trajectory MSE, 2AFC Binomial statistics, and NASA-TLX logger.
* **Test Suite Status:** 16/16 unit and integration tests passing (`Ran 16 tests in 0.489s. OK.`).
* **Git Commit:** `0efd6d2` (`feat(llm-motion): implement few-shot LLM motion library & material assignment pipeline`).

---

### Phase 4: Codebase Refactoring & Consolidation
* **Refactoring Actions:**
  - **Segmentation:** Unified 0th-order SH DC-to-RGB conversion math in `color_heuristic.py`, `vasedeck_heuristic.py`, and `trunk_heuristic.py`.
  - **Rendering & Eval:** Consolidated `load_checkpoint` and `PipelineParamsNoparse` in `src/rendering/checkpoint.py`.
  - **Utilities:** Refactored `src/utils/llm_generator.py` to wrap `MotionTranslator` and `validate_physgaussian_config`.
* **Git Commit:** `a866485` (`refactor: consolidate heuristics, checkpoint loaders, and LLM generators`).

---

### Phase 5: Interactive 3D Web Digest Prototype
* **Artifact Location:** [digest/index.html](file:///home/q/Projects/mit/PBL/Phys4DGS/digest/index.html) (`style.css`, `app.js`)
* **Features:**
  - 3D WebGL Point-Cloud Viewport (Three.js + OrbitControls) with real-time particle color-shifting across 5 pipeline stages:
    1. *Raw 3DGS Base SH Colors*
    2. *2D LangSAM Base Unprojection*
    3. *3D SH RGB Dominance Filter*
    4. *DBSCAN Density Outlier Purge*
    5. *Final Heterogeneous MPM Material Assignment*
  - Material Breakdown Progress Bars, Physics Parameters Matrix ($E, \nu, \rho, \mu, \lambda$), and Live Execution Console.
* **Deployment:** Runnable via `python3 -m http.server 8080 --directory digest`.
