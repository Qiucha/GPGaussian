# Primary sources: physics + editing + segmentation for 3DGS

Research note for Phys4DGS context: **heterogeneous multi-material MPM on trained 3DGS**, with **part-level material tagging** and **LLM-assisted config**. Preference: arXiv abs / project pages / official GitHub READMEs. Retrieved and cross-checked 2026-08-20.

**Phys4DGS relation key (used below):** (1) trained static 3DGS as particles; (2) part-level tags → per-particle Lamé; (3) PhysGaussian-style MPM; (4) LLM-assisted material/config; (5) not Yang-style 4D deformation-field training.

---

## Category A — Physical simulation with Gaussian Splatting

### A1. 3D Gaussian Splatting (foundational)

| Field | Value |
| --- | --- |
| **Title** | 3D Gaussian Splatting for Real-Time Radiance Field Rendering |
| **Authors** | Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis |
| **Venue / year** | SIGGRAPH / ACM TOG 2023; arXiv:2308.04079 |
| **Sources** | [arXiv](https://arxiv.org/abs/2308.04079) · [project](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) · [GitHub](https://github.com/graphdeco-inria/gaussian-splatting) |

**Summary.** Replaces volumetric NeRF ray marching with an explicit set of anisotropic 3D Gaussians optimized from SfM points, with interleaved densification/pruning and a fast tile-based differentiable rasterizer. Achieves real-time (≥30 fps) 1080p novel-view synthesis with competitive quality and training time. Defines the PLY/kernel representation all later physics and editing systems consume.

**Relation to Phys4DGS.** Supplies the trained Gaussian particle cloud (positions, covariances, opacities, SHs) that Phys4DGS loads and re-rasterizes after MPM. No physics, materials, or segmentation.

**Key claim.** “We introduce three key elements that allow us to achieve state-of-the-art visual quality while … allow[ing] high-quality real-time (≥ 30 fps) novel-view synthesis at 1080p resolution” ([arXiv abs](https://arxiv.org/abs/2308.04079)).

---

### A2. PhysGaussian

| Field | Value |
| --- | --- |
| **Title** | PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics |
| **Authors** | Tianyi Xie, Zeshun Zong, Yuxing Qiu, Xuan Li, Yutao Feng, Yin Yang, Chenfanfu Jiang |
| **Venue / year** | CVPR 2024 (Highlight); arXiv:2311.12198 |
| **Sources** | [arXiv](https://arxiv.org/abs/2311.12198) · [project](https://xpandora.github.io/PhysGaussian/) · [GitHub](https://github.com/XPandora/PhysGaussian) |

**Summary.** Treats reconstructed 3D Gaussian kernels as MPM particles under continuum mechanics (“what you see is what you simulate”), evolving positions and covariances from deformation gradients without cage/mesh embedding. Supports elastic, plastic, non-Newtonian, and granular constitutive models via a customized Warp MPM solver; optional anisotropic regularization and internal particle filling. Material parameters are set in JSON configs (typically **homogeneous / region-boxed**, not part-tagged).

**Relation to Phys4DGS.** Direct upstream solver path. Phys4DGS’s delta is heterogeneous **Material Tag Tensor → Lamé** and LLM/config critique on top of this MPM; official `decode_param` does not define a multi-material tag tensor.

**Key claim.** “Both components utilize the same 3D Gaussian kernels as their discrete representations … highlighting the principle of ‘what you see is what you simulate (WS2)’” ([project](https://xpandora.github.io/PhysGaussian/)).

---

### A3. DreamGaussian (related; generative, not physics)

| Field | Value |
| --- | --- |
| **Title** | DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation |
| **Authors** | Jiaxiang Tang, Jiawei Ren, Hang Zhou, Ziwei Liu, Gang Zeng |
| **Venue / year** | ICLR 2024 (camera-ready on arXiv); arXiv:2309.16653 |
| **Sources** | [arXiv](https://arxiv.org/abs/2309.16653) · [project](https://dreamgaussian.github.io/) |

**Summary.** SDS-driven generative 3DGS with progressive densification, then mesh extraction + UV texture refinement (~2 min from a single image). Accelerates optimization-based 3D generation vs NeRF SDS pipelines.

**Relation to Phys4DGS.** Adjacent asset-creation path only; no continuum/MPM. Useful contrast: generative GS vs physics on **trained** capture GS.

**Key claim.** “DreamGaussian produces high-quality textured meshes in just 2 minutes from a single-view image, achieving approximately 10 times acceleration compared to existing methods” ([arXiv](https://arxiv.org/abs/2309.16653)).

---

### A4. PhysDreamer

| Field | Value |
| --- | --- |
| **Title** | PhysDreamer: Physics-Based Interaction with 3D Objects via Video Generation |
| **Authors** | Tianyuan Zhang, Hong-Xing Yu, Rundi Wu, Brandon Y. Feng, Changxi Zheng, Noah Snavely, Jiajun Wu, William T. Freeman |
| **Venue / year** | ECCV 2024; arXiv:2404.13026 |
| **Sources** | [arXiv](https://arxiv.org/abs/2404.13026) · [project](https://physdreamer.github.io/) |

**Summary.** Distills object dynamics priors from video generation models into physics parameters (e.g., stiffness) so static 3D objects respond to novel forces/interactions. Uses physics-based simulation (MPM-family) guided by generative video priors rather than manual Young’s modulus alone. Evaluated with 2AFC user studies on elastic objects.

**Relation to Phys4DGS.** Closest prior on **learning / inferring** material parameters for interactive dynamics; Phys4DGS instead uses **part tags + LLM config** rather than video-distillation SDS loops. Still typically object-level, not part-level multi-material tagging.

**Key claim.** “PhysDreamer … endows static 3D objects with interactive dynamics by leveraging the object dynamics priors learned by video generation models” ([arXiv](https://arxiv.org/abs/2404.13026)).

---

### A5. Physics3D

| Field | Value |
| --- | --- |
| **Title** | Physics3D: Learning Physical Properties of 3D Gaussians via Video Diffusion |
| **Authors** | Fangfu Liu, Hanyang Wang, Shunyu Yao, Shengjun Zhang, Jie Zhou, Yueqi Duan |
| **Venue / year** | arXiv 2024; arXiv:2406.04338 |
| **Sources** | [arXiv](https://arxiv.org/abs/2406.04338) · [project](https://liuff19.github.io/Physics3D/) · [GitHub](https://github.com/THU-SI/Physics3D) |

**Summary.** Extends PhysGaussian-style MPM with a **viscoelastic** constitutive model (elasticity + viscosity) and optimizes physical parameters via Score Distillation Sampling from a text-to-video diffusion model. Aims to recover richer material behavior than a single Young’s modulus.

**Relation to Phys4DGS.** Same MPM+3DGS spine; parameter recovery is video-diffusion SDS, not LLM part tagging. Strong baseline for “auto material params” vs Phys4DGS’s tag→Lamé + critique loop.

**Key claim.** Physics3D learns “various physical properties of 3D objects” by simulating with viscoelastic MPM and distilling dynamics from video diffusion via SDS ([project](https://liuff19.github.io/Physics3D/)).

---

### A6. VR-GS

| Field | Value |
| --- | --- |
| **Title** | VR-GS: A Physical Dynamics-Aware Interactive Gaussian Splatting System in Virtual Reality |
| **Authors** | Ying Jiang, Chang Yu, Tianyi Xie, Xuan Li, Yutao Feng, Huamin Wang, Minchen Li, Henry Lau, Feng Gao, Yin Yang, Chenfanfu Jiang |
| **Venue / year** | SIGGRAPH 2024 Conference Papers; arXiv:2401.16663 |
| **Sources** | [arXiv](https://arxiv.org/abs/2401.16663) · [project](https://yingjiang96.github.io/VR-GS/) |

**Summary.** Interactive VR pipeline: GS reconstruction + object segmentation + inpainting, then **XPBD** (not MPM) on tetrahedral cages with a two-level embedding so Gaussians deform without spiky artifacts. Targets real-time interaction; compares favorably on speed vs PhysGaussian MPM for VR frame budgets.

**Relation to Phys4DGS.** Same lab lineage as PhysGaussian but chooses **XPBD + cages** for interactivity. Shows physics-aware GS editing in VR without LLM material inference (manual/segmented objects). Contrast for solver choice (MPM vs PBD).

**Key claim.** VR-GS “ensures real-time execution with highly realistic dynamic responses” via XPBD and two-level embedding ([project](https://yingjiang96.github.io/VR-GS/)).

---

### A7. Spring-Gaus

| Field | Value |
| --- | --- |
| **Title** | Reconstruction and Simulation of Elastic Objects with Spring-Mass 3D Gaussians |
| **Authors** | Licheng Zhong, Hong-Xing Yu, Jiajun Wu, Yunzhu Li |
| **Venue / year** | ECCV 2024; arXiv:2403.09434 |
| **Sources** | [arXiv](https://arxiv.org/abs/2403.09434) · [project](https://zlicheng.com/spring_gaus) |

**Summary.** Integrates a 3D spring-mass model into Gaussian kernels for **system identification** from multi-view videos of elastic objects. Learnable anchors/springs enable forward simulation under new initial conditions; sparse anchors make per-anchor heterogeneous elasticity more tractable than dense MPM particles.

**Relation to Phys4DGS.** Continuum alternative (spring-mass ID vs forward MPM). Explicitly discusses heterogeneous materials via per-anchor parameters—relevant contrast to part-tag → Lamé, but requires multi-view motion video, not static trained GS + LLM.

**Key claim.** Spring-Gaus enables “future prediction and simulation under various initial states and environmental properties” from multi-view elastic-object videos ([arXiv](https://arxiv.org/abs/2403.09434)).

---

### A8. GASP

| Field | Value |
| --- | --- |
| **Title** | GASP: Gaussian Splatting for Physic-Based Simulations |
| **Authors** | Piotr Borycki, Weronika Smolak, Joanna Waczyńska, Marcin Mazur, Sławomir Tadeja, Przemysław Spurek |
| **Venue / year** | arXiv 2024; arXiv:2409.05819 |
| **Sources** | [arXiv](https://arxiv.org/abs/2409.05819) · [project](https://waczjoan.github.io/GASP) · [GitHub](https://github.com/waczjoan/GASP) |

**Summary.** Uses flat/mesh-tied Gaussians so physics can run in a **black-box** engine (Blender, Taichi, Genesis) by manipulating 3D points/faces, then re-rendering with GS. Avoids rewriting Newtonian dynamics inside the GS renderer; supports hierarchical Gaussian grouping for efficiency.

**Relation to Phys4DGS.** Orthogonal engineering path (external physics engine vs in-kernel PhysGaussian MPM). Less relevant to part-tag Lamé inside Warp MPM.

**Key claim.** GASP “can be integrated into any physics engine that can be treated as a black box” ([arXiv](https://arxiv.org/abs/2409.05819)).

---

### A9. Gaussian Frosting

| Field | Value |
| --- | --- |
| **Title** | Gaussian Frosting: Editable Complex Radiance Fields with Real-Time Rendering |
| **Authors** | Antoine Guédon, Vincent Lepetit |
| **Venue / year** | ECCV 2024 (Oral); arXiv:2403.14554 |
| **Sources** | [arXiv](https://arxiv.org/abs/2403.14554) · [project](https://anttwo.github.io/frosting/) · [GitHub](https://github.com/Anttwo/Frosting) |

**Summary.** Hybrid mesh + adaptive-thickness Gaussian “frosting” layer for fuzzy materials; edits/animations of the base mesh drive Gaussians. Improves editability over unstructured 3DGS and volumetric quality over flattened SuGaR surfaces.

**Relation to Phys4DGS.** Mesh-edit / animation path, **not** continuum MPM. Useful contrast when discussing “editing GS” vs physics simulation.

**Key claim.** Frosting is “editable as a mesh while providing a rendering quality at least equal, sometimes superior to 3DGS” ([project](https://anttwo.github.io/frosting/)).

---

### A10. Contrast: Dynamic 3DGS / 4D-GS (deformation fields, not physics)

#### Dynamic 3D Gaussians (Luiten et al.)

| Field | Value |
| --- | --- |
| **Title** | Dynamic 3D Gaussians: Tracking by Persistent Dynamic View Synthesis |
| **Authors** | Jonathon Luiten, Georgios Kopanas, Bastian Leibe, Deva Ramanan |
| **Venue / year** | 3DV 2024; arXiv:2308.09713 |
| **Sources** | [arXiv](https://arxiv.org/abs/2308.09713) · [project](https://dynamic3dgaussians.github.io/) |

**Summary.** Allows Gaussians to move/rotate over time with persistent color/opacity/size and local-rigidity regularization, yielding dense 6-DOF tracking from multi-view video. Replays/reconstructs observed dynamics; does not introduce constitutive models or forces.

#### 4D Gaussian Splatting (Wu et al.)

| Field | Value |
| --- | --- |
| **Title** | 4D Gaussian Splatting for Real-Time Dynamic Scene Rendering |
| **Authors** | Guanjun Wu, Taoran Yi, Jiemin Fang, Lingxi Xie, Xiaopeng Zhang, Wei Wei, Wenyu Liu, Qi Tian, Xinggang Wang |
| **Venue / year** | CVPR 2024; arXiv:2310.08528 |
| **Sources** | [arXiv](https://arxiv.org/abs/2310.08528) · [project](https://guanjunwu.github.io/4dgs/) |

**Summary.** Canonical 3D Gaussians + HexPlane-inspired spatial-temporal encoder and tiny MLP deformation decoder predict per-timestamp Gaussian motion/shape for real-time dynamic novel-view synthesis.

**Relation to Phys4DGS.** Explicit **negative** definition: Phys4DGS’s “4D” is time-varying Gaussians under **MPM physics**, not a trained deformation field / HexPlane loop. Cite these when clarifying packaging name vs method.

**Key claim (4D-GS).** “Our 4D-GS method achieves real-time rendering under high resolutions, 82 FPS at an 800×800 resolution on an RTX 3090 GPU” ([arXiv](https://arxiv.org/abs/2310.08528)).

---

### A11. Name not verified: “SoftGaussian”

**Status: ambiguous / not verified as a canonical paper title.** Searches of arXiv and project pages (2026-08-20) did not surface a primary-source paper titled SoftGaussian. Nearby soft-body GS works include **VR-GS** (XPBD soft bodies), **Spring-Gaus** (spring-mass elastic), **GASP** (black-box soft-body engines), and later **SoMA** (neural soft-body manipulation on GS; arXiv:2602.02402). Do not cite “SoftGaussian” without a primary URL.

---

## Category B — Modification / edit of GS models (+ LLM physics assignment)

### B1. LIVE-GS (verified)

| Field | Value |
| --- | --- |
| **Title** | LIVE-GS: LLM Powers Interactive VR Experience with Physics-Aware Gaussian Splatting |
| **Authors** | Haotian Mao, Hangyu Zhou, Zhuoxiong Xu, Siyue Wei, Yule Quan, Yan Zhang, Zixuan Guo, Nianchen Deng, Xubo Yang |
| **Venue / year** | arXiv 2024; to appear IEEE TVCG; arXiv:2412.09176 |
| **Sources** | [arXiv](https://arxiv.org/abs/2412.09176) · IEEE TVCG DOI [10.1109/tvcg.2026.3680710](https://doi.org/10.1109/tvcg.2026.3680710) |

**Summary.** VR system that prompts **GPT-4o** to infer physical parameters from static Gaussian assets (~10 s), then drives real-time interaction. Early arXiv abstract emphasizes object-aware GS, feature-mask segmentation, GPT-assisted inpainting, and **PBD/XPBD-style** unified interpolation for rigid/soft/granular; later TVCG framing stresses authoring efficiency vs expert manual tuning. LLM replaces manual material authoring for VR interaction quality.

**Relation to Phys4DGS.** Strongest **LLM → physical config** peer. Differs in solver (XPBD/PBD vs PhysGaussian MPM), granularity (object-level params vs part-level Material Tag Tensor), and goal (interactive VR authoring vs offline heterogeneous MPM on capture scenes).

**Key claim.** “A key innovation of LIVE-GS is its ability to predict reasonable parameters in just 10 seconds from static Gaussian assets while maintaining high-quality VR interactions” ([arXiv html v2](https://arxiv.org/html/2412.09176v2)).

---

### B2. PhysSplat + MPDP (verified; arXiv title differs from short name)

| Field | Value |
| --- | --- |
| **Short name** | PhysSplat |
| **Full title (arXiv / ICCV)** | Efficient Physics Simulation for 3D Scenes via MLLM-Guided Gaussian Splatting |
| **Authors** | Haoyu Zhao, Hao Wang, Xingyue Zhao, Hao Fei, Hongqiu Wang, Chengjiang Long, Hua Zou |
| **Venue / year** | ICCV 2025; arXiv:2411.12789 |
| **Sources** | [arXiv](https://arxiv.org/abs/2411.12789) · [CVF](https://openaccess.thecvf.com/content/ICCV2025/html/Zhao_PhysSplat_Efficient_Physics_Simulation_for_3D_Scenes_via_MLLM-Guided_Gaussian_ICCV_2025_paper.html) · [GitHub](https://github.com/Maxwell-Zhao/PhysSplat) |

**Summary.** Pipeline: GS reconstruction → **object-level** open-vocabulary 3D segmentation (+ inpainting) → MLLM-P3 zero-shot mean material properties → **MPDP** network that predicts a geometry-conditioned property **distribution** (reformulating regression as distribution estimation) → Physical-Geometric Adaptive Sampling → MPM simulation. Claims full-scene simulation in ~2 minutes on one GPU; MPDP ~2% compute of Physics3D-style video optimization.

**Relation to Phys4DGS.** Closest peer on **MLLM/LLM material priors + MPM on GS**. Segmentation is **object-level** (foundation-model priors), not PartSAM-style part tags; MPDP yields continuous property fields rather than discrete material class tags. Direct comparison point for Phys4DGS’s discrete Material Tag Tensor design.

**Key claim.** “We begin with detailed scene reconstruction and object-level 3D open-vocabulary segmentation … MLLM-P3 [predicts] mean physical properties … MPDP then estimates physical property distributions” ([arXiv](https://arxiv.org/abs/2411.12789)).

---

### B3. GaussianEditor

| Field | Value |
| --- | --- |
| **Title** | GaussianEditor: Swift and Controllable 3D Editing with Gaussian Splatting |
| **Authors** | Yiwen Chen, Zilong Chen, Chi Zhang, Feng Wang, Xiaofeng Yang, Yikai Wang, Zhongang Cai, Lei Yang, Huaping Liu, Guosheng Lin |
| **Venue / year** | CVPR 2024; arXiv:2311.14521 |
| **Sources** | [arXiv](https://arxiv.org/abs/2311.14521) · [project](https://buaacyw.github.io/gaussian-editor/) |

**Summary.** Text/diffusion-guided GS editing with Gaussian semantic tracing and Hierarchical Gaussian Splatting; supports localized edits, removal, and integration faster than prior NeRF editors.

**Relation to Phys4DGS.** Appearance/geometry editing, not physics. Semantic tracing is related to “which Gaussians belong to the edit target,” analogous to tagging but not material/MPM.

**Key claim.** Gaussian semantic tracing “traces the editing target throughout the training process” for controllable GS edits ([arXiv](https://arxiv.org/abs/2311.14521)).

---

### B4. Gaussian Grouping

| Field | Value |
| --- | --- |
| **Title** | Gaussian Grouping: Segment and Edit Anything in 3D Scenes |
| **Authors** | Mingqiao Ye, Martin Danelljan, Fisher Yu, Lei Ke |
| **Venue / year** | ECCV 2024; arXiv:2312.00732 |
| **Sources** | [arXiv](https://arxiv.org/abs/2312.00732) · [GitHub](https://github.com/lkeab/gaussian-grouping) |

**Summary.** Adds Identity Encoding to each Gaussian, supervised by multi-view SAM masks + 3D consistency, enabling joint reconstruct/segment/edit (removal, inpainting, style, recomposition).

**Relation to Phys4DGS.** Object/stuff instance grouping on GS—natural precursor to material assignment, but identity IDs ≠ constitutive parameters. FlashSplat later undercuts its training cost for mask lifting.

**Key claim.** “We augment each Gaussian with a compact Identity Encoding, allowing the Gaussians to be grouped according to their object instance or stuff membership” ([arXiv](https://arxiv.org/abs/2312.00732)).

---

### B5. FlashSplat

| Field | Value |
| --- | --- |
| **Title** | FlashSplat: 2D to 3D Gaussian Splatting Segmentation Solved Optimally |
| **Authors** | Qiuhong Shen, Xingyi Yang, Xinchao Wang |
| **Venue / year** | ECCV 2024; arXiv:2409.08270 |
| **Sources** | [arXiv](https://arxiv.org/abs/2409.08270) |

**Summary.** Training-free 2D→3D mask lifting framed as a linear program over Gaussian contributions; claims globally optimal assignment orders of magnitude faster than feature-distillation methods (Gaussian Grouping, SAGA).

**Relation to Phys4DGS.** Repo historically referenced FlashSplat for mask lift; PartSAM is now the intended Material Tag Tensor source. FlashSplat remains a relevant **object-mask lift** baseline, not part-aware 3D foundation segmentation.

**Key claim.** FlashSplat “formulat[es] the mask lifting process as a one-step linear programming (LP) optimization problem” ([arXiv html](https://arxiv.org/html/2409.08270)).

---

### B6. LangSplat

| Field | Value |
| --- | --- |
| **Title** | LangSplat: 3D Language Gaussian Splatting |
| **Authors** | Minghan Qin, Wanhua Li, Jiawei Zhou, Haoqian Wang, Hanspeter Pfister |
| **Venue / year** | CVPR 2024 (Highlight); arXiv:2312.16084 |
| **Sources** | [arXiv](https://arxiv.org/abs/2312.16084) · [project](https://langsplat.github.io/) |

**Summary.** Distills CLIP language features into 3D Gaussians with a scene-wise autoencoder and SAM hierarchical semantics; enables open-vocabulary 3D queries with large speedups vs LERF.

**Relation to Phys4DGS.** Language field for querying objects/regions—orthogonal to MPM but relevant if LLM prompts need grounded 3D regions. Not material tagging.

**Key claim.** “LangSplat is extremely efficient, achieving a 199× speedup compared to LERF at … 1440×1080” ([arXiv](https://arxiv.org/abs/2312.16084)).

---

### B7. Feature 3DGS

| Field | Value |
| --- | --- |
| **Title** | Feature 3DGS: Supercharging 3D Gaussian Splatting to Enable Distilled Feature Fields |
| **Authors** | Shijie Zhou, Haoran Chang, Sicheng Jiang, Zhiwen Fan, Zehao Zhu, Dejia Xu, Pradyumna Chari, Suya You, Zhangyang Wang, Achuta Kadambi |
| **Venue / year** | CVPR 2024; arXiv:2312.03203 |
| **Sources** | [arXiv](https://arxiv.org/abs/2312.03203) |

**Summary.** Distills 2D foundation features (SAM, LSeg/CLIP) into per-Gaussian low-dim features with a convolutional upsample after splatting; enables semantic/promptable segmentation and language-guided editing faster than NeRF feature fields.

**Relation to Phys4DGS.** Feature distillation for segmentation/editing; not physics. Competing paradigm to training-free mask lift (FlashSplat) and native 3D part models (PartSAM).

**Key claim.** “We propose learning a semantic feature at each 3D Gaussian … enabling … semantic segmentation, language-guided editing, promptable/promptless instance segmentation” ([arXiv](https://arxiv.org/abs/2312.03203)).

---

### B8. SA3D

| Field | Value |
| --- | --- |
| **Title** | Segment Anything in 3D with Radiance Fields (SA3D) |
| **Authors** | Jiazhong Cen, Jiemin Fang, Zanwei Zhou, Chen Yang, Lingxi Xie, Xiaopeng Zhang, Wei Shen, Qi Tian |
| **Venue / year** | NeurIPS 2023 (+ journal extension); arXiv:2304.12308 |
| **Sources** | [arXiv](https://arxiv.org/abs/2304.12308) · [project](https://jumpat.github.io/SA3D/) |

**Summary.** Propagates a single-view SAM mask into a NeRF (later also 3DGS variants) via inverse rendering and cross-view self-prompting for interactive 3D object selection.

**Relation to Phys4DGS.** Historical mask-to-3D baseline; slower/heavier than GS grouping/FlashSplat. Object-level, not part-level materials.

**Key claim.** SA3D “propagates a single SAM mask across multiple views into a NeRF-based scene, enabling sparse-to-dense segmentation” (project/paper positioning; [arXiv](https://arxiv.org/abs/2304.12308)).

---

## Category C — Segmentation

### C1. LangSAM / Language Segment-Anything (and Grounded SAM)

**Ambiguity note.** “LangSAM” usually denotes the **engineering wrapper** [luca-medeiros/lang-segment-anything](https://github.com/luca-medeiros/lang-segment-anything) (GroundingDINO + SAM/SAM2 text→boxes→masks). The primary research assemblage is **Grounded SAM**.

| Field | Value |
| --- | --- |
| **Title** | Grounded SAM: Assembling Open-World Models for Diverse Visual Tasks |
| **Authors** | Tianhe Ren, Shilong Liu, Ailing Zeng, Jing Lin, Kunchang Li, He Cao, Jiayu Chen, Xinyu Huang, Yukang Chen, Feng Yan, Zhaoyang Zeng, Hao Zhang, Feng Li, Jie Yang, Hongyang Li, Qing Jiang, Lei Zhang |
| **Venue / year** | arXiv 2024; arXiv:2401.14159 |
| **Sources** | [arXiv](https://arxiv.org/abs/2401.14159) · [GitHub Grounded-SAM](https://github.com/IDEA-Research/Grounded-Segment-Anything) · [LangSAM wrapper](https://github.com/luca-medeiros/lang-segment-anything) |

**Summary.** Couples Grounding DINO (text-prompted detection) with SAM for open-world detect-and-segment; extended demos add generation/tagging. LangSAM packages the same pattern for pip/API use (now often SAM 2.1).

**Relation to Phys4DGS.** 2D text→mask front-end historically considered for voting onto Gaussians; orientation notes LangSAM path as stubbed/empty without `lang_sam`. Inferior to native 3D part models for Material Tag Tensor goals.

**Key claim.** Grounded SAM aims to “detect and segment anything with text inputs” by marrying Grounding DINO and SAM ([GitHub README](https://github.com/IDEA-Research/Grounded-Segment-Anything)).

---

### C2. PartSAM

| Field | Value |
| --- | --- |
| **Title** | PartSAM: A Scalable Promptable Part Segmentation Model Trained on Native 3D Data |
| **Authors** | Zhe Zhu, Le Wan, Rui Xu, Yiheng Zhang, Honghua Chen, Zhiyang Dou, Cheng Lin, Yuan Liu, Mingqiang Wei |
| **Venue / year** | ICLR 2026; arXiv:2509.21965 |
| **Sources** | [arXiv](https://arxiv.org/abs/2509.21965) · [project](https://czvvd.github.io/PartSAMPage/) · [GitHub](https://github.com/czvvd/PartSAM) |

**Summary.** First promptable part segmentation model trained **natively** on large-scale 3D (not multi-view 2D lift): dual-branch triplane encoder + SAM-style decoder; model-in-the-loop curation of >5M shape–part pairs. Supports click prompts and “Segment-Every-Part” automatic decomposition including internal structure.

**Relation to Phys4DGS.** **Intended Material Tag Tensor producer** (`src/segmentation/partsam`). Part-level labels map to heterogeneous Lamé—primary differentiator vs object-level PhysSplat/LIVE-GS segmentation.

**Key claim.** “We present PartSAM, the first promptable part segmentation model trained natively on large-scale 3D data” ([arXiv](https://arxiv.org/abs/2509.21965)).

---

### C3. GaussianProperty

| Field | Value |
| --- | --- |
| **Title** | GaussianProperty: Integrating Physical Properties to 3D Gaussians with LMMs |
| **Authors** | Xinli Xu, Wenhang Ge, Dicong Qiu, ZhiFei Chen, Dongyu Yan, Zhuoyun Liu, Haoyu Zhao, Hanfeng Zhao, Shunsi Zhang, Junwei Liang, Ying-Cong Chen |
| **Venue / year** | arXiv 2024; arXiv:2412.11258 |
| **Sources** | [arXiv](https://arxiv.org/abs/2412.11258) · [project](https://Gaussian-Property.github.io) |

**Summary.** **Training-free** assignment of physical properties to 3D Gaussians: SAM segments 2D views; GPT-4V does global–local material/property reasoning; multi-view **voting** projects properties onto Gaussians. Downstream demos include **MPM dynamic simulation** and robotic grasp-force bounds. Core contribution is property annotation, not a new solver.

**Clarification vs user list wording.** The list said “without physical simulation.” Primary sources show simulation as a **downstream application** of the annotated Gaussians, not the main trained module. Accurate phrasing: segmentation/property lift **without training a simulator**; MPM is used after labeling.

**Relation to Phys4DGS.** Closest “SAM + LMM → per-Gaussian physical properties → MPM” peer. Differs: 2D lift + voting vs PartSAM native 3D parts; continuous/property maps vs discrete tags; no LLM motion-critique loop.

**Key claim.** “We introduce GaussianProperty, a training-free framework that assigns physical properties of materials to 3D Gaussians” via SAM + GPT-4V and multi-view voting ([arXiv](https://arxiv.org/abs/2412.11258)).

---

## Added: multi-material / heterogeneous assignment for MPM on 3DGS

These were missing from the user list but are primary-source relevant.

### M1. PIG — Physically-based Multi-Material Interaction with 3D Gaussians

| Field | Value |
| --- | --- |
| **Title** | PIG: Physically-based Multi-Material Interaction with 3D Gaussians |
| **Authors** | Zeyu Xiao, Zhenyi Wu, Mingyang Sun, Qipeng Yan, Yufan Guo, Zhuoer Liang, Lihua Zhang |
| **Venue / year** | ICMR 2025; arXiv:2506.07657 |
| **Sources** | [arXiv](https://arxiv.org/abs/2506.07657) · ACM DOI [10.1145/3731715.3733414](https://doi.org/10.1145/3731715.3733414) |

**Summary.** Combines fast 2D→3D Gaussian object segmentation with **MLS-MPM**, assigning **unique physical properties per segmented object** for coupled multi-material interaction; clamps Gaussian scale/rotation via constrained deformation gradients to reduce large-deformation artifacts. Positions itself against PhysGaussian’s weak segmentation / single-material region selection.

**Relation to Phys4DGS.** Explicit **multi-material MPM + 3DGS** with object-level property assignment. Still object-level (not PartSAM parts); strong citation for heterogeneous interaction claims.

**Key claim.** “We are the first to combine 3D object-level segmentation with MLS-MPM” and assign unique properties for multi-material coupled interactions ([arXiv](https://arxiv.org/abs/2506.07657)).

---

### M2. GaussianFluent — mixed materials + CD-MPM fracture

| Field | Value |
| --- | --- |
| **Title** | GaussianFluent: Gaussian Simulation for Dynamic Scenes with Mixed Materials |
| **Authors** | Bei Huang, Yixin Chen, Ruijie Lu, Gang Zeng, Hongbin Zha, Yuru Pei, Siyuan Huang |
| **Venue / year** | CVPR 2026; arXiv:2601.09265 |
| **Sources** | [arXiv](https://arxiv.org/abs/2601.09265) · [project](https://hb-pencil-zero.github.io/GaussianFluent/) · [CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_GaussianFluent_Gaussian_Simulation_for_Dynamic_Scenes_with_Mixed_Materials_CVPR_2026_paper.pdf) |

**Summary.** Internal Gaussian filling + generative interior textures; optimized **Continuum Damage MPM (CD-MPM)** for brittle fracture; supports **mixed materials** by assigning different damage/material parameters to parts (e.g., watermelon rind/flesh/seed via segmentation or color heuristics). Explicitly contrasts PhysGaussian’s uniform-material assumption.

**Relation to Phys4DGS.** Rare primary source that documents **part-/region-heterogeneous** constitutive params on GS+MPM (including fracture). Material assignment is manual/heuristic/segmentation—not LLM critique—but validates the heterogeneous-tagging thesis.

**Key claim.** “Unlike PhysGaussian, which assumes uniform material properties, our method supports more realistic and complex simulations by assigning different [damage parameters] to various parts of an object” ([CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_GaussianFluent_Gaussian_Simulation_for_Dynamic_Scenes_with_Mixed_Materials_CVPR_2026_paper.pdf)).

---

### M3. Scene-Level Heterogeneous Physics (RAF)

| Field | Value |
| --- | --- |
| **Title** | Scene-Level Heterogeneous Physics Simulation with 3D Gaussian Splats |
| **Authors** | Xiaoyang Liu, Shangzhe Wu, Kai Han |
| **Venue / year** | CVPR 2026 workshop/findings track (CVF); arXiv:2606.21753 |
| **Sources** | [arXiv](https://arxiv.org/abs/2606.21753) · [project](https://visual-ai.github.io/raf/) |

**Summary.** Representation Abstraction Framework translates 3DGS, meshes, and fluids into a unified particle set for **multi-solver** (MPM/SPH/PBD) scene-level simulation with static collision geometry and Unreal Engine 5 rendering. Argues prior GS-physics methods are siloed/homogeneous/plane-isolated.

**Relation to Phys4DGS.** “Heterogeneous” here means **asset/solver heterogeneity** (GS↔mesh↔fluid), not primarily part-level Lamé tags inside one object. Complementary scope: Phys4DGS focuses on multi-material continuum inside trained GS; RAF focuses on coupling across asset types/engines.

**Key claim.** “For the first time, [we enable] 3DGS assets to participate in scene-level, heterogeneous, multi-solver physical simulations” ([arXiv](https://arxiv.org/abs/2606.21753)).

---

## Cross-cutting map (Phys4DGS lens)

| Need | Closest primary sources |
| --- | --- |
| Trained 3DGS representation | Kerbl et al. 3DGS |
| MPM on Gaussian kernels | PhysGaussian; Physics3D; PhysSplat; PIG; GaussianFluent; GaussianProperty (downstream) |
| LLM/MLLM material or config | LIVE-GS; PhysSplat (MPDP); GaussianProperty; (PhysDreamer/Physics3D = video priors, not LLM) |
| Part-level 3D segmentation | **PartSAM** (native 3D); Spring-Gaus/GaussianFluent (heterogeneous params via parts/heuristics) |
| Object-level GS segmentation | Gaussian Grouping; FlashSplat; Feature 3DGS; LangSplat; SA3D; PhysSplat; PIG |
| Multi-material MPM on GS | **PIG**; **GaussianFluent**; PhysSplat (per-object + spatial distributions); PhysGaussian configs are mainly homogeneous/boxed |
| Not physics “4D” | Dynamic 3DGS (Luiten); 4D-GS (Wu) |

---

## Verification caveats

1. **SoftGaussian** — not verified as a paper title (see A11).
2. **PhysSplat** short name vs arXiv/ICCV full title “Efficient Physics Simulation…” — same work (arXiv:2411.12789); GitHub uses PhysSplat.
3. **LIVE-GS** abstract text differs between arXiv v1 and TVCG/preprint v2 (PBD feature-mask story vs 10-second GPT-4o authoring study); cite version explicitly.
4. **GaussianProperty** includes MPM demos; do not claim the paper “has no physics.”
5. **LangSAM** is primarily a GitHub assembly; cite Grounded SAM (arXiv:2401.14159) as the research primary source.
6. **DreamGaussian4D** (arXiv:2312.17142) exists as generative 4D GS from video; omitted as low relevance vs physics MPM (optional follow-up).

---

## Source checklist (arXiv abs preferred)

- https://arxiv.org/abs/2308.04079 — 3DGS  
- https://arxiv.org/abs/2311.12198 — PhysGaussian  
- https://arxiv.org/abs/2309.16653 — DreamGaussian  
- https://arxiv.org/abs/2404.13026 — PhysDreamer  
- https://arxiv.org/abs/2406.04338 — Physics3D  
- https://arxiv.org/abs/2401.16663 — VR-GS  
- https://arxiv.org/abs/2403.09434 — Spring-Gaus  
- https://arxiv.org/abs/2409.05819 — GASP  
- https://arxiv.org/abs/2403.14554 — Gaussian Frosting  
- https://arxiv.org/abs/2308.09713 — Dynamic 3D Gaussians  
- https://arxiv.org/abs/2310.08528 — 4D-GS  
- https://arxiv.org/abs/2412.09176 — LIVE-GS  
- https://arxiv.org/abs/2411.12789 — PhysSplat  
- https://arxiv.org/abs/2311.14521 — GaussianEditor  
- https://arxiv.org/abs/2312.00732 — Gaussian Grouping  
- https://arxiv.org/abs/2409.08270 — FlashSplat  
- https://arxiv.org/abs/2312.16084 — LangSplat  
- https://arxiv.org/abs/2312.03203 — Feature 3DGS  
- https://arxiv.org/abs/2304.12308 — SA3D  
- https://arxiv.org/abs/2401.14159 — Grounded SAM  
- https://arxiv.org/abs/2509.21965 — PartSAM  
- https://arxiv.org/abs/2412.11258 — GaussianProperty  
- https://arxiv.org/abs/2506.07657 — PIG  
- https://arxiv.org/abs/2601.09265 — GaussianFluent  
- https://arxiv.org/abs/2606.21753 — Scene-Level Heterogeneous Physics (RAF)  
