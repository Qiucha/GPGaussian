# 06 - Merge masks and lift to Material Tag Tensor

Type: task
Status: resolved
Blocked by: 05

## Question

Merge the three masks with priority **trunk > leaves > pot**. Nearest-neighbor lift onto ficus Gaussian means. Write `material_tags.pt` of shape `(N,)` under `.scratch/partsam-ficus-trial/`.

Done when the file length equals the Gaussian count and pot/trunk/leaves counts are recorded (trunk count especially).

## Answer

Priority merge trunk > leaves > pot on the 100k sample, then nearest-neighbor onto Gaussian means (labeled samples only). Tag IDs match FlashSplat / `configs/ficus.json`: 1=pot, 2=trunk, 3=leaves.

[material_tags.pt](../material_tags.pt) shape `(203930,)` int32. Lifted counts: pot 30 339, **trunk 79 053**, leaves 94 538 (all Gaussians labeled). Trunk is high because the PartSAM trunk∩leaves overlap went to trunk. Script: [merge_and_lift.py](../merge_and_lift.py). Stats: [tag_lift_stats.json](../tag_lift_stats.json). Preview: [ficus_gaussians_tags.png](../ficus_gaussians_tags.png).
