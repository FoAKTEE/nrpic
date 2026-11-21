"""K7: module descriptions of AthenaK and the order of its task lists (brief 12.7):
`kb code modules`.

For src/z4c, src/particles, src/pgen, src/mesh and src/bvals of this repository (repo_id
local/nrpic, under athenak/) and of upstream AthenaK (IAS-Astrophysics/athenak), each at the
commit the code index records (table repos), every file is described from its own comments
only, without interpretation:
  path, line count; the header comment (the comment block at the top of the file, with the
  licence banner and the Doxygen markers removed): its `\\file` tag and its first sentences;
  the classes, structs, enums, functions and methods the code index found in the file
  (tree-sitter symbols, table symbols), each with the first sentence of the comment directly
  above its definition (`\\brief` text when there is one).
The task-list order is extracted from the source, not assumed:
  - Driver::Execute (src/driver/driver.cpp): the ExecuteTaskList calls in order, with the
    loops around them (once per cycle, or inside the loop over the explicit stages);
  - MeshBlockPack::AddPhysics (src/mesh/meshblock_pack.cpp): the calls that assemble each
    module's tasks, in order;
  - the numerical-relativity queues (src/tasklist/numerical_relativity.cpp): which task
    list each queue location (Task_Start, Task_Run, Task_End) is assembled into;
  - every AddTask and QueueTask call under src/ (comments removed): task function, list,
    dependencies, optional dependencies, the conditions around the call, and whether the
    task function, or a method of the same class it calls, mentions tmunu (the matter
    sources of Z4c).
Sources are read without running anything: this repository from git objects at the
indexed commit (git ls-tree, git cat-file); upstream from its clone in kb-data/raw/github
read as files, after checking that the clone's HEAD is the indexed commit. Outputs:
kb-data/build/code/<key>/modules.json (inside the writer lock) and a markdown report.
"""
import json
import os
import re
import subprocess
import time

from . import __version__
from .db import connect_ro, open_for_read
from .gitmeta import read_checkout
from .lock import writer_lock

MODULE_DIRS = ("z4c", "particles", "pgen", "mesh", "bvals")
REPOS = {"local/nrpic": "athenak/src/", "IAS-Astrophysics/athenak": "src/"}
ALIASES = {"this": "local/nrpic", "local": "local/nrpic", "athenak": "IAS-Astrophysics/athenak",
           "upstream": "IAS-Astrophysics/athenak"}
SOURCE_EXT = (".cpp", ".hpp", ".cc", ".h", ".c", ".cu", ".hh", ".cxx")
DEF_KINDS = ("class", "struct", "enum", "function", "method")
DRIVER = "driver/driver.cpp"
PACK = "mesh/meshblock_pack.cpp"
NUMREL = "tasklist/numerical_relativity.cpp"
STAGE_LOOP_RE = re.compile(r"^for\s*\(\s*int\s+stage\s*=")
STS_LOOP_RE = re.compile(r"^for\s*\(\s*int\s+sts_stage\s*=")
BANNER_RE = re.compile(r"^[\s=\-*/!#~_]*$|copyright|licen[cs]ed under|astrophysical (plasma|mhd|fluid)? ?code|"
                       r"\bathena(xxx|\+\+|k)\b.*\bcode\b", re.I)
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\\`\"'])")   # a numbered item starts a sentence


# ---------------------------------------------------------------- text helpers
def blank_comments(text, blank_strings=False):
    """Text of the same length with comments (and, if asked, string and character
    literals) replaced by spaces; newlines are kept, so offsets and lines stay valid."""
    out = list(text)
    i, n = 0, len(text)
    state = None
    while i < n:
        c = text[i]
        if state is None:
            if c == "/" and i + 1 < n and text[i + 1] == "/":
                state = "line"
                out[i] = out[i + 1] = " "
                i += 2
                continue
            if c == "/" and i + 1 < n and text[i + 1] == "*":
                state = "block"
                out[i] = out[i + 1] = " "
                i += 2
                continue
            if c in "\"'":
                state = c
                if blank_strings:
                    out[i] = " "
            i += 1
            continue
        if state == "line":
            if c == "\n":
                state = None
            else:
                out[i] = " "
            i += 1
            continue
        if state == "block":
            if c == "*" and i + 1 < n and text[i + 1] == "/":
                out[i] = out[i + 1] = " "
                state = None
                i += 2
                continue
            if c != "\n":
                out[i] = " "
            i += 1
            continue
        # inside a string or character literal
        if c == "\\" and i + 1 < n:
            if blank_strings:
                out[i] = " "
                if text[i + 1] != "\n":
                    out[i + 1] = " "
            i += 2
            continue
        if c == state or c == "\n":                 # an unterminated literal ends at the line end
            if blank_strings and c != "\n":
                out[i] = " "
            state = None
            i += 1
            continue
        if blank_strings:
            out[i] = " "
        i += 1
    return "".join(out)


def first_sentences(text, n=2, cap=400):
    t = re.sub(r"\s+", " ", text or "").strip()
    if not t:
        return ""
    parts = []
    for x in SENT_RE.split(t):                           # no split after "1." or an abbreviation
        if parts and re.search(r"(^|\s)(\d{1,2}|[a-z]|e\.g|i\.e|cf|Eqs?|Fig|Ref|Sec|vs|et al)\.$", parts[-1]):
            parts[-1] += " " + x
        else:
            parts.append(x)
    s = " ".join(parts[:n])
    if len(s) > cap:
        s = s[:cap].rsplit(" ", 1)[0] + " ..."
    return s


def _comment_text(line):
    """Text of a `//` comment line without the markers (//, //!, ///, \\brief); None if the
    line is not a line comment."""
    m = re.match(r"^\s*//+\s*!?<?\s?(.*)$", line)
    if not m:
        return None
    return m.group(1).rstrip()


def header_comment(text):
    """The comment block at the top of a file (before the first line of code; an include
    guard is skipped): {'file_tag', 'text', 'first_sentences', 'banner_lines', 'line_end'}."""
    lines = text.splitlines()
    body, banner, tag = [], 0, None
    i, in_block, end = 0, False, 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if in_block:
            seg = s
            if "*/" in seg:
                seg = seg.split("*/", 1)[0]
                in_block = False
            seg = re.sub(r"^\*+\s?", "", seg.strip())
            body.append(seg)
            end = i + 1
            i += 1
            continue
        if not s:
            if any(x.strip() and not BANNER_RE.search(x) for x in body):
                break                                    # the header ends at the first blank line after its text
            i += 1
            continue
        if re.match(r"^#\s*(ifndef|define)\b", s) and not body:
            i += 1                                       # include guard before the header
            continue
        if s.startswith("/*"):
            seg = s[2:].lstrip("*!")
            if "*/" in seg:
                seg = seg.split("*/", 1)[0]
            else:
                in_block = True
            body.append(seg.strip())
            end = i + 1
            i += 1
            continue
        t = _comment_text(ln)
        if t is None:
            break
        body.append(t)
        end = i + 1
        i += 1
    kept = []
    for t in body:
        if BANNER_RE.search(t):
            banner += 1
            continue
        m = re.match(r"^\s*[\\@]file\b\s*(\S*)\s*(.*)$", t)
        if m:
            tag = tag or (m.group(1) or None)
            if m.group(2).strip():
                kept.append(m.group(2).strip())
            continue
        t = re.sub(r"^\s*[\\@]brief\b\s*", "", t)
        kept.append(t.strip())
    joined = re.sub(r"\s+", " ", " ".join(x for x in kept if x)).strip()
    return {"file_tag": tag, "text": joined, "first_sentences": first_sentences(joined),
            "banner_lines": banner, "line_end": end}


def comment_above(lines, line_start, max_blank=2):
    """First sentence of the comment directly above a definition at line_start (1-based):
    the `\\brief` text when there is one, else the comment without separator and `\\fn`
    lines. Blank lines (at most max_blank) and template lines between are skipped."""
    i = line_start - 2
    blanks = 0
    while i >= 0:
        s = lines[i].strip()
        if not s:
            blanks += 1
            if blanks > max_blank:
                return None
            i -= 1
            continue
        if s.startswith("template") and not s.startswith("//"):
            i -= 1
            continue
        break
    if i < 0:
        return None
    block = []
    s = lines[i].strip()
    if s.endswith("*/"):                                  # a /* ... */ block ending here
        while i >= 0:
            block.insert(0, lines[i].strip())
            if "/*" in lines[i]:
                break
            i -= 1
        text = " ".join(block)
        text = re.sub(r"/\*+!?|\*+/|^\s*\*+", " ", text)
        return _brief_of([re.sub(r"^\s*\*+\s?", "", x) for x in text.split("\n")])
    while i >= 0:
        t = _comment_text(lines[i])
        if t is None:
            break
        block.insert(0, t)
        i -= 1
    return _brief_of(block) if block else None


def _brief_of(block):
    out, in_brief, saw_brief = [], False, False
    for t in block:
        st = t.strip()
        if not st or re.match(r"^[=\-*/~_]+$", st):
            if in_brief and out:
                in_brief = False
            continue
        if re.match(r"^[\\@](fn|class|struct|enum|file|namespace)\b", st):
            in_brief = False
            continue
        m = re.match(r"^[\\@]brief\b\s*(.*)$", st)
        if m:
            if saw_brief:
                break
            saw_brief = in_brief = True
            out = [m.group(1)]
            continue
        if saw_brief and not in_brief:
            continue
        out.append(st)
    s = first_sentences(" ".join(out), n=1, cap=240)
    return s or None


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def blocks(code, raw=None):
    """Brace blocks of comment-and-string-blanked code: [(open, close, header)], where
    header is the text (taken from raw when given, so string literals are kept) between the
    previous ; { or } and the opening brace, whitespace collapsed. An `else` block's header
    names the block before it."""
    raw = code if raw is None else raw
    out, stack = [], []
    last_sep = 0
    last_closed = {}                                     # depth -> index in out of the last block closed there
    paren = 0                                            # the ; of a for header does not end the header
    for i, c in enumerate(code):
        if c == "(":
            paren += 1
        elif c == ")":
            paren = max(0, paren - 1)
        elif c == "{":
            head = re.sub(r"\s+", " ", raw[last_sep:i]).strip()
            depth = len(stack)
            if head.startswith("else") and depth in last_closed:
                prev = out[last_closed[depth]][2]
                head = f"{head} (of {prev})"
            stack.append((i, head))
            last_sep = i + 1
        elif c == "}":
            if stack:
                o, head = stack.pop()
                out.append((o, i, head))
                last_closed[len(stack)] = len(out) - 1
                for d in [d for d in last_closed if d > len(stack)]:
                    del last_closed[d]
            last_sep = i + 1
        elif c == ";" and paren == 0:
            last_sep = i + 1
    return sorted(out)


def enclosing(blks, offset):
    """Headers of the blocks that contain offset, outermost first."""
    return [h for o, c, h in blks if o < offset < c]


def find_calls(code, name_re):
    """Calls matching name_re (a regex ending just before the open parenthesis) in blanked
    code: [(start, open_paren, close_paren)]; parentheses are matched."""
    out = []
    for m in re.finditer(name_re + r"\s*\(", code):
        op = m.end() - 1
        depth, j = 0, op
        while j < len(code):
            if code[j] == "(":
                depth += 1
            elif code[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((m.start(), op, j))
    return out


def split_args(s):
    """Top-level comma split of an argument list; (), {}, [] nest, and so do the angle
    brackets of a template name like &A<B, C>::f."""
    parts, depth, angle, cur = [], 0, 0, []
    for i, c in enumerate(s):
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        elif c == "<" and i > 0 and (s[i - 1].isalnum() or s[i - 1] == "_") and depth == 0:
            angle += 1
        elif c == ">" and angle and depth == 0:
            angle -= 1
        if c == "," and depth == 0 and angle == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def _brace_list(s):
    s = (s or "").strip()
    if s.startswith("{") and s.endswith("}"):
        return [x.strip() for x in s[1:-1].split(",") if x.strip()]
    return [s] if s else []


def _clean(s, cap=160):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= cap else s[:cap] + " ..."


# ---------------------------------------------------------------- sources
class GitSource:
    """Files of this repository at a commit, read from git objects (no worktree state)."""

    def __init__(self, home, commit, prefix):
        self.home, self.commit, self.prefix = home, commit, prefix
        out = subprocess.run(["git", "-C", home, "ls-tree", "-r", "-z", "--full-tree", commit, "--",
                              prefix.rstrip("/")], capture_output=True, check=True, timeout=600).stdout
        self.blobs = {}
        for rec in out.split(b"\0"):
            if not rec:
                continue
            meta, path = rec.split(b"\t", 1)
            mode, typ, obj = meta.split()
            if typ == b"blob" and mode != b"120000":
                self.blobs[path.decode()] = obj.decode()
        self._cache = {}

    def paths(self):
        return sorted(self.blobs)

    def read(self, path):
        if path not in self.blobs:
            return None
        if path not in self._cache:
            r = subprocess.run(["git", "-C", self.home, "cat-file", "blob", self.blobs[path]],
                               capture_output=True, check=True, timeout=120)
            self._cache[path] = r.stdout.decode("utf-8", errors="replace")
        return self._cache[path]

    def describe(self):
        return f"git objects of {self.home} at {self.commit}"


class CheckoutSource:
    """Files of a clone in kb-data/raw/github, read as files (never executed); links are
    not followed."""

    def __init__(self, root, prefix):
        self.root, self.prefix = root, prefix
        self._paths = []
        base = os.path.join(root, prefix.rstrip("/"))
        for dirpath, dirs, files in os.walk(base, followlinks=False):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(dirpath, f)
                if not os.path.islink(p) and os.path.isfile(p):
                    self._paths.append(os.path.relpath(p, root))

    def paths(self):
        return list(self._paths)

    def read(self, path):
        p = os.path.join(self.root, path)
        if path not in self._paths or os.path.islink(p):
            return None
        with open(p, "rb") as f:
            return f.read(8 << 20).decode("utf-8", errors="replace")

    def describe(self):
        return f"files of the clone {self.root}"


def repo_row(con, repo_id):
    r = con.execute("SELECT commit_sha, commit_date, url FROM repos WHERE repo_id = ?", (repo_id,)).fetchone()
    if not r:
        raise SystemExit(f"{repo_id} is not in the code index (kb ingest repo first)")
    return {"commit_sha": r[0], "commit_date": r[1], "url": r[2]}


def open_source(lay, repo_id, commit):
    prefix = REPOS[repo_id]
    if repo_id == "local/nrpic":
        return GitSource(lay.home, commit, prefix)
    root = os.path.join(lay.raw_github, repo_id.replace("/", "__"))
    head = read_checkout(root).get("commit_sha")
    if head != commit:
        raise SystemExit(f"clone {root} is at {head}, the index records {commit}")
    return CheckoutSource(root, prefix)


def load_symbols(con, repo_id, paths):
    """{path: [symbol rows]} from the code index, definitions only."""
    want = set(paths)
    out = {}
    q = ("SELECT f.path, s.name, s.qualname, s.kind, s.line_start, s.line_end FROM symbols s JOIN code_files f "
         "USING(file_id) WHERE f.repo_id = ? ORDER BY f.path, s.line_start")
    for path, name, qual, kind, a, b in con.execute(q, (repo_id,)):
        if path in want:
            out.setdefault(path, []).append({"name": name, "qualname": qual, "kind": kind, "line_start": a,
                                             "line_end": b})
    return out


# ---------------------------------------------------------------- file descriptions
def describe_file(path, text, syms):
    lines = text.splitlines()
    hdr = header_comment(text)
    defs = []
    for s in syms or []:
        if s["kind"] not in DEF_KINDS:
            continue
        defs.append({"kind": s["kind"], "name": s["name"], "qualname": s["qualname"], "line_start": s["line_start"],
                     "line_end": s["line_end"], "brief": comment_above(lines, s["line_start"])})
    return {"path": path, "lines": len(lines), "header": {k: hdr[k] for k in ("file_tag", "first_sentences",
                                                                             "banner_lines", "line_end")},
            "header_text": hdr["text"], "definitions": defs}


# ---------------------------------------------------------------- task lists
def driver_schedule(text):
    """ExecuteTaskList calls of Driver::Execute in source order, with their loops."""
    code = blank_comments(text, blank_strings=True)
    raw = blank_comments(text)
    blks = blocks(code, raw)
    fn = [b for b in blks if re.search(r"\bDriver::Execute\s*\(", b[2])]
    if not fn:
        return {"found": False, "calls": [], "stage_loop": None}
    o, c, _ = fn[0]
    calls, stage_loop = [], None
    for start, op, cp in find_calls(code, r"\bExecuteTaskList"):
        if not (o < start < c):
            continue
        args = split_args(raw[op + 1:cp])
        name = args[1].strip().strip('"') if len(args) > 1 else None
        heads = [h for bo, bc, h in blks if o < bo < start < bc]     # inside the function
        loops = [h for h in heads if h.startswith(("for", "while", "do"))]
        if any(STAGE_LOOP_RE.match(h) for h in heads):
            when = "each explicit stage"
            stage_loop = stage_loop or next(h for h in heads if STAGE_LOOP_RE.match(h))
        elif any(STS_LOOP_RE.match(h) for h in heads):
            when = "each super-time-stepping stage"
        else:
            when = "once per cycle"
        calls.append({"list": name, "stage_arg": args[2].strip() if len(args) > 2 else None,
                      "line": line_of(text, start), "when": when, "loops": [_clean(x, 100) for x in loops],
                      "conditions": [_clean(h, 100) for h in heads if h.startswith(("if", "else"))]})
    other = []
    if stage_loop:
        for bo, bc, h in blks:
            if h == stage_loop and o < bo < c:
                body = code[bo + 1:bc]
                rbody = raw[bo + 1:bc]
                pos = 0
                for stmt in body.split(";"):
                    st = rbody[pos:pos + len(stmt)]
                    pos += len(stmt) + 1
                    s = _clean(st, 120)
                    if s and "ExecuteTaskList" not in s:
                        other.append(s.lstrip("{} "))
                break
    return {"found": True, "line_start": line_of(text, o), "line_end": line_of(text, c), "calls": calls,
            "stage_loop": stage_loop, "other_statements_in_stage_loop": [x for x in other if x]}


def physics_assembly(text):
    """Calls inside MeshBlockPack::AddPhysics that hand the task lists to a module."""
    code = blank_comments(text, blank_strings=True)
    raw = blank_comments(text)
    blks = blocks(code, raw)
    fn = [b for b in blks if re.search(r"\bMeshBlockPack::AddPhysics\s*\(", b[2])]
    if not fn:
        return []
    o, c, _ = fn[0]
    out = []
    for start, op, cp in find_calls(code, r"[\w>\-\.]+->(?:Assemble\w*Tasks|Include\w*Task|Queue\w*Tasks)"):
        if not (o < start < c):
            continue
        call = _clean(raw[start:cp + 1], 140)
        heads = [h for bo, bc, h in blks if o < bo < start < bc]
        out.append({"line": line_of(text, start), "call": call,
                    "conditions": [_clean(h, 120) for h in heads if h.startswith(("if", "else", "switch"))]})
    return out


def nr_queue_map(text):
    """Task_Start/Task_Run/Task_End -> task list, from SelectQueue and the calls
    AssembleNumericalRelativityTasks(tl["..."], <queue>)."""
    code = blank_comments(text)
    loc_to_q = dict(re.findall(r"case\s+(Task_\w+)\s*:\s*return\s+(\w+)\s*;", code))
    q_to_list = {q: l for l, q in re.findall(
        r"AssembleNumericalRelativityTasks\s*\(\s*\w+\s*\[\s*\"([^\"]+)\"\s*\]\s*,\s*(\w+)\s*\)", code)}
    return {loc: q_to_list.get(q) for loc, q in loc_to_q.items()}


ADD_RE = r"(?:(\w+)\s*\[\s*\"([^\"]+)\"\s*\]|([A-Za-z_][\w]*(?:\s*->\s*\w+)*))\s*->\s*(AddTask|QueueTask)"
FN_RE = re.compile(r"^&\s*([A-Za-z_][\w:]*(?:<[^()]*?>)?(?:::\w+)*)")


def returning_blocks(blks, code, start):
    """Headers of the if/else blocks that come before offset start in the same function,
    lie on its path (their parent block contains start) and contain a return: the code at
    start runs only when they were not entered or did not return."""
    fns = [b for b in blks if b[0] < start < b[1] and re.search(r"\)\s*(const\s*)?$", b[2])
           and not b[2].startswith(("if", "else", "for", "while", "switch", "do"))]
    if not fns:
        return []
    fo = fns[-1][0]
    out = []
    for bo, bc, h in blks:
        if not (fo < bo and bc < start and h.startswith(("if", "else"))):
            continue
        if not re.search(r"\breturn\b", code[bo:bc]):
            continue
        parents = [x for x in blks if x[0] < bo and bc < x[1]]
        if parents and parents[-1][0] < start < parents[-1][1]:
            out.append(_clean(h, 100))
    return out


def registrations(path, text, syms):
    """Every AddTask/QueueTask call of one file (comments removed)."""
    code = blank_comments(text, blank_strings=True)
    raw = blank_comments(text)
    blks = blocks(code, raw)
    fns = [s for s in syms or [] if s["kind"] in ("function", "method") and s.get("line_end")]
    out = []
    for m in re.finditer(ADD_RE + r"\s*\(", raw):
        start, op = m.start(), m.end() - 1
        if code[op] != "(":
            continue
        depth, j = 0, op
        while j < len(code):
            if code[j] == "(":
                depth += 1
            elif code[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        args = split_args(raw[op + 1:j])
        if not args or not args[0].startswith("&"):
            continue                                     # the declaration of AddTask/QueueTask itself
        fm = FN_RE.match(args[0])
        func = fm.group(1) if fm else args[0]
        line = line_of(text, start)
        lhs = re.search(r"([\w.\[\]>\-]+)\s*=\s*$", raw[max(0, start - 80):start])
        kind = m.group(4)
        rec = {"path": path, "line": line, "call": kind, "task_function": func,
               "receiver": m.group(1) or (m.group(3) or "").replace(" ", ""),
               "list": m.group(2), "id": lhs.group(1) if lhs else None}
        if kind == "QueueTask":
            rest = args[1:]
            if rest and not rest[0].startswith(("Task_", "{")) and not re.match(r"^[A-Z][\w]*_\w+$", rest[0]):
                rest = rest[1:]                          # the object pointer (this, pmhd, ...)
            rec.update({"name": rest[0] if rest else None,
                        "name_string": rest[1].strip('"') if len(rest) > 1 else None,
                        "location": rest[2] if len(rest) > 2 else None,
                        "dependencies": _brace_list(rest[3]) if len(rest) > 3 else [],
                        "optional_dependencies": _brace_list(rest[4]) if len(rest) > 4 else []})
        else:
            rest = args[1:]
            if rest and rest[0] in ("this",) or (rest and not rest[0].startswith(("id.", "none")) and len(rest) > 1):
                rest = rest[1:]
            rec.update({"dependencies": [x.strip() for x in re.split(r"\s*\|\s*", rest[0])] if rest else []})
        heads = enclosing(blks, start)
        inner = [s for s in fns if s["line_start"] <= line <= s["line_end"]]
        rec["registered_in"] = min(inner, key=lambda s: s["line_end"] - s["line_start"])["qualname"] if inner else None
        rec["conditions"] = [_clean(h, 100) for h in heads if h.startswith(("if", "else", "switch", "for"))]
        rec["after_returning_blocks"] = returning_blocks(blks, code, start)
        out.append(rec)
    return out


def function_bodies(text, syms):
    """{qualname: body text} of the definitions in one file (lines from the index)."""
    lines = text.splitlines()
    out = {}
    for s in syms or []:
        if s["kind"] in ("function", "method") and s.get("line_end"):
            out.setdefault(s["qualname"], "\n".join(lines[s["line_start"] - 1:s["line_end"]]))
    return out


def _short(q):
    """Class::method part of a qualified name (namespaces dropped)."""
    parts = re.sub(r"<[^<>]*>", "", q).split("::")
    return "::".join(parts[-2:]) if len(parts) >= 2 else q


def tmunu_mentions(task_fn, bodies):
    """'direct', 'via <callee>' (a method of the same class called in the body), or None."""
    short = _short(task_fn)
    cands = [q for q in bodies if _short(q) == short]
    if not cands:
        return None
    body = blank_comments(bodies[cands[0]], blank_strings=True)
    if re.search(r"tmunu", body, re.I):
        return "direct"
    cls = short.split("::")[0] if "::" in short else None
    if not cls:
        return None
    via = []
    for name in re.findall(r"\b([A-Za-z_]\w*)\s*(?:<[^<>()]*>)?\s*\(", body):   # in the order of the calls
        for q in bodies:
            if _short(q) == f"{cls}::{name}" and q not in cands and name not in via:
                if re.search(r"tmunu", blank_comments(bodies[q], blank_strings=True), re.I):
                    via.append(name)
    return ("via " + ", ".join(f"{cls}::{x}" for x in via)) if via else None


def resolve_list(rec, nrmap, arg_lists):
    if rec["call"] == "QueueTask":
        return nrmap.get(rec.get("location")) or f"(queue {rec.get('location')})"
    if rec.get("list"):
        return rec["list"]
    fn = (rec.get("registered_in") or "").split("::")[-1]
    return arg_lists.get(fn) or f"(argument {rec.get('receiver')})"


def task_texts(src, prefix):
    """{path: text} of the C/C++ files that register tasks, and of the driver, AddPhysics
    and numerical-relativity files."""
    texts = {}
    for p in src.paths():
        if p.endswith(SOURCE_EXT):
            t = src.read(p)
            if t is not None and ("AddTask" in t or "QueueTask" in t or p.endswith((DRIVER, PACK, NUMREL))):
                texts[p] = t
    return texts


def describe_repo(lay, con, repo_id, log=print):
    info = repo_row(con, repo_id)
    prefix = REPOS[repo_id]
    src = open_source(lay, repo_id, info["commit_sha"])
    all_paths = src.paths()
    mod_paths = [p for p in all_paths if any(p.startswith(prefix + d + "/") for d in MODULE_DIRS)]
    syms = load_symbols(con, repo_id, [p for p in all_paths if p.endswith(SOURCE_EXT)])
    texts = task_texts(src, prefix)
    drv = driver_schedule(texts.get(prefix + DRIVER, ""))
    pack = physics_assembly(texts.get(prefix + PACK, ""))
    nrmap = nr_queue_map(texts.get(prefix + NUMREL, ""))
    arg_lists = {}
    for p, t in texts.items():                           # f(tl_map["stagen"], ...) hands a list to f
        for name, lst in re.findall(r"->\s*(\w+)\s*\(\s*\w+\s*\[\s*\"([^\"]+)\"\s*\]", blank_comments(t)):
            arg_lists.setdefault(name, lst)
    regs = []
    for p in sorted(texts):
        regs += registrations(p, texts[p], syms.get(p, []))
    # bodies of the task functions and of the other methods of their classes
    want_cls = {_short(r["task_function"]).split("::")[0] for r in regs}
    bodies = {}
    for p in sorted(syms):
        if any(_short(s["qualname"]).split("::")[0] in want_cls for s in syms[p]
               if s["kind"] in ("function", "method")):
            t = texts.get(p) or src.read(p)
            if t is not None:
                bodies.update(function_bodies(t, syms[p]))
    order, when = {}, {}
    for k, c in enumerate(drv["calls"]):
        order.setdefault(c["list"], k)
        when.setdefault(c["list"], c["when"])
    tasks = []
    for r in regs:
        lst = resolve_list(r, nrmap, arg_lists)
        rel = r["path"][len(prefix):] if r["path"].startswith(prefix) else r["path"]
        tasks.append(dict(r, path=rel, module=rel.split("/")[0], task_list=lst,
                          when=when.get(lst, "not run by Driver::Execute"), driver_order=order.get(lst),
                          tmunu=tmunu_mentions(r["task_function"], bodies)))
    files = []
    for p in mod_paths:
        t = src.read(p)
        if t is None:
            continue
        rel = p[len(prefix):]
        if not rel.endswith(SOURCE_EXT):
            files.append({"path": rel, "lines": len(t.splitlines()), "header": None, "header_text": None,
                          "definitions": [], "note": "not a C/C++ source file"})
            continue
        files.append(describe_file(rel, t, syms.get(p, [])))
    log(f"{repo_id} @ {info['commit_sha'][:12]}: {len(files)} files in {', '.join(MODULE_DIRS)}; "
        f"{len(tasks)} task registrations; driver lists {[c['list'] for c in drv['calls']]}")
    return {"repo_id": repo_id, "commit_sha": info["commit_sha"], "commit_date": info["commit_date"],
            "source": src.describe(), "path_prefix": prefix, "module_dirs": list(MODULE_DIRS), "files": files,
            "driver": dict(drv, file=DRIVER), "physics_assembly": {"file": PACK, "calls": pack},
            "nr_queue_map": {"file": NUMREL, "map": nrmap}, "list_arguments": arg_lists, "tasks": tasks,
            "tool_version": f"kbtool {__version__}", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def schedule(desc):
    """[(driver position, list, when, [(module, [tasks])])] in the order Driver::Execute runs
    the lists; lists no ExecuteTaskList call names come last."""
    by = {}
    for t in desc["tasks"]:
        by.setdefault(t["task_list"], []).append(t)
    seen, out = set(), []
    for k, c in enumerate(desc["driver"]["calls"]):
        if c["list"] in seen:
            continue
        seen.add(c["list"])
        out.append((k, c["list"], c["when"], _group(by.get(c["list"], []))))
    for lst in sorted(set(by) - seen, key=str):
        out.append((None, lst, "not run by Driver::Execute", _group(by[lst])))
    return out


def _group(tasks):
    mods = []
    for t in tasks:                                       # registration order within a module
        if not mods or mods[-1][0] != t["module"]:
            mods.append((t["module"], []))
        mods[-1][1].append(t)
    return mods


def source_writers(desc):
    """Tasks that mention tmunu, with their list and when they run."""
    return [t for t in desc["tasks"] if t.get("tmunu")]


# ---------------------------------------------------------------- outputs
def write_build(lay, desc):
    d = os.path.join(lay.build, "code", desc["repo_id"].replace("/", "__"))
    with writer_lock(lay, what=f"code modules {desc['repo_id']}"):
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "modules.json")
        tmp = p + f".tmp-{os.getpid()}"
        with open(tmp, "w") as f:
            json.dump(desc, f, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(tmp, p)
    return p


def _md(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def _names(defs, kinds, cap=12):
    xs = [d["name"] for d in defs if d["kind"] in kinds]
    seen = []
    for x in xs:
        if x not in seen:
            seen.append(x)
    if len(seen) > cap:
        return ", ".join(seen[:cap]) + f", ... ({len(seen)} in all)"
    return ", ".join(seen)


def report_md(descs, db_path):
    L = ["# Module descriptions and task-list order of AthenaK (K7, brief 12.7)", "",
         f"Generated by `kb code modules` (kbtool {__version__}) from the code index `{db_path}` and the sources at "
         "the indexed commits. Every description is text of the file's own comments (whitespace joined, licence "
         "banner and Doxygen markers removed), cut after its first sentences; nothing is added. Classes and "
         "functions are the definitions of the code index (tree-sitter), each with the first sentence of the "
         "comment directly above it in modules.json. The task-list order is extracted from the calls in the "
         "source (Driver::Execute, MeshBlockPack::AddPhysics, every AddTask and QueueTask with comments "
         "removed); `kb-data/build/code/<repo>/modules.json` holds everything below in full.", ""]
    for d in descs:
        L += [f"## {d['repo_id']} at {d['commit_sha'][:12]} ({(d['commit_date'] or '')[:10]})", "",
              f"Source: {d['source']}; paths below are relative to `{d['path_prefix']}`.", ""]
        L += _task_md(d)
        for mod in MODULE_DIRS:
            fs = [f for f in d["files"] if f["path"].startswith(mod + "/")]
            L += [f"### src/{mod}: {len(fs)} files, {sum(f['lines'] for f in fs)} lines", "",
                  "| file | lines | header comment (first sentences) | classes, structs, enums | functions and "
                  "methods |", "|---|---|---|---|---|"]
            for f in fs:
                h = f.get("header") or {}
                defs = f.get("definitions", [])
                nf = sum(1 for x in defs if x["kind"] in ("function", "method"))
                hd = _md(h.get("first_sentences")) or (f["note"] if f.get("note") else "(licence banner only)"
                                                       if h.get("banner_lines") else "(no header comment)")
                L.append(f"| {f['path']} | {f['lines']} | {hd} | "
                         f"{_md(_names(defs, ('class', 'struct', 'enum')))} | "
                         f"{nf}: {_md(_names(defs, ('function', 'method')))} |")
            L.append("")
    return "\n".join(L) + "\n"


def _task_md(d):
    drv = d["driver"]
    L = ["### Task lists", ""]
    if not drv.get("found"):
        L += ["Driver::Execute not found in src/driver/driver.cpp.", ""]
        return L
    L.append(f"Driver::Execute (`{DRIVER}`:{drv['line_start']}-{drv['line_end']}) runs, inside its loop over cycles:")
    L.append("")
    for c in drv["calls"]:
        L.append(f"- `{c['list']}` (stage argument {c['stage_arg']}), line {c['line']}: {c['when']}"
                 + (f"; inside {'; '.join('`' + x + '`' for x in c['loops'] if not x.startswith('while'))}"
                    if any(not x.startswith("while") for x in c["loops"]) else "")
                 + (f"; if {'; '.join('`' + x + '`' for x in c['conditions'])}" if c["conditions"] else ""))
    if drv.get("other_statements_in_stage_loop"):
        L.append("- other statements in the stage loop: "
                 + "; ".join(f"`{_md(x)}`" for x in drv["other_statements_in_stage_loop"]))
    L += ["", f"MeshBlockPack::AddPhysics (`{PACK}`) hands the task lists to the modules in this order:", ""]
    for k, c in enumerate(d["physics_assembly"]["calls"], 1):
        L.append(f"{k}. line {c['line']}: `{_md(c['call'])}`"
                 + (f" (inside `{_md(c['conditions'][-1])}`)" if c["conditions"] else ""))
    nm = d["nr_queue_map"]["map"]
    L += ["", "Numerical-relativity queues (`" + NUMREL + "`): "
          + ", ".join(f"{k} -> `{v}`" for k, v in sorted(nm.items())) + ".", "",
          "Order of the physics modules within one cycle: the lists in the order Driver::Execute runs them; "
          "within a list the modules in registration order (MeshBlockPack::AddPhysics), each with its task "
          "functions in registration order (repeated names once; `*` = mentions tmunu, see below; `opt.` = "
          "optional dependencies of a queued task). Conditions: the innermost condition around the calls; "
          "`after X returns` = the calls come after a block X of the same function that returns.", "",
          "| # | task list | runs | module | n | tasks | conditions |", "|---|---|---|---|---|---|---|"]
    for k, lst, when, mods in schedule(d):
        if k is None:
            L.append(f"| | `{lst}` | {when} | {', '.join(m for m, _ in mods)} | {sum(len(t) for _, t in mods)} | "
                     "(see modules.json) | |")
            continue
        for mod, ts in mods:
            names, conds = [], []
            for t in ts:
                nm = _short(t["task_function"]) + ("*" if t.get("tmunu") else "")
                opt = t.get("optional_dependencies") or []
                if opt:
                    nm += f" (opt. {', '.join(opt)})"
                if nm not in names:
                    names.append(nm)
                c = t["conditions"][-1] if t["conditions"] else None
                for r in t.get("after_returning_blocks") or []:
                    c = (c + "; " if c else "") + f"after {r} returns"
                if c and c not in conds:
                    conds.append(c)
            cc = "; ".join(f"`{_md(x)}`" for x in conds[:3]) + (f" (+{len(conds) - 3} more)" if len(conds) > 3 else "")
            L.append(f"| {k + 1} | `{lst}` | {when} | {mod} | {len(ts)} | {_md(', '.join(names))} | {cc} |")
    sw = source_writers(d)
    L += ["", "Tasks whose function, or a method of the same class it calls, mentions `tmunu` (the matter sources "
          "Z4c reads):", ""]
    for t in sw:
        L.append(f"- `{_short(t['task_function'])}` ({t['module']}, `{t['path']}`:{t['line']}): list "
                 f"`{t['task_list']}`, {t['when']}; tmunu {t['tmunu']}"
                 + (f"; inside `{_md(t['conditions'][-1])}`" if t["conditions"] else ""))
    if not sw:
        L.append("- none")
    L.append("")
    return L


def build(lay, repos=None, db=None, report=None, write=True, log=print):
    dbp = open_for_read(lay, db)
    con = connect_ro(dbp)
    descs = []
    try:
        for r in repos or list(REPOS):
            rid = ALIASES.get(r, r)
            if rid not in REPOS:
                raise SystemExit(f"kb code modules covers {', '.join(REPOS)} (aliases {', '.join(ALIASES)}), not {r}")
            d = describe_repo(lay, con, rid, log=log)
            d["database"] = os.path.realpath(dbp)
            if write:
                d["modules_json"] = write_build(lay, d)
            descs.append(d)
    finally:
        con.close()
    if report:
        os.makedirs(os.path.dirname(os.path.abspath(report)), exist_ok=True)
        with open(report, "w") as f:
            f.write(report_md(descs, os.path.basename(os.path.realpath(dbp))))
    return descs
