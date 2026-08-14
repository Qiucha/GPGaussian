import unittest
import torch
import numpy as np
from src.llm.segmenter_agent import SegmenterAgent
from src.segmentation.metadata import extract_scene_metadata
from src.llm.validator import validate_physgaussian_config


class TestMultiModelVerificationBenchmark(unittest.TestCase):
    def setUp(self):
        np.random.seed(123)

        # ----------------------------------------------------
        # Scene 1: Potted Plant (Ficus) - 150 particles
        # ----------------------------------------------------
        N1 = 150
        xyz1 = np.zeros((N1, 3), dtype=np.float32)
        xyz1[:40, 1] = np.random.uniform(0.0, 0.35, size=40)  # Pot
        xyz1[40:90, 1] = np.random.uniform(0.4, 1.2, size=50)
        xyz1[40:90, 0] = np.random.uniform(0.9, 1.1, size=50)  # Stem
        xyz1[90:, 1] = np.random.uniform(1.0, 2.0, size=60)  # Foliage

        sh_dc1 = np.zeros((N1, 3), dtype=np.float32)
        sh_dc1[:40] = (np.array([0.5, 0.5, 0.5]) - 0.5) / 0.28209479  # Pot
        sh_dc1[40:90] = (np.array([0.8, 0.4, 0.2]) - 0.5) / 0.28209479  # Brown stem
        sh_dc1[90:] = (np.array([0.2, 0.8, 0.2]) - 0.5) / 0.28209479  # Green foliage

        scales1 = np.ones((N1, 3), dtype=np.float32) * 0.05
        scales1[40:90, 1] = 0.4  # Anisotropic stem

        self.scene_plant = (torch.tensor(xyz1), torch.tensor(sh_dc1), torch.tensor(scales1))

        # ----------------------------------------------------
        # Scene 2: Office Chair (Furniture) - 120 particles
        # ----------------------------------------------------
        N2 = 120
        xyz2 = np.zeros((N2, 3), dtype=np.float32)
        xyz2[:30, 1] = np.random.uniform(0.0, 0.3, size=30)  # 30 particles (25%) metal legs
        xyz2[30:, 1] = np.random.uniform(0.4, 1.2, size=90)  # 90 particles (75%) cushion seat

        sh_dc2 = np.zeros((N2, 3), dtype=np.float32)
        sh_dc2[:30] = (np.array([0.1, 0.1, 0.1]) - 0.5) / 0.28209479  # Black metal
        sh_dc2[30:] = (np.array([0.7, 0.2, 0.2]) - 0.5) / 0.28209479  # Red fabric

        scales2 = np.ones((N2, 3), dtype=np.float32) * 0.04

        self.scene_chair = (torch.tensor(xyz2), torch.tensor(sh_dc2), torch.tensor(scales2))

        # ----------------------------------------------------
        # Scene 3: Composite Toy (Anisotropic Object) - 100 particles
        # ----------------------------------------------------
        N3 = 100
        xyz3 = np.zeros((N3, 3), dtype=np.float32)
        xyz3[:25, 1] = np.random.uniform(0.0, 0.2, size=25)  # 25 particles (25%) base
        xyz3[25:, 1] = np.random.uniform(0.3, 1.2, size=75)

        sh_dc3 = np.zeros((N3, 3), dtype=np.float32)
        sh_dc3[:25] = (np.array([0.3, 0.3, 0.7]) - 0.5) / 0.28209479
        sh_dc3[25:] = (np.array([0.9, 0.9, 0.1]) - 0.5) / 0.28209479

        scales3 = np.ones((N3, 3), dtype=np.float32) * 0.03
        scales3[25:55, 0] = 0.3  # Needle whiskers anisotropy (>3x)

        self.scene_toy = (torch.tensor(xyz3), torch.tensor(sh_dc3), torch.tensor(scales3))

    def test_multi_model_segmentation_generalization(self):
        agent = SegmenterAgent(mock_llm=True)

        # Model 1: Plant
        xyz1, sh1, s1 = self.scene_plant
        tags1, plan1 = agent.execute_segmentation(xyz1, sh1, s1, object_category="ficus potted plant")
        self.assertEqual(len(tags1), 150)
        self.assertTrue((tags1[:40] == 0).all())  # Pot
        self.assertTrue((tags1[40:90] == 1).all())  # Stem
        self.assertTrue((tags1[90:] == 2).all())  # Foliage

        # Model 2: Chair
        xyz2, sh2, s2 = self.scene_chair
        tags2, plan2 = agent.execute_segmentation(xyz2, sh2, s2, object_category="office chair")
        self.assertEqual(len(tags2), 120)
        self.assertTrue((tags2[:30] == 0).all())  # Metal legs
        self.assertTrue((tags2[30:] == 1).all())  # Cushion

        # Model 3: Toy
        xyz3, sh3, s3 = self.scene_toy
        tags3, plan3 = agent.execute_segmentation(xyz3, sh3, s3, object_category="composite toy")
        self.assertEqual(len(tags3), 100)
        self.assertTrue((tags3[:25] == 0).all())  # Base
        self.assertTrue((tags3[25:55] == 1).all())  # Whiskers anisotropy detail

    def test_mpm_config_generation_and_cfl_validation(self):
        agent = SegmenterAgent(mock_llm=True)
        xyz1, sh1, s1 = self.scene_plant
        tags1, plan1 = agent.execute_segmentation(xyz1, sh1, s1, object_category="ficus potted plant")

        # Build PhysGaussian JSON config from SegmenterExecutionPlan
        materials_dict = {}
        for mat in plan1.materials:
            materials_dict[str(mat.tag_id)] = {
                "E": mat.E,
                "nu": mat.nu,
                "density": mat.density,
                "material_type": mat.material_type,
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

        # Verify CFL & stability guardrails
        is_valid, msg = validate_physgaussian_config(sim_config)
        self.assertTrue(is_valid)
        self.assertIn("Config is valid", msg)


if __name__ == "__main__":
    unittest.main()
