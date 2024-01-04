# PedsBrainAutoSeg tool

This tool can be used to generate AI-predicted brain tumor segmentations for pediatric patients with multi-parametric MRIs. It was trained using the nnU-Net framework on a multi-institutional, heterogeneous dataset (see reference).

Based on 4 input image sequences per patient, the model will output a single prediction file with up to 4 tumor subregions:
1. Enhancing tumor
2. Non-enhancing tumor
3. Cyst
4. Edema

If you use this tool in your work, please cite the following reference accordingly:

[...]

## STEP 1: Prepare the input files

The model requires 4 images per subject (T2w-FLAIR, T1w, T1w post-contrast, T2w).

### Preprocessing

Input files must be pre-processed, we recommend using the [BraTS pipeline](https://cbica.github.io/CaPTk/preprocessing_brats.html) to follow the same pre-processing steps as was performed on the training data.

### Organization

Pre-processed input files must be located in an `input/` directory folder and named with the following format: `[subID]_[imageID].nii.gz` where the imageID for each image type is:

| Image type      | imageID |
| ----------- | ----------- |
| T2w-FLAIR      | 000       |
| T1w   | 001        |
| T1w post-contrast   | 002        |
| T2w   | 003        |



For example:
```
input/
    sub001_000.nii.gz
    sub001_001.nii.gz
    sub001_002.nii.gz
    sub001_003.nii.gz
    sub002_000.nii.gz
    ...
```


## STEP 2: Usage

1. [Install Docker](https://docs.docker.com/engine/install/)
2. copy the `docker-compose.yml` file from this repository into the directory that contains your `input/` folder
3. from within that folder, run the command:
```
docker compose up
```

It takes about an hour to fully process a single subject's data (depending on your machine specs). Model predictions will be stored in an `output/` folder labeled `[subID]_000.nii.gz` .