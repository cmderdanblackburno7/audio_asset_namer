# BinauraWave Audio Asset Namer

A free, offline Windows desktop utility for turning numbered Audacity MP3 exports into descriptive, editable filenames. Pair your clips with a UTF-8 script, review the suggested titles, and copy the named audio into your output folder with a CSV manifest.

**Current source version: 1.3.1.** Original utility code is MIT-licensed; BinauraWave artwork and trademark rights are reserved separately.

![Dark interface showing a sample naming preview](screenshots/dark-theme.jpg)

The screenshot shows an earlier build with demonstration text. The main preview layout remains the same; the existing-output choices are described below.

## Features

- Match Audacity export numbers to script paragraphs, with numeric sorting and strict count/sequence validation.
- Treat blank-line-separated paragraphs as clips; retain full original text and remove literal `[pause]` markers only from titles/cleaned text.
- Suggest descriptive titles using deterministic, offline phrase extraction. Edit every suggestion before copying.
- Preview original filenames, paragraph numbers, final filenames and complete text.
- Export title-only MP3 filenames, preserving original bytes without re-encoding or changing audio tags.
- Create a UTF-8 CSV manifest with filenames, titles, category, original/cleaned text and original track numbers.
- Reject case-insensitive duplicate titles, unsafe names and changed inputs. Choose another output folder or explicitly replace recognised exports with recovery backups; no silent overwrites or numeric suffixes.
- Use a lightweight dark Tkinter interface, local logo/icon and native dark Windows title bar where supported.

No account, API key, paid service, telemetry, automatic splitting, transcription or ElevenLabs integration is involved. Audio files and scripts remain on your computer. Only clicking a website link opens a browser.

## Install and run

### Windows executable

Download the Windows x64 ZIP from the [official GitHub Releases page](https://github.com/cmderdanblackburno7/audio_asset_namer/releases) when a release is available, extract it and double-click `BinauraWave-Audio-Asset-Namer.exe`. No Python, pip, Tkinter installation or administrator privileges are required. Keep the ZIP's licence/branding/third-party notices with the application when redistributing it.

The current executable is unsigned. Windows SmartScreen may show an unrecognised-app warning because a new unsigned publisher has little reputation. Do not bypass warnings for an unexpected download: check the official repository, release filename and checksum, or wait for a signed release. A checksum is an integrity check, not a code signature or a guarantee that antivirus products will trust the file.

The executable can run from an ordinary folder such as Desktop or Downloads. Its runtime extracts temporarily into Windows temp; user audio/CSV output goes only into `Named` beneath the audio folder you choose, or an alternative output folder you explicitly select. The utility does not rely on another BinauraWave application, repository, website connection or development directory.

### From source

Install Python **3.10+** with Tcl/Tk support. From this checkout:

```powershell
python app.py
```

On Windows, `launch.bat` also works with a usable Python launcher or PATH installation. No `pip install` is needed to run the source app. Keep `favicon.ico`, `assets/logo.png` and the Python modules together; asset paths resolve relative to the application, not the working directory. Missing branding artwork falls back gracefully.

## Verify your download

Download `SHA256SUMS.txt` from the same official release as the ZIP. In Windows PowerShell, from the download folder:

```powershell
Get-FileHash .\BinauraWave-Audio-Asset-Namer-1.3.1-Windows-x64.zip -Algorithm SHA256
```

Compare **all 64 hexadecimal characters** in the output with the matching ZIP line in `SHA256SUMS.txt` (letter case does not matter). Stop if they differ and obtain a fresh copy from the official release. After extraction, you can also run `Get-FileHash .\BinauraWave-Audio-Asset-Namer.exe -Algorithm SHA256` and compare the EXE line. Checksums are calculated from the final files and reverified by the build; they detect corruption/changes when the checksum source is trusted.

## Usage

1. Manually split/export clips in Audacity into one folder, for example `01.First track.mp3`, `02.Audio 1.mp3` and `03.Audio 2.mp3`.
2. Save the matching script as UTF-8 `.txt`, one intended clip per paragraph separated by blank lines. Single line breaks stay inside their paragraph; `[pause]` markers do not split it.
3. Select the audio folder and script, then choose **Load / reload preview**.
4. Check every mapping, select rows to inspect the full text, and edit titles in the title field. Filename previews update immediately.
5. Choose **Confirm and copy…**, check the full destination path, then review the per-file results.
6. If `Named` already exists, choose **Choose another folder**, **Replace existing exports** or **Cancel**. Choosing another folder is the initial keyboard/default choice; replacement requires a separate confirmation that defaults to Cancel. Cancelling either dialog or the folder picker makes no file changes.

Only immediate-child MP3s with leading ASCII digits followed by a period, space, underscore or hyphen are included; extension matching is case insensitive. Numbers must run exactly from **1 through the paragraph count**, with no gaps, duplicates or zero. Unnumbered MP3s are ignored and listed. The utility never guesses which paragraph belongs to which recording.

A valid sequence cannot prove the spoken content matches the script: verify the export order yourself. Suggestions use English-language heuristics, aim for 4–8 words within 50 characters, and can be imperfect. Review unfamiliar topics, pronouns, negation and short passages. Repeated suggestions require manual edits; titles must be unique without regard to case.

## Output and privacy

By default, a new `Named` subfolder contains files such as `Noticing Your Natural Breathing Rhythm.mp3` and `manifest.csv`. Originals and the source script are retained unchanged. The selected **audio** folder's name remains the category, even when saving elsewhere.

When `Named` already exists:

- **Choose another folder** opens the standard folder picker. Files go directly into the selected folder, without another `Named` subfolder. Unrelated files can stay there, but any existing target filename or `manifest.csv` collision (including letter-case differences) is refused. Select a separate output folder rather than the original audio folder.
- **Replace existing exports** shows the full destination again and requires explicit confirmation. Only files identified by this session's manifest, plus that manifest, may be replaced. Old title filenames belonging to those exports are removed from the live output; unrelated files and subfolders are retained. If an old MP3 or manifest has been changed, ownership is ambiguous, or a new title collides with an unrelated file, replacement is refused. Choosing another folder remains available.
- **Cancel**, Escape or closing the choice dialog leaves files unchanged. Cancelling the picker or the final confirmation also makes no changes.

Replacement is deliberately conservative: previous manifest rows must match the current track numbers, category and exact paragraphs, and previous audio must still match the selected original recordings. Re-exported/edited original audio, changed scripts or missing/foreign manifests can require a new destination rather than guessing ownership. A manifest from an earlier partial export can be completed safely when its existing entries still match. Replacement needs a local fixed Windows **NTFS** drive; other locations can be used for ordinary non-overwriting copies into a new/non-conflicting folder.

New clips and the complete manifest are staged and checked first. All recognised previous files are copied into flushed recovery storage before any live export is moved. Publication never overwrites a file that appeared unexpectedly. Ordinary failures attempt rollback; previous versions are retained in `.audio-namer-backup-<id>/previous`, with a small transaction record. Keep these backup folders until you have checked the result; they use additional disk space. The app never recursively deletes an output folder or unrelated contents.

Fresh/non-replacement exports keep the existing per-file behaviour: a failed copy may leave successful audio and a manifest of successful copies for inspection. Replacement is treated as one staged set; failures are reported for the requested set and preserve or restore the previous exports. The copy button remains available after completion so another export can be requested without moving the folder aside.

### If an export is interrupted

A multi-file update cannot be a single atomic folder operation. After a forced process exit, the visible output can be incomplete even though previous data is preserved. `.audio-namer-transaction-<id>` and `.audio-namer-export.lock` block another operation into that folder; the app gives the recovery location rather than guessing or overwriting.

Close the app and keep the interrupted folder and its recovery files. You can continue safely by choosing a different output folder. For recovery, inspect `transaction.json`: when `backups_verified` is `true`, `previous/` contains the verified prior exports and manifest. Copy those files into a **separate empty recovery folder** to inspect them; do not blindly overwrite unrelated current files. When `backups_verified` is `false`, replacement had not started moving prior exports: inspect the retained live files instead of trusting an incomplete recovery copy. Do not edit the journal or remove a lock while an export might still be running. If unsure, retain everything and contact support with redacted details.

Backups protect against tested application/process failures, not arbitrary hardware damage or every power-loss scenario. Do not edit output files concurrently with an export. Locked files or incomplete rollback may require inspection/recovery; the app refuses further replacement in an unresolved transaction folder.

The CSV columns are:

| Column | Meaning |
| --- | --- |
| `filename` | Final title-only MP3 basename |
| `title` | Reviewed title |
| `category` | Selected audio folder name |
| `full_original_text` | Full paragraph, including pause markers/internal line breaks |
| `cleaned_spoken_text` | Paragraph with `[pause]` removed and whitespace normalised |
| `track_number` | Original numeric export sequence, for example `01` becomes `1` |

The script's UTF-8 BOM and paragraph separators are structural; paragraph contents are preserved. Inputs are checked again before export. Very long Windows paths may require a shorter location. No files are uploaded. Do not include personal scripts, audio or manifests in bug reports without reviewing their contents. CSV preserves supplied text faithfully: import its columns as text when using a spreadsheet application, which could otherwise interpret formula-like text.

## Build a Windows executable

Use **64-bit Windows and the reviewed official PSF Python 3.13.17 runtime** with Tkinter, pip and venv support. From this checkout:

```powershell
py -3.13 build_windows.py --gui-smoke
```

Or double-click `build_windows.bat`. The release builder checks the exact Python version and native binary hashes in `licenses/runtime-provenance.json`; an old/custom runtime is refused. Move any old `.build-venv` into an ignored backup folder before changing runtimes. Other runtime versions need a fresh provenance/licensing review.

A project-local runtime can also be prepared without a system install: download the [official full runtime ZIP](https://www.python.org/ftp/python/3.13.17/python-3.13.17-amd64.zip), compare its SHA-256 with `archive_sha256` in the provenance file and the [PSF release manifest](https://www.python.org/ftp/python/3.13.17/windows-3.13.17.json), then extract it into `build/python-runtime`. Run `.\build\python-runtime\python.exe build_windows.py --gui-smoke`. The embeddable ZIP is a different package and lacks Tkinter.

 The script creates an ignored `.build-venv`, installs the exact build-only dependencies in `requirements-build.txt`, runs this checkout's tests, and builds with PyInstaller's one-file/windowed spec. Initial dependency installation needs package-index access. `--skip-install` reuses an already prepared environment; `--gui-smoke` needs an interactive desktop and can be omitted for regular tests.

Outputs go to ignored `dist/`: the executable, short README, versioned Windows-x64 ZIP and build/checksum report plus `SHA256SUMS.txt`. The ZIP includes source/branding licence notices and collected Python/Tcl/Tk/build-package notices. The build report also records the source commit and whether the source tree was dirty. A final release must be built from a clean reviewed commit. The source app has no additional runtime pip dependencies. `build/` holds temporary build data. No development fixtures, source audio, private application files or copied virtual environment are bundled. Unused XZ/LZMA decoding is explicitly excluded; bundled native files must match the reviewed PSF binaries. PyInstaller uses a restricted runtime/Windows PATH so unrelated developer tools cannot supply native dependencies.

Review [third-party requirements](THIRD_PARTY_NOTICES.md) and the [release test checklist](PACKAGING_TESTS.md) before publication. Compiled executables and ZIPs belong in **GitHub Releases**, never source commits. Build/publishing/signing are separate steps; these scripts do not push, upload or change Git remotes.

## Tests

```powershell
python tests/audio_asset_namer_regression.py
python tests/audio_asset_namer_regression.py --gui-smoke
python tests/release_packaging_regression.py
python tests/export_workflow_regression.py --gui-smoke
```

Tests and fixtures are included here and need no other repository, credentials, network service, real audio collection or paid API. Dummy audio bytes are sufficient to verify byte-copy behavior. The optional GUI smoke checks actual Tk controls, editing/export, contrast, keyboard traversal, layout, assets and native Windows branding.

## Links and support

- [BinauraWave](https://binaurawave.com/)
- [Create Audio Sessions](https://binaurawave.com/binaurawave_app/)
- [Help & Support](https://binaurawave.com/feedback/)
- [GitHub source and issues](https://github.com/cmderdanblackburno7/audio_asset_namer)


All four footer links are optional and open only when clicked; they cause no startup requests. The three BinauraWave website links include `utm_source=asset-namer`, `utm_medium=desktop_app` and `utm_campaign=free_creator_tools` for website attribution. GitHub is unchanged. These query parameters are sent to the website only when you open a link; no analytics SDK, cookies or background tracking is added to the desktop app. Report ordinary bugs through [GitHub Issues](https://github.com/cmderdanblackburno7/audio_asset_namer/issues), with the version, Windows version, redacted error text and a tiny synthetic example. For security concerns, see [SECURITY.md](SECURITY.md) and contact support before posting sensitive details publicly. Do not send personal audio, full scripts, passwords, API keys or unredacted local file paths.

## Video Demonstration

See how to split audio recordings in Audacity and
automatically rename the resulting files with
BinauraWave Audio Asset Namer.

[![Watch demonstration](https://img.youtube.com/vi/eT6hSekWv2g/hqdefault.jpg)](https://www.youtube.com/watch?v=eT6hSekWv2g)

## Licence, branding and limitations

Original source code, tests, build scripts and original documentation are under the [MIT licence](LICENSE). This does not extend to the reserved BinauraWave name, trademarks, logo, favicon or branded artwork: see [BRANDING.md](BRANDING.md). Third-party components keep their own licences; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The workspace uses Tk's bundled `clam` theme and standard-library Windows APIs. Native file pickers and message dialogs follow OS styling; unsupported systems may keep a light title bar. Large text/high-DPI settings, clean-machine executable releases and browser associations need release-time checks. The fixed dark workspace does not automatically follow OS high-contrast preferences.

See [RUNTIME_SECURITY.md](RUNTIME_SECURITY.md) for the dated native-library/advisory review and [RELEASE_READINESS.md](RELEASE_READINESS.md) for exact artifact identities and performed checks. A separate Windows 10 laptop successfully processed 10 real MP3s in the previous 1.2.6 build, as reported by its owner. Its occasionally light title bar until focus is a cosmetic limitation. Version 1.3.0 added the output-choice/replacement workflow; 1.3.1 adds website-link attribution and requires fresh packaged checks; the report distinguishes those builds.

See [CHANGELOG.md](CHANGELOG.md) for version history. This standalone utility contains no commercial BinauraWave application code.
