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
ENTRY_RE = re.compile(r"\\entry\s*\{([^{}]*)\}\s*\{([^{}]*)\}")      # biblatex .bbl


def parse_bbl(text):
    """Entries of a .bbl or thebibliography text: [{cite_key, raw}] in order."""
    text = F.strip_comments_text(text)
    if ENTRY_RE.search(text) and "\\endentry" in text:
        return _parse_biblatex_bbl(text)
    m0 = re.search(r"\\begin\s*\{thebibliography\}", text)
    if m0:
        g, e = M.read_group(text, m0.end())
        start = e if g is not None else m0.end()
    else:
        start = 0
    mend = re.search(r"\\end\s*\{thebibliography\}", text[start:])
    end = start + mend.start() if mend else len(text)
    region = text[start:end]
    items = list(BIBITEM_RE.finditer(region))
    out = []
    for k, m in enumerate(items):
        nxt = items[k + 1].start() if k + 1 < len(items) else len(region)
        i = m.end()
        g, j = M.read_group(region, i, "[", "]")
        label = None
        if g is not None:
            label, i = g, j
        key, j = M.read_group(region, i)
        if key is None:
            continue
        raw = region[j:nxt].strip()
        out.append({"cite_key": key.strip(), "raw": raw, "label": label})
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
                break
            name = fm.group(1).lower()
            j = fm.end()
            if j < len(body) and body[j] == "{":
                g, e = M.read_group(body, j)
                if g is None:
                    break
                val, j = g, e
            elif j < len(body) and body[j] == '"':
                e = j + 1
                depth = 0
                while e < len(body):
                    if body[e] == "\\":
                        e += 2
                        continue
                    if body[e] == "{":
                        depth += 1
                    elif body[e] == "}":
                        depth -= 1
                    elif body[e] == '"' and depth == 0:
                        break
                    e += 1
                val, j = body[j + 1:e], e + 1
            else:
                vm = re.compile(r"[^,}\s]+").match(body, j)
                val = vm.group(0) if vm else ""
                j = vm.end() if vm else j
            # concatenation with #
            while True:
                cm = re.compile(r"\s*#\s*").match(body, j)
                if not cm:
                    break
                j = cm.end()
                if j < len(body) and body[j] == "{":
                    g, e = M.read_group(body, j)
                    val += g or ""
                    j = e
                else:
                    vm = re.compile(r"[^,}\s]+").match(body, j)
                    j = vm.end() if vm else j
            fields[name] = val.strip()
            cm = re.compile(r"\s*,").match(body, j)
            if cm:
                j = cm.end()
            else:
                break
        out.append({"cite_key": key, "type": typ, "fields": fields, "raw": text[m.start():i]})
    return out


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


# ------------------------------------------------------------------ choice of source
def bibliography(root, main_rel, flat, struct):
    """Entries of the paper with their identifiers. Returns dict(source, files, entries, notes)."""
    notes = []
    files = F.list_files(root)
    main_stem = os.path.splitext(main_rel)[0] if main_rel else None
    has_bibcmd = bool(struct.get("bibliography_files")) or bool(re.search(r"\\addbibresource|\\bibliography\s*\{",
                                                                          flat))
    inline = re.search(r"\\begin\s*\{thebibliography\}", flat)
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
        entries = parse_bbl(flat[inline.start():])
        source = "thebibliography"
    elif chosen_bbl and has_bibcmd:
        p = F.safe_join(root, chosen_bbl)
        entries = parse_bbl(F.read_text(p)[0]) if p else []
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
        entries = parse_bbl(flat[inline.start():])
        source = "thebibliography"
    if not entries and chosen_bbl:
        p = F.safe_join(root, chosen_bbl)
        entries = parse_bbl(F.read_text(p)[0]) if p else []
        source, used = "bbl", [chosen_bbl]
        if entries:
            notes.append("used a .bbl although the TeX has no \\bibliography command")
    for e in entries:
        if source == "bib":
            arx, doi, eprint = bib_entry_ids(e)
            n_ids = 1 if arx else 0
        else:
            arx, doi, eprint, n_ids = bbl_entry_ids(e)
        e.update({"arxiv": arx, "doi": doi, "eprint": eprint, "n_arxiv_ids": n_ids, "title": entry_title(e)})
    return {"source": source, "files": used, "entries": entries, "notes": notes}
