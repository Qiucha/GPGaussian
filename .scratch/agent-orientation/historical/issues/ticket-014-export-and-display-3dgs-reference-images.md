# Ticket 014: Export & Display 3DGS Scene Reference Preview Images

**Type**: `wayfinder:task`
**Status**: Closed

## Question

How do we export high-fidelity reference render images (`reference.jpg`) for all dataset models in `scripts/export_pipeline_data.py` and display reference image preview cards in the digest dashboard UI (`digest/index.html`, `digest/style.css`, `digest/app.js`)?

## Technical Plan

1. Update `scripts/export_pipeline_data.py` to generate `reference.jpg` for each model from the full-density Gaussian point cloud (or camera view) and write `reference_image` paths into `metadata.json` and `manifest.json`.
2. Update `digest/index.html` to add a Reference Image preview card overlay/panel in Panel 1 (3D Viewport) and Panel 3 (Metadata Inspector).
3. Update `digest/style.css` with responsive image styling, glassmorphism badge, and hover zoom effects.
4. Update `digest/app.js` to update the reference image source whenever a model is selected.
5. Execute `export_pipeline_data.py` to generate `reference.jpg` across all 6 dataset models (`bread-trained`, `ficus_whitebg`, `pillow2sofa_whitebg-trained`, `plane-trained`, `vasedeck_whitebg`, `wolf_whitebg-trained`).

## Resolution

- Extended `export_model_data()` in `scripts/export_pipeline_data.py` to project full-density ($N_{\text{raw}}$) 3D Gaussian splat colors into high-resolution canonical reference images (`reference.jpg`) for all 6 models.
- Integrated 3DGS Reference Render controls and card overlays into Panel 1 (`#btn-toggle-ref`, `#reference-image-overlay`) and Panel 3 inspector thumbnail (`#panel-reference-img`) in `digest/index.html`, `digest/style.css`, and `digest/app.js`.
- Re-exported all model assets and verified clean rendering on HTTP server port 8080.
