"""
Few-Shot Motion Translation Engine & System Prompt Orchestrator for PhysGaussian.
"""

from typing import Dict, Any, Tuple, Optional, List
from llm.motion_library import MotionLibraryRetriever
from llm.validator import validate_physgaussian_config

SYSTEM_PROMPT_TEMPLATE = """You are PhysGaussianLLM, an expert continuum mechanics AI assistant.
Your task is to convert natural language motion descriptions into precise, physically valid PhysGaussian MPM simulation configurations adhering to the PhysGaussianLLMConfig schema.

### SYSTEM INVARIANTS & PHYSICAL RULES:
1. MATERIAL UNITS:
   - Young's Modulus E is in Pascals (Pa). Soft/compliant: 1e1 - 1e4. Stiff wood/plastic: 1e5 - 1e6. Rigid base: 1e7 - 1e9.
   - Poisson's Ratio nu MUST satisfy 0.0 <= nu <= 0.49. (Use ~0.45 for incompressible jelly/leaves; 0.3 for rigid components).
   - Mass Density density is in kg/m^3. Typical values: 10 - 2000.

2. STABILITY & TIME-STEPPING (CFL CONDITION):
   - Ensure substep_dt <= 1e-4 when high Young's modulus (E > 1e6) is present.
   - P-wave speed cp = sqrt( (E*(1-nu)) / (rho*(1+nu)*(1-2*nu)) ). Never allow cp * substep_dt > 0.5 * dx.

3. BOUNDARY CONDITION SPECS:
   - particle_impulse: Applies force [Fx, Fy, Fz] inside spatial bounding box [point, size] for num_dt substeps starting at start_time.
   - cuboid: Enforces fixed velocity [vx, vy, vz] inside box [point, size] over [start_time, end_time]. Set reset=1 to anchor base.
   - enforce_particle_velocity_rotation: Applies rotational torque around normal vector centered at point within cylinder [half_height, radius].

### FEW-SHOT MOTION EXEMPLARS:
<exemplars>
{EXEMPLARS_BLOCK}
</exemplars>

### CHAIN-OF-THOUGHT (CoT) REASONING MANDATE:
Before emitting the final JSON output, perform step-by-step physical reasoning inside a <reasoning> block:
- Step 1: Identify object components and assign material tags.
- Step 2: Determine appropriate E, nu, density for each tag.
- Step 3: Compute spatio-temporal force vectors (magnitudes, spatial origins, durations).
- Step 4: Validate numerical stability and time-step bounds.
"""


class MotionTranslator:
    def __init__(
        self,
        retriever: Optional[MotionLibraryRetriever] = None,
        mock_llm: bool = True,
    ):
        self.retriever = retriever or MotionLibraryRetriever()
        self.mock_llm = mock_llm

    def build_prompts(
        self,
        query: str,
        scene_bounds: Optional[Dict[str, Any]] = None,
        k_shot: int = 2,
    ) -> Tuple[str, str]:
        exemplars = self.retriever.retrieve(query, k=k_shot)
        exemplars_block = self.retriever.format_exemplars_for_prompt(exemplars)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(EXEMPLARS_BLOCK=exemplars_block)

        user_prompt = f"User Request: \"{query}\"\n"
        if scene_bounds:
            user_prompt += f"Scene Spatial Bounds: {scene_bounds}\n"

        user_prompt += "Translate this request into CoT reasoning and valid JSON configuration."

        return system_prompt, user_prompt

    def translate(
        self,
        query: str,
        scene_bounds: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], str]:
        system_prompt, user_prompt = self.build_prompts(query, scene_bounds)

        if self.mock_llm:
            # Deterministic mock response for testing/offline execution based on retrieved top exemplar
            top_exemplar = self.retriever.retrieve(query, k=1)[0]
            config = top_exemplar["config"]
            reasoning = top_exemplar["reasoning"]

            # Validate against CFL guardrail
            validate_physgaussian_config(config)
            return config, reasoning

        raise NotImplementedError("Live LLM API endpoint call requires API key configuration.")

    def critique(
        self,
        previous_config: Dict[str, Any],
        previous_cot: str,
        human_text: str,
        frame_paths: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, Any], str]:
        if not (human_text or "").strip():
            raise ValueError("human text is required; empty or whitespace is not a critique turn")
        if not self.mock_llm:
            raise NotImplementedError("Live LLM API endpoint call requires API key configuration.")
        validate_physgaussian_config(previous_config, previous=previous_config)
        reasoning = "identity mock critique"
        if frame_paths:
            reasoning = f"{reasoning}; visual channel skipped (mock)"
        return previous_config, reasoning
