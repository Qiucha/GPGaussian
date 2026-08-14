# Key Design Decisions Log

This document tracks the major technical decisions, workarounds, and optimizations applied to the Phys4DGS pipeline.

## 1. 2D-to-3D Mask Assignment Logic (FlashSplat)
* **Problem:** LangSAM's 2D masks often overlapped (e.g., "leaves" covering "wood"), and the default area-based priority caused large noisy masks to overwrite thin structural masks.
* **Decision:** Replaced the generic area priority with a **Hardcoded Semantic Priority**. We explicitly ordered the Z-stack so that thin structures (`"stem"`, `"wood"`, `"branch"`) always overwrite larger blobs (`"leaves"`, `"pot"`).

## 2. Dependency Resolution (Grounded SAM 2 vs PyTorch)
* **Problem:** We attempted to upgrade to Grounded SAM 2 for temporal tracking to improve the 2D trunk masks.
* **Decision:** We discovered a fundamental C++ incompatibility. Grounding DINO's custom CUDA extensions fail to compile on `PyTorch >= 2.3.1` (which SAM 2 strictly requires). We decided to **abandon Grounded SAM 2** and maintain the original `physgauss` environment to avoid rewriting underlying C++ APIs.

## 3. Trunk Segmentation (3D Color Heuristic)
* **Problem:** Even with semantic priority, the 2D LangSAM models failed to reliably detect the thin, complex Ficus trunk (finding only ~10-100 Gaussians). A geometric cylinder heuristic also failed because the branches spread out too wide.
* **Decision:** We implemented a purely **3D Color Heuristic** based on Gaussian Splatting Spherical Harmonics (SH). By converting the base SH DC component to RGB, we applied a computational filter (`R > G` and `R > B` for wood; `G > R` and `G > B` for leaves). This successfully captured **36,058 trunk Gaussians** without any human intervention or 2D masking noise.
