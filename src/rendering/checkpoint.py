"""
Consolidated Gaussian Splatting checkpoint loading utilities.
"""

import os
import sys

from src.upstream import get_gaussian_splatting_root

_gs_path = get_gaussian_splatting_root()
if _gs_path in sys.path:
    sys.path.remove(_gs_path)
sys.path.insert(0, _gs_path)

from scene.gaussian_model import GaussianModel
from utils.system_utils import searchForMaxIteration


class PipelineParamsNoparse:
    """Same as PipelineParams but without argument parser."""

    def __init__(self):
        self.convert_SHs_python = False
        self.compute_cov3D_python = False
        self.debug = False


def load_checkpoint(model_path, sh_degree=3, iteration=-1):
    """
    Load a trained GaussianModel from a checkpoint directory.

    Args:
        model_path: Path to the trained model directory (contains point_cloud/)
        sh_degree: Spherical harmonics degree (default: 3)
        iteration: Specific iteration to load (-1 for latest)

    Returns:
        GaussianModel instance with loaded weights
    """
    checkpt_dir = os.path.join(model_path, "point_cloud")
    if iteration == -1:
        iteration = searchForMaxIteration(checkpt_dir)
    checkpt_path = os.path.join(
        checkpt_dir, f"iteration_{iteration}", "point_cloud.ply"
    )

    gaussians = GaussianModel(sh_degree)
    gaussians.load_ply(checkpt_path)
    return gaussians
