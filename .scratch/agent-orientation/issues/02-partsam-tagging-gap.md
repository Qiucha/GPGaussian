# 02 - PartSAM as a Material Tag Tensor source

Type: research
Status: resolved
Blocked by: none

## Question

What does **PartSAM** (arXiv 2509.21965, https://arxiv.org/abs/2509.21965) actually take and emit, and how does that sit against this repo's tagging path?

Cover, from primary sources (the paper, any released code/docs, and this repo's segmentation/solver code):

1. PartSAM inputs (representation, prompts, color/normals) and outputs (masks, part sets, "Segment-Every-Part").
2. This repo's current producers of a Material Tag Tensor: Heuristic Primitives, Segmenter Agent, LangSAM, FlashSplat — what each does, what failed (thin structure, Grounded SAM 2), file paths.
3. The **gap** PartSAM would fill vs what it would not (it does not run MPM; it does not replace the PhysGaussian MPM Solver).
4. Confusions to forbid in the orientation pack: LangSAM, SAM2 2D lift, FlashSplat, PartField.
5. Practical constraints later agents will hit (code release status, point-cloud vs Gaussian means, scale, licensing) — only if stated by the paper/repo, not guessed.

Write findings to `.scratch/agent-orientation/research/02-partsam-tagging-gap.md`. Every claim needs a source. Then resolve this ticket with a short gist and a pointer at that file. Do not design the integration.

## Answer

PartSAM (arXiv 2509.21965; https://github.com/czvvd/PartSAM) takes mesh-sampled 100k-point clouds with normals/color and 3D clicks; it emits class-agnostic part masks, not a Material Tag Tensor. This repo’s working tag path is Heuristic Primitives via the Segmenter Agent; LangSAM is 2D text-SAM; FlashSplat lifts 2D masks onto Gaussians; Grounded SAM 2 was abandoned. PartSAM would fill native-3D part decomposition; it does not run or replace the PhysGaussian MPM Solver.

Findings: [02-partsam-tagging-gap.md](../research/02-partsam-tagging-gap.md).
