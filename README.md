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

The segmentation labels for the multi-parametric model are described below:
1. Enhancing tumor (ET; label 1): Areas with enhancement (brightness) on contrast-enhanced T1 sequences (T1C) as compared to pre-contrast T1 (T1N) sequences. In case of mild enhancement, checking the signal intensity of normal brain structure can be helpful.

2. Nonenhancing tumor (NET; label 2): Any other abnormal signal intensity within the tumorous region that cannot be defined as enhancing or cystic. For example, the abnormal signal intensity on T1N, T2F, and T2W sequences that is not enhancing on T1C sequences should be considered as nonenhancing portion.

3. Cystic component (CC; label 3): Typically appearing with hyperintense signal (very bright) on T2W sequences and hypointense signal (dark) on T1C sequences. The cystic portion should be within the tumor, either centrally or peripherally (as compared to ED which is peritumoral). The brightness of CC is here defined as comparable or close to cerebrospinal fluid (CSF).

4. Peritumoral edema (ED; label 4): Abnormal hyperintense signal (very bright) on T2F sequences. ED is finger-like spreading that preserves underlying brain structure and surrounds the tumor.

## Results - Model performance on different pediatric brain tumor histologies
1. Multi-parametric model:
   
| Tumor sub-regions | DIPG/DMG (Dice)       | HGG (Dice)           | LGG (Dice)           | Medulloblastoma (Dice) | Others (Dice)        |
|-------------------|-----------------------|----------------------|----------------------|------------------------|----------------------|
| WT                | 0.92 ± 0.15 (0.98)    | 0.88 ± 0.10 (0.90)   | 0.86 ± 0.15 (0.91)   | 0.89 ± 0.05 (0.91)     | 0.55 ± 0.38 (0.65)   |
| ET                | 0.62 ± 0.39 (0.81)    | 0.53 ± 0.40 (0.67)   | 0.74 ± 0.28 (0.87)   | 0.81 ± 0.12 (0.80)     | 0.38 ± 0.44 (0.34)   |
| NET               | 0.90 ± 0.16 (0.96)    | 0.76 ± 0.18 (0.82)   | 0.51 ± 0.33 (0.61)   | 0.54 ± 0.30 (0.57)     | 0.33 ± 0.42 (0.22)   |
| CC                | 0.57 ± 0.47 (0.86)    | 0.61 ± 0.40 (0.72)   | 0.59 ± 0.43 (0.80)   | 0.51 ± 0.25 (0.50)     | 1.00 ± 0.00 (1.00)   |
| ED                | 0.88 ± 0.31 (1.00)    | 0.67 ± 0.44 (1.00)   | 0.52 ± 0.45 (0.55)   | 0.52 ± 0.42 (0.67)     | 1.00 ± 0.00 (1.00)   |
| NET+CC+ED         | 0.91 ± 0.16 (0.97)    | 0.84 ± 0.09 (0.86)   | 0.72 ± 0.26 (0.80)   | 0.76 ± 0.11 (0.76)     | 0.33 ± 0.42 (0.22)   |
| TC                | 0.92 ± 0.15 (0.98)    | 0.85 ± 0.12 (0.87)   | 0.83 ± 0.19 (0.89)   | 0.88 ± 0.06 (0.89)     | 0.55 ± 0.38 (0.65)   |

2. Whole tumor segmentation using T2w or T2w-FLAIR inputs:

| Tumor Histologies | WT Dice score (input: T2w) | WT Dice score (input: T2w-FLAIR) |
|-------------------|---------------------------|-------------------------------|
| DIPG              | 0.80 ± 0.23 (0.88)        | 0.83 ± 0.21 (0.90)            |
| Medullo           | 0.88 ± 0.07 (0.90)        | 0.84 ± 0.14 (0.88)            |
| LGG               | 0.87 ± 0.14 (0.91)        | 0.88 ± 0.09 (0.91)            |
| Others            | 0.82 ± 0.24 (0.92)        | 0.84 ± 0.22 (0.91)            |

3. Enhancing tumor segmentations using T1CE + T2w or T1CE + T2w-FLAIR inputs:

| Tumor histologies | ET Dice score (inputs: T1CE + T2w) | ET Dice score (inputs: T1CE + T2w-FLAIR) |
|--------------------------|------------------------------------|------------------------------------------|
| DIPG                     | 0.54 ± 0.41 (0.72)                 | 0.55 ± 0.40 (0.74)                       |
| Medullo                  | 0.74 ± 0.25 (0.82)                 | 0.74 ± 0.25 (0.81)                       |
| LGG                      | 0.76 ± 0.28 (0.88)                 | 0.74 ± 0.29 (0.87)                       |
| Others                   | 0.49 ± 0.39 (0.67)                 | 0.55 ± 0.39 (0.73)                       |


## Usage & Citations
Note: Use of this software is available to academic and non-profit institutions for research purposes only subject to the terms of the 2-Clause BSD License (see License). For use or transfers of the software to commercial entities, please inquire with Dr. Anahita Fathi Kazerooni - fathikazea@chop.edu. 

If you use the model in your research study, please cite the following paper(s):
1. Gandhi DB, Khalili N, Familiar AM, Gottipati A, Khalili N, Tu W, Haldar S, Anderson H, Viswanathan K, Storm PB, Ware JB, Resnick A, Vossough A, Nabavizadeh A, Fathi Kazerooni A. Automated pediatric brain tumor imaging assessment tool from CBTN: Enhancing suprasellar region inclusion and managing limited data with deep learning. Neurooncol Adv. 2024 Dec 12;6(1):vdae190. doi: 10.1093/noajnl/vdae190. PMID: 39717438; PMCID: PMC11664259.
2. Arastoo Vossough, Nastaran Khalili, Ariana M. Familiar, Deep Gandhi, Karthik Viswanathan, Wenxin Tu, Debanjan Haldar, Sina Bagheri, Hannah Anderson, Shuvanjan Haldar, Phillip B. Storm, Adam Resnick, Jeffrey B. Ware, Ali Nabavizadeh, Anahita Fathi Kazerooni, "Training and Comparison of nnU-Net and DeepMedic Methods for Autosegmentation of Pediatric Brain Tumors", https://arxiv.org/abs/2401.08404
