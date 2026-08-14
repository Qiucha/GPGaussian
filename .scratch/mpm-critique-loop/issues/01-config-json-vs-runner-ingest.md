# Config JSON vs runner ingest for a Motion Critique Loop

Type: research
Status: resolved
Blocked by: none

## Question

What JSON does `MotionTranslator` / `PhysGaussianLLMConfig` emit, and what does the PhysGaussian MPM Solver runner actually load, such that a Motion Critique Loop can legally patch a post-run config **without** rewriting the Material Tag Tensor?

Cover, from primary sources only (`src/llm/schema.py`, `src/llm/translator.py`, `src/llm/motion_library.py`, `src/simulation/runner.py`, `src/simulation/config.py`, `src/simulation/lame_params.py`, `configs/ficus.json`, parent [spec.md](../../llm-motion-physgaussian/spec.md)):

1. Fields the translator schema names vs fields the runner reads (materials, boundary conditions, timesteps, tag paths).
2. How tag IDs become Lamé parameters today (`material_tags.pt` vs JSON `materials` table).
3. What a loop could patch in JSON vs what would require a new tensor.

Write findings to `.scratch/mpm-critique-loop/research/01-config-json-vs-runner-ingest.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** decide replace-vs-patch or the critique-entry seam.

## Answer

Translator JSON is the motion-library `materials` + `boundary_conditions` + timestep dict (string tags `"0"`/`"1"`/`"2"`); the runner loads that `materials` overlay plus upstream PhysGaussian decode, and loads tags only from CLI `--tags_path`, not from JSON. Retuning E/ν/ρ for IDs already on the tensor, plus BCs and timesteps, is a JSON patch; changing which particles hold which ID needs a new `material_tags.pt`. Findings: [research/01-config-json-vs-runner-ingest.md](../research/01-config-json-vs-runner-ingest.md).
