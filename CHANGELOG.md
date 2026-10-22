# Changelog

## 1.3.1 — 2026-10-22

- Add consistent UTM query parameters to the three existing BinauraWave footer destinations using standard-library URL parsing and encoding. GitHub and browser-opening behaviour are unchanged.
- Add regressions for exact destinations/parameters, existing query values, encoding, fragments, idempotence, explicit opening and browser fallback.
- No telemetry SDK, cookies, background requests, audio/export or UI-layout changes. Rebuild the Windows EXE/ZIP and checksums; no publication or push.

## 1.3.0 — 2026-10-22

- Offer Choose another folder / Replace existing exports / Cancel when Named exists, with safe keyboard defaults and full-path confirmation.
- Retain exclusive copies for alternative destinations; reject collisions and keep unrelated files.
- Require strict manifest/session ownership and matching audio before replacing recognised exports. Stage new files and verified backups first; use no-clobber publication, rollback and retained recovery copies.
- Refuse unsupported replacement locations, linked/ambiguous files, active locks and unresolved interrupted transactions. Keep originals, title generation, CSV schema, theme and branding unchanged.
- Add 30 workflow checks (25 backend and five desktop cases), including real Windows file locking and a forced process-exit recovery test; include them in release builds.
- Keep the reviewed Python/native runtime, licence scope and local-only processing. Build a fresh standalone EXE/ZIP; 59 tests, source GUI smoke and packaged Windows 11 workflow passed. Windows 10 retest remains outstanding; no publication or push.

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
