# Findings: eahentai.com extension for Suwayomi

_Last updated 2026-10-25._

## TL;DR / recommendation
No existing Mihon/Tachiyomi extension supports eahentai.com. I built one, **EAHentai v1.6.1**, and published it as an
extension store:

```
https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb
```

It passed a 20-check end-to-end test in a separate Suwayomi v2.4.2366 instance, the same version you run
(§4). It has not been tested on your server.

## 1. Candidates, best to worst

| Rank | Candidate | Supports eahentai.com? | Installable in Suwayomi? | Verdict |
|---|---|---|---|---|
| 1 | **This repo, EAHentai v1.6.1** ([store](https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb)) | Yes, via the site's JSON API | Yes, store + JAR, tested | **Recommended** |
| 2 | [morg1z/jiyu `EAHentaiSource.kt`](https://github.com/morg1z/jiyu) | Yes | **No**. It's a source for a standalone Android app, not the Tachiyomi extension API. It scrapes HTML and assumes no pagination, which is wrong: the API paginates. | Reference only |
| 3 | [MapoMagpie/comic-looms](https://github.com/MapoMagpie/comic-looms) `matchers/eahentai.ts` | Yes (gallery pages) | No, browser userscript | Reference only; confirmed `/api/image/album/{id}` |
| 4 | [gan-of-culture/get-sauce](https://github.com/gan-of-culture/get-sauce) `extractors/eahentai` | Yes (download) | No, Go CLI | Reference only |
| 5 | hymbz/ComicReadScript | Partly | No, userscript | Not useful |
| — | `keiyoushi/extensions` store | **No** | — | ~1,660 base URLs checked; no eahentai |
| — | `yuzono/cursed-manga-repo` store | **No** | — | 4 extensions (E-Hentai, NHentai, Hentai20, Hentai2Read) |

How I searched (verified):
- Downloaded and gunzipped both of your stores' `index.pb`, then searched every extension name, package and source
  `homeUrl` for `eahentai`/`eah`/`ea-`. Nothing found, including under other names. Keiyoushi's `index.min.json` now only holds
  an "Outdated App" placeholder; the real list is in `index.pb`.
- GitHub code search for `eahentai`, `eahentai.com`, `i.eahentai.com` and `ea-gallery` (178 / 123 / 5 / 946 hits). The only
  site-specific code is the four projects in the table. The rest are blocklists and link lists.
- Web search ("eahentai tachiyomi/mihon extension", "eahentai github extension"): nothing relevant.

Alternate domains: the site only references `eahentai.com` and `i.eahentai.com` (image CDN). I found no mirror domains.

## 2. Site analysis (verified live 2026-10-25)
- Next.js app behind Cloudflare. No Cloudflare challenge for plain HTTP clients. Reading needs no login.
- Public JSON API under `https://eahentai.com/api/image`. I found the paths in the site's own client JavaScript and checked
  each one live:

| Purpose | Endpoint (page is 0-based, `take=42`) | Shape |
|---|---|---|
| Latest | `/latest/?page=&take=` | `{items,totalPages,totalResults}`. 64k galleries |
| Popular | `/popular/?page=&take=&orderby=views_daily\|views_weekly\|views_monthly\|views_alltime` | array |
| Search | `/search/v2/?type=gallery&q=&page=&take=&orderby=date_desc\|views_*` | `{items,totalPages,…}` |
| Artist/parody/character | `/entities/albums?type=artist\|parody\|character&q=<exact name>&…` | `{items,totalPages,…}` (`type=group` returned nothing) |
| Gallery + pages | `/album/{id}` | array of 1 album, `images[]` with `imageUri` + `sort` |

- Images: `https://i.eahentai.com/file/ea-gallery/<imageUri>` (Backblaze B2 behind Cloudflare). They load with or without a
  Referer and need no cookies or tokens. They're served as `application/octet-stream` (webp bytes); Suwayomi detects the type
  and serves them as `image/webp`.
- The HTML home page's `?page=N` links render the same content server-side, which is probably why jiyu concluded there was no
  pagination. The JSON API does paginate.

## 3. Implementation
- Built on the **current Keiyoushi template** (`KeiSource`, lib 1.6, KSP-generated source metadata) from
  `keiyoushi/extensions-source@f1edb03`. It uses `ext-bootstrap.py` scaffolding and follows its CONTRIBUTING.md
  (regular-class DTOs, `parseAs`, `keiyoushi.network.get`, `rateLimit`, `UpdateStrategy.ONLY_FETCH_ONCE`).
- Package `eu.kanade.tachiyomi.extension.en.eahentai`, source id `6252565297586539202`, `contentWarning = NSFW`.
- No multisrc theme fits (the site is a custom Next.js app), so it's a standalone source of about 180 lines.
- Rate limit: 4 requests/second per client.

## 4. Testing
Test bed: a **separate** Suwayomi-Server v2.4.2366 (official release jar, SHA-256 verified against the release asset digest).
It ran with its own data root (`C:\eabuild\suwa-test\root`), bound to `127.0.0.1:4599`, with web UI, tray and KCEF off.
The extension was installed **from the published GitHub URL**, not from local files.

Script: `tools/test/e2e.py`. Result: **20/20 passed** (run twice, the second time after an uninstall/reinstall):

| Check | Result |
|---|---|
| Store URL added; name/badge/signing key parsed | PASS |
| Extension listed (1.6.1, NSFW, en) | PASS |
| Installed from store (Suwayomi downloaded the **JAR** from `jarUrl`) | PASS |
| Popular p1 (42) / p2 distinct | PASS / PASS |
| Latest p1 (42, newest first) / p2 distinct | PASS / PASS |
| Search p1 (42) / p2 distinct / no-results query | PASS / PASS / PASS |
| "Search in: Artist" filter (exact name) | PASS |
| Sort filter changes ordering | PASS |
| Empty query + sort → popular listing | PASS |
| URL search (`/a/76742`, also `/a/76741/3`) | PASS |
| Details: title, artist, genres, description, COMPLETED, ONLY_FETCH_ONCE, WebView URL | PASS |
| One chapter with upload date | PASS |
| Page list (72 pages for gallery 76742) | PASS |
| First and last page images served through Suwayomi (`image/webp`, real bytes) | PASS / PASS |
| Thumbnail served | PASS |

Other verification:
- Hosted `index.pb`, APK, JAR and icon were downloaded anonymously from `raw.githubusercontent.com` and compared
  byte-for-byte with the local build: identical.
- `make_index.py` reproduces Keiyoushi's published `index.pb` byte-for-byte from their `index.json`.
- APK signature: `apksigner verify` shows certificate SHA-256 `ba737e3a…1fa1`, matching the store's `signingKey`.

## 5. Compatibility
- Your server, inspected read-only: Suwayomi-Server **v2.4.2366** (r2366), the latest stable release (2026-09-30).
  It already runs lib-1.6 extensions from Keiyoushi.
- Suwayomi v2.4.2366 source: `LIB_VERSION_MIN = 1.3`, `LIB_VERSION_MAX = 1.6`. It parses `index.pb` including Keiyoushi's
  `jarUrl` (field 501) and installs the JAR when one is present.
- **The APK alone does not work in Suwayomi.** Uploading the lib-1.6 APK makes Suwayomi convert it with dex2jar, and
  browsing then fails with a JVM `VerifyError`. Keiyoushi's own `asmhentai-v1.6.13.apk` fails the same way
  (`ClassCastException`), so this is a general limitation of lib-1.6 APKs on Suwayomi, not of this build. The store uses the
  JAR, so this doesn't affect the normal install. The APK is for Mihon on Android, where it hasn't been tested.
- The store's `signingKey` is my own key, not Keiyoushi's. Suwayomi v2.4.2366 doesn't check store signing keys on
  install (verified in source: `Extension.installExtension`). Mihon would show it as a separate, untrusted signer.

## 6. Safety
- **Network destinations of the built JAR**: only `https://eahentai.com` (API) and `https://i.eahentai.com` (images).
  I checked by extracting every URL string from the shipped JAR. Keiyoushi's `core` mentions other URLs only in docs and
  examples, and R8 strips them from the build.
- No analytics, no third-party services, no WebView, no cookies or credentials. The site itself uses Google Analytics and ad
  scripts in the browser, but the extension never loads HTML or JavaScript; it only calls the JSON API.
- Third parties involved: Cloudflare (in front of both hosts) and Backblaze B2 (image storage behind Cloudflare). Both are
  the site's own infrastructure.
- Source vs package: the published APK and JAR are exactly the files built from the source in `extension/eahentai`
  (byte-compared after download). Release builds are not reproducible bit-for-bit across machines. To trust a package
  without trusting me, rebuild from source (BUILDING.md).
- Content: the site hosts adult material; some galleries carry categories you may want to blacklist in Suwayomi or on the
  site. The extension adds no filtering of its own.

## 7. Uncertainties and limits
- Not tested on **your** server (by design). The isolated instance runs the same version, so I expect the same behavior,
  but your settings (proxy, FlareSolverr, auth) weren't reproduced.
- The JSON API is undocumented. If the site changes it, the extension breaks until it's updated.
- The site's `/latest` list and the popular counts come from the site and weren't checked for completeness.
- Artist/parody/character search needs the exact lower-case name the site uses (e.g. `carn`, `bocchi the rock`). Free-text
  search already matches tags, artists and titles.
- No login features (bookmarks, lists). They aren't needed for reading.

## 8. Your steps
1. In Suwayomi, add the extension store `https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb`
   (the same place you added the Keiyoushi and yuzono stores).
2. Refresh extensions, show NSFW extensions if they're hidden, and install **EAHentai 1.6.1**.
3. Open **Sources → EAHentai** and try Popular, Latest, a search, and reading a gallery.
4. If something fails, the server log line with `EAHentai` or `eahentai.com` is the most useful thing to send back.
