# Testing and release review

Run `python tests/audio_asset_namer_regression.py` from this standalone checkout. Add `--gui-smoke` on an interactive Windows desktop to check the actual Tk interface. All fixtures are local examples and generated dummy bytes; no personal audio or private repository is needed.

The 24 existing checks cover numeric source matching, invalid counts/sequences, UTF-8/BOM/paragraph preservation, pause cleaning, descriptive titles across topics, duplicate/unsafe titles, exact byte copies, CSV fields, unchanged originals, stale previews, overwrite prevention, copy/manifest failures, local branding, source/bundle asset paths and packaging configuration. The optional desktop smoke exercises loading, editing, export, contrast, keyboard traversal, four layouts and native Windows icon/DWM readback. It mocks website opening; the tests make no website requests.

## Before attaching a Windows build to GitHub Releases

- Build from a clean standalone checkout using `build_windows.py --gui-smoke`.
- Confirm `dist/` contains a one-file/windowed executable, versioned ZIP and checksums. Never commit those files.
- Inspect the ZIP's `LICENSE`, `BRANDING.md`, `THIRD_PARTY_NOTICES.md` and runtime/package notice files. Reconcile any new DLLs/dependencies with their redistribution terms.
- Run the executable alone from an unrelated folder on a clean Windows machine without Python, using disposable numbered MP3s and a UTF-8 script.
- Check the local logo/icon, title bar, native pickers, matching preview, edited filenames, duplicate rejection, confirmed output directory, per-file results and CSV. Compare copied audio hashes and confirm originals/scripts remain unchanged.
- Check all three website links in the default browser. GitHub stays disabled until an actual public repository URL is configured.
- Check standard and high-DPI displays, Windows 10/11, taskbar shortcuts and release signing status.

A passing source test suite is not a substitute for reviewing a newly built executable and its licences. This preparation does not build, upload or publish a binary. Old local build/test paths and records are intentionally excluded from public documentation.
