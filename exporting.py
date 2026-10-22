"""Output selection and recoverable replacement. Never imported by the build helper."""
from contextlib import contextmanager
from dataclasses import dataclass
import csv
import ctypes
from ctypes import wintypes
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import uuid

import core

LOCK = ".audio-namer-export.lock"
PENDING = ".audio-namer-transaction-"
BACKUP = ".audio-namer-backup-"


@dataclass(frozen=True)
class ExportRequest:
    destination: Path
    replace: bool
    create: bool
    names: tuple
    # Existing entries, including manifest.csv, are the only files we may retire.
    previous: tuple
    manifest_bytes: bytes | None


def exists(path):
    return os.path.lexists(path)


def digest(path):
    with path.open("rb") as stream:
        value = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
        return value.hexdigest()


def regular_file(path):
    value = path.lstat()
    if (not stat.S_ISREG(value.st_mode) or value.st_nlink != 1 or
            getattr(value, "st_file_attributes", 0) & 0x400):
        raise core.ValidationError(f"Cannot safely replace linked or special files: {path.name}. Choose another folder.")


def entries(folder):
    result = {}
    for path in folder.iterdir():
        key = path.name.casefold()
        if key in result:
            raise core.ValidationError("This output folder contains names that differ only by letter case. Choose another folder.")
        result[key] = path
    return result


def check_folder(folder):
    if not folder.is_dir() or getattr(folder.lstat(), "st_file_attributes", 0) & 0x400 or folder.is_symlink():
        raise core.ValidationError("Choose a normal output folder, rather than a file or folder link.")
    pending = [p for p in folder.iterdir() if p.name.startswith(PENDING)]
    if pending:
        raise core.ValidationError(f"A replacement is running or did not finish. Keep its recovery files at:\n{pending[0]}\nChoose another folder or follow the recovery instructions in the README.")
    if exists(folder / LOCK):
        raise core.ValidationError(f"Another export may be running, or an earlier export was interrupted. Choose another folder. Keep any recovery files and inspect this lock only after the app has closed:\n{folder / LOCK}")


def require_local_ntfs(folder):
    """Replacement relies on local NTFS hard links and same-volume atomic renames."""
    message = "Safe replacement needs a local Windows NTFS drive. Choose another output folder instead."
    if sys.platform != "win32":
        raise core.ValidationError(message)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    mount = ctypes.create_unicode_buffer(32768)
    get_mount = kernel.GetVolumePathNameW
    get_mount.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    get_mount.restype = wintypes.BOOL
    drive_type = kernel.GetDriveTypeW
    drive_type.argtypes = [wintypes.LPCWSTR]
    drive_type.restype = wintypes.UINT
    volume_info = kernel.GetVolumeInformationW
    volume_info.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD,
                            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                            wintypes.LPWSTR, wintypes.DWORD]
    volume_info.restype = wintypes.BOOL
    fs = ctypes.create_unicode_buffer(64)
    if (not get_mount(str(folder), mount, len(mount)) or drive_type(mount.value) != 3 or
            not volume_info(mount.value, None, 0, None, None, None, fs, len(fs)) or fs.value != "NTFS"):
        raise core.ValidationError(message)


def previous_exports(plan, folder, found):
    manifest = found.get("manifest.csv")
    if manifest is None:
        return (), None
    regular_file(manifest)
    raw = manifest.read_bytes()
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
        if reader.fieldnames != list(core.FIELDS):
            raise ValueError("different manifest format")
        clips = {str(c.number): c for c in plan.clips}
        seen_numbers, seen_names, owned = set(), set(), []
        for row in reader:
            clip = clips.get(row.get("track_number"))
            title, name = row.get("title", ""), row.get("filename", "")
            if (set(row) != set(core.FIELDS) or clip is None or clip.number in seen_numbers or
                    not title or title != core.safe_title(title) or name != title + ".mp3" or
                    name.casefold() in seen_names or row["category"] != plan.folder.name or
                    row["full_original_text"] != clip.original or row["cleaned_spoken_text"] != clip.spoken):
                raise ValueError("different session or ambiguous file ownership")
            seen_numbers.add(clip.number)
            seen_names.add(name.casefold())
            old = found.get(name.casefold())
            if old is not None:
                regular_file(old)
                owned.append((old.name, core.signature(old), clip.number))
        if not seen_numbers:
            raise ValueError("empty manifest")
        owned.append((manifest.name, core.signature(manifest), None))
        return tuple(owned), raw
    except core.ValidationError:
        raise
    except (UnicodeError, csv.Error, ValueError, TypeError) as exc:
        raise core.ValidationError("This manifest does not identify exports from the current script and recordings. Choose another folder; existing files were not changed.") from exc


def prepare_export(plan, destination=None, *, replace=False):
    """Read-only preflight. Confirmation/cancellation must not create any files."""
    core.revalidate_plan(plan)
    default = destination is None
    folder = Path(os.path.abspath(destination if destination is not None else plan.folder / "Named"))
    if folder.resolve() == plan.folder.resolve():
        raise core.ValidationError("Choose a separate output folder so the original recordings stay separate.")
    names = tuple(core.filename(c) for c in plan.clips) + ("manifest.csv",)
    create = not exists(folder)
    if create:
        if not folder.parent.is_dir():
            raise core.ValidationError("Choose an output folder whose parent already exists.")
        return ExportRequest(folder, False, True, names, (), None)
    check_folder(folder)
    if default and not replace:
        raise core.ValidationError("Named already exists. Choose another folder, replace the recognised exports, or cancel.")
    found = entries(folder)
    previous, raw = previous_exports(plan, folder, found) if replace else ((), None)
    allowed = {name.casefold() for name, _, _ in previous}
    for name in names:
        if name.casefold() in found and name.casefold() not in allowed:
            raise core.ValidationError(f"{name} already exists and is not a recognised export from this session. Choose another folder or edit the title; nothing was overwritten.")
    protected = [plan.script] + [c.source for c in plan.clips]
    for name in names + tuple(p[0] for p in previous):
        path = folder / name
        if path.resolve() in protected or (path.exists() and any(os.path.samefile(path, p) for p in protected)):
            raise core.ValidationError("The output would affect an original recording or script. Choose another folder.")
    if replace:
        require_local_ntfs(folder)
    return ExportRequest(folder, replace, False, names, previous, raw)


@contextmanager
def folder_lock(folder):
    token = uuid.uuid4().hex
    path = folder / LOCK
    try:
        stream = path.open("x", encoding="ascii")
    except FileExistsError as exc:
        raise core.ValidationError("Another export is using this folder. Choose another folder or try again after it finishes.") from exc
    try:
        with stream:
            stream.write(token)
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        # Never remove a lock which has been replaced by someone else.
        try:
            if path.is_file() and not path.is_symlink() and path.read_text(encoding="ascii") == token:
                path.unlink()
        except (OSError, UnicodeError):
            pass  # Keep an inaccessible/changed lock rather than delete unknown data.


def check_unchanged(request):
    folder = request.destination
    found = entries(folder)
    owned = {name.casefold(): sig for name, sig, _ in request.previous}
    for name, sig, _ in request.previous:
        path = found.get(name.casefold())
        if path is None or path.name != name or core.signature(path) != sig:
            raise core.ValidationError("Previous exports changed since confirmation. Review the destination again.")
        regular_file(path)
    manifest = found.get("manifest.csv")
    if request.manifest_bytes is not None and (manifest is None or manifest.read_bytes() != request.manifest_bytes):
        raise core.ValidationError("The previous manifest changed. Review the destination again.")
    for name in request.names:
        if name.casefold() in found and name.casefold() not in owned:
            raise core.ValidationError(f"A file appeared in the output folder: {name}. Nothing will be overwritten.")


def durable_copy(source, target):
    with source.open("rb") as reader, target.open("xb") as writer:
        core.shutil.copyfileobj(reader, writer, length=1024 * 1024)
        writer.flush()
        os.fsync(writer.fileno())


def write_journal(work, phase, request, backups_verified=False):
    # A torn journal never loses the durable 'previous' copies. Recovery refuses
    # to guess, and the pending directory itself blocks another replacement.
    value = {"phase": phase, "destination": str(request.destination),
             "previous": [p[0] for p in request.previous], "new": list(request.names),
             "backups_verified": backups_verified}
    with (work / "transaction.json").open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())


def save_backup(work, request, phase, backups_verified=False, scratch=None):
    """Keep previous versions even after success/rollback; never recursively delete."""
    try:
        write_journal(work, phase, request, backups_verified)
        backup = request.destination / (BACKUP + work.name.removeprefix(PENDING))
        os.rename(work, backup)
    except OSError:
        return work  # Preserve every recovery file if archiving the backup fails.
    for relative, expected in (scratch or {}).items():
        path = backup / relative
        try:
            if path.is_file() and not path.is_symlink() and core.signature(path) == expected:
                path.unlink()  # Only our identified scratch files, never arbitrary directory contents.
        except OSError:
            pass
    for name in ("new", "retired"):
        try:
            (backup / name).rmdir()  # Only remove our own empty scratch directories.
        except OSError:
            pass
    return backup


def replace_exports(plan, request):
    folder = request.destination
    work = folder / (PENDING + uuid.uuid4().hex)
    work.mkdir()
    for name in ("new", "previous", "retired"):
        (work / name).mkdir()
    retired, published = [], []
    scratch = {}
    backups_verified = False
    try:
        write_journal(work, "preparing", request)
        staged_hashes = {}
        for clip in plan.clips:
            target = work / "new" / core.filename(clip)
            durable_copy(clip.source, target)
            scratch["new/" + target.name] = core.signature(target)
            staged_hashes[clip.number] = digest(target)
            if digest(clip.source) != staged_hashes[clip.number] or core.signature(clip.source) != clip.signature:
                raise core.ValidationError("A recording changed while preparing the export. Load the preview again.")
        with (work / "new" / "manifest.csv").open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=core.FIELDS)
            writer.writeheader()
            for c in plan.clips:
                writer.writerow(dict(zip(core.FIELDS, (core.filename(c), c.title, plan.folder.name, c.original, c.spoken, c.number))))
            stream.flush()
            os.fsync(stream.fileno())
        scratch["new/manifest.csv"] = core.signature(work / "new/manifest.csv")
        core.revalidate_plan(plan)
        check_unchanged(request)
        for name, _, number in request.previous:
            source = folder / name
            if number is not None and digest(source) != staged_hashes[number]:
                raise core.ValidationError(f"{name} no longer matches the original recording. Choose another folder; previous exports are retained.")
            durable_copy(source, work / "previous" / name)
            if digest(source) != digest(work / "previous" / name):
                raise OSError("Could not verify the recovery copy. Previous exports were not replaced.")
        check_unchanged(request)
        # Prove no-clobber links work before moving any previous export.
        os.link(work / "new" / request.names[0], work / "link-check")
        (work / "link-check").unlink()
        backups_verified = True
        write_journal(work, "backups_ready", request, True)
        # Move only manifest-owned files, after ALL new/backup data was flushed.
        for name, _, _ in request.previous:
            os.rename(folder / name, work / "retired" / name)
            retired.append(name)
            scratch["retired/" + name] = core.signature(work / "retired" / name)
        for name in request.names:
            # Atomic no-clobber publication, including after an external collision.
            os.link(work / "new" / name, folder / name)
            published.append(name)
        backup = save_backup(work, request, "complete", True, scratch)
        return [(name, True, (f"Recorded {len(plan.clips)} successful copies" if name == "manifest.csv" else "Copied original bytes") +
                 f"; previous exports saved in {backup}") for name in request.names]
    except Exception as exc:
        restored = True
        for name in reversed(published):
            target = folder / name
            try:
                if os.path.samefile(target, work / "new" / name):
                    target.unlink()
                else:
                    restored = False
            except OSError:
                restored = False
        for name in reversed(retired):
            try:
                os.link(work / "retired" / name, folder / name)
                (work / "retired" / name).unlink()
            except OSError:
                restored = False  # Never overwrite a new/locked/unrelated file.
        backup = save_backup(work, request, "rolled_back", backups_verified, scratch) if restored else work
        detail = (f"Replacement stopped: {exc}. " +
                  ("Previous exports were retained/restored. " if restored else "Some files could not be restored automatically. ") +
                  f"Keep recovery files at: {backup}")
        return [(name, False, detail) for name in request.names]


def export_prepared(plan, request, report):
    core.revalidate_plan(plan)
    if request.names != tuple(core.filename(c) for c in plan.clips) + ("manifest.csv",):
        raise core.ValidationError("Titles changed after confirmation. Review the export again.")
    folder = request.destination
    if request.create:
        try:
            folder.mkdir()
        except FileExistsError as exc:
            raise core.ValidationError("The output folder appeared after confirmation. Choose the destination again.") from exc
    else:
        check_folder(folder)
    if request.replace:
        require_local_ntfs(folder)
    with folder_lock(folder):
        check_unchanged(request)
        results = replace_exports(plan, request) if request.replace else core.copy_exports(plan, folder, report)
    if request.replace:
        for result in results:
            report(*result)
    return results
