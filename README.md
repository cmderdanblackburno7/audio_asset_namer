# BinauraWave Audio Asset Namer

A free, offline Windows desktop utility for turning numbered Audacity MP3 exports into descriptive, editable filenames. Pair your clips with a UTF-8 script, review the suggested titles, and copy the named audio into a fresh folder with a CSV manifest.

**Current source version: 1.2.5.** Original utility code is MIT-licensed; BinauraWave artwork and trademark rights are reserved separately.

![Dark interface showing a sample naming preview](screenshots/dark-theme.jpg)

The screenshot shows an earlier build with demonstration text. The layout and workflow remain the same.

## Features

- Match Audacity export numbers to script paragraphs, with numeric sorting and strict count/sequence validation.
- Treat blank-line-separated paragraphs as clips; retain full original text and remove literal `[pause]` markers only from titles/cleaned text.
- Suggest descriptive titles using deterministic, offline phrase extraction. Edit every suggestion before copying.
- Preview original filenames, paragraph numbers, final filenames and complete text.
- Export title-only MP3 filenames, preserving original bytes without re-encoding or changing audio tags.
- Create a UTF-8 CSV manifest with filenames, titles, category, original/cleaned text and original track numbers.
- Reject case-insensitive duplicate titles, unsafe names, changed inputs and existing output folders. Never overwrite or add automatic numeric suffixes.
- Use a lightweight dark Tkinter interface, local logo/icon and native dark Windows title bar where supported.

No account, API key, paid service, telemetry, automatic splitting, transcription or ElevenLabs integration is involved. Audio files and scripts remain on your computer. Only clicking a website link opens a browser.

## Install and run

### Windows executable

When a release has been published, download the Windows x64 ZIP from **this repository's GitHub Releases page**, extract it and double-click `BinauraWave-Audio-Asset-Namer.exe`. No Python, pip, Tkinter installation or administrator privileges are required. No release URL is assumed or invented here.

The executable can run from an ordinary folder such as Desktop or Downloads. Its runtime extracts temporarily into Windows temp; user audio/CSV output goes only into `Named` beneath the audio folder you choose. The utility does not rely on another BinauraWave application, repository, website connection or development directory.

### From source

Install Python **3.10+** with Tcl/Tk support. From this checkout:

```powershell
python app.py
```

On Windows, `launch.bat` also works with a usable Python launcher or PATH installation. No `pip install` is needed to run the source app. Keep `favicon.ico`, `assets/logo.png` and the Python modules together; asset paths resolve relative to the application, not the working directory. Missing branding artwork falls back gracefully.

## Usage

1. Manually split/export clips in Audacity into one folder, for example `01.First track.mp3`, `02.Audio 1.mp3` and `03.Audio 2.mp3`.
2. Save the matching script as UTF-8 `.txt`, one intended clip per paragraph separated by blank lines. Single line breaks stay inside their paragraph; `[pause]` markers do not split it.
3. Select the audio folder and script, then choose **Load / reload preview**.
4. Check every mapping, select rows to inspect the full text, and edit titles in the title field. Filename previews update immediately.
5. Choose **Confirm and copy to Named...**, check the destination, then review the per-file results.

Only immediate-child MP3s with leading ASCII digits followed by a period, space, underscore or hyphen are included; extension matching is case insensitive. Numbers must run exactly from **1 through the paragraph count**, with no gaps, duplicates or zero. Unnumbered MP3s are ignored and listed. The utility never guesses which paragraph belongs to which recording.

A valid sequence cannot prove the spoken content matches the script: verify the export order yourself. Suggestions use English-language heuristics, aim for 4–8 words within 50 characters, and can be imperfect. Review unfamiliar topics, pronouns, negation and short passages. Repeated suggestions require manual edits; titles must be unique without regard to case.

## Output and privacy

A new `Named` subfolder contains files such as `Noticing Your Natural Breathing Rhythm.mp3` and `manifest.csv`. Originals and the source script are retained unchanged. The selected audio folder's name becomes the initial category. An existing `Named` file or folder is refused, even if empty; inspect/move it aside before retrying. Interrupted or failed copies can leave partial output for inspection; the manifest records successful copies and the results panel reports each file.

The CSV columns are:

| Column | Meaning |
| --- | --- |
| `filename` | Final title-only MP3 basename |
| `title` | Reviewed title |
| `category` | Selected audio folder name |
| `full_original_text` | Full paragraph, including pause markers/internal line breaks |
| `cleaned_spoken_text` | Paragraph with `[pause]` removed and whitespace normalised |
| `track_number` | Original numeric export sequence, for example `01` becomes `1` |

The script's UTF-8 BOM and paragraph separators are structural; paragraph contents are preserved. Inputs are checked again before export. Very long Windows paths may require a shorter location. No files are uploaded. Do not include personal scripts, audio or manifests in bug reports without reviewing their contents.

## Build a Windows executable

Use **64-bit Windows and Python 3.12** with Tkinter, pip and venv support. Python 3.11+ can run the build script. From this checkout:

```powershell
py -3.12 build_windows.py --gui-smoke
```

Or double-click `build_windows.bat`. The script creates an ignored `.build-venv`, installs the exact build-only dependencies in `requirements-build.txt`, runs this checkout's tests, and builds with PyInstaller's one-file/windowed spec. Initial dependency installation needs package-index access. `--skip-install` reuses an already prepared environment; `--gui-smoke` needs an interactive desktop and can be omitted for regular tests.

Outputs go to ignored `dist/`: the executable, short README, versioned Windows-x64 ZIP and build/checksum report. The ZIP includes source/branding licence notices and collected Python/Tcl/Tk/build-package notices. The source app has no additional runtime pip dependencies. `build/` holds temporary build data. No development fixtures, source audio, private application files or copied virtual environment are bundled.

Review [third-party requirements](THIRD_PARTY_NOTICES.md) and the [release test checklist](PACKAGING_TESTS.md) before publication. Compiled executables and ZIPs belong in **GitHub Releases**, never source commits. Build/publishing/signing are separate steps; these scripts do not push, upload or change Git remotes.

## Tests

```powershell
python tests/audio_asset_namer_regression.py
python tests/audio_asset_namer_regression.py --gui-smoke
```

Tests and fixtures are included here and need no other repository, credentials, network service, real audio collection or paid API. Dummy audio bytes are sufficient to verify byte-copy behavior. The optional GUI smoke checks actual Tk controls, editing/export, contrast, keyboard traversal, layout, assets and native Windows branding.

## Links and support

- [BinauraWave](https://binaurawave.com/)
- [Create Audio Sessions](https://binaurawave.com/binaurawave_app/)
- [Help & Support](https://binaurawave.com/feedback/)

These links are optional; the naming workflow is fully offline. The app's GitHub link remains disabled until a real public repository exists. When reporting a problem, include the application version, Windows/Python version if applicable, error text and a small anonymised example.

## Licence, branding and limitations

Original source code, tests, build scripts and original documentation are under the [MIT licence](LICENSE). This does not extend to the reserved BinauraWave name, trademarks, logo, favicon or branded artwork: see [BRANDING.md](BRANDING.md). Third-party components keep their own licences; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The workspace uses Tk's bundled `clam` theme and standard-library Windows APIs. Native file pickers and message dialogs follow OS styling; unsupported systems may keep a light title bar. Large text/high-DPI settings, clean-machine executable releases and browser associations need release-time checks. The fixed dark workspace does not automatically follow OS high-contrast preferences.

See [CHANGELOG.md](CHANGELOG.md) for version history. This standalone utility contains no commercial BinauraWave application code.
