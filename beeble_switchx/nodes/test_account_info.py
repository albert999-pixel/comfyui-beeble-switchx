"""Test node for checking Beeble account info access."""

from __future__ import annotations

import json
import logging

from ..api import get_account_info, sanitize_account_info

LOGGER = logging.getLogger(__name__)


class BeebleAccountInfoTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_json",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    def run(self):
        payload = get_account_info()
        sanitized = sanitize_account_info(payload)
        status_json = json.dumps(sanitized, indent=2, ensure_ascii=False)
        LOGGER.info("Beeble account info:\n%s", status_json)
        return (status_json,)
