BinauraWave Audio Asset Namer @VERSION@ — Windows x64

Free audio organisation utility, developed by BinauraWave.

RUN
Extract this ZIP to any normal folder, then double-click
BinauraWave-Audio-Asset-Namer.exe. No installation, Python, pip or other
dependencies are needed. The utility works offline; only clicking a website
link opens your default browser. Allow a moment for first startup.

USE
1. Select the folder containing your numbered Audacity MP3 exports.
2. Select the matching UTF-8 script, with one clip per blank-line-separated
   paragraph. Export numbers must run from 1 with no gaps or duplicates.
3. Load the preview. Check every mapping and edit titles as needed.
4. Confirm copying. By default, title-only MP3s and manifest.csv appear in Named
   inside the selected audio folder. If it exists, choose another output folder,
   explicitly replace recognised exports, or cancel. The full path is shown.

Original MP3s and scripts remain unchanged. Audio is copied without
re-encoding. CSV retains the original track numbers and full script text.
Titles must be unique (case insensitive). Alternative destinations never
silently overwrite files. Replacement needs a matching session manifest,
unchanged prior audio and a local fixed Windows NTFS drive; it never guesses
ownership or removes unrelated files. Confirm replacement explicitly.
New files and verified recovery copies are prepared before live files change.
Previous exports remain in .audio-namer-backup-<id>/previous. Review all results.

If replacement is interrupted, keep .audio-namer-transaction-* and any lock
file, close the app and choose a different folder. A pending transaction blocks
further replacement. When transaction.json has backups_verified=true, copy
previous/ into a separate empty folder for recovery; never overwrite unrelated
files blindly. If false, inspect retained live exports instead of trusting an
incomplete backup. Do not edit output files concurrently. Hardware failure or
every power-loss scenario cannot be guaranteed recoverable. See the source
README for full recovery instructions. Original recordings/scripts are retained.
Automatic title suggestions are offline heuristics; review them yourself.

Organise and name your audio clips locally. No account required.
Your audio files and scripts remain on your computer.

WINDOWS
Prepared for 64-bit Windows 10/11. This release is tested on Windows 11;
1.2.6 was also tested on a separate Windows 10 laptop. Native dark title
bar is requested where supported. File pickers and message dialogs follow
Windows styling. No administrator rights are required for normal use.
The one-file runtime temporarily extracts its bundled libraries into the
Windows temporary directory; user audio, CSV, staging and recovery output go only to the audio
folder's Named folder or the alternative output folder you selected. The runtime removes its extraction on normal exit.

This initial package is unsigned. Signing and publishing are not part of
this release preparation. Original source code is MIT-licensed. BinauraWave branding/trademark rights
are reserved separately. Read LICENSE, BRANDING.md and THIRD_PARTY_NOTICES.md
and the bundled third-party notices for the applicable terms.

Website: https://binaurawave.com/
Create Audio Sessions: https://binaurawave.com/binaurawave_app/
Help & Support: https://binaurawave.com/feedback/

Official source and downloads:
https://github.com/cmderdanblackburno7/audio_asset_namer/releases
Verify downloads with the release's SHA256SUMS.txt, for example in PowerShell:
Get-FileHash .\BinauraWave-Audio-Asset-Namer.exe -Algorithm SHA256
Compare all 64 hexadecimal characters with the matching filename's checksum.
Checksums detect changes when obtained from a trusted release; they are not
code signatures or antivirus guarantees. Do not disable Windows protections.
Report bugs with synthetic examples; do not share personal audio or scripts.
