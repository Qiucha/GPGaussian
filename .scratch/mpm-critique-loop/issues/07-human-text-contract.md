# Human text contract for the Motion Critique Loop

Type: grilling
Status: resolved
Blocked by: none

## Question

What must the human type on a required critique turn?

Choose among: freeform natural language only; a small set of structured intents (e.g. stiffer trunk, stronger wind) with optional freeform; or structured fields the spec names. The human has watched rasterized frames (Digest Dashboard or runner PNGs). Use `/grilling`.

## Answer

**Freeform natural language only.** No closed intent vocabulary. No named structured fields (that would be hand-editing the `--config`). Empty or whitespace-only is not a critique turn.

The auto path reuses this same string ([Auto-path stop for the Motion Critique Loop](06-auto-path-stop.md)). User interrupt is a separate control, not the word “stop” in the text.

**Watch:** the human is assumed to have watched runner `--render_img` PNGs. Digest Dashboard playback is optional and is **not** solver evidence ([Visual channel’s job in the Motion Critique Loop](05-visual-channel-job.md)).
