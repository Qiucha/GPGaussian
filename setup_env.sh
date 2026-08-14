#!/bin/bash
set -e

echo "Creating environment physgauss_v2..."
conda create -n physgauss_v2 python=3.10 -y

echo "Installing PyTorch 2.3.1 and CUDA 12.1..."
conda run -n physgauss_v2 conda install pytorch==2.3.1 torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

echo "Installing CUDA Toolkit..."
conda run -n physgauss_v2 conda install -c "nvidia/label/cuda-12.1.0" cuda-toolkit -y

echo "Installing Compilers and Build Tools..."
conda run -n physgauss_v2 conda install -c conda-forge ninja cxx-compiler -y

echo "Phase 1 Complete."
