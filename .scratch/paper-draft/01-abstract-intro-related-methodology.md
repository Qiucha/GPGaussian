# Phys4DGS: Part-Aware Heterogeneous MPM on Trained 3D Gaussian Splatting Scenes

**Draft status.** Front-matter sections only (Abstract, Introduction, Related Work, Methodology). Grounded in the Phys4DGS codebase (`src/`, `configs/`, live specs under `.scratch/*/spec.md`) and primary sources catalogued in [`.scratch/gs-physics-segmentation-lit/research/01-primary-sources.md`](../gs-physics-segmentation-lit/research/01-primary-sources.md). Claims about live LLM APIs, full video metrics (FVD/KVD/PSNR/SSIM/LPIPS), and multi-scene wind campaigns are marked as **designed** where the implementation is incomplete. The name “4D” denotes time-varying Gaussians under continuum mechanics, **not** a HexPlane / deformation-field 4DGS trainer.

---

## Abstract

Photorealistic 3D assets reconstructed with 3D Gaussian Splatting (3DGS) are increasingly used as particle sets for continuum physics, yet practical multi-part dynamics still demand tedious manual tagging and fragile, near-homogeneous material setups. We present **Phys4DGS**, a pipeline that turns a *trained* static 3DGS scene into heterogeneous Material Point Method (MPM) dynamics without retraining the radiance field. Each Gaussian receives a discrete **Material Tag Tensor** entry; tags are mapped to per-particle Young’s modulus, Poisson’s ratio, and density (and thence Lamé parameters) and advanced with a PhysGaussian-compatible Warp MPM solver; moved kernels are re-rasterized with the original 3DGS appearance model. For part membership we adopt a native-3D recipe based on **PartSAM**—surface resampling, click prompts, mask prediction, IoU-aware merge, and nearest-neighbor lift onto all Gaussians—replacing brittle 2D language masks and scene-specific color heuristics as the intended tagging path. In parallel, a few-shot **Motion Translator** and human-gated **Motion Critique Loop** target natural-language authoring and post-run retuning of continuum parameters and boundary conditions under CFL and schema guardrails, while freezing tag membership. We situate Phys4DGS against physics-on-GS systems (PhysGaussian, PhysDreamer, Physics3D, VR-GS, PIG, GaussianFluent), LLM/MLLM material assignment (LIVE-GS, PhysSplat/MPDP, GaussianProperty), and segmentation front-ends (Grounded SAM / LangSAM, PartSAM, FlashSplat, Gaussian Grouping). The expected outcome is multi-material motion—e.g., a rigid pot, stiff trunk, and compliant foliage under wind—produced with less hand-edited JSON and with part-level constitutive contrast that homogeneous PhysGaussian configs cannot express.

---

## 1. Introduction

### 1.1 Motivation

3D Gaussian Splatting [Kerbl et al., 2023] made high-quality novel-view synthesis practical by representing a scene as an explicit set of anisotropic Gaussians with a fast tile-based rasterizer. Once a scene is trained, those same kernels are a natural particle cloud for *forward* physical simulation: “what you see is what you simulate” [Xie et al., 2024]. PhysGaussian and follow-ups demonstrate elastic, plastic, and granular dynamics by treating Gaussians as MPM particles, evolving positions and covariances from deformation gradients, and re-rendering frames without cages or mesh proxies.

That capability exposes a bottleneck that is less about the solver and more about *authorship*. Real captured objects are multi-part: a potted plant couples a near-rigid container, a woody stem, and a light canopy; a decorated vase sits on wood while petals flutter. Homogeneous Young’s moduli or coarse spatial boxes cannot express these contrasts. Manually painting particle materials and hand-tuning JSON force fields is slow (often tens of minutes per scene in our internal protocol), error-prone under explicit MPM Courant–Friedrichs–Lewy (CFL) limits, and poorly transferable across scenes when tagging relies on brittle 2D language masks or chromatic heuristics.

### 1.2 Problem statement

We address **heterogeneous continuum simulation on frozen 3DGS assets**: given a trained checkpoint and a desired physical story (e.g., wind-driven sway with an anchored base), produce (i) a per-Gaussian discrete material membership, (ii) a validated continuum and boundary-condition configuration, (iii) stable MPM evolution, and (iv) photoreal frames of the deformed Gaussians—without optimizing a 4D deformation field and without rewriting the underlying MPM kernel.

Two coupled subproblems dominate:

1. **Part-level material membership.** Object-level open-vocabulary segmentation (as in several recent physics-on-GS systems) is insufficient when constitutive parameters must differ *inside* one object. Thin structures (trunks) are especially hard for 2D SAM-style lifts that bleed into foliage.
2. **Config authorship under numerical constraints.** Continuum parameters \(E\), \(\nu\), \(\rho\), timesteps, and impulse / collider schedules must remain CFL-stable and schema-complete; authors need a path from natural language and observed failure modes back to a revised JSON config without retagging the cloud.

### 1.3 Approach overview

Phys4DGS is deliberately a **delta** on PhysGaussian rather than a new radiance-field trainer or MPM discretization. The pipeline is:

1. Load a trained 3DGS PLY.
2. Produce a **Material Tag Tensor** \(T \in \mathbb{Z}^{N}\) (intended producer: PartSAM surface → clicks → masks → merge → lift).
3. Map tag IDs through a `materials` table to per-particle \(E,\nu,\rho\), finalize Lamé parameters in Warp, and step MPM.
4. Rasterize moved Gaussians; optionally compile video.
5. (Parallel track.) Synthesize or revise the JSON config via a motion library / translator and a post-run **Motion Critique Loop** that freezes \(T\) and retunes continuum / boundary fields under validation.

An offline **Segmenter Agent** that composes **Heuristic Primitives** (chromatic SH rules, spatial cutoffs, DBSCAN, etc.) remains available for CPU inspection and testing; it is *not* the lasting tagging policy. A **Digest Dashboard** visualizes plans, tags, and frame scrubbing for multi-scene QA.

### 1.4 Contributions

We claim the following (architecture + system contributions; empirical sections remain to be completed for a camera-ready paper):

- **Part-aware Material Tag Tensor for PhysGaussian MPM.** A discrete \((N,)\) membership seam that turns native-3D part masks into per-particle continuum parameters, enabling multi-material responses on a single trained asset.
- **Intended PartSAM tagging recipe** tailored to solver occupancy: Screened-Poisson surface sampling, geometry-proposed click groups, IoU-priority merge with survival repair so prompted parts remain non-empty after lift, and length-\(N\) tags before opacity filtering.
- **LLM-oriented config stack** with a curated motion-library few-shot interface, CFL/Poisson validators, and a human-gated critique loop that revises complete configs from freeform text (and optional rendered frames) without rewriting tags.
- **Evaluation design** pairing realism metrics (trajectory Kabsch MSE, planned FVD/KVD and image metrics, 2AFC) with setup-effort accounting, aimed at testing whether part-aware tagging and NL config reduce both visual error and authoring cost versus homogeneous baselines.

### 1.5 Expected outcome

On multi-part capture scenes (primary stress case: ficus under canopy wind), we expect: (i) pot / trunk / leaves occupancy that survives lift into the MPM particle set; (ii) qualitative contrast—anchored pot, stiffer trunk, compliant foliage—under identical boundary conditions where a single global material either moves the pot or kills leaf sway; (iii) reduced trial-and-error iterations when critique / translator paths are live, measured against hand-edited JSON. Historical tuning notes already show that coarse grids “glue” soft leaves to stiff trunks and that insufficient trunk rebound persists under some stiffer-trunk schedules—motivating both finer discretization and a post-run critique seam rather than one-shot parameter guessing.

---

## 2. Related Work

We organize prior art into four groups. The first three follow the structure suggested by our project notes; we add a fourth for **multi-material MPM on Gaussian assets**, which has become a distinct line of work since PhysGaussian’s largely homogeneous / region-boxed setups.

### 2.1 Physical simulation with Gaussian Splatting models

**3D Gaussian Splatting.** Kerbl et al. [2023] introduce anisotropic 3D Gaussians optimized from SfM initialization with interleaved densification and a real-time differentiable rasterizer. Phys4DGS consumes trained checkpoints (positions, covariances, opacities, spherical harmonics) and reuses that rasterizer after physics; it does not modify the 3DGS training objective.

**PhysGaussian.** Xie et al. [2024] establish the core principle of treating reconstructed Gaussian kernels as MPM particles under continuum mechanics, supporting multiple constitutive models in a Warp MPM solver with optional internal filling. Official configurations are typically **homogeneous or coarsely boxed**, not part-tagged. Phys4DGS reuses this solver path and adds the Material Tag Tensor → per-particle Lamé overlay as its primary physics delta.

**Learning or distilling material parameters.** PhysDreamer [Zhang et al., 2024] and Physics3D [Liu et al., 2024] infer stiffness / viscoelastic parameters by distilling dynamics priors from video generation or text-to-video SDS, still largely at object scope. Spring-Gaus [Zhong et al., 2024] identifies spring-mass parameters from multi-view elastic videos. These works automate *parameter values*; Phys4DGS instead emphasizes *part membership* plus LLM-authored configs on static captures, and does not require driving video for system identification.

**Interactive / alternative solvers.** VR-GS [Jiang et al., 2024] targets real-time XR with XPBD on tetrahedral cages rather than dense MPM. GASP [Borycki et al., 2024] couples GS to black-box engines. Gaussian Frosting [Guédon & Lepetit, 2024] edits via a mesh substrate. These are complementary editing/interaction paths; our continuum substrate remains PhysGaussian MPM.

**Contrast: deformation-field “4D” GS.** Dynamic 3D Gaussians [Luiten et al., 2024] and 4D Gaussian Splatting [Wu et al., 2024] optimize time-varying motion (e.g., HexPlane encoders) to *replay* observed dynamics. Phys4DGS’s “4D” is **forward physics** on a static reconstruction; there is no deformation-field training loop in our system.

### 2.2 Modification and editing of Gaussian Splatting models (incl. LLM/MLLM physics)

**Appearance and semantic editing.** GaussianEditor [Chen et al., 2024], Gaussian Grouping [Ye et al., 2024], LangSplat [Qin et al., 2024], Feature 3DGS [Zhou et al., 2024], FlashSplat [Shen et al., 2024], and SA3D [Cen et al., 2023] provide text-/mask-driven edit, grouping, or 2D→3D lift. They supply mechanisms to *select* Gaussians but do not define constitutive multi-material MPM schedules. Our repository historically explored FlashSplat lifting; policy now retires it as the Material Tag Tensor producer in favor of PartSAM.

**LIVE-GS.** Mao et al. [2024] use GPT-4o to predict physical parameters from static Gaussian assets for interactive VR, with PBD/XPBD-style dynamics and object-aware segmentation/inpainting. LIVE-GS is the closest peer on **LLM → physics config for GS**, but differs in solver family (XPBD/PBD vs MPM), granularity (object-level parameters vs part-level tags), and interaction goal (real-time VR authoring vs offline heterogeneous capture simulation).

**PhysSplat (MLLM-P3 + MPDP).** Zhao et al. [2025] reconstruct scenes, perform **object-level** open-vocabulary 3D segmentation, predict mean properties with an MLLM, then regress geometry-conditioned property *distributions* with an MPDP network before MPM. PhysSplat is the closest peer on **MLLM priors + MPM on GS**. Phys4DGS instead commits to a **discrete Material Tag Tensor** from native-3D part segmentation and separates membership (tags) from continuum tables revised by a critique loop—trading continuous property fields for an explicit, inspectable part vocabulary (e.g., pot / trunk / leaves).

**GaussianProperty.** Xu et al. [2024] assign physical properties to Gaussians in a training-free loop (SAM views + GPT-4V reasoning + multi-view voting) and demonstrate downstream MPM. Relative to an informal characterization of “segmentation without simulation,” the paper’s core is property annotation; MPM is an application. Phys4DGS shares the SAM/LMM → properties → MPM *story* but uses native-3D PartSAM parts, discrete tags, and a dedicated post-run config critique seam.

### 2.3 Segmentation methods for material-relevant structure

**Language-grounded 2D segmentation (LangSAM / Grounded SAM).** Grounded SAM [Ren et al., 2024] and engineering wrappers such as Lang-Segment-Anything couple text detection with SAM masks. In our early experiments, prompts such as “wood” frequently bled into foliage and under-covered thin trunks after lift—motivating chromatic 3D heuristics as a temporary workaround and, later, PartSAM as the intended producer.

**PartSAM.** Zhu et al. [2026] introduce a promptable part segmentation model trained natively on large-scale 3D data (triplane encoder + SAM-style decoder). This matches our requirement for *intra-object* parts rather than whole-object masks. Phys4DGS wraps PartSAM in a three-stage recipe (surface sample, clicks, mask/merge/lift) whose output is solver-facing tag IDs, not free-form part names alone.

**GaussianProperty (segmentation lens).** As above, multi-view SAM + LMM voting yields per-Gaussian properties without training a simulator. We cite it both as an editing/property peer (§2.2) and as a segmentation-style lift baseline that remains 2D-view-centric compared with PartSAM.

**Object-centric GS segmentation.** Gaussian Grouping, FlashSplat, Feature 3DGS, and LangSplat remain important baselines when the material vocabulary is object-level; they under-serve pot-vs-trunk-vs-leaves constitutive contrast.

### 2.4 Multi-material MPM on Gaussian assets

Recent work explicitly attacks PhysGaussian’s uniform-material assumption. **PIG** [Xiao et al., 2025] pairs object-level Gaussian segmentation with MLS-MPM and unique properties per object for coupled multi-material interaction. **GaussianFluent** [Huang et al., 2026] supports mixed materials and continuum-damage fracture, assigning different parameters to parts (including heuristic/segmentation splits). Scene-level heterogeneous frameworks such as RAF [Liu et al., 2026] couple GS with meshes/fluids across solvers; “heterogeneous” there emphasizes *asset/solver* diversity more than part-level Lamé tags inside one capture.

**Positioning.** Phys4DGS sits at the intersection of PhysGaussian’s MPM-on-kernels line, PartSAM’s native-3D parts, and LIVE-GS / PhysSplat-style language model config assistance—prioritizing an explicit Material Tag Tensor seam and human-gated critique rather than continuous MPDP fields or XPBD VR loops.

---

## 3. Methodology

### 3.1 Overview

Let \(\mathcal{G} = \{g_i\}_{i=1}^{N}\) be the Gaussians of a trained checkpoint, with means \(\mathbf{x}_i \in \mathbb{R}^3\), covariances, opacities, and SH coefficients. Phys4DGS computes a Material Tag Tensor \(T \in \mathbb{Z}^{N}\), a configuration \(\mathcal{C}\) (timesteps, gravity, boundary conditions, and a materials table), and a sequence of deformed states \(\{\mathcal{G}^{(t)}\}_{t=0}^{T_f}\) by MPM, rendered to images \(I^{(t)}\).

```text
Trained 3DGS PLY
        │
        ├──────────────► PartSAM recipe ──► material_tags.pt  T ∈ ℤ^N
        │                                         │
        │    Motion library / translator          │
        │            ▼                            │
        │         Config C ──► CFL/schema validate │
        │            │                            │
        └────────────┴──────────► Warp MPM ◄──────┘
                                      │
                                      ▼
                              Rasterize frames I^(t)
                                      │
                          Motion Critique Loop (optional)
                                      │
                              revised C' (T frozen)
```

### 3.2 Material Tag Tensor

**Definition.** \(T_i\) is a discrete material class for Gaussian \(i\). For the ficus stress case the solver-facing vocabulary is \(1=\text{pot}\), \(2=\text{trunk}\), \(3=\text{leaves}\). Length \(N\) equals the checkpoint Gaussian count *before* opacity filtering so that filtering and optional particle filling remain consistent with PhysGaussian’s runner.

**Design rationale.** Discrete tags provide an inspectable seam between vision and continuum parameters: membership can be frozen while \(E,\nu,\rho\) and boundary conditions are revised. Continuous per-Gaussian property fields (e.g., MPDP) are expressive but harder to critique as “make the trunk rebound more” without an explicit part ID.

### 3.3 Intended tagging: PartSAM recipe

We treat PartSAM as the lasting producer of \(T\). The recipe has three stages.

**Stage 1 — Surface sample.** From Gaussian means, build a Screened-Poisson surface, area-sample \(P_{\mathrm{in}}\) with \(M=10^5\) points and face normals, and bake SH-DC colors via nearest-mean lookup,
\[
\mathbf{c} = \mathrm{clamp}\!\left(f_{\mathrm{dc}}\cdot 0.28209479177387814 + 0.5,\, 0,\, 1\right).
\]
The mesh is throwaway; only the 100k sample (xyz, normals, RGB, sample identity) persists.

**Stage 2 — Clicks.** Geometry proposes on-cloud candidates for named groups (for ficus: low-\(z\) dark → pot; mid-\(z\) thin stem → trunk; high-\(z\) green → leaves). An MLLM or human writes a `clicks.json` of world-space positives/negatives by accepting, swapping, or resampling labeled markers (no free-form XYZ). Clicks are valid only for the sample identity that produced them.

**Stage 3 — Masks, merge, lift.** For each named group, PartSAM `predict_masks` yields a part mask over \(P_{\mathrm{in}}\) and a chosen IoU scalar. Overlaps resolve by **highest IoU wins**, with **smaller mask** on ties. Labeled samples transfer to every Gaussian by nearest neighbor in XYZ. **Survival:** if a prompted group with a non-empty raw mask becomes empty after lift, restore that group’s full raw mask (lowest IoU first when multiple) and lift again so every prompted ID remains occupied on \(T\).

**Occupancy gate.** Before simulation, require \(|T|=N\) and nonzero counts for every Stage-2 prompted ID. A short solver smoke test (\(T_f=5\)) checks finite particle positions.

**Alternates (not lasting policy).** Heuristic Primitives (chromatic SH dominance, spatial AABB/percentile cuts, anisotropy, DBSCAN, etc.) composed by a Segmenter Agent remain for offline digest/tests. LangSAM 2D masks and FlashSplat LP lifting are retained in source history but retired as producers of \(T\).

### 3.4 Heterogeneous continuum parameters

Configuration \(\mathcal{C}\) extends PhysGaussian JSON with a materials table
\[
\texttt{materials}:\; k \mapsto \{E_k,\,\nu_k,\,\rho_k\}.
\]
For each particle with tag \(T_i=k\), the runner writes \(E_i,\nu_i,\rho_i\) (scalar defaults fill missing rows). Warp `finalize_mu_lam` converts
\[
\mu = \frac{E}{2(1+\nu)},\qquad
\lambda = \frac{E\nu}{(1+\nu)(1-2\nu)}.
\]
Optional interior particle filling copies tags from nearest surface Gaussians via a KD-tree so filled volume inherits part membership.

**Ficus exemplar (conceptual).** Pot and trunk use large \(E\) and moderate \(\rho\); leaves use very small \(E\) and low \(\rho\). Boundary conditions combine a reset cuboid on the pot with sequential `particle_impulse` packs on the canopy to produce wind then rebound. Grid resolution and `substep_dt` must be fine enough that soft and stiff particles do not share overly coarse cells (historically observed “gluing” / trunk buckling).

### 3.5 PhysGaussian MPM integration

We load `MPM_Simulator_WARP` from an upstream PhysGaussian checkout. Per frame, the runner executes \(n_{\mathrm{sub}} = \texttt{frame\_dt}/\texttt{substep\_dt}\) `p2g2p` substeps, maps particles back to world/Gaussian space, and rasterizes with `diff_gaussian_rasterization`. Phys4DGS does **not** replace the constitutive kernel; the delta is tag-conditioned parameter arrays, config overlay, tagging, and authoring loops.

### 3.6 Motion library, translation, and critique

**Motion library.** Four curated dynamics primitives—wind/fluid drag, impulse/impact, bending/twisting, elastoplastic tearing—store natural-language prompts, chain-of-thought notes, and exemplar JSON. Retrieval currently uses keyword Jaccard with MMR-style diversity (\(\alpha=0.75\)); dense embedding retrieval is specified for a fuller deployment.

**Motion Translator.** `translate(query, scene_bounds)` is designed to emit a complete config plus reasoning, then pass `validate_physgaussian_config`. The validator enforces \(\nu < 0.499\) and a CFL-style bound
\[
\frac{c_p\cdot \texttt{substep\_dt}}{\Delta x} \le 0.5,\quad
c_p=\sqrt{\frac{E(1-\nu)}{\rho(1+\nu)(1-2\nu)}},
\]
with \(\Delta x\) from the MPM grid. Live API calls are stubbed in the present codebase; a mock path returns retrieved exemplars for integration testing.

**Motion Critique Loop.** After a solver run, `critique` consumes the previous config and CoT, **required** freeform human text (e.g., “the trunk should rebound more”), and optionally paths to rendered PNGs for a visual describe channel. It returns a *complete* next config: every previous key must appear; the `materials` key set is frozen (no new tag rows); \(T\) is never rewritten. Default execution is human-gated before the next Warp run; an auto mode may repeat up to \(N\) runs with the same human text. Mock `critique` is identity under validation—sufficient to test the driver and guardrails before live models are wired.

### 3.7 Evaluation protocol (designed)

We evaluate two hypotheses:

- **H1 (Realism).** Part-aware heterogeneous materials improve dynamics vs homogeneous PhysGaussian baselines under matched boundary conditions (target reductions on video and trajectory metrics; ≥70% 2AFC preference in a planned user study).
- **H2 (Effort).** NL translation / critique reduces setup time, manual JSON edits, and iteration count vs hand tuning (internal baseline >25 minutes / scene).

**Implemented now:** SVD-Kabsch–aligned trajectory MSE; 2AFC statistical helpers; wall-clock / LOC / iteration effort logging. **Specified but not yet implemented as code:** I3D FVD/KVD, PSNR/SSIM/LPIPS, NASA-TLX subscales. Segmentation quality for the heuristic agent uses silhouette-like and speckle metrics in the Digest path.

### 3.8 Digest Dashboard

The Digest Dashboard is an inspection surface (Three.js tagged point clouds, plan JSON, metrics, image scrubbing). Exported “trajectory” previews used for UI demos may be synthetic offsets; **solver evidence** is runner `--render_img` frames / compiled video. Dual-mode HTML5 video playback is specified in the glossary and not required for the methodology claims above.

### 3.9 Experimental structure (as planned / partially executed)

| Scene / setup | Role | Status |
| --- | --- | --- |
| Ficus + canopy wind (`configs/ficus.json`) | Primary multi-material stress case (tags \(1/2/3\)) | PartSAM tagging + short MPM smoke demonstrated; full-length wind fidelity and trunk rebound still under tuning |
| Vasedeck multi-material | Transfer / generalization under colorful parts | Heuristic color tagging failed (multi-colored petals split); motivates PartSAM / non-chromatic parts |
| Synthetic CPU clouds | Segmenter Agent / metric unit tests | Runnable offline without CUDA |
| Ablations (planned) | Homogeneous soft vs stiff vs heterogeneous tags under identical BCs; with/without critique | Requires Warp GPU runs for physics; validator/critique contracts testable on CPU |

**Success criteria for a complete empirical section.** (1) Occupied PartSAM tags on ≥1 additional scene beyond ficus; (2) qualitative and Kabsch evidence that heterogeneous tags are load-bearing vs homogeneous controls; (3) live translator/critique user study for H2; (4) filled FVD/image metrics or an explicit decision to rely on trajectory + 2AFC only.

---

## 4. Closing note for coauthors (not for the paper body)

- Prefer citing **Grounded SAM** for language–SAM segmentation; “LangSAM” is the engineering wrapper name used in our code.
- Prefer **PhysSplat** short name with full title *Efficient Physics Simulation for 3D Scenes via MLLM-Guided Gaussian Splatting* (ICCV 2025, arXiv:2411.12789).
- Do **not** claim GaussianProperty “has no physics”; say property lift is training-free and MPM is downstream.
- Do **not** equate Phys4DGS with 4D-GS [Wu et al., 2024].
- Primary-source dossier: `.scratch/gs-physics-segmentation-lit/research/01-primary-sources.md`.

---

## References (seed bibliography)

1. Kerbl et al., *3D Gaussian Splatting for Real-Time Radiance Field Rendering*, SIGGRAPH 2023. arXiv:2308.04079  
2. Xie et al., *PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics*, CVPR 2024. arXiv:2311.12198  
3. Zhang et al., *PhysDreamer*, ECCV 2024. arXiv:2404.13026  
4. Liu et al., *Physics3D*, arXiv:2406.04338  
5. Jiang et al., *VR-GS*, SIGGRAPH 2024. arXiv:2401.16663  
6. Zhong et al., *Spring-Gaus*, ECCV 2024. arXiv:2403.09434  
7. Mao et al., *LIVE-GS*, arXiv:2412.09176  
8. Zhao et al., *PhysSplat / Efficient Physics Simulation…*, ICCV 2025. arXiv:2411.12789  
9. Xu et al., *GaussianProperty*, arXiv:2412.11258  
10. Ren et al., *Grounded SAM*, arXiv:2401.14159  
11. Zhu et al., *PartSAM*, ICLR 2026. arXiv:2509.21965  
12. Shen et al., *FlashSplat*, ECCV 2024. arXiv:2409.08270  
13. Ye et al., *Gaussian Grouping*, ECCV 2024. arXiv:2312.00732  
14. Xiao et al., *PIG*, ICMR 2025. arXiv:2506.07657  
15. Huang et al., *GaussianFluent*, CVPR 2026. arXiv:2601.09265  
16. Wu et al., *4D Gaussian Splatting*, CVPR 2024. arXiv:2310.08528  
17. Luiten et al., *Dynamic 3D Gaussians*, 3DV 2024. arXiv:2308.09713  
