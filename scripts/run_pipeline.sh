#!/bin/bash
set -e

# Intended path: PartSAM Material Tag Tensor (or reuse occupied tags) → PhysGaussian MPM Solver.
# FlashSplat / color_heuristic are not on this runner. Run from project root.

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

MODEL_PATH="$PROJECT_ROOT/data/models/ficus_whitebg"
OUTPUT_DIR="$PROJECT_ROOT/data/outputs"
PARTSAM_DIR="$OUTPUT_DIR/partsam"
TAGS_PATH="$OUTPUT_DIR/tags/material_tags.pt"
MASKS_PATH="$PARTSAM_DIR/part_masks.npz"
IOU_PATH="$PARTSAM_DIR/chosen_iou.json"
CONFIG_DIR="$PROJECT_ROOT/configs"
export PARTSAM_ROOT="${PARTSAM_ROOT:-$PROJECT_ROOT/third_party/PartSAM}"

PARTSAM_CLI=(python -m src.segmentation.partsam
    --model_path "$MODEL_PATH"
    --output_dir "$PARTSAM_DIR"
    --tags_path "$TAGS_PATH")

if conda run -n physgauss "${PARTSAM_CLI[@]}" --check-occupancy; then
    echo "Reusing existing Material Tag Tensor: $TAGS_PATH"
else
    echo "1. PartSAM Stage 1 surface (physgauss)..."
    conda run -n physgauss "${PARTSAM_CLI[@]}" --stage surface

    if [[ -f "$MASKS_PATH" && -f "$IOU_PATH" ]]; then
        echo "3. PartSAM Stage 3 rematerialize (physgauss)..."
        conda run -n physgauss "${PARTSAM_CLI[@]}" --stage lift
    else
        echo "2. PartSAM Stage 2 clicks (physgauss)..."
        conda run -n physgauss "${PARTSAM_CLI[@]}" --stage clicks

        echo "3. PartSAM Stage 3 lift (PartSAM env)..."
        conda run -n PartSAM "${PARTSAM_CLI[@]}" --stage lift
    fi
fi

echo "4. Running PhysGaussian MPM Solver & rendering..."
conda run -n physgauss python -m src.simulation.runner \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_DIR/simulated_video" \
    --config "$CONFIG_DIR/ficus.json" \
    --tags_path "$TAGS_PATH" \
    --render_img --compile_video

echo "Pipeline complete."
echo "Output video: $OUTPUT_DIR/simulated_video/output.mp4"
