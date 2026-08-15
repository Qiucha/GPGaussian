import unittest


class TestFrameNumOverride(unittest.TestCase):
    def test_override_sets_frame_num_after_decode(self):
        from src.simulation.time_params import apply_frame_num_override

        time_params = {"substep_dt": 5e-6, "frame_dt": 4e-2, "frame_num": 125}
        apply_frame_num_override(time_params, 5)
        self.assertEqual(time_params["frame_num"], 5)
        self.assertEqual(time_params["frame_dt"], 4e-2)

    def test_absent_override_leaves_decoded_frame_num(self):
        from src.simulation.time_params import apply_frame_num_override

        time_params = {"frame_num": 125}
        apply_frame_num_override(time_params, None)
        self.assertEqual(time_params["frame_num"], 125)


if __name__ == "__main__":
    unittest.main()
