"""K3 (brief 12.5): bibliography entries of a paper and the identifiers in them.

Order of preference of sources (brief 12.5): the .bbl, then the .bib, then a thebibliography
environment written in the TeX. A thebibliography environment that is part of the flattened
text IS the compiled bibliography (a pasted or \\input .bbl), so it is used first when the
paper has no \\bibliography command [JUDGEMENT; kb/JOURNAL.md].

Parsing is pure text processing (standard library). Identifiers extracted from each entry:
arXiv id (new form YYMM.NNNN[N], old form archive[.XX]/YYMMNNN, with or without version), DOI,
and the eprint field.
"""
import os
import re

from . import tex_files as F
from . import tex_macros as M
from . import tex_structure as S

OLD_ARCHIVES = ("astro-ph", "gr-qc", "hep-th", "hep-ph", "hep-ex", "hep-lat", "nucl-th", "nucl-ex", "math-ph",
                "math", "physics", "quant-ph", "cond-mat", "nlin", "cs", "q-bio", "q-fin", "stat", "chao-dyn",
                "solv-int", "patt-sol", "adap-org", "comp-gas", "acc-phys", "ao-sci", "atom-ph", "chem-ph",
                "plasm-ph", "supr-con", "mtrl-th", "funct-an", "alg-geom", "dg-ga", "q-alg", "bayes-an")
OLD_RE = re.compile(r"(?<![A-Za-z0-9\-])(" + "|".join(re.escape(a) for a in sorted(OLD_ARCHIVES, key=len, reverse=True))
                    + r")(?:\.[A-Z]{2})?/(\d{7})(v\d+)?(?!\d)", re.I)
NEW_PREFIXED_RE = re.compile(r"(?:arxiv\s*[:=]?\s*|arxiv\.org/(?:abs|pdf)/|eprint\s*[=:{]\s*\{?\s*\"?)"
                             r"(\d{4}\.\d{4,5})(v\d+)?(?!\d)", re.I)
NEW_CLASS_RE = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(v\d+)?\s*\[(?:astro-ph|gr-qc|hep|physics|math|quant|cond|nucl|"
                          r"cs|nlin|stat|q-bio)[^\]]*\]", re.I)
DOI_RE = re.compile(r"(?<![\w/])(10\.\d{4,9}/[^\s\"<>{}\\,]+)")


def valid_new_id(s):
    m = re.fullmatch(r"(\d\d)(\d\d)\.(\d{4,5})", s)
    if not m:
        return False
    yy, mm, num = int(m.group(1)), int(m.group(2)), m.group(3)
    if not 1 <= mm <= 12:
        return False
    if (yy, mm) < (7, 4):
        return False
    return len(num) == (4 if (yy, mm) < (15, 1) else 5)


def arxiv_ids(text):
    """arXiv identifiers in a bibliography entry, in order of appearance, without version."""
    found = []
    for m in OLD_RE.finditer(text):
        found.append((m.start(), f"{m.group(1).lower()}/{m.group(2)}"))
    for rx in (NEW_PREFIXED_RE, NEW_CLASS_RE):
        for m in rx.finditer(text):
            if valid_new_id(m.group(1)):
                found.append((m.start(1), m.group(1)))
    out = []
    for _, i in sorted(found):
        if i not in out:
            out.append(i)
    return out


def dois(text):
    out = []
    for m in DOI_RE.finditer(text.replace("\\_", "_").replace("{\\_}", "_")):
        d = m.group(1).rstrip(".;:)]}")
        if d.lower().startswith("10.48550/arxiv."):      # arXiv's own DOI: an arXiv id
            continue
        if d not in out:
            out.append(d)
    return out


def arxiv_from_doi(text):
    m = re.search(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})", text, re.I)
    return m.group(1) if m and valid_new_id(m.group(1)) else None


# ------------------------------------------------------------------ .bbl / thebibliography
BIBITEM_RE = re.compile(r"\\bibitem(?![A-Za-z@])")
# the commands that start one entry of a reference list: \bibitem[label]{key} (LaTeX, natbib,
# REVTeX, pandoc), \harvarditem[short]{authors}{year}{key} (harvard), \reference (AASTeX: no key)
ITEM_RE = re.compile(r"\\(bibitem|harvarditem|reference)(?![A-Za-z@])")
ENTRY_RE = re.compile(r"\\entry\s*\{([^{}]*)\}\s*\{([^{}]*)\}")      # biblatex .bbl
REF_ENV_RE = re.compile(r"\\begin\s*\{(" + "|".join(sorted(S.REF_ENVS, key=len, reverse=True)) + r")\}")
BIBITEM_TARGETS = ("bibitem", "harvarditem")


def expand_item_aliases(text, aliases):
    """Rewrite macros that stand for \\bibitem (tex_structure.command_aliases) into \\bibitem:
    a bare alias is renamed; a macro with the key as argument k is replaced by
    \\bibitem{<arg k>} followed by its other arguments, which are entry text."""
    if not aliases:
        return text
    pat = re.compile(r"\\(" + "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True))
                     + r")(?![A-Za-z@])")
    out, pos = [], 0
    for m in pat.finditer(text):
        if m.start() < pos:
            continue
        target, nargs, karg = aliases[m.group(1)]
        if karg is None:
            out.append(text[pos:m.start()] + "\\" + target)
            pos = m.end()
            continue
        a = S.command_args(text, m.end(), 0, nargs)
        if not a or len(a[1]) < karg:
            continue
        rest = " ".join(x for k, x in enumerate(a[1]) if k != karg - 1)
        out.append(text[pos:m.start()] + "\\%s{%s} %s" % (target, a[1][karg - 1], rest))
        pos = a[2]
    out.append(text[pos:])
    return "".join(out)


def ref_region(text):
    """(start, end, env) of the first reference-list environment in text whose body holds
    entry commands, or None."""
    for m0 in REF_ENV_RE.finditer(text):
        env = m0.group(1)
        start = m0.end()
        for _ in range(S.REF_ENVS[env]):
            g, e = M.read_group(text, start)
            if g is None:
                break
            start = e
        mend = re.compile(r"\\end\s*\{" + re.escape(env) + r"\}").search(text, start)
        end = mend.start() if mend else len(text)
        if ITEM_RE.search(text, start, end):
            return start, end, env
    return None


def parse_bbl(text, aliases=None):
    """Entries of a .bbl text or of a reference list written in the TeX: [{cite_key, raw, label}]
    in order. The list is the first reference-list environment (thebibliography, references,
    thereferences, CSLReferences) that holds entries, else the whole text. \\reference entries
    have no key: they get '#<n>' (n counts entries from 1), which no \\cite can name."""
    text = F.strip_comments_text(text)
    if ENTRY_RE.search(text) and "\\endentry" in text:
        return _parse_biblatex_bbl(text)
    text = expand_item_aliases(text, aliases)
    r = ref_region(text)
    region = text[r[0]:r[1]] if r else text
    items = list(ITEM_RE.finditer(region))
    out = []
    for k, m in enumerate(items):
        nxt = items[k + 1].start() if k + 1 < len(items) else len(region)
        kind = m.group(1)
        i = m.end()
        g, j = M.read_group(region, i, "[", "]")
        label = None
        if g is not None:
            label, i = g, j
        if kind == "reference":
            g, j = M.read_group(region, i)            # AASTeX writes \reference{} (empty group)
            if g is not None and not g.strip():
                i = j
            raw = region[i:nxt].strip()
            if raw:
                out.append({"cite_key": f"#{len(out) + 1}", "raw": raw, "label": label, "item": kind})
            continue
        if kind == "harvarditem":
            a = S.command_args(region, i, 0, 3)
            if not a:
                continue
            authors, year, key = a[1]
            label = (f"{label} " if label else "") + f"{authors} {year}".strip()
            raw = region[a[2]:nxt].strip()
            out.append({"cite_key": key.strip(), "raw": raw, "label": label, "item": kind})
            continue
        key, j = M.read_group(region, i)
        if key is None:
            continue
        raw = region[j:nxt].strip()
        out.append({"cite_key": key.strip(), "raw": raw, "label": label, "item": kind})
    return out


def _parse_biblatex_bbl(text):
    out = []
    for m in ENTRY_RE.finditer(text):
        e = text.find("\\endentry", m.end())
        raw = text[m.end():e if e > 0 else len(text)]
        fields = {}
        for f in re.finditer(r"\\field\s*\{([^{}]*)\}\s*\{", raw):
            g, _ = M.read_group(raw, f.end() - 1)
            if g is not None:
                fields[f.group(1)] = g
        for v in re.finditer(r"\\verb\s*\{([^{}]*)\}\s*\n?\s*\\verb\s+(.*?)\n?\s*\\endverb", raw, re.S):
            fields.setdefault(v.group(1), v.group(2).strip())
        out.append({"cite_key": m.group(1).strip(), "raw": raw.strip(), "fields": fields})
    return out


# ------------------------------------------------------------------ .bib
def parse_bib(text):
    """A tolerant BibTeX parser (standard library): [{cite_key, type, fields, raw}].
    @string, @preamble and @comment are skipped; field values keep their inner braces."""
    out = []
    i, n = 0, len(text)
    while True:
        m = re.compile(r"@\s*([A-Za-z]+)\s*([{(])").search(text, i)
        if not m:
            break
        typ = m.group(1).lower()
        open_ = m.group(2)
        # find the matching close at brace depth 0
        depth, k = 0, m.end()
        while k < n:
            c = text[k]
            if c == "\\":
                k += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                if depth == 0 and open_ == "{":
                    break
                depth -= 1
            elif c == ")" and open_ == "(" and depth == 0:
                break
            k += 1
        body = text[m.end():k]
        i = k + 1
        if typ in ("string", "preamble", "comment"):
            continue
        km = re.match(r"\s*([^,\s]+)\s*,", body)
        if not km:
            continue
        key = km.group(1)
        fields = {}
        j = km.end()
        while j < len(body):
            fm = re.compile(r"\s*([A-Za-z][\w\-:.]*)\s*=\s*").match(body, j)
            if not fm:
                # junk such as `//eprint = "..."` (not BibTeX): skip to the next comma at depth 0
                nxt = _next_comma(body, j)
                if nxt is None:
                    break
                j = nxt + 1
                continue
            name = fm.group(1).lower()
            j = fm.end()
            val, j = _bib_value(body, j)
            if val is None:
                break
            while True:                                   # concatenation with #
                cm = re.compile(r"\s*#\s*").match(body, j)
                if not cm:
                    break
                more, j = _bib_value(body, cm.end())
                if more is None:
                    break
                val += more
            fields[name] = val.strip()
            cm = re.compile(r"\s*,").match(body, j)
            if cm:
                j = cm.end()
            else:
                break
        out.append({"cite_key": key, "type": typ, "fields": fields, "raw": text[m.start():i]})
    return out


def _next_comma(body, j):
    depth = 0
    while j < len(body):
        c = body[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "," and depth == 0:
            return j
        j += 1
    return None


def _bib_value(body, j):
    """One BibTeX value at body[j:]: {braced}, "quoted" or a bare word. Returns (text, end)."""
    if j < len(body) and body[j] == "{":
        g, e = M.read_group(body, j)
        return (g, e) if g is not None else (None, j)
    if j < len(body) and body[j] == '"':
        e, depth = j + 1, 0
        while e < len(body):
            c = body[e]
            if c == "\\":
                e += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            elif c == '"' and depth == 0:
                break
            e += 1
        return body[j + 1:e], e + 1
    vm = re.compile(r"[^,}#\s]+").match(body, j)
    return (vm.group(0), vm.end()) if vm else ("", j)


def bib_entry_ids(e):
    """(arxiv, doi, eprint_field) of a .bib entry."""
    f = e.get("fields", {})
    eprint = f.get("eprint", "").strip()
    arx = None
    pref = (f.get("archiveprefix") or f.get("eprinttype") or "").lower()
    if eprint:
        cand = re.sub(r"^arxiv:", "", eprint, flags=re.I).strip()
        cand = re.sub(r"v\d+$", "", cand)
        if valid_new_id(cand) or OLD_RE.fullmatch(cand):
            arx = cand.lower() if "/" in cand else cand
        elif pref == "arxiv" and arxiv_ids(cand):
            arx = arxiv_ids(cand)[0]
    if arx is None:
        ids = arxiv_ids(" ".join(f.get(k, "") for k in ("journal", "note", "url", "howpublished", "pages",
                                                        "volume", "archiveprefix", "eprint")))
        if ids:
            arx = ids[0]
    if arx is None:
        arx = arxiv_from_doi(f.get("doi", ""))
    doi = None
    if f.get("doi"):
        d = dois(f["doi"]) or [f["doi"].strip()]
        doi = d[0] if d and not d[0].lower().startswith("10.48550/") else None
    if doi is None:
        ds = dois(" ".join(f.get(k, "") for k in ("url", "note")))
        doi = ds[0] if ds else None
    return arx, doi, eprint or None


def bbl_entry_ids(e):
    raw = e["raw"]
    f = e.get("fields") or {}
    text = raw + " " + " ".join(f.values())
    ids = arxiv_ids(text)
    ep = re.sub(r"v\d+$", "", (f.get("eprint") or "").strip())
    if ep and (valid_new_id(ep) or OLD_RE.fullmatch(ep)) and ep.lower() not in [i.lower() for i in ids]:
        ids.insert(0, ep.lower() if "/" in ep else ep)          # biblatex \field{eprint}{<bare id>}
    arx = ids[0] if ids else arxiv_from_doi(text)
    ds = dois(text)
    eprint = f.get("eprint")
    if eprint is None:
        me = re.search(r"\\(?:eprint|Eprint)\s*(?:\{[^{}]*\}\s*)?\{([^{}]*)\}", raw)
        eprint = me.group(1).strip() if me else None
    return arx, (ds[0] if ds else None), eprint, len(ids)


def entry_title(e):
    """A title for fuzzy matching, when the entry has one."""
    f = e.get("fields") or {}
    if f.get("title"):
        return re.sub(r"[{}\\]", "", f["title"]).strip()
    m = re.search(r"\\bibinfo\s*\{title\}\s*\{", e["raw"])
    if m:
        g, _ = M.read_group(e["raw"], m.end() - 1)
        if g:
            return re.sub(r"[{}\\]", "", g).strip()
    m = re.search(r"``(.+?)''", e["raw"], re.S)
    if m:
        return re.sub(r"[{}\\]", "", m.group(1)).strip()
    return None


# ------------------------------------------------------------------ old-style lists under a heading
# Package ingest4 (wave 3 batch 11): papers of the 1990s written in plain TeX or early LaTeX put
# their references under a heading ("References", centred or bold) with no environment: an
# enumerate list of \item, paragraphs that start with [n], or paragraphs started by a macro of
# the paper (A&A's \ref, a \refh or \i\Key with a hanging indent). They cite with [n], with a
# macro that wraps its argument in brackets (\r{\Key,...}, \Key defined as a number), or by author
# and year. Used only when no other source gives an entry.
HEAD_WORDS_RE = re.compile(r"(?:references?|reference\s+list|bibliography|literature(?:\s+cited)?)[.:]?", re.I)
STOP_HEAD_RE = re.compile(r"(?:figures?|tables?)(?:\s+(?:and\s+tables?\s+)?captions?)?|captions?(?:\s+(?:to|of)"
                          r"(?:\s+the)?\s+(?:figures?|tables?))?|figure\s+legends?|appendix(?:\s+\w+)?|"
                          r"footnotes?|notes", re.I)
_DIM_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)\s*(?:true)?(?:cm|mm|pt|in|em|ex|bp|pc|sp)(?![A-Za-z])")
_ENV_CMD_RE = re.compile(r"\\(?:begin|end)\s*\{[^{}]*\}")
_CS_RE = re.compile(r"\\[A-Za-z@]+\*?|\\.")
_LIST_ENVS = ("enumerate", "itemize", "description")
_LIST_END_RE = re.compile(r"\\end\s*\{(?:" + "|".join(_LIST_ENVS) + r")\}")
_REGION_END_RE = re.compile(r"\\end\s*\{document\}|\\bye(?![A-Za-z@])|^[ \t]*\\end(?![A-Za-z@{])|"
                            r"\\endref(?![A-Za-z@])|\\begin\s*\{(?:figure|table)\*?\}", re.M)
_BRACKET_LINE_RE = re.compile(r"^[ \t]*(?:\\(?:noindent|par|indent|item|next)(?![A-Za-z@])\s*)*\[(\d{1,3})\]", re.M)
_ITEM_RE = re.compile(r"\\item(?![A-Za-z@])")
_LINE_CS_RE = re.compile(r"^[ \t]*\\([A-Za-z@]+)(?![A-Za-z@])", re.M)
# paragraph-starting macros of reference lists in plain-TeX journal styles, accepted without a
# definition in the source (A&A's \ref is defined in aa.cmm, often not shipped)
KNOWN_PAR_MACROS = {"ref", "refh", "rf", "refer", "refa", "rfr", "bibi"}
# a macro defined in the paper starts a paragraph when its body sets one of these
_PAR_BODY_RE = re.compile(r"\\(?:par|hang|hangindent|hangafter|noindent|indent|item|everypar)(?![A-Za-z@])")
_NOT_ENTRY_MACROS = {"noindent", "par", "item", "indent", "vskip", "smallskip", "medskip", "bigskip", "hfill",
                     "hfil", "vfill", "vfil", "eject", "end", "begin", "centerline", "line", "leftline",
                     "bf", "it", "rm", "sl", "sc", "tt", "em", "frenchspacing", "hangindent", "hang",
                     "parindent", "goodbreak", "newpage", "clearpage", "break", "filbreak", "penalty",
                     "bigbreak", "medbreak", "smallbreak", "nobreak", "next", "endref", "begref", "relax",
                     "baselineskip", "parskip", "def", "let", "font", "small", "footnotesize", "large",
                     "Large", "normalsize", "noindent", "vspace", "hspace", "newline", "obeylines"}


def heading_text(line):
    """The words of a line once control words, environment commands, braces and dimensions
    are dropped: `{\\Large \\noindent \\bf References}` -> 'References'."""
    s = _ENV_CMD_RE.sub(" ", line)
    s = _DIM_RE.sub(" ", s)
    s = _CS_RE.sub(" ", s)
    s = re.sub(r"[{}\[\]$&=~]", " ", s)
    return " ".join(s.split())


def _lines(text, lo, hi):
    for m in re.finditer(r"[^\n]*", text[lo:hi]):
        if m.start() == m.end() and m.start() > 0 and text[lo + m.start() - 1:lo + m.start()] != "\n":
            continue
        yield lo + m.start(), lo + m.end(), m.group(0)


def _clean_raw(raw):
    """Entry text without the spacing and separator commands around it and without an unmatched
    closing brace of a group that wrapped the whole list."""
    raw = raw.strip()
    prev = None
    while raw != prev:
        prev = raw
        raw = re.sub(r"(?:\s*\\(?:par|noindent|next|smallskip|medskip|bigskip|vskip\s*\S+|goodbreak|endref|"
                     r"vfill|vfil|eject|newpage|item|bigbreak|medbreak|smallbreak|filbreak|break|hfill|hfil)(?![A-Za-z@]))+\s*$", "", raw).strip()
        if raw.endswith("}") and raw.count("}") > raw.count("{"):
            raw = raw[:-1].strip()
    return raw


def _number_of(arg, macros):
    """A citation key written as digits or as a macro whose body is digits (\\def\\Guth{1})."""
    a = (arg or "").strip()
    if re.fullmatch(r"\d{1,3}", a):
        return a
    m = re.fullmatch(r"\\([A-Za-z@]+)", a)
    if m and macros and m.group(1) in macros:
        spec = macros[m.group(1)]
        if not spec.get("nargs") and re.fullmatch(r"\s*\d{1,3}\s*", spec.get("body", "")):
            return spec["body"].strip()
    return None


def heading_reference_list(flat, struct=None, macros=None):
    """An old-style reference list: the last line of the body whose words are a 'References'
    heading starts it; it ends at \\end{document}, \\bye, a plain \\end, \\endref, a figure or
    table environment, or a line whose words are a caption or appendix heading. Entries, in this
    order of preference: \\item (keys 1, 2, ... or the [label]); lines that start with [n]
    (key n); paragraphs started by one macro used at least 3 times at the start of a line, either
    defined in the paper with a hanging indent or \\par, or a known journal macro (\\ref, \\refh):
    a one-argument macro takes its argument as key (a macro whose body is a number gives that
    number), a macro without argument gives '#<n>'. Returns None or dict(start, end, heading_at,
    heading, style, entries)."""
    macros = macros if macros is not None else M.collect(flat)
    lo = (struct or {}).get("body_start") or 0
    hi = (struct or {}).get("body_end") or len(flat)
    head = None
    for a, b, line in _lines(flat, lo, hi):
        t = heading_text(line)
        if t and HEAD_WORDS_RE.fullmatch(t) and len(line.strip()) < 120:
            head = (a, b, t)
    if head is None:
        return None
    start = head[1]
    end = hi
    m = _REGION_END_RE.search(flat, start, hi)
    if m:
        end = m.start()
    for a, b, line in _lines(flat, start, end):
        t = heading_text(line)
        if t and len(t.split()) <= 5 and STOP_HEAD_RE.fullmatch(t) and not _BRACKET_LINE_RE.match(line):
            end = a
            break
    region = flat[start:end]
    entries, style = [], None
    items = list(_ITEM_RE.finditer(region))
    if len(items) >= 2:
        style = "item"
        for k, mi in enumerate(items):
            nxt = items[k + 1].start() if k + 1 < len(items) else len(region)
            if k + 1 == len(items):
                me = _LIST_END_RE.search(region, mi.end())
                if me:
                    nxt = me.start()
            i = mi.end()
            g, j = M.read_group(region, i, "[", "]")
            label = None
            if g is not None:
                label, i = g, j
            key = re.sub(r"[^\d]", "", label) if label and re.fullmatch(r"\W*\d{1,3}\W*", label) else str(k + 1)
            raw = _clean_raw(region[i:nxt])
            if raw:
                entries.append({"cite_key": key, "raw": raw, "label": label, "item": "heading-item"})
        end = start + (items[-1].end() + (len(entries[-1]["raw"]) if entries else 0))
        me = _LIST_END_RE.search(region, items[-1].end())
        if me:
            end = start + me.end()
    if not entries:
        marks = list(_BRACKET_LINE_RE.finditer(region))
        if len(marks) >= 2:
            style = "bracket"
            for k, mb in enumerate(marks):
                nxt = marks[k + 1].start() if k + 1 < len(marks) else len(region)
                raw = _clean_raw(region[mb.end():nxt])
                if raw:
                    entries.append({"cite_key": mb.group(1), "raw": raw, "label": f"[{mb.group(1)}]",
                                    "item": "heading-bracket"})
    if not entries:
        counts = {}
        for mc in _LINE_CS_RE.finditer(region):
            name = mc.group(1)
            if name in _NOT_ENTRY_MACROS:
                continue
            spec = macros.get(name)
            if spec is not None:
                ok = spec.get("nargs", 0) <= 1 and bool(_PAR_BODY_RE.search(spec.get("body", "")))
            else:
                ok = name in KNOWN_PAR_MACROS and region[mc.end():mc.end() + 1] != "{"
            if ok:
                counts[name] = counts.get(name, 0) + 1
        best = max(counts.items(), key=lambda x: (x[1], x[0]))[0] if counts else None
        if best and counts[best] >= 3:
            style = "macro:\\" + best
            nargs = (macros.get(best) or {}).get("nargs", 0) or 0
            pat = re.compile(r"^[ \t]*\\" + re.escape(best) + r"(?![A-Za-z@])", re.M)
            marks = list(pat.finditer(region))
            for k, mm in enumerate(marks):
                nxt = marks[k + 1].start() if k + 1 < len(marks) else len(region)
                i, key, label = mm.end(), None, None
                if nargs == 1:
                    arg, j = M.read_arg(region, i)
                    if arg is not None:
                        label = arg.strip()
                        key = _number_of(label, macros) or label
                        i = j
                raw = _clean_raw(region[i:nxt])
                if raw:
                    entries.append({"cite_key": key or f"#{len(entries) + 1}", "raw": raw, "label": label,
                                    "item": "heading-macro"})
    if not entries:
        return None
    return {"start": start, "end": end, "heading_at": head[0], "heading": head[2], "style": style,
            "entries": entries}


_BRACKET_CITE_RE = re.compile(r"\[\s*(\d{1,3}(?:\s*(?:,|--?|–|—)\s*\d{1,3})*)\s*\]")


def _expand_numbers(items, macros, valid):
    """'1,3--5' (or macros standing for numbers) -> ['1', '3', '4', '5'], or None when any part
    is not a key of the list."""
    out = []
    for part in re.split(r"\s*,\s*", items.strip()):
        if not part:
            continue
        rng = re.split(r"\s*(?:--?|–|—)\s*", part)
        nums = [_number_of(x, macros) for x in rng]
        if any(n is None for n in nums) or len(nums) > 2:
            return None
        if len(nums) == 2:
            a, b = int(nums[0]), int(nums[1])
            if not 0 < a <= b or b - a > 50:
                return None
            nums = [str(n) for n in range(a, b + 1)]
        out += nums
    if not out or any(n not in valid for n in out):
        return None
    return out


def _math_mask(flat, lo, hi, struct):
    """Intervals of display math (from the structure) and of inline $..$ and \\(..\\) in [lo, hi)."""
    spans = [(s["start"], s["end"]) for s in (struct or {}).get("math_spans", [])]
    text = flat[lo:hi]
    k, n = 0, len(text)
    while k < n:
        c = text[k]
        if c == "\\":
            if text.startswith("\\(", k):
                e = text.find("\\)", k + 2)
                if e > 0:
                    spans.append((lo + k, lo + e + 2))
                    k = e + 2
                    continue
            k += 2
            continue
        if c == "$":
            dbl = text.startswith("$$", k)
            e = text.find("$$" if dbl else "$", k + (2 if dbl else 1))
            if e < 0:
                break
            spans.append((lo + k, lo + e + (2 if dbl else 1)))
            k = e + (2 if dbl else 1)
            continue
        k += 1
    return sorted(spans)


def numeric_citations(flat, struct, macros, keys, hi):
    """Citations of an old-style list in the text before it: [n], [n,m], [n--m] outside math and
    not the optional argument of a command; a one-argument macro whose body only wraps #1 in
    brackets or a superscript (\\def\\r#1{[#1]}) with numbers or number macros as argument.
    Every number must be a key of the list. Returns cite records like tex_structure.extract's."""
    valid = set(keys)
    lo = (struct or {}).get("body_start") or 0
    mask = _math_mask(flat, lo, hi, struct)
    secs = [(s["start"], k) for k, s in enumerate((struct or {}).get("sections", []))]

    def inside(p):
        for a, b in mask:
            if a <= p < b:
                return True
            if a > p:
                break
        return False

    def section_at(p):
        cur = None
        for s0, k in secs:
            if s0 <= p:
                cur = k
        return cur

    out = []
    for m in _BRACKET_CITE_RE.finditer(flat, lo, hi):
        if inside(m.start()) or re.search(r"\\[A-Za-z@]+\*?\s*$|\\\\\s*$", flat[max(lo, m.start() - 40):m.start()]):
            continue
        nums = _expand_numbers(m.group(1), macros, valid)
        if nums:
            out.append({"cmd": "bracket", "keys": nums, "start": m.start(), "end": m.end(),
                        "section": section_at(m.start()), "nocite": False, "old_style": True})
    wraps = [name for name, spec in (macros or {}).items() if spec.get("nargs") == 1 and "#1" in spec.get("body", "")
             and re.fullmatch(r"[\s\[\]{}^$]*", spec["body"].replace("#1", "")) and re.search(r"[\[^]", spec["body"])]
    if wraps:
        pat = re.compile(r"\\(" + "|".join(re.escape(w) for w in sorted(wraps, key=len, reverse=True)) + r")(?![A-Za-z@])")
        for m in pat.finditer(flat, lo, hi):
            if S._is_definition(flat, m.start()):
                continue
            arg, j = M.read_arg(flat, m.end())
            if arg is None:
                continue
            nums = _expand_numbers(arg, macros, valid)
            if nums:
                out.append({"cmd": m.group(1), "keys": nums, "start": m.start(), "end": j,
                            "section": section_at(m.start()), "nocite": False, "old_style": True})
    out.sort(key=lambda c: c["start"])
    return out


# ------------------------------------------------------------------ choice of source
def _cited_keys(struct):
    return {k for c in struct.get("cites", []) if not c.get("nocite") for k in c["keys"] if k != "*"}


def unreached_reference_file(root, reached, cited, aliases):
    """A .tex file of the source that the main file does not reach and that holds a reference
    list with entries for keys the paper cites: (relative name, entries) or (None, [])."""
    best, best_entries, best_hits = None, [], 0
    reached = {r["file"] if isinstance(r, dict) else r for r in (reached or [])}
    for f in F.list_files(root):
        if not f.lower().endswith(".tex") or f in reached:
            continue
        p = F.safe_join(root, f)
        if not p:
            continue
        try:
            text = F.read_text(p)[0]
        except OSError:
            continue
        text = F.strip_comments_text(text)
        al = dict(aliases or {})
        al.update(S.command_aliases(M.collect(text), BIBITEM_TARGETS))
        text = expand_item_aliases(text, al)
        r = ref_region(text)
        if not r:
            continue
        entries = parse_bbl(text[r[0]:r[1]])
        hits = len(cited & {e["cite_key"] for e in entries})
        if hits > best_hits:
            best, best_entries, best_hits = f, entries, hits
    return best, best_entries


def bibliography(root, main_rel, flat, struct, macros=None, reached=None):
    """Entries of the paper with their identifiers. Returns dict(source, files, entries, notes,
    cited_keys, cited_with_entry, unreached_file). `macros` (tex_macros.collect of the flat text)
    gives the macros that stand for \\bibitem; `reached` lists the files the flattening read."""
    notes = []
    files = F.list_files(root)
    main_stem = os.path.splitext(main_rel)[0] if main_rel else None
    has_bibcmd = bool(struct.get("bibliography_files")) or bool(re.search(r"\\addbibresource|\\bibliography\s*\{",
                                                                          flat))
    aliases = S.command_aliases({**S.xparse_macros(flat), **(macros if macros is not None else M.collect(flat))},
                                BIBITEM_TARGETS)
    if aliases:
        notes.append("macros standing for an entry command: " +
                     ", ".join(f"\\{k} -> \\{v[0]}" for k, v in sorted(aliases.items())))
    xflat = expand_item_aliases(flat, aliases)
    reg = ref_region(xflat)
    if reg and reg[2] != "thebibliography":
        notes.append(f"reference list in a {reg[2]} environment")
    inline = reg is not None
    unreached = None
    bbls = [f for f in files if f.lower().endswith(".bbl")]
    chosen_bbl = None
    if main_stem and main_stem + ".bbl" in bbls:
        chosen_bbl = main_stem + ".bbl"
    elif len(bbls) == 1:
        chosen_bbl = bbls[0]
    elif bbls:
        chosen_bbl = max(bbls, key=lambda f: os.path.getsize(os.path.join(root, f)))
        notes.append(f"{len(bbls)} .bbl files; took the largest, {chosen_bbl}")
    entries, source, used = [], None, []
    if inline and not has_bibcmd:
        entries = parse_bbl(xflat[reg[0]:reg[1]])
        source = "thebibliography"
    elif chosen_bbl and has_bibcmd:
        p = F.safe_join(root, chosen_bbl)
        entries = parse_bbl(F.read_text(p)[0], aliases) if p else []
        source, used = "bbl", [chosen_bbl]
    if not entries and has_bibcmd:
        names = [b if b.endswith(".bib") else b + ".bib" for b in struct.get("bibliography_files", [])]
        bibs = [n for n in names if F.safe_join(root, n)]
        missing = [n for n in names if not F.safe_join(root, n)]
        if missing:
            notes.append(f"named .bib files not in the source: {', '.join(missing)}")
        if not bibs:
            bibs = [f for f in files if f.lower().endswith(".bib")]
        allb = []
        for b in bibs:
            allb += parse_bib(F.read_text(F.safe_join(root, b))[0])
        if allb:
            cited = {k for c in struct.get("cites", []) for k in c["keys"]}
            nocite_all = "*" in cited
            byk = {}
            for e in allb:
                byk.setdefault(e["cite_key"], e)
            entries = [e for k, e in byk.items() if nocite_all or k in cited]
            source, used = "bib", bibs
            notes.append(f".bib entries: {len(allb)} parsed, {len(entries)} cited")
    if not entries and inline:
        entries = parse_bbl(xflat[reg[0]:reg[1]])
        source = "thebibliography"
    if not entries and chosen_bbl:
        p = F.safe_join(root, chosen_bbl)
        entries = parse_bbl(F.read_text(p)[0], aliases) if p else []
        source, used = "bbl", [chosen_bbl]
        if entries:
            notes.append("used a .bbl although the TeX has no \\bibliography command")
    cited = _cited_keys(struct)
    if not entries and cited and reached is not None:
        f, ents = unreached_reference_file(root, reached, cited, aliases)
        if f:
            entries, source, used, unreached = ents, "thebibliography", [f], f
            notes.append(f"reference list taken from {f}, a file the main file does not reach "
                         f"(the paper cites and has no other entry)")
    heading, old_cites = None, []
    if not entries:
        hl = heading_reference_list(flat, struct, macros if macros is not None else M.collect(flat))
        if hl:
            entries, source = hl["entries"], "heading"
            heading = {k: hl[k] for k in ("start", "end", "heading_at", "heading", "style")}
            notes.append(f"old-style reference list under the heading '{hl['heading']}' "
                         f"({hl['style']}, {len(entries)} entries)")
            old_cites = numeric_citations(flat, struct, macros if macros is not None else M.collect(flat),
                                          [e["cite_key"] for e in entries], hl["heading_at"])
            if old_cites:
                notes.append(f"{len(old_cites)} citations by number ([n] or a bracket macro)")
                cited = cited | {k for c in old_cites for k in c["keys"]}
    for e in entries:
        if source == "bib":
            arx, doi, eprint = bib_entry_ids(e)
            n_ids = 1 if arx else 0
        else:
            arx, doi, eprint, n_ids = bbl_entry_ids(e)
        e.update({"arxiv": arx, "doi": doi, "eprint": eprint, "n_arxiv_ids": n_ids, "title": entry_title(e)})
    keys = {e["cite_key"] for e in entries}
    return {"source": source, "files": used, "entries": entries, "notes": notes, "cited_keys": len(cited),
            "cited_with_entry": len(cited & keys), "unreached_file": unreached, "heading_list": heading,
            "old_cites": old_cites}
