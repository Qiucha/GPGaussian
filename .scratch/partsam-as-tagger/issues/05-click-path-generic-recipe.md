# 05 - Click path for the generic PartSAM recipe

Type: grilling
Status: resolved
Blocked by: 03

## Question

How does a new scene get the three named click groups (pot / trunk / leaves) in the generic recipe?

Options the trial already distinguished: geometry proposes on-cloud candidates + MLLM accept/swap ([CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md)); human JSON; Segment-Every-Part / automatic prompts.

A **human must click every scene** is a **NO** for PartSAM as lasting source (map Notes). Use [Can automatic PartSAM prompts replace per-scene clicks for material IDs](03-automatic-prompts-vs-clicks.md). Do not implement a new clicker.

## Answer

Happy path: **geometry proposes** on-cloud candidates; **MLLM only accept / swap / resample** from labeled markers (no free-form xyz); snap nearest neighbor. Human only after **two** failed annotated rounds. SEP does not name pot/trunk/leaves.

Geometry bins for this tag vocabulary are the trial’s: low-\(z\) dark = pot, mid-\(z\) thin stem = trunk, high-\(z\) green = leaves. Seam I/O is world-xyz clicks (one or more positives per group; negatives empty until mask retry). Exact filename/path is a later map. This is **not** a standing NO: a human is not the happy path.

Evidence: [CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md), [Can automatic PartSAM prompts replace per-scene clicks for material IDs](03-automatic-prompts-vs-clicks.md).

