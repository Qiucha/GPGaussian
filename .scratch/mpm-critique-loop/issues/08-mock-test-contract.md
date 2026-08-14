# Mock/test contract for the Motion Critique Loop spec

Type: grilling
Status: resolved
Blocked by: 03, 05

## Question

What testable **mock** path does the spec document so a later map can test the Motion Critique Loop without a live LLM or VLM?

Align with existing `MotionTranslator(mock_llm=True)` if that is the seam; otherwise name the mock’s inputs/outputs. Not an implementation. Use `/grilling`.

## Answer

**Same seam, same flag:** `MotionTranslator(mock_llm=True).critique(...)`. Do not retrieve the motion library from human text (that is `translate`’s mock). Do not read PNG bytes or call a VLM.

**Identity mock:** human text must be non-empty. Return `(previous_config, canned_reasoning)` after `validate_physgaussian_config`. If `frame_paths` is set, canned reasoning records that the visual channel was skipped under mock. Empty/whitespace human text fails before this body.

**`mock_llm=False`:** `critique` raises `NotImplementedError` (same as live `translate`). This spec does not implement live or mock code.

No scripted E-mutation and no separate `mock_vlm` flag in this spec. Omit-invalid / frozen `materials` key set are validator tests for a later map, not this mock’s job.
