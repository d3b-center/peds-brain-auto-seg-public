#!/usr/bin/env python3
import argparse
import nibabel as nib
import numpy as np
import os


def create_nifti(modality, reference_file, output_file):
    # Load reference NIfTI to copy affine and header
    ref_img = nib.load(reference_file)
    affine = ref_img.affine
    header = ref_img.header

    # Create zero array with shape [240, 240, 155]
    data = np.zeros((240, 240, 155), dtype=np.float32)

    # Create new NIfTI image
    new_img = nib.Nifti1Image(data, affine, header)

    # Save the new file
    nib.save(new_img, output_file)
    print(f"[INFO] Created {modality} file: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a NIfTI file with zeros, using reference affine and header.")
    parser.add_argument("--modality", type=str, required=True, help="Modality name (e.g., t1, fl)")
    parser.add_argument("--reference", type=str, required=True, help="Path to reference NIfTI file (e.g., t1ce)")
    parser.add_argument("--output", type=str, required=True, help="Path to save the new NIfTI file")

    args = parser.parse_args()

    if not os.path.exists(args.reference):
        raise FileNotFoundError(f"Reference file not found: {args.reference}")

    create_nifti(args.modality, args.reference, args.output)
