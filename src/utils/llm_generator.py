"""
Legacy LLM Config Generator wrapper delegating to src.llm.translator.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from src.llm.translator import MotionTranslator
from src.llm.validator import validate_physgaussian_config


class ConfigGenerator:
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate", model: str = "Qwythos-9B_Q4_MTP:latest"):
        self.ollama_url = ollama_url
        self.model = model
        self.translator = MotionTranslator(mock_llm=True)

    def generate_config(self, bboxes: Dict[str, Any], output_file: str):
        """
        Generates PhysGaussian simulation configuration using MotionTranslator and validates CFL bounds.
        """
        query = f"Simulate object with parts: {', '.join(bboxes.keys())}"
        config, reasoning = self.translator.translate(query=query, scene_bounds=bboxes)

        # Validate configuration
        validate_physgaussian_config(config)

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(config, f, indent=4)

        print(f"Configuration successfully generated and saved to {output_file}")
        return config


if __name__ == "__main__":
    pass
