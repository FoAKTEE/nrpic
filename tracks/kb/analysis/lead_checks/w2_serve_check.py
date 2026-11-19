"""Lead check W2 (wave 2): independent recheck of the serve helper's locator and number check.

Reads the helper's registered statements (checked.jsonl of run kb-20261115-154906-f19880f:
paper, version, file, line ranges, statement text) and, with code of its own (no import of
kb/serve_locate.py or kbtool), checks in the raw store:
  1. the cited file exists under kb-data/raw/arxiv/<key>/<version>/src/ and the lines lie in it;
  2. the numbers the statement quotes (own extraction: decimals, powers of ten, integers >= 10)
     occur in the cited lines, or within three lines.
Then compares the per-statement verdict (all found / all within 3 / some missing) with the
helper's. Writes rows.tsv, summary.json, and a reading sample (sample.txt: the cited lines of
12 statements drawn with seed 20261116) into the output directory, which is in scratch/ and
never committed (it holds paper text). Store files are read as text only.

Usage: python3 -I w2_serve_check.py CHECKED_JSONL KB_DATA [OUTDIR]
(OUTDIR defaults to $NRPIC_RUN_DIR, the run directory nrpic-run gives a local run.)
"""
import collections
import json
import os
import random
import re
import sys

checked, kbdata = sys.argv[1:3]
out = sys.argv[3] if len(sys.argv) > 3 else os.environ["NRPIC_RUN_DIR"]
os.makedirs(out, exist_ok=True)

NUM = re.compile(r"(?<![\w.])(\d+\.\d+|\d+(?:\.\d+)?[eE][-+]?\d+|\d{2,})(?![\w])")


def numbers_of(text):
    """Own extraction: strip line-range locators, then decimals, e-notation, integers >= 10."""
    t = re.sub(r"\bL?\d+-\d+\b", " ", text)          # ranges like 476-487 or L476-487
    t = re.sub(r"\(\d{1,2}\.\d{1,2}\)", " ", t)      # equation numbers like (2.24)
    t = re.sub(r"\b(?:19|20)\d\d\b", " ", t)        # years
    t = re.sub(r"\d{4}\.\d{4,5}", " ", t)           # arXiv ids
    out_ = []
    for m in NUM.finditer(t):
        s = m.group(1)
        if s.isdigit() and int(s) < 10:
            continue
        out_.append(s)
    return sorted(set(out_))


def variants(s):
    """Ways a number may be written in TeX: as is, 1e-3 -> 10^{-3}, 0.19 -> 19\\%."""
    v = {s}
    m = re.fullmatch(r"(\d+(?:\.\d+)?)[eE]([-+]?)0*(\d+)", s)
    if m:
        mant, sign, ex = m.groups()
        sign = "-" if sign == "-" else ""
        v |= {f"10^{{{sign}{ex}}}", f"10^{sign}{ex}"}
        if mant not in ("1", "1.0"):
            v.add(mant)
    if re.fullmatch(r"0\.\d+", s):
        pct = s[2:].lstrip("0") or "0"
        if len(s) == 4:
            v.add(pct)
    return v


def present(s, text):
    for w in variants(s):
        if re.search(r"(?<![\d.])" + re.escape(w) + r"(?!\d)", text):
            return True
    return False


rows = [json.loads(l) for l in open(checked)]
res = []
agree = collections.Counter()
own_class = collections.Counter()
lines_ok = 0
loc_total = 0
for r in rows:
    texts_exact, texts_near = [], []
    for k in r.get("kb", []):
        loc_total += 1
        key = k["paper_id"].replace("/", "_")
        path = os.path.join(kbdata, "raw", "arxiv", key, k["version"], "src", k["file"])
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            L = f.read().split("\n")
        if 1 <= k["lo"] <= k["hi"] <= len(L):
            lines_ok += 1
        texts_exact.append("\n".join(L[k["lo"] - 1:k["hi"]]))
        texts_near.append("\n".join(L[max(0, k["lo"] - 4):k["hi"] + 3]))
    nums = numbers_of(r["text"])
    ex = "\n".join(texts_exact)
    ne = "\n".join(texts_near)
    miss = [n for n in nums if not present(n, ne)]
    exact = all(present(n, ex) for n in nums)
    if not nums:
        mine = "none"
    elif exact:
        mine = "exact"
    elif not miss:
        mine = "near"
    else:
        mine = "missing"
    h = r.get("numbers", {})
    if h.get("n", 0) == 0:
        theirs = "none"
    elif h.get("missing"):
        theirs = "missing"
    elif h.get("found") == h.get("n"):
        theirs = "exact"
    else:
        theirs = "near"
    own_class[mine] += 1
    agree[(theirs, mine)] += 1
    res.append((r["key"], r["owner"], theirs, mine, ",".join(nums), ",".join(miss),
                ",".join(h.get("missing", []))))

with open(os.path.join(out, "rows.tsv"), "w") as f:
    f.write("key\towner\thelper\tlead\tlead_numbers\tlead_missing\thelper_missing\n")
    for t in res:
        f.write("\t".join(t) + "\n")
summary = {"statements": len(rows), "locators": loc_total, "locators_lines_in_file": lines_ok,
           "lead_classes": dict(own_class),
           "helper_vs_lead": {f"{a}->{b}": n for (a, b), n in sorted(agree.items())}}
with open(os.path.join(out, "summary.json"), "w") as f:
    json.dump(summary, f, indent=1)

# reading sample: 12 statements with a resolvable locator, seed 20261116
rng = random.Random(20261116)
pool = [r for r in rows if r.get("kb")]
sample = rng.sample(pool, 12)
with open(os.path.join(out, "sample.txt"), "w") as f:
    for r in sample:
        f.write(f"=== {r['key']} [{r.get('track_label')}] {r['text']}\n")
        for k in r["kb"]:
            key = k["paper_id"].replace("/", "_")
            path = os.path.join(kbdata, "raw", "arxiv", key, k["version"], "src", k["file"])
            with open(path, encoding="utf-8", errors="replace") as g:
                L = g.read().split("\n")
            f.write(f"--- {k['paper_id']} {k['file']}:{k['lo']}-{k['hi']}\n")
            for i in range(max(1, k["lo"] - 1), min(len(L), k["hi"] + 1) + 1):
                f.write(f"{i:5d}| {L[i - 1][:300]}\n")
print(json.dumps(summary, indent=1))
