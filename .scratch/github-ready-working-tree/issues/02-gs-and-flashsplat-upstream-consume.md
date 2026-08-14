# 02 - How to consume Gaussian Splatting and FlashSplat as upstream

Type: research
Status: resolved
Blocked by: none

## Question

`vendor/gaussian-splatting` and `vendor/FlashSplat` are nested clones (~178M) that must not be dumped into GitHub. What do the official repositories specify for clone/install, licenses, and submodules, and what consume-as-upstream pattern should Phys4DGS document (clone URLs, recurse-submodules, expected local path, how `src/__init__.py` and `src/segmentation/flashsplat.py` should resolve them without vendoring)?

Primary sources: https://github.com/graphdeco-inria/gaussian-splatting and https://github.com/florinshen/FlashSplat (README, LICENSE, .gitmodules).

## Answer

Clone graphdeco 3DGS with `--recursive` (Inria/MPII research license); PhysGaussian’s submodule already provides it for simulation. Clone FlashSplat separately with `--recurse-submodules` (local pin `3e3b147`; same Inria license file; ashawkey + flashsplat rasterizer submodules). Stop putting both trees on global `sys.path` — simulation uses PhysGaussian’s `gaussian-splatting`, segmentation uses `FLASHSPLAT_ROOT`. Details: [research/gs-and-flashsplat-upstream.md](../research/gs-and-flashsplat-upstream.md).
