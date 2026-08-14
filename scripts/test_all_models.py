"""
Automated Multi-Model Evaluation Script for PhysGaussian Segmenter Agent.
Tests the multi-heuristic agent segmentation pipeline across all trained 3DGS models in data/models/.
"""

import os
import sys
import torch
import numpy as np

# Ensure project root is in sys.path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.rendering.checkpoint import load_checkpoint
from src.segmentation.metadata import extract_scene_metadata
from src.llm.segmenter_agent import SegmenterAgent
from src.llm.validator import validate_physgaussian_config


def evaluate_model(model_name: str, model_dir: str):
    print(f"\n" + "=" * 70)
    print(f"  EVALUATING MODEL: {model_name}")
    print("=" * 70)

    try:
        gaussians = load_checkpoint(model_dir)
    except Exception as e:
        print(f"❌ Failed to load checkpoint for {model_name}: {e}")
        return

    xyz = gaussians._xyz.detach()
    sh_dc = gaussians._features_dc.detach().squeeze(1) if gaussians._features_dc.dim() == 3 else gaussians._features_dc.detach()
    scales = gaussians._scaling.detach()

    print(f"Loaded {len(xyz)} Gaussians from {model_name}.")

    # Extract Metadata
    metadata = extract_scene_metadata(xyz, sh_dc, scales)
    print("\n--- Extracted Scene Metadata ---")
    print(metadata.format_prompt_summary(scene_name=model_name))

    # Segmenter Agent Pipeline
    agent = SegmenterAgent(mock_llm=True)
    tags, plan = agent.execute_segmentation(xyz, sh_dc, scales, object_category=model_name)

    print("--- Generated Segmenter Execution Plan ---")
    print(f"Scene: {plan.scene_name}")
    print(f"Materials ({len(plan.materials)}):")
    for mat in plan.materials:
        print(f"  Tag {mat.tag_id} [{mat.name}]: E={mat.E:.1e} Pa, nu={mat.nu:.2f}, density={mat.density:.1f} kg/m^3 ({mat.description})")

    print(f"Heuristic Pipeline Steps ({len(plan.steps)}):")
    for idx, step in enumerate(plan.steps):
        print(f"  Step {idx+1}: {step.primitive_type} -> params={step.params} ({step.description})")

    # Particle Tag Distribution Breakdown
    print("\n--- Particle Tag Assignment Breakdown ---")
    unique_tags, counts = torch.unique(tags, return_counts=True)
    for tag_id, count in zip(unique_tags.tolist(), counts.tolist()):
        pct = (count / len(xyz)) * 100.0
        mat_name = next((m.name for m in plan.materials if m.tag_id == tag_id), "Unknown")
        print(f"  Tag {tag_id} ({mat_name}): {count:,} Gaussians ({pct:.2f}%)")

    # Build and validate simulation config
    materials_dict = {
        str(mat.tag_id): {
            "E": mat.E,
            "nu": mat.nu,
            "density": mat.density,
            "material_type": mat.material_type,
        }
        for mat in plan.materials
    }

    sim_config = {
        "substep_dt": 5e-05,
        "frame_dt": 0.04,
        "frame_num": 100,
        "n_grid": 100,
        "grid_lim": 2.0,
        "g": [0.0, 0.0, -9.81],
        "materials": materials_dict,
    }

    is_valid, msg = validate_physgaussian_config(sim_config)
    if is_valid:
        print(f"\n✅ PhysGaussian MPM Config Verification Passed! ({msg})")
    else:
        print(f"\n❌ PhysGaussian MPM Config Verification Failed: {msg}")


def main():
    models_root = os.path.join(_project_root, "data", "models")
    if not os.path.exists(models_root):
        print(f"Error: {models_root} directory not found.")
        return

    model_dirs = [
        d for d in os.listdir(models_root)
        if os.path.isdir(os.path.join(models_root, d)) and os.path.exists(os.path.join(models_root, d, "point_cloud"))
    ]

    model_dirs.sort()
    print(f"Found {len(model_dirs)} trained 3DGS models: {model_dirs}")

    for m_name in model_dirs:
        m_path = os.path.join(models_root, m_name)
        evaluate_model(m_name, m_path)


if __name__ == "__main__":
    main()
