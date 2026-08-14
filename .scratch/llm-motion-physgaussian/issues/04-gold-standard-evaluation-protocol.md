# 04 - Gold-Standard Evaluation Protocol for Realism and Effort Reduction

Type: research
Status: resolved
Blocked by: 01, 02, 03

## Question

What gold-standard quantitative metrics (Fréchet Video Distance / FVD, 3D particle trajectory error, PSNR/SSIM/LPIPS frame diffs) and human perceptual user study protocols (2AFC pairwise preference, task configuration duration) should be specified to validate whether LLM-guided material configuration improves animation realism and reduces user setup effort?

## Answer

### Key Findings & Architectural Decision

1. **Hypotheses & Target Validation Criteria:**
   - **Hypothesis $H_1$ (Realism):** Proposed system achieves $\ge35\%$ FVD reduction, $\ge30\%$ KVD reduction, $\ge45\%$ 3D trajectory MSE reduction, and $\ge70\%$ 2AFC human preference win-rate ($p < 0.001$).
   - **Hypothesis $H_2$ (Effort Reduction):** Achieves $\ge80\%$ reduction in task setup time ($T_{\text{setup}} < 3$ min vs $>25$ min manual), $100\%$ code automation (0 manual lines written), and $\ge65\%$ reduction in trial-and-error simulation iterations ($N_{\text{iter}} \le 1.5$).

2. **Quantitative Realism Metrics Engine:**
   - **FVD / KVD:** I3D ConvNet feature distribution distance ($\text{FVD} = \|\boldsymbol{\mu}_r - \boldsymbol{\mu}_g\|_2^2 + \text{Tr}(\mathbf{\Sigma}_r + \mathbf{\Sigma}_g - 2(\mathbf{\Sigma}_r \mathbf{\Sigma}_g)^{1/2})$) over 16/32 frame clips across 8 camera views.
   - **Dense Trajectory MSE ($\text{MSE}_{\text{traj}}$):** SVD Kabsch rigid alignment at frame $t=0$, followed by tracking particle centroid displacement errors over time $t \in [1, T]$.
   - **Per-Frame Quality:** Multi-view PSNR, SSIM, and AlexNet LPIPS perceptual similarity.

3. **Perceptual 2AFC User Study & Effort Protocols:**
   - **2AFC Protocol:** Web-based forced-choice side-by-side preference test with 30 participants, Latin Square randomization, 2 attentional catch trials (static & anti-gravity controls), Binomial test, and Bradley-Terry logistic regression modeling.
   - **Configuration Effort Protocol:** Instrumentation via `src/eval/evaluate_effort.py` measuring wall-clock duration ($T_{\text{setup}}$), payload lines of code ($LOC_{\text{manual}}$), iteration count ($N_{\text{iter}}$), and NASA-TLX 6-subscale workload scores.
