"""
PhysGaussianLLMConfig schema definitions, mechanical property data models,
and Segmenter Agent JSON Execution Plan schemas.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class MaterialProperties:
    E: float  # Young's modulus in Pascals (Pa)
    nu: float  # Poisson's ratio (0.0 <= nu <= 0.49)
    density: float  # Mass density in kg/m^3
    material_type: str = "jelly"  # "jelly", "metal", "sand", "elastoplastic"
    yield_stress: Optional[float] = None  # For elastoplastic yield models
    friction_angle: Optional[float] = None  # For Drucker-Prager plastic models


@dataclass
class MaterialTagDefinition:
    tag_id: int
    name: str
    E: float = 1e5
    nu: float = 0.3
    density: float = 1000.0
    material_type: str = "jelly"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HeuristicStepConfig:
    primitive_type: str
    params: Dict[str, Any]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SegmenterExecutionPlan:
    scene_name: str
    materials: List[MaterialTagDefinition]
    steps: List[HeuristicStepConfig]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_name": self.scene_name,
            "materials": [m.to_dict() for m in self.materials],
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SegmenterExecutionPlan":
        materials = [
            MaterialTagDefinition(
                tag_id=m["tag_id"],
                name=m["name"],
                E=m.get("E", 1e5),
                nu=m.get("nu", 0.3),
                density=m.get("density", 1000.0),
                material_type=m.get("material_type", "jelly"),
                description=m.get("description", ""),
            )
            for m in data.get("materials", [])
        ]

        steps = [
            HeuristicStepConfig(
                primitive_type=s["primitive_type"],
                params=s.get("params", {}),
                description=s.get("description", ""),
            )
            for s in data.get("steps", [])
        ]

        return cls(
            scene_name=data.get("scene_name", "unknown_scene"),
            materials=materials,
            steps=steps,
        )


def validate_segmenter_execution_plan(plan_dict: Dict[str, Any]) -> SegmenterExecutionPlan:
    """
    Validates plan structure, primitive types, physical constraints, and tag consistency.
    """
    if "materials" not in plan_dict or not isinstance(plan_dict["materials"], list):
        raise ValueError("Segmenter execution plan must contain a 'materials' list.")

    if "steps" not in plan_dict or not isinstance(plan_dict["steps"], list):
        raise ValueError("Segmenter execution plan must contain a 'steps' list.")

    valid_primitives = {
        "color_sh",
        "hsv",
        "rgb",
        "spatial_y_cutoff",
        "spatial_z_cutoff",
        "spatial_percentile_cutoff",
        "spatial_box",
        "cylinder",
        "pca_projection",
        "anisotropy_ratio",
        "scale_magnitude",
        "local_density",
        "dbscan",
        "knn_smooth",
        "surface_normal_curvature",
        "surface_normal",
        "curvature",
        "color_clustering",
        "kmeans_color",
        "gmm_color",
        "superpoint_graph",
        "superpoint_rag",
        "spatial_connectivity",
    }

    tag_ids = set()
    for mat in plan_dict["materials"]:
        tag_id = mat.get("tag_id")
        if tag_id is None or not isinstance(tag_id, int) or tag_id < 0:
            raise ValueError(f"Invalid tag_id: {tag_id}. Must be non-negative integer.")
        tag_ids.add(tag_id)

        E = mat.get("E", 1e5)
        nu = mat.get("nu", 0.3)
        density = mat.get("density", 1000.0)

        if E <= 0:
            raise ValueError(f"Young's Modulus E must be > 0, got {E}")
        if not (0.0 <= nu <= 0.49):
            raise ValueError(f"Poisson's Ratio nu must be in [0.0, 0.49], got {nu}")
        if density <= 0:
            raise ValueError(f"Density must be > 0, got {density}")

    for step in plan_dict["steps"]:
        p_type = step.get("primitive_type")
        if p_type not in valid_primitives:
            raise ValueError(
                f"Unknown primitive_type '{p_type}'. Must be one of {sorted(list(valid_primitives))}"
            )

        params = step.get("params", {})
        target_tag = params.get("target_tag")
        if target_tag is not None and target_tag not in tag_ids:
            # Auto-register target tag if valid non-negative int
            if isinstance(target_tag, int) and target_tag >= 0:
                tag_ids.add(target_tag)

    return SegmenterExecutionPlan.from_dict(plan_dict)


@dataclass
class PhysGaussianLLMConfig:
    substep_dt: float = 1e-4
    frame_dt: float = 0.04
    frame_num: int = 100
    n_grid: int = 100
    grid_lim: float = 2.0
    g: List[float] = field(default_factory=lambda: [0.0, 0.0, -9.81])
    grid_v_damping_scale: float = 0.9999
    rpic_damping: float = 0.0
    opacity_threshold: float = 0.02
    materials: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    material_segmentation_rules: List[Dict[str, Any]] = field(default_factory=list)
    boundary_conditions: List[Dict[str, Any]] = field(default_factory=list)
