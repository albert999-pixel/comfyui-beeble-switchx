"""ComfyUI node wrappers for Beeble SwitchX."""

from .test_account_info import BeebleAccountInfoTestNode
from .test_download_image import BeebleDownloadImageTestNode
from .test_download_video import BeebleDownloadVideoTestNode
from .test_dummy import BeebleDummyTestNode
from .test_export_mask import BeebleExportMaskTestNode
from .test_poll_job import BeeblePollJobTestNode
from .test_start_image_generation import BeebleStartImageGenerationTestNode
from .test_start_video_generation import BeebleStartVideoGenerationTestNode
from .test_upload_image import BeebleUploadImageTestNode
from .test_upload_video import BeebleUploadVideoTestNode
from .test_wait_job import BeebleWaitJobTestNode
from .switchx_image import BeebleSwitchXImageNode
from .switchx_video import BeebleSwitchXVideoNode


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
