"""
Validation guardrails and stability protocols for PhysGaussian simulation configurations.
"""

import math
from typing import Tuple, Dict, Any


def calculate_p_wave_speed(E: float, nu: float, density: float) -> float:
    """
    Computes elastic P-wave speed:
    c_p = sqrt( (E * (1 - nu)) / (rho * (1 + nu) * (1 - 2*nu)) )
    """
    if nu >= 0.499:
        raise ValueError(f"Poisson ratio nu={nu} causes numerical singularity (must be < 0.49).")
    if density <= 0:
        raise ValueError(f"Density must be positive, got density={density}.")
    if E < 0:
        raise ValueError(f"Young's Modulus E must be non-negative, got E={E}.")

    numerator = E * (1.0 - nu)
    denominator = density * (1.0 + nu) * (1.0 - 2.0 * nu)
    return math.sqrt(numerator / denominator)


def validate_physgaussian_config(config: Dict[str, Any], max_cfl: float = 0.5) -> Tuple[bool, str]:
    """
    Validates a PhysGaussian configuration object against physical stability and CFL criteria.

    Args:
        config: Simulation configuration dictionary.
        max_cfl: Maximum allowable CFL ratio (default 0.5).

    Returns:
        Tuple of (is_valid: bool, status_message: str)

    Raises:
        ValueError: If Poisson ratio is singular or CFL stability condition is violated.
    """
    substep_dt = config.get("substep_dt", 1e-4)
    n_grid = config.get("n_grid", 100)
    grid_lim = config.get("grid_lim", 2.0)
    dx = (2.0 * grid_lim) / float(n_grid)

    materials = config.get("materials", {})
    if not materials:
        # Fallback to top-level scalar material properties if multi-material map absent
        E_global = config.get("E", 1e5)
        nu_global = config.get("nu", 0.3)
        rho_global = config.get("density", 1000.0)
        materials = {"0": {"E": E_global, "nu": nu_global, "density": rho_global}}

    for tag, mat in materials.items():
        nu = mat.get("nu", 0.3)
        if nu >= 0.499:
            raise ValueError(f"Material tag '{tag}': Poisson ratio nu={nu} causes numerical singularity (must be < 0.49).")

        E = mat.get("E", 1e5)
        rho = mat.get("density", 1000.0)

        c_p = calculate_p_wave_speed(E, nu, rho)
        cfl_number = (c_p * substep_dt) / dx

        if cfl_number > max_cfl:
            suggested_dt = (max_cfl * dx) / c_p
            raise ValueError(
                f"CFL condition violated for material tag '{tag}'! "
                f"Wave speed c_p={c_p:.1f} m/s, CFL={cfl_number:.3f} > {max_cfl}. "
                f"Reduce substep_dt to <= {suggested_dt:.2e} s."
            )

    return True, "Config is valid and satisfies CFL stability bounds."
