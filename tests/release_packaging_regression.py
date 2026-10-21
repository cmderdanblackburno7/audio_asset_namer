"""Checks for the existing release checksum/provenance additions (Python 3.11+)."""
from pathlib import Path
import sys
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

    def test_provenance_does_not_require_git_for_source_archive(self):
        with patch.object(build_windows.subprocess, "check_output", side_effect=FileNotFoundError):
            self.assertEqual(build_windows.source_state(), {"commit": None, "dirty": None})


if __name__ == "__main__":
    unittest.main()
