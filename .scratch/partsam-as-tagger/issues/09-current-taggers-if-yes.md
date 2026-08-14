# 09 - What happens to the current Material Tag Tensor producers

Type: grilling
Status: resolved
Blocked by: 08

## Question

Given the go/no-go, what is the spec’s recommendation for **Heuristic Primitives**, the **Segmenter Agent**, **FlashSplat**, and **LangSAM**?

The spec must name **one intended producer**. If YES (PartSAM), say which of the others are fallback, retired, or unchanged-but-not-intended. If NO (leave as trial), the intended producer stays the status quo — record that explicitly. Do not edit `src/`.

## Answer

PartSAM remains the **one intended producer** ([Go/no-go: PartSAM as the lasting Material Tag Tensor source](08-go-no-go-partsam-as-tagger.md)). None of the others are fallback.

- **FlashSplat** — **retired** as a tagging path (the 2D-lift producer PartSAM replaces). A later `src/` map unhooks it, including `run_pipeline.sh` starting on FlashSplat.
- **LangSAM** — **retired**. It never writes a Material Tag Tensor; with FlashSplat retired it has no tagging-path consumer.
- **Heuristic Primitives** — **unchanged-but-not-intended**. Stay for digest/tests; not a second producer.
- **Segmenter Agent** — **unchanged-but-not-intended**. Same bucket as the primitives it plans.

The PartSAM recipe is merge + nearest-neighbor only ([Overlap and merge policy without another trial](06-overlap-merge-policy.md)). Heuristic Primitives are not a rewriter on that seam. This ticket does not edit `src/`.
