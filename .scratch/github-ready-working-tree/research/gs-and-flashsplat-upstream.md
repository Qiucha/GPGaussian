# Gaussian Splatting and FlashSplat as upstream

Sources:

- https://github.com/graphdeco-inria/gaussian-splatting README (clone / `--recursive`) and LICENSE.md (Inria/MPII)
- Official `.gitmodules`: https://raw.githubusercontent.com/graphdeco-inria/gaussian-splatting/main/.gitmodules
- https://github.com/florinshen/FlashSplat — local clone `vendor/FlashSplat` origin that URL, HEAD `3e3b147` (2024-09-13); `readme.md`, `LICENSE.md`, `.gitmodules`
- Phys4DGS `src/__init__.py`, `src/segmentation/flashsplat.py`

## Gaussian Splatting (graphdeco-inria)

**License:** Inria and MPII Gaussian-Splatting License — research / non-commercial evaluation; redistribution must include the license and notices ([LICENSE.md](https://raw.githubusercontent.com/graphdeco-inria/gaussian-splatting/main/LICENSE.md)). Do not dump this tree into Phys4DGS.

**Clone** (README):

```shell
git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive
# or git@github.com:graphdeco-inria/gaussian-splatting.git --recursive
```

**Submodules:** `simple-knn` (Inria GitLab), `diff-gaussian-rasterization` (github.com/graphdeco-inria, branch `dr_aa`), `SIBR_viewers`, `fused-ssim`.

**Install (README):** `pip install` the `diff-gaussian-rasterization` and `simple-knn` submodules.

PhysGaussian already vendors this repo as a **submodule** named `gaussian-splatting`. If PhysGaussian is cloned with `--recurse-submodules`, a **second** graphdeco clone is not required for `gs_simulation` / `runner.py`. Official PhysGaussian does `sys.path.append("gaussian-splatting")` and then `from scene.gaussian_model import GaussianModel`, `from gaussian_renderer import render`, `from diff_gaussian_rasterization import ...`.

## FlashSplat (florinshen)

**Origin:** https://github.com/florinshen/FlashSplat  
**Local pin:** `3e3b147`

**License file in the repo:** `LICENSE.md` is the **same Inria/MPII Gaussian-Splatting license** (FlashSplat is a 3DGS-derived tree). Keep that license with the clone; do not re-upload `vendor/FlashSplat`.

**Submodules** (local `.gitmodules`):

- `submodules/simple-knn` → gitlab.inria.fr/bkerbl/simple-knn
- `submodules/diff-gaussian-rasterization` → **github.com/ashawkey/diff-gaussian-rasterization** (not graphdeco)
- `submodules/flashsplat-rasterization` → github.com/florinshen/flashsplat-rasterization

README does not spell a clone one-liner; standard is:

```shell
git clone --recurse-submodules https://github.com/florinshen/FlashSplat.git third_party/FlashSplat
```

Then install its rasterizer submodules (same pattern as 3DGS `pip install -e submodules/...`).

## How Phys4DGS resolves them today

`src/__init__.py` prepends **both** `vendor/gaussian-splatting` and `vendor/FlashSplat` to `sys.path`. Those trees both expose `scene`, `gaussian_renderer`, `utils` — they **collide** if loaded together.

`src/segmentation/flashsplat.py` additionally loads `vendor/FlashSplat/gaussian_renderer/__init__.py` by file path (`flashsplat_render`).

## Consume-as-upstream pattern

Gitignore `vendor/` and `third_party/`. Do not add nested `.git` clones.

| Consumer | Clone | `sys.path` / import |
|---|---|---|
| MPM + `runner.py` | PhysGaussian’s `gaussian-splatting` submodule (from ticket 01) | `third_party/PhysGaussian/gaussian-splatting` only in the simulation process |
| FlashSplat segmentation | Separate FlashSplat clone | Do **not** put FlashSplat on the global `src/__init__.py` path. Point `flashsplat.py` at `os.environ.get("FLASHSPLAT_ROOT", "third_party/FlashSplat")` and load `gaussian_renderer` from that root only |

Env vars (recommended defaults):

- `PHYSGAUSSIAN_ROOT=third_party/PhysGaussian`
- `FLASHSPLAT_ROOT=third_party/FlashSplat`

If someone runs simulation without PhysGaussian, they may clone graphdeco recursively into `third_party/gaussian-splatting` and set `GAUSSIAN_SPLATTING_ROOT` — optional, not required when PhysGaussian is present.

Ticket 05 should gitignore `vendor/`, `third_party/`. Ticket 04 / follow-up import wiring should stop dual `sys.path` inserts in `src/__init__.py`.
