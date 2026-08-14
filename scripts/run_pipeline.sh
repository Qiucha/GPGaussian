#!/bin/bash
set -e

# Phys4DGS Pipeline Runner
# Run from project root: ./scripts/run_pipeline.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

MODEL_PATH="$PROJECT_ROOT/data/models/ficus_whitebg"
OUTPUT_DIR="$PROJECT_ROOT/data/outputs"
CONFIG_DIR="$PROJECT_ROOT/configs"

echo "1. Running FlashSplat Segmentation (Base Tags)..."
conda run -n physgauss python -m src.segmentation.flashsplat \
    --model_path "$MODEL_PATH" \
    --masks_dir "$OUTPUT_DIR/masks" \
    --output_dir "$OUTPUT_DIR/tags" \
    --prompts "ceramic pot" "wooden branch" "thin brown plant stem" "leaves"

echo "2. Applying 3D Color Heuristic for Trunk Segmentation..."
conda run -n physgauss python -m src.segmentation.color_heuristic \
    --model_path "$MODEL_PATH" \
    --tags_path "$OUTPUT_DIR/tags/material_tags.pt" \
    --output_path "$OUTPUT_DIR/tags/material_tags_color.pt"

echo "3. Overwriting Base Tags with Color Tags..."
mv "$OUTPUT_DIR/tags/material_tags_color.pt" "$OUTPUT_DIR/tags/material_tags.pt"

echo "4. Running Physics Simulation & Rendering..."
conda run -n physgauss python -m src.simulation.runner \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_DIR/simulated_video" \
    --config "$CONFIG_DIR/ficus.json" \
    --tags_path "$OUTPUT_DIR/tags/material_tags.pt" \
    --render_img --compile_video

echo "Pipeline complete."
echo "Output video: $OUTPUT_DIR/simulated_video/output.mp4"
