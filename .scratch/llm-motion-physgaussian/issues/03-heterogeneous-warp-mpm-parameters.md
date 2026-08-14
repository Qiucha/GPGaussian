# 03 — Heterogeneous Warp MPM Parameter Array Constructor

**What to build:**
Extends `src/simulation/config.py` and `runner.py` to parse `PhysGaussianLLMConfig` and `material_tags.pt`, constructing 1D per-particle Warp CUDA arrays (`mu`, `lambda`, `density`) for MPM stress evaluation.

**Blocked by:** 01 — PhysGaussianLLMConfig Schema & CFL Validation Guardrail, 02 — Hybrid Point-Cloud Material Segmentation Engine

**Status:** resolved

- [x] Modify `src/simulation/config.py` to load per-particle `material_tags.pt` array of shape (N,).
- [x] Calculate per-particle Lamé parameters mu_p = E_p / (2 * (1 + nu_p)) and lambda_p = (E_p * nu_p) / ((1 + nu_p) * (1 - 2 * nu_p)).
- [x] Initialize and allocate 1D PyTorch tensors and Nvidia Warp arrays (`wp.array(dtype=wp.float32)`) for `mu`, `lambda`, and `density`.
- [x] Update Warp CUDA stress kernels in `mpm_solver_warp.py` to index particle parameters by particle ID `p`.
- [x] Add integration tests verifying Warp array dimensions (N,) and correct Lamé value mapping per material tag.
