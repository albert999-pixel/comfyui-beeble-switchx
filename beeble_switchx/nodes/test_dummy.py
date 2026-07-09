"""Minimal test node to verify ComfyUI registration."""


class BeebleDummyTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Beeble SwitchX is loaded"}),
            }
        }

    def run(self, text):
        return (text,)
