"""Locate gitignored PhysGaussian / FlashSplat / PartSAM clones. Do not vendor their sources in-tree."""

from __future__ import annotations

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_PHYSGAUSSIAN_MARKERS = ("gs_simulation.py", "mpm_solver_warp")


def project_root() -> str:
    return _PROJECT_ROOT


def _first_existing(candidates: list[str]) -> str | None:
    for path in candidates:
        if path and os.path.isdir(path):
            return os.path.abspath(path)
    return None


def get_physgaussian_root() -> str:
    """PHYSGAUSSIAN_ROOT, then third_party/PhysGaussian, then local leftover clone."""
    found = _first_existing(
        [
            os.environ.get("PHYSGAUSSIAN_ROOT", ""),
            os.path.join(_PROJECT_ROOT, "third_party", "PhysGaussian"),
            os.path.join(_PROJECT_ROOT, ".trash", "PhysGaussian"),
        ]
    )
    if found is None or not all(
        os.path.exists(os.path.join(found, m)) for m in _PHYSGAUSSIAN_MARKERS
    ):
        raise FileNotFoundError(
            "PhysGaussian clone not found. Set PHYSGAUSSIAN_ROOT or clone:\n"
            "  git clone --recurse-submodules "
            "https://github.com/XPandora/PhysGaussian.git third_party/PhysGaussian"
        )
    return found


def get_gaussian_splatting_root() -> str:
    """3DGS tree used for simulation: PhysGaussian submodule, else a dedicated clone."""
    pg = None
    try:
        pg = get_physgaussian_root()
    except FileNotFoundError:
        pg = None
    if pg:
        nested = os.path.join(pg, "gaussian-splatting")
        if os.path.isdir(os.path.join(nested, "scene")):
            return nested
    found = _first_existing(
        [
            os.environ.get("GAUSSIAN_SPLATTING_ROOT", ""),
            os.path.join(_PROJECT_ROOT, "third_party", "gaussian-splatting"),
            os.path.join(_PROJECT_ROOT, "vendor", "gaussian-splatting"),
        ]
    )
    if found is None:
        raise FileNotFoundError(
            "gaussian-splatting not found. Clone PhysGaussian with --recurse-submodules "
            "or set GAUSSIAN_SPLATTING_ROOT."
        )
    return found


def get_flashsplat_root() -> str:
    found = _first_existing(
        [
            os.environ.get("FLASHSPLAT_ROOT", ""),
            os.path.join(_PROJECT_ROOT, "third_party", "FlashSplat"),
            os.path.join(_PROJECT_ROOT, "vendor", "FlashSplat"),
        ]
    )
    if found is None or not os.path.isfile(
        os.path.join(found, "gaussian_renderer", "__init__.py")
    ):
        raise FileNotFoundError(
            "FlashSplat clone not found. Set FLASHSPLAT_ROOT or clone:\n"
            "  git clone --recurse-submodules "
            "https://github.com/florinshen/FlashSplat.git third_party/FlashSplat"
        )
    return found


def get_partsam_root() -> str:
    """PARTSAM_ROOT, then third_party/PartSAM. Weights stay in that clone’s pretrained/."""
    found = _first_existing(
        [
            os.environ.get("PARTSAM_ROOT", ""),
            os.path.join(_PROJECT_ROOT, "third_party", "PartSAM"),
        ]
    )
    if found is None or not os.path.isdir(os.path.join(found, "partfield")):
        raise FileNotFoundError(
            "PartSAM clone not found. Set PARTSAM_ROOT or clone:\n"
            "  git clone https://github.com/czvvd/PartSAM.git third_party/PartSAM"
        )
    return found


def ensure_simulation_path() -> str:
    """Put PhysGaussian root then its gaussian-splatting on sys.path (simulation only)."""
    root = get_physgaussian_root()
    gs = get_gaussian_splatting_root()
    # PhysGaussian first so mpm_solver_warp / particle_filling resolve.
    for path in (gs, root):
        if path in sys.path:
            sys.path.remove(path)
    sys.path.insert(0, root)
    sys.path.insert(1, gs)
    return root
