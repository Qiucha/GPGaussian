import unittest


class TestMotionLibraryRetrievalEngine(unittest.TestCase):
    def test_motion_library_exemplars_load(self):
        from llm.motion_library import get_core_motion_exemplars

        exemplars = get_core_motion_exemplars()
        self.assertEqual(len(exemplars), 4)

        categories = [e["primitive_category"] for e in exemplars]
        self.assertIn("wind_fluid_drag", categories)
        self.assertIn("impulse_impact", categories)
        self.assertIn("bending_twisting", categories)
        self.assertIn("tearing_disruption", categories)

    def test_mmr_retrieval_and_filtering(self):
        from llm.motion_library import MotionLibraryRetriever

        retriever = MotionLibraryRetriever()
        # Query for wind gust simulation
        results = retriever.retrieve("gust of wind blowing ficus leaves", k=2, alpha=0.75)
        self.assertEqual(len(results), 2)
        # Top result should be wind_fluid_drag
        self.assertEqual(results[0]["primitive_category"], "wind_fluid_drag")

    def test_exemplar_minification_and_formatting(self):
        from llm.motion_library import MotionLibraryRetriever

        retriever = MotionLibraryRetriever()
        results = retriever.retrieve("twisting flexible silicone vase", k=1)
        formatted_prompt = retriever.format_exemplars_for_prompt(results)

        self.assertIn("bending_twisting", formatted_prompt)
        self.assertIn("boundary_conditions", formatted_prompt)
        self.assertIn("materials", formatted_prompt)


if __name__ == "__main__":
    unittest.main()
