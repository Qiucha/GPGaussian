# Validator vs omit-invalid and frozen materials keys

Primary sources (2026-08-14): `src/llm/validator.py` (`calculate_p_wave_speed`, `validate_physgaussian_config`); `src/llm/schema.py` (`PhysGaussianLLMConfig`, `validate_segmenter_execution_plan`); `tests/test_schema_and_cfl.py`; [Revision shape](../../mpm-critique-loop/issues/04-revision-shape.md); [Motion Critique Loop spec](../../mpm-critique-loop/spec.md) Revision and Modes (CFL/schema). Does not implement the validator.

## 1. What `validate_physgaussian_config` already does

Signature is one candidate dict plus `max_cfl` (default `0.5`). Return type is `Tuple[bool, str]`. Docstring: `ValueError` if Poisson ratio is singular or CFL is violated. (`src/llm/validator.py`, `validate_physgaussian_config`.)

There is no `previous` argument. (`src/llm/validator.py`.)

### Raises (`ValueError`) vs `(True, msg)`

The function never returns `(False, ...)`. If it returns, it is always `(True, "Config is valid and satisfies CFL stability bounds.")`. (`src/llm/validator.py`, last return.)

| Case | Behavior | Source |
|---|---|---|
| `nu >= 0.499` on a materials row | `ValueError`: `Material tag '{tag}': Poisson ratio nu=... causes numerical singularity (must be < 0.49).` Checked **before** P-wave / CFL. | `validate_physgaussian_config` loop |
| CFL `(c_p * substep_dt) / dx > max_cfl` | `ValueError`: `CFL condition violated for material tag '{tag}'!` plus `c_p`, CFL, suggested `substep_dt`. | same loop after `calculate_p_wave_speed` |
| Passing rows | `(True, "Config is valid and satisfies CFL stability bounds.")` | last return |

`dx = (2.0 * grid_lim) / float(n_grid)` with `.get` defaults `substep_dt=1e-4`, `n_grid=100`, `grid_lim=2.0`. Per-row `.get` defaults: `nu=0.3`, `E=1e5`, `density=1000.0`. (`src/llm/validator.py`.)

`calculate_p_wave_speed` also raises `ValueError` for `nu >= 0.499`, `density <= 0`, and `E < 0`. The config validator duplicates the `nu` check; `E < 0` / `density <= 0` are not checked in the validator loop itself but can still raise inside `calculate_p_wave_speed`. (`src/llm/validator.py`.) Tests do not cover those two. (`tests/test_schema_and_cfl.py`.)

Unittests: valid config → `is_valid` True and `"Config is valid"` in the message; `nu=0.499` → `ValueError` with the Poisson-ratio string; large `substep_dt` / stiff `E` → `ValueError` with `"CFL condition violated"`. (`tests/test_schema_and_cfl.py`, `test_valid_config_passes`, `test_poisson_ratio_singularity_raises_error`, `test_cfl_violation_raises_error`.) Remaining tests in that file are Segmenter **plan** schema, not runner `--config`. (`test_valid_segmenter_execution_plan`, `test_invalid_primitive_type_raises_error`.)

### Empty `materials` fallback

`materials = config.get("materials", {})`. If that value is falsy (`{}` or missing), the validator **does not refuse**. It builds a synthetic table `{"0": {"E": ..., "nu": ..., "density": ...}}` from top-level `E` / `nu` / `density` (defaults `1e5` / `0.3` / `1000.0`) and runs `nu` / CFL on that unlabeled `"0"` row. (`src/llm/validator.py`.)

That is the opposite of the loop policy: no new rows, including unlabeled `"0"`. ([spec.md](../../mpm-critique-loop/spec.md) Revision; [04-revision-shape.md](../../mpm-critique-loop/issues/04-revision-shape.md).)

### `schema.py` is a different seam

`validate_physgaussian_config` does not import or call `schema.py`. (`src/llm/validator.py`.)

`PhysGaussianLLMConfig` is a dataclass with a `materials: Dict[str, Dict[str, Any]]` field (default `{}`). No omit-vs-previous check. (`src/llm/schema.py`.)

`validate_segmenter_execution_plan` validates Segmenter Agent plans: `materials` must be a **list** of `{tag_id, ...}`; `E > 0`; `nu` in `[0.0, 0.49]`; `density > 0`; known primitives. That is not runner `--config` and is not the Motion Critique Loop validator. (`src/llm/schema.py`.) Do not treat those plan rules as extra physics for `validate_physgaussian_config`.

## 2. Omit of a previous key is not detected today

Loop policy: `critique` returns a **full** next `--config`. Every key that was on the previous file must appear on the new object. Omit is **invalid** (validator), not copy-through and not PhysGaussian clone defaults. Prompt may seed the previous JSON so the model echoes camera, rotation, opacity, top-level `"material"`. ([spec.md](../../mpm-critique-loop/spec.md) Revision; [04-revision-shape.md](../../mpm-critique-loop/issues/04-revision-shape.md).)

Today the validator sees only the candidate. `.get` fills `substep_dt`, `n_grid`, `grid_lim`, and per-row `E` / `nu` / `density`. Missing `materials` is rewritten to unlabeled `"0"`. (`src/llm/validator.py`.) There is no walk of previous keys. Tests never pass a previous object. (`tests/test_schema_and_cfl.py`.)

## 3. Adding or dropping `materials` rows is not detected today

Loop policy: tag-ID → material stays the existing `materials` table (string-int keys → `{E, nu, density}` plus keys already on that row). **Key set frozen** to the previous table: every previous row must appear; **no new rows** (including unlabeled `"0"`). IDs not on the tensor remain invalid. Tensor IDs with no previous row stay on runner scalar fill. A `"0"`/`"1"`/`"2"` table against ficus `"1"`/`"2"`/`"3"` is invalid. ([spec.md](../../mpm-critique-loop/spec.md) Revision; [04-revision-shape.md](../../mpm-critique-loop/issues/04-revision-shape.md).)

Today the validator iterates whatever dict it has (or the synthetic `"0"`). Extra keys are CFL-checked, not rejected as new rows. Dropped keys are invisible. Inventing `"0"` on empty `materials` is the empty-table fallback. (`src/llm/validator.py`.) Tests use a three-row `"0"`/`"1"`/`"2"` table for the happy path and a one-row `"0"` table for `nu` / CFL errors; they do not compare to a previous table. (`tests/test_schema_and_cfl.py`.)

## 4. What a later implement ticket must add

CFL/schema for the loop: existing `validate_physgaussian_config` (`ValueError` on `nu` / CFL) **plus** omit-invalid and frozen `materials` key set. ([spec.md](../../mpm-critique-loop/spec.md) Modes.) Mock identity still calls `validate_physgaussian_config`; omit / frozen-key tests belong on the validator, not the mock body. ([spec.md](../../mpm-critique-loop/spec.md) Mock.)

**Signature (previous vs candidate only).** Extend the validator so it can see the previous `--config` dict and the candidate dict. Do not add a tensor argument here.

**Keep existing physics, do not invent more.** Still `ValueError` on `nu >= 0.499` and CFL as today. Do not import Segmenter plan bounds (`E > 0`, `nu` in `[0.0, 0.49]`) as new MPM-config rules. (`src/llm/validator.py`; `src/llm/schema.py` `validate_segmenter_execution_plan`.)

**Omit-invalid.** After (or as part of) that function: every key present on the previous object must be present on the candidate. Absence is invalid. Do not merge omitted keys from previous or from clone defaults. ([spec.md](../../mpm-critique-loop/spec.md) Revision; [04-revision-shape.md](../../mpm-critique-loop/issues/04-revision-shape.md).)

**Frozen `materials` key set.** Candidate `materials` keys must be exactly the previous table’s keys: every previous row; no added rows; no unlabeled `"0"` unless `"0"` was already a previous key. Empty / missing `materials` must **not** synthesize `"0"` when previous had a table (and must not add `"0"` when previous had none). Retune values on existing rows (`E`, `nu`, `density`, plus keys already on that row) remains allowed, then existing `nu` / CFL still apply. ([spec.md](../../mpm-critique-loop/spec.md) Revision; [04-revision-shape.md](../../mpm-critique-loop/issues/04-revision-shape.md); `src/llm/validator.py`.)

**Out of this signature (do not invent rows or new physics).** Spec still: IDs absent from the Material Tag Tensor are invalid; tensor IDs with no previous row keep **runner scalar fill** (do not invent JSON rows). Previous-vs-candidate cannot see the tensor. Frozen key set already forbids adding unlabeled `"0"` to “cover” those IDs. Tensor membership is not a new wave-speed / CFL rule. ([spec.md](../../mpm-critique-loop/spec.md) Frozen Material Tag Tensor and Revision.)
