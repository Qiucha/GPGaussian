# 02 - Motion Library & Few-Shot Example Collection

Type: research
Status: resolved
Blocked by: 01

## Question

How should the Motion Library structure and curate few-shot prompt-configuration pairs across the four core physical dynamics primitives (wind/fluid drag, impulse impact/drop, bending/twisting torque, tearing/stress disruption) to maximize in-context learning accuracy of the LLM?

## Answer

### Key Findings & Architectural Decision

1. **Four Core Dynamics Exemplars:**
   - **Wind/Fluid Drag:** Multi-material ficus scene with stationary pot anchor (cuboid velocity), elastic trunk swaying ($E=5\times10^5$), hyperelastic leaves fluttering ($E=2\times10^3$), and continuous particle impulse gust fields (`particle_impulse`).
   - **Impulse Impact/Drop:** High-contrast multi-material drop scene under gravity ($g=-9.81$) with ground plane collider (`cuboid`), rigid plastic core ($E=5\times10^7$), and soft rubber gel outer shell ($E=1\times10^4$).
   - **Bending/Twisting Torque:** Rotational velocity field (`enforce_particle_velocity_rotation`) applying $7.85$ rad/s torque over 0.4s, holding rotated pose for 0.2s, and releasing for elastic springback.
   - **Tearing/Stress Disruption:** Elastoplastic material model (`material_type="elastoplastic"`, `yield_stress=120.0`) with opposing translational displacement velocity vectors ($v=\pm0.25$ m/s) on left and right grips.

2. **Vector Indexing & Hybrid Retrieval Engine:**
   - Dense-sparse hybrid search combining 3072-d embeddings (`text-embedding-3-large` / `BGE-M3`) with metadata filtering (stiffness regime, boundary types, tag count).
   - Maximal Marginal Relevance (MMR) reranking with $\alpha=0.75$ to select $k=2-3$ non-redundant exemplars for token-optimized context injection.

3. **In-Context Injection & Token Budgeting:**
   - Token budget allocation (4096 tokens total): ~800 tokens for system prompt & schema, ~1800 tokens for 2 minified exemplars, ~400 tokens for user query + scene bounds, ~1000 tokens for CoT + JSON output.
