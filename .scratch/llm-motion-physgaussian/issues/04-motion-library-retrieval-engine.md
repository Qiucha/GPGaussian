# 04 — Motion Library & Dense-Sparse Hybrid Retrieval Engine

**What to build:**
Vector-indexed Motion Library (`src/llm/motion_library/`) containing few-shot exemplars across the 4 physical dynamics primitives (wind, drop/impact, twisting torque, tearing) with dense-sparse vector search and MMR reranking.

**Blocked by:** 01 — PhysGaussianLLMConfig Schema & CFL Validation Guardrail

**Status:** resolved

- [x] Create curated JSON exemplars for the 4 core physical dynamics primitives (Wind Drag, Impact Drop, Twisting Torque, Elastoplastic Tearing) matching `PhysGaussianLLMConfig`.
- [x] Build dense-sparse vector indexing module (`text-embedding-3-large` / `BGE-M3` embeddings) with attribute filters (`primitive_category`, `has_plasticity`, `material_tag_count`).
- [x] Implement Maximal Marginal Relevance (MMR) reranker (alpha=0.75) selecting k=2-3 non-redundant exemplars within a 4096-token context budget.
- [x] Add unit tests verifying query retrieval accuracy and token-minified prompt formatting.
