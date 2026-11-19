"""Independent TeX counter of the KB-G1 verifier (does not use kb/kbtool).

Reads an extracted arXiv source directory as untrusted DATA: nothing in it is executed,
compiled or imported. Finds the main file, flattens \\input-like commands, strips comments,
and counts display equations, sections and bibliography entries (see JOURNAL.md, test P).
"""
import os
import re

DISPLAY_ENVS = {
    "equation", "align", "eqnarray", "gather", "multline", "alignat", "flalign",
    "displaymath", "dmath", "dmath*", "IEEEeqnarray", "IEEEeqnarray*", "math",
}
DISPLAY_ENVS |= {e + "*" for e in list(DISPLAY_ENVS) if not e.endswith("*")}
DISPLAY_ENVS.discard("math")      # inline math environment, not a display
DISPLAY_ENVS.discard("math*")

MAX_FILE = 20_000_000


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read(MAX_FILE)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i = 0
        cut = None
        while True:
            j = line.find("%", i)
            if j < 0:
                break
            k = j - 1
            nb = 0
            while k >= 0 and line[k] == "\\":
                nb += 1
                k -= 1
            if nb % 2 == 0:
                cut = j
                break
            i = j + 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def strip_iffalse(text):
    """Remove \\iffalse ... \\fi blocks, counting nested \\if.. / \\fi."""
    tok = re.compile(r"\\iffalse(?![A-Za-z])|\\if[A-Za-z@]*(?![A-Za-z@])|\\fi(?![A-Za-z])")
    out = []
    pos = 0
    while True:
        m = re.search(r"\\iffalse(?![A-Za-z])", text[pos:])
        if not m:
            out.append(text[pos:])
            break
        start = pos + m.start()
        out.append(text[pos:start])
        depth = 0
        end = None
        for t in tok.finditer(text, start):
            s = t.group(0)
            if s == "\\fi":
                depth -= 1
                if depth == 0:
                    end = t.end()
                    break
            elif s.startswith("\\if"):
                # \ifx, \ifnum, \iffalse, \ifdefined, ... all open a conditional
                depth += 1
        if end is None:
            out.append(text[start:])
            break
        pos = end
    return "".join(out)


def strip_comment_env(text):
    return re.sub(r"\\begin\{comment\}.*?\\end\{comment\}", " ", text, flags=re.S)


def clean(text):
    return strip_comment_env(strip_iffalse(strip_comments(text)))


def tex_files(srcdir):
    res = []
    for root, dirs, files in os.walk(srcdir):
        for fn in files:
            p = os.path.join(root, fn)
            if os.path.islink(p):
                continue
            if fn.lower().endswith(".tex") or "." not in fn:
                res.append(p)
    return sorted(res)


def find_main(srcdir):
    cands = []
    for p in tex_files(srcdir):
        try:
            t = strip_comments(read_text(p))
        except OSError:
            continue
        if ("\\documentclass" in t or "\\documentstyle" in t) and "\\begin{document}" in t:
            cands.append(p)
    if not cands:
        # plain TeX (no \begin{document}): take the single largest TeX file
        files = tex_files(srcdir)
        if files:
            return max(files, key=os.path.getsize), []
        return None, []
    # Prefer a file that is not a supplement or response; then the largest.
    def key(p):
        b = os.path.basename(p).lower()
        bad = any(w in b for w in ("supp", "response", "reply", "cover", "letter"))
        return (bad, -os.path.getsize(p))
    cands.sort(key=key)
    return cands[0], cands


INPUT_RE = re.compile(
    r"\\(input|include|subfile)\s*\{([^}]*)\}"
    r"|\\(import|subimport|inputfrom|includefrom)\s*\{([^}]*)\}\s*\{([^}]*)\}"
    r"|\\input\s+([A-Za-z0-9_./-]+)")


def resolve(base_dirs, name):
    name = name.strip()
    for d in base_dirs:
        for cand in (name, name + ".tex"):
            p = os.path.normpath(os.path.join(d, cand))
            if os.path.isfile(p) and not os.path.islink(p):
                return p
    return None


def flatten(path, srcdir, depth=0, missing=None, seen=None):
    if missing is None:
        missing = []
    if seen is None:
        seen = set()
    if depth > 12 or path in seen:
        return "", missing
    seen = seen | {path}
    text = clean(read_text(path))
    here = os.path.dirname(path)
    out = []
    pos = 0
    for m in INPUT_RE.finditer(text):
        out.append(text[pos:m.start()])
        pos = m.end()
        if m.group(1):
            name, dirs = m.group(2), [srcdir, here]
        elif m.group(3):
            d = m.group(4)
            name, dirs = m.group(5), [os.path.join(srcdir, d), os.path.join(here, d)]
        else:
            name, dirs = m.group(6), [srcdir, here]
        if name.endswith(".bbl"):
            p = resolve(dirs, name)
        else:
            p = resolve(dirs, name)
        if p is None:
            missing.append(name)
            continue
        sub, _ = flatten(p, srcdir, depth + 1, missing, seen)
        out.append("\n" + sub + "\n")
    out.append(text[pos:])
    return "".join(out), missing


def body_of(flat):
    a = flat.find("\\begin{document}")
    b = flat.rfind("\\end{document}")
    if a < 0:
        return flat, ""
    pre = flat[:a]
    return flat[a:(b if b > a else len(flat))], pre


_ALIAS_T = r"(\\begin\{[^}]*\}|\\end\{[^}]*\}|\\\[|\\\]|\\nonumber|\\notag)"
ALIAS_RE = re.compile(
    r"\\(?:re)?newcommand\*?\s*\{?\\([A-Za-z]+)\}?\s*(?:\[\d\])?\s*\{\s*" + _ALIAS_T + r"\s*\}"
    r"|\\def\s*\\([A-Za-z]+)\s*\{\s*" + _ALIAS_T + r"\s*\}")


def aliases(pre_and_body):
    al = {}
    for m in ALIAS_RE.finditer(pre_and_body):
        name = m.group(1) or m.group(3)
        target = m.group(2) or m.group(4)
        al[name] = target
    return al


def expand_aliases(body, al):
    # Replace alias macros by their targets (text level only; nothing is executed).
    if not al:
        return body
    names = sorted(al, key=len, reverse=True)
    pat = re.compile(r"\\(" + "|".join(map(re.escape, names)) + r")(?![A-Za-z])")
    return pat.sub(lambda m: al[m.group(1)], body)


MULTIROW = {"align", "eqnarray", "gather", "alignat", "flalign", "IEEEeqnarray"}


def split_rows(content):
    """Split the content of a multi-row display at top-level \\\\ (outside braces and
    nested environments)."""
    rows, depth, envd, start, i = [], 0, 0, 0, 0
    n = len(content)
    while i < n:
        c = content[i]
        if c == "\\":
            if content.startswith("\\\\", i):
                if depth == 0 and envd == 0:
                    rows.append(content[start:i])
                    j = i + 2
                    # optional spacing argument \\[2pt] or \\*
                    if j < n and content[j] == "*":
                        j += 1
                    m = re.match(r"\s*\[[^\]]*\]", content[j:])
                    if m:
                        j += m.end()
                    start = j
                    i = j
                    continue
                i += 2
                continue
            if content.startswith("\\begin", i):
                envd += 1
            elif content.startswith("\\end", i):
                envd -= 1
            i += 2 if i + 1 < n and not content[i + 1].isalpha() else 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    rows.append(content[start:])
    return [r for r in rows if r.strip()]


def count_equations(body, al):
    """Return (environment counts, numbered rows, counter steps before \\appendix,
    per-environment list of (env, n_numbered_rows))."""
    body = expand_aliases(body, al)
    app = re.search(r"\\appendix(?![A-Za-z])|\\begin\{appendices\}", body)
    app_pos = app.start() if app else len(body)
    tok = re.compile(r"\\\\|\\\$|\\begin\s*\{([^}]*)\}|\\end\s*\{([^}]*)\}|\\\[|\\\]|\$\$")
    counts = {}
    closer = None
    envs = []          # (env, start, end of content)
    sub_depth = 0      # inside subequations
    sub_spans = []
    cur = None
    for m in tok.finditer(body):
        s = m.group(0)
        if s in ("\\\\", "\\$"):
            continue
        if closer is None:
            if m.group(1) is not None:
                env = m.group(1).strip()
                if env == "subequations":
                    sub_spans.append([m.start(), None])
                if env in DISPLAY_ENVS:
                    counts[env] = counts.get(env, 0) + 1
                    closer = ("end", env)
                    cur = (env, m.end())
            elif m.group(2) is not None and m.group(2).strip() == "subequations":
                if sub_spans and sub_spans[-1][1] is None:
                    sub_spans[-1][1] = m.end()
            elif s == "\\[":
                counts["\\["] = counts.get("\\[", 0) + 1
                closer = ("tok", "\\]")
                cur = ("\\[", m.end())
            elif s == "$$":
                counts["$$"] = counts.get("$$", 0) + 1
                closer = ("tok", "$$")
                cur = ("$$", m.end())
        else:
            if (closer[0] == "end" and m.group(2) is not None and m.group(2).strip() == closer[1]) \
                    or (closer[0] == "tok" and s == closer[1]):
                envs.append((cur[0], cur[1], m.start()))
                closer = None
    numbered = 0
    steps_main = 0
    steps_all = 0
    per_env = []
    for env, a, b in envs:
        content = body[a:b]
        base = env.rstrip("*")
        starred = env.endswith("*") or env in ("\\[", "$$", "displaymath")
        if base in MULTIROW:
            rows = split_rows(content)
        else:
            rows = [content]
        nnum = 0
        nstep = 0
        for r in rows:
            has_tag = re.search(r"\\tag\*?\s*\{", r) is not None
            nonum = re.search(r"\\(nonumber|notag)(?![A-Za-z])", r) is not None
            if has_tag:
                nnum += 1
            elif not starred and not nonum:
                nnum += 1
                nstep += 1
        if base == "multline" and not starred:
            # one number for the whole environment unless suppressed
            nnum = 0 if re.search(r"\\(nonumber|notag)(?![A-Za-z])", content) else 1
            nstep = nnum
        in_sub = any(sa <= a and (sb is None or a <= sb) for sa, sb in sub_spans)
        numbered += nnum
        if a < app_pos and not in_sub:
            steps_main += nstep
        if not in_sub:
            steps_all += nstep
        per_env.append((env, nnum))
    # each subequations block before the appendix steps the main counter once
    def has_num(sa, sb):
        return any(sa <= a and (sb is None or a <= sb) and n > 0
                   for (e, a, _), (_, n) in zip(envs, per_env))
    steps_main += sum(1 for sa, sb in sub_spans if sa < app_pos and has_num(sa, sb))
    steps_all += sum(1 for sa, sb in sub_spans if has_num(sa, sb))
    return counts, numbered, (steps_main, steps_all), per_env


def braced(text, i):
    """Return the content of the brace group starting at text[i] == '{'."""
    if i >= len(text) or text[i] != "{":
        return None, i
    depth = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == "\\":
            continue
        if c == "{" and (j == 0 or text[j - 1] != "\\"):
            depth += 1
        elif c == "}" and (j == 0 or text[j - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
    return None, len(text)


SEC_RE = re.compile(r"\\(section|subsection|subsubsection)(\*?)\s*(\[[^\]]*\])?\s*(?=\{)")
LEVEL = {"section": 1, "subsection": 2, "subsubsection": 3}


def sections(body):
    res = []
    for m in SEC_RE.finditer(body):
        title, _ = braced(body, m.end())
        res.append({"level": LEVEL[m.group(1)], "star": bool(m.group(2)),
                    "title": (title or "").strip(), "pos": m.start()})
    return res


def norm_title(t):
    t = re.sub(r"\\label\s*\{[^}]*\}", " ", t)
    t = re.sub(r"\$[^$]*\$", " ", t)
    t = re.sub(r"\\[A-Za-z]+\s*", " ", t)
    t = re.sub(r"[^A-Za-z0-9]+", "", t).lower()
    return t


CITE_RE = re.compile(r"\\[A-Za-z]*cite[A-Za-z]*\*?\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}")
BIBITEM_RE = re.compile(r"\\bibitem(?![A-Za-z])")
ENTRY_RE = re.compile(r"\\entry\{")


def bib_counts(srcdir, main, body):
    res = {}
    # inline thebibliography (also catches an \input-ed .bbl)
    n_inline = 0
    for m in re.finditer(r"\\begin\{thebibliography\}(.*?)\\end\{thebibliography\}", body, re.S):
        n_inline += len(BIBITEM_RE.findall(m.group(1)))
    res["thebibliography"] = n_inline
    # .bbl next to the main file
    mainbase = os.path.splitext(os.path.basename(main))[0]
    bbls = []
    for root, _, files in os.walk(srcdir):
        for fn in files:
            if fn.lower().endswith(".bbl"):
                bbls.append(os.path.join(root, fn))
    chosen = None
    for b in bbls:
        if os.path.splitext(os.path.basename(b))[0] == mainbase:
            chosen = b
    if chosen is None and len(bbls) == 1:
        chosen = bbls[0]
    if chosen is None and bbls:
        chosen = max(bbls, key=os.path.getsize)
    if chosen:
        t = strip_comments(read_text(chosen))
        res["bbl"] = len(BIBITEM_RE.findall(t)) + len(ENTRY_RE.findall(t))
        res["bbl_file"] = os.path.relpath(chosen, srcdir)
        res["bbl_all"] = [os.path.relpath(b, srcdir) for b in bbls]
    # .bib: distinct cited keys present in the named .bib files
    names = []
    for m in re.finditer(r"\\bibliography\s*\{([^}]*)\}|\\addbibresource\s*(?:\[[^\]]*\])?\{([^}]*)\}", body):
        for n in (m.group(1) or m.group(2)).split(","):
            if n.strip():
                names.append(n.strip())
    keys = set()
    found_files = []
    for n in names:
        p = resolve([srcdir, os.path.dirname(main)], n if n.endswith(".bib") else n + ".bib")
        if p is None:
            continue
        found_files.append(os.path.relpath(p, srcdir))
        t = read_text(p)
        for m in re.finditer(r"@\s*([A-Za-z]+)\s*[{(]\s*([^,\s]+)\s*,", t):
            if m.group(1).lower() in ("string", "comment", "preamble"):
                continue
            keys.add(m.group(2).strip())
    cited = set()
    nocite_all = False
    for m in CITE_RE.finditer(body):
        for k in m.group(1).split(","):
            k = k.strip()
            if k == "*":
                nocite_all = True
            elif k:
                cited.add(k)
    if found_files:
        res["bib_files"] = found_files
        res["bib_entries_total"] = len(keys)
        res["bib"] = len(keys) if nocite_all else len(keys & cited)
    res["cited_keys"] = len(cited)
    # AASTeX reference list: \begin{references} \reference{} ... \end{references}
    n_aas = 0
    for m in re.finditer(r"\\begin\{references\}(.*?)\\end\{references\}", body, re.S):
        n_aas += len(re.findall(r"\\reference(?![A-Za-z])", m.group(1)))
    res["aastex_references"] = n_aas
    # plain TeX: lines that start with \ref after the last "References" heading
    k = body.rfind("References")
    res["plain_ref_items"] = (len(re.findall(r"(?m)^\s*\\ref(?![A-Za-z])", body[k:])) if k >= 0 else 0)
    res["bibliography_cmd"] = names
    return res


def analyse(srcdir):
    main, cands = find_main(srcdir)
    if main is None:
        return {"error": "no main file"}
    flat, missing = flatten(main, srcdir)
    body, pre = body_of(flat)
    al = aliases(pre + body)
    eqs, numbered, steps_main, per_env = count_equations(body, al)
    # records under the rule "one record per numbered row, at least one per environment"
    n_rec = sum(max(1, n) for _, n in per_env)
    secs = sections(body)
    bib = bib_counts(srcdir, main, body)
    return {
        "main": os.path.relpath(main, srcdir),
        "main_candidates": [os.path.relpath(c, srcdir) for c in cands],
        "missing_inputs": missing,
        "aliases": al,
        "eq_by_env": eqs,
        "n_eq": sum(eqs.values()),
        "n_numbered": numbered,
        "n_steps_main": steps_main[0],
        "n_steps_all": steps_main[1],
        "n_rec_rule": n_rec,
        "sections": secs,
        "n_sec_by_level": {str(l): sum(1 for s in secs if s["level"] == l) for l in (1, 2, 3)},
        "bib": bib,
        "body_chars": len(body),
        "eqno": len(re.findall(r"\\l?eqno(?![A-Za-z])", body)),
    }
