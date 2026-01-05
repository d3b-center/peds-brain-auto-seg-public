About This Repository

## AI-Powered Segmentation and Prognosis with Missing MRI in Pediatric Brain Tumors**

This repository contains a modified version of `nnUNetv2` with support for robust segmentation under missing T1w-pre and/or FLAIR.
**UPDATE 10/10/25**: Currently testing models for robustness to all 4 sequences. 

- The core modifications are implemented in  
  `nnUNet/nnunetv2/training/nnUNetTrainer/`,  
  where several `nnUNetTrainerDropout_pX` variants (e.g., `p0`, `p40`,..., `p100`) have been added. UPDATE (10/10): new variants `nnUNetTrainerDropout_full_pX` have been added for handling all 4 sequences. 

- Custom transforms to support dropout are defined in  
  `batchgeneratorsv2/batchgeneratorsv2/transforms/custom/`.
  **UPDATE 10/10/25**: `batchgeneratorsv2/batchgeneratorsv2/transforms/custom/missing_modality_transform_per_image_full.py`.

To use the modified utilities, simply clone this repository:
```bash
git clone https://github.com/d3b-center/peds-brain-auto-seg-public.git
cd dropout-nnunet-v2
conda env create -f environment_full.yml
cd peds-brain-auto-seg-public/Dropout_nnUNet_2_sequences/nnUNet-master
pip install -e .
cd ../batchgeneratorsv2
pip install -e .
```

The p40 model was termed optimal based on the 85-patient CBTN validation set. p40 should be used for any future inference. All models were trained for a single fold (fold0).

## Prepare dataset for inference
In the `create_dataset` folder, exist scripts to prepare the dataset for inference under missing FLAIR and/or missing T1w-pre. It just takes a list of subjects (in this example case from a .json file) and renames them according to the nnUNet channel convention. The missing scans are simply created as zero tensors of appropriate dimensions and are stored in channels 0002 and/or 0003.  

## Segment based on pre-trained models

The script `infer_nnUNet_dropout_p40.sh` contains the code for segmentation with the p40 model. You just need to specify the input (-i) directory with cases to be segmented
and the output (-o) folder for the predicted masks. In this case, the example is set up for various missing and complete MRI scenarios. 
Note the model `-tr nnUNetTrainerDropout_p40` remains fixed as it can handle missing FLAIR and/or T1w-pre. `-f0` uses the only trained fold0. Also, the model needs access to the
trained models `export nnUNet_results="/home/chrysochod/dropout_nnUNet_data/results"` and the requirements in the `drp_nnUNet_v3` (in environment_full.yml) and `pip install blosc2` 

## Train new models for missing FLAIR and T1w-pre
To train additional models, prepare the dataset following the nnUNet convention. Then run the plan_and_preprocess_mmUNet.sh script. To train a model with the desired level of Dropout, run train_nnUNet_dropout_pX.sh X={0,10,20,...,100}. You can start multiple jobs on the cluster so they can run at the same time. It takes ~12h per dropout value, so I would recommend submitting as many jobs as possible. Note: we are only training a single fold (-f0) with a 3d full_res configuration. 

## UPDATE 10/10: Train new models for handling all 4 sequences
To train additional models, prepare the dataset following the nnUNet convention. Then run the plan_and_preprocess_nnUNet.sh script. To train a model with the desired level of Dropout, run train_nnUNet_dropout_full_pX.sh X={0,10,20,...,100}. Ensure the directories (raw, preprocessed, results) are as intended. You can start multiple jobs on the cluster so they can run at the same time. It takes ~12h per dropout value, so I would recommend submitting as many jobs as possible. Note: we are only training a single fold (-f0) with a 3d full_res configuration. Once optimal p is found on -f0 models perhaps could train subsequent folds for the optimal p.  

## Developer: Dimosthenis Chrysochoou

## Usage & Citations
Note: Use of this software is available to academic and non-profit institutions for research purposes only subject to the terms of the 2-Clause BSD License (see License). For use or transfers of the software to commercial entities, please inquire with Dr. Anahita Fathi Kazerooni - fathikazea@chop.edu. 

If you use the model in your research study, please cite the following paper:

1. Dimosthenis Chrysochoou, Deep B. Gandhi, Sahand Adib, Ariana M. Familiar, Neda Khalili, Nastaran Khalili, Jeffrey B. Ware, Wenxin Tu, Paarth Jain, Hannah Anderson, Shuvanjan Haldar, Phillip B. Storm, Andrea Franson, Michael Prados, Cassie Kline, Sabine Mueller, Adam Resnick, Arastoo Vossough, Christos Davatzikos, Ali Nabavizadeh, Anahita Fathi Kazerooni, "AI-Powered Segmentation and Prognosis with Missing MRI in Pediatric Brain Tumors" medRxiv 2025.07.14.25331187; doi: https://doi.org/10.1101/2025.07.14.25331187
