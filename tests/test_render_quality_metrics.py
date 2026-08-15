"""Unit tests for render PSNR/SSIM/LPIPS and frame sanity (CPU-offline)."""

from __future__ import annotations

import os
import tempfile
import unittest

import numpy as np

from eval.evaluate_realism import (
    assert_expected_frame_count,
    compare_image_pair,
    compute_psnr,
    compute_ssim,
    evaluate_frame_sanity,
    evaluate_render_directory,
    load_image_rgb,
)


class TestRenderQualityMetrics(unittest.TestCase):
    def test_psnr_identical_is_infinite(self):
        img = np.random.RandomState(0).rand(32, 32, 3)
        self.assertEqual(compute_psnr(img, img), float("inf"))

    def test_psnr_decreases_with_noise(self):
        rng = np.random.RandomState(1)
        img = rng.rand(48, 48, 3)
        noisy = np.clip(img + 0.05, 0, 1)
        noisier = np.clip(img + 0.2, 0, 1)
        self.assertGreater(compute_psnr(img, noisy), compute_psnr(img, noisier))

    def test_ssim_identical_near_one(self):
        img = np.random.RandomState(2).rand(64, 64, 3)
        score = compute_ssim(img, img)
        self.assertGreater(score, 0.99)

    def test_ssim_detects_structural_change(self):
        rng = np.random.RandomState(3)
        img = rng.rand(64, 64, 3)
        shifted = np.roll(img, shift=8, axis=1)
        self.assertLess(compute_ssim(img, shifted), compute_ssim(img, img))

    def test_frame_sanity_flags_black_and_nan(self):
        black = np.zeros((16, 16, 3), dtype=np.float64)
        ok = evaluate_frame_sanity(black)
        self.assertFalse(ok["ok"])
        self.assertIn("all_black", ok["reasons"])

        bad = np.ones((16, 16, 3), dtype=np.float64)
        bad[0, 0, 0] = np.nan
        nan_report = evaluate_frame_sanity(bad)
        self.assertFalse(nan_report["ok"])
        self.assertFalse(nan_report["finite"])

        good = np.linspace(0, 1, 16 * 16 * 3).reshape(16, 16, 3)
        self.assertTrue(evaluate_frame_sanity(good)["ok"])

    def test_compare_image_pair_and_directory(self):
        rng = np.random.RandomState(4)
        a = (rng.rand(20, 20, 3) * 255).astype(np.uint8)
        b = np.clip(a.astype(np.int16) + 3, 0, 255).astype(np.uint8)
        pair = compare_image_pair(a, b)
        self.assertIn("psnr", pair)
        self.assertIn("ssim", pair)
        self.assertGreater(pair["ssim"], 0.9)

        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image

            sim = os.path.join(tmp, "sim")
            ref = os.path.join(tmp, "ref")
            os.makedirs(sim)
            os.makedirs(ref)
            for i in range(3):
                Image.fromarray(a).save(os.path.join(sim, f"{i:04d}.png"))
                Image.fromarray(a).save(os.path.join(ref, f"{i:04d}.png"))
            report = evaluate_render_directory(sim, reference_dir=ref)
            self.assertTrue(report["ok"])
            self.assertEqual(report["frame_count"], 3)
            self.assertEqual(report["aggregate"]["mean_psnr"], float("inf"))
            ok, msg = assert_expected_frame_count(sim, 3)
            self.assertTrue(ok, msg)
            loaded = load_image_rgb(os.path.join(sim, "0000.png"))
            self.assertEqual(loaded.shape, (20, 20, 3))


class TestSceneRegistry(unittest.TestCase):
    def test_canonical_six_and_lookup(self):
        from eval.scene_registry import CANONICAL_SCENES, get_scene, select_scenes

        self.assertEqual(len(CANONICAL_SCENES), 6)
        ids = {s.id for s in CANONICAL_SCENES}
        self.assertEqual(
            ids, {"ficus", "vasedeck", "bread", "plane", "pillow2sofa", "wolf"}
        )
        self.assertEqual(get_scene("ficus").tagger, "partsam")
        self.assertEqual(get_scene("bread").config, "configs/tear_bread_multi_material.json")
        subset = select_scenes(["wolf", "plane"])
        self.assertEqual([s.id for s in subset], ["wolf", "plane"])


if __name__ == "__main__":
    unittest.main()
