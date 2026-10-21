# Retained third-party terms — runtime review 2026-10-22

The reviewed release runtime is official PSF CPython 3.13.17 Windows AMD64, with OpenSSL 3.5.9 and Tcl/Tk 8.6.15. `runtime-provenance.json` records its official ZIP/manifest/SBOM URLs, ZIP checksum and exact native-file hashes. Hashes cover the complete PSF runtime's native files; only the subset identified in the final EXE is redistributed.

Retained verbatim upstream terms:

- `TCL-8.6.txt`: https://raw.githubusercontent.com/tcltk/tcl/core-8-6-15/license.terms
- `TK-8.6.txt`: https://raw.githubusercontent.com/tcltk/tk/core-8-6-15/license.terms
- `TCL-LIBTOMMATH-LICENSE.txt`: https://raw.githubusercontent.com/tcltk/tcl/core-8-6-15/libtommath/LICENSE
- `OPENSSL-LICENSE.txt` / `OPENSSL-AUTHORS.md`: https://github.com/openssl/openssl/tree/openssl-3.5.9
- `ZLIB-LICENSE.txt`: https://raw.githubusercontent.com/madler/zlib/v1.3.1/LICENSE (Python and Tcl's bundled zlib 1.3.1).
- `LIBFFI-LICENSE.txt`: https://raw.githubusercontent.com/libffi/libffi/v3.4.4/LICENSE
- `LIBMPDEC-LICENSE.txt`: https://raw.githubusercontent.com/python/cpython-source-deps/mpdecimal-4.0.0/COPYRIGHT.txt
- `HACL-LICENSE.txt`: copyright/licence comment from https://raw.githubusercontent.com/python/cpython/v3.13.17/Modules/_hacl/Hacl_Hash_SHA2.c
- `PYTHON-INCORPORATED.rst`: https://raw.githubusercontent.com/python/cpython/v3.13.17/Doc/license.rst, including Python's additional incorporated-code notices (HACL*, Unicode and others). References to the interpreter licence are fulfilled by the collected full `PYTHON.txt`.
- `LIBLZMA-COPYING.txt`: https://raw.githubusercontent.com/tukaani-project/xz/v5.2.5/COPYING, retained as historical attribution. **The reviewed executable excludes `_lzma`/`lzma` and does not redistribute liblzma.**

Exact libffi 3.4.4 / XZ 5.2.5 provenance is now established by the PSF SBOM and Windows build declarations, rather than inferred for the previous custom runtime. SBOM `NOASSERTION` fields are not licence grants; the actual upstream terms above govern redistribution. Microsoft runtime conditions and bzip2 terms are included in the actual interpreter's complete `LICENSE.txt`, copied into release ZIPs as `licenses/PYTHON.txt`.

These files retain third-party terms and are not covered by the utility's original-code MIT licence. BinauraWave artwork is separately reserved. This directory contains notices/metadata, not third-party implementation source. The existing build-only collector includes it without network requests. See `RUNTIME_SECURITY.md` and `RELEASE_READINESS.md` for applicability and final build evidence. Review matching terms/hashes when dependencies change.
