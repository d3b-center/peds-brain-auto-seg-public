## Pediatric Automated Tumor Segmentation

If you use this tool, please cite the following reference:

### Inputs

1. T2w-FLAIR
2. T1w
3. T1w post-contrast
4. T2w

```
input/
    sub001_000.nii.gz
    sub001_001.nii.gz
    sub001_002.nii.gz
    sub001_003.nii.gz
    sub002_000.nii.gz
    ...
```

Pre-processed using BraTS pipeline

### Usage

1. Install Docker
2. copy the docker-compose.yml file into the directory with your input/ folder
3. run the command:
```
docker compose up
```

Predictions will be stored in an output/ folder.