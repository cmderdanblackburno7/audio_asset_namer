"""Repeated exports, collisions, failure recovery and UI cancellation tests."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from audio_asset_namer_regression import test_directory
import core
import exporting

GUI = "--gui-smoke" in sys.argv
if GUI:
    sys.argv.remove("--gui-smoke")


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = test_directory()
        self.parent = self.temp.__enter__()
        self.addCleanup(self.temp.__exit__, None, None, None)
        self.folder = self.parent / "Session"
        self.folder.mkdir()
        self.script = self.parent / "script.txt"
        self.script.write_text("Relax your shoulders. [pause] Rest.\n\nBreathe slowly.", encoding="utf-8")
        for i in (1, 2):
            (self.folder / f"{i:02}.Audio.mp3").write_bytes(bytes(range(256)) + bytes([i]))
        self.plan = core.load_plan(self.folder, self.script)
        self.output = self.folder / "Named"
        self.inputs = {p: p.read_bytes() for p in [self.script] + [c.source for c in self.plan.clips]}

    def seed(self):
        self.assertTrue(all(ok for _, ok, _ in core.export_plan(self.plan)))
        self.old = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.old_names = [core.filename(c) for c in self.plan.clips]
        return self.old

    def unchanged(self):
        for name, data in self.old.items():
            self.assertEqual((self.output / name).read_bytes(), data, name)
        for path, data in self.inputs.items():
            self.assertEqual(path.read_bytes(), data)

    def rename(self):
        for c, title in zip(self.plan.clips, ("Updated One", "Updated Two")):
            c.title = title

    def test_repeated_export_updates_titles_keeps_unrelated_and_backups(self):
        self.seed()
        (self.output / "unrelated.txt").write_bytes(b"leave this")
        (self.output / "notes").mkdir()
        (self.output / "notes/keep.txt").write_bytes(b"nested")
        self.rename()
        results = core.export_plan(self.plan, replace=True)
        self.assertTrue(all(ok for _, ok, _ in results), results)
        for c in self.plan.clips:
            self.assertEqual((self.output / core.filename(c)).read_bytes(), self.inputs[c.source])
        self.assertTrue(all(not (self.output / n).exists() for n in self.old_names))
        self.assertEqual((self.output / "unrelated.txt").read_bytes(), b"leave this")
        self.assertEqual((self.output / "notes/keep.txt").read_bytes(), b"nested")
        backup = next(self.output.glob(exporting.BACKUP + "*"))
        for n, b in self.old.items():
            self.assertEqual((backup / "previous" / n).read_bytes(), b)
        self.assertEqual(json.loads((backup / "transaction.json").read_text())["phase"], "complete")
        self.assertFalse((self.output / exporting.LOCK).exists())
        self.assertTrue(all(ok for _, ok, _ in core.export_plan(self.plan, replace=True)))
        for p, b in self.inputs.items():
            self.assertEqual(p.read_bytes(), b)

    def test_alternative_existing_folder_keeps_unrelated_files(self):
        self.seed()
        other = self.parent / "Other"
        other.mkdir()
        (other / "notes.txt").write_bytes(b"notes")
        self.assertTrue(all(ok for _, ok, _ in core.export_plan(self.plan, destination=other)))
        self.unchanged()
        self.assertEqual((other / "notes.txt").read_bytes(), b"notes")
        self.assertEqual((other / core.filename(self.plan.clips[0])).read_bytes(), self.inputs[self.plan.clips[0].source])

    def test_alternative_case_insensitive_collision_refused_without_writes(self):
        other = self.parent / "Other"
        other.mkdir()
        name = core.filename(self.plan.clips[0]).upper()
        (other / name).write_bytes(b"unrelated")
        with self.assertRaisesRegex(core.ValidationError, "already exists"):
            core.export_plan(self.plan, destination=other)
        self.assertEqual({p.name for p in other.iterdir()}, {name})
        self.assertEqual((other / name).read_bytes(), b"unrelated")

    def test_empty_named_can_be_used_after_explicit_replacement_choice(self):
        self.output.mkdir()
        self.assertTrue(all(ok for _, ok, _ in core.export_plan(self.plan, replace=True)))

    def test_replacement_without_manifest_cannot_claim_colliding_audio(self):
        self.output.mkdir()
        target = self.output / core.filename(self.plan.clips[0])
        target.write_bytes(b"not ours")
        with self.assertRaisesRegex(core.ValidationError, "not a recognised export"):
            core.export_plan(self.plan, replace=True)
        self.assertEqual(target.read_bytes(), b"not ours")
        self.assertEqual(len(list(self.output.iterdir())), 1)

    def test_foreign_or_malformed_manifest_refuses_before_writes(self):
        self.seed()
        manifest = self.output / "manifest.csv"
        for data in (b"other,file\nnot,ours", b"\xff", self.old["manifest.csv"].replace(b"Relax your shoulders", b"Different script")):
            with self.subTest(data=data[:16]):
                manifest.write_bytes(data)
                with self.assertRaises(core.ValidationError):
                    core.export_plan(self.plan, replace=True)
                self.assertEqual(manifest.read_bytes(), data)
                self.assertFalse(list(self.output.glob(exporting.BACKUP + "*")))

    def test_duplicate_previous_manifest_rows_refuse(self):
        self.seed()
        manifest = self.output / "manifest.csv"
        with manifest.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        with manifest.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=core.FIELDS)
            writer.writeheader()
            writer.writerows(rows + rows[:1])
        before = manifest.read_bytes()
        with self.assertRaises(core.ValidationError):
            core.export_plan(self.plan, replace=True)
        self.assertEqual(manifest.read_bytes(), before)

    def test_modified_previous_audio_is_not_overwritten(self):
        self.seed()
        old = self.output / self.old_names[0]
        old.write_bytes(b"modified by user")
        self.old[old.name] = old.read_bytes()
        self.rename()
        results = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in results))
        self.assertIn("no longer matches", results[0][2])
        self.unchanged()

    def test_swapped_owned_titles_are_safe(self):
        self.seed()
        self.plan.clips[0].title, self.plan.clips[1].title = self.plan.clips[1].title, self.plan.clips[0].title
        self.assertTrue(all(ok for _, ok, _ in core.export_plan(self.plan, replace=True)))
        for c in self.plan.clips:
            self.assertEqual((self.output / core.filename(c)).read_bytes(), self.inputs[c.source])

    def test_stage_failure_leaves_previous_exports_byte_identical(self):
        self.seed()
        self.rename()
        with patch.object(exporting, "durable_copy", side_effect=OSError("disk full")):
            result = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in result))
        self.unchanged()

    def test_backup_failure_leaves_previous_exports_byte_identical(self):
        self.seed()
        self.rename()
        real = exporting.durable_copy
        def fail(source, target):
            if target.parent.name == "previous":
                raise OSError("backup write failed")
            return real(source, target)
        with patch.object(exporting, "durable_copy", side_effect=fail):
            result = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in result))
        self.unchanged()

    def test_locked_previous_file_rolls_back_earlier_moves(self):
        self.seed()
        self.rename()
        real = exporting.os.rename
        def fail(source, target):
            if Path(source).parent == self.output and Path(source).name == self.old_names[1]:
                raise PermissionError("file is open")
            return real(source, target)
        with patch.object(exporting.os, "rename", side_effect=fail):
            result = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in result))
        self.unchanged()

    @unittest.skipUnless(sys.platform == "win32", "Native Windows sharing check")
    def test_real_windows_file_lock_preserves_previous_exports(self):
        import ctypes
        from ctypes import wintypes
        self.seed()
        self.rename()
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        open_file = kernel.CreateFileW
        open_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                              wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        open_file.restype = wintypes.HANDLE
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        handle = open_file(str(self.output / self.old_names[1]), 0x80000000, 1, None, 3, 0, None)
        self.assertNotEqual(handle, wintypes.HANDLE(-1).value)
        try:
            result = core.export_plan(self.plan, replace=True)
        finally:
            close(handle)
        self.assertFalse(any(ok for _, ok, _ in result))
        self.unchanged()

    def test_publication_failure_restores_complete_old_set_and_manifest(self):
        self.seed()
        self.rename()
        real = exporting.os.link
        def fail(source, target):
            if Path(target) == self.output / "Updated Two.mp3":
                raise OSError("simulated publication failure")
            return real(source, target)
        with patch.object(exporting.os, "link", side_effect=fail):
            result = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in result))
        self.assertFalse((self.output / "Updated One.mp3").exists())
        self.unchanged()

    def test_external_publication_collision_is_never_overwritten(self):
        self.seed()
        self.rename()
        real = exporting.os.link
        intruder = self.output / "Updated One.mp3"
        def collide(source, target):
            if Path(target) == intruder:
                intruder.write_bytes(b"concurrent unrelated file")
            return real(source, target)
        with patch.object(exporting.os, "link", side_effect=collide):
            result = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in result))
        self.assertEqual(intruder.read_bytes(), b"concurrent unrelated file")
        self.unchanged()

    def test_rollback_failure_keeps_verified_recovery_and_blocks_retry(self):
        self.seed()
        self.rename()
        real = exporting.os.link
        def fail(source, target):
            if Path(target) in (self.output / "Updated Two.mp3", self.output / self.old_names[0]):
                raise PermissionError("file locked")
            return real(source, target)
        with patch.object(exporting.os, "link", side_effect=fail):
            result = core.export_plan(self.plan, replace=True)
        self.assertIn("could not be restored", result[0][2])
        pending = next(self.output.glob(exporting.PENDING + "*"))
        for name, data in self.old.items():
            self.assertEqual((pending / "previous" / name).read_bytes(), data)
        self.assertTrue(json.loads((pending / "transaction.json").read_text())["backups_verified"])
        with self.assertRaisesRegex(core.ValidationError, "recovery"):
            exporting.prepare_export(self.plan, replace=True)

    def test_process_interruption_preserves_recovery_copies(self):
        self.seed()
        code = '''import os,sys
from pathlib import Path
from unittest.mock import patch
import core,exporting
plan=core.load_plan(sys.argv[1],sys.argv[2])
for c,title in zip(plan.clips,('Updated One','Updated Two')): c.title=title
real=exporting.os.link
def interrupt(source,target):
    if Path(target).parent==plan.folder/'Named': os._exit(71)
    return real(source,target)
with patch.object(exporting.os,'link',side_effect=interrupt): core.export_plan(plan,replace=True)
'''
        child = subprocess.run([sys.executable, "-c", code, str(self.folder), str(self.script)], cwd=TOOL, capture_output=True, text=True)
        self.assertEqual(child.returncode, 71, child.stderr)
        pending = next(self.output.glob(exporting.PENDING + "*"))
        self.assertTrue(json.loads((pending / "transaction.json").read_text())["backups_verified"])
        for name, data in self.old.items():
            self.assertEqual((pending / "previous" / name).read_bytes(), data)
        with self.assertRaisesRegex(core.ValidationError, "recovery"):
            exporting.prepare_export(self.plan, replace=True)
        for path, data in self.inputs.items():
            self.assertEqual(path.read_bytes(), data)

    def test_unsupported_filesystem_refuses_without_changes(self):
        self.seed()
        with patch.object(exporting, "require_local_ntfs", side_effect=core.ValidationError("Choose another folder")):
            with self.assertRaisesRegex(core.ValidationError, "another folder"):
                core.export_plan(self.plan, replace=True)
        self.unchanged()
        self.assertEqual(len(list(self.output.iterdir())), 3)

    def test_linked_previous_file_is_refused(self):
        self.seed()
        os.link(self.output / self.old_names[0], self.parent / "linked.mp3")
        with self.assertRaisesRegex(core.ValidationError, "linked"):
            core.export_plan(self.plan, replace=True)
        self.unchanged()

    def test_unrelated_new_title_collision_refuses(self):
        self.seed()
        self.rename()
        extra = self.output / "UPDATED ONE.MP3"
        extra.write_bytes(b"unrelated")
        with self.assertRaises(core.ValidationError):
            core.export_plan(self.plan, replace=True)
        self.unchanged()
        self.assertEqual(extra.read_bytes(), b"unrelated")

    def test_titles_or_manifest_changed_after_confirmation_refuse(self):
        self.seed()
        request = exporting.prepare_export(self.plan, replace=True)
        self.rename()
        with self.assertRaisesRegex(core.ValidationError, "Titles changed"):
            core.export_plan(self.plan, request=request)
        self.unchanged()
        self.plan = core.load_plan(self.folder, self.script)
        request = exporting.prepare_export(self.plan, replace=True)
        (self.output / "manifest.csv").write_bytes(b"changed")
        with self.assertRaises(core.ValidationError):
            core.export_plan(self.plan, request=request)
        self.assertEqual((self.output / "manifest.csv").read_bytes(), b"changed")

    def test_partial_legacy_manifest_can_be_completed_safely(self):
        real = core.shutil.copyfileobj
        def fail_one(source, target, length):
            if source.name.endswith("01.Audio.mp3"):
                raise OSError("first clip failed")
            real(source, target, length)
        with patch.object(core.shutil, "copyfileobj", side_effect=fail_one):
            self.assertFalse(core.export_plan(self.plan)[0][1])
        self.assertTrue(all(ok for _, ok, _ in core.export_plan(self.plan, replace=True)))
        with (self.output / "manifest.csv").open(encoding="utf-8", newline="") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 2)

    def test_replacement_duplicate_titles_refuse_before_changes(self):
        self.seed()
        self.plan.clips[1].title = self.plan.clips[0].title.upper()
        with self.assertRaisesRegex(core.ValidationError, "duplicate title"):
            core.export_plan(self.plan, replace=True)
        self.unchanged()
        self.assertEqual(len(list(self.output.iterdir())), 3)

    def test_recording_changed_during_staging_leaves_old_exports(self):
        self.seed()
        self.rename()
        real = exporting.durable_copy
        def change(source, target):
            real(source, target)
            if Path(source) == self.plan.clips[0].source:
                source.write_bytes(b"recording edited externally")
        with patch.object(exporting, "durable_copy", side_effect=change):
            results = core.export_plan(self.plan, replace=True)
        self.assertFalse(any(ok for _, ok, _ in results))
        for name, data in self.old.items():
            self.assertEqual((self.output / name).read_bytes(), data)

    def test_original_source_folder_is_never_an_output_destination(self):
        for replace in (False, True):
            with self.assertRaisesRegex(core.ValidationError, "separate output"):
                core.export_plan(self.plan, destination=self.folder, replace=replace)
        for path, data in self.inputs.items():
            self.assertEqual(path.read_bytes(), data)


class UIWorkflowTests(unittest.TestCase):
    setUp = ExportTests.setUp
    seed = ExportTests.seed
    unchanged = ExportTests.unchanged

    def make_ui(self):
        import tkinter as tk
        import app
        root = tk.Tk()
        ui = app.App(root)
        ui.folder.set(str(self.folder))
        ui.script.set(str(self.script))
        ui.load()
        root.update()
        def cleanup():
            for timer in root.tk.call("after", "info"):
                root.after_cancel(timer)
            root.destroy()
        self.addCleanup(cleanup)
        return app, root, ui

    @unittest.skipUnless(GUI, "Requires --gui-smoke and a desktop")
    def test_dialog_cancel_and_picker_cancel_do_not_touch_files(self):
        self.seed()
        app, root, ui = self.make_ui()
        for choice in (None, "choose"):
            with patch.object(ui, "existing_output_choice", return_value=choice), patch.object(app.filedialog, "askdirectory", return_value=""), patch.object(app.threading, "Thread") as thread:
                ui.copy()
                thread.assert_not_called()
            self.unchanged()
            self.assertEqual(len(list(self.output.iterdir())), 3)
            self.assertIn("cancelled", ui.status["text"])

    @unittest.skipUnless(GUI, "Requires --gui-smoke and a desktop")
    def test_replacement_confirmation_cancel_defaults_to_cancel(self):
        self.seed()
        app, root, ui = self.make_ui()
        with patch.object(ui, "existing_output_choice", return_value="replace"), patch.object(app.messagebox, "askokcancel", return_value=False) as confirm, patch.object(app.threading, "Thread") as thread:
            ui.copy()
            self.assertEqual(confirm.call_args.kwargs["default"], "cancel")
            self.assertIn(str(self.output), confirm.call_args.args[1])
            thread.assert_not_called()
        self.unchanged()
        self.assertEqual(len(list(self.output.iterdir())), 3)

    @unittest.skipUnless(GUI, "Requires --gui-smoke and a desktop")
    def test_alternative_folder_is_shown_and_export_can_repeat(self):
        self.seed()
        app, root, ui = self.make_ui()
        other = self.parent / "Other"
        other.mkdir()
        with patch.object(ui, "existing_output_choice", return_value="choose"), patch.object(app.filedialog, "askdirectory", return_value=str(other)), patch.object(app.messagebox, "askokcancel", return_value=True) as confirm:
            ui.copy()
            self.assertIn(str(other), confirm.call_args.args[1])
        deadline = time.monotonic() + 10
        while ui.busy and time.monotonic() < deadline:
            root.update()
            time.sleep(.01)
        self.assertFalse(ui.busy)
        self.assertTrue((other / "manifest.csv").is_file())
        self.assertEqual(str(ui.copy_button["state"]), "normal")
        self.unchanged()

    @unittest.skipUnless(GUI, "Requires --gui-smoke and a desktop")
    def test_real_dialog_enter_defaults_to_choose_another(self):
        self.seed()
        app, root, ui = self.make_ui()
        def enter():
            root.focus_get().event_generate("<Return>")
        root.after(150, enter)
        self.assertEqual(ui.existing_output_choice(self.output), "choose")
        self.unchanged()

    @unittest.skipUnless(GUI, "Requires --gui-smoke and a desktop")
    def test_real_dialog_focus_and_escape_are_non_destructive(self):
        self.seed()
        app, root, ui = self.make_ui()
        checks = []
        def inspect():
            import tkinter as tk
            from tkinter import ttk
            dialog = next(w for w in root.winfo_children() if isinstance(w, tk.Toplevel))
            checks.append(dialog.focus_get()["text"] == "Choose another folder")
            dialog.event_generate("<Escape>")
        root.after(150, inspect)
        self.assertIsNone(ui.existing_output_choice(self.output))
        self.assertEqual(checks, [True])
        self.unchanged()


if __name__ == "__main__":
    unittest.main()
