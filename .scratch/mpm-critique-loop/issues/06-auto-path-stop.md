# Auto-path stop for the Motion Critique Loop

Type: grilling
Status: resolved
Blocked by: none

## Question

The default next PhysGaussian MPM Solver run is **human-gated**. The spec still names an auto-rerun path. What stops that path?

Cover: max iterations N; whether anything besides CFL rejection counts as an automatic stop; whether “user says stop” is the only non-CFL halt. Do not design unimplemented FVD/KVD gates. Use `/grilling`.

## Answer

**Auto-rerun path:** after a human `critique` that passes CFL/schema, loop Warp → `critique` with the **same** human text and new `--render_img` paths. Default mode does not enter this loop (human-gated).

**Stops:**
- **N completed solver runs** (parameter, **default 3**). The first auto-started Warp counts as 1. After run N, do not auto-start N+1; last frames wait for a new human-gated turn.
- **CFL/schema reject** (`validate_physgaussian_config` `ValueError`, omit-invalid / frozen `materials` key set): do not start Warp. **One** inner `critique` retry with the same human text, previous JSON, and the validator error string (no new frames). If that still fails, stop the auto path.
- **User interrupt** — the only other halt.

Not stops: FVD/KVD/PSNR/etc.; visual-channel “looks done”; missing frame paths (skip describe, do not halt). Inner CFL retries do not count toward N. Not Segmenter Agent refinement.
