"""Statements with paper locators, extracted from the tracks' reference documents.

Reads each document with `git show <branch>:<path>` (the tip of the owner's branch; the
commit is recorded) and writes one JSON object per located statement:

    key, owner, request, doc, doc_line, paper_id, version, file, ranges [[lo, hi], ...],
    text (the track's own wording of the clause), track_label, kind, values (F)

Parsers (one per document style; [JUDGEMENT] heuristics, checked afterwards by
kb/serve_locate.py check, which flags every locator that does not resolve):
  A  scope/REFERENCES.md      '## arXiv:<id> v<N>, ... (`file`)', bullets with L<lo>-<hi>
  B  scope/REFERENCES.md      '### <id> (`file`)', bullets with (lo-hi), 'lines lo-hi', ': lo-hi'
  C  stage/G0/REPORT.md s. 6  table rows '| statement | <id> `file:lines` |'
  F  stage/G0/SCOPING.md s. 8 table rows '| statement | <id>/v<N>/src/<file>:<lines> |'
  F  newton3/hills3/reference.py  dict entries (value, "<TAG> file:lines (...)"), read with ast

Usage: python3 -I extract_track_locators.py <out.jsonl>
Runs from the kb worktree (git reads the local branches); nothing outside git is read.
"""
import ast
import json
import re
import subprocess
import sys

WT = "/data/haiyangw/nrpic/wt/kb"
ID = r"(?:\d{4}\.\d{4,5}|(?:astro-ph|gr-qc|hep-th|hep-ph|physics|math-ph|nucl-th|quant-ph)/\d{7})"
LABEL_RE = re.compile(r"\[(VERIFIED|JUDGEMENT|TO VERIFY|BACKGROUND)\b[^\]]*\]")


def git_show(spec):
    return subprocess.run(["git", "-C", WT, "show", spec], check=True, capture_output=True,
                          text=True).stdout


def git_commit(branch, path):
    return subprocess.run(["git", "-C", WT, "log", "-1", "--format=%h", branch, "--", path],
                          check=True, capture_output=True, text=True).stdout.strip()


def bullets(lines, start, end):
    """(first line number, joined text) of each '- ' bullet with its indented continuation."""
    out, cur, at = [], None, None
    for i in range(start, end):
        ln = lines[i]
        if ln.startswith("- "):
            if cur is not None:
                out.append((at, cur))
            cur, at = ln[2:].strip(), i + 1
        elif cur is not None and ln.startswith("  ") and ln.strip():
            cur += " " + ln.strip()
        else:
            if cur is not None:
                out.append((at, cur))
            cur = None
    if cur is not None:
        out.append((at, cur))
    return out


def kind_of(head):
    h = head.lower()
    if h.startswith("not computed") or "caveat" in h:
        return "limitation"
    if any(w in h for w in ("set-up", "setup", "method", "gauge", "matter", "resolution",
                            "initial", "numerical", "particle load", "data")):
        return "method"
    return "result"


def clauses(text, spans):
    """Split a bullet at its locator groups: [(clause text, group span, group ranges)]."""
    out, prev = [], 0
    for (a, b, ranges) in spans:
        cl = text[prev:a]
        cl = re.sub(r"^[\s).,;:]+", "", cl)
        cl = re.sub(r"[\s(,;:]+(?:abstract|Abstract|caption|lines?|also)?[\s(,;:]*$", "", cl)
        out.append((cl.strip(), (a, b), ranges))
        prev = b
    return out


def parse_ranges(s):
    rs = []
    for part in re.split(r"\s*(?:,|;|\band\b)\s*", s):
        m = re.fullmatch(r"L?(\d+)(?:\s*-\s*L?(\d+|\.\.\.))?", part.strip())
        if not m:
            continue
        lo = int(m.group(1))
        hi = lo if not m.group(2) or m.group(2) == "..." else int(m.group(2))
        if hi < lo:
            hi = int(str(lo)[:len(str(lo)) - len(m.group(2))] + m.group(2))
        rs.append([lo, hi])
    return rs


# ------------------------------------------------------------------ A
A_HEAD = re.compile(r"^## arXiv:(" + ID + r") (v\d+),.*?\(`([^`]+)`")
A_TOK = re.compile(r"\bL\d+(?:\s*-\s*\d+)?(?:(?:\s*,\s*|\s+and\s+)L\d+(?:\s*-\s*\d+)?)*")


def parse_A(doc, lines, owner, request, commit):
    out, cur = [], None
    heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")] + [len(lines)]
    for hi_i, h in enumerate(heads[:-1]):
        m = A_HEAD.match(lines[h])
        if not m:
            continue
        pid, ver, fname = m.group(1), m.group(2), m.group(3).split(";")[0].strip()
        n = 0
        for at, text in bullets(lines, h + 1, heads[hi_i + 1]):
            head = text.split(":", 1)[0]
            lab = LABEL_RE.search(head)
            blabel = lab.group(1) if lab else None
            spans = [(t.start(), t.end(), parse_ranges(t.group(0))) for t in A_TOK.finditer(text)]
            for cl, (a, b), ranges in clauses(text, spans):
                if not ranges:
                    continue
                inl = LABEL_RE.search(cl)
                tl = inl.group(1) if inl and inl.start() > 0 and not cl.startswith(head) else blabel
                if cl.startswith(head):
                    cl = cl[len(head):].lstrip(" :")
                n += 1
                out.append(dict(key=f"{owner}/{pid}/{n:02d}", owner=owner, request=request,
                                doc=f"{doc}@{commit}", doc_line=at, paper_id=pid, version=ver,
                                file=fname, ranges=ranges, text=cl, track_label=tl or "TO VERIFY",
                                kind=kind_of(head)))
    return out


# ------------------------------------------------------------------ B
B_HEAD = re.compile(r"^### (" + ID + r") \(`([^`]+)`\)")
B_TOKS = [
    re.compile(r"\((?:also\s+)?(\d{2,5}(?:\s*-\s*\d{2,5})?(?:\s*,\s*\d{2,5}(?:\s*-\s*\d{2,5})?)*)\)"),
    re.compile(r"\blines?\s+(\d{2,5}(?:\s*-\s*(?:\d{2,5}|\.\.\.))?(?:\s*,\s*\d{2,5}(?:\s*-\s*\d{2,5})?)*)"),
    re.compile(r"(?:^|[:;]|\b[Aa]bstract)\s*(\d{2,5}\s*-\s*(?:\d{2,5}|\.\.\.)(?:\s*,\s*\d{2,5}(?:\s*-\s*\d{2,5})?)*)"),
    re.compile(r":\s*(\d{3,5})(?=[.;\s]|$)"),
]


def parse_B(doc, lines, owner, request, commit, versions):
    out = []
    heads = [i for i, ln in enumerate(lines) if ln.startswith("#")] + [len(lines)]
    for hi_i, h in enumerate(heads[:-1]):
        m = B_HEAD.match(lines[h])
        if not m:
            continue
        pid, fname = m.group(1), m.group(2)
        n = 0
        for at, text in bullets(lines, h + 1, heads[hi_i + 1]):
            spans = []
            for rx in B_TOKS:
                for t in rx.finditer(text):
                    a, b = t.start(1), t.end(0)
                    if any(not (b <= s0 or a >= s1) for s0, s1, _ in spans):
                        continue
                    before = text[max(0, a - 60):a]
                    bt = re.findall(r"`([^`]+)`", before)
                    if bt and not bt[-1].endswith(".tex") and "TESTLOG" in bt[-1] + before or \
                            (bt and re.search(r"\.(?:md|py|cpp|hpp)$", bt[-1]) and
                             before.rfind("`") > len(before) - 25):
                        continue                      # a line of this repository, not the paper
                    spans.append((a, b, parse_ranges(t.group(1))))
            spans.sort()
            jud = text.find("[JUDGEMENT]")
            for cl, (a, b), ranges in clauses(text, spans):
                if not ranges:
                    continue
                tl = "JUDGEMENT" if 0 <= jud < a else "VERIFIED"
                n += 1
                out.append(dict(key=f"{owner}/{pid}/{n:02d}", owner=owner, request=request,
                                doc=f"{doc}@{commit}", doc_line=at, paper_id=pid,
                                version=versions.get(pid), file=fname, ranges=ranges, text=cl,
                                track_label=tl, kind="result"))
    return out


# ------------------------------------------------------------------ C and F tables
TAB_LOC = re.compile(r"(?:(" + ID + r")/(v\d+)/src/)?`?([\w./-]*\.tex)?`?:(\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*)")


def parse_table(doc, lines, owner, request, commit, start_pat, end_pat, prefix):
    out, n = [], 0
    s = next(i for i, ln in enumerate(lines) if re.match(start_pat, ln))
    e = next(i for i in range(s + 1, len(lines)) if re.match(end_pat, lines[i]))
    file_to_id = {}
    for i in range(s, e):
        ln = lines[i]
        if not ln.startswith("|") or set(ln.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in ("statement",):
            continue
        stmt, loc = cells[0], cells[1]
        idm = re.search(ID, loc)
        pid = idm.group(0) if idm else None
        cur_file, groups = None, []
        for t in TAB_LOC.finditer(loc):
            if t.group(1):
                pid = t.group(1)
            f = t.group(3)
            if f:
                cur_file = f
                if pid:
                    file_to_id[f] = pid
                elif f in file_to_id:
                    pid = file_to_id[f]
            if t.group(0).startswith(("athenak/", "src/")):
                continue
            if cur_file is None:
                continue
            groups.append((cur_file, parse_ranges(t.group(4))))
        if not pid or not groups:
            out.append(dict(key=f"{owner}/{prefix}/unparsed-{i + 1}", owner=owner, request=request,
                            doc=f"{doc}@{commit}", doc_line=i + 1, paper_id=pid or "?",
                            file="?", ranges=[], text=stmt, track_label="VERIFIED", kind="result",
                            unparsed=loc))
            continue
        # one statement per file of the row (a row may cite two files of one paper)
        for f, rs in groups:
            n += 1
            out.append(dict(key=f"{owner}/{pid}/{prefix}{n:02d}", owner=owner, request=request,
                            doc=f"{doc}@{commit}", doc_line=i + 1, paper_id=pid, file=f, ranges=rs,
                            text=stmt, track_label="VERIFIED", kind="result", locator_cell=loc))
    return out


# ------------------------------------------------------------------ F reference.py
def parse_refpy(doc, src, owner, request, commit):
    tree = ast.parse(src)
    docstr = ast.get_docstring(tree) or ""
    tags = {}
    for m in re.finditer(r"^(\w+)\s*=\s*arXiv:(" + ID + r") (v\d+), \S*/src/([\w./-]+)", docstr, re.M):
        tags[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    arrays = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and node.value.args:
            try:
                arrays[node.targets[0].id] = ast.literal_eval(node.value.args[0])
            except Exception:
                pass
    out = []
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)):
            continue
        dname = node.targets[0].id
        for k, v in zip(node.value.keys, node.value.values):
            key = ast.literal_eval(k)
            if not isinstance(v, ast.Tuple) or len(v.elts) != 2:
                continue
            val_node, note = v.elts[0], ast.literal_eval(v.elts[1])
            if isinstance(val_node, ast.Name):
                val = arrays.get(val_node.id)
            else:
                try:
                    val = ast.literal_eval(val_node)
                except Exception:
                    val = None
            m = re.match(r"(\w+)\s+([\w./-]+\.tex):(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)(.*)", note)
            if not m or m.group(1) not in tags:
                continue
            pid, ver, fname = tags[m.group(1)]
            ranges = parse_ranges(m.group(3))
            for extra in re.finditer(r"(?:also\s+|\(|,\s)(\d{3,4}-\d{3,4})(?=[),])", m.group(4)):
                ranges += parse_ranges(extra.group(1))
            values = []

            def flat(x):
                if isinstance(x, (list, tuple)):
                    for y in x:
                        flat(y)
                elif isinstance(x, dict):
                    for kk, y in x.items():
                        flat(y)
                elif isinstance(x, (int, float)) and not isinstance(x, bool):
                    values.append(repr(x))
            flat(val)
            out.append(dict(key=f"{owner}/{pid}/ref-{dname}-{key}", owner=owner, request=request,
                            doc=f"{doc}@{commit}", doc_line=getattr(k, "lineno", 0), paper_id=pid,
                            version=ver, file=fname, ranges=ranges,
                            text=f"{dname}[{key}] = {val!r}; {note}", values=values,
                            numbers_from="values", promote_on_numbers=True,
                            track_label="TO VERIFY", kind="number"))
    return out


def main(out_path):
    versions = {}
    B_TABLE = re.compile(r"^\| (" + ID + r") \((v\d+)\)")
    allst = []
    spec = ("track/A-emd-pbh", "tracks/A-emd-pbh/scope/REFERENCES.md")
    txt = git_show(":".join(spec))
    allst += parse_A(spec[1], txt.split("\n"), "A-emd-pbh", "ingest-s1-references", git_commit(*spec))
    spec = ("track/B-emd-gw", "tracks/B-emd-gw/scope/REFERENCES.md")
    txt = git_show(":".join(spec))
    for ln in txt.split("\n"):
        m = B_TABLE.match(ln)
        if m:
            versions[m.group(1)] = m.group(2)
    allst += parse_B(spec[1], txt.split("\n"), "B-emd-gw", "track-b-sources", git_commit(*spec), versions)
    spec = ("track/C-sidm", "tracks/C-sidm/stage/G0/REPORT.md")
    txt = git_show(":".join(spec))
    allst += parse_table(spec[1], txt.split("\n"), "C-sidm", "index-locators-typos", git_commit(*spec),
                         r"^## 6\.", r"^## 7\.", "r6-")
    spec = ("track/F-hills", "tracks/F-hills/stage/G0/SCOPING.md")
    txt = git_show(":".join(spec))
    allst += parse_table(spec[1], txt.split("\n"), "F-hills", "index-hills-sources", git_commit(*spec),
                         r"^## 8\.", r"^## 9\.", "s8-")
    spec = ("track/F-hills", "tracks/F-hills/newton3/hills3/reference.py")
    allst += parse_refpy(spec[1], git_show(":".join(spec)), "F-hills", "index-hills-sources",
                         git_commit(*spec))
    seen = {}
    with open(out_path, "w") as f:
        for st in allst:
            k = st["key"]
            if k in seen:                               # make keys unique
                seen[k] += 1
                st["key"] = f"{k}.{seen[k]}"
            else:
                seen[k] = 0
            f.write(json.dumps(st) + "\n")
    by = {}
    for st in allst:
        by[st["owner"]] = by.get(st["owner"], 0) + 1
    print(f"{len(allst)} statements: {by}")


if __name__ == "__main__":
    main(sys.argv[1])
