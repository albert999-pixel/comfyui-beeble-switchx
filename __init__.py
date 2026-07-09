"""ComfyUI custom nodes for Beeble SwitchX."""

try:
    from .beeble_switchx.runtime import initialize_runtime_dir
    from .beeble_switchx.nodes.test_account_info import BeebleAccountInfoTestNode
    from .beeble_switchx.nodes.test_download_image import BeebleDownloadImageTestNode
    from .beeble_switchx.nodes.test_download_video import BeebleDownloadVideoTestNode
    from .beeble_switchx.nodes.test_dummy import BeebleDummyTestNode
    from .beeble_switchx.nodes.test_export_mask import BeebleExportMaskTestNode
    from .beeble_switchx.nodes.test_poll_job import BeeblePollJobTestNode
    from .beeble_switchx.nodes.test_start_image_generation import BeebleStartImageGenerationTestNode
    from .beeble_switchx.nodes.test_start_video_generation import BeebleStartVideoGenerationTestNode
    from .beeble_switchx.nodes.test_upload_image import BeebleUploadImageTestNode
    from .beeble_switchx.nodes.test_upload_video import BeebleUploadVideoTestNode
    from .beeble_switchx.nodes.test_wait_job import BeebleWaitJobTestNode
    from .beeble_switchx.nodes.switchx_image import BeebleSwitchXImageNode
    from .beeble_switchx.nodes.switchx_video import BeebleSwitchXVideoNode
except ImportError:
    from beeble_switchx.runtime import initialize_runtime_dir
    from beeble_switchx.nodes.test_account_info import BeebleAccountInfoTestNode
    from beeble_switchx.nodes.test_download_image import BeebleDownloadImageTestNode
    from beeble_switchx.nodes.test_download_video import BeebleDownloadVideoTestNode
    from beeble_switchx.nodes.test_dummy import BeebleDummyTestNode
    from beeble_switchx.nodes.test_export_mask import BeebleExportMaskTestNode
    from beeble_switchx.nodes.test_poll_job import BeeblePollJobTestNode
    from beeble_switchx.nodes.test_start_image_generation import BeebleStartImageGenerationTestNode
    from beeble_switchx.nodes.test_start_video_generation import BeebleStartVideoGenerationTestNode
    from beeble_switchx.nodes.test_upload_image import BeebleUploadImageTestNode
    from beeble_switchx.nodes.test_upload_video import BeebleUploadVideoTestNode
    from beeble_switchx.nodes.test_wait_job import BeebleWaitJobTestNode
    from beeble_switchx.nodes.switchx_image import BeebleSwitchXImageNode
    from beeble_switchx.nodes.switchx_video import BeebleSwitchXVideoNode

initialize_runtime_dir()

NODE_CLASS_MAPPINGS = {
    "BeebleAccountInfoTestNode": BeebleAccountInfoTestNode,
    "BeebleDownloadImageTestNode": BeebleDownloadImageTestNode,
    "BeebleDownloadVideoTestNode": BeebleDownloadVideoTestNode,
    "BeebleDummyTestNode": BeebleDummyTestNode,
    "BeebleExportMaskTestNode": BeebleExportMaskTestNode,
    "BeeblePollJobTestNode": BeeblePollJobTestNode,
    "BeebleSwitchXImageNode": BeebleSwitchXImageNode,
    "BeebleSwitchXVideoNode": BeebleSwitchXVideoNode,
    "BeebleStartImageGenerationTestNode": BeebleStartImageGenerationTestNode,
    "BeebleStartVideoGenerationTestNode": BeebleStartVideoGenerationTestNode,
    "BeebleUploadImageTestNode": BeebleUploadImageTestNode,
    "BeebleUploadVideoTestNode": BeebleUploadVideoTestNode,
    "BeebleWaitJobTestNode": BeebleWaitJobTestNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BeebleAccountInfoTestNode": "Beeble Account Info Test",
    "BeebleDownloadImageTestNode": "Beeble Download Image Test",
    "BeebleDownloadVideoTestNode": "Beeble Download Video Test",
    "BeebleDummyTestNode": "Beeble Dummy Test",
    "BeebleExportMaskTestNode": "Beeble Export Mask Test",
    "BeeblePollJobTestNode": "Beeble Poll Job Test",
    "BeebleSwitchXImageNode": "Beeble SwitchX Image",
    "BeebleSwitchXVideoNode": "Beeble SwitchX Video",
    "BeebleStartImageGenerationTestNode": "Beeble Start Image Generation Test",
    "BeebleStartVideoGenerationTestNode": "Beeble Start Video Generation Test",
    "BeebleUploadImageTestNode": "Beeble Upload Image Test",
    "BeebleUploadVideoTestNode": "Beeble Upload Video Test",
    "BeebleWaitJobTestNode": "Beeble Wait Job Test",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
