# Ticket 006: Build Multi-Model Pipeline Frame & Video Exporter

**Type**: `wayfinder:task`
**Status**: Closed (Resolved)
**Blocks**: [Implement 5-Panel Interactive Web Digest Dashboard](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-007-build-digest-dashboard-ui.md)

## Question

How can we generate and export particle tag data, segmentation stage checkpoints, frame-by-frame rendered trajectory images, and MP4 videos for all 6 models so the digest dashboard can load them dynamically?

## Resolution

- Created `scripts/export_pipeline_data.py`:
  1. Processed all 6 trained 3DGS models (`bread-trained`, `ficus_whitebg`, `pillow2sofa_whitebg-trained`, `plane-trained`, `vasedeck_whitebg`, `wolf_whitebg-trained`).
  2. Extracted `metadata.json` (spatial bounds, percentiles, color dominance, scale anisotropy).
  3. Generated `plan.json` (LLM segmenter execution steps, parameters, continuum physics properties $E, \nu, \rho$).
  4. Exported WebGL point cloud particles `particles.json` containing positions, SH colors, final material tags, and 5-stage stepper tags.
  5. Rendered 30 frame trajectory images (`frame_00.jpg` ... `frame_29.jpg`) per model depicting MPM impulse deformation.
  6. Generated central manifest index [`digest/data/manifest.json`](file:///home/q/Projects/mit/PBL/Phys4DGS/digest/data/manifest.json).
