# Release readiness — 1.3.0 — 2026-10-22

**Ready for owner review and a fresh Windows 10 acceptance check.** The new output workflow passed the checks below. No confirmed blocker was found in those checks. Version 1.2.6 passed the owner's separate Windows 10 laptop test; that result is not claimed for this new version. Nothing has been published, pushed, tagged or released.

## Exact new artifacts

Built from clean standalone source commit `6771d90d1fa0f359fb204416d8e2e43ba2468d45` (`dirty: false`). This post-build report does not change the binaries. Windows x64, one-file/windowed, unchanged reviewed official PSF Python 3.13.17 / OpenSSL 3.5.9 / Tcl/Tk 8.6.15 and PyInstaller 6.22.3.

| File in ignored `dist/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `BinauraWave-Audio-Asset-Namer.exe` | 10,986,446 | `e9ac07b232b080f8358457dc224199f067cac0d5b1526cb68d20cea14fc378c2` |
| `BinauraWave-Audio-Asset-Namer-1.3.0-Windows-x64.zip` | 10,826,680 | `1054ffea9c329fac1f4ea88f97b6236e93988b4c45d668566f0c018aaa9c4ace` |

Final checksums were recomputed after packaged acceptance. The 42-member ZIP passed CRC checks and contains the identical EXE plus README and licensing/provenance notices. `SHA256SUMS.txt` and `build-info.json` identify this build. Earlier 1.2.6 files are not the new release candidate; a backup is retained under ignored `build/release-1.2.6-before-1.3.0/`. The EXE remains unsigned (`NotSigned`).

## Change and safety boundaries

- Existing `Named` opens a friendly, themed three-choice dialog: Choose another folder / Replace existing exports / Cancel. The first choice is the keyboard default; final confirmation defaults to Cancel and shows the full path.
- Alternative destinations use exclusive, non-overwriting copies and refuse filename/manifest collisions, including case-insensitive collisions.
- Replacement is restricted to a local fixed Windows NTFS volume and manifest entries matching the selected session/category/text and original audio. A changed/foreign manifest, changed prior audio, ambiguous ownership, links, collisions, locks or unresolved transactions are refused. Unrelated files and subfolders are kept.
- All new bytes and the complete unchanged-schema CSV are staged first. Verified, flushed copies of all recognised previous exports and their manifest are saved before live files move. Publication is no-clobber. Ordinary failures attempt rollback; backups are retained for inspection/recovery.
- A forced exit can leave an incomplete visible set, but the tested interrupted commit retained a complete verified previous set. Pending workspaces/locks block retries rather than guessing. No claim of atomic multi-file replacement or protection from arbitrary hardware/power-loss damage is made. Recovery instructions are in README.
- Original numbered MP3s and source scripts are never replacement targets. Title generation, matching, CSV fields, branding, dark theme and website-link targets are unchanged. SHA-256 now checks audio identity without parsing/decoding audio or processing keys/certificates. The runtime review in RUNTIME_SECURITY.md includes this follow-up.

## Fresh validation

| Check | Observed result |
| --- | --- |
| Original application regressions | PASS: 24 tests. |
| Release/build safeguards | PASS: 5 tests. |
| Export workflow regressions | PASS: 30 tests (25 backend, five desktop), including repeated exports, alternate destinations, cancellation, duplicates/collisions, ownership refusal, staging/backup/publication failures and rollback. |
| Windows failure checks | PASS: real Windows locked-file refusal/rollback; child-process forced exit mid-commit preserved verified previous files and blocked unsafe retry. |
| Original source GUI smoke | PASS: contrast/focus, icon/DWM readback, four layouts, load/edit/export/results, About and mocked link targets. |
| New packaged Windows 11 workflow | PASS: ZIP-extracted EXE launched with System32-only PATH and no Python/Tcl/Tk overrides; fresh export of two synthetic MP3-labelled byte fixtures succeeded. Repeated export showed the three choices with Choose another folder focused; Escape cancelled without byte changes. Return on the default opened the native Windows folder picker; full alternative destination was shown and export succeeded. |
| Packaged edit/replacement | PASS: edited first title to `Edited Calm`; replacement confirmation defaulted to Cancel (Return cancelled with previous hashes unchanged). Explicit OK then replaced only the two recognised exports and CSV. The old title file left the live output and was retained in the verified backup. |
| File integrity | PASS: all new audio matched original bytes, original numbered files/script hashes stayed unchanged, unrelated file and nested directory stayed unchanged, and all prior exports/CSV matched their recovery copies. Both manifests retained all six original CSV columns and two rows. No pending transaction or lock remained after success. |
| Packaging/runtime integrity | PASS: x64 GUI subsystem, assets, exact PSF native hashes, excluded XZ, legal notices, final ZIP identity and checksums via release build. Local icon/logo and dark native title bar observed in the new EXE. |
| Separate Windows 10 laptop | NOT YET RUN for 1.3.0. Owner reported 1.2.6 worked with ten real MP3s, manual editing and CSV. Retest the new ZIP on that laptop, including the three existing-folder choices. |

The packaged test uses synthetic opaque byte fixtures, not an audio playback test. External links were not re-clicked in this build; targets/behaviour are unchanged and their source callbacks passed the existing smoke check. No new antivirus certification, penetration test, exhaustive filesystem fault analysis or hardware power-cut test is claimed.

## Documentation, scope and handoff

README, CHANGELOG, release README and packaging test instructions were updated for version 1.3.0. SECURITY/RUNTIME_SECURITY describe the new replacement boundary and unchanged reviewed runtime. Main changes are app.py, core.py, new exporting.py, workflow tests and the build test invocation; title/theme/branding modules remain unchanged. Ignore rules exclude transaction data and user manifests.

Replacement requires extra disk space and retains backup folders. Changed scripts/recordings or non-NTFS/network output locations may require Choose another folder. See README for safe recovery; do not blindly restore over current unrelated files. Native message boxes and the standard folder picker retain OS styling. The previously reported light title bar until focus remains cosmetic and is not a release blocker.

For owner testing, use the 1.3.0 ZIP and matching SHA256SUMS.txt above. Binaries stay out of source control. The private BinauraWave repository remained clean at `9175bb6ff29e9d4f9acc24b6f36dc98a69010ace`; all changes were confined to the standalone repository. No remote configuration was changed.

---

# Historical 1.2.6 runtime security review

The assessment and artifact hashes below apply to the previous 1.2.6 candidate, not the new 1.3.0 workflow. They are retained as security-review history; current handoff details are above.

# Release readiness — 2026-10-22

**READY for a first public release based on the checks performed.** No confirmed applicable security or redistribution-licensing blocker remains from the investigated issues. This is a bounded assessment of the reviewed application and exact artifacts, not an absolute security or antivirus guarantee. A quick Windows 10 spot check of the rebuilt files is recommended; it has not been marked as passed.

## Final artifact identity

Version remains **1.2.6**. Application/UI/processing source is unchanged. Only packaging, dependency review, release checks and documentation changed.

Built from clean local commit **`2ba1883da8fb3a868675ffd875cc61bddc4b0b2c`** (`dirty: false`). Later UTF-8 documentation housekeeping and this report do not change the binaries. Windows x64, official PSF Python **3.13.17**, OpenSSL **3.5.9**, Tcl/Tk **8.6.15**, PyInstaller **6.22.3**. Outputs are in ignored `dist/`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `BinauraWave-Audio-Asset-Namer.exe` | 10,870,788 | `28b49b4ad330b2f2712532c4e6a61abf2174285b0aa4fe4d302e9053bead1760` |
| `BinauraWave-Audio-Asset-Namer-1.2.6-Windows-x64.zip` | 10,710,717 | `8e98bca0604415a33cc9d20facba4cb64dd6d0d0b27701a66926a77fe9f22916` |

`SHA256SUMS.txt` contains these final hashes. Both were recomputed after packaging/acceptance; ZIP CRC/member checks passed and its EXE is identical to the standalone file. The ZIP contains **42 members**, including legal/provenance notices. These files supersede the previous 1.2.6 EXE hash `86d5dfa7ded009cdfdae72e7689bff6524abc6607c7ad51c635a01315cb22a7a`. Preserved old artifacts under ignored `build/previous-release-20261021/` are not release uploads.

## Security investigations and fixes

Full evidence, upstream references, component-use table and advisory applicability are in [RUNTIME_SECURITY.md](RUNTIME_SECURITY.md).

- **Custom/outdated runtime replaced.** The official PSF full-runtime ZIP matched Python.org's manifest SHA-256; `python313.dll` has a valid Python Software Foundation signature. The refreshed runtime incorporates the Python/OpenSSL security fixes missing from the previous candidate.
- **Native origins established.** The PSF SBOM and exact Windows build declarations establish libffi 3.4.4, bzip2 1.0.8, mpdecimal 4.0.0, zlib 1.3.1, Tcl/Tk 8.6.15 and OpenSSL 3.5.9. All **16 DLL/PYD files actually bundled** match hashes from the verified PSF ZIP. The windowed bootloader and both runtime hooks also match the hash-verified official PyInstaller wheel. Build checks reject stale environments, altered/unknown native files and reintroduced `_lzma`.
- **Unused XZ decoder removed.** XZ 5.2.5 has version-applicable index/decoder advisories, but the app provides no archive decoder flow. Excluding `lzma`/`_lzma` removes that code from the EXE instead of shipping it based only on an unreachability assumption. No ad hoc DLL replacement was used.
- **Developer PATH contamination fixed.** The strengthened check initially rejected Microsoft compatibility DLLs collected from an unrelated developer-tool folder. PyInstaller now uses a restricted runtime/Windows PATH and no Python/Tcl path overrides. The final bundle contains neither those foreign API-set/UCRT copies nor XZ.
- **Remaining advisories assessed by actual API use.** zlib 1.3.1 is version-affected by CVE-2026-27171, but the fault requires a negative length to `crc32_combine*`. Exact Python/Tcl bindings and PyInstaller extraction code have no such calls; this API is not exposed through reviewed flows. MP3s remain opaque bytes, scripts are UTF-8 text, and there is no SSL server, certificate/key processing, urllib authentication, archive extraction or input-controlled FFI. No applicable Tcl/Tk/libffi/bzip2/mpdecimal issue was identified in the bounded review. Dormant libraries are not equated with reachable vulnerabilities.
- **Build dependencies checked.** OSV on 2026-10-22 returned no advisories for all seven exact pinned build packages. PyInstaller 6.22.3 is newer than the fix for GHSA-9fxf-4qw3-ghmr. This is not a substitute for the separate native review.

## Licensing status

**Reviewed redistribution requirements addressed for this exact bundle.** The existing collector retains original-code MIT terms, reserved BinauraWave branding, the complete actual interpreter licence (Microsoft/bzip2 conditions included), matching Tcl/Tk/libtommath, OpenSSL/AUTHORS, libffi, zlib, mpdecimal, HACL* and incorporated-Python-code terms, plus build-tool notices. Exact sources and native hashes are in `licenses/README.md` and `licenses/runtime-provenance.json`. XZ's historical notice does not imply it is still bundled. SBOM `NOASSERTION` fields were not treated as permission; actual upstream licence texts were reviewed and retained. No original-code or branding licence scope changed.

## Tests and observed results

| Check | Result / scope |
| --- | --- |
| Application regressions | **PASS: 24 tests** under the refreshed runtime. |
| Release regressions | **PASS: 5 tests**, including checksum tampering/path checks, absent-Git fallback, changed native binary and stale-runtime rejection. |
| Source GUI smoke | **PASS**, contrast, focus, icon/DWM readback, four layouts, load/edit/export/results, About and all four mocked browser targets. |
| Refreshed ZIP workflow | **PASS on Windows 11**, 10 synthetic MP3-labelled byte fixtures matched; unrelated MP3 ignored; title manually edited to `Calm Breathing`; all 10 title-only exports and CSV succeeded. Every output matched original bytes, all original/script hashes remained unchanged, and CSV preserved original/cleaned text, category and track numbers 1–10. These were byte-copy fixtures, not an audio playback test. |
| Independent startup | **PASS**, both ZIP-extracted and direct final EXE, System32-only PATH, no Python/Tcl/Tk environment settings. Direct EXE used an unrelated working folder, which remained empty. GUI subsystem/no console, local logo/icon and dark title bar observed. Test process token was not elevated; EXE manifest is `asInvoker`. |
| New EXE links | **PASS**, live GitHub footer dispatch opened the expected Chrome repository page. All four target callbacks passed source smoke; other three links were not re-clicked in the refreshed EXE. Previous artifact's four live links/native pickers were checked on 2026-10-21. |
| Separate Windows 10 laptop | **Owner-reported PASS**, previous 1.2.6 artifact processed 10 real MP3s with title editing and CSV creation. This is useful independent compatibility evidence, not a claim that the newly rebuilt hash has been tested there. No unreported details such as Python absence or offline conditions are assumed. |
| Native/archive integrity | **PASS**, all 16 native files matched PSF hashes; XZ/foreign compatibility DLLs absent; final notices/ZIP members/checksums verified. Expected optional POSIX, excluded-LZMA and collections alias analysis warnings produced no observed runtime failure. |

Application source files `app.py`, `core.py`, `titles.py`, `theme.py` and `windows_branding.py` are byte-for-byte unchanged from the previously reviewed source. No new accounts, APIs, runtime network requests, telemetry, input mutations or private application dependency was introduced. Local supporting evidence is ignored under `build/security-2026-10-22/` and `build/acceptance-runtime-refresh/`; it is not uploaded or bundled.

## Remaining limitations and recommendation

- **No further confirmed security fix is outstanding** from this investigation. Recommend a quick repeat on the Windows 10 laptop using the **new ZIP/checksum**, since the runtime and artifact hashes changed. That retest is unperformed here; it is a compatibility precaution, not a demonstrated vulnerability.
- The finished EXE remains **unsigned** (`Get-AuthenticodeSignature`: `NotSigned`). SmartScreen/reputation or antivirus warnings remain possible. Signing is optional; no antivirus approval, independent penetration test, fuzzing or system-wide filesystem/network trace is claimed. Signing later requires regenerating the ZIP and both hashes.
- Owner-reported light title bar until focus is accepted as **cosmetic and non-blocking**; native title-bar code was not changed. High-DPI, alternate browser and taskbar/shortcut variations remain normal QA limitations.
- Faithful CSV text may be interpreted as formulas by spreadsheets: import as text. Very large/untrusted scripts may exhaust resources; stale-input stat checks are not adversarial locks. This assessment does not cover a local attacker who can replace the EXE/resources or unknown/future advisories.

## Release handoff and housekeeping

When the owner chooses to publish, attach exactly:

1. `BinauraWave-Audio-Asset-Namer-1.2.6-Windows-x64.zip`
2. `SHA256SUMS.txt`

The ZIP includes the executable and required notices. Do not upload old candidates, build environments, fixtures, internal evidence or a bare EXE without its notices. Binaries stay out of source commits.

README reviewed/updated for the runtime, build safeguards, report links and Windows 10 limitation. CHANGELOG reviewed/updated under 1.2.6; no application version bump was warranted. Relevant tests and packaged acceptance are recorded above. Build/spec/notice collector, release tests, provenance/licence documents and notices are the only changed areas.

No push, publication, tag, GitHub Release, remote/permission change or private BinauraWave application modification was performed. All edits and local commits are confined to the standalone copy.
