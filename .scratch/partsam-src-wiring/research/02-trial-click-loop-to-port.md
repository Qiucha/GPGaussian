# Trial click loop vs spec JSON to port

Primary sources (2026-08-14): [CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md); [propose_clicks.py](../../partsam-ficus-trial/propose_clicks.py); [clicks.template.json](../../partsam-ficus-trial/clicks.template.json); [clicks.json](../../partsam-ficus-trial/clicks.json); [click_candidates.json](../../partsam-ficus-trial/click_candidates.json); [run_predict_clicks.py](../../partsam-ficus-trial/run_predict_clicks.py); spec [Stage 2 — clicks](../../partsam-as-tagger/spec.md). Not a `src/` filename decision.

What the ficus trial ran for Stage 2: geometry on the 100k sample proposes labeled on-cloud candidates and an annotated PNG; a Cursor-agent vision pass only **accept / swap / resample**; the agent writes world-xyz `clicks.json`. Portable into `src/`: that proposer plus persist/consume of the spec JSON, and skip-if-exists on `clicks.json`. Remaining an agent/human JSON write: the accept/swap loop (not a Python VLM client).

## 1. Geometry proposer

[CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md) §1: candidates come from `ficus_100k.npz` (`coords`, `colors` uint8). Bins in prose: **pot** = low \(z\) and low luminance; **leaves** = high \(z\) and green-dominant RGB; **trunk** = mid \(z\), small \(xy\) radius around the stem axis (median \(xy\) of mid-height points), not in pot or canopy color bins. Per group: **centroid of the bin**, then **K nearest sample points (K=5)**; primary = closest to the centroid.

[propose_clicks.py](../../partsam-ficus-trial/propose_clicks.py) is that proposer. Inputs: `ficus_100k.npz` keys `coords` (float32) and `colors` (float32 for luminance/green tests). `K = 5`. Bins as implemented:

- `z_lo, z_hi = np.percentile(zc, [12, 70])`; `lum = rgb.mean(axis=1)`; `green = (g > r+8) & (g > 90)`.
- **pot:** `zc < z_lo` and `lum < 95`.
- **leaves:** `zc > z_hi` and `green`.
- **trunk:** mid-height `p22–p55` excluding pot/leaf (fallback `p20–p60` if mid count `< 200`); stem axis = median \(xy\) of mid; `r_cut = percentile(r[mid], 18)`; `trunk_m = mid & (r < r_cut) & ~green & (lum > 70)`.

`knn_of_centroid` ranks only in-bin points (`d_out = inf` off-bin). Persist paths hardcoded: `click_candidates.json` (per group `n_bin`, `centroid`, `indices`, `points`) and `ficus_100k_click_candidates.png`. There is no skip-if-exists in this script.

[make_click_landmarks.py](../../partsam-ficus-trial/make_click_landmarks.py) is a different human-id landmark drawer (FPS on other masks, writes `click_landmarks.json` / `.png`). It does not write `clicks.json` and is not the Stage 2 loop that produced the trial clicks.

## 2. Annotated preview

[CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md) §2: draw three primaries (and optional extras) on xy / xz / yz views with labeled markers; path `ficus_100k_click_candidates.png`. The MLLM pass (§3) **sees that PNG**.

[propose_clicks.py](../../partsam-ficus-trial/propose_clicks.py) draws the PNG (matplotlib Agg): 12k random subsample of the cloud, hollow P0 + filled P1–P4 per group, annotations `P0` / `1`…`4`. It does not copy a prior preview file. The pipeline text says “world xyz in the legend”; the script’s legend is `{group} P0` / `{group} Pk` only (xyz live in `click_candidates.json`, not on the figure).

Spec Stage 2 **Throwaway:** annotated PNG previews. They are still **required input** for the MLLM accept/swap pass; throwaway means they are not the seam persist.

## 3. MLLM is a Cursor-agent vision loop, not a Python VLM client

[CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md) Roles table: “Accept / reject / sample again” = **MLLM (this Cursor agent with vision on an annotated preview)**; “Write `clicks.json`” = Agent; Human only after two failed annotated rounds. §3: vision model sees the PNG plus a one-line bbox; may only **accept** three primaries, **swap** a primary for a labeled extra in the same group, or **reject a group** and ask geometry to resample. Must not emit free-form xyz. **Out of this pipeline:** a separate hosted VLM API.

[propose_clicks.py](../../partsam-ficus-trial/propose_clicks.py) has no VLM/API import; it stops after candidates + PNG. Spec Stage 2: “MLLM or human **writes** this JSON; they are not a Python import.”

[clicks.json](../../partsam-ficus-trial/clicks.json) records the trial decision: `"mllm": { "round": 1, "decision": "accept primaries P0", "candidates": "click_candidates.json", "preview": "ficus_100k_click_candidates.png" }`.

## 4. JSON shape vs spec

Spec Stage 2 persist and [clicks.template.json](../../partsam-ficus-trial/clicks.template.json) are the same object: `frame: "world"`, `source: "100k sample before ValDataset bbox-normalize"`, `groups.{pot,trunk,leaves}.{positives,negatives}` (arrays). Spec: one or more positives per group; negatives empty until a mask retry.

Trial [clicks.json](../../partsam-ficus-trial/clicks.json) matches that contract: one positive per group, all `negatives: []`. Those positives equal `click_candidates.json` `points[0]` for each group (already on-cloud samples). Extra top-level `mllm` is **not** in the spec / template.

[CLICK_PIPELINE.md](../../partsam-ficus-trial/CLICK_PIPELINE.md) §4: accepted point → `argmin ‖p − coords‖`; write `clicks.json` with `frame: world`. Round-1 accept of P0 needed no extra snap (points were already `xyz[idx]`).

## 5. Skip-if-exists

Spec Stage 2: “Skip this stage if clicks already exist.”

No trial Python implements that check. [run_predict_clicks.py](../../partsam-ficus-trial/run_predict_clicks.py) always `json.loads` **`clicks.json`** for `groups[g].positives` (and reads `click_candidates.json` only for leftover extras on mask retry — Stage 3, not Stage 2). The file the trial treated as already-placed clicks is **`clicks.json`**.

## Portable vs remaining JSON write

| Piece | Trial fact | Into `src/` vs agent/human |
| --- | --- | --- |
| Geometry bins + K=5 centroid-KNN | `propose_clicks.py` | Portable (propose + persist candidates) |
| Annotated PNG | drawn by that script; MLLM input; spec throwaway | Portable to generate; not the persist seam |
| Accept / swap / resample | Cursor agent with vision; no VLM import | **Not** a Python VLM client — MLLM or human **writes** JSON |
| Spec JSON (`frame` / `source` / groups) | template + `clicks.json` body | Persist/consume in `src/` |
| Trial-only `mllm` blob | in `clicks.json` | Not in spec shape |
| Skip-if-exists | spec; trial has no `if exists` | Skip when **`clicks.json`** already has placed groups |

Do not port [make_click_landmarks.py](../../partsam-ficus-trial/make_click_landmarks.py) as the Stage 2 proposer.
