"""
Per-particle Lamé parameter calculation module for multi-material PhysGaussian MPM simulations.
"""

import torch
from typing import Dict, Any, Tuple


def compute_per_particle_lame_params(
    materials_config: Dict[str, Dict[str, Any]],
    material_tags: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Computes per-particle Lamé parameters (mu, lambda) and density arrays from material config and tags tensor.

    Args:
        materials_config: Dictionary mapping material tag strings ('0', '1', '2') to E, nu, density.
        material_tags: Int64 1D PyTorch tensor of shape (N,) containing material tag IDs per particle.

    Returns:
        Tuple of (mu, lambda, density) 1D float32 PyTorch tensors of shape (N,).
    """
    N = material_tags.shape[0]
    device = material_tags.device

    mu_array = torch.zeros(N, dtype=torch.float32, device=device)
    lambda_array = torch.zeros(N, dtype=torch.float32, device=device)
    density_array = torch.zeros(N, dtype=torch.float32, device=device)

    # Precompute Lamé parameters per tag
    lame_lookup = {}
    for tag_str, props in materials_config.items():
        tag_id = int(tag_str)
        E = float(props.get("E", 1e5))
        nu = float(props.get("nu", 0.3))
        rho = float(props.get("density", 1000.0))

        mu = E / (2.0 * (1.0 + nu))
        lam = (E * nu) / ((1.0 + nu) * (1.0 - 2.0 * nu))

        lame_lookup[tag_id] = (mu, lam, rho)

    # Assign values per particle tag
    for tag_id, (mu_val, lam_val, rho_val) in lame_lookup.items():
        mask = material_tags == tag_id
        mu_array[mask] = mu_val
        lambda_array[mask] = lam_val
        density_array[mask] = rho_val

    # If any particles were unassigned (tags not in config), assign default tag '0' properties
    unassigned_mask = density_array == 0.0
    if unassigned_mask.any() and 0 in lame_lookup:
        default_mu, default_lam, default_rho = lame_lookup[0]
        mu_array[unassigned_mask] = default_mu
        lambda_array[unassigned_mask] = default_lam
        density_array[unassigned_mask] = default_rho

    return mu_array, lambda_array, density_array
