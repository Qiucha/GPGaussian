# Map: Ficus PartSAM trial

## Destination

A written pass/fail for the settled ficus PartSAM trial: throwaway surface → 100k points → three click groups (pot/trunk/leaves, merge trunk > leaves > pot) → `material_tags.pt` → 5–10-frame PhysGaussian MPM Solver run. Destination is the result note, not a production tagging path in `src/`.

## Notes

- Effort slug: `partsam-ficus-trial`
- Domain: Phys4DGS glossary in `CONTEXT.md`. Recipe: [PartSAM trial design (scene, I/O, success)](../agent-orientation/issues/06-partsam-trial-design.md). Orientation: [docs/agents/orientation.md](../../docs/agents/orientation.md).
- Skills: `/research`, `/grilling`, `/domain-modeling`
- This effort **executes** the trial (overrides plan-only). Agent drives the run. Clicks: geometric candidates + MLLM accept/swap ([CLICK_PIPELINE.md](CLICK_PIPELINE.md)); human only if that fails twice. JSON contract still [clicks.template.json](clicks.template.json).
- Artifacts: `.scratch/partsam-ficus-trial/` (surface, clicks, tags, logs, result). Research notes: `.scratch/partsam-ficus-trial/research/`.
- Standing: ficus_whitebg; 100k ValDataset-style sample with normals + color; merge priority trunk > leaves > pot; short run = `configs/ficus.json` with `frame_num` 5–10.
- Pass: `material_tags.pt` length = Gaussian count; all three tags non-trivial (trunk > 1 000); runner loads tags; short MPM run does not immediately explode.

## Decisions so far

- [PartSAM official inference path for three-click masks](issues/01-partsam-inference-path.md) — No click UI; three masks via `predict_masks()` on a normalized 100k cloud; `eval_everypart.py` is auto Segment-Every-Part only. Env torch 2.4.1+cu124; weights `Czvvd/PartSAM`; MIT + NVIDIA-noncommercial `partfield/`. Findings: [research/01-partsam-inference-path.md](research/01-partsam-inference-path.md).
- [Provision PartSAM environment and weights](issues/03-provision-partsam-env.md) — Clone + 859MB weights + conda `PartSAM` with torch 2.4.1+cu124 (CUDA true). Leftover: torkit3d/apex/pointops. See [ENV.md](ENV.md).
- [Ficus Gaussians to a 100k ValDataset-style sample](issues/02-ficus-surface-sample.md) — ValDataset needs a triangle mesh sampled to 100k with face normals + color; ficus is a 203 930-Gaussian PLY with no faces; this repo has no mesher. Findings: [research/02-ficus-surface-sample.md](research/02-ficus-surface-sample.md).
- [Choose the external ficus mesher](issues/09-choose-external-mesher.md) — pymeshlab Screened Poisson in `physgauss` from iter-60000 Gaussian means; bake SH RGB via nearest-mean `sh_dc_to_rgb`; ball pivoting only if the mesh is unclickable.
- [Build the ficus 100k-point surface](issues/04-build-ficus-surface.md) — Poisson mesh `ficus_surface.ply`; 100k xyz+normals+SH RGB in `ficus_100k.npz` / `.ply`. Note: [SURFACE.md](SURFACE.md).
- [How the human supplies three click groups](issues/10-click-capture-method.md) — JSON of world-xyz clicks (template [clicks.template.json](clicks.template.json)); agent PNG previews; one or more positives per pot/trunk/leaves; negatives only on retry.
- [LLM/MLLM pipeline for three click groups](issues/11-mllm-click-pipeline.md) — Geometry proposes on-cloud candidates; MLLM only accept/swap/resample on an annotated preview; no free-form xyz. Spec: [CLICK_PIPELINE.md](CLICK_PIPELINE.md).
- [Place three click groups on the ficus surface](issues/05-place-click-groups.md) — Accepted P0 clicks; `predict_masks` wrote `mask_{pot,trunk,leaves}.npy` (11.8k / 26.7k / 42.8k). Trunk∩leaves overlap is large; no empty/covers-most retry. Preview: [ficus_100k_part_masks.png](ficus_100k_part_masks.png).
- [Merge masks and lift to Material Tag Tensor](issues/06-merge-and-lift-tags.md) — `material_tags.pt` `(203930,)` int32; IDs 1=pot / 2=trunk / 3=leaves; counts 30 339 / 79 053 / 94 538. Preview: [ficus_gaussians_tags.png](ficus_gaussians_tags.png).
- [Short PhysGaussian MPM Solver run](issues/07-short-mpm-run.md) — Tags loaded; 5-frame `ficus_short.json` run exit 0; positions finite, no explosion. Log: [mpm_short.log](mpm_short.log).
- [Record trial pass or fail](issues/08-record-trial-result.md) — **Pass.** All four bars met. Destination note: [RESULT.md](RESULT.md).

## Not yet specified

_(none — destination reached)_

## Out of scope

- Production integration of PartSAM into `src/` as the lasting tagger.
- What to do after a pass (leave as trial vs a later production map) — beyond this destination; a fresh effort if wanted.
- Other scenes (vasedeck, etc.).
- Full-length ficus wind campaign.
- Expanding `CONTEXT.md` with PartSAM.
- Root README polish from the orientation map.
