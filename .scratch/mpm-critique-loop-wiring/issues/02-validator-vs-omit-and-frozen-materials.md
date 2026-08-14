# 02 - Validator vs omit-invalid and frozen materials keys

Type: research
Status: resolved
Blocked by: none

## Question

What does `validate_physgaussian_config` already refuse, and what must a later implement ticket add so omit of a previous `--config` key is invalid and the `materials` key set stays frozen to the previous table?

Cover, from primary sources only (`src/llm/validator.py`, `src/llm/schema.py`, `tests/test_schema_and_cfl.py`, [Revision shape](../../mpm-critique-loop/issues/04-revision-shape.md), [spec.md](../../mpm-critique-loop/spec.md) Revision / CFL/schema):

1. Current raises vs return `(True, msg)` — `nu`, CFL, empty `materials` fallback.
2. Whether omit of a previous key is detected today.
3. Whether adding/dropping `materials` rows (including unlabeled `"0"`) is detected today.
4. What an implement ticket must add (signature: previous config vs candidate only) without inventing new physics rules.

Write findings to `.scratch/mpm-critique-loop-wiring/research/02-validator-vs-omit-and-frozen-materials.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** implement the validator.

## Answer

Today `validate_physgaussian_config` only raises on `nu >= 0.499` and CFL (else `(True, msg)`); empty/missing `materials` synthesizes unlabeled `"0"`. Omit of a previous key and add/drop of `materials` rows are undetected (single-dict signature). An implement ticket must compare previous `--config` vs candidate: every previous key required; `materials` key set frozen (no new `"0"`); keep existing `nu`/CFL; do not invent Segmenter-plan physics or tensor-driven rows.

Findings: [research/02-validator-vs-omit-and-frozen-materials.md](../research/02-validator-vs-omit-and-frozen-materials.md).

## Comments
