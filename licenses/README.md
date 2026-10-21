# Retained third-party terms

- `TCL-8.6.txt`: verbatim Tcl 8.6.12 terms from https://raw.githubusercontent.com/tcltk/tcl/core-8-6-12/license.terms
- `TK-8.6.txt`: verbatim Tk 8.6.12 terms from https://raw.githubusercontent.com/tcltk/tk/core-8-6-12/license.terms

These notice texts retain their upstream terms and are not covered by the utility's MIT licence. No Tcl/Tk implementation source is vendored. The build-only notice collector adds the full licence from the actual Python interpreter and installed build packages to release ZIPs. Review matching terms if runtime versions change.

## Additional bundled-runtime notices (1.2.6 audit)

- `OPENSSL-LICENSE.txt` and `OPENSSL-AUTHORS.md`: verbatim OpenSSL 3.5.8 files from https://github.com/openssl/openssl/tree/openssl-3.5.8 (matching the actual runtime's reported version). OpenSSL copyright 1998–2026 The OpenSSL Authors.
- `ZLIB-LICENSE.txt`: verbatim https://raw.githubusercontent.com/madler/zlib/v1.3.2/LICENSE (matching `zlib.ZLIB_RUNTIME_VERSION`).
- `LIBMPDEC-LICENSE.txt`: verbatim copyright/licence comment from https://raw.githubusercontent.com/python/cpython/v3.12.14/Modules/_decimal/libmpdec/mpdecimal.h (matching libmpdec 2.5.1).
- `LIBFFI-LICENSE.txt`: verbatim https://raw.githubusercontent.com/libffi/libffi/v3.4.4/LICENSE.
- `LIBLZMA-COPYING.txt`: verbatim https://raw.githubusercontent.com/tukaani-project/xz/v5.2.5/COPYING.

The last two are the baseline versions declared in CPython 3.12.14's `PCbuild/python.props`; exact libffi/liblzma provenance in this custom Windows runtime still needs confirmation before public binary release. Their presence here does not certify that runtime provenance. See `RELEASE_READINESS.md` for the final build inventory and limitations. Microsoft runtime terms are retained in the actual interpreter's full `PYTHON.txt` notice inside the release ZIP. The collector automatically includes this entire directory; it does not fetch these files at build time or startup.
