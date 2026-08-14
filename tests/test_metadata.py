import unittest
import torch
import numpy as np
from src.segmentation.metadata import extract_scene_metadata, SceneMetadata


class TestSceneMetadataExtractor(unittest.TestCase):
    def setUp(self):
        N = 100
        np.random.seed(42)

        xyz = np.zeros((N, 3), dtype=np.float32)
        xyz[:, 0] = np.random.uniform(-1.0, 1.0, size=N)
        xyz[:, 1] = np.random.uniform(0.0, 2.0, size=N)
        xyz[:, 2] = np.random.uniform(-0.5, 0.5, size=N)

        sh_dc = np.zeros((N, 3), dtype=np.float32)
        # Red dominant for first 50 particles, Green dominant for remaining 50
        sh_dc[:50] = (np.array([0.9, 0.2, 0.1]) - 0.5) / 0.28209479
        sh_dc[50:] = (np.array([0.1, 0.8, 0.2]) - 0.5) / 0.28209479

        scales = np.ones((N, 3), dtype=np.float32) * 0.05
        scales[:20, 1] = 0.5  # 10x anisotropy for 20 particles

        self.xyz = torch.tensor(xyz)
        self.sh_dc = torch.tensor(sh_dc)
        self.scales = torch.tensor(scales)

    def test_extract_scene_metadata(self):
        meta = extract_scene_metadata(self.xyz, self.sh_dc, self.scales)
        self.assertEqual(meta.num_particles, 100)
        self.assertAlmostEqual(meta.min_xyz[1], 0.0, delta=0.2)
        self.assertAlmostEqual(meta.max_xyz[1], 2.0, delta=0.2)
        self.assertEqual(meta.color_dominance_pct["red_dominant"], 50.0)
        self.assertEqual(meta.color_dominance_pct["green_dominant"], 50.0)
        self.assertEqual(meta.pct_anisotropic, 20.0)

    def test_format_prompt_summary(self):
        meta = extract_scene_metadata(self.xyz, self.sh_dc, self.scales)
        summary = meta.format_prompt_summary("TestScene")
        self.assertIn("TestScene", summary)
        self.assertIn("Total Particles: 100", summary)
        self.assertIn("Red-Dominant=50.0%", summary)
        self.assertIn("Highly Anisotropic (>3x): 20.0%", summary)

    def test_empty_tensor_raises_error(self):
        empty_xyz = torch.zeros((0, 3))
        empty_sh = torch.zeros((0, 3))
        with self.assertRaises(ValueError):
            extract_scene_metadata(empty_xyz, empty_sh)


if __name__ == "__main__":
    unittest.main()
