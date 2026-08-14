# 05 - Is Stage 2 in the fix

Type: grilling
Status: resolved
Blocked by: 01

## Question

Does the spec’s allowed change include **Stage 2 clicks** (new accept/swap, negatives, refuse skip-if-exists of trial JSON on a new 100k), or is the live defect **merge-only** given on-cloud primaries?

If Stage 2 stays out, say so explicitly so a later implementation map does not reopen clicks by default.

## Answer

Stage 2 **is** in the spec, but only a generic skip contract: `clicks.json` may skip-if-exists only when it belongs to **this** 100k sample. Otherwise geometry proposes on this cloud and MLLM/human accept/swap. Do not reuse another sample’s world-xyz (including the ficus trial JSON on a newly built `sample_100k.npz`).

No new negatives rule. Mask retry with negatives stays the existing recipe if a prompted ID is still empty after merge survival.

Rejected: merge-only (Stage 2 explicitly out); ficus-specific click placement or stem negatives.

