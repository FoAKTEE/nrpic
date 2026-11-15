#!/usr/bin/env python3
"""Track locators -> knowledge-base locators, a number check at the source, and the loading
of served statements into the claims table (brief 12.8; kb serve package of wave 2).

A track cites a paper as `<file>:<line>` of the stored source
`kb-data/raw/arxiv/<id_>/<version>/src/<file>`. The knowledge base keeps the flattened text
`kb-data/build/tex/<id_>/flat.tex` and a source map offset -> (file, line, column), and
every section, chunk, equation and figure carries a character range of flat.tex. This
module inverts the source map, so a track locator becomes: the version, the character range
in flat.tex, the section number and title, the chunk ids, and the equation and figure
numbers that overlap the lines.

Downloads are data: a source file is only read as text, never executed or compiled.
Writes (claims) happen inside the writer lock `locks/kb-writer.lock`.

    python3 -I kb/serve_locate.py resolve <id> <file> <lines> [--expect TOKEN ...]
    python3 -I kb/serve_locate.py check <statements.jsonl> <out.jsonl> [--db PATH]
    python3 -I kb/serve_locate.py load <checked.jsonl> <out_ids.tsv> [--dry-run]

<lines> is "491", "491-493" or "491,493,667-673". The `check` input has one JSON object per
line with at least key, paper_id, file, ranges ([[lo, hi], ...]) and text; `check` adds the
fields `kb` (one resolution per range) and `numbers` (number check) and writes them out.
`load` writes the claims of a checked file (origin `served:<key>`, idempotent: an existing
claim with that origin is updated in place and keeps its id).
"""
import argparse
import bisect
import json
import math
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbtool import db as _db  # noqa: E402
from kbtool import lock as _lock  # noqa: E402
from kbtool import paths as _paths  # noqa: E402

TOOL = "kb/serve_locate.py 1"


# ---------------------------------------------------------------- source map inversion
class PaperMap:
    """The source map of one paper, inverted: (file, line) -> flat.tex offsets."""

    def __init__(self, lay, pid):
        key = pid.replace("/", "_")
        d = os.path.join(lay.build, "tex", key)
        with open(os.path.join(d, "sourcemap.json")) as f:
            sm = json.load(f)
        with open(os.path.join(d, "flat.tex"), encoding="utf-8", errors="replace") as f:
            self.flat_len = len(f.read())
        self.starts = [s for s, _, _, _ in sm]
        self.by_line = {}                      # (file, line) -> [start, end)
        for i, (s, fname, line, _col) in enumerate(sm):
            e = sm[i + 1][0] if i + 1 < len(sm) else self.flat_len
            k = (fname, line)
            if k in self.by_line:
                a, b = self.by_line[k]
                self.by_line[k] = (min(a, s), max(b, e))
            else:
                self.by_line[k] = (s, e)
        self.files = sorted({k[0] for k in self.by_line})
        self.lines_of = {}
        for (fname, line) in self.by_line:
            self.lines_of.setdefault(fname, []).append(line)
        for v in self.lines_of.values():
            v.sort()

    def match_file(self, fname):
        """The file name as the source map writes it (tracks write `main.tex` or `./main.tex`;
        an \\input file may be written without its directory)."""
        if fname in self.lines_of:
            return fname
        norm = fname.lstrip("./")
        for f in self.files:
            if f == norm or f.lstrip("./") == norm:
                return f
        for f in self.files:
            if os.path.basename(f) == os.path.basename(norm):
                return f
        return None

    def span(self, fname, lo, hi):
        """[start, end) in flat.tex of lines lo..hi of fname; lines that the flattening
        dropped (comments, blank) map to the nearest kept line inside the range, else to the
        nearest kept line after it, else before it. Returns (start, end, how)."""
        f = self.match_file(fname)
        if f is None:
            return None, None, "file-not-in-flat"
        lines = self.lines_of[f]
        i, j = bisect.bisect_left(lines, lo), bisect.bisect_right(lines, hi)
        if i < j:
            a = min(self.by_line[(f, ln)][0] for ln in lines[i:j])
            b = max(self.by_line[(f, ln)][1] for ln in lines[i:j])
            return a, b, "exact" if (lines[i] == lo and lines[j - 1] == hi) else "partial"
        if i < len(lines) and lines[i] - hi <= 5:
            a, b = self.by_line[(f, lines[i])]
            return a, b, f"next-line {lines[i]}"
        if i > 0 and lo - lines[i - 1] <= 5:
            a, b = self.by_line[(f, lines[i - 1])]
            return a, b, f"previous-line {lines[i - 1]}"
        return None, None, "lines-not-in-flat (comment, preamble or beyond the end)"


def overlap(con, sql, args, a, b):
    return [r for r in con.execute(sql, args) if r[-2] is not None and r[-2] < b and r[-1] > a]


def resolve(con, lay, pid, fname, lo, hi, cache=None):
    """One track locator -> knowledge-base locator (dict)."""
    out = {"paper_id": pid, "file": fname, "lo": lo, "hi": hi}
    p = con.execute("SELECT version, flat_sha256, parse_status FROM papers WHERE paper_id=?",
                    (pid,)).fetchone()
    if not p:
        out["status"] = "paper-not-ingested"
        return out
    out["version"], out["flat_sha256"], out["parse_status"] = p
    key = pid.replace("/", "_")
    src = os.path.join(lay.raw_arxiv, key, p[0] or "", "src")
    path = os.path.join(src, fname)
    out["source_file_exists"] = os.path.isfile(path) and os.path.realpath(path).startswith(os.path.realpath(src))
    if out["source_file_exists"]:
        with open(path, "rb") as f:
            n = f.read().count(b"\n") + 1
        out["source_lines"] = n
        out["lines_in_file"] = hi <= n
    try:
        pm = cache[pid] if cache is not None and pid in cache else PaperMap(lay, pid)
        if cache is not None:
            cache[pid] = pm
    except OSError:
        out["status"] = "no-build-files"
        return out
    a, b, how = pm.span(fname, lo, hi)
    out["map"] = how
    if a is None:
        out["status"] = "unmapped"
        return out
    out["flat"] = [a, b]
    secs = overlap(con, "SELECT section_id, number, title, level, char_start, char_end FROM sections "
                   "WHERE paper_id=?", (pid,), a, b)
    # innermost section containing the start of the span
    inner = [s for s in secs if s[4] <= a < s[5]]
    inner.sort(key=lambda s: (s[5] - s[4]))
    s0 = inner[0] if inner else (secs[0] if secs else None)
    out["section"] = ({"section_id": s0[0], "number": s0[1], "title": s0[2]} if s0 else None)
    ch = overlap(con, "SELECT chunk_id, kind, char_start, char_end FROM chunks WHERE paper_id=? "
                 "AND kind != 'comment'", (pid,), a, b)
    out["chunks"] = [{"chunk_id": c[0], "kind": c[1]} for c in ch]
    eq = overlap(con, "SELECT eq_id, number, label, char_start, char_end FROM equations WHERE paper_id=?",
                 (pid,), a, b)
    out["equations"] = [{"eq_id": e[0], "number": e[1], "label": e[2]} for e in eq]
    fg = overlap(con, "SELECT fig_id, kind, number, label, char_start, char_end FROM figures WHERE paper_id=?",
                 (pid,), a, b)
    out["figures"] = [{"fig_id": g[0], "kind": g[1], "number": g[2], "label": g[3]} for g in fg]
    out["status"] = "resolved"
    return out


def kb_locator(r):
    """Short text form: 'kb:2108.11967v2 sec 3.1 chunk 123 eq (12) flat 1000-1200'."""
    if r.get("status") != "resolved":
        return f"kb:{r['paper_id']} {r.get('status')}"
    s = r.get("section")
    parts = [f"kb:{r['paper_id']}{r.get('version') or ''}"]
    if s:
        parts.append(f"sec {s['number'] or '-'}")
    if r["chunks"]:
        parts.append("chunk " + ",".join(str(c["chunk_id"]) for c in r["chunks"][:3]))
    nums = [e["number"] for e in r["equations"] if e["number"]]
    if nums:
        parts.append("eq (" + "),(".join(nums[:4]) + ")")
    figs = [f"{g['kind'] or 'fig'} {g['number']}" for g in r["figures"] if g["number"]]
    if figs:
        parts.append(", ".join(figs[:2]))
    parts.append(f"flat {r['flat'][0]}-{r['flat'][1]}")
    return " ".join(parts)


# ---------------------------------------------------------------- number check
_ID_RE = re.compile(r"\b(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?\b")
_RUN_RE = re.compile(r"\b[A-Za-z]+(?:-[A-Za-z0-9]+)*-\d{8}-\d{6}-[0-9a-f]{7}\b")
_LOC_RE = re.compile(r"[\w./-]*\.(?:tex|ltx|bbl|bib|py|md|cpp|hpp)(?::\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*)?")
_NUM_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?:\s*(?:e|E)\s*([-+]?\d+))?(?![\w])")


def claim_numbers(text):
    """Numbers a statement quotes, as (float, significant digits, written form). Integers
    below 10, line numbers, identifiers and run ids are not counted (they match anywhere)."""
    t = _RUN_RE.sub(" ", text)
    t = _LOC_RE.sub(" ", t)
    t = _ID_RE.sub(" ", t)
    t = re.sub(r"\bL\d+(?:\s*-\s*\d+)?", " ", t)
    out = []
    for m in _NUM_RE.finditer(t):
        mant, exp = m.group(1), m.group(2)
        try:
            v = float(mant) * (10.0 ** int(exp) if exp else 1.0)
        except (ValueError, OverflowError):
            continue
        digits = len(mant.replace(".", "").lstrip("0")) or 1
        if exp is None and "." not in mant and v < 10:
            continue
        out.append((v, digits, m.group(0)))
    return out


_TEX_SCI = re.compile(r"(\d+(?:\.\d+)?)\s*(?:\\times|\\cdot|\\,\\times\\,|\s[x×]\s)\s*10\s*\^\s*\{?\s*([-−+]?\s*\d+)\s*\}?")
_TEX_POW = re.compile(r"(?<![\d.])10\s*\^\s*\{?\s*([-−+]?\s*\d+)\s*\}?")
_TEX_E = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)[eE]([-+]?\d+)(?![\w])")
_TEX_NUM = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)")
_TEX_PCT = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:\\%|\\,\\%|\s?per\s?cent|\s?percent)")


def source_numbers(tex):
    """Every number a TeX passage writes, in the forms 1.2, 1.2e-3, 1.2\\times 10^{-3}, 10^{-3},
    with thin spaces and braces in digit groups removed ({,} and \\, between digits)."""
    t = re.sub(r"(?<=\d)\{,\}(?=\d)", ".", tex)
    t = re.sub(r"(?<=\d)\\[,!; ](?=\d)", "", t)
    t = t.replace("−", "-")
    vals = []
    for m in _TEX_SCI.finditer(t):
        try:
            vals.append(float(m.group(1)) * 10.0 ** int(m.group(2).replace(" ", "")))
        except (ValueError, OverflowError):
            pass
    for m in _TEX_POW.finditer(t):
        try:
            vals.append(10.0 ** int(m.group(1).replace(" ", "")))
        except (ValueError, OverflowError):
            pass
    for m in _TEX_E.finditer(t):
        try:
            vals.append(float(m.group(1)) * 10.0 ** int(m.group(2)))
        except (ValueError, OverflowError):
            pass
    for m in _TEX_NUM.finditer(t):
        vals.append(float(m.group(1)))
    for m in _TEX_PCT.finditer(t):                      # 19\% is the fraction 0.19 as well
        vals.append(float(m.group(1)) / 100.0)
    return vals


def _round_sig(x, d):
    if x == 0:
        return 0.0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (d - 1))


def number_found(v, digits, pool):
    """v (written with `digits` significant digits) equals a source number rounded to that
    many digits, or a source number equals v exactly; the sign is ignored."""
    for y in pool:
        y = abs(y)
        if y == v or (y and math.isclose(_round_sig(y, digits), v, rel_tol=1e-9)):
            return True
        if v and math.isclose(y, v, rel_tol=1e-9):
            return True
    return False


def read_lines(lay, pid, version, fname, lo, hi):
    key = pid.replace("/", "_")
    src = os.path.realpath(os.path.join(lay.raw_arxiv, key, version or "", "src"))
    path = os.path.realpath(os.path.join(src, fname))
    if not path.startswith(src + os.sep) or not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        lines = f.read().decode("utf-8", errors="replace").split("\n")
    lo = max(lo, 1)
    return "\n".join(lines[lo - 1:hi])


def check_numbers(lay, st, kbres, pad=3):
    """Fraction of the statement's numbers found in the located lines (exact range) and
    within `pad` lines around each range (near)."""
    if st.get("numbers_from") == "values" or st.get("label"):
        nums = claim_numbers(" ".join(st.get("values", [])))
    else:
        nums = claim_numbers(st.get("text", ""))
    if not nums:
        return {"n": 0}
    exact_pool, near_pool = [], []
    for r in kbres:
        v = r.get("version")
        if not r.get("source_file_exists"):
            continue
        t = read_lines(lay, r["paper_id"], v, r["file"], r["lo"], r["hi"])
        tn = read_lines(lay, r["paper_id"], v, r["file"], r["lo"] - pad, r["hi"] + pad)
        if t is not None:
            exact_pool += source_numbers(t)
        if tn is not None:
            near_pool += source_numbers(tn)
    found = [number_found(v, d, exact_pool) for v, d, _ in nums]
    near = [number_found(v, d, near_pool) for v, d, _ in nums]
    return {"n": len(nums), "found": sum(found), "near": sum(near),
            "missing": [w for (v, d, w), ok in zip(nums, near) if not ok]}


def check_expect(lay, kbres, expect, pad=0):
    """Literal tokens (TeX as written) that must occur in the located lines."""
    text = ""
    for r in kbres:
        if r.get("source_file_exists"):
            t = read_lines(lay, r["paper_id"], r.get("version"), r["file"], r["lo"] - pad, r["hi"] + pad)
            text += (t or "") + "\n"
    squash = re.sub(r"\s+", "", text)
    return {tok: (tok in text or re.sub(r"\s+", "", tok) in squash) for tok in expect}


# ---------------------------------------------------------------- commands
def parse_lines(s):
    out = []
    for part in re.split(r"\s*,\s*", s.strip()):
        m = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", part)
        if not m:
            raise ValueError(f"bad line range {part!r}")
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        if hi < lo:                                     # "1101-03" style abbreviations
            hi = int(str(lo)[:len(str(lo)) - len(m.group(2))] + m.group(2))
        out.append([lo, hi])
    return out


def cmd_resolve(a):
    lay = _paths.layout()
    con = _db.connect_ro(a.db or _db.open_for_read(lay))
    res = [resolve(con, lay, a.id, a.file, lo, hi) for lo, hi in parse_lines(a.lines)]
    for r in res:
        print(kb_locator(r))
        print(json.dumps(r, indent=1))
    if a.expect:
        print(json.dumps(check_expect(lay, res, a.expect, pad=a.pad)))
    return 0


def cmd_check(a):
    lay = _paths.layout()
    con = _db.connect_ro(a.db or _db.open_for_read(lay))
    cache = {}
    n = 0
    with open(a.inp) as f, open(a.out, "w") as g:
        for line in f:
            if not line.strip():
                continue
            st = json.loads(line)
            res = [resolve(con, lay, st["paper_id"], st["file"], lo, hi, cache) for lo, hi in st["ranges"]]
            st["kb"] = res
            st["kb_locator"] = "; ".join(kb_locator(r) for r in res)
            st["numbers"] = check_numbers(lay, st, res, pad=a.pad)
            if st.get("expect"):
                st["expect_found"] = check_expect(lay, res, st["expect"], pad=st.get("expect_pad", 0))
            g.write(json.dumps(st) + "\n")
            n += 1
    print(f"checked {n} statements")
    return 0


LABELS = {"VERIFIED": "fulltext", "JUDGEMENT": "judgement", "TO VERIFY": "to_verify",
          "BACKGROUND": "background", "REFUTED": "refuted"}


def decide_label(st):
    """(label, reason) of a checked statement [JUDGEMENT of the serve package]:
    - the label the entry gives, else the track's label mapped by LABELS;
    - 'fulltext' needs: every locator resolved with its lines inside the source file, every
      quoted number found within the pad around the lines, every expected token found;
      otherwise it becomes 'to_verify' (the reason names what failed);
    - 'to_verify' becomes 'fulltext' when the entry asks for it (promote_on_numbers,
      promote_on_expect) and the numbers are all in the exact lines / the tokens all found."""
    res = st.get("kb") or []
    ok = bool(res) and all(r.get("status") == "resolved" and r.get("lines_in_file", False) for r in res)
    nums = st.get("numbers") or {"n": 0}
    exp = st.get("expect_found") or {}
    label = st.get("label") or LABELS.get(st.get("track_label", ""), "to_verify")
    why = []
    if not ok:
        why.append("locator not resolved: " + ", ".join(sorted({str(r.get("status")) + "/" + str(r.get("map"))
                                                                for r in res})) if res else "no locator")
    if nums.get("n") and nums.get("near", 0) < nums["n"]:
        why.append("numbers not at the locator: " + " ".join(nums.get("missing", [])))
    if exp and not all(exp.values()):
        why.append("tokens not at the locator: " + " ".join(k for k, v in exp.items() if not v))
    if label == "fulltext" and why:
        return "to_verify", "; ".join(why)
    if label == "to_verify" and ok and not why:
        if st.get("promote_on_numbers") and nums.get("n") and nums.get("found") == nums["n"]:
            return "fulltext", "all numbers found in the located lines"
        if st.get("promote_on_expect") and exp and all(exp.values()):
            return "fulltext", "all expected tokens found in the located lines"
    return label, "; ".join(why)


def claim_row(st, run_id, at):
    """The claims row of a checked statement (label by decide_label)."""
    r0 = st["kb"][0] if st.get("kb") else {}
    label, why = decide_label(st)
    st["label_final"], st["label_reason"] = label, why
    chunk = next((c["chunk_id"] for c in r0.get("chunks", []) if c["kind"] != "comment"), None)
    flat = r0.get("flat") or [None, None]
    loc = "; ".join(f"{r['file']}:{r['lo']}" + (f"-{r['hi']}" if r["hi"] != r["lo"] else "")
                    for r in st.get("kb", []))
    loc = f"{st['paper_id']} {st.get('version') or r0.get('version') or ''} {loc} | {st.get('kb_locator', '')}"
    if label == "fulltext":
        vb = (f"{st.get('owner')} read at the source ({st.get('doc')}); locator resolved and checked by kb "
              f"run {run_id}" + (f" ({why})" if why else ""))
    elif label == "refuted":
        vb = f"counter-evidence of {st.get('owner')}: {st.get('evidence', '?')}; locator checked by kb run {run_id}"
    else:
        vb = None
    if label == "to_verify" and why:
        loc += f" | kb check: {why}"
    return dict(text=st["text"], kind=st.get("kind", "result"), paper_id=st["paper_id"], locator=loc,
                chunk_id=chunk, quote_start=flat[0], quote_end=flat[1], label=label,
                origin=f"served:{st['key']}", track_tags=st.get("track_tags") or st.get("owner"),
                verified_by=vb, verified_at=at if vb else None)


def cmd_load(a):
    lay = _paths.layout()
    rows = []
    with open(a.inp) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    at = _db.utcnow()
    out = []
    if a.dry_run:
        for st in rows:
            out.append((st["key"], None, claim_row(st, a.run_id, at)))
    else:
        with _lock.writer_lock(lay, what="serve claims"):
            con = _db.connect_rw(lay.db_work)
            try:
                con.execute("BEGIN")
                for st in rows:
                    c = claim_row(st, a.run_id, at)
                    old = con.execute("SELECT claim_id FROM claims WHERE origin=?", (c["origin"],)).fetchone()
                    cols = list(c)
                    if old:
                        con.execute("UPDATE claims SET " + ", ".join(f"{k}=?" for k in cols) + " WHERE claim_id=?",
                                    [c[k] for k in cols] + [old[0]])
                        cid = old[0]
                    else:
                        cur = con.execute(f"INSERT INTO claims({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                                          [c[k] for k in cols])
                        cid = cur.lastrowid
                    out.append((st["key"], cid, c))
                _db.log(con, "serve-claims", os.path.basename(a.inp), "ok",
                        f"{len(rows)} claims (origin served:*), run {a.run_id}, {TOOL}")
                con.commit()
            except Exception:
                con.rollback()
                raise
            finally:
                con.close()
    with open(a.out, "w") as g:
        g.write("key\tclaim_id\tlabel\tkind\tpaper_id\tchunk_id\tlocator\n")
        for key, cid, c in out:
            g.write(f"{key}\t{cid}\t{c['label']}\t{c['kind']}\t{c['paper_id']}\t{c['chunk_id']}\t{c['locator']}\n")
    print(f"{'would load' if a.dry_run else 'loaded'} {len(out)} claims -> {a.out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="kb/serve_locate.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("resolve")
    p.add_argument("id")
    p.add_argument("file")
    p.add_argument("lines")
    p.add_argument("--expect", nargs="*")
    p.add_argument("--pad", type=int, default=0)
    p.add_argument("--db")
    p = sub.add_parser("check")
    p.add_argument("inp")
    p.add_argument("out")
    p.add_argument("--pad", type=int, default=3)
    p.add_argument("--db")
    p = sub.add_parser("load")
    p.add_argument("inp")
    p.add_argument("out")
    p.add_argument("--run-id", default="unregistered")
    p.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    return {"resolve": cmd_resolve, "check": cmd_check, "load": cmd_load}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
