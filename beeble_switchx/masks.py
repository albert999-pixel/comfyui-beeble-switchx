"""Mask conversion helpers for Beeble SwitchX."""

from __future__ import annotations

from pathlib import Path

from .errors import BeebleMediaError

try:
    import numpy as np
except ImportError:
    np = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import torch
except ImportError:
    torch = None


def save_mask_as_grayscale_png(mask, output_path: str, invert: bool = False) -> str:
    """Save the first MASK item as a grayscale PNG file."""
    if torch is None or np is None or Image is None:
        raise BeebleMediaError(
            "Saving MASK to PNG requires torch, numpy, and Pillow in the ComfyUI environment."
        )

    if not isinstance(mask, torch.Tensor):
        raise BeebleMediaError("Expected MASK to be a torch.Tensor.")

    if mask.ndim == 3:
        if mask.shape[0] < 1:
            raise BeebleMediaError("MASK batch is empty.")
        # MVP behavior: use only the first batch item when MASK is batched.
        mask = mask[0]
    elif mask.ndim != 2:
        mask = mask.squeeze()
        if mask.ndim != 2:
            raise BeebleMediaError(f"Unsupported MASK shape: {tuple(mask.shape)}")

    local_path = Path(output_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    array = mask.detach().cpu().clamp(0, 1).numpy()
    if invert:
        array = 1.0 - array
    array = (array * 255.0).round().astype(np.uint8)

    try:
        Image.fromarray(array, mode="L").save(local_path, format="PNG")
    except Exception as exc:
        raise BeebleMediaError(f"Failed to save MASK as PNG: {exc}") from exc

    return str(local_path)


def load_mask_file_as_tensor(path: str):
    """Load a grayscale image file as a ComfyUI MASK tensor."""
    if torch is None or np is None or Image is None:
        raise BeebleMediaError(
            "Loading MASK from file requires torch, numpy, and Pillow in the ComfyUI environment."
        )

    local_path = Path(path)
    if not local_path.is_file():
        raise BeebleMediaError(f"Mask file does not exist: {path}")

    try:
        with Image.open(local_path) as image:
            image = image.convert("L")
            array = np.asarray(image, dtype=np.float32) / 255.0
    except Exception as exc:
        raise BeebleMediaError(f"Failed to load mask file: {exc}") from exc

    return torch.from_numpy(array)


def empty_mask_like_image(image):
    """Create an empty MASK matching the first IMAGE batch item dimensions."""
    if torch is None:
        raise BeebleMediaError("Creating an empty MASK requires torch in the ComfyUI environment.")

    if not isinstance(image, torch.Tensor):
        raise BeebleMediaError("Expected IMAGE to be a torch.Tensor.")

    if image.ndim == 4:
        if image.shape[0] < 1:
            raise BeebleMediaError("IMAGE batch is empty.")
        height, width = image.shape[1], image.shape[2]
    elif image.ndim == 3:
        height, width = image.shape[0], image.shape[1]
    else:
        raise BeebleMediaError(f"Unsupported IMAGE shape: {tuple(image.shape)}")

    return torch.zeros((height, width), dtype=image.dtype, device=image.device)


__all__ = ["empty_mask_like_image", "load_mask_file_as_tensor", "save_mask_as_grayscale_png"]
