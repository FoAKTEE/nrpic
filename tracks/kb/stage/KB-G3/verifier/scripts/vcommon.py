"""Read-only helpers of the KB-G3 verifier (standard library only; run with python3 -I).

The snapshot is opened read-only and immutable; raw sources are read as text and never
executed. Nothing here writes outside the output directory a script is given.
"""
import os
import re
import sqlite3

ROOT = "/data/haiyangw/nrpic"
SNAPSHOT = os.path.join(ROOT, "kb-data/db/kb-20261121-aa0a2ae.sqlite")
RAW = os.path.join(ROOT, "kb-data/raw/arxiv")
REPO = os.path.join(ROOT, "wt/kb")


def connect(path=SNAPSHOT):
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % path, uri=True)


def paper_dir(paper_id):
    return os.path.join(RAW, paper_id.replace("/", "_"))


def src_dir(paper_id, version):
    return os.path.join(paper_dir(paper_id), version, "src")


def versions(paper_id):
    d = paper_dir(paper_id)
    if not os.path.isdir(d):
        return []
    return sorted(v for v in os.listdir(d) if re.fullmatch(r"v\d+", v))


def read_text(path):
    with open(path, "rb") as f:
        b = f.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", "replace")


def source_lines(paper_id, version, fname):
    p = os.path.join(src_dir(paper_id, version), fname)
    if not os.path.isfile(p):
        return None
    return read_text(p).split("\n")


# ---------------------------------------------------------------- own flattening of raw TeX

_INPUT = re.compile(r"\\(input|include|subfile)\s*(?:\{([^}]+)\}|([^\s{}\\%]+))")


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[: m.start()] if m else line)
    return "\n".join(out)


def tex_files(sdir):
    out = []
    for dp, _dn, fn in os.walk(sdir):
        for f in fn:
            if f.lower().endswith((".tex", ".ltx", ".latex")):
                out.append(os.path.relpath(os.path.join(dp, f), sdir))
    return sorted(out)


def find_main(sdir):
    files = tex_files(sdir)
    cands = []
    included = set()
    for f in files:
        t = strip_comments(read_text(os.path.join(sdir, f)))
        for m in _INPUT.finditer(t):
            name = (m.group(2) or m.group(3) or "").strip()
            included.add(os.path.normpath(name if name.endswith(".tex") else name + ".tex"))
        if re.search(r"\\document(class|style)", t) and "\\begin{document}" in t:
            cands.append((f, len(t)))
    if not cands:
        # plain TeX or unusual: the largest file that is not included by another
        rest = [(f, os.path.getsize(os.path.join(sdir, f))) for f in files
                if os.path.normpath(f) not in included]
        rest = rest or [(f, os.path.getsize(os.path.join(sdir, f))) for f in files]
        return max(rest, key=lambda x: x[1])[0] if rest else None
    top = [c for c in cands if os.path.normpath(c[0]) not in included] or cands
    return max(top, key=lambda x: x[1])[0]


def flatten(sdir, main, depth=0, seen=None):
    seen = seen if seen is not None else set()
    path = os.path.join(sdir, main)
    if depth > 12 or main in seen or not os.path.isfile(path):
        return ""
    seen.add(main)
    t = strip_comments(read_text(path))
    base = os.path.dirname(main)

    def rep(m):
        name = (m.group(2) or m.group(3) or "").strip()
        for cand in (name, name + ".tex", os.path.join(base, name), os.path.join(base, name + ".tex")):
            cand = os.path.normpath(cand)
            if os.path.isfile(os.path.join(sdir, cand)):
                return flatten(sdir, cand, depth + 1, seen)
        return ""

    return _INPUT.sub(rep, t)


def own_flat(paper_id, version):
    sdir = src_dir(paper_id, version)
    if not os.path.isdir(sdir):
        return None, None
    main = find_main(sdir)
    if main is None:
        return None, None
    return main, flatten(sdir, main)


CITE = re.compile(r"\\([A-Za-z]*cite[A-Za-z]*)\*?\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}")


def cited_keys(flat):
    keys = []
    for m in CITE.finditer(flat):
        if m.group(1).lower() in ("citestyle", "bibliographystyle"):
            continue
        for k in m.group(2).split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
    return keys


def body_of(flat):
    i = flat.find("\\begin{document}")
    return flat[i:] if i >= 0 else flat


def word_count(text):
    t = re.sub(r"\\[A-Za-z@]+\*?", " ", text)
    t = re.sub(r"\$[^$]*\$", " ", t)
    return len(re.findall(r"[A-Za-z]{2,}", t))


DISPLAY = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray|flalign|alignat|split|dmath)\*?\}")


def display_count(flat):
    b = body_of(flat)
    n = 0
    for m in DISPLAY.finditer(b):
        if m.group(1) != "split":
            n += 1
    n += len(re.findall(r"(?<!\\)\\\[", b))
    n += len(re.findall(r"\$\$", b)) // 2
    return n


def section_count(flat):
    return len(re.findall(r"\\(?:sub)?section\*?\s*(?:\[[^\]]*\])?\s*\{", body_of(flat)))
