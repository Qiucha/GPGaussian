import unittest
import torch
import numpy as np
import json
from src.llm.segmenter_agent import SegmenterAgent
from src.segmentation.metadata import extract_scene_metadata


class TestSegmenterAgentPipeline(unittest.TestCase):
    def setUp(self):
        N = 100
        np.random.seed(42)

        xyz = np.zeros((N, 3), dtype=np.float32)
        # Pot: y < 0.4 (30 particles)
        xyz[:30, 1] = np.random.uniform(0.0, 0.4, size=30)
        # Stem & Foliage: y >= 0.5 (70 particles)
        xyz[30:, 1] = np.random.uniform(0.5, 1.5, size=70)
        xyz[30:70, 0] = np.random.uniform(0.9, 1.1, size=40)  # Stem

        sh_dc = np.zeros((N, 3), dtype=np.float32)
        # Pot (Gray)
        sh_dc[:30] = (np.array([0.5, 0.5, 0.5]) - 0.5) / 0.28209479
        # Stem (Brown)
        sh_dc[30:70] = (np.array([0.8, 0.4, 0.2]) - 0.5) / 0.28209479
        # Foliage (Green)
        sh_dc[70:] = (np.array([0.2, 0.8, 0.2]) - 0.5) / 0.28209479

        scales = np.ones((N, 3), dtype=np.float32) * 0.05
        scales[30:70, 1] = 0.5  # Needle stem anisotropy

        self.xyz = torch.tensor(xyz)
        self.sh_dc = torch.tensor(sh_dc)
        self.scales = torch.tensor(scales)

    def test_prompt_construction(self):
        agent = SegmenterAgent(mock_llm=True)
        meta = extract_scene_metadata(self.xyz, self.sh_dc, self.scales)
        system_prompt, user_prompt = agent.build_prompt(meta, "ficus potted plant")

        self.assertIn("PhysGaussianSegmenter", system_prompt)
        self.assertIn("ficus potted plant", user_prompt)
        self.assertIn("Total Particles: 100", user_prompt)

    def test_generate_plan_plant_category(self):
        agent = SegmenterAgent(mock_llm=True)
        meta = extract_scene_metadata(self.xyz, self.sh_dc, self.scales)
        plan = agent.generate_plan(meta, "ficus potted plant")

        self.assertEqual(len(plan.materials), 3)
        self.assertEqual(plan.materials[0].name, "Pot/Base")
        self.assertTrue(len(plan.steps) >= 3)

    def test_execute_segmentation_end_to_end(self):
        agent = SegmenterAgent(mock_llm=True)
        tags, plan = agent.execute_segmentation(
            self.xyz, self.sh_dc, self.scales, object_category="ficus potted plant"
        )

        self.assertEqual(tags.shape, (100,))
        self.assertIsInstance(tags, torch.Tensor)
        # Pot (0), Stem (1), Foliage (2)
        self.assertTrue((tags[:30] == 0).all())
        self.assertTrue((tags[30:70] == 1).all())
        self.assertTrue((tags[70:] == 2).all())

    def test_custom_llm_callable_integration(self):
        custom_json_plan = {
            "scene_name": "custom_chair",
            "materials": [
                {"tag_id": 0, "name": "Legs", "E": 1e7, "nu": 0.3, "density": 1000.0},
                {"tag_id": 1, "name": "Seat", "E": 5e4, "nu": 0.4, "density": 300.0},
            ],
            "steps": [
                {
                    "primitive_type": "spatial_y_cutoff",
                    "params": {"target_tag": 0, "cutoff_y": 0.45},
                    "description": "Tag legs",
                }
            ],
        }

        def mock_llm_fn(sys_prompt, usr_prompt):
            return json.dumps(custom_json_plan)

        agent = SegmenterAgent(llm_callable=mock_llm_fn, mock_llm=False)
        meta = extract_scene_metadata(self.xyz, self.sh_dc, self.scales)
        plan = agent.generate_plan(meta, "custom_chair")

        self.assertEqual(plan.scene_name, "custom_chair")
        self.assertEqual(len(plan.materials), 2)
        self.assertEqual(plan.steps[0].primitive_type, "spatial_y_cutoff")

    def test_execute_with_iterative_refinement(self):
        agent = SegmenterAgent(mock_llm=True)
        tags, plan, metrics, history = agent.execute_with_iterative_refinement(
            self.xyz, self.sh_dc, self.scales, object_category="ficus potted plant", max_iterations=2
        )
        self.assertEqual(tags.shape, (100,))
        self.assertIsNotNone(metrics)
        self.assertTrue(len(history) >= 1)
        self.assertIn("iteration", history[0])


if __name__ == "__main__":
    unittest.main()
