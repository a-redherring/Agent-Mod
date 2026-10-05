import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ea_build", ROOT / "tools/build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BuildToolsTests(unittest.TestCase):
    def test_unpinned_compiler_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            compiler = Path(directory) / "Caprica.exe"
            compiler.write_bytes(b"Not the approved compiler")
            with self.assertRaisesRegex(ValueError, "checksum"):
                build.validate_compiler(compiler)

    def test_package_published_only_after_content_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "EA_Test.esp"
            source.write_bytes(b"test payload")
            archive = root / "release.zip"
            files = [(source, source.name)]
            manifest = {"sha256": {source.name: hashlib.sha256(source.read_bytes()).hexdigest()}}
            build.write_package(files, archive, manifest)
            original = archive.read_bytes()
            with zipfile.ZipFile(archive) as package:
                self.assertEqual(package.read(source.name), source.read_bytes())
                self.assertEqual(json.loads(package.read("manifest.json")), manifest)
            source.write_bytes(b"unexpected change after manifest creation")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                build.write_package(files, archive, manifest)
            self.assertEqual(archive.read_bytes(), original)
            self.assertEqual(list(root.glob("*.tmp")), [])

    def test_duplicate_and_unsafe_members_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "file"
            source.write_bytes(b"test")
            for names in (("x", "x"), ("manifest.json",), ("../x",), ("/absolute",), ("Scripts\\x",)):
                with self.subTest(names=names):
                    with self.assertRaises(ValueError):
                        build.write_package([(source, name) for name in names], root / "release.zip", {"sha256": {name: hashlib.sha256(source.read_bytes()).hexdigest() for name in names}})

    def test_package_rejects_unhashed_members(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "EA_Test.esp"
            source.write_bytes(b"test")
            with self.assertRaisesRegex(ValueError, "manifest hash"):
                build.write_package([(source, source.name)], root / "release.zip", {"sha256": {}})
            self.assertFalse((root / "release.zip").exists())
