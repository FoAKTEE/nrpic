"""K2 step 4 (brief 12.4): collect \\newcommand, \\renewcommand, \\providecommand, \\def and
\\DeclareMathOperator, and expand them at the text level only (string substitution of #1..#9).
TeX is never executed. Expansion is bounded in depth and in size.
"""
import re

CS_RE = re.compile(r"\\([A-Za-z@]+)|\\(.)", re.S)
MAX_DEPTH = 8
MAX_GROWTH = 20            # expanded text at most this many times the input (and 200k characters)


def skip_space(s, i):
    while i < len(s) and s[i] in " \t\n\r":
        i += 1
    return i


def read_group(s, i, open_="{", close="}"):
    """s[i] must be open_ (after optional spaces). Returns (content, end) or (None, i)."""
    j = skip_space(s, i)
    if j >= len(s) or s[j] != open_:
        return None, i
    depth, k = 0, j
    while k < len(s):
        c = s[k]
        if c == "\\":
            k += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if open_ == "{" and depth == 0:
                return s[j + 1:k], k + 1
        elif open_ == "[" and c == "]" and depth == 0:
            return s[j + 1:k], k + 1
        if open_ == "[" and c == "[" and k == j:
            pass
        k += 1
    return None, i


def read_arg(s, i):
    """One undelimited TeX argument: a {group} or a single token. Returns (text, end) or (None, i)."""
    j = skip_space(s, i)
    if j >= len(s):
        return None, i
    if s[j] == "{":
        return read_group(s, j)
    if s[j] == "\\":
        m = CS_RE.match(s, j)
        return m.group(0), m.end()
    if s[j] in "}":
        return None, i
    return s[j], j + 1


def read_csname(s, i):
    """\\name or {\\name} at s[i:]. Returns (name, end) or (None, i)."""
    j = skip_space(s, i)
    if j < len(s) and s[j] == "{":
        g, e = read_group(s, j)
        if g is None:
            return None, i
        m = re.fullmatch(r"\s*\\([A-Za-z@]+|.)\s*", g)
        return (m.group(1), e) if m else (None, i)
    m = CS_RE.match(s, j)
    if m:
        return (m.group(1) or m.group(2)), m.end()
    return None, i


DEF_KINDS = ("newcommand", "renewcommand", "providecommand", "DeclareRobustCommand", "DeclareMathOperator",
             "def", "gdef", "edef", "xdef", "newcommandx")
DEF_START = re.compile(r"\\(" + "|".join(DEF_KINDS) + r")(\*?)(?![A-Za-z@])")
_KIND = "(" + "|".join(DEF_KINDS) + ")"
# an alias of a definition command: \newcommand{\nc}{\newcommand}, \def\nc{\newcommand},
# \let\nc\newcommand (the body must be the bare command, so a macro that defines another is no alias)
ALIAS_DEF_RE = re.compile(
    r"\\(?:newcommand|renewcommand|providecommand)\*?\s*\{\s*\\([A-Za-z@]+)\s*\}\s*\{\s*\\" + _KIND + r"\s*\}"
    r"|\\(?:newcommand|renewcommand|providecommand)\*?\s*\\([A-Za-z@]+)\s*\{\s*\\" + _KIND + r"\s*\}"
    r"|\\(?:def|gdef)\s*\\([A-Za-z@]+)\s*\{\s*\\" + _KIND + r"\s*\}"
    r"|\\let\s*\\([A-Za-z@]+)\s*=?\s*\\" + _KIND + r"(?![A-Za-z@])")


def definition_aliases(text):
    """{alias: definition command} for aliases such as \\nc -> newcommand."""
    out = {}
    for m in ALIAS_DEF_RE.finditer(text):
        g = m.groups()
        for k in range(0, len(g), 2):
            if g[k]:
                if g[k] not in DEF_KINDS:
                    out[g[k]] = g[k + 1]
                break
    return out


def collect(text):
    """Macro definitions in text (preamble and body). Returns {name: spec}; the first
    \\newcommand wins over a later \\providecommand, a \\renewcommand or \\def overrides.
    Definitions written through an alias of a definition command (\\nc for \\newcommand)
    count as definitions of that command."""
    macros = {}
    aliases = definition_aliases(text)
    start = DEF_START
    if aliases:
        start = re.compile(r"\\(" + "|".join(list(DEF_KINDS) + sorted(aliases, key=len, reverse=True))
                           + r")(\*?)(?![A-Za-z@])")
    for m in start.finditer(text):
        kind, star = aliases.get(m.group(1), m.group(1)), m.group(2)
        i = m.end()
        name, i = read_csname(text, i)
        if not name:
            continue
        if kind == "DeclareMathOperator":
            body, e = read_group(text, i)
            if body is None:
                continue
            macros[name] = {"nargs": 0, "default": None, "body": "\\operatorname%s{%s}" % (star, body),
                            "kind": kind, "at": m.start()}
            continue
        if kind in ("def", "gdef", "edef", "xdef"):
            pm = re.match(r"((?:#[1-9])*)\s*\{", text[i:i + 40])
            if not pm:
                continue                       # delimited parameters: not expanded
            nargs = len(pm.group(1)) // 2
            body, e = read_group(text, i + pm.end() - 1)
            if body is None:
                continue
            macros[name] = {"nargs": nargs, "default": None, "body": body, "kind": kind, "at": m.start()}
            continue
        nargs, default = 0, None
        g, j = read_group(text, i, "[", "]")
        if g is not None:
            try:
                nargs = int(g.strip())
            except ValueError:
                continue
            i = j
            g2, j2 = read_group(text, i, "[", "]")
            if g2 is not None:
                default, i = g2, j2
        body, e = read_group(text, i)
        if body is None:
            continue
        if kind == "providecommand" and name in macros:
            continue
        macros[name] = {"nargs": max(0, min(nargs, 9)), "default": default, "body": body, "kind": kind,
                        "at": m.start()}
    return macros


ENV_ALIAS_RE = re.compile(r"^\s*\\(begin|end)\s*\{([A-Za-z*]+)\}\s*$")
ENV_SEQ_RE = re.compile(r"^\s*(?:\\(?:begin|end)\s*\{[A-Za-z*]+\}\s*)+$")
ENV_ONE_RE = re.compile(r"\\(begin|end)\s*\{([A-Za-z*]+)\}")


def env_aliases(macros):
    """Macros that stand for \\begin{env} or \\end{env} (\\be, \\ee, \\bea, ...), or for a
    sequence of them only (\\bea = \\begin{equation}\\begin{aligned}): {name: replacement}.
    Used before structure extraction so that equations written with such shorthands are found."""
    out = {}
    for name, sp in macros.items():
        if sp["nargs"] == 0 and ENV_SEQ_RE.match(sp["body"]):
            out[name] = "".join("\\%s{%s}" % (mm.group(1), mm.group(2)) for mm in ENV_ONE_RE.finditer(sp["body"]))
    return out


def substitute_aliases(text, aliases):
    if not aliases:
        return text
    pat = re.compile(r"\\(" + "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True))
                     + r")(?![A-Za-z@])")
    return pat.sub(lambda m: aliases[m.group(1)], text)


def _apply(body, args):
    out = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == "#" and i + 1 < len(body):
            d = body[i + 1]
            if d.isdigit() and d != "0":
                k = int(d)
                out.append(args[k - 1] if k <= len(args) else "")
                i += 2
                continue
            if d == "#":
                out.append("#")
                i += 2
                continue
        out.append(c)
        i += 1
    return "".join(out)


def expand_once(s, macros):
    """One pass of expansion. Returns (text, n_expanded)."""
    out, i, n = [], 0, 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            j = s.find("\\", i)
            j = len(s) if j < 0 else j
            out.append(s[i:j])
            i = j
            continue
        m = CS_RE.match(s, i)
        if not m:
            out.append(c)
            i += 1
            continue
        name = m.group(1)
        sp = macros.get(name) if name else None
        if sp is None:
            out.append(m.group(0))
            i = m.end()
            continue
        k = m.end()
        args = []
        ok = True
        for a in range(sp["nargs"]):
            if a == 0 and sp["default"] is not None:
                g, e = read_group(s, k, "[", "]")
                if g is not None:
                    args.append(g)
                    k = e
                else:
                    args.append(sp["default"])
                continue
            g, e = read_arg(s, k)
            if g is None:
                ok = False
                break
            args.append(g)
            k = e
        if not ok:
            out.append(m.group(0))
            i = m.end()
            continue
        body = _apply(sp["body"], args)
        # a control word followed by a letter needs a separating space
        if body and re.search(r"\\[A-Za-z@]+$", body) and k < len(s) and s[k].isalpha():
            body += " "
        out.append(body)
        i = k
        n += 1
    return "".join(out), n


def expand(s, macros, max_depth=MAX_DEPTH):
    """Expand the paper's own macros in s. Returns (text, stats) with stats = dict(expanded,
    depth, truncated)."""
    if not macros:
        return s, {"expanded": 0, "depth": 0, "truncated": False}
    limit = max(200000, MAX_GROWTH * len(s))
    total, depth = 0, 0
    for depth in range(1, max_depth + 1):
        t, n = expand_once(s, macros)
        if len(t) > limit:
            return s, {"expanded": total, "depth": depth, "truncated": True}
        s = t
        total += n
        if n == 0:
            break
    return s, {"expanded": total, "depth": depth, "truncated": False}


def control_words(s):
    return [m.group(1) for m in CS_RE.finditer(s) if m.group(1)]
