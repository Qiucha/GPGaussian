# PhysGaussian as upstream (not in-tree copies)

Sources:

- Official README (live): https://raw.githubusercontent.com/XPandora/PhysGaussian/master/README.md
- Official repo: https://github.com/XPandora/PhysGaussian
- Official `.gitmodules` (local clone matching README): gaussian-splatting → https://github.com/graphdeco-inria/gaussian-splatting
- MPM solver announced as https://github.com/zeshunzong/warp-mpm (README News, 2023-12-20)
- Local leftover clone `.trash/PhysGaussian` at `8339ed6` (`plane example`, 2025-04-06)
- Official `gs_simulation.py` / `utils/decode_param.py` via raw.githubusercontent.com (2026-08-14)

## License and intended use

PhysGaussian’s GitHub tree has **no LICENSE / LICENSE.md / COPYING** (HTTP 404 on `master`). The README’s intended use is: clone the research code, install its Python env, run `gs_simulation.py` against a 3DGS model + JSON config, cite Xie et al. arXiv:2311.12198.

The nested **gaussian-splatting** submodule is under the Inria/MPII Gaussian-Splatting research license (non-commercial research; redistribution must keep that license). Do not re-upload that tree.

PhysGaussian is a **runnable application repo**, not a pip package. It expects to be the working tree: `sys.path.append("gaussian-splatting")` in official `gs_simulation.py`, and packages `mpm_solver_warp`, `particle_filling`, `utils`.

Clone command from the official README:

```shell
git clone --recurse-submodules git@github.com:XPandora/PhysGaussian.git
```

(HTTPS equivalent: `https://github.com/XPandora/PhysGaussian.git`.)

## Layout vs Phys4DGS copies

| Official path | Phys4DGS path | Class |
|---|---|---|
| `mpm_solver_warp/warp_utils.py` | `src/simulation/mpm_solver/warp_utils.py` | Identical to local clone |
| `mpm_solver_warp/engine_utils.py` | `src/simulation/mpm_solver/engine_utils.py` | Identical to local clone |
| `particle_filling/filling.py` | `src/simulation/particle_filling/filling.py` | Identical to local clone |
| `mpm_solver_warp/mpm_solver_warp.py` | `src/simulation/mpm_solver/solver.py` | Import-path rewrite only |
| `mpm_solver_warp/mpm_utils.py` | `src/simulation/mpm_solver/utils.py` | Import-path rewrite only |
| `utils/camera_view_utils.py` | `src/rendering/camera.py` | Import-path rewrite only |
| `utils/render_utils.py` | `src/rendering/rasterize.py` | Import-path rewrite only |
| `utils/transformation_utils.py` | `src/rendering/transforms.py` | Import-path rewrite only |
| `gs_simulation.py` | `src/simulation/runner.py` | Import-path rewrite + `import src` / Warp init; not a new solver |
| `utils/decode_param.py` | `src/simulation/config.py` | Import rewrite **plus** `materials` dict (also present in the *local* `.trash` clone; **absent** from official `master` `decode_param.py`) |
| `config/*.json` | `configs/*.json` | Scene configs; `vasedeck_multi_material.json` is Phys4DGS-only |

**Keep as Phys4DGS delta (do not treat as upstream):** `src/simulation/lame_params.py`, `src/llm/`, `src/segmentation/`, `src/eval/`, `src/utils/`, tests, the `materials` overlay on config decode, and small helpers such as `gt_depth` on `src/rendering/camera.py`. Official `master` does not define `materials`.

## Consume-as-upstream pattern

Do not git-add `.trash/PhysGaussian` or copies of `mpm_solver_warp/`.

1. Gitignore a clone dir, e.g. `third_party/`.
2. Document:

```shell
git clone --recurse-submodules https://github.com/XPandora/PhysGaussian.git third_party/PhysGaussian
# local working pin used in this workspace: 8339ed6
```

3. At runtime, put `third_party/PhysGaussian` and `third_party/PhysGaussian/gaussian-splatting` on `sys.path` (or `PYTHONPATH`). Import `mpm_solver_warp`, `particle_filling`, and `utils.decode_param` from that tree.
4. Keep a thin Phys4DGS wrapper that reads `materials` and calls `lame_params` / the Segmenter Agent — do not fork the Warp kernels into `src/`.
5. PhysGaussian’s recurse-submodules checkout **already** supplies Gaussian Splatting. A second `vendor/gaussian-splatting` is redundant for MPM/render. FlashSplat stays a **separate** clone (different rasterizer); do not put both GS trees on `sys.path` at once.

Ticket 04 should delete the identical/import-rewritten copies listed above and wire the path/wrapper described here.
