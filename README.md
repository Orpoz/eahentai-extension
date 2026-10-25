# eahentai-extension

A Mihon/Tachiyomi-compatible extension for **eahentai.com**, published as an extension store for
[Suwayomi-Server](https://github.com/Suwayomi/Suwayomi-Server). (18+ content; the extension is flagged NSFW.)

No existing extension supports this site (see [FINDINGS.md](FINDINGS.md)), so this one was built against the current
Keiyoushi extension template (lib 1.6) and the site's public JSON API.

**Status:** v1.6.1 passed a 20-check end-to-end test in a separate Suwayomi v2.4.2366 instance. It has not been tested on
your own server yet.

## Install in Suwayomi

This repository is **private**, so Suwayomi can't read a store from it. Install the JAR file directly instead (tested,
19/19 checks):

1. Get `tachiyomi-en.eahentai-v1.6.1.jar` (on this PC: `C:\eabuild\store\jar\`; also in the private `repo` branch).
2. In Suwayomi's web UI, go to **Extensions** and use the install-from-file/external-extension button (or POST it to
   `/api/v1/extension/install` as form field `file`). Choose the `.jar`, **not** the `.apk`.
3. The source appears as **EAHentai** (English, NSFW). Updates are installed the same way, with a newer JAR.

### Store install (only works if the repository is public)
1. In Suwayomi's web UI, open the settings page where you added your other stores (the extension repository/store list,
   stored server-side as `server.extensionStores`) and add a new entry.
2. Paste:

   ```
   https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb
   ```

3. Go to **Extensions**, refresh, enable NSFW/18+ display if it's hidden, and install **EAHentai** (en, 1.6.1).
4. The source shows up under **Sources → English → EAHentai**.

Fallback: the APK and JAR are also in the [`repo` branch](https://github.com/Orpoz/eahentai-extension/tree/repo).
For Suwayomi, use the **JAR**. Lib-1.6 APKs, including Keiyoushi's own, fail in Suwayomi's APK→JAR conversion (see FINDINGS.md §5).

## Features
| Feature | How |
|---|---|
| Popular | `/api/image/popular` (today's views), paginated |
| Latest | `/api/image/latest`, paginated |
| Search | title/tag search with sort (newest, popular today/week/month/all-time) |
| Artist / parody / character | "Search in" filter (needs the exact name, as shown on the site) |
| Open by URL | paste `https://eahentai.com/a/12345` (or a reader URL) into search |
| Details | title, artist, tags + type as genres, parody/characters/page count in description |
| Reader | one "Gallery" chapter; pages loaded directly from `i.eahentai.com` |

## Repository layout
| Path | What |
|---|---|
| `extension/eahentai/` | Extension module (drop into `keiyoushi/extensions-source/src/en/`) |
| `tools/build.sh` | Build a signed release APK + JAR |
| `tools/make_store.py`, `tools/make_index.py` | Generate the store (`index.json`, `index.pb`, `index.html`) |
| `tools/publish.sh` | Regenerate and push the store branch |
| `tools/test/` | End-to-end test against a disposable Suwayomi |
| branch `repo` | The published store |

Building and updating: [BUILDING.md](BUILDING.md). Progress log: [PROGRESS.md](PROGRESS.md).

Not affiliated with eahentai.com, Keiyoushi, Mihon or Suwayomi. License: Apache-2.0 (see NOTICE.md).
