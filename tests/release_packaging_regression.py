"""Checks for the existing release checksum/provenance additions (Python 3.11+)."""
from pathlib import Path
import sys
import hashlib
import json
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_windows
from audio_asset_namer_regression import test_directory


class ReleaseChecks(unittest.TestCase):
    def test_final_bytes_match_standalone_checksums(self):
        with test_directory() as folder:
            exe, archive = folder / "App.exe", folder / "App.zip"
            exe.write_bytes(b"final executable bytes")
            archive.write_bytes(b"final archive bytes")
            sums = folder / "SHA256SUMS.txt"
            build_windows.write_checksums((exe, archive), sums)
            self.assertEqual(len([line for line in sums.read_text().splitlines() if line and not line.startswith("#")]), 2)
            build_windows.verify_checksums(sums)
            archive.write_bytes(b"altered after packaging")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                build_windows.verify_checksums(sums)

    def test_checksum_file_cannot_escape_release_directory(self):
        with test_directory() as folder:
            sums = folder / "SHA256SUMS.txt"
            sums.write_text("0" * 64 + "  ../outside.exe\n", encoding="ascii")
            with self.assertRaises(ValueError):
                build_windows.verify_checksums(sums)

    def test_reviewed_runtime_rejects_changed_binary(self):
        with test_directory() as folder:
            (folder / "licenses").mkdir()
            binary = folder / "python313.dll"
            binary.write_bytes(b"reviewed PSF binary")
            review = {"python_version": "3.13.17", "binaries": {binary.name: hashlib.sha256(binary.read_bytes()).hexdigest()}}
            (folder / "licenses/runtime-provenance.json").write_text(json.dumps(review))
            actual = json.dumps({"version": "3.13.17", "base": str(folder)})
            with patch.object(build_windows, "TOOL", folder), patch.object(build_windows.subprocess, "check_output", return_value=actual):
                build_windows.verify_runtime("python.exe")
                binary.write_bytes(b"different native binary")
                with self.assertRaisesRegex(ValueError, "Unreviewed build runtime binary"):
                    build_windows.verify_runtime("python.exe")

    def test_reviewed_runtime_rejects_stale_venv(self):
        actual = json.dumps({"version": "3.12.14", "base": "unused"})
        with patch.object(build_windows.subprocess, "check_output", return_value=actual):
            with self.assertRaisesRegex(ValueError, "Build requires reviewed Python 3.13.17"):
                build_windows.verify_runtime("python.exe")

    def test_provenance_does_not_require_git_for_source_archive(self):
        with patch.object(build_windows.subprocess, "check_output", side_effect=FileNotFoundError):
            self.assertEqual(build_windows.source_state(), {"commit": None, "dirty": None})


if __name__ == "__main__":
    unittest.main()
