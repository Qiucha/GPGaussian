# Heterogeneous Material Assignment — Slide Draft

Focused final-talk outline: **prior work, methodology, and results** for the heterogeneous material / Material Tag Tensor path only.  
Out of scope for this deck: Motion Critique Loop, full Digest product tour, few-shot motion library, and end-to-end “Phys4DGS product” pitch.

**Suggested length:** ~8–10 minutes (~12–14 slides) + optional tag/MPM visuals.

---

## Slide 1 — Title (narrow scope)

**Heterogeneous Material Tagging for PhysGaussian**  
Assigning per-Gaussian material labels for multi-material MPM

- Problem focus: pot / trunk / leaves (and similar multi-part assets)  
- Output: **Material Tag Tensor** `(N,)` → per-particle Lamé parameters  
- Project context: Phys4DGS delta on PhysGaussian (Xie et al.)

*Speaker: This talk is only about who gets which material — not NL motion config or the dashboard product.*

---

## Slide 2 — Why Heterogeneous Materials Matter

Homogeneous MPM treats the whole 3DGS cloud as one continuum.

| Homogeneous | Heterogeneous (this work) |
| --- | --- |
| One \(E, \nu, \rho\) for all particles | Discrete tags → different \(E, \nu, \rho\) per region |
| Leaves as stiff as the pot | Pot anchored, trunk structural, foliage compliant |
| Wind looks wrong or blows the whole object | Region-appropriate deformation |

**Central artifact:** Material Tag Tensor — integer label per Gaussian, consumed by the PhysGaussian MPM Solver.

---

## Slide 3 — Prior Work (1): PhysGaussian & 3DGS

**PhysGaussian** (Xie et al., arXiv:2311.12198)

- Treats 3D Gaussians as MPM particles  
- Steps continuum mechanics in Warp, re-rasterizes moved Gaussians  
- Configures materials largely via **scene-level / manual JSON** (not automatic part tagging)

**3D Gaussian Splatting** (Kerbl et al.)

- Provides the frozen trained scene (means, SH, scales, opacity)  
- SH DC coefficients are a free **appearance cue** for 3D color heuristics  

*Gap we target:* PhysGaussian can simulate multi-material particles, but **producing the labels** for real trained scenes is still hard.

---

## Slide 4 — Prior Work (2): 2D Foundation Models → 3D

| Approach | Idea | Limit on our scenes |
| --- | --- | --- |
| **LangSAM / open-vocab 2D SAM** | Text prompts → image masks | Thin structures (ficus trunk) often get ~10–100 Gaussians |
| **FlashSplat-style lift** | Project / fuse 2D masks onto 3D Gaussians | Overlapping masks; large foliage blobs overwrite thin wood |
| **Grounded SAM 2** (attempted) | Better tracking / detection | Env conflict: Grounding DINO CUDA vs SAM2’s PyTorch ≥ 2.3.1 — abandoned |

**Lesson from prior art + our trials:** 2D→3D alone is insufficient for fine heterogeneous parts; need **3D-native cues** and/or **part-aware 3D segmentation**.

---

## Slide 5 — Prior Work (3): Part-Aware 3D Segmentation

**PartSAM** (Czvvd/PartSAM + PartField features)

- Class-agnostic **part** masks from sparse clicks on a surface sample  
- Strong fit for “name the parts, then map parts → materials”  
- Constraint: NVIDIA-noncommercial PartField; used as **gitignored upstream**, not vendored weights in git

**Positioning vs heuristics**

- Heuristics: fast, interpretable, scene-tuned rules on SH / geometry  
- PartSAM: learned part grouping with an explicit click vocabulary (pot / trunk / leaves)

*Speaker: Our lasting intended producer is PartSAM; heuristics remain evidence of the problem and an offline/test path.*

---

## Slide 6 — Problem Statement (Materials Only)

**Given** a trained 3DGS checkpoint with \(N\) Gaussians,  
**produce** tags \(t_i \in \{1,2,3,\ldots\}\) such that:

1. Each semantic part is **non-empty** and geometrically coherent  
2. Overlaps have an **explicit merge policy** (thin structure must survive)  
3. Tags map cleanly to continuum props \(\{E,\nu,\rho\}_t\) and Lamé \((\mu,\lambda)\)  
4. A short heterogeneous MPM run **loads the tensor and remains stable**

Ficus running example: **1 = pot**, **2 = trunk**, **3 = leaves**.

---

## Slide 7 — Method Overview (Evolution)

Three generations of tagging tried in this project:

```text
Gen A  LangSAM / FlashSplat 2D masks + semantic Z-priority
          └─ failed on thin trunk (~10–100 Gaussians)

Gen B  Hybrid Heuristic Primitives (SH + spatial + DBSCAN)
          └─ recovered trunk (~36k Gaussians on ficus)
          └─ Segmenter Agent chains primitives from metadata

Gen C  PartSAM recipe (intended producer)
          surface → clicks → masks → IoU merge → NN lift → survival
          └─ ficus trial: all three parts occupied; short MPM OK
```

---

## Slide 8 — Methodology A: Hybrid Heuristic Pipeline

**Heuristic Primitives** (`src/segmentation/heuristics.py`) — deterministic rules on Gaussians:

| Family | Examples |
| --- | --- |
| Chromatic / SH | \(C_{\mathrm{RGB}} = f_{\mathrm{dc}}\cdot Y_0^0 + 0.5\); wood \(R>G \land R>B\); foliage \(G>R \land G>B\) |
| Spatial | AABB / axis percentiles / cylinder–cone |
| Structural | Anisotropy (scale ratios), local density |
| Topological | DBSCAN outlier purge; KNN tag smoothing |

**Segmenter Agent** (supporting): reads scene metadata → ordered JSON plan of primitives → Material Tag Tensor.

**FlashSplat / LangSAM base (historical):** 2D unprojection with hardcoded priority  
`stem/trunk > leaves > pot` so large leaf masks do not erase wood.

---

## Slide 9 — Methodology B: PartSAM Three-Stage Recipe

**Intended producer** (`src/segmentation/partsam`):

1. **Surface** — Screened Poisson on Gaussian means → area-sample 100k + normals; bake SH RGB from nearest mean  
2. **Clicks** — Geometry proposes candidates per bin (low-\(z\) dark → pot; mid thin → trunk; high green → leaves); MLLM/human accept·swap·resample → `clicks.json`  
3. **Masks → merge → lift**
   - `predict_masks` per group  
   - Overlap: **highest chosen IoU wins** (smaller mask on ties)  
   - NN from labeled 100k samples onto **every** Gaussian  
   - **Survival:** if a prompted ID is emptied after lift, restore that group’s raw mask and re-lift  

Output: `material_tags.pt` `(N,)` int32 with IDs **1 / 2 / 3**.

---

## Slide 10 — Methodology C: Tags → Heterogeneous Continuum

Map discrete tags to PhysGaussian materials, then per-particle Lamé:

\[
\mu = \frac{E}{2(1+\nu)}, \qquad
\lambda = \frac{E\nu}{(1+\nu)(1-2\nu)}
\]

Example ficus table (`configs/ficus.json`):

| Tag | Role | \(E\) | \(\nu\) | \(\rho\) |
| --- | --- | --- | --- | --- |
| 1 | Pot / anchor | \(10^7\) | 0.3 | 200 |
| 2 | Trunk | \(2\times10^7\) | 0.4 | 200 |
| 3 | Leaves | \(50\) | 0.45 | 5 |

Plus BCs (cuboid pot freeze, wind impulses). Opacity filter may drop particles for MPM (e.g. 203 930 → 171 553) without changing tag vocabulary.

---

## Slide 11 — Results (1): Heuristic / 2D Path Findings

Empirical findings on **ficus_whitebg** (design log + SH trunk work):

| Method | Trunk capture (approx.) | Outcome |
| --- | --- | --- |
| LangSAM 2D masks alone | ~10–100 Gaussians | Unusable for structural MPM |
| Cylinder geometry heuristic | — | Failed (branches too wide) |
| Grounded SAM 2 upgrade | — | Blocked by CUDA/PyTorch conflict |
| **3D SH RGB dominance** | **~36 058 trunk Gaussians** | Usable trunk material region without 2D noise |

Additional: semantic Z-priority (`stem > leaves > pot`) required when fusing overlapping 2D masks via FlashSplat-style lift.

*Takeaway:* Appearance-aware **3D** filtering was the first method that made heterogeneous trunk vs leaf assignment practical.

---

## Slide 12 — Results (2): PartSAM Ficus Trial

**Pass** on ingest bar (`.scratch/partsam-ficus-trial/RESULT.md`):

| Criterion | Result |
| --- | --- |
| Tag length = Gaussian count | `(203 930,)` int32 |
| Occupancy | pot **30 339** · trunk **79 053** · leaves **94 538** |
| Runner ingest | Loaded via `--tags_path`; per-tag counts logged |
| Short MPM | `frame_num=5`, exit 0; positions finite; coherent ficus frames |

**Caveat (not a fail):** trunk∩leaves overlap on the 100k sample was large (~23 038); priority/IoU merge favored trunk → trunk tag **larger than a thin stem**. Motivated later **IoU + survival** policy in the production seam (not a one-off threshold hack).

---

## Slide 13 — Results (3): Offline / Synthetic Checks

Supporting evidence (unit / mock path — not claimed as real-scene SOTA):

- **Multi-model synthetic benchmark:** Segmenter Agent (`mock_llm`) correctly tags constructed plant / chair / anisotropic-toy clouds with expected pot–stem–foliage (or analogue) partitions  
- **Segmentation quality metrics:** silhouette, per-tag spatial/color std, connected components, **speckle %** — used to score and refine heuristic plans  
- **Always-on PartSAM seam tests:** merge / IoU / lift / FPS / clicks / surface contracts without publishing weights  

*Speaker: Distinguish live ficus PartSAM numbers (Slide 12) from synthetic heuristic tests.*

---

## Slide 14 — Results Summary Table

| Question | Answer from this work |
| --- | --- |
| Can 2D foundation masks alone tag a thin trunk? | **No** (~10² Gaussians) |
| Can 3D SH heuristics recover trunk mass? | **Yes** (~3.6×10⁴ on ficus) |
| Can PartSAM produce a full `(N,)` multi-part tensor? | **Yes** (all three parts >1 000) |
| Does that tensor drive stable short heterogeneous MPM? | **Yes** (5-frame Warp check) |
| Is trunk geometry “thin” after PartSAM merge? | **Not yet** — overlap bias; survival/IoU is the control knob |
| Intended lasting producer? | **PartSAM recipe in `src/`**; heuristics for digest/tests |

---

## Slide 15 — Limitations (Materials Scope)

- Evidence concentrated on **ficus**; other scenes mainly configs / heuristic digest exports  
- PartSAM trunk can be **over-thick** vs anatomic stem  
- Inference uses in-repo **FPS stand-in** (not claiming official PartSAM compile stack)  
- Heuristic path is **scene-sensitive** (color thresholds, bins)  
- Full-length wind fidelity and perceptual video metrics are **outside this materials deck**

---

## Slide 16 — Takeaways (Materials Only)

1. Heterogeneous MPM needs a **Material Tag Tensor**, not one global \((E,\nu,\rho)\).  
2. **Prior 2D→3D lifts** struggle on thin structure; **3D SH heuristics** were the first practical fix.  
3. **PartSAM** is the lasting methodology: surface sample → clicks → part masks → IoU merge → NN lift → survival.  
4. Results: non-trivial pot/trunk/leaves occupancy on ficus + short stable multi-material MPM ingest.  
5. Remaining materials research: thinner trunk occupancy, more scenes, less click/MLLM friction.

---

## Appendix — Visual Checklist

| Slide | Suggested figure |
| --- | --- |
| 2 | Homogeneous vs multi-color tagged cloud |
| 7 | Gen A → B → C timeline |
| 8 | SH RGB trunk vs leaf filter diagram |
| 9 | Three-stage PartSAM flowchart |
| 11 | Side-by-side: 2D trunk failure vs 36k SH trunk |
| 12 | `ficus_gaussians_tags.png` + 5 MPM frames |
| 10 | Material table overlaid on tagged cloud |

---

## Appendix — Explicitly Excluded from This Deck

Do not expand these here (other talks / slides):

- Few-shot Motion Translator / motion library  
- Motion Critique Loop  
- Digest Dashboard UI features (except as a tag viewer if needed)  
- CFL/LLM config synthesis beyond the materials table  
- Yang-style 4DGS training  

---

*Draft scoped to heterogeneous material tagging from `CONTEXT.md`, design decisions, PartSAM trial RESULT, and `src/segmentation/` methodology.*
