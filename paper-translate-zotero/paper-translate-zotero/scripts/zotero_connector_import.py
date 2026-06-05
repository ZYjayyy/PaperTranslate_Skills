#!/usr/bin/env python3
"""Import generated files into Zotero through the local Connector server."""

from __future__ import annotations

import argparse
import json
import mimetypes
import socket
import urllib.error
import urllib.request
import uuid
from pathlib import Path


DEFAULT_BASE_URL = "http://127.0.0.1:23119"


def post(base_url: str, path: str, data: bytes, headers: dict[str, str], timeout: int = 180) -> tuple[int | str, str]:
    req = urllib.request.Request(base_url + path, data=data, method="POST")
    for key, value in headers.items():
        req.add_header(key, value)
    req.add_header("X-Zotero-Connector-API-Version", "3")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except (TimeoutError, socket.timeout) as exc:
        return "timeout", str(exc)


def import_file(base_url: str, file_path: Path, title: str) -> dict:
    data = file_path.read_bytes()
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    metadata = {
        "sessionID": "codex-paper-translate-" + uuid.uuid4().hex,
        "title": title,
        "url": file_path.resolve().as_uri(),
    }
    status, body = post(
        base_url,
        "/connector/saveStandaloneAttachment",
        data,
        {
            "Content-Type": content_type,
            "Content-Length": str(len(data)),
            "X-Metadata": json.dumps(metadata, ensure_ascii=True),
        },
    )
    return {"title": title, "file": str(file_path.resolve()), "status": status, "body": body}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Files to import")
    parser.add_argument("--title-prefix", default="中文全文翻译PDF - ")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    results = []
    for file_name in args.files:
        file_path = Path(file_name).expanduser().resolve()
        title = args.title_prefix + file_path.stem
        results.append(import_file(args.base_url, file_path, title))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
