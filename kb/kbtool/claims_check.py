"""K8 check of a claim's locators against the stored sources (independent of the track).

For every locator: the paper is in the store (`kb-data/raw/arxiv/<id_>/<v>/src`), the file
exists there (exact relative path, else a unique base name), the lines exist; the line
range is mapped to a character range of `build/tex/<id_>/flat.tex` through
`sourcemap.json` and to the chunks that overlap it. Then the numbers of the claim's text
(decimals, powers of ten, integers >= 10; not the locators, ids, run ids or our own
bracketed remarks) are looked for in the cited lines (window of +-3 lines), as written or
rounded to the digits the claim quotes.

Files under kb-data/raw are read as text and nothing else: never executed, imported or
compiled. Standard library only.
"""
import json
import math
import os
import re
from dataclasses import dataclass, field

WINDOW = 3                       # lines of slack around a cited range
YEAR = re.compile(r"^(19|20)\d\d$")


# ---------------------------------------------------------------- numbers
_STRIP_CLAIM = [
    re.compile(r"\[[^\]]*\]"),                                        # our remarks, labels
    re.compile(r"\b[A-Za-z]-?[A-Za-z-]*-\d{8}-\d{6}-[0-9a-f]{7}\b"),  # run ids
    re.compile(r"(?:arXiv:)?(?:[a-z-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?"),  # arXiv ids
    re.compile(r"`[^`]*`"),                                           # file names, code
    re.compile(r"\((?:[a-z]+\s*,?\s*)?L?\d{1,5}(?:\s*-\s*L?\d{1,5})?(?:\s*[,;]\s*(?:[a-z]+\s*)?L?\d{1,5}(?:\s*-\s*L?\d{1,5})?)*\)"),
    re.compile(r"(?<![A-Za-z0-9_])L\d{1,5}(?:\s*-\s*L?\d{1,5})?"),
    re.compile(r"\blines?\s+\d[\d\s,-]*"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),                             # dates
    re.compile(r"\b(?:brief|Brief|row|rows|CHARTER|charter)\s+(?:lines?\s+)?\d+(?:\s*-\s*\d+)?"),  # brief lines
    re.compile(r"^\s*\d+\s*\|"),                                        # first cell: a brief line
    re.compile(r"\b(?:v|eq\.?\s*|Eq\.?\s*|Fig\.?\s*|Table\s+|Sec\.?\s*|section\s+)\(?\d+\)?", re.I),
    re.compile(r"\b[A-Za-z]+\d+[A-Za-z]*\b"),                         # names such as A1, G14, 3D, ST85
    re.compile(r"\b(?:sub)?(?:script|index)\b"),
]

RE_TIMES10 = re.compile(r"(\d+(?:\.\d+)?)\s*(?:x|×|\*|\\times|\\cdot)\s*10\s*\^\s*\(?\{?\s*([-+−]?\s*\d+)\s*\}?\)?")
RE_POW10 = re.compile(r"(?<![\d.])10\s*\^\s*\(?\{?\s*([-+−]?\s*\d+)\s*\}?\)?")
RE_EXP = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)[eE]([-+]?\d+)(?!\w|\.\d)")
RE_THOUS = re.compile(r"(?<![\d.])\d{1,3}(?:(?:,|\{,\})\d{3})+(?![\d])")
RE_DEC = re.compile(r"(?<![\d.])\d*\.\d+")
RE_INT = re.compile(r"(?<![\d.])\d+(?![\d.])")


@dataclass
class Num:
    value: float
    text: str                 # as written (digits)
    decimals: int             # digits after the point as written (for rounding)
    kind: str                 # 'dec', 'pow', 'int'


def _num_tokens(s):
    """Numbers of a string, consuming composite forms first."""
    out = []
    taken = []

    def free(a, b):
        return all(b <= x or a >= y for x, y in taken)

    for m in RE_TIMES10.finditer(s):
        mant, ex = float(m.group(1)), int(m.group(2).replace("−", "-").replace(" ", ""))
        out.append(Num(mant * 10.0 ** ex, m.group(0), -1, "pow"))
        taken.append(m.span())
    for m in RE_EXP.finditer(s):
        if free(*m.span()):
            out.append(Num(float(m.group(1)) * 10.0 ** int(m.group(2)), m.group(0), -1, "pow"))
            taken.append(m.span())
    for m in RE_POW10.finditer(s):
        if free(*m.span()):
            out.append(Num(10.0 ** int(m.group(1).replace("−", "-").replace(" ", "")), m.group(0), -1, "pow"))
            taken.append(m.span())
    for m in RE_THOUS.finditer(s):
        if free(*m.span()):
            v = int(m.group(0).replace("{,}", "").replace(",", ""))
            out.append(Num(float(v), m.group(0), 0, "int"))
            taken.append(m.span())
    for m in RE_DEC.finditer(s):
        if free(*m.span()):
            t = m.group(0)
            out.append(Num(float(t), t, len(t.split(".")[1]), "dec"))
            taken.append(m.span())
    for m in RE_INT.finditer(s):
        if free(*m.span()):
            out.append(Num(float(m.group(0)), m.group(0), 0, "int"))
            taken.append(m.span())
    return out


def claim_numbers(text):
    """Checkable numbers of a claim (our wording)."""
    s = text
    for r in _STRIP_CLAIM:
        s = r.sub(" ", s)
    s = re.sub(r"[A-Za-z]\^\(?\d+(?:/\d+)?\)?", " ", s)           # exponents of symbols: r^(-9/4), k^2
    s = re.sub(r"\(\d+/\d+\)", " ", s)                              # fractions (2/5)
    s = re.sub(r"\b\d+/\d+\b", " ", s)
    out = []
    for n in _num_tokens(s):
        if n.kind == "int" and (n.value < 10 or YEAR.match(n.text)):
            continue
        if n.kind == "dec" and n.value == 0:
            continue
        out.append(n)
    return out


def tex_numbers(tex):
    """Numbers of TeX source lines (braces and spacing commands removed)."""
    s = tex.replace("{,}", ",").replace("\\,", "").replace("\\!", "").replace("~", " ")
    s = re.sub(r"\\(?:mathrm|rm|text|textrm)\{([^{}]*)\}", r"\1", s)
    s = s.replace("$", " ")
    return _num_tokens(s)


def number_found(n, cands, window_text):
    """'exact', 'rounded' or ''."""
    if n.kind in ("dec", "int") and re.search(rf"(?<![\d.]){re.escape(n.text)}(?![\d])", window_text):
        return "exact"
    for c in cands:
        if c.value == 0 and n.value == 0:
            return "exact"
        if c.value != 0 and abs(c.value - n.value) <= 1e-9 * max(abs(c.value), abs(n.value)):
            return "exact"
    if n.kind == "dec" and n.decimals > 0:
        for c in cands:
            if c.kind == "dec" and c.decimals > n.decimals and round(c.value, n.decimals) == round(n.value, n.decimals):
                return "rounded"
    if n.kind == "pow":                                     # "1e4" against "10^4" or "10000"
        for c in cands:
            if c.value > 0 and n.value > 0 and abs(math.log10(c.value) - math.log10(n.value)) < 1e-9:
                return "exact"
    return ""


# ---------------------------------------------------------------- store access (read only)
def key_of(pid):
    return pid.replace("/", "_")


def versions_in_store(raw_arxiv, pid):
    d = os.path.join(raw_arxiv, key_of(pid))
    try:
        vs = [v for v in os.listdir(d) if re.fullmatch(r"v\d+", v) and os.path.isdir(os.path.join(d, v, "src"))]
    except FileNotFoundError:
        return []
    return sorted(vs, key=lambda v: int(v[1:]))


def find_file(src, name):
    """Relative path of `name` under src: exact, else a unique base-name match."""
    if not name:
        return None, "no file named"
    if ".." in name.split("/") or name.startswith("/"):
        return None, "unsafe path"
    p = os.path.join(src, name)
    if os.path.isfile(p) and not os.path.islink(p):
        return name, ""
    base = os.path.basename(name).lower()
    hits = []
    for root, dirs, files in os.walk(src, followlinks=False):
        for f in files:
            if f.lower() == base:
                hits.append(os.path.relpath(os.path.join(root, f), src))
    if len(hits) == 1:
        return hits[0], "found by base name"
    if hits:
        return None, f"base name ambiguous ({len(hits)})"
    return None, "file not in source"


_LINES_CACHE = {}


def read_lines(path):
    if path not in _LINES_CACHE:
        with open(path, "rb") as f:
            data = f.read(64 << 20)
        _LINES_CACHE[path] = data.decode("utf-8", errors="replace").split("\n")
        if len(_LINES_CACHE) > 200:
            _LINES_CACHE.pop(next(iter(_LINES_CACHE)))
    return _LINES_CACHE[path]


@dataclass
class LocResult:
    paper_id: str = ""
    version: str = ""
    file: str = ""
    line_start: int = 0
    line_end: int = 0
    resolved: bool = False
    problem: str = ""
    notes: list = field(default_factory=list)
    flat_start: int = None
    flat_end: int = None
    chunk_ids: list = field(default_factory=list)
    window: str = ""         # never stored, never printed: used for the number check only
    comment_only: bool = False   # every cited line is a TeX comment (brief 12.4: low reliability)


class Store:
    """Read-only view of the stored sources and of the database rows a check needs."""

    def __init__(self, raw_arxiv, build_tex, con=None):
        self.raw_arxiv = raw_arxiv
        self.build_tex = build_tex
        self.con = con
        self._main = {}
        self._smap = {}

    def main_file(self, pid):
        if pid not in self._main:
            mt, ver = None, None
            if self.con is not None:
                r = self.con.execute("SELECT main_tex, version FROM papers WHERE paper_id=?", (pid,)).fetchone()
                if r:
                    mt, ver = r
            self._main[pid] = (mt, ver)
        return self._main[pid]

    def sourcemap(self, pid):
        if pid not in self._smap:
            p = os.path.join(self.build_tex, key_of(pid), "sourcemap.json")
            try:
                self._smap[pid] = json.load(open(p))
            except (FileNotFoundError, ValueError):
                self._smap[pid] = None
        return self._smap[pid]

    def flat_range(self, pid, relfile, a, b):
        """Character range of flat.tex holding lines a..b of relfile (None if unmapped)."""
        sm = self.sourcemap(pid)
        if not sm:
            return None, None
        starts = [e[0] for e in sm if e[1] == relfile and a <= e[2] <= b]
        if not starts:
            return None, None
        lo = min(starts)
        nxt = [e[0] for e in sm if e[0] > max(starts)]
        hi = min(nxt) if nxt else None
        if hi is None:
            mt = os.path.join(self.build_tex, key_of(pid), "flat.tex")
            try:
                hi = os.path.getsize(mt)
            except OSError:
                hi = lo
        return lo, hi

    def chunks_overlapping(self, pid, lo, hi):
        if self.con is None or lo is None:
            return []
        return [r[0] for r in self.con.execute(
            "SELECT chunk_id FROM chunks WHERE paper_id=? AND kind!='comment' AND char_start < ? AND char_end > ? "
            "ORDER BY char_start", (pid, hi, lo))]

    def resolve(self, loc):
        """LocResult of one claims_parse.Locator."""
        tried = [loc.paper_id] + [i for i in getattr(loc, "alt_ids", ()) if i and i != loc.paper_id]
        last = None
        for k, pid in enumerate(tried):
            r = self._resolve_in(loc, pid, loc.version if k == 0 else "")
            if r.resolved:
                if k > 0:
                    r.notes.append(f"file found in {pid}, not in {loc.paper_id}")
                return r
            last = last or r
        return last

    def _resolve_in(self, loc, pid, want_ver):
        r = LocResult(paper_id=pid, line_start=loc.line_start, line_end=loc.line_end)
        if not pid:
            r.problem = "no paper in context"
            return r
        vs = versions_in_store(self.raw_arxiv, pid)
        if not vs:
            r.problem = "paper not in store"
            return r
        ver = want_ver if want_ver in vs else vs[-1]
        if want_ver and want_ver not in vs:
            r.notes.append(f"note says {want_ver}, store has {','.join(vs)}; used {ver}")
        r.version = ver
        src = os.path.join(self.raw_arxiv, key_of(pid), ver, "src")
        name = loc.file
        if not name:
            mt, _ = self.main_file(pid)
            name = mt or ""
            if not name:
                r.problem = "no file named and no main file known"
                return r
        rel, how = find_file(src, name)
        if not rel:
            r.problem = how
            return r
        if how:
            r.notes.append(how)
        r.file = rel
        lines = read_lines(os.path.join(src, rel))
        n = len(lines) - (1 if lines and lines[-1] == "" else 0)
        if loc.line_start < 1 or loc.line_end > n:
            r.problem = f"line {loc.line_end} beyond end of file ({n} lines)"
            return r
        r.resolved = True
        cited = lines[loc.line_start - 1:loc.line_end]
        r.comment_only = bool(cited) and all(c.lstrip().startswith("%") or not c.strip() for c in cited) \
            and any(c.strip() for c in cited)
        if r.comment_only:
            r.notes.append("cited lines are TeX comments")
        lo = max(0, loc.line_start - 1 - WINDOW)
        hi = min(len(lines), loc.line_end + WINDOW)
        r.window = "\n".join(lines[lo:hi])
        mt, ingested_ver = self.main_file(pid)
        if ingested_ver and ingested_ver != ver:
            r.notes.append(f"database holds {ingested_ver}; no character range")
        else:
            a, b = self.flat_range(pid, rel, loc.line_start, loc.line_end)
            r.flat_start, r.flat_end = a, b
            r.chunk_ids = self.chunks_overlapping(pid, a, b)
            if a is None:
                r.notes.append("lines not in flat.tex (comment, preamble or unused file)")
        return r


# ---------------------------------------------------------------- one claim
def check_claim(seed_text, locators, store):
    """(status, detail dict, [LocResult]). Status: located, partial, unresolved, unlocated."""
    if not locators:
        return "unlocated", {"locators": 0}, []
    res = [store.resolve(l) for l in locators]
    bad = [r for r in res if not r.resolved]
    text = seed_text
    for l in locators:                                   # the locators' own numbers are not quoted values
        if l.raw:
            text = text.replace(l.raw, " ")
    nums = claim_numbers(text)
    window = "\n".join(r.window for r in res if r.resolved)
    cands = tex_numbers(window)
    flat_window = window.replace("{,}", ",").replace("\\,", "").replace("$", " ")
    found, missing, rounded = [], [], []
    for n in nums:
        how = number_found(n, cands, flat_window)
        if how == "exact":
            found.append(n.text)
        elif how == "rounded":
            rounded.append(n.text)
        else:
            missing.append(n.text)
    detail = {"locators": len(res), "unresolved": [f"{l.key()}: {r.problem}" for l, r in zip(locators, res) if not r.resolved],
              "numbers": len(nums), "found": found, "rounded": rounded, "missing": missing,
              "notes": sorted({n for r in res for n in r.notes})}
    detail["comment_lines"] = sum(1 for r in res if r.resolved and r.comment_only)
    if bad:
        status = "unresolved"
    elif missing or detail["comment_lines"]:
        status = "partial"           # a passage that was commented out is not the published text
    else:
        status = "located"
    return status, detail, res
