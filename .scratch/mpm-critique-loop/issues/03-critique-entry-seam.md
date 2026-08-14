# Critique-entry seam on MotionTranslator

Type: grilling
Status: resolved
Blocked by: 01

## Question

Does the Motion Critique Loop re-enter `MotionTranslator.translate` with critique appended to the user query, or does the spec name a **new** critique-entry seam (separate method/payload) that takes previous JSON + CoT + human text + frame paths?

Assume the live first-shot API stays out of this spec’s write-scope. Decide the seam a later implementation map would add or reuse. Use `/grilling` and `/domain-modeling`.

## Answer

**New seam:** `MotionTranslator.critique`, not a re-entry of `translate` and not optional kwargs on `translate`. First-shot `translate(query, scene_bounds)` is unchanged. This spec still does not implement the live first-shot API.

**Payload in:** previous JSON config, previous CoT, required human text, optional frame paths. Not the original first-shot `query` or `scene_bounds` (those stay on `translate`; critique does not re-retrieve the motion library from the first-shot string).

**Payload out:** the same `(config, reasoning)` pair as `translate`. Whether `config` is a full `PhysGaussianLLMConfig` document or a patch is [Revision shape for Motion Critique Loop JSON](04-revision-shape.md). What the visual channel *does* with those paths is [Visual channel’s job in the Motion Critique Loop](05-visual-channel-job.md). Mock/test of `critique` is [Mock/test contract for the Motion Critique Loop spec](08-mock-test-contract.md).

No new `CONTEXT.md` term. Not Segmenter Agent refinement.
