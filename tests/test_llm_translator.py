import unittest


class TestLLMMotionTranslator(unittest.TestCase):
    def test_prompt_construction(self):
        from llm.translator import MotionTranslator

        translator = MotionTranslator(mock_llm=True)
        system_prompt, user_prompt = translator.build_prompts(
            query="Blow a strong gust of wind across ficus leaves",
            scene_bounds={"min": [-1, -1, 0], "max": [1, 1, 2]},
        )

        self.assertIn("PHYSICAL RULES", system_prompt)
        self.assertIn("wind_fluid_drag", system_prompt)
        self.assertIn("ficus leaves", user_prompt)

    def test_end_to_end_mock_translation(self):
        from llm.translator import MotionTranslator

        translator = MotionTranslator(mock_llm=True)
        config, reasoning = translator.translate(
            query="Simulate wind gust blowing leaves"
        )

        self.assertIn("substep_dt", config)
        self.assertIn("materials", config)
        self.assertIn("boundary_conditions", config)
        self.assertTrue(len(reasoning) > 0)


if __name__ == "__main__":
    unittest.main()
