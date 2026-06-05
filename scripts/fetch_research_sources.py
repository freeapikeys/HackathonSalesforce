#!/usr/bin/env python3

"""Download registered research sources into the ignored local archive."""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIR = ROOT / "research" / "mauritius-relationship-management"
REGISTER_PATH = RESEARCH_DIR / "source-register.json"
DOWNLOAD_DIR = RESEARCH_DIR / "_downloads"
CHECKSUM_PATH = RESEARCH_DIR / "download-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "HackathonSalesforce research archive/1.0"},
    )
    partial = destination.with_name(f"{destination.name}.part")
    downloaded = partial.stat().st_size if partial.exists() else 0
    headers = {}
    if downloaded:
        headers["Range"] = f"bytes={downloaded}-"
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "HackathonSalesforce research archive/1.0",
                **headers,
            },
        )

    with urllib.request.urlopen(request, timeout=90) as response:
        supports_resume = response.status == 206
        mode = "ab" if downloaded and supports_resume else "wb"
        if mode == "wb":
            downloaded = 0

        next_report = downloaded + 10 * 1024 * 1024
        with partial.open(mode) as destination_file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                destination_file.write(chunk)
                downloaded += len(chunk)
                if downloaded >= next_report:
                    print(
                        f"  {destination.name}: {downloaded / (1024 * 1024):.1f} MiB",
                        flush=True,
                    )
                    next_report += 10 * 1024 * 1024

    partial.replace(destination)


def main() -> int:
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    failures = 0

    for source in register["sources"]:
        destination = DOWNLOAD_DIR / source["local_filename"]
        status = "existing"

        if source.get("download", True) is False:
            status = "link-only"
        elif not destination.exists() or destination.stat().st_size == 0:
            print(f"{source['id']}: downloading", flush=True)
            for attempt in range(1, 3):
                try:
                    download(source["url"], destination)
                    status = "downloaded"
                    break
                except (urllib.error.URLError, TimeoutError, OSError) as error:
                    status = f"failed: {error}"
                    if attempt < 2:
                        print(
                            f"  retrying after attempt {attempt}: {error}",
                            flush=True,
                        )
                        time.sleep(2)
            else:
                failures += 1

        result = {
            "id": source["id"],
            "filename": source["local_filename"],
            "status": status,
        }
        if destination.exists() and destination.stat().st_size > 0:
            result["bytes"] = destination.stat().st_size
            result["sha256"] = sha256(destination)

        results.append(result)
        print(f"{source['id']}: {status}", flush=True)

    CHECKSUM_PATH.write_text(
        json.dumps({"sources": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Checksums: {CHECKSUM_PATH}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
