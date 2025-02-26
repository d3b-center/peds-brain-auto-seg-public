# PedsBrainAutoSeg tool

This tool can be used to generate AI-predicted brain tumor segmentations for pediatric patients with any available combination of brain MRIs - including 1) multiparametric MRI i.e., T2w-FLAIR, T1w, T1w post-contrast, T2w; 2) either T2w-FLAIR or T2w; and 3) T1w post-contrast and either  T2w-FLAIR or T2w. It was trained using the nnU-Net framework on a multi-institutional, heterogeneous dataset (see reference).

Based on the provided input image sequences per patient, 
1) Multiparametric inputs will output a single prediction file with up to 4 tumor subregions: Enhancing tumor, Non-enhancing tumor, Cyst and Edema.
2) T2w-FLAIR or T2w inputs will output a single prediction file with whole brain tumor segmentation.
3) T1w post-contrast and either T2w-FLAIR or T2w inputs will output a single prediction file with enhancing brain tumor segmentation.

If you use this tool in your work, please cite the following reference accordingly:

1. Gandhi DB, Khalili N, Familiar AM, Gottipati A, Khalili N, Tu W, Haldar S, Anderson H, Viswanathan K, Storm PB, Ware JB, Resnick A, Vossough A, Nabavizadeh A, Fathi Kazerooni A. Automated pediatric brain tumor imaging assessment tool from CBTN: Enhancing suprasellar region inclusion and managing limited data with deep learning. Neurooncol Adv. 2024 Dec 12;6(1):vdae190. doi: 10.1093/noajnl/vdae190. PMID: 39717438; PMCID: PMC11664259.
2. Arastoo Vossough, Nastaran Khalili, Ariana M. Familiar, Deep Gandhi, Karthik Viswanathan, Wenxin Tu, Debanjan Haldar, Sina Bagheri, Hannah Anderson, Shuvanjan Haldar, Phillip B. Storm, Adam Resnick, Jeffrey B. Ware, Ali Nabavizadeh, Anahita Fathi Kazerooni, "Training and Comparison of nnU-Net and DeepMedic Methods for Autosegmentation of Pediatric Brain Tumors", https://arxiv.org/abs/2401.08404

## STEP 1: Prepare the input files

The multi-parametric model requires 4 images per subject (T2w-FLAIR, T1w, T1w post-contrast, T2w).
However, if all 4 images are not available you can provide either T2w-FLAIR or T2w inputs for just the whole tumor segmentation or T1w post-contrast and either T2w-FLAIR or T2w inputs for enhancing tumor segmentation. 

### Preprocessing

Input files must be pre-processed, we recommend using the [BraTS pipeline](https://cbica.github.io/CaPTk/preprocessing_brats.html) to follow the same pre-processing steps as was performed on the training data.

### Organization

Pre-processed input files must be located in an `input/` directory folder (called "input") and named with the following format: `[subID]_[imageID]...[.nii/.nii.gz]` where the imageID for each image type is:

| Image type      | imageID |
| ----------- | ----------- |
| T2w-FLAIR      | FL       |
| T1w   | T1        |
| T1w post-contrast   | T1CE        |
| T2w   | T2        |

NOTE: the exact file format is required with an underscore: [subID]_[imageID]

For example:
```
input/
    sub001_FL.nii.gz
    sub001_T1.nii.gz
    sub001_T1CE.nii.gz
    sub001_T2.nii.gz
    sub002_FL.nii.gz
    ...
```


## STEP 2: Usage

1. [Install Docker](https://docs.docker.com/engine/install/)
2. copy the appropriate `.yml` file from this repository into the directory that contains your `input/` folder:
   
   `docker-compose_multiparametric.yml` for Multi-parametric inputs
   `docker-compose_t2orflair.yml` for T2w-FLAIR or T2w inputs
   `docker-compose_t1ceandt2orflair.yml` for T1w post-contrast and either T2w-FLAIR or T2w inputs

   example:
    ```
    docker-compose_multiparametric.yml
    input/
        sub001_FL.nii.gz
        sub001_T1.nii.gz
        sub001_T1CE.nii.gz
        sub001_T2.nii.gz
        ...
    ```
4. from within that folder, run the command:
    
    ```
    docker compose -f docker-compose_t1ceandt2orflair.yml up
    ```

It takes about an hour to fully process a single subject's data (depending on your machine specs). Model predictions will be stored in an `output/` folder with files named `[subID]_pred_brainTumorSeg.nii.gz` for multi-parametric model, `[subID]_pred_wholeTumorSeg.nii.gz` for T2/FLAIR model, OR for T1CE and T2/FLAIR model `[subID]_pred_enhancingTumorSeg.nii.gz` (enhancing region only).


## Usage & Citations
Note: Use of this software is available to academic and non-profit institutions for research purposes only subject to the terms of the 2-Clause BSD License (see License). For use or transfers of the software to commercial entities, please inquire with Dr. Anahita Fathi Kazerooni - fathikazea@chop.edu. 

If you use the model in your research study, please cite the following paper(s):
1. Gandhi DB, Khalili N, Familiar AM, Gottipati A, Khalili N, Tu W, Haldar S, Anderson H, Viswanathan K, Storm PB, Ware JB, Resnick A, Vossough A, Nabavizadeh A, Fathi Kazerooni A. Automated pediatric brain tumor imaging assessment tool from CBTN: Enhancing suprasellar region inclusion and managing limited data with deep learning. Neurooncol Adv. 2024 Dec 12;6(1):vdae190. doi: 10.1093/noajnl/vdae190. PMID: 39717438; PMCID: PMC11664259.
2. Arastoo Vossough, Nastaran Khalili, Ariana M. Familiar, Deep Gandhi, Karthik Viswanathan, Wenxin Tu, Debanjan Haldar, Sina Bagheri, Hannah Anderson, Shuvanjan Haldar, Phillip B. Storm, Adam Resnick, Jeffrey B. Ware, Ali Nabavizadeh, Anahita Fathi Kazerooni, "Training and Comparison of nnU-Net and DeepMedic Methods for Autosegmentation of Pediatric Brain Tumors", https://arxiv.org/abs/2401.08404
