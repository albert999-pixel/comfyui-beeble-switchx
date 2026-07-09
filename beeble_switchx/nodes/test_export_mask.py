"""Test node for exporting and previewing a MASK."""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from ..masks import save_mask_as_grayscale_png
from ..media import load_image_file_as_tensor

LOGGER = logging.getLogger(__name__)


class BeebleExportMaskTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("mask_image", "debug_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "invert": ("BOOLEAN", {"default": False}),
            }
        }

    def run(self, mask, invert):
        temp_path = Path(
            tempfile.NamedTemporaryFile(
                prefix="beeble_mask_export_",
                suffix=".png",
                delete=False,
            ).name
        )

        try:
            save_mask_as_grayscale_png(mask, str(temp_path), invert=invert)
            mask_image = load_image_file_as_tensor(str(temp_path))
            debug_payload = {
                "file_path": str(temp_path),
                "invert": bool(invert),
            }
            debug_json = json.dumps(debug_payload, indent=2, ensure_ascii=False)
            LOGGER.info("Beeble mask export test:\n%s", debug_json)
            return (mask_image, debug_json)
        finally:
            temp_path.unlink(missing_ok=True)
