# Visual channel’s job in the Motion Critique Loop

Type: grilling
Status: resolved
Blocked by: 02

## Question

What is the optional visual-token channel **for**?

Choose among: describe the observed motion in text for the human/LLM; propose a JSON delta (or full JSON) itself; or both, with a stated precedence short of a full merge policy (merge-when-they-disagree stays map fog).

Not in this ticket: VLM vendor, API keys, or prompt templates. Use `/grilling`.

## Answer

**Describe only.** The optional visual channel turns runner `--render_img` PNGs into a textual observation of motion. It does **not** propose JSON (full or delta). `MotionTranslator.critique` is the only JSON author.

**Lives inside `critique`.** When `frame_paths` is set, the same call consumes those paths; the description may appear in returned `reasoning`. No new payload field (no change to [Critique-entry seam on MotionTranslator](03-critique-entry-seam.md)). Absent paths, skip the channel. The human is not blocked on a caption before typing.

**Not this channel:** Digest Dashboard 30-frame PIL JPEGs; optional `output.mp4`; eval scalars.

**No JSON merge.** Human text is required intent; visual text is optional evidence in the same call. Map fog “merge policy when human text and the visual channel disagree” does not graduate — there are not two JSON proposals to merge. Vendor/API/prompts stay fog.
