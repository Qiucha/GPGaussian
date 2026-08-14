## Destination

Integrate 3DGS scene reference image generation into `scripts/export_pipeline_data.py` and display rendered scene preview cards in the digest dashboard UI (`digest/index.html`, `digest/style.css`, `digest/app.js`) to provide users with direct visual comparison between the true 3DGS scene and the point-cloud material segmentation.

## Notes

- Domain: Phys4DGS Digest Dashboard & 3DGS Reference Rendering.
- Key Skills: `domain-modeling`, `codebase-design`, `web_application_development`, `tdd`.
- Standing Preferences: Clean responsive dark modern aesthetic, instant image loading, zero external library overhead.

## Decisions so far

- [Export & Display 3DGS Scene Reference Preview Images](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-014-export-and-display-3dgs-reference-images.md) — Extended `export_pipeline_data.py` to project full-density 3DGS scene splats into `reference.jpg` and added reference preview overlays/thumbnails to `digest/index.html`, `digest/style.css`, and `digest/app.js`.

## Frontier Tickets

*(All tickets resolved! Map destination reached.)*

## Not yet specified

- Multi-angle thumbnail carousel preview for multi-camera 3DGS datasets.

## Out of scope

- Heavy real-time server-side raytracing stream.
