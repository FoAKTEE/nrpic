"""Brief section 16 (the reference list) read by script, and compared with the downloaded
metadata (brief 12.3: "Compare title and authors entry by entry with section 16 ... Where they
differ, the downloaded data win").

An entry of section 16 is one line
    - <mark> [arXiv:<id>](<link>) — <authors> — *<title>* — <note>
where the author field may be absent, "X et al.", "X (first author)" or "(authors include ...)".
The group is the "### Gnn ..." heading above the entry; the mark (★ ◆ ·) is the priority 3/2/1.

Title classes: same (identical after collapsing white space), format (identical after folding
case, accents, TeX, dashes, quotes and punctuation), minor (normalised similarity >= 0.9),
differs (below). Author classes: match, order (every name found, not in the brief's order or
the brief's first author is not the first), incomplete (a plain list without "et al." that
omits authors), mismatch (a name of the brief is not among the authors), collaboration (the
brief names a collaboration; recorded whether the metadata lists it), not-checked (no author
field). Metadata author entries without a letter (";" or "." that the arXiv API returns for
some old papers) are dropped; two authors of the same surname take two places.
"""
import difflib
import hashlib
import re
import unicodedata

ENTRY_RE = re.compile(r"^- (?P<mark>\S+) \[arXiv:(?P<id>[^\]]+)\]\((?P<link>[^)]*)\) \u2014 "
                      r"(?:(?P<authors>.*?) \u2014 )?\*(?P<title>.+?)\*(?: \u2014 (?P<note>.*))?$")
GROUP_RE = re.compile(r"^### (?P<g>G\d{2}) (?P<title>.*?) \((?P<n>\d+) entries\)\s*$")
MARK_PRIORITY = {"\u2605": 3, "\u25c6": 2, "\u00b7": 1}
TITLE_MINOR = 0.9


class Brief16Error(ValueError):
    pass


def parse_section16(path):
    """Entries of brief section 16 with their line numbers (1-based)."""
    blob = open(path, "rb").read()
    lines = blob.decode("utf-8").split("\n")
    try:
        s = next(i for i, l in enumerate(lines) if l.startswith("## 16."))
        e = next(i for i, l in enumerate(lines) if l.startswith("## 17."))
    except StopIteration:
        raise Brief16Error("headings '## 16.' and '## 17.' not found")
    entries, groups, problems, group = [], {}, [], None
    for i in range(s, e):
        line = lines[i]
        m = GROUP_RE.match(line)
        if m:
            group = m.group("g")
            groups[group] = {"title": m.group("title"), "declared": int(m.group("n")), "line": i + 1, "found": 0}
            continue
        if not line.startswith("- ") or "[arXiv:" not in line:
            continue
        m = ENTRY_RE.match(line)
        if not m:
            problems.append(f"line {i + 1}: entry not parsed")
            continue
        if group is None:
            problems.append(f"line {i + 1}: entry before any group heading")
        aid = m.group("id")
        if not m.group("link").endswith("/" + aid):
            problems.append(f"line {i + 1}: link {m.group('link')} does not end with the id {aid}")
        groups[group]["found"] += 1
        entries.append({"id": aid, "line": i + 1, "group": group, "mark": m.group("mark"),
                        "priority": MARK_PRIORITY.get(m.group("mark")), "authors_raw": (m.group("authors") or "").strip(),
                        "title": m.group("title").strip(), "note": (m.group("note") or "").strip()})
    for g, d in groups.items():
        if d["declared"] != d["found"]:
            problems.append(f"{g}: heading says {d['declared']} entries, found {d['found']}")
    seen = set()
    for x in entries:
        if x["id"] in seen:
            problems.append(f"line {x['line']}: duplicate id {x['id']}")
        seen.add(x["id"])
    return {"entries": entries, "groups": groups, "problems": problems, "first_line": s + 1, "last_line": e,
            "brief_sha256": hashlib.sha256(blob).hexdigest()}


# ------------------------------------------------------------------ titles
GREEK = {"α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "ζ": "zeta", "η": "eta",
         "θ": "theta", "κ": "kappa", "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "π": "pi", "ρ": "rho",
         "σ": "sigma", "τ": "tau", "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega", "Γ": "gamma", "Δ": "delta",
         "Θ": "theta", "Λ": "lambda", "Ξ": "xi", "Π": "pi", "Σ": "sigma", "Φ": "phi", "Ψ": "psi", "Ω": "omega"}
TEX_ACCENT = re.compile(r"\\(?:[`'^\"~=.]|[uvHtcdbr](?![A-Za-z]))\s*\{?([A-Za-z])\}?")


def fold(s):
    """Accents removed, Greek letters spelled out, lower case."""
    s = "".join(GREEK.get(ch, ch) for ch in s or "")
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


TEX_FONT = re.compile(r"\\(?:mathrm|mathcal|mathbf|mathbb|mathtt|mathsf|mathit|mathfrak|boldsymbol|textrm|textit|"
                      r"texttt|textsf|textbf|textsc|emph|rm|it|bf|tt|sf|sc|em|scriptstyle|displaystyle|textstyle)"
                      r"(?![A-Za-z])\s*")


def norm_title(t):
    t = TEX_FONT.sub("", t or "")
    t = TEX_ACCENT.sub(r"\1", t)
    t = re.sub(r"\\[,;:!]", "", t).replace("{", "").replace("}", "")
    t = re.sub(r"\\([A-Za-z]+)", r" \1 ", t)                         # \Lambda -> lambda
    t = fold(t).replace("$", " ")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def compare_title(brief, meta):
    if meta is None:
        return {"class": "no-metadata", "ratio": None}
    if re.sub(r"\s+", " ", brief).strip() == re.sub(r"\s+", " ", meta).strip():
        return {"class": "same", "ratio": 1.0}
    a, b = norm_title(brief), norm_title(meta)
    if a == b or a.replace(" ", "") == b.replace(" ", ""):
        return {"class": "format", "ratio": 1.0}
    r = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    return {"class": "minor" if r >= TITLE_MINOR else "differs", "ratio": round(r, 4)}


# ------------------------------------------------------------------ authors
INITIAL = re.compile(r"^(?:[A-Z][a-z]?\.(?:-?[A-Z][a-z]?\.)*|[A-Z])$")
SUFFIX = re.compile(r",?\s+(?:Jr\.?|Sr\.?|II|III|IV)$")


COLLAB = re.compile(r"\b(?:Collaboration|Network|Consortium|Team|Group)\b", re.I)


def parse_brief_authors(s):
    """{"kind": none|collaboration|list|etal|first|include, "names": [surname strings as written]}."""
    s = (s or "").strip()
    if not s:
        return {"kind": "none", "names": []}
    if COLLAB.search(s) and "," not in s:
        return {"kind": "collaboration", "names": [s]}
    m = re.match(r"^\(authors include (.*)\)$", s)
    if m:
        return {"kind": "include", "names": [x.strip() for x in re.split(r",\s*|\s+and\s+", m.group(1)) if x.strip()]}
    m = re.match(r"^(.*?)\s*\(first author\)$", s)
    if m:
        return {"kind": "first", "names": [m.group(1).strip()]}
    m = re.match(r"^(.*?),?\s+et al\.?$", s)
    if m:
        return {"kind": "etal", "names": [x.strip() for x in m.group(1).split(",") if x.strip()]}
    return {"kind": "list", "names": [x.strip() for x in re.split(r",\s*|\s+and\s+|\s*&\s*", s) if x.strip()]}


def surname_tokens(name):
    """Folded tokens of a brief name without initials: 'E. R. Most' -> ['most'], 'van Meter' -> ['van', 'meter']."""
    toks = [t for t in re.split(r"\s+", name.strip()) if t and not INITIAL.match(t)]
    return fold(" ".join(toks)).replace("-", " ").replace("'", "").replace("\u2019", "").split()


def full_tokens(name):
    """Folded tokens of a metadata author name ('First Last' or 'Last, First')."""
    name = SUFFIX.sub("", name.strip())
    if "," in name:
        last, first = name.split(",", 1)
        name = first.strip() + " " + last.strip()
    return fold(name).replace("-", " ").replace("'", "").replace("\u2019", "").replace(".", " ").split()


def _match(st, ft):
    """Brief surname tokens st against metadata tokens ft: 'suffix' (ends with them), 'contains', or None."""
    if not st:
        return None
    n = len(st)
    if ft[-n:] == st:
        return "suffix"
    for k in range(len(ft) - n + 1):
        if ft[k:k + n] == st:
            return "contains"
    return None


def compare_authors(brief_raw, meta_authors):
    pa = parse_brief_authors(brief_raw)
    if pa["kind"] == "none":
        return {"class": "not-checked", "kind": "none", "missing": [], "n_brief": 0,
                "n_meta": len(meta_authors or [])}
    meta_authors = [a for a in meta_authors or [] if re.search(r"[A-Za-z\u00c0-\u024f]", a or "")]
    if not meta_authors:
        return {"class": "no-metadata", "kind": pa["kind"], "missing": [], "n_brief": len(pa["names"]), "n_meta": 0}
    if pa["kind"] == "collaboration":
        name = fold(pa["names"][0])
        listed = any(fold(a) == name or name in fold(a) for a in meta_authors)
        return {"class": "collaboration", "kind": "collaboration", "missing": [] if listed else pa["names"],
                "collaboration_listed": listed, "n_brief": 1, "n_meta": len(meta_authors)}
    ft = [full_tokens(a) for a in meta_authors]
    pos, missing, used = [], [], set()
    for nm in pa["names"]:
        st = surname_tokens(nm)
        free = [k for k in range(len(ft)) if k not in used]      # two authors of one surname: two places
        hit = next((k for k in free if _match(st, ft[k]) == "suffix"), None)
        if hit is None:
            hit = next((k for k in free if _match(st, ft[k])), None)
        if hit is None:
            missing.append(nm)
        else:
            used.add(hit)
        pos.append(hit)
    res = {"kind": pa["kind"], "missing": missing, "positions": pos, "n_brief": len(pa["names"]),
           "n_meta": len(meta_authors)}
    if missing:
        res["class"] = "mismatch"
    elif pa["kind"] == "include":
        res["class"] = "match"
    elif pa["kind"] == "first":
        res["class"] = "match" if pos[0] == 0 else "order"
    elif pa["kind"] == "etal":
        res["class"] = "match" if pos == list(range(len(pos))) else "order"
    else:
        if pos != list(range(len(pos))):
            res["class"] = "order"
        elif len(pa["names"]) < len(meta_authors):
            res["class"] = "incomplete"
        else:
            res["class"] = "match"
    return res


def compare_entry(entry, meta_title, meta_authors):
    t = compare_title(entry["title"], meta_title)
    a = compare_authors(entry["authors_raw"], meta_authors)
    agree = t["class"] in ("same", "format") and a["class"] in ("match", "not-checked", "collaboration")
    return {"title": t, "authors": a, "agree": agree}
