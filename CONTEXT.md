# Phys4DGS Domain Model

Multi-material physical simulation pipeline for 3D Gaussian Splatting (3DGS) scenes driven by Material Point Method (MPM) and AI agent heuristics.

## Language

**Heuristic Primitive**:
A deterministic, single-purpose mathematical or geometric rule applied to 3D Gaussians (e.g., Chromatic ratio, AABB spatial cutoff, PCA alignment, Anisotropy ratio, DBSCAN noise filter) to assign material classification.
_Avoid_: Rule, filter, segmenter script

**Segmenter Agent**:
A lightweight LLM component that inspects 3DGS scene metadata (bounding box, point density, SH color histograms) and selects/configures a chain of heuristic primitives into a structured JSON execution plan.
_Avoid_: Heuristic picker, LLM segmenter, auto-tagger

**Material Tag Tensor**:
A 1D PyTorch tensor of shape (N,) containing discrete integer material labels (e.g., 0=Anchor/Pot, 1=Rigid Trunk, 2=Compliant Leaves) assigned to every Gaussian particle.
_Avoid_: Segmentation mask, color tag, particle class array

**PhysGaussian MPM Solver**:
The material point physics simulation engine that ingests spatial coordinates, velocities, and per-particle Lamé elastic parameters derived from the Material Tag Tensor.
_Avoid_: Warp simulator, physics engine, backend solver

**Digest Dashboard**:
The interactive browser-based web application (`digest/index.html`) providing multi-model inspection panels for heuristic choices, 3D particle segmentation tags, continuum physics properties, and frame-by-frame simulation trajectory playback.
_Avoid_: Results viewer, static report, html dump

**Dual-Mode Frame Player**:
The dashboard playback component featuring canvas-based single-frame image scrubbing controls (play/pause, step forward/backward, frame slider) alongside HTML5 video preview.
_Avoid_: Video element, frame slider
