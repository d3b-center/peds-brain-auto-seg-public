import torch
from batchgeneratorsv2.transforms.base.basic_transform import ImageOnlyTransform
from batchgeneratorsv2.helpers.scalar_type import RandomScalar

class MissingModalityTransform_perImage(ImageOnlyTransform):
    def __init__(self, probability: RandomScalar = 0.2):
        """
        Custom transform to randomly set channels 0 and 1 of an image to 0 independently
        with a given probability. The segmentation remains unchanged.

        :param probability: Probability of setting each channel independently to 0.
        """
        self.probability = probability
        super().__init__()

    def get_parameters(self, **data_dict) -> dict:
        """
        Generates a dictionary of parameters needed for the augmentation.
        """
        params = {
            "mask_channel_0": torch.rand(1).item() < self.probability,
            "mask_channel_1": torch.rand(1).item() < self.probability
        }
        return params

    def _apply_to_image(self, img: torch.Tensor, **params) -> torch.Tensor:
        """
        Applies the missing modality effect to the image.
        """
        if params.get("mask_channel_0", False):
            img[0] = 0  # Set channel 0 to zero
        if params.get("mask_channel_1", False):
            img[1] = 0  # Set channel 1 to zero
        return img
