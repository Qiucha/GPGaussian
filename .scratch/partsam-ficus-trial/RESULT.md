# Ficus PartSAM trial — RESULT

**Pass.** PartSAM produced an ingestible Material Tag Tensor for `ficus_whitebg`, and a 5-frame PhysGaussian MPM Solver run did not explode. This is a throwaway trial, not a production tagger in `src/`.

Recipe: [PartSAM trial design (scene, I/O, success)](../agent-orientation/issues/06-partsam-trial-design.md). Map: [Ficus PartSAM trial](map.md).

## Pass bar

| Criterion | Score | Evidence |
| --- | --- | --- |
| `material_tags.pt` length = Gaussian count | **pass** | `(203930,)` int32 = `gaussian_xyz.npy` / iter-60000 PLY. [Merge masks and lift to Material Tag Tensor](issues/06-merge-and-lift-tags.md), [tag_lift_stats.json](tag_lift_stats.json) |
| pot / trunk / leaves each non-trivial; trunk > 1 000 | **pass** | pot 30 339, **trunk 79 053**, leaves 94 538 (IDs 1 / 2 / 3). Preview: [ficus_gaussians_tags.png](ficus_gaussians_tags.png) |
| runner loaded tags | **pass** | `--tags_path` the trial tensor; log prints shape and per-tag counts before `src.simulation.runner`. [mpm_short.log](mpm_short.log), [Short PhysGaussian MPM Solver run](issues/07-short-mpm-run.md) |
| 5–10-frame run did not immediately explode | **pass** | `frame_num` 5, exit 0, Warp CUDA; ply positions finite, absmax 1.50 → 1.48; frames still a coherent ficus. [mpm_short_check.json](mpm_short_check.json), [mpm_short/0000.png](mpm_short/0000.png)–[0004.png](mpm_short/0004.png) |

## What ran

Throwaway Screened Poisson surface → 100k xyz+normals+SH RGB → three click groups (geometry + MLLM accept of P0) → `predict_masks` → priority merge trunk > leaves > pot → nearest-neighbor onto Gaussian means → short `configs/ficus.json` MPM (`ficus_short.json`).

Clicks: [clicks.json](clicks.json). Masks: `mask_{pot,trunk,leaves}.npy`. Tags: [material_tags.pt](material_tags.pt). Env: [ENV.md](ENV.md).

## Caveats (not fail)

- PartSAM trunk∩leaves overlap was 23 038 of 100k; merge gave those points to trunk, so the trunk tag is large relative to a thin stem.
- `torkit3d` was a PyTorch FPS stub; apex/pointops were not compiled (`predict_masks` does not import them).
- Opacity threshold dropped 203 930 Gaussians to 171 553 MPM particles (same as a normal ficus run).
- Full-length wind, other scenes, and wiring PartSAM into `src/` were out of scope.

A later effort can decide whether to leave this as a trial or chart a production tagging path.
