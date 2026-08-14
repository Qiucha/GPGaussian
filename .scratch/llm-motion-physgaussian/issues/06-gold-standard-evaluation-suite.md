# 06 — Gold-Standard Realism & User Effort Evaluation Suite

**What to build:**
Benchmark evaluation scripts (`src/eval/evaluate_realism.py` and `src/eval/evaluate_effort.py`) computing FVD, KVD, SVD-Kabsch Trajectory MSE, PSNR, SSIM, LPIPS, setup duration T_setup, LOC automation, and NASA-TLX workload stats.

**Blocked by:** 03 — Heterogeneous Warp MPM Parameter Array Constructor, 05 — LLM Few-Shot Motion Translation Engine

**Status:** resolved

- [x] Implement `src/eval/evaluate_realism.py` computing I3D FVD/KVD, SVD-Kabsch aligned particle trajectory MSE, multi-view PSNR, SSIM, and AlexNet LPIPS.
- [x] Implement `src/eval/evaluate_effort.py` logging wall-clock task setup duration T_setup, manual lines of code LOC_manual, simulation iteration count N_iter, and NASA-TLX survey responses.
- [x] Add 2AFC web study data exporter generating Bradley-Terry preference models and Binomial statistical significance tests.
- [x] Add integration tests verifying metric computation pipelines against reference dummy simulation outputs.
