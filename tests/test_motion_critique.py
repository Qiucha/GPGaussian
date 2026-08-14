import copy
import unittest


PREVIOUS_CONFIG = {
    "substep_dt": 5e-05,
    "frame_dt": 0.04,
    "frame_num": 100,
    "n_grid": 100,
    "grid_lim": 2.0,
    "g": [0.0, 0.0, -9.81],
    "materials": {
        "1": {"E": 1e7, "nu": 0.30, "density": 1800.0},
        "2": {"E": 5e5, "nu": 0.35, "density": 600.0},
        "3": {"E": 2e3, "nu": 0.45, "density": 150.0},
    },
    "boundary_conditions": [],
}


class _BoomRetriever:
    def retrieve(self, *args, **kwargs):
        raise AssertionError("critique must not retrieve the motion library")


class TestMotionTranslatorCritique(unittest.TestCase):
    def test_empty_human_text_fails_before_mock_body(self):
        from llm.translator import MotionTranslator

        translator = MotionTranslator(retriever=_BoomRetriever(), mock_llm=True)
        with self.assertRaises(ValueError):
            translator.critique(
                copy.deepcopy(PREVIOUS_CONFIG),
                previous_cot="prior",
                human_text="   ",
            )

    def test_identity_mock_returns_previous_config_without_library_retrieve(self):
        from llm.translator import MotionTranslator

        translator = MotionTranslator(retriever=_BoomRetriever(), mock_llm=True)
        previous = copy.deepcopy(PREVIOUS_CONFIG)
        config, reasoning = translator.critique(
            previous,
            previous_cot="prior cot",
            human_text="leaves too floppy",
        )
        self.assertEqual(config, previous)
        self.assertTrue(len(reasoning) > 0)

    def test_frame_paths_record_visual_skip_without_reading_files(self):
        from llm.translator import MotionTranslator

        translator = MotionTranslator(retriever=_BoomRetriever(), mock_llm=True)
        missing = "/no/such/critique_frame.png"
        config, reasoning = translator.critique(
            copy.deepcopy(PREVIOUS_CONFIG),
            previous_cot="",
            human_text="stiffer trunk",
            frame_paths=[missing],
        )
        self.assertEqual(config["materials"]["1"]["E"], 1e7)
        self.assertIn("visual channel skipped (mock)", reasoning)

    def test_live_critique_raises_not_implemented(self):
        from llm.translator import MotionTranslator

        translator = MotionTranslator(retriever=_BoomRetriever(), mock_llm=False)
        with self.assertRaises(NotImplementedError):
            translator.critique(
                copy.deepcopy(PREVIOUS_CONFIG),
                previous_cot="prior",
                human_text="leaves too floppy",
            )


class _StopFlag:
    def __init__(self, value=False):
        self.value = value

    def __call__(self):
        return self.value


class _FlakyTranslator:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def critique(self, previous_config, previous_cot, human_text, frame_paths=None):
        self.calls += 1
        if self.calls == 1:
            raise ValueError("CFL condition violated for material tag '1'")
        return self.inner.critique(
            previous_config, previous_cot, human_text, frame_paths=frame_paths
        )


class TestCritiqueLoopDriver(unittest.TestCase):
    def _translator(self):
        from llm.translator import MotionTranslator

        return MotionTranslator(retriever=_BoomRetriever(), mock_llm=True)

    def test_human_gated_solver_once_then_wait(self):
        import tempfile
        from pathlib import Path

        from llm.critique_loop import run_critique_loop

        calls = []

        def fake_solver(config, output_path):
            calls.append(Path(output_path))
            Path(output_path).mkdir(parents=True, exist_ok=True)
            return []

        with tempfile.TemporaryDirectory() as tmp:
            result = run_critique_loop(
                previous_config=copy.deepcopy(PREVIOUS_CONFIG),
                previous_cot="",
                human_text="leaves too floppy",
                translator=self._translator(),
                solver=fake_solver,
                output_dir=Path(tmp),
                mode="human-gated",
            )
            self.assertEqual(len(calls), 1)
            self.assertEqual(result.status, "waiting")
            self.assertTrue((calls[0] / "config.json").exists())
            self.assertTrue((Path(tmp) / "run_01" / "config.json").exists())
            self.assertTrue((Path(tmp) / "run_01" / "reasoning.txt").exists())

    def test_auto_runs_solver_n_times(self):
        import tempfile
        from pathlib import Path

        from llm.critique_loop import run_critique_loop

        calls = []

        def fake_solver(config, output_path):
            calls.append(1)
            Path(output_path).mkdir(parents=True, exist_ok=True)
            return []

        with tempfile.TemporaryDirectory() as tmp:
            result = run_critique_loop(
                previous_config=copy.deepcopy(PREVIOUS_CONFIG),
                previous_cot="",
                human_text="leaves too floppy",
                translator=self._translator(),
                solver=fake_solver,
                output_dir=Path(tmp),
                mode="auto",
                max_runs=2,
            )
        self.assertEqual(len(calls), 2)
        self.assertEqual(result.status, "done")
        self.assertEqual(result.solver_runs, 2)

    def test_inner_retry_does_not_increment_solver_runs(self):
        import tempfile
        from pathlib import Path

        from llm.critique_loop import run_critique_loop

        calls = []

        def fake_solver(config, output_path):
            calls.append(1)
            Path(output_path).mkdir(parents=True, exist_ok=True)
            return []

        flaky = _FlakyTranslator(self._translator())
        with tempfile.TemporaryDirectory() as tmp:
            result = run_critique_loop(
                previous_config=copy.deepcopy(PREVIOUS_CONFIG),
                previous_cot="",
                human_text="leaves too floppy",
                translator=flaky,
                solver=fake_solver,
                output_dir=Path(tmp),
                mode="human-gated",
            )
        self.assertEqual(len(calls), 1)
        self.assertEqual(flaky.calls, 2)
        self.assertEqual(result.solver_runs, 1)

    def test_interrupt_flag_stops_without_another_solve(self):
        import tempfile
        from pathlib import Path

        from llm.critique_loop import run_critique_loop

        calls = []
        flag = _StopFlag(False)

        def fake_solver(config, output_path):
            calls.append(1)
            flag.value = True
            Path(output_path).mkdir(parents=True, exist_ok=True)
            return []

        with tempfile.TemporaryDirectory() as tmp:
            result = run_critique_loop(
                previous_config=copy.deepcopy(PREVIOUS_CONFIG),
                previous_cot="",
                human_text="leaves too floppy",
                translator=self._translator(),
                solver=fake_solver,
                output_dir=Path(tmp),
                mode="auto",
                max_runs=2,
                stop_flag=flag,
            )
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.status, "interrupted")


if __name__ == "__main__":
    unittest.main()
