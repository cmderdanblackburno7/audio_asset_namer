# Reporting security concerns

Processing is local and offline. No account, registration, API key, analytics or telemetry is required. The app opens only fixed public URLs, only after explicit link clicks. It never uploads your audio or scripts.

For a suspected security problem, contact [BinauraWave Help & Support](https://binaurawave.com/feedback/) with the version, operating system, a description and a small synthetic reproduction. Do not include real audio/scripts, credentials, private paths or other personal information. Do not post sensitive exploit details in a public issue before contacting the maintainer. If GitHub offers private vulnerability reporting for this repository, that is another option; its availability is not assumed here. No response-time guarantee or bug-bounty programme is offered.

Report ordinary bugs in [GitHub Issues](https://github.com/cmderdanblackburno7/audio_asset_namer/issues). Review any screenshot/error output before posting it.

Download releases only from [the official repository](https://github.com/cmderdanblackburno7/audio_asset_namer/releases), compare SHA-256 checksums, and retain the ZIP's legal notices. Current builds are unsigned: SmartScreen/reputation prompts and antivirus false positives are possible. No statement here certifies a binary as malware-free or universally trusted. Do not disable Windows security protections to run an unexpected file.

This utility is intended for files you select on your own machine with normal user privileges. It is not a security boundary against another process modifying your files concurrently or a hardened processor for hostile multi-gigabyte input. Existing stat/identity checks are workflow protection, not cryptographic locking. CSV retains original text, so import it as text in spreadsheet software to avoid formula interpretation.

The release review checks known advisories as of a stated date; absence from an advisory database is not proof of absence of vulnerabilities. Bundled runtimes, clean-Windows checks and the final licence inventory must be reviewed for each release. See `RELEASE_READINESS.md` for the current release's actual results and outstanding checks.
