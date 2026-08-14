"""
Spherical Harmonics ↔ RGB color conversion utilities.

Consolidates the various sh_to_rgb, rgb_to_sh, color_to_sh functions
that were scattered across multiple files.
"""

import torch
import numpy as np

# The zeroth-order SH coefficient
SH_C0 = 0.28209479177387814


def sh_to_rgb(sh):
    """
    Convert SH DC component to RGB color.

    Args:
        sh: SH coefficients (numpy array or torch tensor)

    Returns:
        RGB values in [0, 1] range (same type as input)
    """
    return sh * SH_C0 + 0.5


def rgb_to_sh(rgb):
    """
    Convert RGB color to SH DC component.

    Args:
        rgb: RGB values in [0, 1] range (numpy array or torch tensor)

    Returns:
        SH DC coefficients (same type as input)
    """
    return (rgb - 0.5) / SH_C0


def color_to_sh_tensor(color):
    """
    Convert a color list/tuple to SH DC tensor.

    Args:
        color: RGB color as list, tuple, or tensor

    Returns:
        torch.Tensor of SH DC coefficients
    """
    return (torch.tensor(color) - 0.5) / SH_C0
