# 02 - Trial click loop vs spec JSON to port

Type: research
Status: resolved
Blocked by: none

## Question

What does the ficus trial actually run for Stage 2, and what is portable into `src/` vs remaining an agent/human JSON write?

Cover, from primary sources only ([CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md), trial scripts, [clicks.template.json](../../partsam-ficus-trial/clicks.template.json), spec Stage 2):

1. Geometry proposer: inputs, bins (pot/trunk/leaves), K, persist paths.
2. Annotated preview: who draws it, throwaway vs required for MLLM.
3. Whether “MLLM” is a Python VLM client or a Cursor-agent vision loop that writes JSON.
4. JSON shape vs spec (`frame`, `source`, groups, positives/negatives).
5. Skip-if-exists: which file the trial treated as already-placed clicks.

Write findings to `.scratch/partsam-src-wiring/research/02-trial-click-loop-to-port.md`. Every claim needs a source. Then resolve this ticket with a gist + pointer. Do **not** choose `src/` filenames.

## Answer

The ficus Stage 2 loop is `propose_clicks.py` (100k npz → pot/trunk/leaves bins, K=5 centroid-KNN, persist `click_candidates.json` + annotated PNG) then a Cursor-agent vision pass that only accept/swap/resample and writes `clicks.json`; there is no Python VLM client. Spec JSON (`frame`/`source`/groups positives/negatives) matches the template; the trial file adds a non-spec `mllm` blob. Skip-if-exists is `clicks.json` (Stage 3 already consumes it; trial scripts do not implement the skip). Port geometry propose + JSON persist/consume; leave the accept/swap loop as MLLM/human JSON write. Findings: [research/02-trial-click-loop-to-port.md](../research/02-trial-click-loop-to-port.md).

## Comments
