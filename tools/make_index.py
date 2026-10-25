"""Encode an extension-store index (JSON) into the gzipped protobuf `index.pb` read by Mihon/Suwayomi.

Schema: tools/index.proto (copied from keiyoushi/extensions-source, which derives it from
mihonapp/tachiyomix). This is a dependency-free encoder for that schema; it reproduces the
deterministic output of the official protobuf runtime (fields in number order, proto3 defaults
omitted, `optional` fields kept when set).

Usage: python make_index.py index.json index.pb
"""

import gzip
import json
import sys

CONTENT_WARNING = {
    "CONTENT_WARNING_UNSPECIFIED": 0,
    "CONTENT_WARNING_SAFE": 1,
    "CONTENT_WARNING_MIXED": 2,
    "CONTENT_WARNING_NSFW": 3,
}


def varint(n: int) -> bytes:
    if n < 0:
        n += 1 << 64
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def key(field: int, wire: int) -> bytes:
    return varint((field << 3) | wire)


def f_bytes(field: int, data: bytes) -> bytes:
    return key(field, 2) + varint(len(data)) + data


def f_str(field: int, value, optional: bool = False) -> bytes:
    if value is None or (value == "" and not optional):
        return b""
    return f_bytes(field, value.encode("utf-8"))


def f_int(field: int, value) -> bytes:
    value = int(value or 0)
    return key(field, 0) + varint(value) if value else b""


def contact(c: dict) -> bytes:
    return f_str(1, c.get("website")) + f_str(2, c.get("discord"), optional=True)


def resources(r: dict) -> bytes:
    return f_str(1, r.get("apkUrl")) + f_str(2, r.get("iconUrl")) + f_str(501, r.get("jarUrl"))


def source(s: dict) -> bytes:
    out = f_int(1, s.get("id")) + f_str(2, s.get("name")) + f_str(3, s.get("language")) + f_str(4, s.get("homeUrl"))
    for mirror in s.get("mirrorUrls", []):
        out += f_bytes(5, mirror.encode("utf-8"))
    return out + f_str(7, s.get("message"), optional=True)


def extension(e: dict) -> bytes:
    cw = e.get("contentWarning", 0)
    cw = CONTENT_WARNING[cw] if isinstance(cw, str) else int(cw)
    out = (
        f_str(1, e.get("name"))
        + f_str(2, e.get("packageName"))
        + f_bytes(3, resources(e.get("resources", {})))
        + f_str(4, e.get("extensionLib"))
        + f_int(5, e.get("versionCode"))
        + f_str(6, e.get("versionName"))
        + f_int(7, cw)
    )
    for s in e.get("sources", []):
        out += f_bytes(8, source(s))
    return out


def index(i: dict) -> bytes:
    out = f_str(1, i.get("name")) + f_str(2, i.get("badgeLabel")) + f_str(3, i.get("signingKey"))
    if "contact" in i:
        out += f_bytes(4, contact(i["contact"]))
    if "extensionList" in i:
        exts = b"".join(f_bytes(1, extension(e)) for e in i["extensionList"].get("extensions", []))
        out += f_bytes(101, exts)
    elif "extensionListUrl" in i:
        out += f_str(102, i["extensionListUrl"], optional=True)
    return out


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    with open(dst, "wb") as f:
        f.write(gzip.compress(index(data), mtime=0))


if __name__ == "__main__":
    main()
