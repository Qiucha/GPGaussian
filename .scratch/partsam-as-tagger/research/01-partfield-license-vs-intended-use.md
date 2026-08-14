# PartField NVIDIA license vs this repo’s intended distribution

Primary sources (2026-08-14): in-tree clone `.scratch/partsam-ficus-trial/vendor/PartSAM/` (https://github.com/czvvd/PartSAM); [LICENSE.md](https://github.com/czvvd/PartSAM/blob/main/LICENSE.md); [LICENSES/MIT.txt](https://github.com/czvvd/PartSAM/blob/main/LICENSES/MIT.txt); [LICENSES/NVIDIA-PartField.txt](https://github.com/czvvd/PartSAM/blob/main/LICENSES/NVIDIA-PartField.txt); owner [issue #6](https://github.com/czvvd/PartSAM/issues/6#issuecomment-5200447202); [nv-tlabs/PartField LICENSE](https://github.com/nv-tlabs/PartField/blob/main/LICENSE); `PartSAM/model/pc_sam.py`, `pc_encoder.py`, `partfield_init.py`; `configs/model/PartSAM.yaml`; `evaluation/eval_everypart.py`; Phys4DGS [README.md](../../../README.md), [.gitignore](../../../.gitignore), [GitHub-Ready map](../../github-ready-working-tree/map.md). Not legal advice. Does not decide go/no-go.

## 1. Dual license (not MIT-only)

PartSAM [LICENSE.md](https://github.com/czvvd/PartSAM/blob/main/LICENSE.md): original PartSAM code is **MIT** (`LICENSES/MIT.txt`, Copyright (c) 2026 Czvvd — use, copy, modify, **sell**). Code under `partfield/` from/adapted from [NVIDIA PartField](https://github.com/nv-tlabs/PartField), including NVIDIA-copyright files, is redistributed under the **NVIDIA License** (`LICENSES/NVIDIA-PartField.txt`). “Inclusion of this license does not imply affiliation with or endorsement by NVIDIA.” “Nothing in the PartSAM MIT License overrides the license terms of third-party components.”

Owner [czvvd on #6](https://github.com/czvvd/PartSAM/issues/6#issuecomment-5200447202): original PartSAM = MIT; `partfield/` = NVIDIA License; terms are in the repo. (The issue asked whether PVCNN files could be treated as MIT; the owner did not grant that.)

In-tree NVIDIA headers (still “express license agreement … strictly prohibited”) on `partfield/model/PVCNN/encoder_pc.py`, `dnnlib_util.py`, and `partfield/clustering.py` (the last points at `LICENSES/NVIDIA-PartField.txt`). LICENSE.md covers the **whole** `partfield/` tree, not only those three files.

NVIDIA text in-tree matches [nv-tlabs/PartField LICENSE](https://github.com/nv-tlabs/PartField/blob/main/LICENSE) (same numbered terms). Material clauses:

- **§3.3 Use:** “The Work and any derivative works thereof only may be used or intended for use non-commercially.” “Non-commercially” = “non-commercial research and educational purposes only.” NVIDIA and affiliates may use commercially.
- **§3.1 Redistribution:** allowed only (a) under this license, (b) with a complete copy of the license, (c) retaining notices.
- **§3.2:** extra terms on *your* derivatives are allowed only if they still apply §3.3.
- **§1:** “derivative works shall not include works that remain separable from, or merely link (or bind by name) to the interfaces of, the Work.”

LICENSE.md: “The current PartSAM inference pipeline imports and uses these components, so use of the complete pipeline must comply with those terms.”

Hub `Czvvd/PartSAM` has `model.safetensors` only; the model API returns **no** `cardLicense` / README. Weights are not a documented MIT escape.

## 2. `predict_masks` must import `partfield/`

Released Hydra graph (`configs/model/PartSAM.yaml`): `_target_: PartSAM.model.pc_sam.PartSAM` with `pc_encoder: PartSAM.model.pc_encoder.PFEncoderDual`. `eval_everypart.py` does `hydra.utils.instantiate(cfg.model)` then `model.predict_masks`.

`pc_sam.py` **module-level** `from partfield.model.PVCNN.encoder_pc import sample_triplane_feat`. `predict_masks` calls `self.pc_encoder(coords, color, normal)` then `sample_triplane_feat` on prompt coords.

`pc_encoder.py` imports `ResidualUNet3D`, `TriplaneTransformer`, `VanillaMLP`, `TriPlanePC2Encoder`, `sample_triplane_feat` from `partfield.model.*`. `PFEncoderDual` builds frozen `PartField` + trainable `PartFieldPath`; both construct `TriPlanePC2Encoder` from that package. `forward` runs `self.partfield(coords)` / `self.partfieldMy(...)`.

`partfield_init.py` does **not** import the `partfield` package (checkpoint key split `partfield.` / `partfieldMy.`). Encoder construction still does.

There is no released MIT-only encoder for the published checkpoint. `build.py` `build_sam()` targets a `PointCloudSAM` class that is **not** in `pc_sam.py`; it is not the Hydra inference path.

## 3. This repo’s intended distribution

[README.md](../../../README.md): public GitHub [Qiucha/GPGaussian](https://github.com/Qiucha/GPGaussian) (“BlendED NVIDIA project, 2026”); Phys4DGS is the **delta**; it does **not** vendor PhysGaussian / 3DGS / FlashSplat; nested 3DGS/FlashSplat use the Inria/MPII research / non-commercial license. [pyproject.toml](../../../pyproject.toml) has **no** `license` field; no root `LICENSE`.

[GitHub-Ready map](../../github-ready-working-tree/map.md): public clone of that remote; third-party trees as documented upstream pointers, not dumped in-tree; creating/pushing the remote is out of this destination. Not a commercial product.

That distribution already documents a **research / non-commercial** upstream (Inria) via clone, not vendor.

NVIDIA themselves publish PartField as a **public GitHub** repo under this same LICENSE — the license text does not forbid public hosting.

§3.3 matches an academic research/education project. Public visibility is not, on the text, a commercial-use trigger. Commercial *use* of `partfield/` / the complete pipeline would be outside §3.3. MIT on original PartSAM does not make the pipeline MIT-sellable.

§1 linking/separable: Phys4DGS code that only binds by name to PartSAM may not itself be a NVIDIA derivative; **running** inference still uses the Work under §3.3.

## 4. What a later implementation would ship

**Clone upstream (matches GitHub-Ready):** gitignored `third_party/PartSAM` (same as PhysGaussian/FlashSplat). Root `.gitignore` already has `vendor/` and `third_party/`; `git check-ignore` reports the trial clone `.scratch/partsam-ficus-trial/vendor/PartSAM/...` ignored by `vendor/`. Published Phys4DGS tree need not contain NVIDIA sources; cloners receive PartSAM `LICENSE.md`. README would need to name NVIDIA §3.3 the way it already names Inria.

**Vendoring `partfield/` into the published tree:** §3.1 redistribution is allowed if the NVIDIA license copy and notices travel with it; §3.3 still applies. That **conflicts** with the GitHub-Ready standing preference not to dump third-party clones. `.scratch/` is on the publish surface, but nested `vendor/` stays ignored.

No MIT-only `predict_masks` subset to vendor instead.
