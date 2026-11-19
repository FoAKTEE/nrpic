"""Lead check L2: independent scan of kb-data/raw/arxiv against the brief manifest.

Reads only directory names, the meta records and the bytes of source.bin (hashing and the
first bytes after gunzip of the first 64 KiB). Nothing in the store is executed.
Usage: python3 -I store_scan.py <arx_raw.tsv> <kb-data root>
"""
import gzip, hashlib, io, json, os, sys, zlib, collections

man = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip()]
root = sys.argv[2]
raw = os.path.join(root, "raw", "arxiv")
meta = os.path.join(root, "meta", "arxiv")
ids = {m[0] for m in man}
store = set(os.listdir(raw))
res = collections.Counter()
rows = []
for pid, grp, pri in man:
    key = pid.replace("/", "_")
    d = os.path.join(raw, key)
    if not os.path.isdir(d):
        res["missing"] += 1; rows.append((pid, "missing")); continue
    vers = sorted(v for v in os.listdir(d) if v.startswith("v"))
    if not vers:
        res["noversion"] += 1; rows.append((pid, "noversion")); continue
    sb = os.path.join(d, vers[-1], "source.bin")
    h = hashlib.sha256(open(sb, "rb").read()).hexdigest()
    try:
        rec = json.load(open(os.path.join(meta, key + ".json")))
    except Exception:
        rec = {}
    shaok = rec.get("sha256") == h
    head = open(sb, "rb").read(65536)
    kind = "other"
    if head[:2] == b"\x1f\x8b":
        try:
            dec = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(head, 4096)
        except Exception:
            dec = b""
        if dec[:2] == b"%!":
            kind = "gzip-ps"
        elif len(dec) > 262 and dec[257:262] == b"ustar":
            kind = "gzip-tar"
        else:
            kind = "gzip-other"
    elif head[:4] == b"%PDF":
        kind = "pdf"
    res[(kind, shaok)] += 1
    if not shaok or kind not in ("gzip-tar", "gzip-other"):
        rows.append((pid, kind, "sha_ok" if shaok else "sha_MISMATCH", vers[-1]))
extras = sorted(s for s in store if s.replace("_", "/", 1) not in ids and s not in ids)
print("manifest", len(man), "store dirs", len(store))
for k, v in sorted(res.items(), key=str):
    print(" ", k, v)
print("notable:", rows)
print("extras", len(extras), extras)
