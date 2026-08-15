import tempfile
import unittest
from pathlib import Path

import numpy as np


class TestPartsamSurfacePersist(unittest.TestCase):
    def test_fixture_writer_round_trips_sample_100k_keys_dtypes_and_shapes(self):
        from src.segmentation.partsam.surface import load_sample_100k, write_sample_100k

        n = 8
        coords = np.arange(n * 3, dtype=np.float32).reshape(n, 3)
        normals = np.tile(np.array([0.0, 0.0, 1.0], dtype=np.float32), (n, 1))
        colors = np.array(
            [[10, 20, 30], [40, 50, 60], [70, 80, 90], [100, 110, 120],
             [130, 140, 150], [160, 170, 180], [190, 200, 210], [220, 230, 240]],
            dtype=np.uint8,
        )
        point_to_face = np.arange(n, dtype=np.int32)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample_100k.npz"
            write_sample_100k(path, coords, normals, colors, point_to_face)
            sample = load_sample_100k(path)

        self.assertEqual(
            set(sample.keys()),
            {"coords", "normals", "colors", "point_to_face", "sample_id"},
        )
        self.assertEqual(sample["coords"].shape, (n, 3))
        self.assertEqual(sample["normals"].shape, (n, 3))
        self.assertEqual(sample["colors"].shape, (n, 3))
        self.assertEqual(sample["point_to_face"].shape, (n,))
        self.assertEqual(sample["coords"].dtype, np.float32)
        self.assertEqual(sample["normals"].dtype, np.float32)
        self.assertEqual(sample["colors"].dtype, np.uint8)
        self.assertEqual(sample["point_to_face"].dtype, np.int32)
        np.testing.assert_array_equal(sample["coords"], coords)
        np.testing.assert_array_equal(sample["colors"], colors)
        np.testing.assert_array_equal(sample["point_to_face"], point_to_face)

    def test_stage_surface_skips_when_sample_npz_already_exists(self):
        from src.segmentation.partsam.surface import run_stage_surface, write_sample_100k

        n = 4
        coords = np.ones((n, 3), dtype=np.float32)
        normals = np.zeros((n, 3), dtype=np.float32)
        colors = np.full((n, 3), 7, dtype=np.uint8)
        point_to_face = np.zeros(n, dtype=np.int32)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            path = out / "sample_100k.npz"
            write_sample_100k(path, coords, normals, colors, point_to_face)
            before = path.read_bytes()
            returned = run_stage_surface(
                model_path=Path(tmp) / "missing_checkpoint",
                output_dir=out,
            )
            self.assertEqual(returned, path)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
