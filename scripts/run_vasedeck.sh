#!/bin/bash
set -e

# Vasedeck Pipeline Runner
# Run from project root: ./scripts/run_vasedeck.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

MODEL_PATH="$PROJECT_ROOT/data/models/vasedeck_whitebg/point_cloud/iteration_30000"
OUTPUT_DIR="$PROJECT_ROOT/data/outputs/vasedeck"
CONFIG_DIR="$PROJECT_ROOT/configs"

# Since the directory has point_cloud/iteration_30000/point_cloud.ply
# We need to give it the root model path that contains point_cloud
MODEL_PATH="$PROJECT_ROOT/data/models/vasedeck_whitebg"

echo "1. Generating Tags using Color and Spatial Heuristic..."
conda run -n physgauss python -m src.segmentation.vasedeck_heuristic \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_DIR/tags/material_tags.pt"

# Skip 3D color heuristic for now, we want to evaluate pure LangSAM
# If it fails, we will add a Vasedeck-specific heuristic.

echo "2. Verifying Tags Before Simulation..."
conda run -n physgauss python -m src.eval.render_tags \
    --model_path "$MODEL_PATH" \
    --tags_path "$OUTPUT_DIR/tags/material_tags.pt" \
    --output_path "$OUTPUT_DIR/tags/tags_verification.png"

echo "3. Running Physics Simulation & Rendering..."
conda run -n physgauss python -m src.simulation.runner \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_DIR/simulated_video" \
    --config "$CONFIG_DIR/vasedeck_multi_material.json" \
    --tags_path "$OUTPUT_DIR/tags/material_tags.pt" \
    --render_img --compile_video

echo "Pipeline complete."
echo "Output tags verification: $OUTPUT_DIR/tags/tags_verification.png"

