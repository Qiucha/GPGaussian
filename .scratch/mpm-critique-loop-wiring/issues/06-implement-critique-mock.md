# 06 - Implement MotionTranslator.critique mock

Type: task
Status: resolved
Blocked by: 03, 04, 05

## Question

Implement `MotionTranslator.critique` per spec: `mock_llm=True` identity (non-empty human text; return `(previous_config, canned_reasoning)` after `validate_physgaussian_config`; if `frame_paths` is set, canned reasoning records visual skipped; no motion-library retrieve; no PNG/VLM I/O). `mock_llm=False` raises `NotImplementedError`. Empty/whitespace human text fails before the mock body.

`translate` stays first-shot only. Paths from [Persist filenames and src/llm module tree](03-filenames-and-module-tree.md). Tests from [Test contract for the Motion Critique Loop without Warp](04-test-contract-without-warp.md).

## Answer

`MotionTranslator.critique(previous_config, previous_cot, human_text, frame_paths=None)`: empty/whitespace `ValueError` first; `mock_llm=False` → `NotImplementedError`; mock identity returns `(previous_config, canned_reasoning)` after `validate_physgaussian_config(..., previous=previous_config)`; no motion-library retrieve; no PNG reads; `frame_paths` set → reasoning includes `visual channel skipped (mock)`. `translate` unchanged. Tests: `tests/test_motion_critique.py`.

## Comments
