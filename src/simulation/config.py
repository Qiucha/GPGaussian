"""Phys4DGS overlay on PhysGaussian JSON decode: heterogeneous `materials` map."""

import json

from src.upstream import ensure_simulation_path

ensure_simulation_path()

from mpm_solver_warp.mpm_solver_warp import MPM_Simulator_WARP  # noqa: E402,F401
from utils.decode_param import (  # noqa: E402
    decode_param_json as _upstream_decode_param_json,
    set_boundary_conditions,
)


def decode_param_json(json_file):
    material_params, bc_params, time_params, preprocessing_params, camera_params = (
        _upstream_decode_param_json(json_file)
    )
    with open(json_file) as f:
        sim_params = json.load(f)
    if "materials" in sim_params:
        material_params["materials"] = {
            int(k): v for k, v in sim_params["materials"].items()
        }
    else:
        material_params.setdefault("materials", None)
    return material_params, bc_params, time_params, preprocessing_params, camera_params
