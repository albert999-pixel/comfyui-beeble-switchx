"""Media conversion helpers for Beeble SwitchX."""

from __future__ import annotations
import logging
import time
from pathlib import Path
from urllib import error, parse, request

from .api import (
    BEEBLE_NETWORK_RETRY_COUNT,
    BEEBLE_NETWORK_RETRY_DELAY,
    format_network_error_message,
    should_retry_url_error,
)
from .errors import BeebleMediaError

try:
    from comfy_api.input_impl import VideoFromFile
except ImportError:
    VideoFromFile = None

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


LOGGER = logging.getLogger(__name__)


def save_image_tensor_as_png(image, output_path: str) -> str:
    """Save the first IMAGE batch item as a PNG file."""
    if torch is None or np is None or Image is None:
        raise BeebleMediaError(
            "Saving IMAGE to PNG requires torch, numpy, and Pillow in the ComfyUI environment."
        )

    if not isinstance(image, torch.Tensor):
        raise BeebleMediaError("Expected IMAGE to be a torch.Tensor.")

    if image.ndim == 4:
        if image.shape[0] < 1:
            raise BeebleMediaError("IMAGE batch is empty.")
        # MVP behavior: use only the first batch item when IMAGE is batched.
        image = image[0]
    elif image.ndim != 3:
        raise BeebleMediaError(f"Unsupported IMAGE shape: {tuple(image.shape)}")

    if image.shape[-1] not in (1, 3, 4):
        raise BeebleMediaError(
            f"Unsupported IMAGE channel count: {image.shape[-1]}"
        )

    local_path = Path(output_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    array = image.detach().cpu().clamp(0, 1).numpy()
    array = (array * 255.0).round().astype(np.uint8)

    if array.shape[-1] == 1:
        pil_image = Image.fromarray(array[..., 0], mode="L")
    elif array.shape[-1] == 3:
        pil_image = Image.fromarray(array, mode="RGB")
    else:
        pil_image = Image.fromarray(array, mode="RGBA")

    pil_image.save(local_path, format="PNG")
    return str(local_path)


def save_video_input_to_file(video, output_path: str) -> str:
    """Save a VIDEO input to a local file path."""
    if not hasattr(video, "save_to"):
        raise BeebleMediaError("Expected VIDEO input with a save_to() method.")

    local_path = Path(output_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        video.save_to(str(local_path))
    except Exception as exc:
        raise BeebleMediaError(f"Failed to save VIDEO to file: {exc}") from exc

    if not local_path.is_file():
        raise BeebleMediaError(f"VIDEO save did not create a file: {local_path}")

    return str(local_path)


def load_image_file_as_tensor(path: str):
    """Load an image file as a ComfyUI IMAGE tensor with shape [1, H, W, C]."""
    if torch is None or np is None or Image is None:
        raise BeebleMediaError(
            "Loading IMAGE from file requires torch, numpy, and Pillow in the ComfyUI environment."
        )

    local_path = Path(path)
    if not local_path.is_file():
        raise BeebleMediaError(f"Image file does not exist: {path}")

    try:
        with Image.open(local_path) as image:
            image = image.convert("RGB")
            array = np.asarray(image, dtype=np.float32) / 255.0
    except Exception as exc:
        raise BeebleMediaError(f"Failed to load image file: {exc}") from exc

    return torch.from_numpy(array).unsqueeze(0)


def load_video_file_as_input(path: str):
    """Load a local video file as a ComfyUI VIDEO input."""
    if VideoFromFile is None:
        raise BeebleMediaError("Loading VIDEO from file requires ComfyUI video input support.")

    local_path = Path(path)
    if not local_path.is_file():
        raise BeebleMediaError(f"Video file does not exist: {path}")

    return VideoFromFile(str(local_path))


def download_file(url_or_uri: str, output_path: str) -> str:
    """Download a Beeble result URL to a local file."""
    source = url_or_uri.strip()
    if not source:
        raise BeebleMediaError("url_or_uri is required")

    parsed = parse.urlparse(source)
    if parsed.scheme not in {"http", "https"}:
        raise BeebleMediaError(
            f"Unsupported download source '{source}'. Expected an http(s) URL."
        )

    local_path = Path(output_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(BEEBLE_NETWORK_RETRY_COUNT + 1):
        try:
            with request.urlopen(source, timeout=60.0) as response:
                data = response.read()
            break
        except error.HTTPError as exc:
            raise BeebleMediaError(
                f"Failed to download file: HTTP {exc.code}."
            ) from exc
        except error.URLError as exc:
            if attempt >= BEEBLE_NETWORK_RETRY_COUNT or not should_retry_url_error(exc):
                raise BeebleMediaError(format_network_error_message("Beeble download", exc)) from exc
            LOGGER.warning(
                "Beeble download failed with a temporary network error, retrying (%s/%s).",
                attempt + 1,
                BEEBLE_NETWORK_RETRY_COUNT,
            )
            time.sleep(BEEBLE_NETWORK_RETRY_DELAY)

    try:
        local_path.write_bytes(data)
    except Exception as exc:
        raise BeebleMediaError(f"Failed to write downloaded file: {exc}") from exc

    return str(local_path)


__all__ = [
    "download_file",
    "load_image_file_as_tensor",
    "load_video_file_as_input",
    "save_image_tensor_as_png",
    "save_video_input_to_file",
]
