import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.segmentation.partsam.surface import write_sample_100k


def _complete_clicks(pot, trunk, leaves):
    return {
        "frame": "world",
        "source": "100k sample before ValDataset bbox-normalize",
        "groups": {
            "pot": {"positives": [list(pot)], "negatives": []},
            "trunk": {"positives": [list(trunk)], "negatives": []},
            "leaves": {"positives": [list(leaves)], "negatives": []},
        },
    }


def _synthetic_cloud():
    rng = np.random.default_rng(0)
    n_bg = 400
    xyz = np.vstack(
        [
            np.column_stack([rng.normal(0.0, 0.25, 40), rng.normal(0.0, 0.25, 40), np.full(40, 0.02)]),
            np.column_stack([rng.normal(0.0, 0.015, 50), rng.normal(0.0, 0.015, 50), np.full(50, 0.38)]),
            np.column_stack([rng.normal(0.0, 0.3, 40), rng.normal(0.0, 0.3, 40), np.full(40, 0.95)]),
            np.column_stack([rng.normal(0.0, 0.4, n_bg), rng.normal(0.0, 0.4, n_bg), np.linspace(0.0, 1.0, n_bg)]),
        ]
    ).astype(np.float32)
    colors = np.vstack(
        [
            np.full((40, 3), 40, dtype=np.uint8),
            np.tile(np.array([110, 90, 70], dtype=np.uint8), (50, 1)),
            np.tile(np.array([40, 140, 40], dtype=np.uint8), (40, 1)),
            np.full((n_bg, 3), 128, dtype=np.uint8),
        ]
    )
    return xyz, colors


class TestPartsamClicks(unittest.TestCase):
    def test_validate_rejects_empty_group_positives(self):
        from src.segmentation.partsam.clicks import validate_clicks

        doc = _complete_clicks([0, 0, 0], [0, 0, 1], [0, 0, 2])
        doc["groups"]["pot"]["positives"] = []
        with self.assertRaises(ValueError):
            validate_clicks(doc)

    def test_validate_rejects_missing_group(self):
        from src.segmentation.partsam.clicks import validate_clicks

        doc = _complete_clicks([0, 0, 0], [0, 0, 1], [0, 0, 2])
        del doc["groups"]["trunk"]
        with self.assertRaises(ValueError):
            validate_clicks(doc)

    def test_stage_clicks_skips_when_every_group_has_a_positive(self):
        from src.segmentation.partsam.clicks import run_stage_clicks

        doc = _complete_clicks([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            path = out / "clicks.json"
            path.write_text(json.dumps(doc))
            before = path.read_bytes()
            returned = run_stage_clicks(
                model_path=out / "missing_checkpoint",
                output_dir=out,
            )
            self.assertEqual(returned, path)
            self.assertEqual(path.read_bytes(), before)

    def test_stage_clicks_does_not_skip_partial_groups(self):
        from src.segmentation.partsam.clicks import run_stage_clicks

        doc = _complete_clicks([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
        doc["groups"]["leaves"]["positives"] = []
        xyz, colors = _synthetic_cloud()
        n = len(xyz)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_sample_100k(
                out / "sample_100k.npz",
                xyz,
                np.tile(np.array([0.0, 0.0, 1.0], dtype=np.float32), (n, 1)),
                colors,
                np.zeros(n, dtype=np.int32),
            )
            (out / "clicks.json").write_text(json.dumps(doc))
            with self.assertRaises(RuntimeError):
                run_stage_clicks(model_path=out / "missing", output_dir=out)
            self.assertTrue((out / "click_candidates.json").exists())

    def test_geometry_bins_place_primaries_in_pot_trunk_leaves(self):
        from src.segmentation.partsam.clicks import propose_click_candidates

        xyz, colors = _synthetic_cloud()
        groups = propose_click_candidates(xyz, colors)
        self.assertEqual(set(groups), {"pot", "trunk", "leaves"})
        for name in ("pot", "trunk", "leaves"):
            self.assertGreaterEqual(groups[name]["n_bin"], 5)
            self.assertEqual(len(groups[name]["indices"]), 5)
            self.assertEqual(len(groups[name]["points"]), 5)

        pot = np.array(groups["pot"]["points"][0])
        trunk = np.array(groups["trunk"]["points"][0])
        leaves = np.array(groups["leaves"]["points"][0])
        self.assertLess(pot[2], trunk[2])
        self.assertLess(trunk[2], leaves[2])
        pot_rgb = colors[groups["pot"]["indices"][0]].astype(np.float32)
        leaf_rgb = colors[groups["leaves"]["indices"][0]].astype(np.float32)
        self.assertLess(float(pot_rgb.mean()), 95.0)
        self.assertGreater(float(leaf_rgb[1]), float(leaf_rgb[0]) + 8.0)
        self.assertGreater(float(leaf_rgb[1]), 90.0)


if __name__ == "__main__":
    unittest.main()
