# 03 - Persist filenames and src/segmentation module tree

Type: grilling
Status: resolved
Blocked by: none

## Question

What persist filenames and Python module tree under `src/` does this map implement for the three stages?

Cover: 100k sample path; clicks JSON path; part masks + per-group IoU scalars; `material_tags.pt` (solver-facing name is already spec); Stage 1 throwaway mesh location; CLI entry (`python -m …`); how skip-if-exists is spelled. Not merge policy, not tag IDs, not clone-vs-vendor.

## Answer

Package **`src/segmentation/partsam/`**: `surface.py`, `clicks.py`, `infer.py`, `merge.py`, FPS stand-in in-package, `__main__.py`. CLI: **`python -m src.segmentation.partsam`** with `--model_path` / `--output_dir` (default `data/outputs/partsam/`) and `--stage {surface,clicks,lift}`; default runs 1→2→3. `run_pipeline.sh` calls this once, then the solver.

Persist under `--output_dir` (scene-agnostic names, not `ficus_*`):

| File | Role |
| --- | --- |
| `sample_100k.npz` | 100k \(P_{in}\): `coords`, `normals`, `colors` (uint8), `point_to_face` (trial `predict_masks` passes this) |
| `clicks.json` | Spec JSON (`frame`, `source`, groups pot/trunk/leaves) |
| `part_masks.npz` | Three 100k masks |
| `chosen_iou.json` | One chosen-mask predicted IoU scalar per group |
| `poisson_mesh.ply` | Throwaway debug mesh (gitignored with `data/`; not solver input) |
| throwaway PNGs | Same dir (`click_candidates.png`, etc.) |

Solver-facing tags: **`data/outputs/tags/material_tags.pt`** so `--tags_path` stays as today.

Skip-if-exists: Stage 1 if `sample_100k.npz` exists; Stage 2 if `clicks.json` exists and each of pot/trunk/leaves has one or more positives (do not skip empty/partial); Stage 3 skip `material_tags.pt` only when the caller asked to reuse tags.

## Comments
