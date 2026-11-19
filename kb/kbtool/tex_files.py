"""K2 steps 1-3 (brief 12.4): find the main file, flatten \\input/\\include/\\subfile/\\import
with a source map, and strip comments into a separate list.

Everything here reads the extracted tree under kb-data/raw as bytes and text. Nothing in it is
executed or compiled; paths named inside the TeX are resolved only inside the tree (no
absolute paths, no `..` out of the root, no symbolic links) with depth and size limits.
"""
import bisect
import json
import os
import re

MAX_FILE_BYTES = 20 * 1024 * 1024        # a single TeX file larger than this is data, not text [JUDGEMENT]
MAX_FLAT_CHARS = 60 * 1024 * 1024        # total flattened text
MAX_DEPTH = 16
TEX_EXT = (".tex", ".ltx", ".latex", ".txt", "")   # extensions tried for a main-file candidate

VERBATIM_ENVS = ("verbatim", "Verbatim", "lstlisting", "minted", "alltt")
INPUT_RE = re.compile(
    r"\\(input|include|subfile|import|subimport|inputfrom|subinputfrom|includefrom|subincludefrom)"
    r"(?![A-Za-z@])\s*")
DOCCLASS_RE = re.compile(r"\\document(?:class|style)(?![A-Za-z@])")
BEGIN_DOC_RE = re.compile(r"\\begin\s*\{document\}")


def decode(raw):
    """Bytes -> str. UTF-8 when it decodes, else Latin-1 (never fails). Returns (text, encoding)."""
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("latin-1"), "latin-1"


def read_text(path):
    if os.path.islink(path) or not os.path.isfile(path):
        raise OSError(f"not a regular file: {path}")
    size = os.path.getsize(path)
    if size > MAX_FILE_BYTES:
        raise OSError(f"file larger than {MAX_FILE_BYTES} bytes: {path}")
    with open(path, "rb") as f:
        return decode(f.read())


# ------------------------------------------------------------------ comments
def comment_start(line):
    """Index of the first comment character % in a line, or -1. A backslash escapes the next
    character (so \\% is a percent sign and \\\\% starts a comment); \\verb|...| is skipped."""
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c == "\\":
            if line.startswith("\\verb", i) and i + 5 < n and not line[i + 5].isalpha():
                j = i + 5
                if line[j] == "*":
                    j += 1
                if j < n:
                    delim = line[j]
                    k = line.find(delim, j + 1)
                    i = (k + 1) if k >= 0 else n
                    continue
            i += 2
            continue
        if c == "%":
            return i
        i += 1
    return -1


IFFALSE_RE = re.compile(r"^\s*\\iffalse(?![A-Za-z@])")
IF_RE = re.compile(r"\\if[A-Za-z@]*(?![A-Za-z@])|\\newif(?![A-Za-z@])")
FI_RE = re.compile(r"\\fi(?![A-Za-z@])")
BEGIN_COMMENT_RE = re.compile(r"^\s*\\begin\s*\{comment\}")
END_COMMENT_RE = re.compile(r"\\end\s*\{comment\}")
BEGIN_VERB_RE = re.compile(r"\\begin\s*\{(" + "|".join(VERBATIM_ENVS) + r")\*?\}")


def strip_comments(text):
    """Split one file into body pieces and comments, line by line, with TeX semantics: a %
    removes the rest of the line and its end of line. Whole blocks \\begin{comment}..\\end{comment}
    and \\iffalse..\\fi (starting at the beginning of a line) also go to the comments.

    Returns (pieces, comments): pieces = [(line_no, col, text)] whose concatenation is the
    comment-free text; comments = [(line_no, text)]."""
    pieces, comments = [], []
    lines = text.split("\n")
    in_verb = None
    block = None            # ('comment', None) or ('iffalse', depth)
    for ln, line in enumerate(lines, start=1):
        last = ln == len(lines)
        eol = "" if last else "\n"
        if block is not None:
            comments.append((ln, line))
            if block[0] == "comment":
                if END_COMMENT_RE.search(line):
                    block = None
            else:
                depth = block[1]
                code = line[:comment_start(line)] if comment_start(line) >= 0 else line
                for m in re.finditer(r"\\if[A-Za-z@]*(?![A-Za-z@])|\\fi(?![A-Za-z@])", code):
                    depth += 1 if m.group(0) != "\\fi" else -1
                    if depth == 0:
                        rest = code[m.end():]
                        block = None
                        if rest.strip():
                            pieces.append((ln, m.end(), rest + eol))
                        break
                if block is not None:
                    block = ("iffalse", depth)
            continue
        if in_verb:
            pieces.append((ln, 0, line + eol))
            if re.search(r"\\end\s*\{" + re.escape(in_verb) + r"\*?\}", line):
                in_verb = None
            continue
        if BEGIN_COMMENT_RE.match(line):
            comments.append((ln, line))
            block = ("comment", None)
            if END_COMMENT_RE.search(line[line.index("comment") + 7:]):
                block = None
            continue
        if IFFALSE_RE.match(line):
            comments.append((ln, line))
            code = line
            cs = comment_start(code)
            if cs >= 0:
                code = code[:cs]
            depth = 0
            closed = False
            for m in re.finditer(r"\\if[A-Za-z@]*(?![A-Za-z@])|\\fi(?![A-Za-z@])", code):
                depth += 1 if m.group(0) != "\\fi" else -1
                if depth == 0:
                    closed = True
                    rest = code[m.end():]
                    if rest.strip():
                        pieces.append((ln, m.end(), rest + eol))
                    break
            if not closed:
                block = ("iffalse", depth)
            continue
        vm = BEGIN_VERB_RE.search(line)
        cs = comment_start(line)
        if vm and (cs < 0 or vm.start() < cs):
            in_verb = vm.group(1)
            pieces.append((ln, 0, line + eol))
            if re.search(r"\\end\s*\{" + re.escape(in_verb) + r"\*?\}", line[vm.end():]):
                in_verb = None
            continue
        if cs < 0:
            pieces.append((ln, 0, line + eol))
        else:
            if line[cs + 1:].strip():
                comments.append((ln, line[cs + 1:]))
            head = line[:cs]
            if head:
                pieces.append((ln, 0, head))      # the % also removes the end of line
    return pieces, comments


def strip_comments_text(text):
    return "".join(p[2] for p in strip_comments(text)[0])


# ------------------------------------------------------------------ paths inside the tree
def safe_join(root, rel):
    """Path of `rel` inside `root`, or None if it would leave the tree, is absolute, is a
    symbolic link or is not a regular file."""
    rel = rel.strip().strip('"').strip()
    if not rel or rel.startswith(("/", "~")) or "\x00" in rel or "#" in rel or "\\" in rel:
        return None
    norm = os.path.normpath(rel)
    if norm.startswith("..") or os.path.isabs(norm):
        return None
    p = os.path.join(root, norm)
    real_root = os.path.realpath(root)
    # every component must be a real directory/file, not a link
    cur = root
    for part in norm.split(os.sep):
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            return None
    if not os.path.realpath(p).startswith(real_root + os.sep):
        return None
    return p if os.path.isfile(p) else None


def resolve_input(root, name, cur_dir_rel, import_dir_rel, cmd):
    """Find the file an input command names. TeX resolves relative to the directory of the
    main file (the root); \\import and \\subimport relative to their directory argument. We
    also try the directory of the including file, which some submissions rely on."""
    tries = []
    bases = []
    if import_dir_rel is not None:
        bases.append(import_dir_rel)
    bases += ["", cur_dir_rel]
    exts = ("", ".tex") if cmd != "include" else (".tex", "")
    for b in bases:
        for e in exts:
            rel = os.path.normpath(os.path.join(b, name + e)) if b else os.path.normpath(name + e)
            if rel in tries:
                continue
            tries.append(rel)
            p = safe_join(root, rel)
            if p:
                return rel, p
    return None, None


def _group(s, i):
    """If s[i:] starts (after spaces) with {...}, return (content, end) else (None, i)."""
    j = i
    while j < len(s) and s[j] in " \t":
        j += 1
    if j >= len(s) or s[j] != "{":
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
            if depth == 0:
                return s[j + 1:k], k + 1
        k += 1
    return None, i


def parse_input_command(line, m):
    """Arguments of an input command found by INPUT_RE at match m.
    Returns (cmd, import_dir or None, name, end) or None."""
    cmd = m.group(1)
    i = m.end()
    if cmd in ("import", "subimport", "inputfrom", "subinputfrom", "includefrom", "subincludefrom"):
        d, i2 = _group(line, i)
        if d is None:
            return None
        name, i3 = _group(line, i2)
        if name is None:
            return None
        return cmd, d.strip(), name.strip(), i3
    name, i2 = _group(line, i)
    if name is not None:
        return cmd, None, name.strip(), i2
    if cmd == "input":                    # primitive form: \input file
        mm = re.match(r"([^\s{}\\%]+)", line[i:])
        if mm:
            return cmd, None, mm.group(1), i + mm.end()
    return None


# ------------------------------------------------------------------ main file
def read_00readme(root):
    """Hints of arXiv's 00README (json, or the older 00README.XXX text). Returns
    {'toplevel': [paths], 'ignore': [paths]}."""
    out = {"toplevel": [], "ignore": []}
    pj = safe_join(root, "00README.json")
    if pj:
        try:
            d = json.loads(read_text(pj)[0])
            for s in d.get("sources", []) or []:
                if isinstance(s, dict) and s.get("filename"):
                    usage = s.get("usage", "")
                    if usage == "toplevel":
                        out["toplevel"].append(s["filename"])
                    elif usage == "ignore":
                        out["ignore"].append(s["filename"])
        except Exception:
            pass
    for name in ("00README.XXX", "00README", "00readme.xxx"):
        p = safe_join(root, name)
        if p:
            for line in read_text(p)[0].splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "toplevelfile":
                    out["toplevel"].append(parts[0])
                elif len(parts) >= 2 and parts[1] == "ignore":
                    out["ignore"].append(parts[0])
    return out


def list_files(root):
    out = []
    for d, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(x for x in dirs if not os.path.islink(os.path.join(d, x)))
        for f in sorted(files):
            p = os.path.join(d, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            out.append(os.path.relpath(p, root))
    return out


def find_main(root):
    """Brief 12.4 step 1. Returns dict(main, candidates, reason, notes)."""
    files = list_files(root)
    hints = read_00readme(root)
    cands, inputs_of = [], {}
    for rel in files:
        ext = os.path.splitext(rel)[1].lower()
        if ext not in TEX_EXT:
            continue
        p = os.path.join(root, rel)
        if os.path.getsize(p) > MAX_FILE_BYTES:
            continue
        txt = strip_comments_text(read_text(p)[0])
        if DOCCLASS_RE.search(txt) and BEGIN_DOC_RE.search(txt):
            cands.append(rel)
        names = set()
        for m in INPUT_RE.finditer(txt):
            a = parse_input_command(txt, m)
            if a:
                names.add(os.path.normpath(os.path.join(a[1] or "", a[2])))
        inputs_of[rel] = names
    notes = []
    top = [os.path.normpath(t) for t in hints["toplevel"]]
    for t in top:
        if t in files:
            reason = "00README toplevel"
            if t not in cands:
                notes.append(f"00README names {t} but it has no \\documentclass and \\begin{{document}}")
            return {"main": t, "candidates": cands, "reason": reason, "notes": notes}
    cands = [c for c in cands if c not in hints["ignore"]]
    if len(cands) == 1:
        return {"main": cands[0], "candidates": cands, "reason": "only file with \\documentclass and \\begin{document}",
                "notes": notes}
    if len(cands) > 1:
        included = set()
        for c in cands:
            for n in inputs_of.get(c, ()):
                included |= {n, n + ".tex"}
        top_level = [c for c in cands if c not in included and os.path.splitext(c)[0] not in included]
        pool = top_level or cands
        stems_bbl = {os.path.splitext(f)[0] for f in files if f.endswith(".bbl")}
        with_bbl = [c for c in pool if os.path.splitext(c)[0] in stems_bbl]
        if len(with_bbl) == 1:
            return {"main": with_bbl[0], "candidates": cands, "reason": "candidate with a .bbl of the same name",
                    "notes": notes}
        pool = with_bbl or pool
        best = max(pool, key=lambda c: (os.path.getsize(os.path.join(root, c)), c))
        return {"main": best, "candidates": cands,
                "reason": "largest of several candidates not \\input by another", "notes": notes}
    # no LaTeX main file: plain TeX or fragments; take the largest .tex file
    tex = [f for f in files if os.path.splitext(f)[1].lower() in (".tex", ".ltx", ".latex")]
    if tex:
        best = max(tex, key=lambda c: (os.path.getsize(os.path.join(root, c)), c))
        notes.append("no file has both \\documentclass and \\begin{document}")
        return {"main": best, "candidates": [], "reason": "largest .tex file (no LaTeX main file)", "notes": notes}
    return {"main": None, "candidates": [], "reason": "no TeX file", "notes": notes}


# ------------------------------------------------------------------ flattening
class SourceMap:
    """Maps a character offset of the flattened text to (file, line, column)."""

    def __init__(self):
        self.starts, self.where = [], []

    def add(self, flat_offset, file_rel, line, col):
        self.starts.append(flat_offset)
        self.where.append((file_rel, line, col))

    def locate(self, offset):
        i = bisect.bisect_right(self.starts, offset) - 1
        if i < 0:
            return None
        f, line, col = self.where[i]
        return {"file": f, "line": line, "col": col + (offset - self.starts[i])}

    def to_json(self):
        return [[s, f, ln, c] for s, (f, ln, c) in zip(self.starts, self.where)]


def flatten(root, main_rel):
    """Brief 12.4 steps 2-3. Returns dict(flat, source_map, comments, files, unresolved, notes)."""
    parts, comments, used, unresolved, notes = [], [], [], [], []
    smap = SourceMap()
    total = [0]

    def emit(text, f, ln, col):
        if not text:
            return
        if total[0] + len(text) > MAX_FLAT_CHARS:
            raise OSError(f"flattened text exceeds {MAX_FLAT_CHARS} characters")
        smap.add(total[0], f, ln, col)
        parts.append(text)
        total[0] += len(text)

    def walk(rel, path, depth, stack, import_dir):
        if depth > MAX_DEPTH:
            notes.append(f"input depth above {MAX_DEPTH} at {rel}")
            return
        text, enc = read_text(path)
        used.append({"file": rel, "encoding": enc, "depth": depth})
        pieces, coms = strip_comments(text)
        for ln, c in coms:
            comments.append({"file": rel, "line": ln, "text": c})
        cur_dir = os.path.dirname(rel)
        for ln, col, piece in pieces:
            pos = 0
            for m in INPUT_RE.finditer(piece):
                if m.start() < pos:
                    continue
                # skip \input inside a macro definition (#1) or a control word like \inputencoding
                a = parse_input_command(piece, m)
                if not a:
                    continue
                cmd, idir, name, end = a
                if "#" in name:
                    continue
                emit(piece[pos:m.start()], rel, ln, col + pos)
                if idir is not None:
                    base_dir = os.path.normpath(os.path.join(import_dir or "", idir)) if cmd.startswith("sub") \
                        else os.path.normpath(idir)
                else:
                    base_dir = import_dir
                child_rel, child = resolve_input(root, name, cur_dir, base_dir, cmd)
                if child is None:
                    unresolved.append({"file": rel, "line": ln, "command": cmd, "name": name})
                    emit(piece[m.start():end], rel, ln, col + m.start())     # keep the command text
                elif child_rel in stack:
                    notes.append(f"input cycle at {rel}:{ln} -> {child_rel}")
                else:
                    if cmd == "include":
                        emit("\n", rel, ln, col + m.start())
                    walk(child_rel, child, depth + 1, stack | {child_rel},
                         base_dir if idir is not None else import_dir)
                    emit("\n" if cmd == "include" else " ", rel, ln, col + end)
                pos = end
            emit(piece[pos:], rel, ln, col + pos)

    walk(main_rel, os.path.join(root, main_rel), 0, {main_rel}, None)
    return {"flat": "".join(parts), "source_map": smap, "comments": comments, "files": used,
            "unresolved": unresolved, "notes": notes}


def group_comments(comments, max_gap=1):
    """Consecutive comment lines of the same file -> blocks {file, line_start, line_end, text}."""
    blocks = []
    for c in comments:
        if blocks and blocks[-1]["file"] == c["file"] and c["line"] - blocks[-1]["line_end"] <= max_gap:
            blocks[-1]["line_end"] = c["line"]
            blocks[-1]["text"] += "\n" + c["text"]
        else:
            blocks.append({"file": c["file"], "line_start": c["line"], "line_end": c["line"], "text": c["text"]})
    return blocks
