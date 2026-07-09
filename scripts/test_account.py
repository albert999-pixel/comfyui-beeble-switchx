"""Small manual test for the Beeble account info endpoint."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from beeble_switchx.api import get_account_info, sanitize_account_info
from beeble_switchx.errors import BeebleError


def main() -> int:
    try:
        payload = get_account_info()
    except BeebleError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(sanitize_account_info(payload), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
