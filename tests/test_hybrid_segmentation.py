import unittest
import torch
import numpy as np


class TestHybridSegmentationEngine(unittest.TestCase):
    def setUp(self):
        # Synthetic point cloud (100 particles)
        N = 100
        np.random.seed(42)

        # 30 pot particles (low Y), 40 stem/trunk particles (brown SH), 30 leaf particles (green SH)
        xyz = np.zeros((N, 3), dtype=np.float32)
        # Pot: y < 0.5
        xyz[:30, 1] = np.random.uniform(0.0, 0.4, size=30)
        # Stem & Leaves: y >= 0.5
        xyz[30:, 1] = np.random.uniform(0.5, 1.5, size=70)
        xyz[30:70, 0] = np.random.uniform(0.9, 1.1, size=40)  # Narrow cylinder stem

        # SH DC components (f_dc * 0.28209479 + 0.5 = RGB)
        sh_dc = np.zeros((N, 3), dtype=np.float32)
        # Pot
        sh_dc[:30] = (np.array([0.5, 0.5, 0.5]) - 0.5) / 0.28209479
        # Stem (R > G and R > B)
        sh_dc[30:70] = (np.array([0.8, 0.4, 0.2]) - 0.5) / 0.28209479
        # Leaves (G > R and G > B)
        sh_dc[70:] = (np.array([0.2, 0.8, 0.2]) - 0.5) / 0.28209479

        # Synthetic anisotropic scales
        scales = np.ones((N, 3), dtype=np.float32) * 0.05
        scales[30:70, 1] = 0.5  # High aspect ratio stem needles (0.5 / 0.05 = 10x anisotropy)

        self.cloud_xyz = torch.tensor(xyz)
        self.cloud_sh_dc = torch.tensor(sh_dc)
        self.cloud_scales = torch.tensor(scales)

    def test_sh_dc_to_rgb_conversion(self):
        from src.segmentation.heuristics import sh_dc_to_rgb

        rgb = sh_dc_to_rgb(self.cloud_sh_dc)
        self.assertEqual(rgb.shape, (100, 3))
        self.assertAlmostEqual(rgb[30, 0].item(), 0.8, places=3)
        self.assertAlmostEqual(rgb[30, 1].item(), 0.4, places=3)

    def test_hsv_conversion_and_filtering(self):
        from src.segmentation.heuristics import ColorSHHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        # Green leaves in HSV (Hue ~ 120 deg)
        leaf_heuristic = ColorSHHeuristic(
            target_tag=2,
            color_space="hsv",
            hsv_bounds={"min_h": 100.0, "max_h": 140.0, "min_s": 0.5},
        )
        tags = leaf_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)
        self.assertTrue((tags[70:] == 2).all())
        self.assertTrue((tags[:70] == 0).all())

    def test_anisotropy_ratio_heuristic(self):
        from src.segmentation.heuristics import AnisotropicStructuralHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        aniso_heuristic = AnisotropicStructuralHeuristic(
            target_tag=1,
            analysis_type="anisotropy_ratio",
            threshold=5.0,
        )
        tags = aniso_heuristic.apply(
            self.cloud_xyz, self.cloud_sh_dc, current_tags, scales=self.cloud_scales
        )
        # Stem particles (30:70) have 10x scale ratio and should be tagged as 1
        self.assertTrue((tags[30:70] == 1).all())
        self.assertTrue((tags[:30] == 0).all())
        self.assertTrue((tags[70:] == 0).all())

    def test_heuristic_registry_pipeline(self):
        from src.segmentation.heuristics import HeuristicRegistry

        current_tags = torch.zeros(100, dtype=torch.int64)
        steps = [
            {
                "primitive_type": "spatial_y_cutoff",
                "params": {"target_tag": 0, "cutoff_y": 0.45},
            },
            {
                "primitive_type": "color_sh",
                "params": {"target_tag": 1, "condition": "R > G and R > B"},
            },
            {
                "primitive_type": "hsv",
                "params": {
                    "target_tag": 2,
                    "color_space": "hsv",
                    "hsv_bounds": {"min_h": 100.0, "max_h": 140.0, "min_s": 0.5},
                },
            },
        ]
        tags = HeuristicRegistry.apply_pipeline(
            self.cloud_xyz, self.cloud_sh_dc, current_tags, steps, scales=self.cloud_scales
        )
        # Pot: 0, Stem: 1, Leaves: 2
        self.assertTrue((tags[:30] == 0).all())
        self.assertTrue((tags[30:70] == 1).all())
        self.assertTrue((tags[70:] == 2).all())

    def test_dbscan_filtering_heuristic(self):
        from src.segmentation.heuristics import TopologicalGraphHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        current_tags[30:70] = 1  # Stem tag
        current_tags[98:] = 1  # Outliers far away

        dbscan_heuristic = TopologicalGraphHeuristic(
            target_tag=1, mode="dbscan", fallback_tag=3, eps=0.3, min_samples=3
        )
        filtered_tags = dbscan_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)

        self.assertEqual(filtered_tags[98].item(), 3)
        self.assertEqual(filtered_tags[99].item(), 3)

    def test_surface_normal_and_curvature_heuristic(self):
        from src.segmentation.heuristics import SurfaceNormalCurvatureHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        # Test vertical planar orientation
        normal_heuristic = SurfaceNormalCurvatureHeuristic(
            target_tag=4,
            mode="normal_orientation",
            k_neighbors=5,
            normal_axis="z",
            min_normal_dot=0.5,
        )
        tags = normal_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)
        self.assertEqual(tags.shape, (100,))
        self.assertIn(4, tags.numpy())

    def test_color_clustering_heuristic(self):
        from src.segmentation.heuristics import ColorClusteringHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        clustering_heuristic = ColorClusteringHeuristic(
            target_tag=5,
            n_clusters=2,
            color_space="hsv",
            method="kmeans",
            selection_criteria="darkest",
        )
        tags = clustering_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)
        self.assertEqual(tags.shape, (100,))
        self.assertIn(5, tags.numpy())

    def test_superpoint_graph_heuristic(self):
        from src.segmentation.heuristics import SuperpointGraphHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        current_tags[:10] = 6
        # Single isolated speckle point far away tagged as 6
        current_tags[99] = 6

        sp_heuristic = SuperpointGraphHeuristic(
            target_tag=6,
            voxel_size=0.1,
            min_component_ratio=0.05,
            fallback_tag=0,
            mode="superpoint_rag",
        )
        tags = sp_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)
        self.assertEqual(tags.shape, (100,))

    def test_dynamic_expression_heuristic(self):
        from src.segmentation.heuristics import DynamicExpressionHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        expr_heuristic = DynamicExpressionHeuristic(
            target_tag=7,
            expression="y > 0.0 and r > 0.1",
        )
        tags = expr_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)
        self.assertEqual(tags.shape, (100,))

    def test_surface_distance_heuristic(self):
        from src.segmentation.heuristics import SurfaceDistanceHeuristic

        current_tags = torch.zeros(100, dtype=torch.int64)
        sd_heuristic = SurfaceDistanceHeuristic(
            target_tag=8,
            min_distance=0.0,
            max_distance=0.5,
        )
        tags = sd_heuristic.apply(self.cloud_xyz, self.cloud_sh_dc, current_tags)
        self.assertEqual(tags.shape, (100,))


if __name__ == "__main__":
    unittest.main()
