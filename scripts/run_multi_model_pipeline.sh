#!/usr/bin/env bash
# Thin wrapper around scripts/run_multi_model_pipeline.py for the six-scene QA pass.
# Run on a CUDA host from the repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python scripts/run_multi_model_pipeline.py "$@"
