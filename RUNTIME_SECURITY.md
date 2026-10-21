# Runtime security and redistribution review — 2026-10-22

Scope: Audio Asset Namer 1.2.6, Windows x64, normal-user local file processing. This is an evidence-based applicability review, not penetration testing, an antivirus certification or a guarantee against unknown vulnerabilities. `RELEASE_READINESS.md` identifies the exact final artifacts and test results.

## Provenance and practical fixes

The previous candidate used a custom Python 3.12.14 runtime reporting OpenSSL 3.5.8; exact libffi/liblzma provenance could not be established. Those binaries are superseded. No exploitable path through the app was demonstrated, but replacing that runtime removes the uncertainty and incorporates current Python/OpenSSL security patches.

The replacement is the **official PSF Python 3.13.17 Windows AMD64 full runtime**, released 2026-10-21:

- [Official manifest](https://www.python.org/ftp/python/3.13.17/windows-3.13.17.json), entry `pythoncore-3.13-64`.
- [Full runtime ZIP](https://www.python.org/ftp/python/3.13.17/python-3.13.17-amd64.zip), SHA-256 `b26ca4b4ee51e157836049934d2b8eabd55939be296f3130254251b6df96ec2f`, downloaded and matched to the manifest before extraction. No system Python installation was changed.
- Its `python313.dll` Authenticode signature validated as **Python Software Foundation**. This does not sign the finished application EXE.
- [PSF release SBOM](https://www.python.org/ftp/python/3.13.17/python-3.13.17-amd64.exe.spdx.json), [Windows dependency declarations](https://github.com/python/cpython/blob/v3.13.17/PCbuild/python.props) and [Tcl/Tk declarations](https://github.com/python/cpython/blob/v3.13.17/PCbuild/tcltk.props) establish dependency origins. The installer SBOM describes the official Windows build, not a claim that every listed component ships in this utility. Actual runtime version queries confirm Python 3.13.17, OpenSSL 3.5.9, Tcl/Tk 8.6.15, zlib 1.3.1 and mpdecimal 4.0.0.

`licenses/runtime-provenance.json` records the PSF URLs, ZIP/SBOM hashes and 34 native-file hashes from that verified ZIP. Before building, both the selected interpreter and cached build environment must match. After building, **every bundled DLL/PYD** must match an official file hash; unknown/mismatched native files fail the build. The PyInstaller bootloader separately comes from pinned PyInstaller 6.22.3. This is stronger than inferring origin from a DLL filename or version string.

Unused `lzma`/`_lzma` archive support is excluded in the spec, removing liblzma from the frozen app. No DLL was swapped individually. The application source, UI, title rules, input validation, copying and CSV behaviour are unchanged; version remains 1.2.6.

## What the application actually uses

| Component | Origin/terms | Use and exposure |
| --- | --- | --- |
| CPython 3.13.17 / standard library | PSF, retained historical/incorporated terms | Parses UTF-8 script paragraphs and numbers; works with paths/regex/queues/threads/CSV; streams opaque MP3 bytes. No audio decoding, script execution, archive extraction, remote downloads or TLS endpoint. |
| Tcl/Tk 8.6.15 / `_tkinter` | PSF Windows distribution, permissive Tcl/Tk notices; embedded libtommath and zlib keep own terms | UI, fixed local logo, native dialogs, text display. User text is inserted as data through Tkinter, not evaluated as Tcl commands. No user-supplied images, fonts or Tcl programs are loaded. |
| libffi 3.4.4 / `_ctypes` | PSF SBOM; upstream MIT | Fixed Windows shell/icon/DWM API calls with declared signatures and developer-selected DLL/function names. Paragraphs do not control FFI types, pointers or callbacks. |
| OpenSSL/libcrypto 3.5.9 | PSF SBOM; Apache-2.0/AUTHORS | Can accompany standard-library hash support in the conservative bundle. The app offers no certificates, keys, encrypted traffic or crypto operations on selected inputs. Opening links delegates to the external browser. |
| zlib 1.3.1 | PSF/Tcl source; zlib licence | Trusted embedded-code/assets decompression, including PyInstaller/Tk PNG handling; the app does not decompress selected audio/scripts. |
| bzip2 1.0.8, mpdecimal 4.0.0 | PSF SBOM; retained bzip2 / BSD-2-Clause terms | May be collected through standard-library dependencies; no bzip2 or decimal operations exposed by the application. Presence/import is distinguished from use of vulnerable APIs. |
| HACL*, Unicode, other incorporated CPython code | PSF source notices retained in `PYTHON-INCORPORATED.rst` and HACL notice | Builtin/runtime support; their notices supplement, rather than replace, the complete interpreter licence. |
| XZ/liblzma 5.2.5 | Origin now known from PSF SBOM; public-domain liblzma terms | **Excluded from release EXE**. Historical notice is retained; no XZ command-line tools were ever included. |
| Microsoft VC runtime | Unmodified PSF runtime files, checked by exact hashes | Native Windows runtime support. Microsoft redistribution conditions remain in the full collected interpreter licence; no claim of MIT licensing. Windows OS DLLs used in place are not application-authored components. |

Static review of `app.py`, `core.py`, `titles.py`, `theme.py` and `windows_branding.py` found no route from selected input to SSL, certificate parsing, urllib authentication, archive extraction, crypto-key processing or dynamic FFI declarations. Profiling the existing source GUI smoke exercise observed no SSL/hashlib/bzip2/LZMA/decimal/socket/zlib native API calls; imports made by a test harness alone are not evidence that those features are used. Profiling is bounded evidence, not exhaustive reachability analysis; export also has a worker thread whose source was reviewed directly.

## Advisory applicability

| Advisory / verified upstream evidence | Finding for this release |
| --- | --- |
| [Python 3.13.16 security fixes](https://www.python.org/downloads/release/python-31316/) and [3.13.17 release](https://www.python.org/downloads/release/python-31317/) | New 3.13.17 contains the security updates missing from the previous 3.12.14 runtime. The earlier SSL, tarfile, zipfile, urllib credential and StringPrep paths were not exposed by this app; upgrading avoids depending on that assessment alone. Pip/certifi's October certificate update is build-side; pip/certifi are not shipped in the frozen application. |
| [OpenSSL 3.5.9 security release](https://www.openssl-library.org/news/openssl-3.5-notes/) | Replaces 3.5.8. Reviewed September fixes concern DTLS/QUIC, certificates/CRLDP, CMP and EC/SM2 operations, not MP3 copying. The application has no such endpoint/API flow; the fixed version is used regardless. |
| [XZ GHSA-x872-m794-cxhv / CVE-2026-34743](https://github.com/tukaani-project/xz/security/advisories/GHSA-x872-m794-cxhv) and [GHSA-5qpq-xqfv-j9pg](https://github.com/tukaani-project/xz/security/advisories/GHSA-5qpq-xqfv-j9pg) | Version 5.2.5 falls within affected ranges. Required index-append / decoder reinitialisation operations are not offered by this app. Practical fix: remove unused liblzma from the bundle; the build fails if `_lzma` reappears. |
| [XZ CVE-2025-31115](https://github.com/tukaani-project/xz/security/advisories/GHSA-6cc8-p5mm-29w2) | Affects multithreaded decoding from 5.3.3alpha through 5.8.0; 5.2.5 is outside that range and now excluded anyway. [CVE-2024-47611](https://github.com/tukaani-project/xz/security/advisories/GHSA-m538-c5qw-3cg4) concerns Windows XZ command-line tools, not liblzma; those tools are not bundled. |
| [zlib CVE-2026-27171 / upstream issue 904](https://github.com/madler/zlib/issues/904) | zlib 1.3.1 is version-affected, but the fault requires a negative length passed to `crc32_combine*`. Exact Python 3.13.17 `Modules/zlibmodule.c`, Tcl 8.6.15 `generic/tclZlib.c` and PyInstaller 6.22.3 `bootloader/src/pyi_archive.c` contain no `crc32_combine` calls. Python 3.13 does not expose this combine API. App byte-copy/UI flows cannot supply that argument. **Not applicable to reviewed flows**, not a claim that zlib 1.3.1 has no advisories. |
| [libffi CVE-2017-1000376](https://nvd.nist.gov/vuln/detail/CVE-2017-1000376) | ELF executable-stack hardening issue, not the reviewed Windows AMD64 DLL. No input-controlled FFI declarations. No applicable libffi/Tcl/Tk/bzip2/mpdecimal issue was identified in the bounded upstream/database review; this is not proof none exists. |
| [PyInstaller GHSA-9fxf-4qw3-ghmr](https://github.com/pyinstaller/pyinstaller/security/advisories/GHSA-9fxf-4qw3-ghmr) | Fixed before pinned 6.22.3. The resulting EXE requests `asInvoker`, not administrator privileges. OSV checks on 2026-10-22 returned no advisories for the seven exact pinned build packages. Native components were reviewed separately; a PyPI-only scan does not clear them. |

Local copies of upstream declarations/advisories and bounded workflow observations are under ignored `build/security-2026-10-22/`. No personal audio/scripts or credentials were sent to advisory services; requests contained public package/version names only.

## Redistribution and remaining limits

The licence gap is closed for the reviewed bundle: exact origins are established, native files are checked, and matching upstream notices accompany the release ZIP through the existing collector. Original utility code remains MIT; reserved BinauraWave branding is unchanged. Third-party notices include the actual interpreter's full licence, incorporated-code terms, Microsoft conditions, OpenSSL/AUTHORS, Tcl/Tk/libtommath, libffi, zlib, bzip2 and mpdecimal attribution, plus installed build-tool notices. An SBOM's `NOASSERTION` field is not used as permission; actual upstream licence texts are retained. A future native dependency or runtime change requires repeating this review.

No confirmed input-reachable security vulnerability remains from the issues investigated. This conclusion is limited to the reviewed code paths and exact files, not every dormant API in the runtime or future advisories. No fuzzing, hostile local-attacker isolation, system-wide network tracing, independent penetration test, code signing or antivirus certification was performed. A user/process already able to modify the EXE, embedded resources or runtime is outside the integrity boundary. Very large scripts can exhaust resources; CSV text must be imported safely in spreadsheets; stat-based stale-input checks are not adversarial locking.

The unsigned distribution may trigger SmartScreen/reputation warnings. Do not disable protections. The owner-reported Windows 10 test covers the earlier artifact's 10-MP3 workflow; the rebuilt artifact's test coverage is reported separately. The occasionally light native title bar until focus is cosmetic, as accepted by the owner. Windows 10 runtime compatibility and high-DPI/alternate-browser spot checks remain useful release QA, without being presented as security vulnerabilities.
