# 05 - Implement omit-invalid and frozen materials validator

Type: task
Status: resolved
Blocked by: 02, 04

## Question

Extend the config validator so omit of a previous `--config` key is invalid and the `materials` key set is frozen to the previous table (no new rows, including unlabeled `"0"`). Keep existing `nu` / CFL `ValueError` behavior. IDs absent from the tensor remain invalid per spec; tensor IDs with no previous row keep runner scalar fill (do not invent rows).

Use [Validator vs omit-invalid and frozen materials keys](02-validator-vs-omit-and-frozen-materials.md) and tests from [Test contract for the Motion Critique Loop without Warp](04-test-contract-without-warp.md).

## Answer

`validate_physgaussian_config(..., previous=None)` keeps first-shot CFL/`nu` and empty-`materials` → synthetic `"0"`. With `previous` set: omit of any previous key is `ValueError`; candidate `materials` keys must equal the previous table (no new `"0"`); retune of `E`/`nu`/`density` on existing rows still runs CFL/`nu`. No tensor argument (runner scalar fill unchanged). Tests in `tests/test_schema_and_cfl.py`.

## Comments
