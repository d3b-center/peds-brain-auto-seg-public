

#!/bin/bash
#SBATCH --mem=32G
#SBATCH -c 16
#SBATCH -t 00:02:00
#SBATCH --error=/err/path
#SBATCH --output=/out/path
#SBATCH -p gpuq
#SBATCH --gres=gpu:a100:1
#SBATCH --job-name=infer_p10


module load cuda11.8/toolkit/11.8.0
nvidia-smi
date

# Activate the Miniconda base environment
source {your_conda_directory}/miniconda3/bin/activate

conda activate drp_nnUNet
# pip install blosc2


cd {parent_directory}/nnUNet

export nnUNet_results="{parent_directory}/data/results"


nnUNetv2_predict -i /path/to/nifti/to/be/segmented \
                 -o /path/ti/store/predicted/segmentation/masks \
                 -d Dataset001_BrainTumor \
                 -c 3d_fullres \
                 -f 0 \
                 -tr nnUNetTrainerDropout_p10
