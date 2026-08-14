"""Re-export PhysGaussian render helpers."""

from src.upstream import ensure_simulation_path

ensure_simulation_path()

from utils.render_utils import *  # noqa: F401,F403,E402
