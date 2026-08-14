# 04 - Test contract for the Motion Critique Loop without Warp

Type: grilling
Status: resolved
Blocked by: none

## Question

What always-on unittests must this map add, given live Warp, live LLM, and VLM are out of scope?

Cover: mock `critique` identity + empty-text reject + visual-skip canned reasoning; live `critique` `NotImplementedError`; omit-invalid / frozen `materials` validator; human-gated wait (no second solver call); auto-rerun with fake runner (N, inner retry, interrupt). What is explicitly not a test in this map.

## Answer

Always-on `python -m unittest` only. No Warp, live LLM, VLM, or PNG reads.

**Files:** `tests/test_motion_critique.py` for `critique` + driver (fake PhysGaussian MPM Solver). Omit-invalid / frozen-`materials` cases go in `tests/test_schema_and_cfl.py` beside existing `nu` / CFL tests. Do not extend `tests/test_llm_translator.py`.

**`critique` (mock):** empty/whitespace human text fails before the mock body; identity returns `(previous_config, canned_reasoning)` after `validate_physgaussian_config` (no motion-library retrieve from human text); if `frame_paths` is set, canned reasoning contains **`visual channel skipped (mock)`** and no files are read; `mock_llm=False` raises `NotImplementedError`.

**Validator:** omit of a previous `--config` key → `ValueError`; new `materials` row (including unlabeled `"0"`) → `ValueError`. Existing `nu` / CFL tests stay.

**Driver:** human-gated: fake runner once, then wait (no second solve). Auto: fake runner **N=2** in tests; inner `critique` retry does not increment N; **injectable stop flag** (not SIGINT in unittest) stops without another solve. Live driver may map SIGINT onto that flag.

**Explicitly not a test:** live Warp, live LLM/VLM, PNG bytes, Digest JPEGs, FVD/KVD/etc., `run_pipeline.sh`, a ficus campaign.

## Comments
