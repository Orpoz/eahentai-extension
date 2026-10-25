"""Assemble the extension store (the `repo` branch) from a finished Keiyoushi build.

Reads the `keiyoushi-source-info.json` the build writes next to the APK/JAR, copies the APK, JAR and
icon into the store directory, and writes index.json, index.pb and index.html.

Usage:
  python make_store.py <module build dir> <store dir> <signing cert sha256>
e.g.
  python make_store.py C:/eabuild/extensions-source/src/en/eahentai/build store <sha256>
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_index  # noqa: E402

STORE_BASE_URL = "https://raw.githubusercontent.com/Orpoz/eahentai-extension/repo"
CONTENT_WARNING = {0: "CONTENT_WARNING_UNSPECIFIED", 1: "CONTENT_WARNING_SAFE", 2: "CONTENT_WARNING_MIXED", 3: "CONTENT_WARNING_NSFW"}


def main() -> None:
    build_dir, store_dir, signing_key = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    info = json.loads(next(build_dir.glob("**/keiyoushi-source-info.json")).read_text(encoding="utf-8"))
    apk = next((build_dir / "outputs/apk/release").glob("*.apk"))
    jar = next((build_dir / "outputs/jar/release").glob("*.jar"))
    icon = build_dir.parent / "res/mipmap-xhdpi/ic_launcher.png"
    pkg = info["packageName"]

    for sub in ("apk", "jar", "icon"):
        target = store_dir / sub
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
    shutil.copy2(apk, store_dir / "apk" / apk.name)
    shutil.copy2(jar, store_dir / "jar" / jar.name)
    shutil.copy2(icon, store_dir / "icon" / f"{pkg}.png")

    cw = info["contentWarning"]
    extension = {
        "name": info["name"],
        "packageName": pkg,
        "resources": {
            "apkUrl": f"{STORE_BASE_URL}/apk/{apk.name}",
            "iconUrl": f"{STORE_BASE_URL}/icon/{pkg}.png",
            "jarUrl": f"{STORE_BASE_URL}/jar/{jar.name}",
        },
        "extensionLib": info["extensionLib"],
        "versionCode": str(info["versionCode"]),
        "versionName": info["versionName"],
        "contentWarning": CONTENT_WARNING.get(cw, cw),
        "sources": [
            {
                "id": str(s["id"]),
                "name": s["name"],
                "language": s["lang"],
                "homeUrl": s["baseUrl"],
                **({"mirrorUrls": s["mirrorUrls"]} if s.get("mirrorUrls") else {}),
            }
            for s in info["sources"]
        ],
    }
    index = {
        "name": "EAHentai (Orpoz)",
        "badgeLabel": "EAH",
        "signingKey": signing_key,
        "contact": {"website": "https://github.com/Orpoz/eahentai-extension"},
        "extensionList": {"extensions": [extension]},
    }

    (store_dir / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    make_index.main_args(store_dir / "index.json", store_dir / "index.pb")
    (store_dir / "index.html").write_text(
        '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>apks</title>\n</head>\n<body>\n<pre>\n'
        f'<a href="apk/{apk.name}">Tachiyomi: {info["name"]}</a>\n</pre>\n</body>\n</html>\n',
        encoding="utf-8",
    )
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
