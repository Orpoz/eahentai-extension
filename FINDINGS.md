# Findings — eahentai.com extension for Suwayomi

_Status: research complete (2026-10-25); implementation in progress. See PROGRESS.md._

## 1. Existing-solution search

### Your current stores
Both stores' `index.pb` files were downloaded, gunzipped and searched for every source name, package and base URL.

| Store | Result |
|---|---|
| `yuzono/cursed-manga-repo` | 4 extensions (E-Hentai, NHentai, Hentai20, Hentai2Read). **No eahentai.** |
| `keiyoushi/extensions` | ~1,660 distinct base URLs. **No eahentai.com, no `i.eahentai.com`, no source named EAHentai.** |

(Keiyoushi's `index.min.json` now only contains an "Outdated App" placeholder; the real index is `index.pb`.)

### Wider search
- GitHub code search for `eahentai`, `eahentai.com`, `i.eahentai.com`, `ea-gallery`: 178 hits, **none of them a Mihon/Tachiyomi extension**.
- Web search for "eahentai tachiyomi/mihon extension": nothing.

Projects that do parse the site (useful as references, but none installable in Suwayomi):

| Project | What it is | Usable in Suwayomi? |
|---|---|---|
| [MapoMagpie/comic-looms](https://github.com/MapoMagpie/comic-looms) `src/platform/matchers/eahentai.ts` | Browser userscript; uses `/api/image/album/{id}` | No |
| [gan-of-culture/get-sauce](https://github.com/gan-of-culture/get-sauce) `extractors/eahentai` | Go CLI downloader; scrapes embedded JSON | No |
| [morg1z/jiyu](https://github.com/morg1z/jiyu) `EAHentaiSource.kt` | Source for a standalone Android app (not the Tachiyomi extension API); HTML scraping, claims no pagination | No |
| hymbz/ComicReadScript | Userscript | No |

**Conclusion:** no existing extension supports eahentai.com, so a custom one is needed.

## 2. Site analysis (verified live, 2026-10-25)
- Next.js app behind Cloudflare. No Cloudflare challenge for plain HTTP clients, no login needed to read.
- Public JSON API at `https://eahentai.com/api/image` (found in the site's own client JS):

| Purpose | Endpoint | Response |
|---|---|---|
| Latest | `/latest/?page={0..}&take=42` | `{items, totalPages, totalResults}` (64k galleries) |
| Popular | `/popular/?page={0..}&take=42&orderby=views_daily\|views_weekly\|views_monthly\|views_alltime` | JSON array |
| Search | `/search/v2/?type=gallery&q={q}&take=42&page={0..}&orderby=date_desc\|views_…` | `{items, totalPages, totalResults}` |
| Artist/parody/character/group | `/entities/albums?type=artist&q={name}&page=0&take=42&orderby=date_desc` | `{items, totalPages, totalResults}` |
| Gallery + pages | `/album/{id}` | JSON array with one album whose `images[]` list every page (`imageUri`, `sort`) |

- Album fields: `albumID, addDt, title, tags, characters, from (parody), author, albumType, thumbnailUri, imageUri, images[]`. Multi-value fields are `|`-separated.
- Images: `https://i.eahentai.com/file/ea-gallery/{imageUri}`. Backblaze B2 behind Cloudflare. Fetched OK with **and without** a Referer. Served as `application/octet-stream` (webp bytes).
- Gallery URL on the site: `https://eahentai.com/a/{id}`.
