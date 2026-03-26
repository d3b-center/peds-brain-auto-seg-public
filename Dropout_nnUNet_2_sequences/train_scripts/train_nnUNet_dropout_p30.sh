#!/bin/bash
#SBATCH --mem=32G
#SBATCH -c 16
#SBATCH -t 16:00:00
#SBATCH --error=/logs/err_%j.err
#SBATCH --output=/logs/out_%j.out
#SBATCH -p gpuq
#SBATCH --gres=gpu:a100:1
#SBATCH --job-name=drp_p30

module load cuda11.8/toolkit/11.8.0
nvidia-smi
date

# Activate the Miniconda base environment
source {your_conda_directory}/miniconda3/bin/activate

conda activate drp_nnUNet
# pip install blosc2


cd {parent_directory}/nnUNet

export nnUNet_raw="{parent_directory}/data/raw"
export nnUNet_preprocessed="{parent_directory}/data/preprocessed"
export nnUNet_results="{parent_directory}/data/results"

nnUNetv2_train Dataset001_BrainTumor 3d_fullres 0 -tr nnUNetTrainerDropout_p30
