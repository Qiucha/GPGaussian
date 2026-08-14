import unittest
import torch
import numpy as np


class TestHeterogeneousWarpParams(unittest.TestCase):
    def setUp(self):
        self.materials_config = {
            "0": {"E": 1.0e7, "nu": 0.30, "density": 1800.0},
            "1": {"E": 5.0e5, "nu": 0.35, "density": 600.0},
            "2": {"E": 2.0e3, "nu": 0.45, "density": 150.0},
        }
        # 100 particles: 30 of tag 0, 40 of tag 1, 30 of tag 2
        N = 100
        tags = np.zeros(N, dtype=np.int64)
        tags[30:70] = 1
        tags[70:] = 2
        self.material_tags = torch.tensor(tags)

    def test_lame_parameter_computation(self):
        from simulation.lame_params import compute_per_particle_lame_params

        mu, lam, density = compute_per_particle_lame_params(
            self.materials_config, self.material_tags
        )

        self.assertEqual(mu.shape, (100,))
        self.assertEqual(lam.shape, (100,))
        self.assertEqual(density.shape, (100,))

        # Check Tag 0: E=1e7, nu=0.3 -> mu = 1e7 / (2 * 1.3) = 3846153.85
        # lam = (1e7 * 0.3) / (1.3 * 0.4) = 5769230.77
        expected_mu_0 = 1.0e7 / (2.0 * 1.3)
        expected_lam_0 = (1.0e7 * 0.3) / (1.3 * 0.4)
        self.assertAlmostEqual(mu[0].item(), expected_mu_0, places=-1)
        self.assertAlmostEqual(lam[0].item(), expected_lam_0, places=-1)
        self.assertAlmostEqual(density[0].item(), 1800.0, places=1)

        # Check Tag 1: E=5e5, nu=0.35 -> density=600.0
        self.assertAlmostEqual(density[40].item(), 600.0, places=1)
        # Check Tag 2: E=2e3, nu=0.45 -> density=150.0
        self.assertAlmostEqual(density[80].item(), 150.0, places=1)


if __name__ == "__main__":
    unittest.main()
