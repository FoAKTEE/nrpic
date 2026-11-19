"""K2 step 5 (brief 12.4): structure of a flattened, comment-free LaTeX document.

Title, authors, abstract; the section tree (number, title, label, character range); display
equations (equation, align, gather, multline, eqnarray, flalign, alignat, \\[ \\], $$) with
label, number and enclosing section; figures and tables (caption, label, files, number);
footnotes; appendices; every \\cite with its keys and offset; the labels map.

All offsets are character offsets into the flattened text that is stored as flat.tex.
Numbers follow the LaTeX counters as this module computes them [JUDGEMENT; checked against
LaTeX's own .aux on synthetic documents in tests/test_tex_numbering.py]: one equation
counter, reset per section with \\numberwithin{equation}{section}; REVTeX numbers appendix
equations A1, A2, ...; subequations give 3a, 3b; \\tag{x} gives x; one number per line of
align, gather, eqnarray, flalign, alignat unless \\nonumber or \\notag; one per multline.
"""
import re

from . import tex_macros as M

DISPLAY_ENVS = {"equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*",
                "eqnarray", "eqnarray*", "flalign", "flalign*", "alignat", "alignat*", "displaymath",
                "dmath", "dmath*", "dgroup", "dgroup*", "IEEEeqnarray", "IEEEeqnarray*"}
MULTILINE_ENVS = {"align", "gather", "eqnarray", "flalign", "alignat", "IEEEeqnarray"}
ONE_NUMBER_ENVS = {"equation", "multline", "dmath"}
FIG_ENVS = {"figure": "figure", "figure*": "figure", "sidewaysfigure": "figure", "sidewaysfigure*": "figure",
            "wrapfigure": "figure", "SCfigure": "figure",
            "table": "table", "table*": "table", "sidewaystable": "table", "sidewaystable*": "table",
            "wraptable": "table"}
VERB_ENVS = {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "alltt"}
NESTED_LINE_ENVS = {"aligned", "alignedat", "gathered", "split", "array", "cases", "matrix", "pmatrix", "bmatrix",
                    "vmatrix", "Vmatrix", "Bmatrix", "smallmatrix", "subarray", "tabular", "dcases", "rcases",
                    "multlined", "eqnarray", "subequations"}
SECTION_LEVELS = {"part": 0, "chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}
CITE_RE = re.compile(r"\\(cite|citep|citet|citealt|citealp|citeauthor|citeyear|citeyearpar|onlinecite|Cite|Citep|"
                     r"Citet|Citealt|Citealp|parencite|textcite|autocite|footcite|supercite|cites|nocite|citenum)"
                     r"(\*?)(?![A-Za-z@])")
LABEL_RE = re.compile(r"\\label\s*\{([^{}]*)\}")
TOKEN_RE = re.compile(r"\\begin\s*\{([^{}]*)\}|\\end\s*\{([^{}]*)\}|\\([A-Za-z@]+)|\\(.)|\$\$|\$", re.S)


def letters(n):
    """1 -> A, 26 -> Z, 27 -> AA (LaTeX \\Alph stops at 26; beyond that we continue)."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def alph(n):
    return letters(n).lower()


# ------------------------------------------------------------------ scanning
def scan_math(body, aliases=None):
    """Spans of math and verbatim in body: list of dicts {kind: display|inline|verbatim,
    env, start, end, inner_start, inner_end}. `aliases` maps control words to
    '\\begin{env}' / '\\end{env}' (from tex_macros.env_aliases)."""
    aliases = aliases or {}
    spans = []
    i, n = 0, len(body)
    stack = None          # current open span: dict
    while i < n:
        m = TOKEN_RE.search(body, i)
        if not m:
            break
        tok_begin, tok_end, word, sym = m.group(1), m.group(2), m.group(3), m.group(4)
        if word and word in aliases:
            # a shorthand may stand for several \begin/\end (\bea = \begin{equation}\begin{aligned}):
            # the outermost environment counts, i.e. the first \begin or the last \end
            parts = re.findall(r"\\(begin|end)\{([^{}]*)\}", aliases[word])
            if parts and parts[0][0] == "begin":
                tok_begin = parts[0][1]
            elif parts:
                tok_end = parts[-1][1]
            word = None
        if stack is None:
            if tok_begin is not None:
                env = tok_begin.strip()
                if env in DISPLAY_ENVS or env in VERB_ENVS or env == "math":
                    kind = "display" if env in DISPLAY_ENVS else ("verbatim" if env in VERB_ENVS else "inline")
                    stack = {"kind": kind, "env": env, "start": m.start(), "inner_start": m.end(), "depth": 1}
            elif m.group(0) == "$$":
                stack = {"kind": "display", "env": "$$", "start": m.start(), "inner_start": m.end()}
            elif m.group(0) == "$":
                stack = {"kind": "inline", "env": "$", "start": m.start(), "inner_start": m.end()}
            elif sym == "[":
                stack = {"kind": "display", "env": "\\[", "start": m.start(), "inner_start": m.end()}
            elif sym == "(":
                stack = {"kind": "inline", "env": "\\(", "start": m.start(), "inner_start": m.end()}
            elif word == "verb":
                j = m.end()
                if j < n and body[j] == "*":
                    j += 1
                if j < n:
                    k = body.find(body[j], j + 1)
                    i = (k + 1) if k > 0 else n
                    continue
            i = m.end()
            continue
        # inside a span: look for its end
        env = stack["env"]
        closed = False
        if env in ("$", "$$"):
            if m.group(0) == env:
                closed = True
            elif env == "$" and m.group(0) == "$$":     # "$$" inside inline math: "$a$$b$" -> close at first
                stack_end = m.start() + 1
                stack.update({"end": stack_end, "inner_end": m.start()})
                spans.append(stack)
                stack = {"kind": "inline", "env": "$", "start": m.start() + 1, "inner_start": m.end()}
                i = m.end()
                continue
        elif env == "\\[":
            closed = sym == "]"
        elif env == "\\(":
            closed = sym == ")"
        else:
            if tok_begin is not None and tok_begin.strip() == env:
                stack["depth"] += 1
            elif tok_end is not None and tok_end.strip() == env:
                stack["depth"] -= 1
                closed = stack["depth"] == 0
        if closed:
            stack.update({"end": m.end(), "inner_end": m.start()})
            stack.pop("depth", None)
            spans.append(stack)
            stack = None
        i = m.end()
    if stack is not None:
        stack.update({"end": n, "inner_end": n, "unclosed": True})
        stack.pop("depth", None)
        spans.append(stack)
    return spans


class Mask:
    """Fast test whether an offset is inside one of the given spans."""

    def __init__(self, spans):
        self.s = sorted((sp["start"], sp["end"]) for sp in spans)
        import bisect
        self._b = bisect
        self.starts = [a for a, _ in self.s]

    def inside(self, pos):
        i = self._b.bisect_right(self.starts, pos) - 1
        return i >= 0 and self.s[i][0] <= pos < self.s[i][1]


def find_envs(body, names, mask=None):
    """Top-level environments with a name in `names` (matching \\begin/\\end by name, with
    nesting of the same name). Returns [{env, start, end, inner_start, inner_end}]."""
    out = []
    pat = re.compile(r"\\(begin|end)\s*\{(" + "|".join(re.escape(x) for x in sorted(names, key=len, reverse=True))
                     + r")\}")
    stack = []
    for m in pat.finditer(body):
        if mask and mask.inside(m.start()):
            continue
        kind, env = m.group(1), m.group(2)
        if kind == "begin":
            stack.append((env, m.start(), m.end()))
        else:
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0] == env:
                    e, s, ins = stack[k]
                    del stack[k:]
                    if not stack:
                        out.append({"env": env, "start": s, "end": m.end(), "inner_start": ins, "inner_end": m.start()})
                    break
    for env, s, ins in stack[:1]:                  # unclosed outermost environment
        out.append({"env": env, "start": s, "end": len(body), "inner_start": ins, "inner_end": len(body),
                    "unclosed": True})
    return sorted(out, key=lambda d: d["start"])


def command_args(s, i, n_opt=1, n_req=1):
    """Read up to n_opt optional [..] then n_req {..} arguments at s[i:].
    Returns (opts, reqs, end) or None if a required argument is missing."""
    opts = []
    j = i
    if s[j:j + 1] == "*":
        j += 1
    for _ in range(n_opt):
        g, e = M.read_group(s, j, "[", "]")
        if g is None:
            break
        opts.append(g)
        j = e
    reqs = []
    for _ in range(n_req):
        g, e = M.read_group(s, j)
        if g is None:
            return None
        reqs.append(g)
        j = e
    return opts, reqs, j


# ------------------------------------------------------------------ equations
def split_lines(inner):
    """Split the inside of a multi-line environment at top-level \\\\ (not inside braces or
    nested aligned/array/cases/...). Returns [(start, end)] relative to inner."""
    out, depth, env_depth, start = [], 0, 0, 0
    i, n = 0, len(inner)
    while i < n:
        c = inner[i]
        if c == "\\":
            mb = re.match(r"\\(begin|end)\s*\{([^{}]*)\}", inner[i:])
            if mb:
                if mb.group(2) in NESTED_LINE_ENVS or mb.group(2).rstrip("*") in NESTED_LINE_ENVS:
                    env_depth += 1 if mb.group(1) == "begin" else -1
                i += mb.end()
                continue
            if inner.startswith("\\\\", i) and depth == 0 and env_depth <= 0:
                out.append((start, i))
                j = i + 2
                if j < n and inner[j] == "*":
                    j += 1
                mo = re.match(r"\s*\[[^\]]*\]", inner[j:])
                if mo:
                    j += mo.end()
                start = j
                i = j
                continue
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    out.append((start, n))
    return out


NONUMBER_RE = re.compile(r"\\(nonumber|notag)(?![A-Za-z@])")
TAG_RE = re.compile(r"\\tag\*?\s*\{([^{}]*)\}")


def _line_is_empty(t):
    t = LABEL_RE.sub("", NONUMBER_RE.sub("", t))
    return not t.strip()


# ------------------------------------------------------------------ the document
def split_document(flat):
    """(preamble, body, body_offset): body is between \\begin{document} and \\end{document}."""
    mb = re.search(r"\\begin\s*\{document\}", flat)
    if not mb:
        return "", flat, 0
    me = re.search(r"\\end\s*\{document\}", flat[mb.end():])
    end = mb.end() + me.start() if me else len(flat)
    return flat[:mb.start()], flat[mb.end():end], mb.end()


def document_class(preamble):
    m = re.search(r"\\document(?:class|style)\s*(?:\[([^\]]*)\])?\s*\{([^{}]*)\}", preamble)
    return (m.group(2).strip(), (m.group(1) or "")) if m else (None, "")


def extract(flat, macros=None):
    """Structure of a flattened, comment-free document. Offsets refer to `flat`."""
    macros = macros if macros is not None else M.collect(flat)
    aliases = M.env_aliases(macros)
    preamble, body, off = split_document(flat)
    cls, cls_opts = document_class(preamble)
    revtex = bool(cls and cls.lower().startswith("revtex"))
    numberwithin = bool(re.search(r"\\numberwithin\s*\{equation\}\s*\{section\}", preamble)) or \
        bool(re.search(r"\\renewcommand\s*\{?\\theequation\}?\s*\{\s*\\(?:arabic|thesection)\s*\{?\\?(?:section)",
                       preamble))
    spans = scan_math(body, aliases)
    math_mask = Mask(spans)
    displays = [s for s in spans if s["kind"] == "display"]

    # --- title, authors, abstract (searched in the whole flat text: some classes put them in the preamble)
    title = None
    for mt in re.finditer(r"\\title(?![A-Za-z@])", flat):
        if _is_definition(flat, mt.start()):
            continue                      # \renewcommand{\title}[2][]{...} in a class or preamble
        a = command_args(flat, mt.end(), 1, 1)
        if a and "#" not in a[1][0]:
            title = {"tex": a[1][0], "start": mt.start(), "end": a[2]}
            break
    authors = []
    for ma in re.finditer(r"\\author(?![A-Za-z@])", flat):
        if _is_definition(flat, ma.start()):
            continue
        a = command_args(flat, ma.end(), 1, 1)
        if a and "#" not in a[1][0]:
            for part in re.split(r"\\and(?![A-Za-z@])", a[1][0]):
                if part.strip():
                    authors.append({"tex": part.strip(), "start": ma.start(), "end": a[2]})
    abstract = None
    envs_abs = find_envs(body, {"abstract"}, math_mask)
    if envs_abs:
        e = envs_abs[0]
        abstract = {"tex": body[e["inner_start"]:e["inner_end"]], "start": off + e["start"], "end": off + e["end"],
                    "inner_start": off + e["inner_start"], "inner_end": off + e["inner_end"]}
    else:
        for src, o in ((body, off), (preamble, 0)):
            mabs = re.search(r"\\abstract\s*\{", src)
            if mabs:
                g, e2 = M.read_group(src, mabs.end() - 1)
                if g is not None:
                    abstract = {"tex": g, "start": o + mabs.start(), "end": o + e2,
                                "inner_start": o + mabs.end(), "inner_end": o + e2 - 1}
                    break
    if abstract is None:
        # pre-abstract fallback: elsarticle frontmatter etc. use the environment in the preamble
        envs_abs = find_envs(preamble, {"abstract"})
        if envs_abs:
            e = envs_abs[0]
            abstract = {"tex": preamble[e["inner_start"]:e["inner_end"]], "start": e["start"], "end": e["end"],
                        "inner_start": e["inner_start"], "inner_end": e["inner_end"]}

    # --- appendix start, bibliography
    appendix_at = None
    mapp = re.search(r"\\appendix(?![A-Za-z@])|\\begin\s*\{appendices\}", body)
    while mapp and math_mask.inside(mapp.start()):
        mapp = re.compile(r"\\appendix(?![A-Za-z@])|\\begin\s*\{appendices\}").search(body, mapp.end())
    if mapp:
        appendix_at = mapp.start()
    bibenv = find_envs(body, {"thebibliography"}, math_mask)
    mbib = re.search(r"\\bibliography\s*\{([^{}]*)\}", body)
    bib_start = None
    if bibenv:
        bib_start = bibenv[0]["start"]
    elif mbib:
        bib_start = mbib.start()
    body_end = len(body)

    # --- sections
    sections = []
    counters = {0: 0, 1: 0, 2: 0, 3: 0}
    used_levels = set()
    for ms in re.finditer(r"\\(part|chapter|section|subsection|subsubsection)(?![A-Za-z@])(\*?)", body):
        if math_mask.inside(ms.start()):
            continue
        a = command_args(body, ms.end(), 1, 1)
        if not a:
            continue
        used_levels.add(SECTION_LEVELS[ms.group(1)])
        sections.append({"cmd": ms.group(1), "level": SECTION_LEVELS[ms.group(1)], "starred": ms.group(2) == "*",
                         "title_tex": a[1][0], "start": ms.start(), "cmd_end": a[2]})
    has_chapter = any(s["cmd"] == "chapter" for s in sections)
    toplevel = 0 if has_chapter else 1
    app_mode = False
    for s in sections:
        lvl = s["level"]
        s["appendix"] = appendix_at is not None and s["start"] > appendix_at
        if s["appendix"] and not app_mode:
            app_mode = True
            for k in range(toplevel, 4):
                counters[k] = 0
        if s["starred"] or s["cmd"] == "part":
            s["number"] = None
        else:
            counters[lvl] += 1
            for deeper in range(lvl + 1, 4):
                counters[deeper] = 0
            parts = [letters(counters[k]) if (k == toplevel and app_mode) else str(counters[k])
                     for k in range(toplevel, lvl + 1)]
            s["number"] = ".".join(parts)
        mlab = re.match(r"\s*\\label\s*\{([^{}]*)\}", body[s["cmd_end"]:])
        s["label"] = mlab.group(1).strip() if mlab else None
    for idx, s in enumerate(sections):
        end = bib_start if bib_start is not None and bib_start > s["start"] else body_end
        for t in sections[idx + 1:]:
            if t["level"] <= s["level"]:
                end = min(end, t["start"])
                break
        s["end"] = end
        nxt = sections[idx + 1]["start"] if idx + 1 < len(sections) else end
        s["own_end"] = min(nxt, end)
        s["parent"] = None
        for t in reversed(sections[:idx]):
            if t["level"] < s["level"]:
                s["parent"] = sections.index(t)
                break

    def section_at(pos):
        best = None
        for k, s in enumerate(sections):
            if s["start"] <= pos < s["end"]:
                best = k
        return best

    # --- equations
    eq_rows = []
    eqn = 0
    sub_envs = find_envs(body, {"subequations"}, math_mask)
    # equation counter resets at unstarred top-level sections (numberwithin) and, in REVTeX,
    # at \appendix and at every appendix section
    tops = [s for s in sections if s["level"] == toplevel and not s["starred"]]
    resets = sorted(([s["start"] for s in tops if numberwithin or (revtex and s["appendix"])]) +
                    ([appendix_at] if (revtex and appendix_at is not None) else []))
    reset_i = 0
    sub_state = {}
    for d in displays:
        while reset_i < len(resets) and resets[reset_i] < d["start"]:
            eqn = 0
            reset_i += 1
        cur_top = None
        for s in tops:
            if s["start"] < d["start"]:
                cur_top = s
        top_secnum = cur_top["number"] if cur_top else None
        k = section_at(d["start"])
        in_app = appendix_at is not None and d["start"] > appendix_at
        sub = None
        for se in sub_envs:
            if se["start"] <= d["start"] < se["end"]:
                sub = se
        env = d["env"]
        base_env = env.rstrip("*")
        starred = env.endswith("*") or env in ("$$", "\\[", "displaymath")
        inner = body[d["inner_start"]:d["inner_end"]]
        if base_env in MULTILINE_ENVS:
            lines = split_lines(inner)
        else:
            lines = [(0, len(inner))]
        groups = []          # [start, end, numbered, tag, labels, empty]
        if base_env in MULTILINE_ENVS and not starred:
            # LaTeX numbers every line of these environments unless \nonumber/\notag, empty lines
            # included (a trailing \\ makes an empty numbered line; checked against pdflatex)
            cur = None
            for (a, b) in lines:
                t = inner[a:b]
                tag = TAG_RE.search(t)
                numbered = not NONUMBER_RE.search(t) or bool(tag)
                empty = _line_is_empty(t) and not tag
                if cur is None:
                    cur = [a, b, False, None, [], empty]
                else:
                    cur[1] = b
                    cur[5] = cur[5] and empty
                cur[4] += LABEL_RE.findall(t)
                if numbered:
                    cur[2] = True
                    cur[3] = tag.group(1) if tag else None
                    groups.append(cur)
                    cur = None
            if cur is not None:
                if groups and cur[5]:
                    groups[-1][1] = cur[1]
                    groups[-1][4] += cur[4]
                else:
                    groups.append(cur)
        else:
            tag = TAG_RE.search(inner)
            numbered = (not starred and base_env in ONE_NUMBER_ENVS | MULTILINE_ENVS
                        and not NONUMBER_RE.search(inner)) or bool(tag)
            groups.append([0, len(inner), numbered, tag.group(1) if tag else None, LABEL_RE.findall(inner), False])
        n_rows = sum(1 for g in groups if not (g[5] and not g[4]))
        for (a, b, numbered, tag, labels, empty) in groups:
            number = None
            if numbered:
                if tag is not None:
                    number = tag
                elif sub is not None:
                    key = sub["start"]
                    if key not in sub_state:
                        eqn += 1
                        sub_state[key] = [eqn, 0, _prefix(numberwithin, revtex, in_app, top_secnum)]
                    sub_state[key][1] += 1
                    number = f"{sub_state[key][2]}{sub_state[key][0]}{alph(sub_state[key][1])}"
                else:
                    eqn += 1
                    number = f"{_prefix(numberwithin, revtex, in_app, top_secnum)}{eqn}"
            if empty and not labels:
                continue                  # an empty numbered line: it takes a number, it is not a row
            rs = d["start"] if n_rows == 1 else d["inner_start"] + a
            re_ = d["end"] if n_rows == 1 else d["inner_start"] + b
            eq_rows.append({"env": env, "labels": [x.strip() for x in labels], "number": number,
                            "start": off + rs, "end": off + re_, "section": k,
                            "inner_start": off + d["inner_start"] + a, "inner_end": off + d["inner_start"] + b})
    # labels placed in a subequations block outside its equations name the parent number
    sub_labels = {}
    for se in sub_envs:
        if se["start"] in sub_state:
            st = sub_state[se["start"]]
            for ml in LABEL_RE.finditer(body, se["inner_start"], se["inner_end"]):
                if not math_mask.inside(ml.start()):
                    sub_labels[ml.group(1).strip()] = f"{st[2]}{st[0]}"

    # --- figures and tables
    figs = []
    fig_count = {"figure": 0, "table": 0}
    for fe in find_envs(body, set(FIG_ENVS), math_mask):
        kind = FIG_ENVS[fe["env"]]
        inner = body[fe["inner_start"]:fe["inner_end"]]
        files = []
        for mg in re.finditer(r"\\(includegraphics\*?|epsfbox|epsffile|plotone|includegraphicsx)(?![A-Za-z@])",
                              inner):
            a = command_args(inner, mg.end(), 2, 1)
            if a:
                files.append(a[1][0].strip())
        for mg in re.finditer(r"\\plottwo(?![A-Za-z@])", inner):
            a = command_args(inner, mg.end(), 0, 2)
            if a:
                files += [x.strip() for x in a[1]]
        for mg in re.finditer(r"\\(?:epsfig|psfig)\s*\{[^{}]*file\s*=\s*([^,}\s]+)", inner):
            files.append(mg.group(1))
        caps = []
        for mc in re.finditer(r"\\caption(?![A-Za-z@])", inner):
            a = command_args(inner, mc.end(), 1, 1)
            if a:
                caps.append({"tex": a[1][0], "start": mc.start(), "end": a[2]})
        labels = [(ml.start(), ml.group(1).strip()) for ml in LABEL_RE.finditer(inner)]
        k = section_at(fe["start"])
        if not caps:
            figs.append({"kind": kind, "env": fe["env"], "number": None, "caption_tex": None, "label":
                         labels[0][1] if labels else None, "files": files, "start": off + fe["start"],
                         "end": off + fe["end"], "section": k, "caption_start": None, "caption_end": None})
            continue
        for ci, c in enumerate(caps):
            fig_count[kind] += 1
            nxt = caps[ci + 1]["start"] if ci + 1 < len(caps) else len(inner)
            prev_end = caps[ci - 1]["end"] if ci > 0 else 0
            lab = [l for p, l in labels if c["start"] <= p < nxt] or \
                  ([l for p, l in labels if prev_end <= p < c["start"]] if ci == 0 or True else [])
            figs.append({"kind": kind, "env": fe["env"], "number": str(fig_count[kind]), "caption_tex": c["tex"],
                         "label": lab[0] if lab else None, "files": files if ci == 0 else [],
                         "start": off + fe["start"], "end": off + fe["end"], "section": k,
                         "caption_start": off + fe["inner_start"] + c["start"],
                         "caption_end": off + fe["inner_start"] + c["end"]})
    fig_spans = [{"start": f["start"] - off, "end": f["end"] - off} for f in figs]

    # --- footnotes
    footnotes = []
    for mf in re.finditer(r"\\footnote(?![A-Za-z@])", body):
        if math_mask.inside(mf.start()):
            continue
        a = command_args(body, mf.end(), 1, 1)
        if a:
            footnotes.append({"tex": a[1][0], "start": off + mf.start(), "end": off + a[2],
                              "section": section_at(mf.start())})

    # --- citations
    cites = []
    for mc in CITE_RE.finditer(body):
        if math_mask.inside(mc.start()):
            continue
        a = command_args(body, mc.end(), 2, 1)
        if not a:
            continue
        keys = [k.strip() for k in a[1][0].split(",") if k.strip()]
        cites.append({"cmd": mc.group(1), "keys": keys, "start": off + mc.start(), "end": off + a[2],
                      "section": section_at(mc.start()), "nocite": mc.group(1) == "nocite"})

    # --- labels map for \ref
    labels = {}
    for s in sections:
        if s["label"]:
            labels[s["label"]] = {"kind": "section", "number": s["number"]}
    for r in eq_rows:
        for l in r["labels"]:
            labels[l] = {"kind": "equation", "number": r["number"]}
    for l, num in sub_labels.items():
        labels.setdefault(l, {"kind": "equation", "number": num})
    for f in figs:
        if f["label"]:
            labels[f["label"]] = {"kind": f["kind"], "number": f["number"]}

    for s in sections:
        for key in ("start", "end", "cmd_end", "own_end"):
            s[key] += off
    return {"class": cls, "class_options": cls_opts, "revtex": revtex, "numberwithin_section": numberwithin,
            "title": title, "authors": authors, "abstract": abstract, "sections": sections,
            "equations": eq_rows, "figures": figs, "footnotes": footnotes, "cites": cites, "labels": labels,
            "appendix_at": (off + appendix_at) if appendix_at is not None else None,
            "bibliography_at": (off + bib_start) if bib_start is not None else None,
            "bibliography_files": [x.strip() for x in mbib.group(1).split(",")] if mbib else [],
            "body_start": off, "body_end": off + body_end,
            "math_spans": [{"kind": s["kind"], "env": s["env"], "start": off + s["start"], "end": off + s["end"]}
                           for s in spans if s["kind"] != "inline"],
            "figure_spans": [{"start": x["start"] + off, "end": x["end"] + off} for x in fig_spans],
            "aliases": aliases}


def _is_definition(text, pos):
    """True if the control word at pos is the name being defined (\\newcommand{\\title}, \\def\\title)."""
    before = text[max(0, pos - 30):pos]
    return bool(re.search(r"\\(?:re)?newcommand\*?\s*\{?\s*$|\\providecommand\*?\s*\{?\s*$|\\(?:g|e|x)?def\s*$|"
                          r"\\let\s*$|\\DeclareRobustCommand\*?\s*\{?\s*$", before))


def _prefix(numberwithin, revtex, in_app, top_secnum):
    if in_app and revtex:
        return top_secnum or ""
    if numberwithin and top_secnum:
        return top_secnum + "."
    return ""
