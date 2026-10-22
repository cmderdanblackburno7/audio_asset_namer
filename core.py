"""Offline audio naming and exclusive byte-copy export. Standard library only."""
from collections import Counter
from dataclasses import dataclass
import csv
from pathlib import Path
import re
import shutil
from titles import suggest_title, suggest_titles

VERSION = "1.3.1"
PREFIX = re.compile(r"^(\d+)(?=[. _-])", re.ASCII)
PAUSE = re.compile(r"\[pause\]", re.IGNORECASE)
UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]')
RESERVED = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", re.I)
FIELDS = ("filename", "title", "category", "full_original_text", "cleaned_spoken_text", "track_number")


class ValidationError(ValueError):
    pass


@dataclass
class Clip:
    number: int
    source: Path
    original: str
    spoken: str
    title: str
    signature: tuple


@dataclass
class Plan:
    folder: Path
    script: Path
    script_bytes: bytes
    clips: list[Clip]
    ignored: list[str]


def signature(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ino


def paragraphs(text):
    # Preserve paragraph contents (including internal line endings and spaces).
    return [part for part in re.split(r"(?:\r?\n)[ \t]*(?:\r?\n)(?:[ \t]*\r?\n)*", text)
            if part.strip()]


def clean_text(text):
    return re.sub(r"\s+", " ", PAUSE.sub(" ", text)).strip()


def safe_title(text):
    text = clean_text(UNSAFE.sub(" ", text)).strip(" .")[:50].rstrip(" .")
    if RESERVED.match(text):
        text = "Spoken " + text
    return text[:50].rstrip(" .")


def numbered_files(folder):
    numbered, ignored = [], []
    for path in folder.iterdir():
        if path.is_file() and path.suffix.lower() == ".mp3":
            match = PREFIX.match(path.name)
            if match:
                numbered.append((int(match[1]), path))
            else:
                ignored.append(path.name)
    return sorted(numbered, key=lambda pair: (pair[0], pair[1].name)), sorted(ignored)


def load_plan(folder, script):
    folder, script = Path(folder).resolve(), Path(script).resolve()
    if not folder.is_dir():
        raise ValidationError("Choose an existing audio folder.")
    raw = script.read_bytes()
    try:
        parts = paragraphs(raw.decode("utf-8-sig"))
    except UnicodeDecodeError as exc:
        raise ValidationError("The script must be UTF-8 text (a UTF-8 BOM is accepted).") from exc
    numbered, ignored = numbered_files(folder)
    counts = Counter(number for number, _ in numbered)
    expected = set(range(1, len(parts) + 1))
    errors = []
    if not parts:
        errors.append("The script has no nonblank paragraphs.")
    if not numbered:
        errors.append("No numbered MP3s found; use prefixes such as 01., 02 - or 03_.")
    if len(numbered) != len(parts):
        errors.append(f"Found {len(numbered)} numbered MP3s and {len(parts)} paragraphs.")
    duplicates = sorted(n for n, count in counts.items() if count > 1)
    missing, unexpected = sorted(expected - counts.keys()), sorted(counts.keys() - expected)
    for label, numbers in (("Duplicate", duplicates), ("Missing", missing), ("Unexpected", unexpected)):
        if numbers:
            errors.append(f"{label} sequence numbers: {', '.join(map(str, numbers))}.")
    if errors:
        raise ValidationError("\n".join(errors) + "\nCorrect the exports/script and load again; no mapping was guessed.")
    clips = []
    for (number, path), original, title in zip(numbered, parts, suggest_titles(parts)):
        title = safe_title(title)
        clips.append(Clip(number, path, original, clean_text(original), title, signature(path)))
    return Plan(folder, script, raw, clips, ignored)


def filename(clip):
    return f"{clip.title}.mp3"


def validate_titles(clips):
    used = set()
    for clip in clips:
        if not clip.title or clip.title != safe_title(clip.title):
            raise ValidationError(f"Paragraph {clip.number}: use a nonempty Windows-safe title of at most 50 characters, without [pause].")
        if clip.title.casefold() in used:
            raise ValidationError(f"Paragraph {clip.number}: duplicate title '{clip.title}'. Edit it before copying.")
        used.add(clip.title.casefold())


def revalidate_plan(plan):
    """Check the original preview again before preparing or publishing output."""
    validate_titles(plan.clips)
    current = load_plan(plan.folder, plan.script)
    if (current.script_bytes != plan.script_bytes or
            [(c.number, c.source, c.signature) for c in current.clips] !=
            [(c.number, c.source, c.signature) for c in plan.clips]):
        raise ValidationError("Inputs changed since preview. Load and review them again.")


def export_plan(plan, report=lambda name, ok, detail: None, *, destination=None, replace=False, request=None):
    from exporting import export_prepared, prepare_export
    return export_prepared(plan, request or prepare_export(plan, destination, replace=replace), report)


def copy_exports(plan, destination, report):
    """Existing exclusive-copy/partial-success behaviour for non-replacement exports."""
    rows, results = [], []
    for clip in plan.clips:
        name = filename(clip)
        target = destination / name
        created = False
        try:
            with clip.source.open("rb") as source, target.open("xb") as output:
                created = True
                shutil.copyfileobj(source, output, length=1024 * 1024)
            if signature(clip.source) != clip.signature:
                raise OSError("Source changed while copying; load again.")
            rows.append(dict(zip(FIELDS, (name, clip.title, plan.folder.name, clip.original, clip.spoken, clip.number))))
            result = (name, True, "Copied original bytes")
        except OSError as exc:
            detail = str(exc)
            if created:
                try:
                    target.unlink()
                except OSError as cleanup_error:
                    detail += f"; incomplete output could not be removed: {cleanup_error}"
            result = (name, False, detail)
        results.append(result)
        report(*result)
    try:
        with (destination / "manifest.csv").open("x", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        result = ("manifest.csv", True, f"Recorded {len(rows)} successful copies")
    except OSError as exc:
        result = ("manifest.csv", False, str(exc))
    results.append(result)
    report(*result)
    return results
