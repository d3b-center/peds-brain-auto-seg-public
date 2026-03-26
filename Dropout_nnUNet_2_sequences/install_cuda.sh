#!/bin/bash
#SBATCH --job-name=fix_torch_cuda
#SBATCH -p gpuq
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=32G
#SBATCH -c 4
#SBATCH -t 02:00:00
#SBATCH --output=/home/chrysochod/DRP_REPLICATION_FOR_GIT_PUBLISHING/logs/fix_torch_cuda_%j.out
#SBATCH --error=/home/chrysochod/DRP_REPLICATION_FOR_GIT_PUBLISHING/logs/fix_torch_cuda_%j.err

set -euo pipefail

echo "Job started on $(hostname)"
date

module load cuda11.8/toolkit/11.8.0
nvidia-smi

# Activate conda
source /home/chrysochod/miniconda3/bin/activate
conda activate dropout_nnunet

# Make sure ~/.local never interferes
export PYTHONNOUSERSITE=1
unset PYTHONPATH

echo "===== Before ====="
which python
python -V
python -c "import torch; print('torch:', torch.__version__, 'cuda:', torch.version.cuda, 'file:', torch.__file__)"

echo "===== Conda packages (before) ====="
conda list | egrep -i "pytorch|torchvision|torchaudio|pytorch-cuda|pytorch-mutex|cudnn|nccl|cuda" || true

# Optional: remove CPU-only torch stack if present (ignore errors)
conda remove -y pytorch torchvision torchaudio pytorch-cuda 2>/dev/null || true

echo "===== Installing CUDA-enabled PyTorch 2.6.0 + CUDA 11.8 ====="
# Force reinstall from pytorch+nvidia channels
conda install -y -c pytorch -c nvidia \
  "pytorch=2.6.0" "torchvision=0.21.0" "torchaudio=2.6.0" "pytorch-cuda=11.8" \
  --force-reinstall

echo "===== Conda packages (after) ====="
conda list | egrep -i "pytorch|torchvision|torchaudio|pytorch-cuda|pytorch-mutex|cudnn|nccl|cuda" || true

echo "===== After ====="
python -c "import torch; print('torch:', torch.__version__, 'cuda:', torch.version.cuda, 'avail:', torch.cuda.is_available()); print('file:', torch.__file__)"
python -c "import torch; print('device0:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO GPU')"

echo "Done."
