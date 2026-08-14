# Post-run frames a visual channel can see

Primary sources (2026-08-14): [`src/simulation/runner.py`](../../../src/simulation/runner.py); [`src/rendering/rasterize.py`](../../../src/rendering/rasterize.py); [`scripts/export_pipeline_data.py`](../../../scripts/export_pipeline_data.py); [`digest/app.js`](../../../digest/app.js); [`digest/index.html`](../../../digest/index.html); [`configs/ficus.json`](../../../configs/ficus.json); [`scripts/run_simulation.sh`](../../../scripts/run_simulation.sh). Supporting (imports / wrappers / eval / ignore rules): [`src/upstream.py`](../../../src/upstream.py); leftover PhysGaussian [`utils/render_utils.py`](../../../.trash/PhysGaussian/utils/render_utils.py) (`initialize_resterize`); [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh); [`src/eval/evaluate_realism.py`](../../../src/eval/evaluate_realism.py); [`scripts/verify_digest_assets.py`](../../../scripts/verify_digest_assets.py); [`.gitignore`](../../../.gitignore); glossary [CONTEXT.md](../../../CONTEXT.md) Dual-Mode Frame Player. Secondary cache only: orientation [01-repo-current-state.md](../../agent-orientation/research/01-repo-current-state.md) — verified against the files above. Does not decide the visual channel’s job (describe vs propose-delta). No implementation.

## 1. Who writes frames

**PhysGaussian MPM Solver run (watchable solver motion).** Warp steps particles; 3DGS rasterization paints pixels. [`runner.py`](../../../src/simulation/runner.py) constructs `MPM_Simulator_WARP`, then in `for frame in tqdm(range(frame_num))` calls `mpm_solver.p2g2p` `step_per_frame` times. Only if `--render_img`: export `x` / covariance / `R` to torch, inverse-transform into world space, `convert_SH`, then `rasterize(...)` (means, precomputed colors, opacities, `cov3D_precomp`). The RGB tensor is `permute`d, `cv2.cvtColor(..., COLOR_BGR2RGB)`, and `cv2.imwrite`’d as PNG. Warp does not write images.

[`src/rendering/rasterize.py`](../../../src/rendering/rasterize.py) is a star-re-export of PhysGaussian `utils.render_utils` after `ensure_simulation_path()` ([`src/upstream.py`](../../../src/upstream.py): PhysGaussian root then its `gaussian-splatting` on `sys.path`). The runner does `from src.rendering.rasterize import *` and also imports `GaussianRasterizer` from `diff_gaussian_rasterization`. Leftover clone `.trash/PhysGaussian/utils/render_utils.py`: `initialize_resterize` builds `GaussianRasterizationSettings` and returns `GaussianRasterizer(...)`. Orientation: MPM frames use 3DGS `GaussianRasterizer`, not FlashSplat — matches this import graph.

**Digest export (not a solver run).** [`scripts/export_pipeline_data.py`](../../../scripts/export_pipeline_data.py) never invokes the runner, Warp, or `rasterize`. It loads a 3DGS checkpoint, downsamples to ≤8000 points, runs `SegmenterAgent(mock_llm=True)`, then for `t in range(30)` builds `Image.new("RGB", (640, 480), ...)` and `ImageDraw` ellipses with sine/cosine displacements on tags 1 and 2. Overlay text says “PhysGaussian MPM Simulation”. Orientation names these **PIL 2D fake “MPM” frames, not Warp**.

Optional non-image dumps from the same runner loop: `--output_ply` / `--output_h5` call `save_data_at_frame` under `{output_path}/simulation_ply` (index 0 before the loop, then `frame + 1` after each iteration). Particle archives, not a visual channel.

## 2. Paths, filename pattern, count vs `frame_num`

**Runner PNGs** (only when `--render_img`; `assert args.output_path is not None`):

| | |
|---|---|
| Directory | `args.output_path` (flat; no `frames/` subdirectory) |
| Pattern | `os.path.join(args.output_path, f"{frame}.png".rjust(8, "0"))` → four-digit pad + `.png` for `frame` 0–999 (`0000.png`, `0001.png`, …) |
| Count | `range(frame_num)` → **exactly `frame_num` PNGs**, indices `0 .. frame_num-1` |

`frame_num` is `time_params["frame_num"]` from decoded scene JSON. [`configs/ficus.json`](../../../configs/ficus.json): `"frame_num": 125`, `"frame_dt": 4e-2`, `"substep_dt": 5e-6`. A ficus `--render_img` run therefore writes 125 PNGs. Without `--render_img`, the MPM loop still runs and writes **no** images.

Each PNG is written **after** that iteration’s `p2g2p` substeps, not a rest pose. There is no extra PNG for `t = 0` before the first `frame_dt` of physics.

[`runner.py`](../../../src/simulation/runner.py) `--output_path` default is `None`. [`scripts/run_simulation.sh`](../../../scripts/run_simulation.sh) sets `OUTPUT_PATH="$PROJECT_ROOT/data/outputs/simulated_video"` and passes `--render_img --compile_video`. [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh) uses `$OUTPUT_DIR/simulated_video` the same way (`OUTPUT_DIR=data/outputs`). That directory is a **script convention**, not a runner default.

This clone’s gitignored `data/outputs/simulated_video/` (2026-08-14) contains `0000.png` … `0124.png` (125 files) plus `output.mp4`, matching ficus `frame_num`. Root [`.gitignore`](../../../.gitignore) ignores `data/`.

**Digest JPEGs** (exporter only):

| | |
|---|---|
| Directory | `digest/data/<model_name>/frames/` |
| Pattern | `frame_{t:02d}.jpg` (`frame_00.jpg` … `frame_29.jpg`) |
| Count | **hardcoded `num_frames = 30`**, independent of JSON `frame_num` |

[`digest/data/manifest.json`](../../../digest/data/manifest.json) (gitignored with `digest/data/`) records `"num_frames": 30` per model. This clone: six models × 30 JPEGs = 180 `frame_*.jpg`. [`scripts/verify_digest_assets.py`](../../../scripts/verify_digest_assets.py) asserts exactly 30 `frame_*.jpg` per model.

A ficus solver run (125 PNGs under `simulated_video/`) and digest ficus (30 JPEGs under `digest/data/ficus_whitebg/frames/`) do not share path, extension, stem, or length.

## 3. Digest Dashboard / Dual-Mode Frame Player vs runner output

The player is `<img id="frame-image">` plus `<input type="range" id="frame-slider" min="0" max="29">` ([`digest/index.html`](../../../digest/index.html)). There is **no** `<video>` element (search of `digest/` for `video` / `<video` is empty aside from the Dual-Mode comment in [`digest/app.js`](../../../digest/app.js) header).

[`digest/app.js`](../../../digest/app.js) `updateFrameDisplay`: `imgEl.src = data/${currentModelId}/frames/frame_${padFrame}.jpg` with `padStart(2, "0")`; counter `Frame NN / 29`; time `(currentFrame / 29) * 0.4` seconds (matches the exporter overlay `t_norm * 0.4`). Playback is `setInterval` wrapping `currentFrame = (currentFrame + 1) % 30`. The player does not read `--output_path`, `%04d.png`, or `output.mp4`.

Glossary [CONTEXT.md](../../../CONTEXT.md) Dual-Mode Frame Player: “canvas-based single-frame image scrubbing … **alongside HTML5 video preview**.” The UI implements `<img>` + slider only. Orientation: Dual-Mode is image scrubbing; digest trajectory images are the exporter’s PIL animation, not Warp renders. Frame JPEGs are produced only if someone ran `export_pipeline_data.py`; they are not a side effect of `runner.py`.

A human (or VLM) watching **solver** motion must consume the runner PNGs (or an ffmpeg mp4 if compiled). Watching the Digest player is watching the mock 30-frame PIL clip.

## 4. What is not available today (do not assume in the spec)

**Video file is optional, not a guaranteed post-run artifact.** `output.mp4` is written only if **both** `--render_img` and `--compile_video`: `os.system(f"ffmpeg -framerate {fps} -i {args.output_path}/%04d.png ... {args.output_path}/output.mp4")` with `fps = int(1.0 / time_params["frame_dt"])`. For ficus, `int(1.0 / 4e-2)` = 25. `%04d.png` matches the `rjust(8, "0")` names for frames 0–999. `os.system` does not fail the Python process if ffmpeg is missing. [`run_simulation.sh`](../../../scripts/run_simulation.sh) then `cp "$OUTPUT_PATH/output.mp4" "$EXP_DIR/"` (fails the script via `set -e` if the mp4 was never created).

Git: [`.gitignore`](../../../.gitignore) has `*.mp4` and `data/`; `git ls-files '*.mp4'` is empty. Orientation’s “no archived `output.mp4` in the tree” is true for **tracked** files. This clone’s local disk (2026-08-14) does have gitignored copies (`data/outputs/simulated_video/output.mp4`, four `data/experiments/exp_*/output.mp4`). Spec must treat video as an optional ffmpeg product of a flagged run, not as something the repo or every runner invocation always leaves behind.

**Eval scalars are not produced by a solver run.** [`runner.py`](../../../src/simulation/runner.py) does not import or call `src/eval/`. [`evaluate_realism.py`](../../../src/eval/evaluate_realism.py) implements `compute_kabsch_alignment`, `compute_trajectory_mse_kabsch`, and `compute_2afc_statistics` only. The module docstring names FVD/KVD; there are **no** `FVD` / `KVD` / `PSNR` / `SSIM` / `LPIPS` functions (orientation, verified). Kabsch/2AFC exist as library functions; they are not written next to frames.

**Digest frames are not solver evidence.** Separate mock export; count ≠ `frame_num`; not 3DGS rasterizations of Warp state.

**Default runner CLI writes no rasterized sequence.** `--render_img` is opt-in. A visual channel that needs images depends on that flag (and a non-`None` `--output_path`), which the `.sh` helpers turn on and a bare `python -m src.simulation.runner` does not.
