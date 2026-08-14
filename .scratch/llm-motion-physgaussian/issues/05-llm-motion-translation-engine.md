# 05 — LLM Few-Shot Motion Translation Engine

**What to build:**
End-to-end natural language motion translator (`src/llm/translator.py`) that queries the Motion Library, formats System/User prompts with Chain-of-Thought reasoning, calls the LLM, and runs CFL validation guardrails to output a runnable `PhysGaussianLLMConfig`.

**Blocked by:** 01 — PhysGaussianLLMConfig Schema & CFL Validation Guardrail, 04 — Motion Library & Dense-Sparse Hybrid Retrieval Engine

**Status:** resolved

- [x] Implement System Prompt builder with Chain-of-Thought (CoT) reasoning mandate and schema invariant rules.
- [x] Implement LLM orchestrator (`src/llm/translator.py`) querying Motion Library retrieval engine for k-shot exemplars.
- [x] Connect pre-simulation validator (`validate_physgaussian_config`) to automatically retry or raise errors on non-physical parameter scale outputs.
- [x] Add integration tests verifying end-to-end translation from natural language prompt strings to valid, CFL-checked JSON configuration objects.
