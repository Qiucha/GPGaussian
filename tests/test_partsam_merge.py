import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch


class TestPartsamMergeLift(unittest.TestCase):
    def test_highest_chosen_iou_wins_on_overlap(self):
        from src.segmentation.partsam.merge import TAG_LEAVES, TAG_POT, TAG_TRUNK, merge_masks

        pot = np.array([1, 1, 1, 0, 0, 0], dtype=np.uint8)
        trunk = np.array([0, 0, 1, 1, 0, 0], dtype=np.uint8)
        leaves = np.array([0, 0, 0, 0, 1, 0], dtype=np.uint8)
        merged = merge_masks(
            pot,
            trunk,
            leaves,
            {"pot": 0.4, "trunk": 0.9, "leaves": 0.2},
        )
        self.assertEqual(merged.dtype, np.int32)
        np.testing.assert_array_equal(
            merged,
            np.array([TAG_POT, TAG_POT, TAG_TRUNK, TAG_TRUNK, TAG_LEAVES, 0], dtype=np.int32),
        )

    def test_smaller_mask_wins_on_iou_tie(self):
        from src.segmentation.partsam.merge import TAG_POT, TAG_TRUNK, merge_masks

        pot = np.array([1, 1, 1, 0], dtype=np.uint8)
        trunk = np.array([0, 1, 0, 1], dtype=np.uint8)
        leaves = np.zeros(4, dtype=np.uint8)
        merged = merge_masks(
            pot,
            trunk,
            leaves,
            {"pot": 0.5, "trunk": 0.5, "leaves": 0.1},
        )
        self.assertEqual(int(merged[1]), TAG_TRUNK)
        self.assertEqual(int(merged[0]), TAG_POT)

    def test_unlabeled_samples_do_not_vote_nn_lifts_every_gaussian(self):
        from src.segmentation.partsam.merge import TAG_LEAVES, TAG_POT, TAG_TRUNK, lift_tags

        sample_xyz = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0]],
            dtype=np.float32,
        )
        merged = np.array([TAG_POT, TAG_TRUNK, 0, TAG_LEAVES], dtype=np.int32)
        gaussians = np.array(
            [
                [0.01, 0.0, 0.0],
                [0.99, 0.0, 0.0],
                [2.4, 0.0, 0.0],
                [10.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        )
        lifted = lift_tags(gaussians, sample_xyz, merged)
        self.assertEqual(lifted.dtype, np.int32)
        self.assertEqual(lifted.shape, (4,))
        np.testing.assert_array_equal(
            lifted,
            np.array([TAG_POT, TAG_TRUNK, TAG_LEAVES, TAG_LEAVES], dtype=np.int32),
        )

    def test_write_material_tags_int32_ids(self):
        from src.segmentation.partsam.merge import TAG_POT, TAG_TRUNK, write_material_tags

        tags = np.array([TAG_POT, TAG_TRUNK, TAG_POT], dtype=np.int32)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "material_tags.pt"
            write_material_tags(path, tags)
            loaded = torch.load(path, weights_only=True)
        self.assertEqual(loaded.dtype, torch.int32)
        self.assertEqual(tuple(loaded.shape), (3,))
        self.assertTrue(torch.equal(loaded, torch.tensor([1, 2, 1], dtype=torch.int32)))


if __name__ == "__main__":
    unittest.main()
