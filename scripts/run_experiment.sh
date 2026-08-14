echo "Cleaning up old masks..."
rm -rf output/config/masks_output

echo "Running Pipeline (Rendering and Segmentation) with new prompts..."
conda run -n physgauss python pipeline.py \
    --model_path "$PROJECT_ROOT/data/models/ficus_whitebg" \
    --output_config output/config/output_config.json \
    --prompts "ceramic pot" "wooden branch" "thin brown plant stem" "leaves"

echo "Running FlashSplat Optimization..."
conda run -n physgauss python run_flashsplat.py \
    --model_path "$PROJECT_ROOT/data/models/ficus_whitebg" \
    --masks_dir output/config/masks_output \
    --output_dir output/config \
    --prompts "ceramic pot" "wooden branch" "thin brown plant stem" "leaves"

echo "Verifying Tags..."
conda run -n physgauss python verify_tags.py \
    --model_path "$PROJECT_ROOT/data/models/ficus_whitebg" \
    --tags_path output/config/material_tags.pt \
    --output_dir output/verify_renders