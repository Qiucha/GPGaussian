"""
LLM Segmenter Agent for PhysGaussian Multi-Material Heuristic Pipeline Selection.
Ingests SceneMetadata and object descriptions, generates structured SegmenterExecutionPlan JSON,
and executes the plan via HeuristicRegistry to produce material tag tensors.
"""

import torch
import json
from typing import Dict, Any, Tuple, Optional, Callable, List
from src.segmentation.metadata import SceneMetadata, extract_scene_metadata
from src.segmentation.heuristics import HeuristicRegistry
from src.llm.schema import (
    SegmenterExecutionPlan,
    MaterialTagDefinition,
    HeuristicStepConfig,
    validate_segmenter_execution_plan,
)

SEGMENTER_SYSTEM_PROMPT = """You are PhysGaussianSegmenter, an expert AI 3D vision and physical material segmentation assistant.
Your task is to analyze 3D Gaussian Splatting scene metadata and output a deterministic multi-heuristic segmentation execution plan in JSON adhering strictly to the SegmenterExecutionPlan schema.

### AVAILABLE HEURISTIC PRIMITIVES:
1. Chromatic & Color:
   - "color_sh": params={"target_tag": int, "condition": str} (e.g. "R > G and R > B", "G > R and G > B")
   - "hsv": params={"target_tag": int, "color_space": "hsv", "hsv_bounds": {"min_h": float, "max_h": float, "min_s": float, "min_v": float}}
   - "color_clustering": params={"target_tag": int, "n_clusters": int, "color_space": "hsv"|"rgb", "method": "kmeans"|"gmm", "selection_criteria": "darkest"|"lightest"|"highest_saturation"}

2. Spatial & Geometric:
   - "spatial_y_cutoff": params={"target_tag": int, "cutoff_y": float}
   - "spatial_z_cutoff": params={"target_tag": int, "cutoff_z": float}
   - "spatial_percentile_cutoff": params={"target_tag": int, "axis": int, "percentile": float, "comparison": "less"|"greater"}
   - "spatial_box": params={"target_tag": int, "min_x": float, "max_x": float, "min_y": float, "max_y": float, "min_z": float, "max_z": float}
   - "cylinder": params={"target_tag": int, "center_xz": [float, float], "radius": float, "y_range": [float, float]}
   - "pca_projection": params={"target_tag": int, "min_proj": float, "max_proj": float}
   - "surface_normal_curvature": params={"target_tag": int, "mode": "normal_orientation"|"curvature", "normal_axis": "x"|"y"|"z", "min_normal_dot": float}

3. Structural & Anisotropic:
   - "anisotropy_ratio": params={"target_tag": int, "threshold": float} (e.g., threshold=3.0 for needle/branch Gaussians)
   - "scale_magnitude": params={"target_tag": int, "threshold": float}
   - "local_density": params={"target_tag": int, "threshold": float, "radius": float}

4. Topological & Graph:
   - "dbscan": params={"target_tag": int, "fallback_tag": int, "eps": float, "min_samples": int}
   - "knn_smooth": params={"target_tag": int, "k_neighbors": int}
   - "superpoint_graph": params={"target_tag": int, "voxel_size": float, "min_component_ratio": float, "fallback_tag": int}

### MATERIAL GUIDELINES:
- Assign non-negative integer tag_ids (0, 1, 2...).
- Specify physical parameters: Young's Modulus E (soft: 1e4, wood/stem: 5e5, rigid base: 1e7), Poisson's Ratio nu (0.0 to 0.49), Density (kg/m^3).

### OUTPUT REQUIREMENT:
Return ONLY a valid JSON object matching SegmenterExecutionPlan:
{
  "scene_name": str,
  "materials": [ {"tag_id": int, "name": str, "E": float, "nu": float, "density": float, "material_type": str, "description": str} ],
  "steps": [ {"primitive_type": str, "params": dict, "description": str} ]
}
"""


class SegmenterAgent:
    """
    LLM Agent that orchestrates 3DGS scene metadata inspection, heuristic selection plan generation,
    and execution via HeuristicRegistry.
    """

    def __init__(
        self,
        llm_callable: Optional[Callable[[str, str], str]] = None,
        mock_llm: bool = True,
    ):
        self.llm_callable = llm_callable
        self.mock_llm = mock_llm

    def build_prompt(self, metadata: SceneMetadata, object_category: str) -> Tuple[str, str]:
        system_prompt = SEGMENTER_SYSTEM_PROMPT
        user_prompt = f"Object Category & Description: \"{object_category}\"\n\n"
        user_prompt += metadata.format_prompt_summary(scene_name=object_category)
        user_prompt += "\nSelect and configure the optimal sequence of heuristic primitives to segment this object into distinct material parts."
        return system_prompt, user_prompt

    def generate_plan(
        self,
        metadata: SceneMetadata,
        object_category: str = "generic_object",
    ) -> SegmenterExecutionPlan:
        system_prompt, user_prompt = self.build_prompt(metadata, object_category)

        if not self.mock_llm and self.llm_callable is not None:
            response_text = self.llm_callable(system_prompt, user_prompt)
            plan_dict = json.loads(response_text)
            return validate_segmenter_execution_plan(plan_dict)

        return self._rule_based_fallback_plan(metadata, object_category)

    def _rule_based_fallback_plan(
        self,
        metadata: SceneMetadata,
        object_category: str,
    ) -> SegmenterExecutionPlan:
        cat_lower = object_category.lower()

        # Rule set 1: Plant / Ficus / Tree (Pot=0, Stem=1, Leaves=2)
        if any(kw in cat_lower for kw in ["ficus", "plant", "tree", "flower", "pot"]):
            pot_cutoff = metadata.y_percentiles["p25"]
            materials = [
                MaterialTagDefinition(
                    tag_id=0, name="Pot/Base", E=1e7, nu=0.30, density=1800.0, material_type="jelly", description="Rigid base pot"
                ),
                MaterialTagDefinition(
                    tag_id=1, name="Stem/Trunk", E=5e5, nu=0.35, density=800.0, material_type="jelly", description="Flexible woody stem"
                ),
                MaterialTagDefinition(
                    tag_id=2, name="Leaves/Foliage", E=1e4, nu=0.40, density=200.0, material_type="jelly", description="Compliant soft leaves"
                ),
            ]
            steps = [
                HeuristicStepConfig(
                    primitive_type="spatial_y_cutoff",
                    params={"target_tag": 0, "cutoff_y": pot_cutoff},
                    description=f"Tag base pot particles below Y={pot_cutoff:.2f}",
                ),
                HeuristicStepConfig(
                    primitive_type="color_sh",
                    params={"target_tag": 1, "condition": "R > G and R > B"},
                    description="Tag brown woody stem particles above pot cutoff",
                ),
                HeuristicStepConfig(
                    primitive_type="hsv",
                    params={
                        "target_tag": 2,
                        "color_space": "hsv",
                        "hsv_bounds": {"min_h": 60.0, "max_h": 160.0, "min_s": 0.2},
                    },
                    description="Tag green leaf particles in foliage region",
                ),
                HeuristicStepConfig(
                    primitive_type="dbscan",
                    params={"target_tag": 1, "fallback_tag": 2, "eps": 0.3, "min_samples": 3},
                    description="Purge stray brown stem noise outliers into leaf category",
                ),
            ]

        # Rule set 2: Bread / Food / Pastry (Crust=0, Soft Crumb=1)
        elif any(kw in cat_lower for kw in ["bread", "food", "pastry", "dough", "tear_bread"]):
            materials = [
                MaterialTagDefinition(
                    tag_id=0, name="Crisp Crust", E=3e5, nu=0.30, density=500.0, material_type="jelly", description="Darker crispy outer crust"
                ),
                MaterialTagDefinition(
                    tag_id=1, name="Soft Crumb", E=3e4, nu=0.42, density=200.0, material_type="jelly", description="Soft porous interior crumb"
                ),
            ]
            steps = [
                HeuristicStepConfig(
                    primitive_type="color_clustering",
                    params={
                        "target_tag": 0,
                        "n_clusters": 2,
                        "color_space": "hsv",
                        "method": "kmeans",
                        "selection_criteria": "darkest",
                    },
                    description="Cluster dark brown crust using K-Means color clustering",
                ),
                HeuristicStepConfig(
                    primitive_type="superpoint_graph",
                    params={"target_tag": 0, "voxel_size": 0.05, "min_component_ratio": 0.02, "fallback_tag": 1},
                    description="Clean up isolated crust speckles via Superpoint RAG filtering",
                ),
            ]

        # Rule set 3: Aircraft / Plane (Fuselage=0, Wings=1)
        elif any(kw in cat_lower for kw in ["plane", "aircraft", "jet"]):
            materials = [
                MaterialTagDefinition(
                    tag_id=0, name="Rigid Fuselage", E=1e7, nu=0.28, density=2700.0, material_type="jelly", description="Main body fuselage"
                ),
                MaterialTagDefinition(
                    tag_id=1, name="Compliant Wings", E=5e5, nu=0.33, density=1200.0, material_type="jelly", description="Flexing planar wings"
                ),
            ]
            steps = [
                HeuristicStepConfig(
                    primitive_type="surface_normal_curvature",
                    params={
                        "target_tag": 1,
                        "mode": "normal_orientation",
                        "normal_axis": "y",
                        "min_normal_dot": 0.7,
                    },
                    description="Tag horizontal planar wing surfaces via surface normal orientation",
                ),
            ]

        # Rule set 4: Furniture / Chair / Table (Legs/Base=0, Cushion/Top=1)
        elif any(kw in cat_lower for kw in ["chair", "table", "furniture", "desk", "pillow"]):
            base_cutoff = metadata.y_percentiles["p25"]
            materials = [
                MaterialTagDefinition(
                    tag_id=0, name="Legs/Structure", E=1e7, nu=0.30, density=2000.0, material_type="jelly", description="Rigid frame legs"
                ),
                MaterialTagDefinition(
                    tag_id=1, name="Cushion/Seat", E=5e4, nu=0.42, density=300.0, material_type="jelly", description="Soft padded cushion"
                ),
            ]
            steps = [
                HeuristicStepConfig(
                    primitive_type="spatial_y_cutoff",
                    params={"target_tag": 0, "cutoff_y": base_cutoff},
                    description=f"Tag lower structural legs below Y={base_cutoff:.2f}",
                ),
                HeuristicStepConfig(
                    primitive_type="spatial_percentile_cutoff",
                    params={"target_tag": 1, "axis": 1, "percentile": 25.0, "comparison": "greater"},
                    description="Tag upper cushion seat region",
                ),
            ]

        # Rule set 5: General multi-part or anisotropic toy / object (Base=0, Anisotropic=1, Main=2)
        else:
            materials = [
                MaterialTagDefinition(
                    tag_id=0, name="Base/Support", E=1e7, nu=0.30, density=1500.0, description="Support base"
                ),
                MaterialTagDefinition(
                    tag_id=1, name="Elongated/Detail", E=2e5, nu=0.35, density=700.0, description="High aspect ratio detail"
                ),
                MaterialTagDefinition(
                    tag_id=2, name="MainBody", E=5e4, nu=0.40, density=400.0, description="Main compliance body"
                ),
            ]
            p20 = metadata.y_percentiles["p25"]
            steps = [
                HeuristicStepConfig(
                    primitive_type="spatial_y_cutoff",
                    params={"target_tag": 0, "cutoff_y": p20},
                    description="Tag lower support base",
                ),
                HeuristicStepConfig(
                    primitive_type="anisotropy_ratio",
                    params={"target_tag": 1, "threshold": 3.0},
                    description="Tag thin anisotropic Gaussians",
                ),
            ]

        plan_dict = {
            "scene_name": object_category,
            "materials": [m.to_dict() for m in materials],
            "steps": [s.to_dict() for s in steps],
        }
        return validate_segmenter_execution_plan(plan_dict)

    def execute_segmentation(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
        object_category: str = "generic_object",
    ) -> Tuple[torch.Tensor, SegmenterExecutionPlan]:
        """
        Full pipeline: extracts metadata, generates execution plan, executes heuristic steps,
        and returns particle material tags tensor of shape (N,) along with the SegmenterExecutionPlan.
        """
        metadata = extract_scene_metadata(xyz, sh_dc, scales)
        plan = self.generate_plan(metadata, object_category)

        current_tags = torch.zeros(len(xyz), dtype=torch.int64, device=xyz.device)
        steps_dicts = [s.to_dict() for s in plan.steps]

        final_tags = HeuristicRegistry.apply_pipeline(
            xyz, sh_dc, current_tags, steps_dicts, scales=scales
        )
        return final_tags, plan

    def build_refinement_prompt(
        self,
        metadata: SceneMetadata,
        object_category: str,
        previous_plan: SegmenterExecutionPlan,
        metrics: Any,
        iteration: int,
    ) -> Tuple[str, str]:
        system_prompt = SEGMENTER_SYSTEM_PROMPT
        user_prompt = f"Object Category & Description: \"{object_category}\" (Refinement Iteration {iteration})\n\n"
        user_prompt += metadata.format_prompt_summary(scene_name=object_category)
        user_prompt += "\nPREVIOUS CANDIDATE PLAN EXECUTION RESULT:\n"
        user_prompt += json.dumps(previous_plan.to_dict(), indent=2) + "\n\n"
        user_prompt += metrics.format_llm_feedback() + "\n\n"
        user_prompt += "Critique the previous candidate plan and diagnostic report. Adjust parameters, add superpoint_graph/color_clustering/dynamic_expression filtering steps, or fix under-segmented categories to improve segmentation quality."
        return system_prompt, user_prompt

    def execute_with_iterative_refinement(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
        object_category: str = "generic_object",
        max_iterations: int = 3,
    ) -> Tuple[torch.Tensor, SegmenterExecutionPlan, Any, List[Dict[str, Any]]]:
        """
        Executes an iterative refinement loop:
        1. Extract SceneMetadata
        2. Generate initial plan & execute
        3. Evaluate quantitative SegmentationMetrics
        4. If rating is EXCELLENT or max_iterations reached, terminate & return
        5. Else, feed diagnostic metrics back to LLM to self-correct plan and re-execute.
        """
        from src.segmentation.metrics import SegmentationEvaluator

        metadata = extract_scene_metadata(xyz, sh_dc, scales)
        plan = self.generate_plan(metadata, object_category)

        history = []
        tags = torch.zeros(len(xyz), dtype=torch.int64, device=xyz.device)
        metrics = None

        for iteration in range(1, max_iterations + 1):
            current_tags = torch.zeros(len(xyz), dtype=torch.int64, device=xyz.device)
            steps_dicts = [s.to_dict() for s in plan.steps]

            tags = HeuristicRegistry.apply_pipeline(
                xyz, sh_dc, current_tags, steps_dicts, scales=scales
            )

            mat_names = {m.tag_id: m.name for m in plan.materials}
            metrics = SegmentationEvaluator.evaluate(xyz, sh_dc, tags, material_names=mat_names)

            history.append({
                "iteration": iteration,
                "plan": plan.to_dict(),
                "metrics": metrics.to_dict(),
            })

            # Termination condition: EXCELLENT quality or last iteration
            if metrics.overall_quality_rating == "EXCELLENT" or iteration == max_iterations:
                return tags, plan, metrics, history

            # If mock_llm is True and not EXCELLENT, auto-append a superpoint_graph cleanup step if missing
            if self.mock_llm:
                step_types = [s.primitive_type for s in plan.steps]
                if "superpoint_graph" not in step_types and metrics.speckle_total_pct > 1.0:
                    plan.steps.append(
                        HeuristicStepConfig(
                            primitive_type="superpoint_graph",
                            params={"target_tag": 0, "voxel_size": 0.06, "min_component_ratio": 0.02, "fallback_tag": 1},
                            description="Auto-inserted refinement: clean up isolated speckles via Superpoint RAG filtering",
                        )
                    )
            elif self.llm_callable is not None:
                ref_sys_prompt, ref_user_prompt = self.build_refinement_prompt(
                    metadata, object_category, plan, metrics, iteration + 1
                )
                response_text = self.llm_callable(ref_sys_prompt, ref_user_prompt)
                plan_dict = json.loads(response_text)
                plan = validate_segmenter_execution_plan(plan_dict)

        return tags, plan, metrics, history
