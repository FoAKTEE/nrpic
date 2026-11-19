"""Run-parameter index (brief 12.7): every input-file parameter that C++ code reads through
the ParameterInput interface of AthenaK (and of Athena++ and Parthenon, which share it):

    pin->Get{Real,Integer,Boolean,String}(block, name)                 required parameter
    pin->GetOrAdd{Real,Integer,Boolean,String}(block, name, default)   optional, with default
    pin->Set{...}(block, name, value)                                  written by the code (not read)
    pin->DoesParameterExist(block, name), pin->DoesBlockExist(block)   existence checks

The parser is the standard library only: comments and the contents of string literals are
masked (same length, newlines kept, so offsets and lines stay exact), calls are found in the
masked text, their argument lists are split at top-level commas, and each argument is taken
from the original text. A block or name that is not a string literal is kept as the
expression the code uses (for example `op.block_name`) with `block_literal = False`.

Also: the parser of AthenaK input files (`<block>` lines, `name = value  # comment`), and
the comparison of the parameters set in input files with the parameters the code reads.
Nothing here executes or compiles the files it reads.
"""
import re

TYPES = ("Real", "Integer", "Boolean", "String")
CALL_RE = re.compile(r"(?P<recv>[A-Za-z_][\w\.\->\[\]\(\)]*?)?\s*(?P<arrow>->|\.)\s*"
                     r"(?P<method>(?:GetOrAdd|Get|Set)(?:Real|Integer|Boolean|String)|DoesParameterExist|DoesBlockExist)"
                     r"\s*\(")
STRING_LIT = re.compile(r'^"((?:[^"\\\n]|\\.)*)"$', re.S)


def mask_cpp(src):
    """Return src with comments and the contents of string and character literals replaced
    by spaces (newlines kept). Quotes stay, so a literal is still visible as `"   "`."""
    out = list(src)
    n = len(src)
    i = 0

    def blank(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif c == "/" and i + 1 < n and src[i + 1] == "*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(i, j)
            i = j
        elif c == '"':
            if i > 0 and src[i - 1] == "R" and (i < 2 or not (src[i - 2].isalnum() or src[i - 2] == "_")):
                k = src.find("(", i + 1)
                delim = src[i + 1:k] if 0 <= k - i - 1 <= 16 else None
                if delim is not None and '"' not in delim and "\n" not in delim:
                    end = src.find(")" + delim + '"', k + 1)
                    end = n - 1 if end < 0 else end + len(delim) + 1
                    blank(i + 1, end)
                    i = end + 1
                    continue
            j = i + 1
            while j < n and src[j] != '"' and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
            j = min(j, n)
            blank(i + 1, j)
            i = j + 1
        elif c == "'":
            if i > 0 and (src[i - 1].isdigit() or (src[i - 1] in "abcdefABCDEF" and _in_number(src, i))):
                i += 1                                # C++14 digit separator 1'000'000
                continue
            j = i + 1
            while j < n and src[j] != "'" and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
            j = min(j, n)
            blank(i + 1, j)
            i = j + 1
        else:
            i += 1
    return "".join(out)


def _in_number(src, i):
    k = i - 1
    while k >= 0 and (src[k].isalnum() or src[k] in "'."):
        k -= 1
    tok = src[k + 1:i]
    return bool(re.match(r"^0[xX]", tok))


def split_args(src, masked, open_pos):
    """Arguments of the call whose '(' is at open_pos: list of (start, end) spans in src,
    and the position of the closing ')'. Brackets are counted in the masked text."""
    depth = 0
    spans = []
    start = open_pos + 1
    i = open_pos
    n = len(masked)
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack = []
    while i < n:
        c = masked[i]
        if c in pairs:
            stack.append(pairs[c])
            depth += 1
        elif c in ")]}":
            if not stack:
                return None, None
            want = stack.pop()
            depth -= 1
            if c != want:
                return None, None
            if depth == 0:
                if src[start:i].strip() or spans:
                    spans.append((start, i))
                return spans, i
        elif c == "," and depth == 1:
            spans.append((start, i))
            start = i + 1
        i += 1
    return None, None


def literal(text):
    m = STRING_LIT.match(text.strip())
    if not m:
        return None
    return bytes(m.group(1), "utf-8").decode("unicode_escape") if "\\" in m.group(1) else m.group(1)


def norm_expr(text):
    return re.sub(r"\s+", " ", text.strip())


def line_starts(src):
    starts = [0]
    for m in re.finditer("\n", src):
        starts.append(m.end())
    return starts


def line_of(starts, pos):
    import bisect
    return bisect.bisect_right(starts, pos)


def extract_calls(src, path=None):
    """All ParameterInput calls of one C/C++ source text, in order. Each a dict:
    method, access (get|get_or_add|set|exists|block_exists), type, block, block_literal,
    name, name_literal, default, line, end_line, receiver, args_ok."""
    masked = mask_cpp(src)
    starts = line_starts(src)
    out = []
    for m in CALL_RE.finditer(masked):
        method = m.group("method")
        open_pos = m.end() - 1
        spans, close = split_args(src, masked, open_pos)
        rec = {"method": method, "line": line_of(starts, m.start("method")), "receiver": None, "args_ok": True}
        recv = (m.group("recv") or "").strip()
        rec["receiver"] = recv[-60:] if recv else None
        if method.startswith("GetOrAdd"):
            rec["access"], rec["type"] = "get_or_add", method[len("GetOrAdd"):]
        elif method.startswith("Get"):
            rec["access"], rec["type"] = "get", method[3:]
        elif method.startswith("Set"):
            rec["access"], rec["type"] = "set", method[3:]
        elif method == "DoesParameterExist":
            rec["access"], rec["type"] = "exists", None
        else:
            rec["access"], rec["type"] = "block_exists", None
        if spans is None:
            rec["args_ok"] = False
            rec.update({"block": None, "block_literal": False, "name": None, "name_literal": False,
                        "default": None, "end_line": rec["line"]})
            out.append(rec)
            continue
        args = [src[a:b] for a, b in spans]
        rec["end_line"] = line_of(starts, close)
        need = {"get": 2, "get_or_add": 3, "set": 3, "exists": 2, "block_exists": 1}[rec["access"]]
        if len(args) != need:
            rec["args_ok"] = False
        blk = args[0] if args else ""
        lit = literal(blk)
        rec["block"] = lit if lit is not None else norm_expr(blk)
        rec["block_literal"] = lit is not None
        if rec["access"] == "block_exists":
            rec.update({"name": None, "name_literal": False, "default": None})
        else:
            nm = args[1] if len(args) > 1 else ""
            litn = literal(nm)
            rec["name"] = litn if litn is not None else norm_expr(nm)
            rec["name_literal"] = litn is not None
            rec["default"] = norm_expr(args[2]) if len(args) > 2 and rec["access"] in ("get_or_add", "set") else None
        out.append(rec)
    return out


# ---------------------------------------------------------------- input files
BLOCK_RE = re.compile(r"^\s*<\s*([^<>\s]+)\s*>")
PARAM_RE = re.compile(r"^\s*([A-Za-z_][\w\-\.]*)\s*=\s*(.*?)\s*$")


def parse_athinput(text):
    """[(line, block, name, value)] of an AthenaK input file. Comments start with '#'."""
    out = []
    block = None
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        m = BLOCK_RE.match(line)
        if m:
            block = m.group(1)
            continue
        m = PARAM_RE.match(line)
        if m and block is not None:
            out.append((i, block, m.group(1), m.group(2)))
    return out


def is_athinput(path):
    base = path.rsplit("/", 1)[-1]
    return base.startswith("athinput") or base.endswith(".athinput")


def name_pattern(expr):
    """Regex for a parameter name the code builds at run time, from the string literals of
    the expression in order: `"co_" + nstr + "_type"` -> ^co_.*_type$, `pre + "x1"` ->
    ^.*x1$. None when the expression has no literal (a plain variable)."""
    lits = re.findall(r'"((?:[^"\\\n]|\\.)*)"', expr or "")
    if not lits:
        return None
    e = expr.strip()
    body = ".*".join(re.escape(x) for x in lits)
    return re.compile(("^" if e.startswith('"') else "^.*") + body + ("$" if e.endswith('"') else ".*$"))


def compare_inputs(input_params, code_params):
    """Match parameters set in input files against parameters read by the code.

    input_params: [(file, line, block, name, value)]
    code_params:  [dict(block, block_literal, name, name_literal, access)] (reads only)
    Returns rows with status:
      literal     the code reads (block, name) with both as string literals
      computed    the code reads `name` (literal) with a block computed at run time
                  (for example the numbered <outputN> blocks)
      pattern     the code builds the name at run time and the name fits the literals of that
                  expression (weaker evidence: `pre + "x1"` fits any name ending in x1)
      other_block the name is read, but only under another literal block
      comment_block  the <comment> block (documentation only)
      unmatched   no read of this name in the indexed code
    """
    lit = {(p["block"], p["name"]) for p in code_params if p["block_literal"] and p["name_literal"]}
    by_name = {p["name"] for p in code_params if p["name_literal"]}
    comp = {p["name"] for p in code_params if p["name_literal"] and not p["block_literal"]}
    pats = []                                          # (block or None if computed, regex)
    for p in code_params:
        if not p["name_literal"]:
            rx = name_pattern(p["name"])
            if rx is not None:
                pats.append((p["block"] if p["block_literal"] else None, rx))
    rows = []
    for f, line, block, name, value in input_params:
        if (block, name) in lit:
            st = "literal"
        elif name in comp:
            st = "computed"
        elif any((b is None or b == block) and rx.match(name) for b, rx in pats):
            st = "pattern"                             # the name is built at run time and fits the pattern
        elif name in by_name:
            st = "other_block"                         # the name is read, but under another literal block
        elif block == "comment":
            st = "comment_block"                       # AthenaK's documentation block, not read by any code
        else:
            st = "unmatched"
        rows.append({"file": f, "line": line, "block": block, "name": name, "value": value, "status": st})
    return rows
