#!/bin/bash
set -e

source ~/miniforge3/bin/activate physgauss_v2
export CUDA_HOME=$CONDA_PREFIX
export CXX=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++
export CC=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc

echo "Installing Grounding DINO..."
pip install --no-build-isolation git+https://github.com/IDEA-Research/GroundingDINO.git

echo "Installing Segment Anything 2..."
pip install git+https://github.com/facebookresearch/segment-anything-2.git

echo "Phase 2 Complete."
