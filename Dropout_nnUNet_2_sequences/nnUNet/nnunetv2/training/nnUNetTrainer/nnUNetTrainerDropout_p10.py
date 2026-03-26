#import base trainer so I can inherit from it
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

#import custom transform 
# from batchgeneratorsv2.transforms.custom.missing_modality_transform import MissingModalityTransform
from batchgeneratorsv2.transforms.custom.missing_modality_transform_per_image import MissingModalityTransform_perImage


#make all othet imports found in nnUNetTrainer 
import inspect
import multiprocessing
import os
import shutil
import sys
import warnings
from copy import deepcopy
from datetime import datetime
from time import time, sleep
from typing import Tuple, Union, List

import numpy as np
import torch
from batchgenerators.dataloading.multi_threaded_augmenter import MultiThreadedAugmenter
from batchgenerators.dataloading.nondet_multi_threaded_augmenter import NonDetMultiThreadedAugmenter
from batchgenerators.dataloading.single_threaded_augmenter import SingleThreadedAugmenter
from batchgenerators.utilities.file_and_folder_operations import join, load_json, isfile, save_json, maybe_mkdir_p
from batchgeneratorsv2.helpers.scalar_type import RandomScalar
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform
from batchgeneratorsv2.transforms.intensity.brightness import MultiplicativeBrightnessTransform
from batchgeneratorsv2.transforms.intensity.contrast import ContrastTransform, BGContrast
from batchgeneratorsv2.transforms.intensity.gamma import GammaTransform
from batchgeneratorsv2.transforms.intensity.gaussian_noise import GaussianNoiseTransform
from batchgeneratorsv2.transforms.nnunet.random_binary_operator import ApplyRandomBinaryOperatorTransform
from batchgeneratorsv2.transforms.nnunet.remove_connected_components import \
    RemoveRandomConnectedComponentFromOneHotEncodingTransform
from batchgeneratorsv2.transforms.nnunet.seg_to_onehot import MoveSegAsOneHotToDataTransform
from batchgeneratorsv2.transforms.noise.gaussian_blur import GaussianBlurTransform
from batchgeneratorsv2.transforms.spatial.low_resolution import SimulateLowResolutionTransform
from batchgeneratorsv2.transforms.spatial.mirroring import MirrorTransform
from batchgeneratorsv2.transforms.spatial.spatial import SpatialTransform
from batchgeneratorsv2.transforms.utils.compose import ComposeTransforms
from batchgeneratorsv2.transforms.utils.deep_supervision_downsampling import DownsampleSegForDSTransform
from batchgeneratorsv2.transforms.utils.nnunet_masking import MaskImageTransform
from batchgeneratorsv2.transforms.utils.pseudo2d import Convert3DTo2DTransform, Convert2DTo3DTransform
from batchgeneratorsv2.transforms.utils.random import RandomTransform
from batchgeneratorsv2.transforms.utils.remove_label import RemoveLabelTansform
from batchgeneratorsv2.transforms.utils.seg_to_regions import ConvertSegmentationToRegionsTransform
from torch import autocast, nn
from torch import distributed as dist
from torch._dynamo import OptimizedModule
from torch.cuda import device_count
from torch.cuda.amp import GradScaler
from torch.nn.parallel import DistributedDataParallel as DDP

from nnunetv2.configuration import ANISO_THRESHOLD, default_num_processes
from nnunetv2.evaluation.evaluate_predictions import compute_metrics_on_folder
from nnunetv2.inference.export_prediction import export_prediction_from_logits, resample_and_save
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
from nnunetv2.inference.sliding_window_prediction import compute_gaussian
from nnunetv2.paths import nnUNet_preprocessed, nnUNet_results
from nnunetv2.training.data_augmentation.compute_initial_patch_size import get_patch_size
from nnunetv2.training.dataloading.data_loader_2d import nnUNetDataLoader2D
from nnunetv2.training.dataloading.data_loader_3d import nnUNetDataLoader3D
from nnunetv2.training.dataloading.nnunet_dataset import nnUNetDataset
from nnunetv2.training.dataloading.utils import get_case_identifiers, unpack_dataset
from nnunetv2.training.logging.nnunet_logger import nnUNetLogger
from nnunetv2.training.loss.compound_losses import DC_and_CE_loss, DC_and_BCE_loss
from nnunetv2.training.loss.deep_supervision import DeepSupervisionWrapper
from nnunetv2.training.loss.dice import get_tp_fp_fn_tn, MemoryEfficientSoftDiceLoss
from nnunetv2.training.lr_scheduler.polylr import PolyLRScheduler
from nnunetv2.utilities.collate_outputs import collate_outputs
from nnunetv2.utilities.crossval_split import generate_crossval_split
from nnunetv2.utilities.default_n_proc_DA import get_allowed_n_proc_DA
from nnunetv2.utilities.file_path_utilities import check_workers_alive_and_busy
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans
from nnunetv2.utilities.helpers import empty_cache, dummy_context
from nnunetv2.utilities.label_handling.label_handling import convert_labelmap_to_one_hot, determine_num_input_channels
from nnunetv2.utilities.plans_handling.plans_handler import PlansManager

class nnUNetTrainerDropout_p10(nnUNetTrainer): #Define custom class and inherit from nnUnetTrainer class    

    def run_training(self): #Use this so we also get statistics on distribution of dropout.
        self.on_train_start()

        for epoch in range(self.current_epoch, self.num_epochs):
            self.on_epoch_start()

            # Initialize counters for the epoch
            ch0_zero_count = 0
            ch1_zero_count = 0
            both_zero_count = 0
            neither_zero_count = 0
            total_images = 0

            self.on_train_epoch_start()
            train_outputs = []
            for batch_id in range(self.num_iterations_per_epoch):
                batch = next(self.dataloader_train)  # Fetch batch

                # Extract image tensor
                images = batch['data']
                batch_size = images.shape[0]
                total_images += batch_size  # Increment image count

                # Debugging: Print shape, min, and max values for each image's channels
                print(f"\nEpoch {epoch}, Batch {batch_id} Debug Info:")
                for img_idx in range(batch_size):
                    # print(f"Image {img_idx}:")

                    ch0_min, ch0_max = images[img_idx, 0].min().item(), images[img_idx, 0].max().item()
                    ch1_min, ch1_max = images[img_idx, 1].min().item(), images[img_idx, 1].max().item()
                    ch2_min, ch2_max = images[img_idx, 2].min().item(), images[img_idx, 2].max().item()
                    ch3_min, ch3_max = images[img_idx, 3].min().item(), images[img_idx, 3].max().item()

                    # print(f"  Channel 0 -> Shape: {images[img_idx, 0].shape}, Min: {ch0_min}, Max: {ch0_max}")
                    # print(f"  Channel 1 -> Shape: {images[img_idx, 1].shape}, Min: {ch1_min}, Max: {ch1_max}")
                    # print(f"  Channel 2 -> Shape: {images[img_idx, 2].shape}, Min: {ch2_min}, Max: {ch2_max}")
                    # print(f"  Channel 3 -> Shape: {images[img_idx, 3].shape}, Min: {ch3_min}, Max: {ch3_max}")

                    # Count occurrences where channels are completely zero
                    ch0_is_zero = ch0_min == 0 and ch0_max == 0
                    ch1_is_zero = ch1_min == 0 and ch1_max == 0

                    if ch0_is_zero:
                        ch0_zero_count += 1
                    if ch1_is_zero:
                        ch1_zero_count += 1
                    if ch0_is_zero and ch1_is_zero:
                        both_zero_count += 1
                    if not ch0_is_zero and not ch1_is_zero:
                        neither_zero_count += 1

                # Debugging: Print shape, min, and max values for segmentation masks
                if isinstance(batch['target'], list):  # Deep supervision case (multiple segmentation outputs)
                    for i, target in enumerate(batch['target']):
                        print(f"Segmentation Level {i} -> Shape: {target.shape}, "
                            f"Min: {target.min().item()}, "
                            f"Max: {target.max().item()}")
                else:
                    print(f"Segmentation -> Shape: {batch['target'].shape}, "
                        f"Min: {batch['target'].min().item()}, "
                        f"Max: {batch['target'].max().item()}")

                train_outputs.append(self.train_step(batch))
            self.on_train_epoch_end(train_outputs)

            with torch.no_grad():
                self.on_validation_epoch_start()
                val_outputs = []
                for batch_id in range(self.num_val_iterations_per_epoch):
                    val_outputs.append(self.validation_step(next(self.dataloader_val)))
                self.on_validation_epoch_end(val_outputs)

            self.on_epoch_end()

            # Print dropout statistics at the end of the epoch
            print("\n=== Dropout Statistics for Epoch {} ===".format(epoch))
            print(f"Total images processed: {total_images}")
            print(f"Channel 0 was zeroed in {ch0_zero_count} / {total_images} images ({(ch0_zero_count / total_images) * 100:.2f}%)")
            print(f"Channel 1 was zeroed in {ch1_zero_count} / {total_images} images ({(ch1_zero_count / total_images) * 100:.2f}%)")
            print(f"Both channels were zeroed in {both_zero_count} / {total_images} images ({(both_zero_count / total_images) * 100:.2f}%)")
            print(f"Neither channel was zeroed in {neither_zero_count} / {total_images} images ({(neither_zero_count / total_images) * 100:.2f}%)")

        self.on_train_end()



    #only overwrite  get_training_transforms
    @staticmethod
    def get_training_transforms( 
            patch_size: Union[np.ndarray, Tuple[int]],
            rotation_for_DA: RandomScalar,
            deep_supervision_scales: Union[List, Tuple, None],
            mirror_axes: Tuple[int, ...],
            do_dummy_2d_data_aug: bool,
            use_mask_for_norm: List[bool] = None,
            is_cascaded: bool = False,
            foreground_labels: Union[Tuple[int, ...], List[int]] = None,
            regions: List[Union[List[int], Tuple[int, ...], int]] = None,
            ignore_label: int = None,
    ) -> BasicTransform:
        transforms = []
        if do_dummy_2d_data_aug:
            ignore_axes = (0,)
            transforms.append(Convert3DTo2DTransform())
            patch_size_spatial = patch_size[1:]
        else:
            patch_size_spatial = patch_size
            ignore_axes = None
        transforms.append(
            SpatialTransform(
                patch_size_spatial, patch_center_dist_from_border=0, random_crop=False, p_elastic_deform=0,
                p_rotation=0.2,
                rotation=rotation_for_DA, p_scaling=0.2, scaling=(0.7, 1.4), p_synchronize_scaling_across_axes=1,
                bg_style_seg_sampling=False  # , mode_seg='nearest'
            )
        )

        if do_dummy_2d_data_aug:
            transforms.append(Convert2DTo3DTransform())

        transforms.append(RandomTransform(
            GaussianNoiseTransform(
                noise_variance=(0, 0.1),
                p_per_channel=1,
                synchronize_channels=True
            ), apply_probability=0.1
        ))
        transforms.append(RandomTransform(
            GaussianBlurTransform(
                blur_sigma=(0.5, 1.),
                synchronize_channels=False,
                synchronize_axes=False,
                p_per_channel=0.5, benchmark=True
            ), apply_probability=0.2
        ))
        transforms.append(RandomTransform(
            MultiplicativeBrightnessTransform(
                multiplier_range=BGContrast((0.75, 1.25)),
                synchronize_channels=False,
                p_per_channel=1
            ), apply_probability=0.15
        ))
        transforms.append(RandomTransform(
            ContrastTransform(
                contrast_range=BGContrast((0.75, 1.25)),
                preserve_range=True,
                synchronize_channels=False,
                p_per_channel=1
            ), apply_probability=0.15
        ))
        transforms.append(RandomTransform(
            SimulateLowResolutionTransform(
                scale=(0.5, 1),
                synchronize_channels=False,
                synchronize_axes=True,
                ignore_axes=ignore_axes,
                allowed_channels=None,
                p_per_channel=0.5
            ), apply_probability=0.25
        ))
        transforms.append(RandomTransform(
            GammaTransform(
                gamma=BGContrast((0.7, 1.5)),
                p_invert_image=1,
                synchronize_channels=False,
                p_per_channel=1,
                p_retain_stats=1
            ), apply_probability=0.1
        ))
        transforms.append(RandomTransform(
            GammaTransform(
                gamma=BGContrast((0.7, 1.5)),
                p_invert_image=0,
                synchronize_channels=False,
                p_per_channel=1,
                p_retain_stats=1
            ), apply_probability=0.3
        ))
        if mirror_axes is not None and len(mirror_axes) > 0:
            transforms.append(
                MirrorTransform(
                    allowed_axes=mirror_axes
                )
            )

        if use_mask_for_norm is not None and any(use_mask_for_norm):
            transforms.append(MaskImageTransform(
                apply_to_channels=[i for i in range(len(use_mask_for_norm)) if use_mask_for_norm[i]],
                channel_idx_in_seg=0,
                set_outside_to=0,
            ))

        transforms.append(
            RemoveLabelTansform(-1, 0)
        )
        if is_cascaded:
            assert foreground_labels is not None, 'We need foreground_labels for cascade augmentations'
            transforms.append(
                MoveSegAsOneHotToDataTransform(
                    source_channel_idx=1,
                    all_labels=foreground_labels,
                    remove_channel_from_source=True
                )
            )
            transforms.append(
                RandomTransform(
                    ApplyRandomBinaryOperatorTransform(
                        channel_idx=list(range(-len(foreground_labels), 0)),
                        strel_size=(1, 8),
                        p_per_label=1
                    ), apply_probability=0.4
                )
            )
            transforms.append(
                RandomTransform(
                    RemoveRandomConnectedComponentFromOneHotEncodingTransform(
                        channel_idx=list(range(-len(foreground_labels), 0)),
                        fill_with_other_class_p=0,
                        dont_do_if_covers_more_than_x_percent=0.15,
                        p_per_label=1
                    ), apply_probability=0.2
                )
            )

        if regions is not None:
            # the ignore label must also be converted
            transforms.append(
                ConvertSegmentationToRegionsTransform(
                    regions=list(regions) + [ignore_label] if ignore_label is not None else regions,
                    channel_in_seg=0
                )
            )

        if deep_supervision_scales is not None:
            transforms.append(DownsampleSegForDSTransform(ds_scales=deep_supervision_scales))

        # Dropout Transform
        transforms.append(RandomTransform(
        MissingModalityTransform_perImage(probability=0.1), apply_probability=1.0
        ))


        return ComposeTransforms(transforms)
    


