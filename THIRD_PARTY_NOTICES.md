# Third-party licensing

## Source repository

The original utility source, tests and build scripts are MIT-licensed under `LICENSE`. No third-party implementation source, Python environment, audio collection or commercial application code is vendored here. The artwork and trademarks are separately reserved in `BRANDING.md`. The application imports Python's standard library, including Tkinter; it has no pip runtime requirements.

## Python/Tk runtime in executable releases

A PyInstaller executable includes third-party runtime components that are **not relicensed under MIT**:

- **CPython:** PSF Licence Version 2 plus retained historical/incorporated-software terms. See [Python's licensing documentation](https://docs.python.org/3.12/license.html). The release-notice collector copies the complete `LICENSE.txt` from the actual build interpreter, including its incorporated-software notices. CPython is bundled without modifications to its source.
- **Tcl/Tk:** permissive BSD-style terms requiring retained copyright and licence notices. Verbatim upstream Tcl 8.6 and Tk 8.6 terms are in `licenses/`, with source references. Tcl/Tk is bundled without source modifications. Different runtime versions require reviewing their matching notices.
- **PyInstaller:** GPL-2.0-or-later with a bootloader/bundling exception, and Apache-2.0 for specified files. The [upstream exception](https://pyinstaller.org/en/stable/license.html) permits executable bundles under the application's chosen licence, subject to dependency terms; it does not force this original application source to become GPL. This project does not modify or distribute the PyInstaller development tool itself. Its installed COPYING notice is retained in release notices for clarity.

The audited Python 3.12 executable also includes OpenSSL/libcrypto, libffi, zlib, libmpdec, liblzma/bzip2 and Microsoft runtime components, directly or through extension modules. Additional upstream notices are retained in `licenses/`; their provenance and remaining version checks are recorded there. The complete interpreter licence includes bzip2 and Microsoft redistribution conditions. These bundled components keep their own terms; the utility's MIT licence does not override them. See `RELEASE_READINESS.md` for the audited artifact inventory and any outstanding runtime provenance checks.

## Build-only dependency review

Pinned packages in `requirements-build.txt` are installed in an ignored build environment, not vendored or shipped as development tools:

| Package | Upstream terms |
| --- | --- |
| PyInstaller | GPL-2.0-or-later with bundling exception; specified files Apache-2.0 |
| pyinstaller-hooks-contrib | Standard hooks GPL-2.0-or-later; runtime hooks Apache-2.0 |
| altgraph | MIT |
| packaging | Apache-2.0 OR BSD-2-Clause |
| pefile | MIT |
| pywin32-ctypes | BSD-3-Clause |
| setuptools | MIT; vendored components retain their own notices |

These identifications were checked against the pinned installed package metadata/licence files and [community hooks terms](https://github.com/pyinstaller/pyinstaller-hooks-contrib/blob/master/LICENSE). Standard build hooks are not application code; any bundled runtime hooks retain their own notices.

## Release obligations

`release_notices.py` runs only during a build. It copies this project's MIT/branding notices, the actual Python licence, Tcl/Tk terms and the installed build packages' licence/notice files into the ZIP. It fails if required runtime notices are missing. It performs no network requests. The runtime application does not import this helper.

Before publishing a binary, inspect the actual bundled DLL/runtime inventory against the licences from that build environment, including any additional Python extension libraries or Microsoft runtime redistributables. Adding a dependency or changing Python/Tcl/Tk versions requires repeating the licence review. The existing ignored 1.2.4 binaries predate this source/notice preparation and must not be uploaded as current releases. Build a fresh release with the current scripts and review its notices first.
