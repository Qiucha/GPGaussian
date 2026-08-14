import sys
import unittest

import torch

_TORKIT_KEYS = (
    "torkit3d",
    "torkit3d.nn",
    "torkit3d.nn.functional",
    "torkit3d.ops",
    "torkit3d.ops.sample_farthest_points",
    "torkit3d.ops.chamfer_distance",
)


class TestPartsamFpsStandIn(unittest.TestCase):
    def setUp(self):
        self.points = torch.tensor(
            [[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]]
        )

    def tearDown(self):
        for key in _TORKIT_KEYS:
            sys.modules.pop(key, None)



class TestPartsamFpsStandIn(unittest.TestCase):
    def setUp(self):
        self.points = torch.tensor(
            [[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]]
        )

    def test_first_centroid_is_index_zero(self):
        from src.segmentation.partsam.fps import sample_farthest_points

        idx = sample_farthest_points(self.points, num_samples=3)
        self.assertEqual(idx[0, 0].item(), 0)

    def test_two_calls_return_the_same_indices(self):
        from src.segmentation.partsam.fps import sample_farthest_points

        a = sample_farthest_points(self.points, num_samples=3)
        b = sample_farthest_points(self.points, num_samples=3)
        self.assertTrue(torch.equal(a, b))

    def test_install_exposes_torkit3d_fps_with_seed_zero(self):
        from src.segmentation.partsam.fps import install

        install()
        from torkit3d.ops.sample_farthest_points import sample_farthest_points

        idx = sample_farthest_points(self.points, num_samples=3)
        self.assertEqual(idx[0, 0].item(), 0)


if __name__ == "__main__":
    unittest.main()
