"""K9: an independent count of numbered display equations, for a sample of papers.

Written apart from kbtool's extractor (tex_structure.py, tex_macros.py) and from the lead's
regular-expression checkers (tracks/kb/analysis/lead_checks/eqcount*.py): one pass over the
characters with a stack of environments.

Rules (amsmath and LaTeX defaults):
- comments: from an unescaped % to the end of the line; `comment` environments and
  \\iffalse ... \\fi blocks are dropped;
- shorthands defined in the source (\\def\\be{\\begin{equation}}, \\newcommand{\\bea}{...},
  \\newcommand\\ee{\\end{equation}}, also \\renewcommand, \\providecommand and \\let\\be=..)
  are replaced by their text when it contains \\begin or \\end of a display environment;
- display blocks: equation, align, gather, multline, eqnarray, flalign, alignat (starred
  forms unnumbered), displaymath, \\[ \\], $$ $$; only outermost blocks count;
- numbered lines: equation and multline give one unless the block holds \\nonumber,
  \\notag or (starred) no \\tag; align-like environments split at \\\\ outside braces and
  inner environments (aligned, split, cases, array, matrix, ...); the empty last row
  after a trailing \\\\ is numbered (pdflatex does so for align, gather and eqnarray); a
  row with \\nonumber or \\notag has no number unless it has \\tag;
  \\tag gives a number in a starred environment too.

Input: the raw main file when it includes no other .tex file (independent of flattening
too), else build/tex/<id_>/flat.tex (comments already stripped by kbtool; the flattening is
then shared). Text is read only; nothing is compiled or executed.
"""
import os
import re

NUMBERED = {"equation", "align", "gather", "multline", "eqnarray", "flalign", "alignat", "xalignat"}
ONE_LINE = {"equation", "multline"}
UNNUMBERED = {"displaymath", "math"}
INNER = {"aligned", "split", "cases", "array", "matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix", "smallmatrix",
         "gathered", "alignedat", "subarray", "dcases", "rcases", "tabular", "substack", "multlined", "eqnarray*"}
RE_BEGIN_END = re.compile(r"\\(begin|end)\s*\{([A-Za-z]+\*?)\}")
RE_INCLUDE = re.compile(r"\\(?:input|include|subfile|import|subimport)\b")


def strip_comments(tex):
    out = []
    for line in tex.split("\n"):
        i, n = 0, len(line)
        cut = n
        while i < n:
            c = line[i]
            if c == "\\":
                i += 2
                continue
            if c == "%":
                cut = i
                break
            i += 1
        out.append(line[:cut])
    s = "\n".join(out)
    s = re.sub(r"\\begin\{comment\}.*?\\end\{comment\}", "", s, flags=re.S)
    s = re.sub(r"\\iffalse\b.*?\\fi\b", "", s, flags=re.S)
    return s


def _brace_arg(s, i):
    """Text of the {...} group starting at s[i] == '{' and the index after it."""
    if i >= len(s) or s[i] != "{":
        return None, i
    depth, j = 0, i
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return None, i


def shorthands(tex):
    """{name: replacement} for macros whose body opens or closes a display environment."""
    out = {}
    disp = NUMBERED | UNNUMBERED
    pat = re.compile(r"\\(?:re|provide)?newcommand\*?\s*(\{\\([A-Za-z]+)\}|\\([A-Za-z]+))\s*(?:\[\d\])?\s*|"
                     r"\\def\s*\\([A-Za-z]+)\s*|\\let\s*\\([A-Za-z]+)\s*=?\s*")
    for m in pat.finditer(tex):
        name = m.group(2) or m.group(3) or m.group(4) or m.group(5)
        j = m.end()
        while j < len(tex) and tex[j] in " \t\n":
            j += 1
        body, _ = _brace_arg(tex, j)
        if body is None:
            continue
        envs = [e.rstrip("*") for _, e in RE_BEGIN_END.findall(body)]
        if body.strip() in ("\\[", "\\]") or any(e in disp for e in envs):
            out[name] = body
    return out


def expand_shorthands(body, sh):
    if not sh:
        return body
    names = sorted(sh, key=len, reverse=True)
    pat = re.compile(r"\\(" + "|".join(map(re.escape, names)) + r")(?![A-Za-z])")
    return pat.sub(lambda m: " " + sh[m.group(1)] + " ", body)


def _split_rows(inner):
    """Rows of an align-like block: split at \\\\ outside braces and inner environments."""
    rows, cur, depth, envd, i, n = [], [], 0, 0, 0, len(inner)
    while i < n:
        if inner.startswith("\\\\", i):
            if depth == 0 and envd == 0:
                rows.append("".join(cur))
                cur = []
                i += 2
                # skip an optional [..] spacing argument and a following *
                while i < n and inner[i] in " *":
                    i += 1
                if i < n and inner[i] == "[":
                    k = inner.find("]", i)
                    i = k + 1 if k > 0 else i
                continue
            cur.append("\\\\")
            i += 2
            continue
        m = RE_BEGIN_END.match(inner, i)
        if m:
            envd += 1 if m.group(1) == "begin" else -1
            cur.append(m.group(0))
            i = m.end()
            continue
        c = inner[i]
        if c == "\\":
            cur.append(inner[i:i + 2])
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        cur.append(c)
        i += 1
    rows.append("".join(cur))
    # a trailing \\ leaves an empty last row, and amsmath numbers it (align, gather and
    # eqnarray alike; checked with pdflatex on a synthetic file, run in tracks/kb/claims/JOURNAL.md P3)
    return rows


def count_numbered(env, star, inner):
    """(numbered lines, tagged lines) of one display block."""
    base = env
    has_tag = lambda t: bool(re.search(r"\\tag\*?\s*\{", t))           # noqa: E731
    no_num = lambda t: bool(re.search(r"\\(?:nonumber|notag)(?![A-Za-z])", t))  # noqa: E731
    if base in ONE_LINE:
        if has_tag(inner):
            return 1, 1
        if star or no_num(inner):
            return 0, 0
        return 1, 0
    if base in NUMBERED:
        num, tag = 0, 0
        for row in _split_rows(inner):
            if has_tag(row):
                num += 1
                tag += 1
            elif not star and not no_num(row):
                num += 1
        return num, tag
    return 0, 0


def scan(body):
    """Displays and numbered lines of a document body (comments already stripped)."""
    res = {"displays": 0, "numbered": 0, "tagged": 0, "by_env": {}}
    i, n = 0, len(body)
    while i < n:
        j = body.find("\\", i)
        k = body.find("$", i)
        if j < 0 and k < 0:
            break
        if k >= 0 and (j < 0 or k < j):
            if body.startswith("$$", k):                # display math
                e = body.find("$$", k + 2)
                if e < 0:
                    break
                res["displays"] += 1
                res["by_env"]["$$"] = res["by_env"].get("$$", 0) + 1
                i = e + 2
            else:                                       # inline math: skip to its closing $
                p = k + 1
                while p < n and body[p] != "$":
                    p += 2 if body[p] == "\\" else 1
                i = p + 1                               # "$a$$b$" is two inline maths, not a display
            continue
        if body.startswith("\\[", j):
            e = body.find("\\]", j + 2)
            if e < 0:
                break
            res["displays"] += 1
            res["by_env"]["\\["] = res["by_env"].get("\\[", 0) + 1
            i = e + 2
            continue
        m = RE_BEGIN_END.match(body, j)
        if m and m.group(1) == "begin":
            env_full = m.group(2)
            star = env_full.endswith("*")
            env = env_full.rstrip("*")
            if env in NUMBERED or env in UNNUMBERED:
                # find the matching \end{env_full}, counting nested same-name blocks
                depth, p = 1, m.end()
                end_re = re.compile(r"\\(begin|end)\s*\{" + re.escape(env_full) + r"\}")
                while depth and p < n:
                    mm = end_re.search(body, p)
                    if not mm:
                        p = n
                        break
                    depth += 1 if mm.group(1) == "begin" else -1
                    p = mm.end()
                inner = body[m.end():p - len("\\end{%s}" % env_full)] if depth == 0 else body[m.end():]
                if env == "alignat" or env == "xalignat":
                    inner = re.sub(r"^\s*\{\d+\}", "", inner)
                num, tag = count_numbered(env, star, inner)
                res["displays"] += 1
                res["numbered"] += num
                res["tagged"] += tag
                res["by_env"][env_full] = res["by_env"].get(env_full, 0) + 1
                i = p
                continue
            i = m.end()
            continue
        i = j + 2 if j >= 0 else n                      # a control symbol or the first letter of a word
    return res


def count_document(tex):
    s = strip_comments(tex)
    sh = shorthands(s)
    parts = s.split("\\begin{document}", 1)
    body = parts[1] if len(parts) == 2 else s
    body = body.split("\\end{document}", 1)[0]
    body = expand_shorthands(body, sh)
    out = scan(body)
    out["shorthands"] = sorted(sh)
    return out


def source_for(raw_src, main_tex, flat_path):
    """(text, which): the raw main file if it includes no other .tex file, else flat.tex."""
    if main_tex:
        p = os.path.join(raw_src, main_tex)
        if os.path.isfile(p) and not os.path.islink(p):
            with open(p, "rb") as f:
                t = f.read(64 << 20).decode("utf-8", errors="replace")
            if not RE_INCLUDE.search(strip_comments(t)):
                return t, "raw main file"
    if os.path.isfile(flat_path):
        with open(flat_path, "rb") as f:
            return f.read(64 << 20).decode("utf-8", errors="replace"), "flat.tex"
    return None, "none"
