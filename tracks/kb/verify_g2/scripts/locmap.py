"""The verifier's own map from source lines to flat.tex characters (independent of the tool's
sourcemap.json, which is read only to cross-check).

Method: every expected source line is stripped of its TeX comment (an unescaped %) and of
surrounding white space; a line with at least MINLEN characters left is searched verbatim
in flat.tex (the flattened, comment-stripped main file keeps the text of each line). Unique
occurrences are anchors; a line with several occurrences takes the one nearest to the
median of the unique anchors (or, without unique anchors, the first one after the previous
anchor). Lines not found verbatim are tried once more with white space as a wildcard.
The expected range is [first anchor start, last anchor end).

The raw sources are read as text only (untrusted data); nothing is executed.
"""
import bisect
import hashlib
import json
import os
import re

import vg2common as C

MINLEN = 12


def strip_comment(line):
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if ch == "%":
            break
        out.append(ch)
        i += 1
    return "".join(out).strip()


def flat_path(pid):
    return os.path.join(C.BUILD_TEX, C.id_dir(pid), "flat.tex")


def flat_text(pid):
    return C.read_text(flat_path(pid))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def src_lines(pid, version, file):
    p = os.path.join(C.RAW_ARXIV, C.id_dir(pid), version, "src", file)
    return C.read_text(p).split("\n")


def _all(hay, needle):
    out, i = [], hay.find(needle)
    while i >= 0:
        out.append(i)
        i = hay.find(needle, i + 1)
    return out


def map_lines(pid, version, file, a, b, flat=None):
    """Return dict(start, end, n_lines, n_content, n_found, method) for source lines a..b (1-based)."""
    flat = flat if flat is not None else flat_text(pid)
    lines = src_lines(pid, version, file)
    found = []   # (line_no, [offsets], length)
    n_content = 0
    for ln in range(a, b + 1):
        s = strip_comment(lines[ln - 1]) if ln - 1 < len(lines) else ""
        if len(s) < MINLEN:
            continue
        n_content += 1
        occ = _all(flat, s)
        length = len(s)
        if not occ:
            toks = s.split()
            if toks:
                pat = r"\s+".join(re.escape(t) for t in toks)
                occ = [m.start() for m in re.finditer(pat, flat)]
                m = re.search(pat, flat)
                length = (m.end() - m.start()) if m else length
        if occ:
            found.append((ln, occ, length))
    if not found:
        return dict(start=None, end=None, n_lines=b - a + 1, n_content=n_content, n_found=0, method="none")
    uniq = [occ[0] for _, occ, _ in found if len(occ) == 1]
    anchors = []
    prev = None
    for ln, occ, length in found:
        if len(occ) == 1:
            o = occ[0]
        elif uniq:
            med = sorted(uniq)[len(uniq) // 2]
            o = min(occ, key=lambda x: abs(x - med))
        else:
            after = [x for x in occ if prev is None or x >= prev]
            o = after[0] if after else occ[0]
        anchors.append((o, o + length))
        prev = o
    # keep anchors that are mutually consistent (within 20000 chars of the median)
    mids = sorted(x for x, _ in anchors)
    med = mids[len(mids) // 2]
    good = [(s, e) for s, e in anchors if abs(s - med) < 20000]
    return dict(start=min(s for s, _ in good), end=max(e for _, e in good), n_lines=b - a + 1,
                n_content=n_content, n_found=len(good), method="verbatim")


def tool_range(pid, file, a, b):
    """The tool's own sourcemap range of lines a..b of `file` (for the cross-check only)."""
    p = os.path.join(C.BUILD_TEX, C.id_dir(pid), "sourcemap.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        sm = json.load(f)
    offs = [x[0] for x in sm]
    sel = [i for i, x in enumerate(sm) if os.path.basename(x[1]) == os.path.basename(file) and a <= x[2] <= b]
    if not sel:
        return None
    s = sm[sel[0]][0]
    e = sm[sel[-1] + 1][0] if sel[-1] + 1 < len(sm) else None
    return dict(start=s, end=e)
