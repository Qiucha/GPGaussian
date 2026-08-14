# 06 - Where the spec lives

Type: grilling
Status: resolved
Blocked by: 04

## Question

Does this effort **amend** [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md) (the overlap paragraph), or write a **new** [spec.md](../spec.md) here that a later implementation map reads, leaving the old spec as history?

The destination is a written spec, not `src/`. Pick one home so [Write the live tagging-fix spec](08-write-spec.md) has a path.

## Answer

Amend [PartSAM as Material Tag Tensor source](../../partsam-as-tagger/spec.md) **in place** (Stage 2 skip-if-exists bound to this 100k sample; Stage 3 IoU plus prompted-ID survival after lift; later-map success bar). Do **not** write `.scratch/partsam-live-tag-fix/spec.md`. History of the live-run change stays in this map’s tickets. [Write the live tagging-fix spec](08-write-spec.md) patches that one file.

