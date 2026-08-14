# 01 - LLM Schema and Few-Shot System Prompt Design

Type: research
Status: resolved
Blocked by: none

## Question

What is the optimal JSON configuration schema and few-shot prompt structure for an LLM to translate natural language motion descriptions into precise PhysGaussian material parameters (Young's Modulus E, Poisson's ratio nu, density rho) and 3D spatio-temporal force/impulse vectors?

## Answer

### Key Findings & Architectural Decision

1. **Constitum Mechanics Parameterization:**
   - Evaluates Lamé parameters $\mu = \frac{E}{2(1+\nu)}$ and $\lambda = \frac{E\nu}{(1+\nu)(1-2\nu)}$ for per-particle stress.
   - Requires Poisson's ratio $\nu \le 0.499$ to avoid numerical singularities, and computes CFL explicit time-step bounds based on P-wave speed $c_p = \sqrt{\frac{E(1-\nu)}{\rho(1+\nu)(1-2\nu)}}$.

2. **JSON Schema Extension (`PhysGaussianLLMConfig`):**
   - Extends standard PhysGaussian JSON with `materials` dictionary (mapping tags '0', '1', '2' to $E, \nu, \rho$, `material_type`, `yield_stress`), `material_segmentation_rules` array, and spatio-temporal `boundary_conditions` array (`particle_impulse`, `cuboid`, `enforce_particle_velocity_rotation`, `surface_collider`).

3. **Few-Shot Prompt Architecture with CoT Reasoning:**
   - Mandates step-by-step physical reasoning prior to JSON output: (1) Component & material tag identification, (2) Parameter scale estimation ($E$ range $10^1-10^9$ Pa), (3) Spatio-temporal boundary condition timing & spatial bounds, (4) CFL stability verification.

4. **Automated Validation Guardrail:**
   - Specified pre-simulation Python validation function (`validate_physgaussian_config`) checking $\nu < 0.49$ and $CFL = \frac{c_p \cdot \Delta t_{\text{sub}}}{\Delta x} \le 0.5$.
