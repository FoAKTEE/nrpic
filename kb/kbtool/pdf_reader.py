"""Reader for papers whose TeX source is unusable (brief 12.4 step 6): text from a stored PDF.

Which PDF (`pdf_candidates`, `check_pdf`):
  raw/arxiv/<key>/<vN>/source.pdf   fetched by `nrpic-fetch-arxiv --pdf` for an e-print without
                                    TeX (gzipped PostScript, PostScript tar); its record is
                                    meta/arxiv-pdf/<key>.json (status, version, sha256, path)
  raw/arxiv/<key>/<vN>/src/paper.pdf  an e-print that is itself a PDF; record meta/arxiv/<key>.json
Each is checked from the bytes: a regular file, `%PDF-` at the start and `%%EOF` in the tail,
sha256 and version equal to the record.

Text (`extract_text`): poppler's `pdftotext` reads the PDF as data (it is a parser, not code
of the paper), from an empty working directory, with a minimal environment, a timeout and
limits on memory, CPU time and file size; the output is UTF-8 with a form feed at the end of
each page. Nothing of the download is executed, compiled or imported.

Repairs (`repair`), all counted and listed with their offsets in the raw text:
  - PDFs typeset with Computer Modern Type 3 fonts (dvips of the 1990s) lose the f-ligatures
    ("rst" for "first", "signi cant", "in ationary") or print them as control characters
    (0x0B-0x0F in OT1: ff, fi, fl, ffi, ffl). A token is repaired only when exactly one
    ligature inserted at one place gives a word of the corpus vocabulary (built from the
    TeX-ingested papers) that is frequent, and the token itself is not;
  - OT1 punctuation: "{" between digits is an en dash; a backslash before a letter is an
    opening double quote;
  - accent control characters inside a word are dropped; other control characters are the
    math-italic Greek letters of cmmi and become those letters;
  - a word broken by a hyphen at a line end is joined when the joined word is in the
    vocabulary.

Structure (`analyse_text`): pages, paragraphs, headings (Roman, numbered, lettered, appendix,
acknowledgements and references lines; PRL-style run-in headings when there is no numbered
one), the abstract located against the arXiv-API abstract, figure captions ("FIG. n." /
"Figure n:"), the reference list (numbered "[n]" or "n." entries) with arXiv ids and DOIs, and
the numeric citation markers of the body. No equations (brief 12.4 step 6).
"""
import collections
import difflib
import hashlib
import json
import os
import re
import subprocess
import unicodedata

from . import bib_parse as B
from . import tex_text as T
from .inventory import id_key, version_dirs

TOOL = "kbtool pdf-reader 1"
PDFTOTEXT = "/usr/bin/pdftotext"
LIGATURES = ("fi", "fl", "ff", "ffi", "ffl")
OT1_LIG = {"\x0b": "ff", "\x0c": "fi", "\x0d": "fl", "\x0e": "ffi", "\x0f": "ffl"}
CMMI = {0x0B: "α", 0x0C: "β", 0x0D: "γ", 0x0E: "δ", 0x0F: "ε", 0x10: "ζ", 0x11: "η", 0x12: "θ",
        0x13: "ι", 0x14: "κ", 0x15: "λ", 0x16: "μ", 0x17: "ν", 0x18: "ξ", 0x19: "π", 0x1A: "ρ",
        0x1B: "σ", 0x1C: "τ", 0x1D: "υ", 0x1E: "φ", 0x1F: "χ"}
VOCAB_MIN = 20          # a repair target must occur at least this often in the corpus [JUDGEMENT]
TOKEN_RARE = 3          # below this count a token is "out of vocabulary" (oov_fraction, dehyphenation)
RATIO = 10              # a repaired word must be this many times more frequent than the token [JUDGEMENT]
TOKEN_COMMON = 500      # a token this frequent is a word in its own right and never changed
ABSTRACT_FOUND = 0.6    # word-sequence similarity above which a paragraph run is the abstract [JUDGEMENT]
LIMITS = {"timeout_s": 120, "address_space": 2 << 30, "cpu_s": 120, "max_pdf_bytes": 200 << 20}


# ------------------------------------------------------------------ which PDF
def _read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pdf_candidates(lay, pid):
    """PDF files of one paper in the store, newest version first:
    [{"kind": "source.pdf"|"eprint-pdf", "path", "version", "record_path"}]."""
    key = id_key(pid)
    base = os.path.join(lay.raw_arxiv, key)
    out = []
    for v in reversed(version_dirs(base)):
        vdir = os.path.join(base, v)
        p = os.path.join(vdir, "source.pdf")
        if os.path.lexists(p):
            out.append({"kind": "source.pdf", "path": p, "version": v.split(".")[0],
                        "record_path": os.path.join(lay.data, "meta", "arxiv-pdf", key + ".json")})
        p = os.path.join(vdir, "src", "paper.pdf")
        if os.path.lexists(p):
            out.append({"kind": "eprint-pdf", "path": p, "version": v.split(".")[0],
                        "record_path": os.path.join(lay.meta_arxiv, key + ".json")})
    return out


def check_pdf(cand):
    """Checks of one candidate from the bytes and its record. Returns dict(ok, problems, ...)."""
    p = cand["path"]
    res = {**cand, "problems": []}
    if os.path.islink(p) or not os.path.isfile(p):
        res["problems"].append("not a regular file")
        res["ok"] = False
        return res
    size = os.path.getsize(p)
    res["bytes"] = size
    if size > LIMITS["max_pdf_bytes"]:
        res["problems"].append(f"larger than {LIMITS['max_pdf_bytes']} bytes")
    with open(p, "rb") as f:
        head = f.read(8)
        f.seek(max(0, size - 2048))
        tail = f.read()
    if not head.startswith(b"%PDF-"):
        res["problems"].append("does not start with %PDF-")
    if b"%%EOF" not in tail:
        res["problems"].append("no %%EOF in the last 2 KiB")
    res["sha256"] = sha256_file(p)
    rec = _read_json(cand["record_path"])
    if rec is None:
        res["problems"].append(f"no record {os.path.basename(cand['record_path'])}")
    else:
        if rec.get("status") != "ok":
            res["problems"].append(f"record status {rec.get('status')!r}")
        if rec.get("version") and rec["version"] != cand["version"]:
            res["problems"].append(f"record version {rec['version']} differs from directory {cand['version']}")
        if cand["kind"] == "source.pdf":
            if rec.get("sha256") != res["sha256"]:
                res["problems"].append("sha256 differs from the --pdf record")
            if rec.get("pdf") and os.path.normpath(rec["pdf"]) != os.path.normpath(p):
                res["problems"].append("record names another file")
        else:
            src_bin = os.path.join(os.path.dirname(os.path.dirname(p)), "source.bin")
            if rec.get("kind") != "pdf":
                res["problems"].append(f"e-print record kind {rec.get('kind')!r}, not pdf")
            if rec.get("sha256") not in (res["sha256"],) and not (
                    os.path.isfile(src_bin) and rec.get("sha256") == sha256_file(src_bin)):
                res["problems"].append("sha256 matches neither paper.pdf nor source.bin")
        res["record"] = {k: rec.get(k) for k in ("status", "version", "sha256", "url", "fetched_utc")}
    res["ok"] = not res["problems"]
    return res


def choose_pdf(lay, pid):
    """The first candidate that passes every check, with the checks of all candidates."""
    checks = [check_pdf(c) for c in pdf_candidates(lay, pid)]
    good = next((c for c in checks if c["ok"]), None)
    return good, checks


# ------------------------------------------------------------------ text
def _limits():
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (LIMITS["address_space"], LIMITS["address_space"]))
    resource.setrlimit(resource.RLIMIT_CPU, (LIMITS["cpu_s"], LIMITS["cpu_s"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))          # no file is written; stdout is a pipe
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def extract_text(pdf_path, workdir):
    """pdftotext of the whole PDF (UTF-8, a form feed after each page). `workdir` must be an
    existing directory outside the download; it is the working directory of the parser."""
    out = subprocess.run([PDFTOTEXT, "-enc", "UTF-8", "-eol", "unix", "-q", os.path.abspath(pdf_path), "-"],
                         capture_output=True, timeout=LIMITS["timeout_s"], cwd=workdir, stdin=subprocess.DEVNULL,
                         env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": workdir},
                         preexec_fn=_limits, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"pdftotext exit {out.returncode}: {out.stderr[:300]!r}")
    return out.stdout.decode("utf-8", "replace")


# ------------------------------------------------------------------ vocabulary and repairs
WORD_RE = re.compile(r"[A-Za-z]+")


def build_vocab(texts):
    """Lower-case word counts of an iterable of texts."""
    c = collections.Counter()
    for t in texts:
        c.update(w.lower() for w in WORD_RE.findall(t))
    return c


def vocab_from_db(con, min_count=2):
    """The vocabulary of the TeX-ingested papers (body, abstract, appendix, caption chunks)."""
    rows = con.execute("SELECT c.text FROM chunks c JOIN papers p ON p.paper_id = c.paper_id "
                       "WHERE p.source_kind = 'tex' AND c.kind IN ('body','abstract','appendix','caption')")
    c = build_vocab(r[0] for r in rows)
    return {w: n for w, n in c.items() if n >= min_count}


def _case_like(src, word):
    if src.isupper() and len(src) > 1:
        return word.upper()
    if src[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def ligature_candidates(token, vocab):
    """Words of the vocabulary obtained by inserting one ligature into `token`, with counts."""
    t = token.lower()
    out = {}
    for lig in LIGATURES:
        for k in range(len(t) + 1):
            w = t[:k] + lig + t[k:]
            n = vocab.get(w, 0)
            if n >= VOCAB_MIN:
                out[w] = max(out.get(w, 0), n)
    return out


def best_repair(token, vocab):
    """The repaired word for a token, or None. The best candidate must be frequent (VOCAB_MIN),
    RATIO times more frequent than the token itself, and 5 times more frequent than the second
    candidate [JUDGEMENT]. Short all-capital tokens (acronyms) are never changed."""
    if token.isupper() and len(token) <= 4:
        return None
    own = vocab.get(token.lower(), 0)
    cand = ligature_candidates(token, vocab)
    if not cand:
        return None
    ranked = sorted(cand.items(), key=lambda kv: -kv[1])
    if ranked[0][1] < RATIO * max(own, 1) or own >= TOKEN_COMMON:
        return None
    if len(ranked) > 1 and ranked[1][1] * 5 > ranked[0][1]:
        return None                                   # ambiguous
    return _case_like(token, ranked[0][0])


class Edits:
    """Text rebuilt from replacements of spans of the raw text; keeps the list for audit."""

    def __init__(self):
        self.items = []                               # (start, end, old, new, kind)

    def add(self, a, b, old, new, kind):
        self.items.append((a, b, old, new, kind))


def _apply(text, edits, kind_filter=None):
    out, pos, done = [], 0, []
    for a, b, old, new, kind in sorted(edits, key=lambda e: e[0]):
        if a < pos:
            continue                                  # overlapping edit: the first wins
        out.append(text[pos:a])
        out.append(new)
        pos = b
        done.append((a, b, old, new, kind))
    out.append(text[pos:])
    return "".join(out), done


def repair(raw, vocab):
    """Returns (text, edits, counts). Edits are (start, end, old, new, kind) in `raw`."""
    edits = []
    # 1. control characters inside words: OT1 ligatures, accents; elsewhere cmmi Greek.
    #    0x0C is left alone everywhere: pdftotext writes it as the page break.
    for m in re.finditer(r"[A-Za-z]*[\x0b\x0d-\x1f]+[A-Za-z]*", raw):
        s = m.group(0)
        word = None
        if re.fullmatch(r"[A-Za-z]*[\x0b\x0d-\x0f][A-Za-z]*", s):
            w = "".join(OT1_LIG.get(ch, ch) for ch in s)
            if vocab.get(w.lower(), 0) >= VOCAB_MIN:
                word, kind = w, "ot1-ligature"
        if word is None and re.fullmatch(r"[A-Za-z]+[\x12-\x18]+[A-Za-z]+", s):
            word, kind = re.sub(r"[\x12-\x18]", "", s), "accent-dropped"
        if word is None:
            word = "".join(CMMI.get(ord(ch), "") if ord(ch) < 0x20 else ch for ch in s)
            kind = "cmmi-greek"
        if word != s:
            edits.append((m.start(), m.end(), s, word, kind))
    text1, done1 = _apply(raw, edits)
    # positions after step 1 no longer match `raw`; steps 2-4 work on text1 and are recorded against it
    edits2 = []
    ot1 = bool(re.search(r"\d\{\d", text1))
    if ot1:
        for m in re.finditer(r"(?<=\d)\{(?=\d)", text1):
            edits2.append((m.start(), m.end(), "{", "–", "ot1-endash"))
        for m in re.finditer(r"\\(?=[A-Za-z])", text1):
            edits2.append((m.start(), m.end(), "\\", "“", "ot1-quote"))
    # 2. hyphen at a line end
    for m in re.finditer(r"([A-Za-z]{2,})-\n([a-z]{2,})([A-Za-z]*)", text1):
        joined = (m.group(1) + m.group(2) + m.group(3))
        if vocab.get(joined.lower(), 0) >= TOKEN_RARE:
            edits2.append((m.start(), m.end(), m.group(0), joined + "\n", "dehyphen"))
    # 3. split ligature: "signi cant", "in ationary", "de ne" -> one word
    toks = list(WORD_RE.finditer(text1))
    for m, m2 in zip(toks, toks[1:]):                 # every pair of neighbours (overlapping)
        if text1[m.end():m2.start()] != " " or not m2.group(0)[0].islower():
            continue
        a, b = m.group(0), m2.group(0)
        floor = min(vocab.get(a.lower(), 0), vocab.get(b.lower(), 0))
        cands = {}
        for lig in LIGATURES:
            w = (a + lig + b)
            n = vocab.get(w.lower(), 0)
            # the joined word must be frequent, and more frequent than the rarer of the two
            # parts (two ordinary words stay apart) [JUDGEMENT: a factor 2]
            if n >= VOCAB_MIN and n >= 2 * floor:
                cands[w] = n
        if len(cands) == 1 or (cands and sorted(cands.values())[-2] * 5 <= max(cands.values())):
            w = max(cands, key=cands.get)
            edits2.append((m.start(), m2.end(), text1[m.start():m2.end()], _case_like(a, w), "ligature-split"))
    # 4. dropped ligature inside one token: "rst", "uid", "eld"
    for m in re.finditer(r"(?<![A-Za-z\-])[A-Za-z]{2,}(?![A-Za-z])", text1):
        tok = m.group(0)
        w = best_repair(tok, vocab)
        if w:
            edits2.append((m.start(), m.end(), tok, w, "ligature-dropped"))
    text2, done2 = _apply(text1, edits2)
    counts = collections.Counter(e[4] for e in done1 + done2)
    return text2, {"step1_on_raw": done1, "step2_on_step1": done2}, dict(counts)


def oov_fraction(text, vocab, min_len=3):
    """Fraction of alphabetic tokens (length >= min_len) that are rare in the vocabulary."""
    toks = [w.lower() for w in WORD_RE.findall(text) if len(w) >= min_len]
    if not toks:
        return None, 0
    bad = sum(1 for w in toks if vocab.get(w, 0) < TOKEN_RARE)
    return bad / len(toks), len(toks)


# ------------------------------------------------------------------ structure
ROMAN = re.compile(r"^(?P<num>[IVX]{1,6})\.\s+(?P<title>[A-Z][A-Z0-9 ,:;'’\-–()/&.]+?)\s*$")
NUMBERED = re.compile(r"^(?P<num>\d{1,2}(?:\.\d{1,2}){0,2})\.?\s+(?P<title>[A-Z][^\n]{1,100}?)\s*$")
LETTERED = re.compile(r"^(?P<num>[A-H])\.\s+(?P<title>[A-Z][a-z][^\n]{1,90}?)\s*$")
APPENDIX = re.compile(r"^(?:APPENDIX|Appendix)(?:\s+(?P<num>[A-Z0-9]{1,2}))?[:.]?(?:\s+(?P<title>[^\n]{2,90}))?\s*$")
UNNUMBERED = re.compile(r"^(?P<title>Acknowledg(?:e)?ments?|ACKNOWLEDG(?:E)?MENTS?|References|REFERENCES|"
                        r"Bibliography|Abstract|ABSTRACT|Introduction|INTRODUCTION|Conclusions?|CONCLUSIONS?)\.?\s*$")
RUNIN = re.compile(r"^(?P<title>[A-Z][a-z]*(?:[ \-][A-Za-z][a-z]*){0,5})\.\s+(?=[A-Z])")
STANDALONE = re.compile(r"^[A-Z][A-Za-z\-]*(?: [A-Za-z][A-Za-z\-]*){0,5}$")
AFFILIATION = re.compile(r"Universit|Institut|Department|Departament|Laborator|Observator|College|School of|"
                         r"Centre|Center for|@|\b[A-Z]{2}\s?\d{4,5}\b")
RUNIN_STOP = {"is", "are", "was", "were", "be", "been", "has", "have", "had", "we", "it", "can", "will", "may",
              "this", "there", "here", "then", "eq", "eqs", "fig", "figs", "ref", "refs", "sec", "al", "et", "see",
              "phys", "rev", "lett", "vol", "no", "i", "e", "g", "cf", "thus", "hence", "note", "but", "so", "form",
              "forms", "gives", "reads", "becomes", "follows", "shows", "yields", "holds"}
FIG_RE = re.compile(r"^(?P<kind>FIG\.|Fig\.|Figure|FIGURE|TABLE|Table)\s*(?P<num>[0-9IVX]{1,4})[.:]\s+")


def _lines(text):
    pos = 0
    for line in text.split("\n"):
        yield pos, line
        pos += len(line) + 1


def _title_ok(title):
    letters = sum(ch.isalpha() for ch in title)
    words = title.split()
    return (letters >= 3 and letters / max(1, len(title.replace(" ", ""))) > 0.7 and len(words) <= 14
            and not title.rstrip().endswith((",", ";", "=")) and re.search(r"[A-Za-z]{3,}", title) is not None)


def _num_key(num):
    return tuple(int(x) for x in num.split("."))


def find_headings(text):
    """Heading candidates [(start, end, level, number, title, kind)], filtered so that
    numbered headings continue a consistent sequence."""
    lines = list(_lines(text))
    cands = []
    for i, (pos, line) in enumerate(lines):
        s = line.strip().replace("\x0c", "")
        if not s or len(s) > 110:
            continue
        lead = pos + (len(line) - len(line.lstrip()))
        m = ROMAN.match(s)
        if m and _title_ok(m.group("title")):
            title, end = m.group("title"), pos + len(line)
            # an upper-case heading may wrap onto the next line
            if i + 1 < len(lines):
                nxt = lines[i + 1][1].strip()
                if nxt and nxt.isupper() and len(nxt) < 80 and re.fullmatch(r"[A-Z0-9 ,:;'\-()/&.]+", nxt):
                    title, end = title + " " + nxt, lines[i + 1][0] + len(lines[i + 1][1])
            cands.append((lead, end, 1, m.group("num"), title, "roman"))
            continue
        m = APPENDIX.match(s)
        if m:
            cands.append((lead, pos + len(line), 1, m.group("num") or "", (m.group("title") or "").strip(), "appendix"))
            continue
        m = UNNUMBERED.match(s)
        if m:
            cands.append((lead, pos + len(line), 1, "", m.group("title"), "unnumbered"))
            continue
        m = NUMBERED.match(s)
        if m and _title_ok(m.group("title")) and not m.group("title").rstrip().endswith("."):
            lvl = m.group("num").count(".") + 1
            cands.append((lead, pos + len(line), lvl, m.group("num"), m.group("title"), "numbered"))
            continue
        m = LETTERED.match(s)
        if m and _title_ok(m.group("title")) and not m.group("title").rstrip().endswith("."):
            cands.append((lead, pos + len(line), 2, m.group("num"), m.group("title"), "lettered"))
    # numbered sequence: keep 1, 2, 2.1, 2.2, 3, ... (a candidate must follow the last kept one)
    out, last = [], None
    roman_seen = any(c[5] == "roman" for c in cands)
    last_letter = None
    for c in cands:
        if c[5] == "numbered":
            k = _num_key(c[3])
            if last is None:
                ok = k in ((1,), (1, 1), (0,))
            else:
                ok = (len(k) == 1 and k[0] == last[0] + 1) or \
                     (len(k) == len(last) + 1 and k[:-1] == last and k[-1] == 1) or \
                     (len(k) == len(last) and k[:-1] == last[:-1] and k[-1] == last[-1] + 1) or \
                     (len(k) < len(last) and k[:-1] == last[:len(k) - 1] and k[-1] == last[len(k) - 1] + 1)
            if not ok:
                continue
            last = k
        elif c[5] == "lettered":
            if not roman_seen:
                continue
            expect = "A" if last_letter is None else chr(ord(last_letter) + 1)
            if c[3] != expect:
                continue
            last_letter = c[3]
        elif c[5] == "roman":
            last_letter = None
        out.append(c)
    return out


def find_runin(text):
    """PRL-style run-in headings at the start of a paragraph: 'Introduction. For decades ...'."""
    out = []
    lines = list(_lines(text))
    for i, (pos, line) in enumerate(lines):
        prev = lines[i - 1][1].strip() if i else ""
        if prev and not prev.endswith((".", ":")) and "\x0c" not in prev:
            continue
        body = line.lstrip("\x0c")                     # a page break may start the line
        off = len(line) - len(body)
        m = RUNIN.match(body)
        if not m:
            continue
        title = m.group("title")
        words = [w.lower() for w in re.split(r"[ \-]", title)]
        if any(w in RUNIN_STOP for w in words) or len(title) < 4:
            continue
        out.append((pos + off, pos + off + m.end("title") + 1, 1, "", title, "run-in"))
    return out


def find_standalone(text):
    """Unnumbered headings on a line of their own (JOSS-style 'Summary', 'Statement of need'):
    at most six words, letters only, a blank line before and text right after."""
    out = []
    lines = list(_lines(text))
    for i in range(1, len(lines) - 1):
        pos, line = lines[i]
        s = line.strip()
        if not s or lines[i - 1][1].strip().replace("\x0c", "") or not lines[i + 1][1].strip():
            continue
        if STANDALONE.match(s) and not AFFILIATION.search(s) and len(s) >= 4:
            lead = pos + (len(line) - len(line.lstrip()))
            out.append((lead, pos + len(line), 1, "", s, "standalone"))
    return out


AUTHOR_YEAR = re.compile(r"^[A-Z\u00c0-\u017f][^\s,]{1,40}(?: [a-z]{1,4})?(?: [A-Z][^\s,]{1,30})?, (?:[A-Z]\.|[A-Z][a-z]+)")


def _entry_text(s):
    """One entry on one line; a URL or DOI broken at a line end is joined again."""
    s = re.sub(r"(https?:|doi\.org/\S*|10\.\d{4,9}/\S*)\n(\S)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip()


def find_references(text, start_hint=0):
    """The reference list: entries '[n] ...' (or 'n. ...' after a References heading) in an
    increasing sequence from 1. Returns (entries, spans) with entries
    [{"key": "n", "start", "end", "raw"}] and the list of (start, end) spans they cover."""
    entries = []
    pat = re.compile(r"^\[(\d{1,3})\]\s+", re.M)
    hits = [m for m in pat.finditer(text, start_hint)]
    expect = 1
    starts = []
    for m in hits:
        n = int(m.group(1))
        if n == expect:
            starts.append((m.start(), n))
            expect += 1
    style = "numeric"
    if len(starts) < 3:
        # numbered "1. Author" lists, else author-year entries, after a References heading
        mh = None
        for mh in re.finditer(r"^(References|REFERENCES|Bibliography)\s*$", text[start_hint:], re.M):
            pass
        if mh:
            base = start_hint + mh.end()
            starts, expect = [], 1
            for m in re.finditer(r"^(\d{1,3})\.\s+(?=[A-Z])", text[base:], re.M):
                if int(m.group(1)) == expect:
                    starts.append((base + m.start(), expect))
                    expect += 1
            if len(starts) < 3:
                style = "author-year"
                starts = []
                for pos, line in _lines(text[base:]):
                    if AUTHOR_YEAR.match(line):
                        starts.append((base + pos, len(starts) + 1))
    for k, (a, n) in enumerate(starts):
        nxt = starts[k + 1][0] if k + 1 < len(starts) else len(text)
        # an entry ends at the next entry, or at a blank line / page break before it
        para_end = re.search(r"\n[ \t]*\n|\x0c", text[a:nxt])
        b = a + para_end.start() if para_end else nxt
        entries.append({"key": str(n), "start": a, "end": b, "raw": _entry_text(text[a:b]), "style": style})
    spans = [(e["start"], e["end"]) for e in entries]
    return entries, spans


def find_captions(text):
    out = []
    for pos, line in _lines(text):
        m = FIG_RE.match(line.strip())
        if not m:
            continue
        a = pos + (len(line) - len(line.lstrip()))
        end = re.search(r"\n[ \t]*\n|\x0c", text[a:])
        b = a + end.start() if end else len(text)
        kind = "table" if m.group("kind").lower().startswith("tab") else "figure"
        out.append({"kind": kind, "number": m.group("num"), "start": a, "end": b,
                    "caption": re.sub(r"\s+", " ", text[a:b]).strip()})
    return out


def word_similarity(a, b):
    wa = [w.lower() for w in WORD_RE.findall(a or "")]
    wb = [w.lower() for w in WORD_RE.findall(b or "")]
    if not wa or not wb:
        return 0.0
    return difflib.SequenceMatcher(None, wa, wb, autojunk=False).ratio()


def paragraph_spans(text, lo=0, hi=None):
    hi = len(text) if hi is None else hi
    out, pos = [], lo
    for m in re.finditer(r"\n[ \t]*\n|\x0c", text[lo:hi]):
        a = lo + m.start()
        if text[pos:a].strip():
            out.append((pos, a))
        pos = lo + m.end()
    if text[pos:hi].strip():
        out.append((pos, hi))
    return out


def locate_abstract(text, meta_abstract, page_end):
    """The run of 1-4 consecutive paragraphs of the first two pages most similar (word sequence)
    to the metadata abstract. Returns (start, end, similarity) or (None, None, 0.0)."""
    if not meta_abstract:
        return None, None, 0.0
    paras = paragraph_spans(text, 0, page_end)
    best = (None, None, 0.0)
    for i in range(len(paras)):
        for k in range(1, 5):
            if i + k > len(paras):
                break
            a, b = paras[i][0], paras[i + k - 1][1]
            if len(text[a:b]) > 4 * len(meta_abstract) + 500:
                break
            r = word_similarity(text[a:b], meta_abstract)
            if r > best[2]:
                best = (a, b, r)
    a, b, r = best
    if a is None:
        return best
    # trim whole lines at either end while the similarity does not fall (title, PACS lines)
    changed = True
    while changed:
        changed = False
        nl = text.find("\n", a, b)
        if nl != -1 and text[nl + 1:b].strip():
            r2 = word_similarity(text[nl + 1:b], meta_abstract)
            if r2 >= r:
                a, r, changed = nl + 1, r2, True
        nl = text.rfind("\n", a, b.__sub__(1) if text[b - 1:b] == "\n" else b)
        if nl > a and text[a:nl].strip():
            r2 = word_similarity(text[a:nl], meta_abstract)
            if r2 >= r:
                b, r, changed = nl, r2, True
    return a, b, r


CITE_RE = re.compile(r"\[(\d{1,3}(?:\s*[,–\-]\s*\d{1,3})*)\]")


def numeric_citations(text, spans_excluded, n_entries):
    """Numeric citation markers '[3]', '[5,7]', '[5-7]' of the body -> [(start, end, [keys])]."""
    out = []
    for m in CITE_RE.finditer(text):
        if any(a <= m.start() < b for a, b in spans_excluded):
            continue
        keys = []
        for part in re.split(r"\s*,\s*", m.group(1)):
            r = re.split(r"\s*[–\-]\s*", part)
            if len(r) == 2 and r[0].isdigit() and r[1].isdigit() and int(r[0]) < int(r[1]) <= int(r[0]) + 50:
                keys += [str(x) for x in range(int(r[0]), int(r[1]) + 1)]
            elif r[0].isdigit():
                keys.append(r[0])
        keys = [k for k in keys if 1 <= int(k) <= n_entries]
        if keys:
            out.append((m.start(), m.end(), keys))
    return out


def _protect(text):
    """Copy of text in which characters that tex_text treats as TeX are blanked (same length)."""
    return text.replace("\\", " ").replace("{", " ").replace("}", " ").replace("\x0c", "\n")


def analyse_text(text, meta=None):
    """Everything the knowledge base derives from the repaired text of one PDF paper.
    `meta` is the arXiv-API record (title, authors, abstract) or None. Returns the doc dict of
    papers_ingest (title, authors, abstract, sections, chunks, figures, cites, bib, quality)."""
    meta = meta or {}
    pages = [0] + [m.end() for m in re.finditer("\x0c", text)]
    if pages[-1] >= len(text):
        pages = pages[:-1]
    page_end_2 = pages[2] if len(pages) > 2 else len(text)
    # references first: their span is excluded from headings, chunks and citations
    entries, ref_spans = find_references(text, start_hint=len(text) // 4)
    caps = find_captions(text)
    cap_spans = [(c["start"], c["end"]) for c in caps]
    a0, a1, abs_sim = locate_abstract(text, meta.get("abstract"), page_end_2)
    if abs_sim < ABSTRACT_FOUND:
        a0 = a1 = None                     # no paragraph of the PDF is the metadata abstract
    excluded = ref_spans + cap_spans + ([(a0, a1)] if a0 is not None else [])
    front_end = a1 if a1 is not None else 0
    heads = [h for h in find_headings(text) if not any(a <= h[0] < b for a, b in ref_spans + cap_spans)
             and h[0] >= front_end and not AFFILIATION.search(h[4])]
    if not any(h[5] in ("roman", "numbered") for h in heads):
        runin = [h for h in find_runin(text) if not any(a <= h[0] < b for a, b in excluded)]
        heads = sorted(heads + runin, key=lambda h: h[0])
    if not any(h[5] in ("roman", "numbered", "run-in") for h in heads):
        known = {h[0] for h in heads}
        alone = [h for h in find_standalone(text) if h[0] not in known and h[0] >= front_end
                 and not any(a <= h[0] < b for a, b in excluded)]
        heads = sorted(heads + alone, key=lambda h: h[0])
    heads = [h for h in heads if not (h[5] == "unnumbered" and h[4].lower().startswith("abstract"))]
    # section spans: to the next heading of the same or a higher level
    secs = []
    for k, (s0, s1, lvl, num, title, kind) in enumerate(heads):
        end = len(text)
        for h in heads[k + 1:]:
            if h[2] <= lvl:
                end = h[0]
                break
        own_end = heads[k + 1][0] if k + 1 < len(heads) else len(text)
        parent = None
        for j in range(k - 1, -1, -1):
            if heads[j][2] < lvl:
                parent = j
                break
        secs.append({"level": lvl, "number": num, "title": re.sub(r"\s+", " ", title).strip(), "label": None,
                     "start": s0, "end": end, "cmd_end": s1, "own_end": own_end, "parent": parent,
                     "appendix": kind == "appendix", "starred": kind in ("unnumbered", "run-in", "standalone"),
                     "kind": kind})
    masked = list(_protect(text))
    for a, b in excluded:
        for i in range(a, b):
            if masked[i] != "\n":
                masked[i] = " "
    masked = "".join(masked)
    ident = lambda s: s                                                  # noqa: E731
    chunks = []
    first = secs[0]["start"] if secs else len(text)
    regions = [(None, 0, first)] + [(k, s["cmd_end"], s["own_end"]) for k, s in enumerate(secs)]
    words_body = 0
    for k, a, b in regions:
        if b <= a:
            continue
        kind = "appendix" if k is not None and secs[k]["appendix"] else "body"
        for c in T.chunk_section(masked, a, b, [], ident, kind):
            txt = re.sub(r"\s+", " ", text[c["start"]:c["end"]]).strip()
            # blanked spans (captions, references) inside the range are not part of the chunk text
            mtxt = re.sub(r"\s+", " ", masked[c["start"]:c["end"]]).strip()
            use = mtxt if len(mtxt) < len(txt) else txt
            if len(use.split()) < 3:
                continue
            chunks.append({"kind": kind, "start": c["start"], "end": c["end"], "text": use, "tex": None,
                           "n_tokens": T.ntok(use), "section": k})
            words_body += T.ntok(use)
    if meta.get("abstract"):
        ab = re.sub(r"\s+", " ", meta["abstract"]).strip()
        atext = re.sub(r"\s+", " ", text[a0:a1]).strip() if a0 is not None else ab
        chunks.insert(0, {"kind": "abstract", "start": a0, "end": a1, "text": atext,
                          "tex": None, "n_tokens": T.ntok(atext), "section": None})
    figures = []
    for c in caps:
        sec = None
        for k, s in enumerate(secs):
            if s["start"] <= c["start"] < s["end"]:
                sec = k
        figures.append({"label": None, "number": c["number"], "kind": c["kind"], "files": [], "caption": c["caption"],
                        "caption_tex": None, "start": c["start"], "end": c["end"], "section": sec})
        chunks.append({"kind": "caption", "start": c["start"], "end": c["end"], "text": c["caption"], "tex": None,
                       "n_tokens": T.ntok(c["caption"]), "section": sec})
    bib_entries = []
    for e in entries:
        ids = B.arxiv_ids(e["raw"])
        ds = B.dois(e["raw"])
        bib_entries.append({"cite_key": e["key"], "raw": e["raw"], "arxiv": ids[0] if ids else None,
                            "doi": ds[0] if ds else None, "eprint": None, "n_arxiv_ids": len(ids), "title": None,
                            "start": e["start"], "end": e["end"]})
    cites = []
    for s0, s1, keys in numeric_citations(text, ref_spans + cap_spans, len(entries)):
        sec = None
        for k, s in enumerate(secs):
            if s["start"] <= s0 < s["end"]:
                sec = k
        lo = max(0, s0 - 400)
        window = re.sub(r"\s+", " ", masked[lo:s0] + "CITEMARK" + masked[s1:s1 + 400])
        sent = next((x for x in T.sentences(window) if "CITEMARK" in x), "")
        cites.append({"keys": keys, "start": s0, "end": s1, "section": sec, "nocite": False,
                      "context": sent.replace("CITEMARK", "[cit.]").strip()[:1200]})
    title = meta.get("title") or ""
    authors = list(meta.get("authors") or [])
    comp = {"title": 1.0 if title else 0.0,
            "abstract": min(1.0, abs_sim / 0.8) if meta.get("abstract") else 0.0,
            "sections": min(1.0, sum(1 for s in secs if s["kind"] != "unnumbered") / 3.0),
            "body_text": min(1.0, words_body / 1000.0)}
    w = {"title": .15, "abstract": .25, "sections": .25, "body_text": .35}
    score = round(sum(w[k] * comp[k] for k in w), 4)
    doc = {"title": title, "authors": authors, "abstract": meta.get("abstract"),
           "sections": [{k: s[k] for k in ("level", "number", "title", "label", "start", "end", "parent",
                                            "appendix", "starred", "kind")} for s in secs],
           "equations": [], "figures": figures, "footnotes": 0, "cites": cites, "labels": {},
           "chunks": chunks, "pages": pages,
           "quality": {"score": score, "components": comp, "weights": w, "abstract_similarity_to_metadata":
                       round(abs_sim, 4), "body_words": words_body, "pages": len(pages),
                       "threshold": None, "note": "PDF text: no equations (brief 12.4 step 6)"},
           "converter": TOOL + " / pdftotext",
           "bib": {"source": "pdf-text", "files": [], "notes": [], "entries": bib_entries}}
    return doc
