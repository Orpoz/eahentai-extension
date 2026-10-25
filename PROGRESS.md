# Progress

## Current state (2026-10-25, updated)
**Repository is private by the user's choice.** It was briefly made public by mistake (about 30 minutes; no forks/stars) and
then reverted. The store URL therefore does not resolve. Install by uploading the JAR (README.md), which is tested 19/19.

## Earlier state
**Done, waiting for the user to test on their own server.** EAHentai v1.6.1 is built, published as a store on the `repo`
branch, and passed 20/20 end-to-end checks in an isolated Suwayomi v2.4.2366.

Store URL: `https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb`

## Completed
- [x] Repo setup. It is private by the owner's choice. I wrongly switched it to public; it is now reverted to private.
- [x] Existing-solution search: none (both user stores, GitHub code search, web). FINDINGS.md §1.
- [x] Site/API analysis. FINDINGS.md §2.
- [x] Extension written on the Keiyoushi lib-1.6 template; release build signed with a project key.
- [x] `index.pb` encoder, verified byte-identical against Keiyoushi's index.
- [x] Store published; hosted files byte-identical to the build.
- [x] Isolated Suwayomi test: 20/20 pass (store → install JAR → browse/search/details/pages/images).
- [x] APK fallback investigated: lib-1.6 APKs (Keiyoushi's too) fail under Suwayomi's dex2jar; the JAR is the supported path.
- [x] Network-destination audit of the shipped JAR.

## Test results
See FINDINGS.md §4. Re-run with `python tools/test/e2e.py` against a disposable instance on :4599.

## Blockers
- None. The user's own server was not touched (read-only check of version and extension filenames only).

## Next steps
- User: add the store URL in Suwayomi and install EAHentai (README.md).
- If the site's API changes: update `extension/eahentai`, bump `versionCode`, follow BUILDING.md.

## Local environment (for resuming on this machine)
- `C:\eabuild\extensions-source`: Keiyoushi checkout containing `src/en/eahentai`.
- `C:\eabuild\android-sdk`: SDK. `C:\eabuild\signing`: keystore and passwords (**back up; never commit**).
- `C:\eabuild\store`: `repo` branch clone. `C:\eabuild\suwa-test`: disposable Suwayomi (jar, `root/` data dir, `run.sh`).
