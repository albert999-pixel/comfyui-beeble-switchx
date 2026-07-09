"""Production Beeble SwitchX image node."""

from __future__ import annotations

from ..flows import run_switchx_image


class BeebleSwitchXImageNode:
    CATEGORY = "Beeble/SwitchX/Image"
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "alpha")
    SEARCH_ALIASES = ["beeble image", "switchx image", "beeble switchx image"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Source image to send to Beeble SwitchX."}),
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": True,
                        "tooltip": "Main edit prompt. Provide this or connect reference_image.",
                    },
                ),
                "alpha_mode": (
                    ["auto", "fill", "select", "custom"],
                    {
                        "default": "auto",
                        "tooltip": "auto: detect subject automatically. fill: keep the original scene. select/custom: use the mask input.",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "control_after_generate": True,
                        "tooltip": "Seed for Beeble generation. Change it to vary the result.",
                    },
                ),
                "max_resolution": (
                    [720, 1080],
                    {"default": 720, "tooltip": "Maximum output resolution sent to Beeble."},
                ),
                "timeout_seconds": (
                    "INT",
                    {
                        "default": 600,
                        "min": 1,
                        "advanced": True,
                        "tooltip": "Maximum time to wait for the Beeble job before failing.",
                    },
                ),
                "poll_interval_seconds": (
                    "FLOAT",
                    {
                        "default": 2.0,
                        "min": 0.1,
                        "step": 0.1,
                        "advanced": True,
                        "tooltip": "How often to poll Beeble for job status.",
                    },
                ),
            },
            "optional": {
                "reference_image": (
                    "IMAGE",
                    {"tooltip": "Optional reference image. Use this or write a prompt."},
                ),
                "mask": (
                    "MASK",
                    {"tooltip": "[select/custom only] Mask sent to Beeble as alpha input."},
                ),
            },
        }

    def run(
        self,
        image,
        alpha_mode,
        prompt,
        seed,
        max_resolution,
        timeout_seconds,
        poll_interval_seconds,
        mask=None,
        reference_image=None,
    ):
        result = run_switchx_image(
            image=image,
            alpha_mode=alpha_mode,
            prompt=prompt,
            seed=seed,
            max_resolution=max_resolution,
            mask=mask,
            reference_image=reference_image,
            timeout=float(timeout_seconds),
            poll_interval=float(poll_interval_seconds),
        )
        return (result["image"], result["alpha"])
