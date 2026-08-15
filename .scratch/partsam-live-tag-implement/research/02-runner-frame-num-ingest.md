# How the runner ingests `frame_num`

Primary sources (2026-08-14): [`src/simulation/runner.py`](../../../src/simulation/runner.py); [`src/simulation/config.py`](../../../src/simulation/config.py) (`decode_param_json`); PhysGaussian [`utils/decode_param.py`](../../../.trash/PhysGaussian/utils/decode_param.py) (`decode_param_json`, `set_boundary_conditions`) via `ensure_simulation_path()` → `.trash/PhysGaussian`; [`configs/ficus.json`](../../../configs/ficus.json); [`scripts/run_pipeline.sh`](../../../scripts/run_pipeline.sh). Does **not** implement a CLI.

`frame_num` is not a runner constant. It is copied from the `--config` JSON into `time_params["frame_num"]` and used as `range(frame_num)` for the MPM + optional render loop. No argparse flag, env var, or `run_pipeline.sh` argument already overrides time keys. `configs/ficus.json` sets `"frame_num": 125`. The smallest in-process override without editing that file is writing `time_params["frame_num"]` after decode (a new flag on `runner.py`); a different `--config` path is the only override that exists today.

## 1. How `frame_num` is loaded and used

`python -m src.simulation.runner` requires `--config` (a JSON path). Immediately after parse it unpacks five dicts from `decode_param_json(args.config)`: `material_params`, `bc_params`, `time_params`, `preprocessing_params`, `camera_params`. (`runner.py` argparse `--config`; `decode_param_json` call.)

`src/simulation/config.py` `decode_param_json` calls upstream `_upstream_decode_param_json(json_file)`, then overlays JSON `"materials"` onto `material_params` (int keys) or `setdefault("materials", None)`. It does **not** read or rewrite `time_params`. (`config.py`.)

Upstream `decode_param_json` (`utils.decode_param`, PhysGaussian root on `sys.path`) builds `time_params` from the same file:

| Key | If present in JSON | Else |
|---|---|---|
| `substep_dt` | `sim_params["substep_dt"]` | `1e-4` |
| `frame_dt` | `sim_params["frame_dt"]` | `1e-2` |
| `frame_num` | `sim_params["frame_num"]` | `100` |

(`.trash/PhysGaussian/utils/decode_param.py`, `decode_param_json` time-step block.)

The runner later binds locals and loops:

- `substep_dt = time_params["substep_dt"]`
- `frame_dt = time_params["frame_dt"]`
- `frame_num = time_params["frame_num"]`
- `step_per_frame = int(frame_dt / substep_dt)`
- `for frame in tqdm(range(frame_num)):` — camera, `initialize_resterize`, then `for step in range(step_per_frame): mpm_solver.p2g2p(...)`. Optional ply/h5 at `frame + 1`. Optional `--render_img` PNG `{output_path}/{NNNN}.png` (zero-padded 8-char name). (`runner.py` simulation loop.)

Loop bound is therefore **exactly** decoded `frame_num` (indices `0 .. frame_num-1`). Nothing else in `runner.py` assigns `frame_num`.

`set_boundary_conditions(mpm_solver, bc_params, time_params)` runs **before** that loop. For `particle_impulse` it passes `dt=time_params["substep_dt"]` only; it does not read `frame_num`. (`decode_param.py` `set_boundary_conditions`; `runner.py` call site.) Overriding `frame_num` after decode does not change BC registration. Simulated span is `frame_num * frame_dt`; a 5-frame ficus run is `5 * 4e-2 = 0.2` s, so the second ficus impulse (`"start_time": 2.0`) never starts. (`ficus.json` `boundary_conditions`; loop as above.)

## 2. Whether any CLI already overrides time params

`runner.py` argparse flags: `--model_path`, `--output_path`, `--config`, `--output_ply`, `--output_h5`, `--render_img`, `--compile_video`, `--white_bg`, `--debug`, `--tags_path`. None name `frame_num`, `frame_dt`, or `substep_dt`. (`runner.py` `ArgumentParser`.)

Upstream `gs_simulation.py` uses the same flag list (including `--tags_path`); no time override there either. (`.trash/PhysGaussian/gs_simulation.py` argparse.)

`scripts/run_pipeline.sh` step 4 invokes the runner with a **fixed** `--config "$CONFIG_DIR/ficus.json"` plus `--model_path`, `--output_path`, `--tags_path`, `--render_img --compile_video`. The shell has no extra positional or flag for time. (`run_pipeline.sh`.)

The only existing way to change `frame_num` without editing `configs/ficus.json` is a **different `--config` path** (another JSON that still has the rest of the scene). That is a whole-file swap, not a time override. This effort’s standing note is that `run_pipeline.sh` must not point at a smoke config. (`run_pipeline.sh`; map standing on `ficus.json` 125.)

## 3. What `configs/ficus.json` sets for `frame_num`

Top-level time keys on [`configs/ficus.json`](../../../configs/ficus.json) (2026-08-14):

- `"substep_dt": 5e-6`
- `"frame_dt": 4e-2`
- `"frame_num": 125`

With those values, `step_per_frame = int(4e-2 / 5e-6) = 8000` `p2g2p` calls per outer frame, 125 outer frames. (`ficus.json`; `runner.py` `step_per_frame`.)

## Smallest override seam (do not implement here)

Mutate `time_params["frame_num"]` **after** `decode_param_json(args.config)` and **before** the `range(frame_num)` loop. That dict is the only source the loop reads; `config.py` and upstream decode need no change; `configs/ficus.json` can stay 125. A new optional argparse on `runner.py` (absent today) is the smallest code surface. Leave `run_pipeline.sh` pointed at `configs/ficus.json`.

Do not treat a second checked-in JSON as the intended seam for this effort’s 5-frame bar.
