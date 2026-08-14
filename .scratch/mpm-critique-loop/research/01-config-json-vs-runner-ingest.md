# Config JSON vs runner ingest (without rewriting the Material Tag Tensor)

Primary sources (2026-08-14): `src/llm/schema.py` (`PhysGaussianLLMConfig`, `MaterialProperties`, `MaterialTagDefinition`); `src/llm/translator.py` (`MotionTranslator.translate`, `SYSTEM_PROMPT_TEMPLATE`); `src/llm/motion_library.py` (`get_core_motion_exemplars`); `src/simulation/runner.py`; `src/simulation/config.py` (`decode_param_json`); `src/simulation/lame_params.py` (`compute_per_particle_lame_params`); `configs/ficus.json`; parent [spec.md](../../llm-motion-physgaussian/spec.md) Implementation Decisions §1–§2. Ingest buckets come from the module `config.py` imports: `.trash/PhysGaussian/utils/decode_param.py` (`decode_param_json`, `set_boundary_conditions`) and `.trash/PhysGaussian/mpm_solver_warp/mpm_solver_warp.py` (`set_parameters_dict`, `finalize_mu_lam`). Does not decide replace-vs-patch or the critique-entry seam.

## 1. What the translator emits (not the dataclass)

`PhysGaussianLLMConfig` is a dataclass. Fields: `substep_dt`, `frame_dt`, `frame_num`, `n_grid`, `grid_lim`, `g`, `grid_v_damping_scale`, `rpic_damping`, `opacity_threshold`, `materials` (`Dict[str, Dict[str, Any]]`), `material_segmentation_rules`, `boundary_conditions`. No `to_dict` / serializer. (`src/llm/schema.py`, class `PhysGaussianLLMConfig`.)

`MotionTranslator.translate` with `mock_llm=True` (the only implemented path; live call is `NotImplementedError`) returns the retrieved exemplar’s `"config"` dict and `"reasoning"`, then calls `validate_physgaussian_config`. It never constructs a `PhysGaussianLLMConfig` instance. (`src/llm/translator.py`, `translate`.)

Those configs are the four `get_core_motion_exemplars()` payloads. Shared keys: `substep_dt`, `frame_dt`, `frame_num`, `n_grid`, `g`, `materials` (string-int keys `"0"` / `"1"` / `"2"` → `{E, nu, density, material_type}`; tearing also `yield_stress` on tag `"2"`), `boundary_conditions`. They omit `grid_lim`, `opacity_threshold`, `grid_v_damping_scale`, `rpic_damping`, `material_segmentation_rules`, camera keys, preprocessing keys (`rotation_*`, `sim_area`, `scale`, `particle_filling`), top-level `material` / scalar `E` / `nu` / `density`, and any tag-file path. (`src/llm/motion_library.py`.)

The system prompt tells the model to emit JSON “adhering to the PhysGaussianLLMConfig schema” and documents BC types `particle_impulse`, `cuboid`, `enforce_particle_velocity_rotation`. (`src/llm/translator.py`, `SYSTEM_PROMPT_TEMPLATE`.) Exemplars also use `enforce_particle_translation`. (`src/llm/motion_library.py`, `exemplar_tearing_disruption_04`.) Prompt text does not name `surface_collider`.

Parent spec: schema “extends standard PhysGaussian JSON” with `materials` mapping `"0"` / `"1"` / `"2"` to `E`, `nu`, `density`, `material_type`, `yield_stress`; plus `material_segmentation_rules`; plus `boundary_conditions` including `particle_impulse`, `cuboid`, `enforce_particle_velocity_rotation`, `surface_collider`, `enforce_particle_translation`. Example JSON in that section has no `material_type` on materials and no `material_segmentation_rules` key. (`../llm-motion-physgaussian/spec.md`, Implementation Decisions §1.)

`material_segmentation_rules` exists only as the dataclass default `[]`. (`src/llm/schema.py`.) It is not in exemplars and is not read by runner ingest (below).

`MaterialTagDefinition` / `SegmenterExecutionPlan.materials` is a **list** of `{tag_id, name, E, nu, density, material_type, description}` — a different shape from the LLM `materials` dict. (`src/llm/schema.py`.) The translator does not emit that list.

## 2. What the runner loads

`--config` is a JSON file. `--tags_path` is a CLI argument (`Path to material_tags.pt`), default `None`. No JSON field names a tag tensor. (`src/simulation/runner.py`, argparse and tag load.)

JSON ingest is `decode_param_json(args.config)` from `src/simulation/config.py`: call upstream `utils.decode_param.decode_param_json`, then if `"materials"` is in the file, set `material_params["materials"] = {int(k): v for k, v in ...}`; else `setdefault("materials", None)`.

The clone decoder **already** does the same `int(k)` overlay (or `None`). (`src/simulation/config.py`; `.trash/PhysGaussian/utils/decode_param.py`, `decode_param_json`.) Phys4DGS’s extra pass is redundant with this clone, not a second table.

Upstream decode splits the file into:

| Bucket | JSON keys it copies (defaults if omitted) |
|---|---|
| `material_params` | `material` (`"jelly"`), `materials` (dict→int keys, or `None`), `grid_lim` (`2.0`), `n_grid` (`50`), top-level `nu` (`0.4`), `E` (`1e5`), `yield_stress`, `hardening`, `xi`, `friction_angle`, `plastic_viscosity`, `g` (`9.8` scalar default if omitted), `density` (`200.0`), `rpic_damping`, `pic_damping`, `softening`, `opacity_threshold`, `grid_v_damping_scale`, `additional_material_params` (spatial boxes requiring `point`/`size`/`E`/`nu`) |
| `bc_params` | `boundary_conditions` (or `{}` if absent) |
| `time_params` | `substep_dt` (`1e-4`), `frame_dt` (`1e-2`), `frame_num` (`100`) |
| `preprocessing_params` | `opacity_threshold` (`0.02`), `rotation_degree`/`rotation_axis` (`[]`), `sim_area` (`None`), `scale` (`1.0`), `particle_filling` (`None` or filled sub-defaults) |
| `camera_params` | `mpm_space_viewpoint_center`, `mpm_space_vertical_upward_axis`, `default_camera_index`, `show_hint`, `init_azimuthm`/`elevation`/`radius`, `delta_a`/`e`/`r`, `move_camera` |

It does **not** copy `material_segmentation_rules`. (`decode_param.py`.)

`configs/ficus.json` is a runnable scene file: `opacity_threshold`, `rotation_degree`/`axis`, `substep_dt` / `frame_dt` / `frame_num`, `materials` keyed `"1"` / `"2"` / `"3"` (only `E`, `nu`, `density` — no `material_type`), `n_grid`, top-level `"material": "jelly"`, `density`, `g`, damping, BCs (`cuboid`, two `particle_impulse`s), camera keys. No `grid_lim`, no tag path, no `material_segmentation_rules`.

Runner uses:

- Tags: `torch.load(args.tags_path)` if the path exists; else `zeros(N, int32)` on Gaussian count. Then opacity mask, optional `sim_area` mask, optional particle-fill nearest-neighbor tag copy. (`runner.py`.)
- `preprocessing_params["opacity_threshold"]`, rotations, `sim_area`, `scale`, `particle_filling`.
- `material_params["n_grid"]`, `grid_lim`, `"material"` (sand volume flag `unifrom=material_params["material"] == "sand"`), optional `"materials"` map, scalar `E`/`nu`/`density` as fill defaults.
- `set_boundary_conditions(mpm_solver, bc_params, time_params)` then the frame loop on `time_params["substep_dt"|"frame_dt"|"frame_num"]`. (`runner.py`.)

`set_boundary_conditions` types: `cuboid`, `particle_impulse`, `bounding_box`, `enforce_particle_translation`, `surface_collider`, `release_particles_sequentially`, `enforce_particle_velocity_rotation`. Else `TypeError`. (`decode_param.py`.) `particle_impulse` passes `dt=time_params["substep_dt"]`. Translator prompt names a subset; exemplars use cuboid / impulse / rotation / translation; ficus uses cuboid + impulse. Parent spec also names `surface_collider`; that type is accepted at ingest, not present in translator emit.

## 3. Schema names vs runner reads

| Field | Schema / exemplars | Runner ingest |
|---|---|---|
| `materials` | dict of string tags → `E`, `nu`, `density`, `material_type`, optional `yield_stress` (`schema.py`; exemplars; parent spec §1) | Overlay into `material_params` with `int(k)`; per-tag loop copies **only** `E`, `nu`, `density` (`config.py`; `runner.py`) |
| `material` (top-level string) | not on `PhysGaussianLLMConfig`; ficus `"jelly"` | sand volume flag; `set_parameters_dict` constitutive switch (`runner.py`; clone `MPM_Simulator_WARP.set_parameters_dict`) |
| `boundary_conditions` | list of typed dicts | `bc_params` → `set_boundary_conditions` |
| `substep_dt`, `frame_dt`, `frame_num` | schema + exemplars | `time_params`; impulse BC also uses `substep_dt` |
| `n_grid`, `g` | schema + exemplars | `material_params`. Schema default `n_grid=100`; clone default **50** if the key is omitted |
| `grid_lim` | schema default `2.0`; **absent** from exemplars and ficus | clone default `2.0` if omitted |
| `opacity_threshold`, `grid_v_damping_scale`, `rpic_damping` | schema defaults; **absent** from exemplars; present on ficus | damping → `material_params`; opacity also → `preprocessing_params` |
| `material_segmentation_rules` | schema default `[]`; parent spec §1 | **unread** |
| tag tensor path | **not named** | `--tags_path` only (`runner.py`) |
| camera / rotation / `sim_area` / fill | not in translator emit | ficus + clone decode; runner uses them |
| `additional_material_params` | not in translator | spatial boxes in clone decode / `set_parameters_dict`; **not** the tag table |

Tag ID **namespace mismatch**: exemplars and parent spec example use `"0"` / `"1"` / `"2"`. Ficus uses `"1"` / `"2"` / `"3"`. Overlay does `int(k)`; assignment is `mpm_init_tags == tag_id`. A `"0"` table does not retune ficus tags `1/2/3`. (`motion_library.py`; `ficus.json`; `config.py`; `runner.py`.)

## 4. How tag IDs become Lamé parameters

Two artifacts:

1. **Material Tag Tensor** — `material_tags.pt` via `--tags_path`. Per-Gaussian int IDs, filtered with opacity / `sim_area`, NN-copied onto filled particles. Missing path → all zeros. (`runner.py`.)
2. **JSON `materials` table** — tag ID → mechanical properties. (`config.py` overlay; clone decode; `ficus.json`.)

If `"materials"` is present and not `None`, runner builds `E_tensor` / `nu_tensor` / `density_tensor` the same shape as `mpm_init_tags`, filled with scalar defaults `E` / `nu` / `density` (runner `.get` defaults `1e5` / `0.4` / `200.0` if those keys missing — matching clone decode defaults), then for each table entry writes those three scalars onto `mpm_init_tags == tag_id`. Stores them as `material_params["E_array"|"nu_array"|"density_array"]`, then `load_initial_data_from_torch`, `set_parameters_dict(material_params)`, `finalize_mu_lam()`. (`runner.py`.)

`set_parameters_dict` prefers `E_array` / `nu_array` / `density_array` over scalar `E` / `nu` / `density`. `finalize_mu_lam` launches `compute_mu_lam_from_E_nu` on all particles. (`mpm_solver_warp.py`.) That is the run-time Lamé conversion: μ and λ from per-particle E and ν **after** tag lookup, not from `lame_params.py`.

`src/simulation/lame_params.py` `compute_per_particle_lame_params` maps string tags → μ = E/(2(1+ν)), λ = Eν/((1+ν)(1−2ν)), plus density; unassigned particles (density still 0) fall back to tag `0`. **The runner does not call this.** Parent spec still describes evaluating μ/λ per particle in Warp arrays (`../llm-motion-physgaussian/spec.md` §2) — that matches `finalize_mu_lam`, not the unused helper.

Per-tag `material_type` and `yield_stress` in translator JSON are **not** applied in the runner’s tag loop. Global `yield_stress` applies only if present at JSON **top** level (clone decode → `material_params` → homogeneous `set_parameters_dict` fill). Ficus has neither per-tag type nor top-level `E`/`nu` (only top-level `density` and `material`).

If the `materials` overlay is `None` (key absent), the tag tensor is still loaded but never used for property lookup; the solver gets homogeneous scalars.

## 5. What a loop may patch in JSON vs what needs a new tensor

**JSON-only (same `material_tags.pt`, same `--tags_path`):**

- Existing keys in `materials`: `E`, `nu`, `density` for IDs that already appear on the tensor (ficus: `1` / `2` / `3`). That retunes which ID maps to which Lamé/density without rewriting tags. (`runner.py` mask-assign; `ficus.json`.)
- `boundary_conditions` list (forces, cuboid anchors, times, extra types the clone dispatcher already accepts).
- `substep_dt`, `frame_dt`, `frame_num`.
- Homogeneous fallbacks and grid: top-level `E`, `nu`, `density`, `material`, `n_grid`, `g`, damping, `grid_lim`.
- Scene extras the runner already reads from JSON: opacity, rotations, `sim_area`, fill, camera.

**Does not change assignment without a new tensor:**

- Which particles hold which ID. That is the int array from `--tags_path`. (`runner.py`.)
- Introducing a **new** tag ID in JSON with no particles holding that ID: overlay assigns to an empty mask; those properties never attach.
- Remapping IDs that are **not** on the tensor (e.g. writing `"0"` while the file is `1/2/3`): no particles match; they keep scalar defaults.
- `material_segmentation_rules`: unused at ingest; editing them does not retag.

A new tensor is required to change per-particle **membership** (split/merge regions, new parts, different ID layout). Changing **constitutive numbers and BCs/timesteps for existing IDs** is JSON.

## 6. Ingest contract a critique loop can rely on (facts only)

Post-run replay is: same `--model_path`, same `--tags_path`, a JSON file `--config` that still has a `materials` map whose integer keys match the tensor’s IDs, plus `boundary_conditions` and time keys the clone decoder already understands. Translator-shaped JSON (`"0"` / `"1"` / `"2"`, no camera / opacity / rotation / top-level `material`) is **not** a drop-in replacement for `configs/ficus.json`; ficus-shaped JSON already is. (`runner.py`; `ficus.json`; `motion_library.py`.)
