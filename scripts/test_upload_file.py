"""Small manual test for the Beeble upload flow."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from beeble_switchx.errors import BeebleError
from beeble_switchx.upload import create_upload_url, upload_file, upload_file_to_url


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    temp_path: Path | None = None

    try:
        if argv:
            file_path = Path(argv[0]).expanduser().resolve()
        else:
            with tempfile.NamedTemporaryFile(
                prefix="beeble_upload_test_",
                suffix=".txt",
                delete=False,
            ) as tmp:
                tmp.write(b"beeble upload test\n")
                temp_path = Path(tmp.name)
            file_path = temp_path

        upload_info = create_upload_url(file_path.name)
        upload_file_to_url(str(file_path), upload_info["upload_url"])

        result = {
            "file_path": str(file_path),
            "upload_id": upload_info.get("upload_id"),
            "beeble_uri": upload_info["beeble_uri"],
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))

        beeble_uri = upload_file(str(file_path))
        print(f"upload_file() beeble_uri: {beeble_uri}")
        return 0
    except BeebleError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
