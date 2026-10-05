#!/usr/bin/env python3
"""Download the pinned upstream compiler archive; verify before extraction."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

DEST = Path(__file__).resolve().parents[1] / ".tools"
CONFIG = json.loads((DEST.parent / "content/build-config.json").read_text(encoding="utf-8"))["compiler"]
URL = CONFIG["url"]
SHA256 = CONFIG["archive_sha256"]


def main():
    DEST.mkdir(exist_ok=True)
    archive = DEST / "Caprica.v0.3.0.7z"
    with urllib.request.urlopen(URL, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise SystemExit("Compiler archive checksum mismatch; refusing to extract")
    archive.write_bytes(data)
    subprocess.run(["7z", "x", "-y", str(archive), "-o" + str(DEST / "caprica")], check=True)
    compiler = DEST / "caprica/Caprica.exe"
    if hashlib.sha256(compiler.read_bytes()).hexdigest() != CONFIG["executable_sha256"]:
        raise SystemExit("Extracted compiler executable checksum mismatch")
    print("Compiler:", compiler)


if __name__ == "__main__":
    main()
