# Release readiness — 2026-10-21

**MANUAL CHECK REQUIRED — retain these files as release candidates; do not publish them yet.** Packaging and local acceptance passed. The bundled runtime needs security/provenance review and a clean-PC check before a public binary release.

## Build identity and files

- Version: **1.2.6**. Enabling the verified public GitHub footer link is the only application behaviour change; naming, validation, copying and CSV logic are unchanged.
- Built from clean local source commit **`15409dfe893d02618836c3b3353d0391a20b6455`** (`dirty: false` recorded before building). This report was written after the build; it is not embedded in the EXE.
- Fresh isolated build environment; Windows 11 x64, Python 3.12.14, Tcl/Tk 8.6.12, PyInstaller 6.22.3. Existing one-file/windowed spec, pinned packages and notice collector reused.
- Location: this checkout's ignored `dist/`. **Unsigned**, confirmed with `Get-AuthenticodeSignature` (`NotSigned`). No publication, tags, pushes, remote or visibility changes were made.

| Final artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `BinauraWave-Audio-Asset-Namer.exe` | 11,881,328 | `86d5dfa7ded009cdfdae72e7689bff6524abc6607c7ad51c635a01315cb22a7a` |
| `BinauraWave-Audio-Asset-Namer-1.2.6-Windows-x64.zip` | 11,668,796 | `062edf0d2f3f51c75605484a63c86fc7d4e503d413f227c1d7ed393c5e20dd7c` |

`SHA256SUMS.txt` contains both final hashes; both were recalculated and verified after packaging. ZIP CRC/member checks passed; its embedded EXE matches the standalone EXE. `build-info.json` retains build versions and source provenance. README documents PowerShell `Get-FileHash` verification. Hashes establish integrity against a trusted checksum, not publisher identity or antivirus approval.

## Performed checks

| Check | Result and scope |
| --- | --- |
| Application regressions | **PASS: 24 tests**, including ordering/counts, titles, duplicates, stale inputs, byte copies, CSV, failures, assets and packaging configuration. |
| Release regressions | **PASS: 3 tests** for final checksum verification/tampering, path escape rejection and absent-Git provenance fallback. |
| Source GUI smoke | **PASS**, actual Tk/Windows icon handles and DWM readback, contrast, Tab focus, About, load/edit/copy/results and four client sizes (1100×820, 1500×800, 1200×680, 800×650). Layouts fit typical 1600×900/1366×768 displays; high DPI remains a manual check. Four link targets verified with mocked browser dispatch; startup performs no browser navigation. |
| EXE packaging | **PASS**, AMD64 PE GUI subsystem 2, `asInvoker` manifest, embedded icon plus bundled favicon/logo/Python/Tk. No unwanted console appeared during normal startup. UPX disabled. |
| Packaged startup | **PASS**, both final dist EXE and ZIP-extracted EXE launched/exited successfully with System32-only PATH and Python/Tcl/Tk environment variables removed. Direct EXE used an unrelated working directory. This is still a developer PC, not proof of a clean installation. |
| Packaged workflow | **PASS**, native folder/script pickers; numeric matching; unnumbered file ignored; descriptive preview; manual edits updated title-only filenames; case-insensitive `Calm`/`calm` duplicate rejected; corrected `Calm.mp3`/`Rest.mp3` export succeeded with per-file results and CSV. |
| Packaged data preservation | **PASS**, post-export hashes confirm exact source bytes copied, both original numbered fixtures, unrelated fixture and script unchanged; CSV retains titles, category, original/cleaned paragraphs and track numbers 1/2. Retrying into existing `Named` was refused and original exports remained intact. Synthetic MP3-labelled bytes were used; decoding/playback was not tested or required by this byte-copy utility. |
| Packaged links/About | **PASS**, four footer clicks opened default Chrome pages with the expected repository, website, session studio and feedback titles. About shows 1.2.6. This checks browser dispatch, not all website features or alternate browser associations. |
| Output locations | **PASS within observed scope**, audio/CSV appeared only in the chosen fixture folder's `Named`; unrelated startup working directory stayed empty. No user output beside the EXE or in bundled assets. One-file extraction uses normal Windows temp. No system-wide filesystem/network trace was performed. |
| Source/bundle audit | **PASS within reviewed scope**, tracked-text secret/private-home-path pattern scan found no matches; no audio, executables, archives or environments tracked. Actual EXE/PYZ inventory contains standard runtime/app modules, no private app, tests or build-tool modules. App bytecode filenames are relative and contain no developer home paths. No credentials, telemetry, API calls or startup network code found. |

Local supporting evidence is ignored under `build/security/` and `build/acceptance-1.2.6/`; it is not release content. Expected PyInstaller warnings concern conditional POSIX/importlib modules; no missing asset or runtime error was observed.

## Security and licence findings

- **Build pins:** OSV query on 2026-10-21 returned no advisories for PyInstaller 6.22.3, hooks-contrib 2026.9, altgraph 0.17.5, packaging 26.3, pefile 2024.8.26, pywin32-ctypes 0.2.3 and setuptools 84.2.1. This is a database snapshot, not a comprehensive native-runtime scan. [PyInstaller GHSA-9fxf-4qw3-ghmr](https://github.com/pyinstaller/pyinstaller/security/advisories/GHSA-9fxf-4qw3-ghmr) affects versions before 6.22.1; this build uses a patched version and requests no elevation.
- **Runtime review required:** bundled Python **3.12.14** predates [3.12.15's security fixes](https://www.python.org/downloads/release/python-31215/). Bundled OpenSSL/libcrypto **3.5.8** predates [3.5.9's security fixes](https://www.openssl-library.org/news/openssl-3.5-notes/), including [CVE-2026-35189](https://www.openssl-library.org/news/vulnerabilities-3.5/index.html) affecting versions before 3.5.9. The app does not offer SSL/certificate/archive processing and only opens fixed URLs in a separate browser; that is an initial reachability observation, not a complete proof that all affected code is unreachable. Prefer a reviewed, updated runtime and rebuild; otherwise document a maintainer-reviewed applicability decision before publication. No runtime DLLs were replaced ad hoc.
- **Runtime inventory:** Python/Tcl/Tk, VCRUNTIME140/UCRT/API-set DLLs, libcrypto/libffi and the `_bz2`, `_ctypes`, `_decimal`, `_hashlib`, `_lzma`, `_queue`, `_socket`, `_tkinter`, `select` and `unicodedata` extensions. Reported zlib is 1.3.2 and libmpdec 2.5.1. Exact libffi/liblzma build versions were not established; Tcl/Tk 8.6.12 also requires currency review. Do not interpret the Python-package OSV result as clearance of these native components.
- **Licence status: provisional pending runtime provenance.** Final ZIP has 38 members including original-code MIT terms, reserved BinauraWave branding, complete actual interpreter licence (including Microsoft/bzip2 terms), Tcl/Tk terms, installed build-package notices and added OpenSSL/AUTHORS, zlib and libmpdec notices. Baseline libffi/liblzma notices are included, but their exact build provenance/terms must be confirmed. See `licenses/README.md` and `THIRD_PARTY_NOTICES.md`. The [PyInstaller bundling exception](https://pyinstaller.org/en/stable/license.html) permits the application's chosen licence subject to dependency terms; third-party code and artwork are not relicensed under MIT.
- **Trust/limitations:** unsigned one-file applications may trigger SmartScreen or antivirus heuristics. Existing windowed bootloader, official local icon, no UPX/obfuscation, no installer/admin requirement and restrained bundle reduce avoidable surprises; no antivirus scan, signing, malware-free certification or universal trust claim is made. Preserve Windows protections. CSV faithfully retains supplied text; import as text in spreadsheets. Input-stat checks are not adversarial locking, and very large/untrusted scripts can consume resources.

## Required manual work before publication

1. Resolve the Python/OpenSSL security review, exact libffi/liblzma provenance and runtime/Tcl/Tk currency. If the runtime changes, review matching notices, rebuild, repeat acceptance and regenerate this report/checksums.
2. Test the final candidate on another clean Windows machine without Python, as a normal user, from actual Downloads/Desktop. Repeat native selection, preview/edit/export with disposable real MP3s; compare hashes/CSV; confirm offline operation. Developer-PC tests above are not marked as clean-PC passes.
3. Check Windows 10 if it will be supported, high DPI/text scaling, taskbar/shortcut icons, minimising/maximising/remapping and alternate default browsers. Main-window icon/dark title bar were observed on this Windows 11 machine; unsupported systems may retain OS-native styling.
4. Decide whether to sign. If signing changes the EXE, rebuild the ZIP and recompute both checksums. Review actual SmartScreen/antivirus results without bypassing protections. Publish the reviewed source commit only through a separately authorised push/tag/release step.

## Exact eventual release upload set

After the checks above, attach only:

- `BinauraWave-Audio-Asset-Namer-1.2.6-Windows-x64.zip`
- `SHA256SUMS.txt`

The ZIP includes the EXE and required legal notices. The EXE hash also supports checking after extraction; avoid distributing a bare EXE without its notices. Do not upload old 1.2.4 ZIPs, fixtures, environments, `build/` or internal build reports. Do not commit compiled files to the source repository. If a rebuild changes files, replace the hashes in this report before upload.

## Changes and isolation

Application: `app.py` (verified GitHub link), `core.py` (version only). Build/tests: `build_windows.py`, existing app regression suite and new `tests/release_packaging_regression.py`. Documentation: reviewed/updated README, CHANGELOG, AUDIT_REPORT, PACKAGING_TESTS, RELEASE_README, THIRD_PARTY_NOTICES, SECURITY, this report and `licenses/` provenance/notice files. Existing spec, build launcher, original MIT/branding scope and processing modules are unchanged.

The private BinauraWave repository remained clean at its original HEAD throughout the final read-only check. No private application files were modified or bundled. Existing public remote configuration was left unchanged. The audit/build work and local commits are confined to the standalone copy.
