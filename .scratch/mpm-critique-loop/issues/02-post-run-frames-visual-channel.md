# Post-run frames a visual channel can see

Type: research
Status: resolved
Blocked by: none

## Question

After a PhysGaussian MPM Solver run, what frame artifacts actually exist that a Motion Critique Loop visual channel (or a human watching) could consume?

Cover, from primary sources only (`src/simulation/runner.py`, `src/rendering/rasterize.py`, `scripts/export_pipeline_data.py`, `digest/` player code, orientation [repo current state](../../agent-orientation/research/01-repo-current-state.md), a ficus config such as `configs/ficus.json`):

1. Who writes frames (Warp/3DGS rasterization vs PIL offsets / mock digest export).
2. Paths, filename pattern, count, and whether they match `frame_num`.
3. What the Digest Dashboard / Dual-Mode Frame Player actually plays vs what the runner writes.
4. What is **not** available today (video file, eval scalars) so the spec does not assume it.

Write findings to `.scratch/mpm-critique-loop/research/02-post-run-frames-visual-channel.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** decide the visual channel’s job (describe vs propose-delta).

## Answer

A visual channel that should see **solver** motion consumes `--render_img` PNGs: Warp advances particles, 3DGS `rasterize` writes `{output_path}/{NNNN}.png` for `frame` in `0 .. frame_num-1` (ficus: 125). Digest’s Dual-Mode player plays a **different** 30-frame PIL JPEG sequence (`digest/data/<model>/frames/frame_NN.jpg`) and has no `<video>`. `output.mp4` exists only if `--compile_video` and ffmpeg succeed; the runner writes no FVD/KVD (those functions do not exist). Do not treat digest frames or eval scalars as post-run solver evidence.

Findings: [research/02-post-run-frames-visual-channel.md](../research/02-post-run-frames-visual-channel.md).
