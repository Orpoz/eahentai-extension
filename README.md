# EAHentai Extension

A Mihon/Tachiyomi-compatible extension for [eahentai.com](https://eahentai.com), distributed as an extension repository for [Suwayomi Server](https://github.com/Suwayomi/Suwayomi-Server).

> [!WARNING]
> This extension provides access to adult content and is marked as NSFW.

The extension is based on the Keiyoushi extension template (lib 1.6) and uses the site's public JSON API. Compatibility research and implementation notes are available in [FINDINGS.md](FINDINGS.md).

## Installation

### Extension repository

1. Open the extension repository settings in the Suwayomi web interface.
2. Add the following repository URL:

   ```text
   https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb
   ```

3. Open **Extensions** and refresh the repository list.
4. Enable the display of NSFW extensions if necessary.
5. Install **EAHentai**.
6. The source will appear under **Sources → English → EAHentai**.

### Manual installation

1. Download the latest JAR from the [`repo` branch](https://github.com/Orpoz/eahentai-extension/tree/repo).
2. In the Suwayomi web interface, open **Extensions** and select the option to install an external extension from a file.
3. Select the `.jar` file—not the `.apk`.

The JAR can also be uploaded to `/api/v1/extension/install` as the `file` form field.

Updates may be installed using either the extension repository or a newer JAR. Suwayomi users should use the JAR because lib 1.6 APKs are incompatible with Suwayomi's APK-to-JAR conversion. Additional details are documented in [FINDINGS.md](FINDINGS.md).

## Features

| Feature | Description |
|---|---|
| Popular | Browses galleries by today's views using `/api/image/popular` |
| Latest | Browses recently added galleries using `/api/image/latest` |
| Search | Searches titles and tags, with sorting by newest or popularity |
| Filtered search | Searches by artist, parody, or character using the exact site name |
| Open by URL | Accepts gallery and reader URLs such as `https://eahentai.com/a/12345` |
| Gallery details | Displays the title, artist, tags, type, parody, characters, and page count |
| Reader | Exposes each gallery as a single chapter with pages loaded from `i.eahentai.com` |
| Pagination | Supports paginated popular, latest, and search results |

## Repository layout

| Path | Description |
|---|---|
| `extension/eahentai/` | Extension module for `keiyoushi/extensions-source/src/en/` |
| `tools/build.sh` | Builds signed release APK and JAR artifacts |
| `tools/make_store.py` | Generates extension repository metadata |
| `tools/make_index.py` | Generates repository index files |
| `tools/publish.sh` | Regenerates and publishes the repository branch |
| `tools/test/` | End-to-end tests using a disposable Suwayomi instance |
| `repo` branch | Published extension repository and release artifacts |

Build and release instructions are available in [BUILDING.md](BUILDING.md). Development history is recorded in [PROGRESS.md](PROGRESS.md).

## Disclaimer

This project is not affiliated with eahentai.com, Keiyoushi, Mihon, or Suwayomi.

Licensed under the Apache License 2.0. See [NOTICE.md](NOTICE.md) for attribution and additional notices.
