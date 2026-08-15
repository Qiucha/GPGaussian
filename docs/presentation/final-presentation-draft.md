# Phys4DGS — Final Presentation Slide Draft

Draft slide contents for a final project talk. Each section is one slide (or a short cluster). Speaker cues are in *italics*. Swap in live demo frames / Digest screenshots where noted.

**Suggested length:** ~12–15 minutes talk + demo + Q&A (~18–22 slides).

**Suggested visual assets:** Digest Dashboard WebGL view; PartSAM tag preview (pot / trunk / leaves); ficus wind frames; architecture diagram (pipeline below).

---

## Slide 1 — Title

**Phys4DGS**  
Heterogeneous MPM on Trained 3D Gaussian Splatting Scenes

- Subtitle: *From material tags to physics-driven 4D motion*
- Project / course line: BlendED · NVIDIA · 2026  
- Repo: [Qiucha/GPGaussian](https://github.com/Qiucha/GPGaussian)  
- Cite upstream: PhysGaussian (Xie et al., arXiv:2311.12198)

*Speaker: One sentence — we animate existing 3DGS scenes with multi-material continuum physics, not by training a 4D Gaussian model.*

---

## Slide 2 — Agenda

1. Problem & motivation  
2. What “4D” means here  
3. End-to-end pipeline  
4. Material Tag Tensor (PartSAM)  
5. Physics: Lamé → PhysGaussian MPM  
6. LLM-assisted config & critique  
7. Digest Dashboard  
8. Results, status, next steps  
9. Demo & takeaways  

---

## Slide 3 — The Problem

**Configuring PhysGaussian by hand does not scale.**

- Trained 3DGS scenes are static — beautiful geometry, no dynamics  
- PhysGaussian adds MPM, but setup is still manual:
  - Continuum params: \(E\), \(\nu\), \(\rho\), timesteps, forces  
  - Multi-material tagging of ~10⁵–10⁶ Gaussians (pot vs trunk vs leaves)  
- Pain points from this project’s design brief:
  - Slow (>25 min / scene of hand tuning is common)  
  - Error-prone → CFL explosions, bad Poisson ratios  
  - Thin structures (ficus trunk) defeat naive 2D masks  

*Speaker: The bottleneck is not the renderer — it is material assignment + stable physics config.*

---

## Slide 4 — Goal

**Reduce human setup effort while enabling heterogeneous physical animation of real 3DGS assets.**

User intent (natural language or curated config) → validated simulation:

> “Blow a gust of wind so the leaves sway, the trunk flexes, and the pot stays anchored.”

Deliverables of this **delta** repo (not a full PhysGaussian reimplementation):

| Delta piece | Role |
| --- | --- |
| Material Tag Tensor producer | PartSAM (intended) |
| Per-particle Lamé overlay | Tags → \(\mu, \lambda, \rho\) |
| Runner + configs | Warp MPM on checkpoint |
| Segmenter Agent / heuristics | Offline digest & tests |
| Digest Dashboard | Inspect tags, params, frames |
| Motion Critique Loop | Post-run config retune (spec + mock) |

---

## Slide 5 — What “4D” Means (and Does Not)

**4D here = time-varying 3DGS particles under physics.**

```
Static 3DGS PLY  →  tags  →  MPM steps  →  re-rasterize frames
```

- **Is:** PhysGaussian-style particle motion + Gaussian rasterization over time  
- **Is not:** Yang-style 4D Gaussian training (no HexPlane / deformation-field optimizer in `src/`)  

*Speaker: Packaging text says “physics-based 4D Gaussian Splatting”; the code is a physics delta on frozen splats.*

---

## Slide 6 — Related Building Blocks

| Component | What we use |
| --- | --- |
| **3D Gaussian Splatting** | Trained scene checkpoint (`point_cloud/`) |
| **PhysGaussian** | Warp MPM solver + rasterize loop |
| **PartSAM** | Part masks → Material Tag Tensor |
| **This repo** | Tagging seam, Lamé map, LLM/schema, Digest, runners |

Upstream clones stay gitignored (`third_party/`); we do not vendor PhysGaussian / PartSAM / 3DGS.

---

## Slide 7 — Pipeline Overview (Architecture)

**Five stages, one closed loop for inspection.**

```text
┌─────────────────┐
│ 1. Load 3DGS    │  PLY / GaussianModel
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Material Tag │  PartSAM → material_tags.pt  (N,)
│    Tensor       │  [heuristics / Segmenter Agent: digest/tests]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Lamé map     │  tag → E, ν, density → μ, λ
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. MPM solve    │  PhysGaussian Warp (p2g2p)
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. Rasterize    │  Moved Gaussians → frames / video
└────────┬────────┘
         ▼
┌─────────────────┐
│ Digest Dashboard│  Tags · materials · Dual-Mode Frame Player
└─────────────────┘
```

Optional side loop: **Motion Critique** retunes JSON config (not membership of tags).

---

## Slide 8 — Domain Vocabulary (Keep Consistent)

| Term | Meaning |
| --- | --- |
| **Material Tag Tensor** | `(N,)` int labels on every Gaussian |
| **Heuristic Primitive** | Deterministic geometric/color rule (SH, AABB, DBSCAN, …) |
| **Segmenter Agent** | LLM (or mock) that chains primitives from scene metadata |
| **PhysGaussian MPM Solver** | Continuum particle engine (Warp) |
| **Digest Dashboard** | Browser inspector for the pipeline |
| **Dual-Mode Frame Player** | Frame scrubbing (+ intended HTML5 video) |

*Speaker: Use these names in the talk — they match CONTEXT.md and the code.*

---

## Slide 9 — Material Tag Tensor

**The central seam between perception and physics.**

- Shape: `(N,)` with \(N\) = Gaussian count (pre–opacity filter)  
- Ficus vocabulary (PartSAM path): **1 = pot**, **2 = trunk**, **3 = leaves**  
- Consumed by the runner via `--tags_path material_tags.pt`  
- Each ID maps to continuum properties in config `materials`

Example (ficus wind config sketch):

| Tag | Role | Typical \(E\) order |
| --- | --- | --- |
| 1 | Anchor / pot | ~10⁷ (stiff) |
| 2 | Trunk | ~10⁷ (structural) |
| 3 | Leaves | ~10¹–10² (compliant) |

*Visual: colored point cloud — pot / trunk / leaves.*

---

## Slide 10 — PartSAM as Intended Tagger

**Three-stage recipe (wired under `src/segmentation/partsam`).**

1. **Surface sample** — Screened Poisson from Gaussian means → 100k points + normals + baked SH RGB  
2. **Clicks** — Geometry proposes candidates; MLLM/human accept · swap · resample → `clicks.json` (pot / trunk / leaves)  
3. **Masks → merge → lift** — PartSAM `predict_masks`; highest IoU wins overlaps; nearest labeled sample → every Gaussian; **survival** so prompted IDs stay non-empty after lift  

Trial evidence (ficus): ingestible tags + short 5-frame MPM run without explosion  
*(caveat: trunk mask can be oversized vs a thin stem — merge/survival policy is the fix path, not a one-off retune).*

---

## Slide 11 — Heuristics & Segmenter Agent (Supporting Path)

**Still in the tree for digest, tests, and offline CPU demos — not the lasting production tagger.**

Heuristic Primitives (examples):

- Chromatic / SH DC → RGB dominance (wood vs foliage)  
- Spatial AABB cutoff  
- PCA / anisotropy  
- DBSCAN noise purge  

**Segmenter Agent:**

- Reads scene metadata (bbox, density, SH histograms)  
- Emits a structured JSON plan of primitives  
- `mock_llm=True` path is fully offline / unit-tested  

*Speaker: Early work proved thin trunks need 3D SH cues; PartSAM later became the intended producer.*

---

## Slide 12 — From Tags to Continuum Parameters

**Per-particle Lamé from discrete labels.**

\[
\mu = \frac{E}{2(1+\nu)}, \qquad
\lambda = \frac{E\nu}{(1+\nu)(1-2\nu)}
\]

- Implemented in `src/simulation/lame_params.py`  
- Solver also needs density, grid resolution, substep \(\Delta t\), BCs  
- **CFL guardrail** rejects unsafe configs before Warp:

\[
c_p = \sqrt{\frac{E(1-\nu)}{\rho(1+\nu)(1-2\nu)}}, \quad
\Delta t_{\mathrm{sub}} \le 0.5\,\frac{\Delta x}{c_p}, \quad \nu \le 0.49
\]

*Speaker: Automation without CFL checks just fails faster.*

---

## Slide 13 — PhysGaussian MPM Solver

**Heterogeneous particles, one Warp simulation.**

- Input: Gaussian xyz (+ velocities), per-particle \(\mu,\lambda,\rho\)  
- Engine: PhysGaussian `MPM_Simulator_WARP` / p2g2p  
- Boundary conditions (config-driven): cuboid anchors, particle impulses (wind), rotations, colliders, …  
- Output: updated particle positions → 3DGS rasterization → frame sequence  

Runner entry:

```bash
./scripts/run_pipeline.sh
# or
python -m src.simulation.runner \
  --model_path data/models/ficus_whitebg \
  --tags_path data/outputs/tags/material_tags.pt \
  --config configs/ficus.json
```

---

## Slide 14 — LLM Motion Library & Translator

**Natural language → validated PhysGaussian JSON.**

- **Motion Library:** few-shot exemplars — wind drag, impact/drop, twisting torque, elastoplastic tearing  
- Retrieval + MMR reranking → CoT prompt context  
- **MotionTranslator:** emits full config + reasoning  
- Schema extends PhysGaussian with `materials`, BCs, segmentation rules  
- Status: **mock path works & is tested**; live API still `NotImplementedError`

*User story slide alternate:* animator types intent; engineer inspects CoT; validator blocks explosions.

---

## Slide 15 — Motion Critique Loop

**After a run, retune physics — not tags — from human language.**

- Frozen Material Tag Tensor (`--tags_path` unchanged)  
- Input: previous config + required freeform text (+ optional render PNGs)  
- Output: **complete** next `--config` (materials / BCs / timesteps)  
- Modes: human-gated (default) or auto-rerun with stop conditions  
- Mock `critique` = identity (for wiring tests); live critique still stubbed  

Example critique:

> “the trunk should rebound more”

---

## Slide 16 — Digest Dashboard

**Interactive inspection of the full pipeline.**

- Static web app: `digest/` (Three.js WebGL point cloud)  
- Pipeline stage tabs: Raw 3DGS → spatial → chromatic/SH → DBSCAN → MPM tags  
- Material breakdown, physics parameter matrix (\(E,\nu,\rho,\mu,\lambda\))  
- Dual-Mode Frame Player: scrub simulation frames  
- Multi-scene selector via `manifest.json`  

*Demo cue: open Digest; toggle stages; scrub frames.*

---

## Slide 17 — Evaluation Protocol

**Realism + effort (designed; partially implemented).**

| Axis | Metrics | Status in repo |
| --- | --- | --- |
| Trajectory | SVD–Kabsch MSE | Implemented |
| Perception | 2AFC binomial | Implemented |
| Video / image quality | FVD, KVD, PSNR, SSIM, LPIPS | Named; not fully implemented |
| Setup effort | \(T_{\mathrm{setup}}\), LOC, \(N_{\mathrm{iter}}\) | Timer path; NASA-TLX subscales pending |

*Speaker: Be honest — gold-standard video metrics are specified; Kabsch/2AFC/effort scaffolding is what ships today.*

---

## Slide 18 — Results & Scenes

**Primary narrative scene: ficus (wind / sway).**

- Multi-material tags: pot · trunk · leaves  
- Configs: `configs/ficus.json` (impulses + gravity + pot cuboid anchor)  
- Experiment notes: stiffening trunk / finer \(\Delta t\) improves behavior; full rebound still hard  
- PartSAM trial: non-trivial occupancy on all three parts; short MPM run stable  

**Other configs / digest models:** vasedeck (multi-material), wolf, plane, pillow2sofa, tear_bread, …

*Visuals: before/after wind frames; tag coloring; Digest panel.*

---

## Slide 19 — What Works vs What’s Next

**Works (demonstrable)**

- Heuristic primitives + Segmenter Agent (`mock_llm`)  
- Schema / CFL validation  
- PartSAM tagging path in `src/` + `run_pipeline.sh`  
- Lamé overlay + PhysGaussian runner wiring  
- Digest Dashboard UI  
- Mock motion translate / critique driver  

**Incomplete / future**

- Live LLM `translate` / `critique`  
- Full-length high-quality wind campaign + archived demo video in-tree  
- Video quality metrics (FVD/KVD/…)  
- Digest frames always = real Warp renders  
- Broader scenes beyond ficus evidence for PartSAM  

---

## Slide 20 — Design Lessons Learned

1. **2D masks alone fail on thin structure** → 3D SH cues, then PartSAM lift  
2. **Overlap needs an explicit merge policy** (IoU / survival), not “largest mask wins”  
3. **Tags and continuum params are different seams** — critique retunes JSON, not membership  
4. **CFL validation is a product feature**, not a nice-to-have  
5. **Upstream stays upstream** — delta repo + gitignored clones keeps licenses and scope clear  

---

## Slide 21 — Live Demo Plan

| Beat | Show |
| --- | --- |
| 1 | Digest: ficus tags & stage toggles |
| 2 | Material matrix (\(E,\nu,\rho\)) |
| 3 | Frame scrub / wind motion (if assets present) |
| 4 | (Optional) short `material_tags` occupancy or runner CLI |

Fallback if GPU/checkpoints unavailable: offline Segmenter Agent mock path + Digest with exported JSON.

---

## Slide 22 — Takeaways

1. **Phys4DGS** = heterogeneous MPM on **trained** 3DGS — time from physics, not from a 4D trainer  
2. The hard problem is **Material Tag Tensor quality** + **stable multi-material config**  
3. **PartSAM → Lamé → Warp → rasterize → Digest** is the intended end-to-end story  
4. **LLM motion + critique** is the effort-reduction layer (mock today; live next)  
5. Contribution is a **practical delta** on PhysGaussian: tagging, parameters, tooling, inspection  

---

## Slide 23 — Acknowledgments & References

- PhysGaussian — Xie et al., arXiv:2311.12198  
- 3D Gaussian Splatting — Kerbl et al.  
- PartSAM / PartField (upstream; non-commercial research constraints apply)  
- BlendED / NVIDIA project context  
- Team / mentors / *(fill names)*  

**Q&A**

---

## Appendix A — One-Slide Pipeline Diagram (backup)

Use if the architecture slide feels crowded; print as a full-bleed diagram.

```text
3DGS PLY ──► PartSAM (surface → clicks → masks → lift)
                 │
                 ▼
          material_tags.pt (N,)
                 │
                 ▼
     materials{E,ν,ρ} ──► Lamé (μ,λ) ──► Warp MPM ──► Rasterize
                 ▲                                      │
                 └──── Motion Critique (optional) ◄─────┘
                                  │
                                  ▼
                           Digest Dashboard
```

---

## Appendix B — Suggested Timing

| Block | Minutes |
| --- | --- |
| Problem → goal → “what 4D means” | 2 |
| Pipeline + tags + PartSAM | 4 |
| MPM + CFL + LLM/critique | 3 |
| Digest + results + status | 3 |
| Demo | 2–3 |
| Takeaways + Q&A | remainder |

---

## Appendix C — Honest Scope Notes for Speakers

Do **not** claim:

- A trained Yang-style 4DGS model in this repo  
- Live production LLM critique without the mock flag  
- That Digest “MPM” export frames are always Warp (exporter historically used PIL placeholders)  
- Commercial redistribution of PartField weights / `partfield/`  

Do claim:

- A working delta architecture around PhysGaussian  
- Offline-tested Segmenter Agent / schema / metrics core  
- Intended PartSAM tagging seam with survival/merge policy  
- An inspectable Digest Dashboard and multi-material configs  

---

*Draft generated from repo purpose (`docs/agents/orientation.md`, `CONTEXT.md`, `README.md`) and current implementation state. Update Slide 18–19 with the latest demo assets before presenting.*
