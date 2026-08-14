"""Camera helpers: PhysGaussian utils.camera_view_utils plus gt_depth for FlashSplat-compatible Camera."""

from src.upstream import ensure_simulation_path

ensure_simulation_path()

from utils.camera_view_utils import (  # noqa: E402
    generate_camera_rotation_matrix,
    generate_local_coord,
    get_camera_position_and_rotation,
    get_current_radius_azimuth_and_elevation,
    get_point_on_sphere,
)
from utils.camera_view_utils import get_camera_view as _upstream_get_camera_view  # noqa: E402


def get_camera_view(*args, **kwargs):
    cam = _upstream_get_camera_view(*args, **kwargs)
    if not hasattr(cam, "gt_depth"):
        cam.gt_depth = None
    return cam
