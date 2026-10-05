#!/usr/bin/env python3
"""Compile, validate, and package the bounded EA prototype. No game files edited."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULES = ("EA_Core", "EA_Dispatch", "EA_Service", "EA_Accounts", "EA_Prototype")
CONFIG = json.loads((ROOT / "content/build-config.json").read_text(encoding="utf-8"))
VERSION = CONFIG["version"]


def validate_compiler(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != CONFIG["compiler"]["executable_sha256"]:
        raise ValueError("Compiler checksum does not match the pinned Caprica v0.3.0 executable")
    return digest


def write_package(files, archive, manifest):
    """Publish only a complete ZIP whose contents match the manifest."""
    names = [name for _, name in files]
    if len(names) != len(set(names)) or "manifest.json" in names:
        raise ValueError("Duplicate package member")
    if set(names) != set(manifest["sha256"]):
        raise ValueError("Every package member must have exactly one manifest hash")
    if any(name.startswith(("/", "\\")) or "\\" in name or ".." in name.split("/") for name in names):
        raise ValueError("Unsafe package member path")
    fd, temp_name = tempfile.mkstemp(prefix=archive.stem + "-", suffix=".tmp", dir=archive.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as package:
            for path, name in files:
                package.write(path, name)
            package.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        with zipfile.ZipFile(temp) as package:
            if package.testzip() is not None:
                raise ValueError("ZIP integrity check failed")
            for name, expected in manifest["sha256"].items():
                if hashlib.sha256(package.read(name)).hexdigest() != expected:
                    raise ValueError("Package hash mismatch: " + name)
        temp.replace(archive)
    finally:
        temp.unlink(missing_ok=True)


def run(command, **kwargs):
    print("+", " ".join(str(x) for x in command), flush=True)
    subprocess.run([str(x) for x in command], cwd=ROOT, check=True, **kwargs)


def wine_path(path):
    return "Z:" + str(Path(path).resolve()).replace("/", "\\")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caprica", type=Path, required=True, help="Caprica v0.3.0 executable")
    parser.add_argument("--wine", type=Path, help="Wine executable on Linux (omit on Windows)")
    parser.add_argument("--wine-prefix", type=Path, help="Dedicated Wine prefix, used only with --wine")
    parser.add_argument("--papyrus-import", type=Path, help="Extracted Skyrim SE Creation Kit script sources; recommended for release validation")
    parser.add_argument("--restore", action="store_true", help="Restore the locked NuGet packages before compiling")
    args = parser.parse_args()
    if not args.caprica.is_file():
        parser.error("The supplied Caprica executable does not exist")
    try:
        compiler_hash = validate_compiler(args.caprica)
    except ValueError as error:
        parser.error(str(error))
    if args.wine_prefix and not args.wine:
        parser.error("--wine-prefix requires --wine")
    if args.wine and not args.wine.is_file():
        parser.error("The supplied Wine executable does not exist")
    if args.papyrus_import:
        if not args.papyrus_import.is_dir():
            parser.error("--papyrus-import must be a directory of extracted Creation Kit sources")
        required = {p.name.lower() for p in (ROOT / "tools/papyrus-api").glob("*.psc")}
        supplied = {p.name.lower() for p in args.papyrus_import.iterdir() if p.is_file()}
        if required - supplied:
            parser.error("Missing Creation Kit base scripts: " + ", ".join(sorted(required - supplied)))
    data = ROOT / "build/Data"
    compiled = data / "Scripts"
    compiled.mkdir(parents=True, exist_ok=True)
    # Only clear this builder's own script artifacts, preventing stale compiler output.
    for path in compiled.glob("EA_*.*"):
        if path.suffix.lower() in (".pex", ".pas"):
            path.unlink()
    imports = args.papyrus_import or ROOT / "tools/papyrus-api"
    convert = wine_path if args.wine else lambda p: str(Path(p).resolve())
    command = [args.caprica.resolve(), "--game", "skyrim", "--ignorecwd", "--all-warnings-as-errors", "--flags", convert(ROOT / "tools/TESV_Papyrus_Flags.flg"), "--import", convert(imports), "--import", convert(ROOT / "Data/Source/Scripts"), "--output", convert(compiled), "--dump-asm", convert(ROOT / "Data/Source/Scripts")]
    env = os.environ.copy()
    if args.wine:
        command.insert(0, args.wine.resolve())
        env["WINEDEBUG"] = "-all"
        if args.wine_prefix:
            args.wine_prefix.mkdir(parents=True, exist_ok=True)
            env["WINEPREFIX"] = str(args.wine_prefix.resolve())
    run(command, env=env)
    for source in (ROOT / "Data/Source/Scripts").glob("EA_*.psc"):
        for suffix in (".pex", ".pas"):
            if not (compiled / (source.stem + suffix)).is_file():
                raise RuntimeError("Compiler did not produce " + source.stem + suffix)
    if args.restore:
        run(["dotnet", "restore", "tools/PluginBuilder", "--locked-mode"])
    run(["dotnet", "run", "--no-restore", "--project", "tools/PluginBuilder", "--", ROOT])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    files = [(data / (name + ".esp"), name + ".esp") for name in MODULES]
    files += [(p, "Scripts/" + p.name) for p in sorted(compiled.glob("EA_*.pex"))]
    files += [(p, "Source/Scripts/" + p.name) for p in sorted((ROOT / "Data/Source/Scripts").glob("EA_*.psc"))]
    files += [(ROOT / "README.md", "README.md")]
    files += [(ROOT / "Elenwen_Agent_Mod_Build_Specification.md", "Elenwen_Agent_Mod_Build_Specification.md")]
    files += [(p, "docs/" + p.name) for p in sorted((ROOT / "docs").glob("*.md"))]
    files += [(ROOT / "build/record-map.json", "docs/record-map.json")]
    manifest = {
        "version": VERSION,
        "status": "technical prototype; not validated in Skyrim",
        "compiler": CONFIG["compiler"]["name"] + ", Skyrim target",
        "compiler_sha256": compiler_hash,
        "api_source": "Creation Kit sources supplied by builder" if args.papyrus_import else "project-authored compile-only API declarations",
        "plugins": [name + ".esp" for name in MODULES],
        "build_inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / "content/build-config.json", ROOT / "content/documents.json", ROOT / "content/record-ids.json", ROOT / "tools/PluginBuilder/Program.cs", ROOT / "tools/PluginBuilder/packages.lock.json"]},
        "sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for path, name in files},
    }
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    archive = dist / f"ElenwenAgent-{VERSION}.zip"
    write_package(files, archive, manifest)
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Built {archive.relative_to(ROOT)} ({archive.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
