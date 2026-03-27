"""
Script: Prepare Incomplete-Modality Inference Set for nnUNet Segmentation

Description:
This script prepares a validation subset for segmentation experiments under 
missing-modality conditions. It performs the following steps:

1. Reads the validation subject IDs from `splits_final.json`. You can use your own list depending on your subcohort.
2. Copies the available modalities (T1ce and T2) for each subject into a 
   specified destination directory using nnUNet channel naming conventions.
3. Creates zero-filled NIfTI volumes to simulate missing modalities:
      - FLAIR  -> saved as *_0000.nii.gz
      - T1     -> saved as *_0001.nii.gz
4. The zero volumes inherit affine and header information from an existing 
   modality to preserve spatial metadata compatibility.

Purpose:
This enables evaluation of segmentation models under incomplete MRI inputs,
while maintaining nnUNet’s expected 4-channel structure:
    0000 = FLAIR
    0001 = T1
    0002 = T1ce
    0003 = T2

Assumptions:
- Input images follow nnUNet raw dataset structure:
  Dataset001_BrainTumor/imagesTr/<subject>_XXXX.nii.gz
- All volumes are 240×240×155.
- T1ce and T2 are available for every subject in the validation split.
- The destination directory already exists.
"""

import pandas as pd
import shutil
import os 
import nibabel as nib
import numpy as np 
import json

destination_directory = '/path/to/nifti/to/be/segmented'

#form subject list from splits_final.json
file_path = "data/preprocessed/Dataset001_BrainTumor/splits_final.json" 
# Load JSON data from file
with open(file_path, "r") as file:
    json_data = json.load(file)
# Extract the first "val" list
first_val_list = json_data[0]["val"] #first fold of validation set

print(first_val_list)

def sub_copy(path_T1ce, path_T2, directory_destination, element):
    new_names = {
        # path_FL: f"{element}_0000.nii.gz",
        # path_T1: f"{element}_0001.nii.gz",
        path_T1ce: f"{element}_0002.nii.gz",
        path_T2: f"{element}_0003.nii.gz"
    }

    # Copy and rename the files
    for src_path, new_name in new_names.items():
        if src_path:  # Only copy if the file exists
            dest_path = os.path.join(directory_destination, new_name)
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")


for subject in first_val_list:
    #Available modalities
    path_T2 = 'data/'+subject+'_0003.nii.gz'
    path_T1ce='data/'+subject+'_0002.nii.gz'

    sub_copy(path_T1ce, path_T2, destination_directory, subject)

    #Make a zero image for T1
    nii_img_T1CE = nib.load(path_T1ce) #I need affine and header 
    arr = np.zeros((240, 240, 155), dtype=np.float32)
    zero_NIIGZ = nib.Nifti1Image(arr, nii_img_T1CE.affine, nii_img_T1CE.header)
    output_filename = subject+'_0001.nii.gz'
    # Combine directory and filename to get the full path
    output_path = os.path.join(destination_directory, output_filename)
    # Save the Nifti image to the specified path
    nib.save(zero_NIIGZ ,output_path)
    print("Zero saved at " + output_path)

    #Make a zero image for FLAIR
    nii_img_T2 = nib.load(path_T2) #I need affine and header 
    print(nii_img_T2.shape)
    arr = np.zeros((240, 240, 155), dtype=np.float32)
    zero_NIIGZ = nib.Nifti1Image(arr, nii_img_T2.affine, nii_img_T2.header)
    output_filename = subject+'_0000.nii.gz'
    # Combine directory and filename to get the full path
    output_path = os.path.join(destination_directory, output_filename)
    # Save the Nifti image to the specified path
    nib.save(zero_NIIGZ ,output_path)
    print("Zero saved at " + output_path)

