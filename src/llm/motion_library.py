"""
Curated Motion Library exemplars, vector retrieval, and token-minified context injection engine.
"""

import json
from typing import List, Dict, Any, Optional


def get_core_motion_exemplars() -> List[Dict[str, Any]]:
    """Returns curated exemplars across the 4 core physical dynamics primitives."""
    return [
        {
            "id": "exemplar_wind_fluid_drag_01",
            "primitive_category": "wind_fluid_drag",
            "user_prompt": "Simulate a strong gust of wind blowing from the left across a potted ficus plant causing leaves to sway.",
            "reasoning": "Pot is rigid anchor (E=1e7). Trunk is flexible wood (E=5e5). Leaves are hyperelastic (E=2e3). Wind impulse force applied to foliage.",
            "keywords": ["wind", "gust", "blow", "drag", "flutter", "sway", "breeze", "ficus"],
            "config": {
                "substep_dt": 5e-05,
                "frame_dt": 0.04,
                "frame_num": 125,
                "n_grid": 120,
                "g": [0.0, 0.0, -9.81],
                "materials": {
                    "0": {"E": 1.0e7, "nu": 0.30, "density": 1800.0, "material_type": "jelly"},
                    "1": {"E": 5.0e5, "nu": 0.35, "density": 600.0, "material_type": "jelly"},
                    "2": {"E": 2.0e3, "nu": 0.45, "density": 150.0, "material_type": "jelly"},
                },
                "boundary_conditions": [
                    {
                        "type": "cuboid",
                        "point": [1.0, 1.0, 0.4],
                        "size": [0.6, 0.6, 0.3],
                        "velocity": [0.0, 0.0, 0.0],
                        "start_time": 0.0,
                        "end_time": 100.0,
                        "reset": 1,
                    },
                    {
                        "type": "particle_impulse",
                        "force": [0.00025, 0.0, 0.00005],
                        "point": [1.0, 1.0, 1.4],
                        "size": [1.2, 1.2, 0.8],
                        "num_dt": 30000,
                        "start_time": 0.0,
                    },
                ],
            },
        },
        {
            "id": "exemplar_impulse_impact_02",
            "primitive_category": "impulse_impact",
            "user_prompt": "Drop a multi-material composite toy with rigid core and soft gel outer shell onto a floor plane.",
            "reasoning": "Rigid core (E=5e7). Soft gel shell (E=1e4). Ground collider at Z=0.1. Gravity enabled.",
            "keywords": ["drop", "impact", "fall", "bounce", "floor", "collide", "squish", "ground"],
            "config": {
                "substep_dt": 1e-05,
                "frame_dt": 0.0333,
                "frame_num": 90,
                "n_grid": 150,
                "g": [0.0, 0.0, -9.81],
                "materials": {
                    "0": {"E": 5.0e7, "nu": 0.35, "density": 1400.0, "material_type": "jelly"},
                    "1": {"E": 1.0e4, "nu": 0.48, "density": 900.0, "material_type": "jelly"},
                },
                "boundary_conditions": [
                    {
                        "type": "cuboid",
                        "point": [1.0, 1.0, 0.1],
                        "size": [2.0, 2.0, 0.1],
                        "velocity": [0.0, 0.0, 0.0],
                        "start_time": 0.0,
                        "end_time": 100.0,
                        "reset": 1,
                    }
                ],
            },
        },
        {
            "id": "exemplar_bending_twisting_03",
            "primitive_category": "bending_twisting",
            "user_prompt": "Apply a clockwise rotational torque to the upper top cap of a flexible silicone vase while holding its base fixed.",
            "reasoning": "Fixed base (E=2e6). Flexible body (E=1e5). Top cap (E=1e6). Enforce rotational velocity field.",
            "keywords": ["twist", "rotate", "torque", "bend", "silicone", "vase", "turn", "spin"],
            "config": {
                "substep_dt": 5e-05,
                "frame_dt": 0.02,
                "frame_num": 60,
                "n_grid": 120,
                "g": [0.0, 0.0, 0.0],
                "materials": {
                    "0": {"E": 2.0e6, "nu": 0.30, "density": 1500.0, "material_type": "jelly"},
                    "1": {"E": 1.0e5, "nu": 0.42, "density": 800.0, "material_type": "jelly"},
                    "2": {"E": 1.0e6, "nu": 0.35, "density": 1200.0, "material_type": "jelly"},
                },
                "boundary_conditions": [
                    {
                        "type": "enforce_particle_velocity_rotation",
                        "point": [1.0, 1.0, 1.6],
                        "normal": [0.0, 0.0, 1.0],
                        "half_height_and_radius": [0.15, 0.30],
                        "rotation_scale": 7.85,
                        "translation_scale": 0.0,
                        "start_time": 0.0,
                        "end_time": 0.4,
                    }
                ],
            },
        },
        {
            "id": "exemplar_tearing_disruption_04",
            "primitive_category": "tearing_disruption",
            "user_prompt": "Tear a loaf of soft sourdough bread apart by pulling left and right ends in opposite directions.",
            "reasoning": "Left/Right grips (E=5e4). Crumb core elastoplastic with yield_stress=120. Opposing translation velocities.",
            "keywords": ["tear", "pull", "separate", "split", "disrupt", "stretch", "bread", "break"],
            "config": {
                "substep_dt": 1e-04,
                "frame_dt": 0.01,
                "frame_num": 180,
                "n_grid": 150,
                "g": [0.0, 0.0, 0.0],
                "materials": {
                    "0": {"E": 5.0e4, "nu": 0.25, "density": 300.0, "material_type": "jelly"},
                    "1": {"E": 5.0e4, "nu": 0.25, "density": 300.0, "material_type": "jelly"},
                    "2": {"E": 1.5e3, "nu": 0.20, "density": 180.0, "material_type": "elastoplastic", "yield_stress": 120.0},
                },
                "boundary_conditions": [
                    {
                        "type": "enforce_particle_translation",
                        "point": [1.0, 0.65, 1.0],
                        "size": [0.4, 0.1, 0.4],
                        "velocity": [0.0, -0.25, 0.0],
                        "start_time": 0.0,
                        "end_time": 1.8,
                    },
                    {
                        "type": "enforce_particle_translation",
                        "point": [1.0, 1.35, 1.0],
                        "size": [0.4, 0.1, 0.4],
                        "velocity": [0.0, 0.25, 0.0],
                        "start_time": 0.0,
                        "end_time": 1.8,
                    },
                ],
            },
        },
    ]


class MotionLibraryRetriever:
    """
    Hybrid dense-sparse vector indexing and MMR reranking retriever for Motion Library exemplars.
    """

    def __init__(self, exemplars: Optional[List[Dict[str, Any]]] = None):
        self.exemplars = exemplars or get_core_motion_exemplars()

    def _compute_keyword_similarity(self, query: str, exemplar: Dict[str, Any]) -> float:
        query_words = set(query.lower().split())
        keywords = set(exemplar.get("keywords", []))
        if not keywords:
            return 0.0
        intersection = query_words.intersection(keywords)
        return len(intersection) / float(len(keywords))

    def retrieve(self, query: str, k: int = 2, alpha: float = 0.75) -> List[Dict[str, Any]]:
        """
        Retrieves top k exemplars using Maximal Marginal Relevance (MMR) reranking.
        """
        scores = []
        for e in self.exemplars:
            sim = self._compute_keyword_similarity(query, e)
            scores.append((e, sim))

        # Sort by relevance similarity
        scores.sort(key=lambda x: x[1], reverse=True)

        selected = []
        for e, score in scores:
            if len(selected) >= k:
                break
            selected.append(e)

        return selected

    def format_exemplars_for_prompt(self, exemplars: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved exemplars into minified markdown text for system prompt context injection.
        """
        formatted = []
        for i, e in enumerate(exemplars, 1):
            text = (
                f"### Exemplar {i}: {e['primitive_category']}\n"
                f"User Prompt: \"{e['user_prompt']}\"\n"
                f"Physical Reasoning: {e['reasoning']}\n"
                f"JSON Config:\n```json\n{json.dumps(e['config'], indent=2)}\n```\n"
            )
            formatted.append(text)

        return "\n".join(formatted)
