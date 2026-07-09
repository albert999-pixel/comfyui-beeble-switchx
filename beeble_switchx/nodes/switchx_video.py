"""Production Beeble SwitchX video node."""

from __future__ import annotations

from ..flows import run_switchx_video


class BeebleSwitchXVideoNode:
    CATEGORY = "Beeble/SwitchX/Video"
    FUNCTION = "run"
    RETURN_TYPES = ("VIDEO", "VIDEO")
    RETURN_NAMES = ("video", "alpha_video")
    SEARCH_ALIASES = ["beeble video", "switchx video", "beeble switchx video"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO", {"tooltip": "Source video to send to Beeble SwitchX."}),
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
                        "tooltip": "auto: detect subject automatically. fill: keep the scene. select: single-frame mask. custom: full alpha video.",
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
                "alpha_keyframe_index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "tooltip": "[select only] Frame index for the reference mask. 0 means the first frame.",
                    },
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
                "alpha_keyframe_mask": (
                    "MASK",
                    {"tooltip": "[select only] Single reference-frame mask propagated through the whole video."},
                ),
                "alpha_video": (
                    "VIDEO",
                    {"tooltip": "[custom only] Full frame-by-frame alpha video."},
                ),
            },
        }

    def run(
        self,
        video,
        alpha_mode,
        prompt,
        seed,
        max_resolution,
        alpha_keyframe_index,
        timeout_seconds,
        poll_interval_seconds,
        alpha_keyframe_mask=None,
        alpha_video=None,
        reference_image=None,
    ):
        result = run_switchx_video(
            video=video,
            alpha_mode=alpha_mode,
            prompt=prompt,
            seed=seed,
            max_resolution=max_resolution,
            reference_image=reference_image,
            alpha_keyframe_mask=alpha_keyframe_mask,
            alpha_video=alpha_video,
            alpha_keyframe_index=alpha_keyframe_index,
            timeout=float(timeout_seconds),
            poll_interval=float(poll_interval_seconds),
        )
        return (result["video"], result["alpha_video"])
