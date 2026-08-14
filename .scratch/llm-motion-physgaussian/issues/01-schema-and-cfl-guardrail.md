# 01 — PhysGaussianLLMConfig Schema & CFL Validation Guardrail

**What to build:**
Schema definition and automated validation module (`validate_physgaussian_config`) enforcing Poisson ratio bounds (nu <= 0.49) and explicit MPM CFL time-step bounds (CFL <= 0.5) to prevent numerical divergence in explicit Warp MPM simulations.

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] Define JSON schema specification for `PhysGaussianLLMConfig` extending PhysGaussian config with `materials`, `material_segmentation_rules`, and `boundary_conditions`.
- [x] Implement `validate_physgaussian_config(config: dict)` checking Poisson's ratio singularities (nu < 0.49).
- [x] Compute elastic P-wave speed c_p = sqrt((E * (1 - nu)) / (rho * (1 + nu) * (1 - 2 * nu))) and enforce CFL constraint (c_p * dt_sub) / dx <= 0.5.
- [x] Add unit tests verifying schema parsing and CFL guardrail exception raising for unstable parameter inputs.
