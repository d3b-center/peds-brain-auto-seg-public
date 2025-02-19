# PedsBrainAutoSeg tool

This tool can be used to generate AI-predicted brain tumor segmentations for pediatric patients with multi-parametric MRIs. It was trained using the nnU-Net framework on a multi-institutional, heterogeneous dataset (see reference).

Based on 4 input image sequences per patient, the model will output a single prediction file with up to 4 tumor subregions:
1. Enhancing tumor
2. Non-enhancing tumor
3. Cyst
4. Edema

If you use this tool in your work, please cite the following reference accordingly:

1. Gandhi DB, Khalili N, Familiar AM, Gottipati A, Khalili N, Tu W, Haldar S, Anderson H, Viswanathan K, Storm PB, Ware JB, Resnick A, Vossough A, Nabavizadeh A, Fathi Kazerooni A. Automated pediatric brain tumor imaging assessment tool from CBTN: Enhancing suprasellar region inclusion and managing limited data with deep learning. Neurooncol Adv. 2024 Dec 12;6(1):vdae190. doi: 10.1093/noajnl/vdae190. PMID: 39717438; PMCID: PMC11664259.
2. Arastoo Vossough, Nastaran Khalili, Ariana M. Familiar, Deep Gandhi, Karthik Viswanathan, Wenxin Tu, Debanjan Haldar, Sina Bagheri, Hannah Anderson, Shuvanjan Haldar, Phillip B. Storm, Adam Resnick, Jeffrey B. Ware, Ali Nabavizadeh, Anahita Fathi Kazerooni, "Training and Comparison of nnU-Net and DeepMedic Methods for Autosegmentation of Pediatric Brain Tumors", https://arxiv.org/abs/2401.08404

## STEP 1: Prepare the input files

The model requires 4 images per subject (T2w-FLAIR, T1w, T1w post-contrast, T2w).

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
2. copy the `docker-compose.yml` file from this repository into the directory that contains your `input/` folder:
    ```
    docker-compose.yml
    input/
        sub001_FL.nii.gz
        sub001_T1.nii.gz
        ...
    ```
3. from within that folder, run the command:
    ```
    docker compose up
    ```

or if the yaml is not named `docker-compose.yml` then specify the file with -f:
    ```
    docker compose -f docker-compose_t1ceandt2orflair.yml up
    ```

It takes about an hour to fully process a single subject's data (depending on your machine specs). Model predictions will be stored in an `output/` folder with files named `[subID]_pred_brainTumorSeg.nii.gz` .


## Usage & Citations
Note: Use of this software is available to academic and non-profit institutions for research purposes only subject to the terms of the 2-Clause BSD License (see License). For use or transfers of the software to commercial entities, please inquire with Dr. Anahita Fathi Kazerooni - fathikazea@chop.edu. 

If you use the model in your research study, please cite the following paper(s):
1. Gandhi DB, Khalili N, Familiar AM, Gottipati A, Khalili N, Tu W, Haldar S, Anderson H, Viswanathan K, Storm PB, Ware JB, Resnick A, Vossough A, Nabavizadeh A, Fathi Kazerooni A. Automated pediatric brain tumor imaging assessment tool from CBTN: Enhancing suprasellar region inclusion and managing limited data with deep learning. Neurooncol Adv. 2024 Dec 12;6(1):vdae190. doi: 10.1093/noajnl/vdae190. PMID: 39717438; PMCID: PMC11664259.
2. Arastoo Vossough, Nastaran Khalili, Ariana M. Familiar, Deep Gandhi, Karthik Viswanathan, Wenxin Tu, Debanjan Haldar, Sina Bagheri, Hannah Anderson, Shuvanjan Haldar, Phillip B. Storm, Adam Resnick, Jeffrey B. Ware, Ali Nabavizadeh, Anahita Fathi Kazerooni, "Training and Comparison of nnU-Net and DeepMedic Methods for Autosegmentation of Pediatric Brain Tumors", https://arxiv.org/abs/2401.08404
