# 01 - NVIDIA-noncommercial partfield vs this repo's intended use

Type: research
Status: resolved
Blocked by: none

## Question

Does `partfield/`’s NVIDIA non-commercial (research/education) license block using PartSAM as the lasting Material Tag Tensor source for this repo’s intended distribution?

Cover, from primary sources only (PartSAM `LICENSE.md`, NVIDIA PartField license text in-tree and upstream, PartSAM owner comments, this repo’s GitHub-ready intent):

1. Exact license terms on `partfield/` vs MIT on PartSAM original code.
2. Whether `predict_masks` / the encoder **must** import `partfield/` (cannot be MIT-only).
3. This repo’s intended use: public GitHub academic project ([GitHub-Ready Working Tree](../../github-ready-working-tree/map.md) names https://github.com/Qiucha/GPGaussian.git); not a commercial product, but a public clone.
4. What a later implementation would ship: clone upstream vs vendoring `partfield/`.

Write findings to `.scratch/partsam-as-tagger/research/01-partfield-license-vs-intended-use.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** decide the go/no-go.

## Answer

NVIDIA §3.3 binds the full `predict_masks` path (it must import `partfield/`; not MIT-only) to non-commercial research/education; the same text allows redistribution under that license and does not forbid this repo’s public academic GitHub clone if PartSAM is consumed as gitignored upstream (like Inria 3DGS) or if any vendored `partfield/` carries the NVIDIA license. Commercial use of the pipeline would be outside the grant.

Findings: [research/01-partfield-license-vs-intended-use.md](../research/01-partfield-license-vs-intended-use.md)
