import unittest
import numpy as np


class TestPhysGaussianLLMConfigValidator(unittest.TestCase):
    def setUp(self):
        self.valid_config = {
            "substep_dt": 5e-05,
            "frame_dt": 0.04,
            "frame_num": 100,
            "n_grid": 100,
            "grid_lim": 2.0,
            "g": [0.0, 0.0, -9.81],
            "materials": {
                "0": {"E": 1e7, "nu": 0.30, "density": 1800.0, "material_type": "jelly"},
                "1": {"E": 5e5, "nu": 0.35, "density": 600.0, "material_type": "jelly"},
                "2": {"E": 2e3, "nu": 0.45, "density": 150.0, "material_type": "jelly"},
            },
            "boundary_conditions": [
                {
                    "type": "particle_impulse",
                    "force": [0.00025, 0.0, 0.00005],
                    "point": [1.0, 1.0, 1.4],
                    "size": [1.2, 1.2, 0.8],
                    "num_dt": 30000,
                    "start_time": 0.0,
                }
            ],
        }

        self.valid_plan = {
            "scene_name": "ficus_scene",
            "materials": [
                {"tag_id": 0, "name": "Pot", "E": 1e7, "nu": 0.3, "density": 1800.0},
                {"tag_id": 1, "name": "Trunk", "E": 5e5, "nu": 0.35, "density": 800.0},
                {"tag_id": 2, "name": "Leaves", "E": 1e4, "nu": 0.4, "density": 200.0},
            ],
            "steps": [
                {
                    "primitive_type": "spatial_y_cutoff",
                    "params": {"target_tag": 0, "cutoff_y": 0.45},
                    "description": "Tag base pot below height threshold",
                },
                {
                    "primitive_type": "color_sh",
                    "params": {"target_tag": 1, "condition": "R > G and R > B"},
                    "description": "Tag brown woody stem",
                },
                {
                    "primitive_type": "hsv",
                    "params": {
                        "target_tag": 2,
                        "color_space": "hsv",
                        "hsv_bounds": {"min_h": 100.0, "max_h": 140.0},
                    },
                    "description": "Tag green foliage",
                },
            ],
        }

    def test_valid_config_passes(self):
        from llm.validator import validate_physgaussian_config

        is_valid, msg = validate_physgaussian_config(self.valid_config)
        self.assertTrue(is_valid)
        self.assertIn("Config is valid", msg)

    def test_poisson_ratio_singularity_raises_error(self):
        from llm.validator import validate_physgaussian_config

        invalid_config = dict(self.valid_config)
        invalid_config["materials"] = {
            "0": {"E": 1e7, "nu": 0.499, "density": 1800.0}
        }
        with self.assertRaises(ValueError) as ctx:
            validate_physgaussian_config(invalid_config)
        self.assertIn("Poisson ratio nu=0.499 causes numerical singularity", str(ctx.exception))

    def test_cfl_violation_raises_error(self):
        from llm.validator import validate_physgaussian_config

        invalid_config = dict(self.valid_config)
        invalid_config["substep_dt"] = 1e-3
        invalid_config["materials"] = {
            "0": {"E": 5e7, "nu": 0.30, "density": 1000.0}
        }
        with self.assertRaises(ValueError) as ctx:
            validate_physgaussian_config(invalid_config)
        self.assertIn("CFL condition violated", str(ctx.exception))

    def test_valid_segmenter_execution_plan(self):
        from llm.schema import validate_segmenter_execution_plan

        plan = validate_segmenter_execution_plan(self.valid_plan)
        self.assertEqual(plan.scene_name, "ficus_scene")
        self.assertEqual(len(plan.materials), 3)
        self.assertEqual(len(plan.steps), 3)
        dict_rep = plan.to_dict()
        self.assertEqual(dict_rep["scene_name"], "ficus_scene")

    def test_invalid_primitive_type_raises_error(self):
        from llm.schema import validate_segmenter_execution_plan

        invalid_plan = dict(self.valid_plan)
        invalid_plan["steps"] = [
            {"primitive_type": "invalid_magic_primitive", "params": {}}
        ]
        with self.assertRaises(ValueError) as ctx:
            validate_segmenter_execution_plan(invalid_plan)
        self.assertIn("Unknown primitive_type 'invalid_magic_primitive'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
