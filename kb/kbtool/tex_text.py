"""K2 steps 6-7 (brief 12.4): TeX to plain text, sentences, chunks, equation normalization.

Converter: pylatexenc (LatexNodes2Text) when it can be imported (the kb/.venv environment);
otherwise a small standard-library converter (recorded as converter 'stdlib'). LaTeXML is not
installed on the machine and is not installed for this [JUDGEMENT; kb/JOURNAL.md].
Math stays in the text as LaTeX between $...$ (display math too), so that equations are
searchable; \\ref and \\eqref become the numbers this tool computed for their labels.
"""
import re

from . import tex_macros as M

try:                                                     # optional (kb/.venv)
    import logging as _logging
    _logging.getLogger("pylatexenc").setLevel(_logging.CRITICAL)
    from pylatexenc.latex2text import LatexNodes2Text
    from pylatexenc import latex2text as _l2t, latexwalker as _lw
    CONVERTER = "pylatexenc " + __import__("pylatexenc").__version__
except Exception:                                        # pragma: no cover - depends on the environment
    LatexNodes2Text = None
    CONVERTER = "stdlib"

TARGET_MIN, TARGET_MAX, OVERLAP = 200, 400, 0.15        # tokens (whitespace words) [brief 12.4 step 7]
REF_RE = re.compile(r"\\(ref|eqref|autoref|cref|Cref|pageref|vref|Eqref|nameref)\*?\s*\{([^{}]*)\}")
CITE_TEXT_RE = re.compile(r"\\(?:cite|citep|citet|citealt|citealp|onlinecite|Cite|Citep|Citet|parencite|textcite|"
                          r"autocite|footcite|supercite|citenum|citeauthor|citeyear)\*?(?![A-Za-z@])"
                          r"(?:\s*\[[^\]]*\]){0,2}\s*\{[^{}]*\}")
DISPLAY_TEXT_RE = re.compile(r"\\begin\s*\{(equation|align|gather|multline|eqnarray|flalign|alignat|displaymath|"
                             r"dmath)(\*?)\}(.*?)\\end\s*\{\1\2\}", re.S)
LABEL_RE = re.compile(r"\\label\s*\{[^{}]*\}")

_KNOWN = None


def known_macros():
    """Control words a converter knows (pylatexenc's databases, when present) plus common
    LaTeX/AMS/REVTeX commands. Used for the 'unresolved macros' fraction of the quality score."""
    global _KNOWN
    if _KNOWN is None:
        k = set(EXTRA_KNOWN.split())
        if LatexNodes2Text is not None:
            try:
                k |= {m.macroname for m in _l2t.get_default_latex_context_db().iter_macro_specs()}
                db = _lw.get_default_latex_context_db()
                for cat in db.categories():
                    k |= {m.macroname for m in db.iter_macro_specs(categories=[cat])}
            except Exception:
                pass
        _KNOWN = k
    return _KNOWN


EXTRA_KNOWN = """
begin end label ref eqref cite citep citet onlinecite nocite section subsection subsubsection paragraph part chapter
appendix caption includegraphics footnote footnotemark footnotetext thanks title author affiliation email date
maketitle and keywords pacs bibliography bibliographystyle acknowledgments item hline cline toprule midrule
bottomrule centering raggedright raggedleft noindent newline linebreak pagebreak newpage clearpage hspace vspace
hfill vfill quad qquad left right big Big bigg Bigg bigl bigr Bigl Bigr biggl biggr frac dfrac tfrac sqrt sum prod
int oint iint iiint lim limsup liminf sup inf max min log ln exp sin cos tan sinh cosh tanh arcsin arccos arctan det
partial nabla infty mathrm mathbf mathit mathcal mathbb mathfrak mathsf mathtt boldsymbol bm text textrm textbf
textit emph mbox hbox operatorname overline underline hat tilde bar vec dot ddot widetilde widehat cdot cdots
ldots dots vdots ddots times otimes oplus pm mp leq geq le ge neq approx sim simeq equiv propto ll gg in notin
subset supset cup cap forall exists rightarrow leftarrow Rightarrow Leftrightarrow to mapsto langle rangle lfloor
rfloor lceil rceil prime dagger ast star circ bullet nonumber notag tag displaystyle textstyle scriptstyle
label nolinebreak url href ensuremath phantom hphantom vphantom smallskip medskip bigskip par newcommand
renewcommand def let usepackage documentclass setlength addtolength textwidth columnwidth linewidth
pdfoutput resizebox scalebox rotatebox textsc textsf texttt sl it bf rm em tt small footnotesize scriptsize tiny
large Large LARGE huge Huge normalsize mathop limits nolimits stackrel overset underset substack binom choose
over atop sqrt bibitem bibinfo bibfield eprint doi Eprint BibitemOpen BibitemShut natexlab newblock
textsuperscript textsubscript ce SI si unit num degree odot hbar ell Re Im wp aleph emptyset
cal rm bf it sl sf tt eqno leqno cr kern vskip hskip baselineskip lineskip font eject centerline leftline
rightline line noalign halign valign settabs obeylines addcontentsline tableofcontents listoffigures
Biggl Biggr biggl biggr bigm Bigm relax ignorespaces protect expandafter hfil hss vss null strut mathstrut
""".strip()


# ------------------------------------------------------------------ conversion
def _stdlib_text(tex):
    """A crude standard-library converter (used only when pylatexenc is missing)."""
    t = re.sub(r"\\(begin|end)\s*\{[^{}]*\}", " ", tex)
    t = re.sub(r"\\(textbf|textit|emph|textrm|mbox|text|textsc|textsf|texttt|underline)\s*\{([^{}]*)\}", r"\2", t)
    t = re.sub(r"\\(label|includegraphics|vspace|hspace)\*?\s*(\[[^\]]*\])?\s*\{[^{}]*\}", " ", t)
    t = re.sub(r"\\([%&$#_{}])", r"\1", t)
    t = re.sub(r"~", " ", t)
    t = re.sub(r"\\[A-Za-z@]+\*?", " ", t)
    t = t.replace("{", "").replace("}", "")
    return re.sub(r"[ \t\r\f\v]+", " ", t)


def _make_l2t():
    return LatexNodes2Text(math_mode="with-delimiters", keep_comments=False, strict_latex_spaces=False)


_L2T = None


def to_text(tex, labels=None, macros=None):
    """Plain text of a TeX fragment. \\ref -> computed number; \\cite -> [cit.]; display math
    -> $...$ on its own; the paper's macros expanded first (text level)."""
    global _L2T
    labels = labels or {}

    def ref(m):
        lab = labels.get(m.group(2).strip())
        num = lab.get("number") if lab else None
        if num is None:
            return "?"
        return f"({num})" if m.group(1).lower() == "eqref" else str(num)

    t = REF_RE.sub(ref, tex)
    t = CITE_TEXT_RE.sub("[cit.]", t)
    t = LABEL_RE.sub("", t)
    t = DISPLAY_TEXT_RE.sub(lambda m: " $" + re.sub(r"\\\\(\[[^\]]*\])?|&|\\nonumber|\\notag", " ", m.group(3))
                            + "$ ", t)
    if macros:
        t, _ = M.expand(t, macros, max_depth=4)
    if LatexNodes2Text is not None:
        if _L2T is None:
            _L2T = _make_l2t()
        try:
            out = _L2T.latex_to_text(t)
        except Exception:
            out = _stdlib_text(t)
    else:
        out = _stdlib_text(t)
    out = out.replace("\u00a0", " ")
    out = re.sub(r"[ \t\r\f\v]+", " ", out)
    out = re.sub(r" *\n *", "\n", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


# ------------------------------------------------------------------ sentences
ABBREV = {"eq", "eqs", "fig", "figs", "ref", "refs", "sec", "secs", "tab", "tabs", "e.g", "i.e", "cf", "vs", "al",
          "no", "nos", "dr", "prof", "approx", "resp", "app", "apps", "ch", "chap", "vol", "pp", "p", "ed", "eds",
          "etc", "viz", "phys", "rev", "lett", "astrophys", "j", "mon", "not", "r", "astron", "soc", "theor"}
SENT_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9\\$(\[])")


def sentences(text):
    """Split plain text into sentences (rule-based; abbreviations and initials kept). Blank
    lines and headings (lines starting with the section sign that pylatexenc writes) end a
    sentence too."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = "\n".join(l for l in para.split("\n") if not l.lstrip().startswith("\u00a7"))
        out += _sentences(para)
    return out


def _sentences(text):
    out, start = [], 0
    for m in SENT_END.finditer(text):
        before = text[start:m.start()]
        w = re.search(r"([A-Za-z.]+)\.[\"')\]]*$", before)
        if w:
            word = w.group(1).lower()
            if word in ABBREV or len(word) == 1:
                continue
        out.append(text[start:m.start()].strip())
        start = m.end()
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return [s for s in out if s]


def tex_units(tex, base, protected):
    """Split TeX of one paragraph into sentence units with offsets, never inside a protected
    span (display math, figures) or a brace group. Returns [(start, end)] (absolute)."""
    units, depth, start = [], 0, 0
    i, n = 0, len(tex)
    prot = sorted(protected)
    pi = 0
    while i < n:
        while pi < len(prot) and prot[pi][1] <= base + i:
            pi += 1
        if pi < len(prot) and prot[pi][0] <= base + i < prot[pi][1]:
            i = prot[pi][1] - base
            continue
        c = tex[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth = max(0, depth - 1)
        elif c in ".!?" and depth == 0:
            m = re.match(r"[.!?][\"')\]]*\s+(?=[A-Z\\])", tex[i:])
            if m:
                w = re.search(r"([A-Za-z.]+)$", tex[start:i])
                word = w.group(1).lower() if w else ""
                if word not in ABBREV and len(word) != 1:
                    units.append((base + start, base + i + m.end()))
                    start = i + m.end()
                    i = start
                    continue
        i += 1
    if tex[start:].strip():
        units.append((base + start, base + n))
    return units


def paragraphs(flat, start, end, protected):
    """Paragraph spans of flat[start:end] split at blank lines outside protected spans."""
    out = []
    prot = sorted(protected)
    pos = start
    for m in re.finditer(r"\n[ \t]*\n\s*", flat[start:end]):
        a = start + m.start()
        if any(p0 <= a < p1 for p0, p1 in prot):
            continue
        if flat[pos:a].strip():
            out.append((pos, a))
        pos = start + m.end()
    if flat[pos:end].strip():
        out.append((pos, end))
    return out


def ntok(text):
    return len(text.split())


def chunk_section(flat, start, end, protected, convert, kind="body"):
    """Chunks of one section's own text: paragraphs packed to TARGET_MIN..TARGET_MAX tokens,
    long paragraphs split at sentence units, about OVERLAP of the previous chunk repeated
    (whole units), never cutting a protected span. Returns [dict(start, end, text, tex, n_tokens)]."""
    units = []                                      # (start, end, text, ntok, para_index)
    for pi, (a, b) in enumerate(paragraphs(flat, start, end, protected)):
        for (u0, u1) in tex_units(flat[a:b], a, protected):
            txt = convert(flat[u0:u1])
            if txt.strip():
                units.append((u0, u1, txt, ntok(txt), pi))
    chunks = []
    cur = []
    for u in units:
        size = sum(x[3] for x in cur)
        if cur and size + u[3] > TARGET_MAX and size >= TARGET_MIN // 2:
            chunks.append(cur)
            keep, acc = [], 0
            for x in reversed(cur):                 # overlap: trailing units up to OVERLAP of the target
                if acc + x[3] > OVERLAP * TARGET_MAX or len(keep) >= len(cur) - 1:
                    break
                keep.insert(0, x)
                acc += x[3]
            cur = keep
        # prefer to break at a paragraph end once the minimum is reached
        elif cur and size >= TARGET_MIN and u[4] != cur[-1][4]:
            chunks.append(cur)
            keep, acc = [], 0
            for x in reversed(cur):
                if acc + x[3] > OVERLAP * TARGET_MAX or len(keep) >= len(cur) - 1:
                    break
                keep.insert(0, x)
                acc += x[3]
            cur = keep
        cur.append(u)
    if cur and (not chunks or any(x not in chunks[-1] for x in cur)):
        chunks.append(cur)
    out = []
    for c in chunks:
        text = " ".join(x[2] for x in c)
        out.append({"start": c[0][0], "end": c[-1][1], "text": text, "tex": flat[c[0][0]:c[-1][1]],
                    "n_tokens": ntok(text), "kind": kind})
    return out


# ------------------------------------------------------------------ equations
SPACING_RE = re.compile(r"\\(?:,|;|!|:|>|quad|qquad|enspace|thinspace|medspace|thickspace|negthinspace|"
                        r"displaystyle|textstyle|scriptstyle|scriptscriptstyle|nonumber|notag|nolinebreak|"
                        r"allowbreak|left|right|middle|big|Big|bigg|Bigg|bigl|bigr|Bigl|Bigr|biggl|biggr|Biggl|Biggr)"
                        r"(?![A-Za-z@])")
SPACE_CMD_RE = re.compile(r"\\(?:hspace|vspace|phantom|hphantom|vphantom|mspace|kern|mkern)\*?\s*\{[^{}]*\}")


def normalize_equation(tex, macros=None):
    """tex_norm of brief 12.6: macros expanded, labels/tags/spacing removed, equivalent
    notations unified (\\dfrac,\\tfrac -> \\frac; \\rm{x} -> \\mathrm{x}), whitespace removed
    except where it separates a control word from a letter."""
    t = tex
    t = re.sub(r"^\\begin\s*\{[^{}]*\}(\{[^{}]*\})?|\\end\s*\{[^{}]*\}$", "", t.strip())
    if macros:
        t, _ = M.expand(t, macros)
    t = LABEL_RE.sub("", t)
    t = re.sub(r"\\tag\*?\s*\{[^{}]*\}", "", t)
    t = SPACE_CMD_RE.sub("", t)
    t = SPACING_RE.sub("", t)
    t = re.sub(r"\\\\(\*)?(\[[^\]]*\])?", " ", t)
    t = t.replace("&", " ")
    t = re.sub(r"\\[dt]frac(?![A-Za-z@])", r"\\frac", t)
    t = re.sub(r"\{\\rm\s+([^{}]*)\}", r"\\mathrm{\1}", t)
    t = re.sub(r"\{\\bf\s+([^{}]*)\}", r"\\mathbf{\1}", t)
    t = re.sub(r"\\(begin|end)\s*\{(aligned|split|gathered)\}", "", t)
    t = re.sub(r"(?<!\\)[,.;]\s*$", "", t.strip())
    toks = re.findall(r"\\[A-Za-z@]+|\\.|[^\s]", t)
    out = []
    for k, tok in enumerate(toks):
        if out and re.match(r"\\[A-Za-z@]+$", out[-1]) and re.match(r"[A-Za-z@]", tok):
            out.append(" ")
        out.append(tok)
    return "".join(out)


GREEK = set("alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi "
            "rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma "
            "Upsilon Phi Psi Omega ell hbar nabla partial".split())


def symbols(tex_norm):
    """Set of symbols of a normalized equation: Greek letters and similar, single Latin
    letters, and styled letters (\\mathcal{L}, \\mathbb{R}, ...)."""
    out = set()
    styled = re.compile(r"\\(mathcal|mathbb|mathrm|mathbf|mathfrak|mathsf|boldsymbol|bm|vec|hat|tilde|bar)\{([A-Za-z])\}")
    for m in styled.finditer(tex_norm):
        out.add(f"\\{m.group(1)}{{{m.group(2)}}}")
    tex_norm = styled.sub(" ", tex_norm)
    for m in re.finditer(r"\\([A-Za-z]+)", tex_norm):
        if m.group(1) in GREEK:
            out.add("\\" + m.group(1))
    stripped = re.sub(r"\\[A-Za-z@]+", " ", tex_norm)
    for m in re.finditer(r"(?<![A-Za-z])([A-Za-z])(?![A-Za-z])", stripped):
        out.add(m.group(1))
    return sorted(out)


def context(flat, start, end, convert, n=2, window=1500, lo=0, hi=None):
    """Two sentences of plain text before and after flat[start:end] (within [lo, hi))."""
    hi = len(flat) if hi is None else hi
    before = convert(flat[max(lo, start - window):start])
    after = convert(flat[end:min(hi, end + window)])
    b = sentences(before)[-n:]
    a = sentences(after)[:n]
    return " ".join(b).strip(), " ".join(a).strip()
