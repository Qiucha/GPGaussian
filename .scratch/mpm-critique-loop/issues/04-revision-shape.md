# Revision shape for Motion Critique Loop JSON

Type: grilling
Status: resolved
Blocked by: 01

## Question

When the Motion Critique Loop revises a config, is the LLM output a **full** replacement `PhysGaussianLLMConfig` JSON, or a **patch** (delta) against the previous JSON?

Include how tag-ID → material (`E`, `nu`, density) mapping is expressed, given the Material Tag Tensor stays frozen. Use `/grilling`. Do not invent a new tensor format.

## Answer

**Full replacement, not a patch.** `MotionTranslator.critique` returns `(config, reasoning)` where `config` is the complete next runner `--config` JSON (not a JSON Patch, not a nested delta, not a translator-only slice).

**Omit is invalid, not copy-through.** Every key that was on the previous file must appear on the new object. Prompt may seed the previous JSON so the model echoes camera, rotation, opacity, top-level `"material"`, etc.; that is not a silent merge. Omitted keys do not fall through to PhysGaussian clone defaults.

**Tag-ID → material** stays the existing `materials` table (string-int keys → `{E, nu, density}` plus keys already on that row). The Material Tag Tensor stays frozen.

**`materials` key set is frozen to the previous table.** Every previous row must appear; no new rows (including unlabeled `"0"`). IDs not on the tensor remain invalid. Tensor IDs with no previous row stay on runner scalar fill. A `"0"`/`"1"`/`"2"` table against ficus `"1"`/`"2"`/`"3"` is invalid.
