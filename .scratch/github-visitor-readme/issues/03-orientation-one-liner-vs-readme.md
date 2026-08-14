# 03 - Orientation one-liner vs the new README

Type: task
Status: resolved
Blocked by: 02

## Question

After the visitor README is rewritten, does [docs/agents/orientation.md](../../../docs/agents/orientation.md) fight it (clone paths, FlashSplat required vs optional, Segmenter Agent as intended tagger, setup scripts)?

If yes: one `/writing-for-agents` pointer or correction so agents and GitHub visitors are not taught opposite install stories. If no: resolve as no pack change.

Do not restate the README. Do not add PartSAM to `CONTEXT.md`. Do not push.

## Answer

Yes: **Vendor and experiments** still taught `vendor/gaussian-splatting` as load-bearing via `src/__init__.py` and `vendor/FlashSplat` in-tree. That fights the README (`third_party/` clones, nested PhysGaussian 3DGS, FlashSplat optional / unused by `run_pipeline.sh`). Segmenter Agent-as-intended and `setup_env.sh` / `physgauss_v2` did not fight. One orientation correction: that heading is now **Upstream clones and experiments**, pointing at `src/upstream.py`; Pointers table reaches [README.md](../../../README.md) for visitor clone/install. No `CONTEXT.md` change, no push.
