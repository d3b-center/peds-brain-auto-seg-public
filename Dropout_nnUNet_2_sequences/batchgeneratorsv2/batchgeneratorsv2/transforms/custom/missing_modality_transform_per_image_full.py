import torch
from batchgeneratorsv2.transforms.base.basic_transform import ImageOnlyTransform
from batchgeneratorsv2.helpers.scalar_type import RandomScalar

class MissingModalityTransform_perImage_full(ImageOnlyTransform):
    def __init__(self, probability: RandomScalar = 0.2, num_channels: int = 4):
        """
        Randomly zeroes out channels with probability p, ensuring at least one survives.
        """
        self.probability = probability
        self.num_channels = num_channels
        super().__init__()

    def get_parameters(self, **data_dict) -> dict:
        # Independent masking for each channel
        params = {
            f"mask_channel_{i}": torch.rand(1).item() < self.probability
            for i in range(self.num_channels)
        }

        # If all channels are masked, unmask one random channel
        if all(params.values()):
            keep_channel = torch.randint(0, self.num_channels, (1,)).item()
            params[f"mask_channel_{keep_channel}"] = False

        return params

    def _apply_to_image(self, img: torch.Tensor, **params) -> torch.Tensor:
        # Apply the masks
        for i in range(self.num_channels):
            if params[f"mask_channel_{i}"]:
                img[i] = 0
        return img
