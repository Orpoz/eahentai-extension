"""End-to-end test of the EAHentai store/extension against a disposable Suwayomi on :4599."""
import json, sys, urllib.request
import gql

STORE = "https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo/index.pb"
PKG = "eu.kanade.tachiyomi.extension.en.eahentai"
results = []

def check(name, ok, detail=""):
    results.append((name, ok)); print(("PASS " if ok else "FAIL ") + name + ("  -- " + detail if detail else "")); sys.stdout.flush()

def run(query, variables=None):
    r = gql.q(query, variables)
    if r.get("errors"): raise RuntimeError(json.dumps(r["errors"])[:800])
    return r["data"]

stores = run("{extensionStores{nodes{indexUrl}}}")["extensionStores"]["nodes"]
if not any(s["indexUrl"] == STORE for s in stores):
    run("mutation($u:String!){addExtensionStore(input:{indexUrl:$u}){clientMutationId}}", {"u": STORE})
st = run("query($u:String!){extensionStore(indexUrl:$u){name badgeLabel signingKey}}", {"u": STORE})["extensionStore"]
check("store added and parsed", st["name"] == "EAHentai (Orpoz)", json.dumps(st))

run("mutation{fetchExtensions(input:{}){clientMutationId}}")
ext = run("query($p:String!){extension(pkgName:$p){name versionName versionCode isInstalled isNsfw lang apkName}}", {"p": PKG})["extension"]
check("extension listed from store", ext["versionName"] == "1.6.1", json.dumps(ext))

if not ext["isInstalled"]:
    run("mutation($p:String!){updateExtension(input:{id:$p,patch:{install:true}}){extension{isInstalled}}}", {"p": PKG})
ext = run("query($p:String!){extension(pkgName:$p){isInstalled source{nodes{id name lang isNsfw}}}}", {"p": PKG})["extension"]
check("extension installed", ext["isInstalled"], json.dumps(ext["source"]))
src = ext["source"]["nodes"][0]["id"]

def browse(kind, page=1, query=None, filters=None):
    v = {"s": src, "t": kind, "p": page, "q": query, "f": filters}
    return run("""mutation($s:LongString!,$t:FetchSourceMangaType!,$p:Int!,$q:String,$f:[FilterChangeInput!]){
      fetchSourceManga(input:{source:$s,type:$t,page:$p,query:$q,filters:$f}){hasNextPage mangas{id title url thumbnailUrl}}}""", v)["fetchSourceManga"]

pop1 = browse("POPULAR"); pop2 = browse("POPULAR", 2)
check("popular p1", len(pop1["mangas"]) > 0 and pop1["hasNextPage"], f'{len(pop1["mangas"])} items, first={pop1["mangas"][0]["title"][:50]!r}')
check("popular p2 differs", {m["url"] for m in pop1["mangas"]}.isdisjoint({m["url"] for m in pop2["mangas"]}), f'{len(pop2["mangas"])} items')
lat1 = browse("LATEST"); lat2 = browse("LATEST", 2)
check("latest p1", len(lat1["mangas"]) == 42 and lat1["hasNextPage"], lat1["mangas"][0]["title"][:60])
check("latest p2 differs", {m["url"] for m in lat1["mangas"]}.isdisjoint({m["url"] for m in lat2["mangas"]}))
s1 = browse("SEARCH", 1, "blowjob"); s2 = browse("SEARCH", 2, "blowjob")
check("search p1", len(s1["mangas"]) == 42 and s1["hasNextPage"])
check("search p2 differs", {m["url"] for m in s1["mangas"]}.isdisjoint({m["url"] for m in s2["mangas"]}))
s3 = browse("SEARCH", 1, "zzzzqqqxxnonexistent")
check("search no results", len(s3["mangas"]) == 0 and not s3["hasNextPage"])
# filters: position 1 = Sort, 2 = Search in (0 = header)
sa = browse("SEARCH", 1, "carn", [{"position": 2, "selectState": 1}])
check("artist search (exact)", len(sa["mangas"]) > 0 and not sa["hasNextPage"], f'{len(sa["mangas"])} items')
sv = browse("SEARCH", 1, "blowjob", [{"position": 1, "selectState": 4}])
check("sort all-time differs from newest", sv["mangas"][0]["url"] != s1["mangas"][0]["url"], sv["mangas"][0]["title"][:50])
se = browse("SEARCH", 1, "", [{"position": 1, "selectState": 2}])
check("empty query + weekly sort -> popular listing", len(se["mangas"]) > 0)
su = browse("SEARCH", 1, "https://eahentai.com/a/76742")
check("URL search", len(su["mangas"]) == 1 and su["mangas"][0]["url"] == "76742", json.dumps(su["mangas"])[:200])

mid = su["mangas"][0]["id"] if su["mangas"] else lat1["mangas"][0]["id"]
d = run("""mutation($i:Int!){fetchMangaAndChapters(input:{id:$i,fetchManga:true,fetchChapters:true}){
  manga{title artist author genre description status thumbnailUrl realUrl updateStrategy}
  chapters{id name url uploadDate chapterNumber realUrl}}}""", {"i": mid})["fetchMangaAndChapters"]
m = d["manga"]; print(json.dumps(m, indent=1)[:900])
check("details", m["artist"] and m["genre"] and m["status"] == "COMPLETED" and m["realUrl"] == "https://eahentai.com/a/76742")
ch = d["chapters"]; print(json.dumps(ch))
check("single chapter with date", len(ch) == 1 and int(ch[0]["uploadDate"]) > 0)
pages = run("mutation($c:Int!){fetchChapterPages(input:{chapterId:$c}){pages}}", {"c": ch[0]["id"]})["fetchChapterPages"]["pages"]
check("page list", len(pages) == 72, f"{len(pages)} pages, first={pages[0]}")

for i in (0, len(pages) - 1):
    with urllib.request.urlopen("http://127.0.0.1:4599" + pages[i], timeout=120) as r:
        body = r.read()
    check(f"image {i} served by Suwayomi", r.status == 200 and len(body) > 10000 and body[:4] == b"RIFF", f"{r.headers.get('Content-Type')} {len(body)} bytes")

thumb = lat1["mangas"][0]["thumbnailUrl"]
with urllib.request.urlopen("http://127.0.0.1:4599" + thumb, timeout=120) as r:
    tb = r.read()
check("thumbnail served", r.status == 200 and len(tb) > 1000, f"{r.headers.get('Content-Type')} {len(tb)} bytes")

print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
