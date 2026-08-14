# Ticket 007: Implement 5-Panel Interactive Web Digest Dashboard

**Type**: `wayfinder:task`
**Status**: Closed (Resolved)
**Blocks**: [Verify Dashboard Playback and Frame Scrubbing](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-008-verify-dashboard-cross-browser.md)

## Question

How do we design and build `digest/index.html`, `digest/app.js`, and `digest/style.css` to render an interactive 5-panel dashboard supporting model switching, 3D WebGL point cloud material tag inspection, LLM heuristic decision rationale, physical property tables, and dual-mode frame-by-frame simulation playback?

## Resolution

- Upgraded `digest/index.html`, `digest/app.js`, and `digest/style.css` with a 5-panel layout:
  1. **Dataset Model & Stage Selector Bar**: Dynamically selects between all 6 dataset models (`ficus_whitebg`, `wolf_whitebg-trained`, `bread-trained`, `pillow2sofa_whitebg-trained`, `plane-trained`, `vasedeck_whitebg`) and 5 pipeline stages (`Raw 3DGS`, `Spatial Base Cutoff`, `Chromatic/SH`, `DBSCAN Filtered`, `MPM Physics Tags`).
  2. **Panel 1: 3D Point-Cloud WebGL Viewport**: Built with Three.js featuring vertex color tag rendering, orbit controls, auto-rotate, reset view button, and dynamic material legend.
  3. **Panel 2: Dual-Mode Frame-by-Frame Simulation Player**: Displays rendered impulse deformation frames with frame slider (`0` to `29`), Play/Pause toggle, Step Backward (-1), Step Forward (+1), First/Last frame jump, and playback speed controls (`0.5x` .. `2.0x`).
  4. **Panel 3: LLM Heuristic Choice & Rationale Inspector**: Displays scene metadata (extents, percentiles, color dominance, anisotropy), selected heuristic steps (primitive type, parameters), and LLM reasoning descriptions.
  5. **Panel 4: Continuum Physics Property Table**: Displays tag IDs, Young's Modulus ($E$), Poisson's Ratio ($\nu$), Density ($\rho$), Lamé Shear Modulus ($\mu$), and Lamé Bulk Modulus ($\lambda$).
  6. **Panel 5: Material Tag Distribution Breakdown**: Animated progress bars showing particle counts and percentages per material tag.
