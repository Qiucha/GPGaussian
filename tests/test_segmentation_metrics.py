"""
Unit tests for SegmentationEvaluator and SegmentationMetrics in src/segmentation/metrics.py.
"""

import unittest
import torch
import numpy as np
from src.segmentation.metrics import SegmentationEvaluator, SegmentationMetrics


class TestSegmentationMetrics(unittest.TestCase):

    def setUp(self):
        torch.manual_seed(42)
        np.random.seed(42)

        self.N = 200
        self.xyz = torch.randn(self.N, 3)
        self.sh_dc = torch.randn(self.N, 3)
        self.tags = torch.zeros(self.N, dtype=torch.int64)
        self.tags[:100] = 0
        self.tags[100:] = 1

    def test_evaluate_basic(self):
        metrics = SegmentationEvaluator.evaluate(
            self.xyz,
            self.sh_dc,
            self.tags,
            material_names={0: "Base", 1: "Top"},
        )
        self.assertIsInstance(metrics, SegmentationMetrics)
        self.assertEqual(metrics.total_particles, 200)
        self.assertEqual(metrics.num_tags, 2)
        self.assertEqual(len(metrics.tag_metrics), 2)
        self.assertIn(metrics.overall_quality_rating, ["EXCELLENT", "GOOD", "NEEDS_REFINEMENT", "POOR"])

    def test_format_llm_feedback(self):
        metrics = SegmentationEvaluator.evaluate(
            self.xyz,
            self.sh_dc,
            self.tags,
            material_names={0: "Base", 1: "Top"},
        )
        feedback_str = metrics.format_llm_feedback()
        self.assertIn("QUANTITATIVE SEGMENTATION EVALUATION REPORT", feedback_str)
        self.assertIn("Tag 0 (Base)", feedback_str)
        self.assertIn("Tag 1 (Top)", feedback_str)


if __name__ == "__main__":
    unittest.main()
