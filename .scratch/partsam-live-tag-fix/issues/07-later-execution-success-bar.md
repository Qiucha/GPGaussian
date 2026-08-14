# 07 - Later execution success bar

Type: grilling
Status: resolved
Blocked by: none

## Question

What numbers does a **later** implementation map use to know it is done?

Destination already requires non-trivial **1/2/3** on the Material Tag Tensor and a **short** PhysGaussian MPM Solver run that does not explode. Pin: minimum trunk (and pot/leaves) Gaussian counts; `frame_num` (5 vs 10 vs other); whether CUDA 700 / non-finite positions is the explode test; whether 125-frame `configs/ficus.json` stays explicitly out.

Do not run the solver in this ticket.

## Answer

A later implementation map is done when all of these hold (no ficus-specific count floors):

1. `material_tags.pt` length equals checkpoint Gaussian count *N* (before opacity filter).
2. Every Stage 2 group with at least one positive click has its tag ID **non-empty on the lifted Material Tag Tensor** (count > 0). Do not score this on the merged 100k cloud.
3. PhysGaussian MPM Solver: `frame_num` **5**, exit 0, finite positions, no CUDA 700.
4. 125-frame `configs/ficus.json` stays out of that bar.

Rejected: trunk > 1 000 (scene-specific). Live failure (tag 2 = 0 after lift) fails (2) without naming a trunk.

