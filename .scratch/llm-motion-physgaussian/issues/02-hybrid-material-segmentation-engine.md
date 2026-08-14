# 02 — Hybrid Point-Cloud Material Segmentation Engine

**What to build:**
End-to-end 3D point-cloud material tagger (`src/segmentation/`) combining 2D LangSAM unprojection (with Z-priority `stem > leaves > pot`), 3D SH RGB dominance filtering (R > G and R > B for wood, G > R and G > B for leaves), and DBSCAN noise purging to generate `material_tags.pt`.

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] Implement `ColorSHHeuristic` executing 0th-order SH DC un-normalization C_RGB = f_dc * 0.282095 + 0.5 and evaluating chromatic dominance masks.
- [x] Implement `SpatialBoundingHeuristic` executing axis percentiles, radial cylinders, and spatial box masks.
- [x] Implement `DBSCANFilterHeuristic` purging isolated outlier Gaussians and reassigning noise points to canopy/background.
- [x] Integrate 2D LangSAM unprojection with hardcoded semantic priority (`stem > leaves > pot`).
- [x] Add integration tests verifying output `material_tags.pt` shape (N,) and non-empty tag assignments on sample point clouds.
