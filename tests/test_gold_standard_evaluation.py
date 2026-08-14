import unittest
import numpy as np


class TestGoldStandardEvaluationSuite(unittest.TestCase):
    def test_trajectory_mse_kabsch_alignment(self):
        from eval.evaluate_realism import compute_trajectory_mse_kabsch

        # Synthetic 3D particle trajectories (10 particles, 5 frames)
        N, T = 10, 5
        np.random.seed(42)
        P_gt = np.random.uniform(-1, 1, size=(N, T, 3))
        # Simulated trajectories with small offset
        P_sim = P_gt + 0.05

        mse, rel_err = compute_trajectory_mse_kabsch(P_sim, P_gt)
        self.assertTrue(mse >= 0.0)
        self.assertAlmostEqual(mse, 0.0, places=2)  # SVD Kabsch removes constant translation offset

    def test_effort_metrics_logging(self):
        from eval.evaluate_effort import ConfigurationEffortTracker

        tracker = ConfigurationEffortTracker()
        tracker.start_session("scene_ficus_wind")
        tracker.record_code_change("{\"materials\": {\"0\": {\"E\": 1e7}}}")
        tracker.record_simulation_run()
        summary = tracker.end_session()

        self.assertIn("t_setup_seconds", summary)
        self.assertEqual(summary["loc_manual"], 1)
        self.assertEqual(summary["n_iter"], 1)

    def test_2afc_binomial_and_bradley_terry(self):
        from eval.evaluate_realism import compute_2afc_statistics

        # 30 trials, 23 wins for proposed system
        p_val, win_rate = compute_2afc_statistics(wins=23, total_trials=30)
        self.assertAlmostEqual(win_rate, 76.67, places=1)
        self.assertTrue(p_val < 0.01)  # Statistically significant


if __name__ == "__main__":
    unittest.main()
