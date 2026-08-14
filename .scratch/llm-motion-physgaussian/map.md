# Map: Few-Shot LLM Motion Library & Granular Material Assignment for PhysGaussian

## Destination

A comprehensive Research & Architecture Specification (RFC) for a Few-Shot LLM Motion-to-Configuration system with granular 3D point-cloud material segmentation heuristics and gold-standard evaluation protocols for PhysGaussian.

## Notes

- Effort slug: `llm-motion-physgaussian`
- Key Skills: `/research`, `/domain-modeling`, `/grilling`
- Standing preferences: Focus on reducing human configuration effort while improving sim-to-real visual/physical animation fidelity; use gold-standard evaluation metrics.

## Decisions so far

- [01 - LLM Schema and Few-Shot System Prompt Design](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/01-llm-schema-and-prompt-design.md) — Defined JSON config schema, CoT prompt architecture, mechanical parameter transformations, and CFL stability validation guardrails.
- [02 - Motion Library & Few-Shot Example Collection](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/02-motion-library-few-shot-examples.md) — Specified 4 physical dynamics primitives (wind, drop/impact, twisting torque, elastoplastic tearing), hybrid vector indexing/MMR retrieval, and prompt context injection mechanics.
- [03 - 3D Point-Cloud Material Segmentation & Generalized Heuristics](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/03-pointcloud-material-segmentation-heuristics.md) — Defined hybrid segmentation (LangSAM base + 3D SH RGB filter + DBSCAN) and declarative schema/Python/LLM function calling interfaces for per-particle MPM parameter tagging.
- [04 - Gold-Standard Evaluation Protocol for Realism and Effort Reduction](file:///home/q/Projects/mit/PBL/Phys4DGS/.scratch/llm-motion-physgaussian/issues/04-gold-standard-evaluation-protocol.md) — Formulated FVD/KVD, SVD-Kabsch trajectory MSE, PSNR/SSIM/LPIPS, 2AFC perceptual user study protocols, and NASA-TLX setup effort metrics.

## Not yet specified

- **Physics Solver Kernel Optimization:** Custom CUDA kernels for per-particle material parameter decoding in Warp MPM.

Leftover **LLM Real-Time Feedback Loop** fog graduated to [Motion Critique Loop spec](../mpm-critique-loop/map.md) (new destination; this map stays closed).

## Out of scope

- Direct 3D Gaussian retraining/re-splatting (e.g. semantic feature distillation in 3DGS training).
- Real-world sensor hardware integration (e.g. physical force torque sensor calibration).
