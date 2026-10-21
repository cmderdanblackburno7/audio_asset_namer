# Changelog

## 1.2.6 — 2026-10-21

Runtime/package maintenance reviewed 2026-10-22 (application version unchanged):

- Replace the custom Python 3.12.14 runtime with hash-verified official PSF Python 3.13.17 / OpenSSL 3.5.9 / Tcl/Tk 8.6.15.
- Verify build and bundled native hashes; reject stale environments and isolate DLL discovery from unrelated developer PATH entries.
- Exclude unused XZ/LZMA decoding, retain matching incorporated-software notices and add two release-guard regression tests.
- Document advisory applicability, the owner-reported Windows 10 test and the cosmetic title-bar limitation. Application processing/UI source is unchanged.

- Enable the verified public GitHub footer link; no startup network requests or processing changes.
- Extend existing release hashes with a reverified `SHA256SUMS.txt` and source commit/clean-tree metadata.
- Add focused release-check tests and improve official download/checksum, unsigned-build and security-reporting documentation.
- Retain additional bundled OpenSSL, zlib, libmpdec, libffi and liblzma notices through the existing licence collector.
- Reuse the existing pinned build and PyInstaller spec for a clean local release audit. No publication, tag or push.

## 1.2.5 — 2026-10-21

- Prepare an independent source repository with its own tests, fixtures and root-relative build paths.
- Add a public README, MIT terms for original code, separate reserved-branding terms and third-party notices.
- Include code/branding/runtime notices in future release ZIPs and keep binaries, environments, caches and user audio out of source control.
- Preserve all naming, preview/editing, validation, audio copying, CSV and link behaviour.
- No public repository, remote changes, push or binary release is created by this preparation.

## Earlier versions

- 1.2.4: standalone Windows one-file/windowed build and versioned distribution ZIP.
- 1.2.3: local window/taskbar icon and native Windows dark title bar.
- 1.2.2: cohesive dark workspace theme.
- 1.2.1: local branding, footer links and About.
- 1.2.0: title-only exported filenames and CSV track-number traceability.
- 1.1.0: source-phrase title suggestions.
- 1.0.0: initial offline naming, preview, validation, byte-copy export and CSV manifest.
