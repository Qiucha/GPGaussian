# 08 - Write the live tagging-fix spec

Type: task
Status: resolved
Blocked by: 04, 05, 06, 07

## Question

Write the spec at the path chosen in [Where the spec lives](06-where-the-spec-lives.md): merge rule from [Which merge rule now](04-which-merge-rule-now.md), Stage 2 in or out from [Is Stage 2 in the fix](05-is-stage-2-in-the-fix.md), later-map success bar from [Later execution success bar](07-later-execution-success-bar.md).

Use `/writing-for-agents`. No `src/` edits. `CONTEXT.md` unchanged.

## Answer

Amended [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md) in place: Stage 2 skip bound to this 100k sample; Stage 3 IoU merge plus prompted-ID survival after lift (full raw-mask restore, increasing IoU); later implementation map done-when (*N*, prompted IDs non-empty on the lifted tensor, 5-frame finite solver). No `.scratch/partsam-live-tag-fix/spec.md`. `CONTEXT.md` and `src/` unchanged.

