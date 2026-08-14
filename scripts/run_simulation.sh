#!/bin/bash
set -e

# Run a simulation experiment
# Usage: ./scripts/run_simulation.sh [config_name] [experiment_name]
# Example: ./scripts/run_simulation.sh ficus exp_5_higher_stiffness

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

CONFIG_NAME="${1:-ficus}"
EXP_NAME="${2:-unnamed_experiment}"

MODEL_PATH="$PROJECT_ROOT/data/models/ficus_whitebg"
TAGS_PATH="$PROJECT_ROOT/data/outputs/tags/material_tags.pt"
CONFIG_PATH="$PROJECT_ROOT/configs/${CONFIG_NAME}.json"
OUTPUT_PATH="$PROJECT_ROOT/data/outputs/simulated_video"

echo "=== Running Simulation ==="
echo "Config: $CONFIG_PATH"
echo "Model:  $MODEL_PATH"
echo "Tags:   $TAGS_PATH"

conda run -n physgauss python -m src.simulation.runner \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_PATH" \
    --config "$CONFIG_PATH" \
    --tags_path "$TAGS_PATH" \
    --render_img --compile_video

# Save to experiments folder
EXP_DIR="$PROJECT_ROOT/data/experiments/$EXP_NAME"
mkdir -p "$EXP_DIR"
cp "$OUTPUT_PATH/output.mp4" "$EXP_DIR/"
cp "$CONFIG_PATH" "$EXP_DIR/"

echo "=== Experiment saved to $EXP_DIR ==="
