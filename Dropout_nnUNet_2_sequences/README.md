# AI-powered segmentation and prognosis with missing MRI in pediatric brain tumors
Link to the paper: https://doi.org/10.1038/s41698-025-01269-x

**Installation**

To clone the code and install all dependencies, run the block below, ensuring you have adjusted the prefix path in the requirements.yml

```
git clone https://github.com/dchry/dropout-nnunet-flair-t1.git
cd dropout-nnunet-flair-t1
conda env create -f requirements.yml
conda activate drp_nnUNet
cd nnUNet
pip install -e .
cd ../batchgeneratorsv2
pip install -e .

```

**Data formatting**

This repository is based on the nnUNet v2 model (https://github.com/MIC-DKFZ/nnUNet), so we follow their data convention for model training. The training and test data should be organized as shown below. We are using the following convention: FLAIR=0000, T1w-pre=0001, T1w-post=0002, T2w=0003. A sample dataset.json is included in our repo.

```
data/
├── raw/
│   └── Dataset001_BrainTumor/
│       ├── dataset.json
│       ├── imagesTr/
│       │   ├── Case001_0000.nii.gz
│       │   ├── Case001_0001.nii.gz
│       │   ├── Case001_0002.nii.gz
│       │   ├── Case001_0003.nii.gz
│       │   └── ...
│       ├── labelsTr/
│       │   ├── Case001.nii.gz
│       │   └── ...
│       ├── imagesTs/
│       │   ├── Case101_0000.nii.gz
│       │   ├── Case101_0001.nii.gz
│       │   ├── Case101_0002.nii.gz
│       │   ├── Case101_0003.nii.gz
│       │   └── ...
│       └── labelsTs/
│           ├── Case101.nii.gz
│           └── ...
│
├── preprocessed/
│   └── Dataset001_BrainTumor/
│       └── ...
│
└── results/
    └── Dataset001_BrainTumor/
        └── ...

```

**Model Training**

First, we run the plan and preprocess command. You can use the following script, ensuring you have adjusted the required paths. The script will populate the data/preprocessed directory with preprocessed data.

```
train_scripts/plan_and_preprocess.sh
```
Then, we train 3d_fullres configuration nnUNet models with different levels of dropout applied independently to channels 0 (FLAIR) and 1 (T1w-pre). For example, to train a model with modality dropout of p=0.4 (optimal level of dropout based on the 85 validation CBTN patients), you can use the script below. Trained models are stored under data/results.
```
train_scripts/train_nnUNet_dropout_p40.sh
```
For more clarity on the **dropout functionality**, you can inspect the scripts under 

```
nnUNet/nnunetv2/training/nnUNetTrainer/nnUNetTrainerDropout_pX.py, X={0,10,...,100}
batchgeneratorsv2/batchgeneratorsv2/transforms/custom/missing_modality_transform_per_image.py
```
**Inference**

During inference, the model expects 4 nifti scans with the nnUNet v2 model naming convention. We set missing FLAIR and/or T1 to zeroed images and copy available modalities using the script below
```
inference_scripts/copy_zFL_zT1.py
```

We can then use the models trained at different dropout levels with the corresponding scripts under /inference_scripts. For example, for the model trained with p=0.4, you can use the following script, adjusting the associated paths. 
```
inference_scripts/infer_nnUNet_dropout_p40.sh
```

**Evaluation**

To calculate Dice scores for the predicted segmentation masks per subregion, you can adapt the following script to your evaluation pipeline

```
inference_scripts/dice.py
```

## Developer: Dimosthenis Chrysochoou

## Usage & Citations
Note: Use of this software is available to academic and non-profit institutions for research purposes only subject to the terms of the 2-Clause BSD License (see License). For use or transfers of the software to commercial entities, please inquire with Dr. Anahita Fathi Kazerooni - fathikazea@chop.edu. 

If you use the model in your research study, please cite the following paper:

1. Chrysochoou, D., Gandhi, D.B., Adib, S. et al. AI-powered segmentation and prognosis with missing MRI in pediatric brain tumors. npj Precis. Onc. (2026). https://doi.org/10.1038/s41698-025-01269-x

