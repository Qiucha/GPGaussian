# 06 - Overlap and merge policy without another trial

Type: grilling
Status: resolved
Blocked by: none

## Question

Can the spec state a **generic** mask-merge policy from the ficus trial alone, or is that a **NO** (policy cannot be stated without another trial)?

Trial: priority merge **trunk > leaves > pot**; trunk∩leaves = 23 038 of 100k; lifted trunk 79 053 of 203 930 Gaussians ([Place three click groups on the ficus surface](../../partsam-ficus-trial/issues/05-place-click-groups.md), [Merge masks and lift to Material Tag Tensor](../../partsam-ficus-trial/issues/06-merge-and-lift-tags.md)). Tag IDs stay **1=pot / 2=trunk / 3=leaves**. Unlabeled 100k samples did not vote; every Gaussian got the nearest labeled sample.

If a policy can be written (even if ficus trunk is oversized), write it. If merge order or overlap handling is scene-specific with no generic rule, that is a NO input to [Go/no-go: PartSAM as the lasting Material Tag Tensor source](08-go-no-go-partsam-as-tagger.md). Do not re-run PartSAM.

## Answer

A policy **can** be stated (not a standing NO). It is **not** the trial’s named order trunk > leaves > pot.

On overlap, the point goes to the mask with the **highest chosen-mask predicted IoU** (the scalar PartSAM already returns when picking among three candidates per prompt). Names are labels on masks, not the comparator. A later map must **persist those IoU scalars** (the ficus trial did not). Ties: **smaller mask wins**. Unlabeled 100k samples do not vote; every Gaussian gets the nearest labeled sample after merge. Tag IDs remain 1=pot / 2=trunk / 3=leaves on the surviving unique regions.

