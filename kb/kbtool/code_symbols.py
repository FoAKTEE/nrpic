"""Symbols of source files (brief 12.7): C and C++ (also CUDA and headers) with tree-sitter,
Python with the standard-library `ast` module, Fortran with line patterns. Parsing only:
no file is executed, compiled or imported.

Each symbol: name, qualname, kind, signature, line_start, line_end, doc (the comment block
right above it, or the Python docstring), body (True when the symbol has a body).
Kinds: namespace, class, struct, union, enum, function, method, prototype, macro (C/C++);
class, function, method (Python); module, program, subroutine, function (Fortran).

tree-sitter comes from the tool environment kb/.venv (packages tree-sitter,
tree-sitter-cpp); without it C/C++ files get no symbols and the caller records why.
"""
import ast
import re

# Attribute-like macros of Kokkos, CUDA and AMReX that a parser without the preprocessor
# cannot read; each is replaced by spaces of the same length (KOKKOS_LAMBDA by "[=]"), so
# byte offsets and lines do not move.
MACROS = ["KOKKOS_FORCEINLINE_FUNCTION", "KOKKOS_INLINE_FUNCTION", "KOKKOS_FUNCTION", "KOKKOS_LAMBDA",
          "KOKKOS_CLASS_LAMBDA", "__forceinline__", "__host__", "__device__", "__global__",
          "AMREX_GPU_HOST_DEVICE", "AMREX_GPU_DEVICE", "AMREX_GPU_HOST", "AMREX_FORCE_INLINE",
          "AMREX_INLINE", "AMREX_GPU_GLOBAL"]
MACRO_RE = re.compile(r"\b(" + "|".join(re.escape(m) for m in MACROS) + r")\b")

_TS = {}


def tree_sitter_available():
    try:
        _cpp_parser()
        return True
    except Exception:
        return False


def tree_sitter_versions():
    out = {}
    try:
        from importlib.metadata import version
        for p in ("tree-sitter", "tree-sitter-cpp"):
            out[p] = version(p)
    except Exception:
        pass
    return out


def _cpp_parser():
    if "cpp" not in _TS:
        import tree_sitter_cpp
        from tree_sitter import Language, Parser
        _TS["cpp"] = Parser(Language(tree_sitter_cpp.language()))
    return _TS["cpp"]


def neutralize_macros(text):
    def rep(m):
        s = m.group(1)
        return ("[=]" + " " * (len(s) - 3)) if s.endswith("LAMBDA") else " " * len(s)
    return MACRO_RE.sub(rep, text)


def _txt(src, node):
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _declarator_name(src, decl):
    """Name text of a (function) declarator, unwrapping pointers and references."""
    d = decl
    for _ in range(8):
        if d is None:
            return None
        if d.type in ("function_declarator", "pointer_declarator", "reference_declarator",
                      "parenthesized_declarator", "attributed_declarator"):
            inner = d.child_by_field_name("declarator")
            if inner is None:
                inner = next((c for c in d.named_children if c.type.endswith("declarator") or
                              c.type in ("identifier", "qualified_identifier", "field_identifier")), None)
            d = inner
            continue
        if d.type in ("identifier", "field_identifier", "qualified_identifier", "destructor_name",
                      "operator_name", "template_function", "type_identifier", "operator_cast"):
            return re.sub(r"\s+", "", _txt(src, d))
        return None
    return None


def _find_function_declarator(decl):
    d = decl
    for _ in range(8):
        if d is None:
            return None
        if d.type == "function_declarator":
            return d
        d = d.child_by_field_name("declarator")
    return None


def _doc_above(src_lines, line_start, comment_lines):
    """The comment block that ends on the line right above line_start (1-based)."""
    k = line_start - 1
    block = []
    while k >= 1 and k in comment_lines and len(block) < 30:
        block.append(k)
        k -= 1
    if not block:
        return None
    lo, hi = min(block), max(block)
    text = "\n".join(src_lines[i - 1] for i in range(lo, hi + 1)).strip()
    return text[:1500] if text else None


def cpp_symbols(text):
    """Symbols of a C/C++ source text with tree-sitter. Returns (symbols, n_error_nodes)."""
    parser = _cpp_parser()
    src = neutralize_macros(text).encode("utf-8", errors="replace")
    tree = parser.parse(src)
    lines = text.splitlines()
    comment_lines = set()
    syms = []
    n_err = 0

    # first pass: lines that hold only comments (for doc blocks)
    stack = [tree.root_node]
    while stack:
        nd = stack.pop()
        if nd.type == "ERROR":
            n_err += 1
        if nd.type == "comment":
            for ln in range(nd.start_point[0] + 1, nd.end_point[0] + 2):
                lt = lines[ln - 1].strip() if ln - 1 < len(lines) else ""
                if lt.startswith(("//", "/*", "*")) or nd.start_point[0] + 1 < ln:
                    comment_lines.add(ln)
        stack.extend(nd.children)

    def add(kind, name, scope, node, sig_end=None, body=False):
        if not name:
            return
        q = "::".join(scope + [name]) if scope else name
        ls, le = node.start_point[0] + 1, node.end_point[0] + 1
        sig = src[node.start_byte:(sig_end if sig_end is not None else node.end_byte)].decode("utf-8", "replace")
        sig = re.sub(r"\s+", " ", sig).strip()[:400]
        syms.append({"name": name.split("::")[-1], "qualname": q, "kind": kind, "signature": sig,
                     "line_start": ls, "line_end": le, "doc": _doc_above(lines, ls, comment_lines), "body": body})

    def walk(node, scope, in_class):
        for ch in node.named_children:
            t = ch.type
            if t == "namespace_definition":
                nm = ch.child_by_field_name("name")
                nmt = re.sub(r"\s+", "", _txt(src, nm)) if nm is not None else "(anonymous)"
                body = ch.child_by_field_name("body")
                add("namespace", nmt, scope, ch, sig_end=body.start_byte if body is not None else None, body=True)
                if body is not None:
                    walk(body, scope + [nmt], False)
            elif t in ("class_specifier", "struct_specifier", "union_specifier", "enum_specifier"):
                nm = ch.child_by_field_name("name")
                body = ch.child_by_field_name("body")
                if nm is not None and body is not None:
                    nmt = re.sub(r"\s+", "", _txt(src, nm))
                    kind = {"class_specifier": "class", "struct_specifier": "struct",
                            "union_specifier": "union", "enum_specifier": "enum"}[t]
                    add(kind, nmt, scope, ch, sig_end=body.start_byte, body=True)
                    if kind != "enum":
                        walk(body, scope + [nmt.split("<")[0]], True)
            elif t == "function_definition":
                decl = ch.child_by_field_name("declarator")
                nm = _declarator_name(src, decl)
                body = ch.child_by_field_name("body")
                kind = "method" if (in_class or (nm and "::" in nm)) else "function"
                add(kind, nm, scope, ch, sig_end=body.start_byte if body is not None else None, body=True)
            elif t in ("declaration", "field_declaration"):
                decl = ch.child_by_field_name("declarator")
                fd = _find_function_declarator(decl)
                if fd is not None:
                    add("prototype", _declarator_name(src, fd), scope, ch)
                # classes defined inside a declaration (struct X {...} x;)
                ty = ch.child_by_field_name("type")
                if ty is not None and ty.type in ("class_specifier", "struct_specifier", "union_specifier",
                                                  "enum_specifier"):
                    walk_type(ty, scope)
            elif t in ("template_declaration", "linkage_specification", "declaration_list",
                       "field_declaration_list", "preproc_if", "preproc_ifdef", "preproc_else",
                       "preproc_elif", "access_specifier", "export_declaration"):
                walk(ch, scope, in_class)
            elif t in ("preproc_def", "preproc_function_def"):
                nm = ch.child_by_field_name("name")
                if nm is not None:
                    add("macro", _txt(src, nm), [], ch, sig_end=None)
                    syms[-1]["signature"] = syms[-1]["signature"][:200]

    def walk_type(ty, scope):
        fake = type("N", (), {})()
        fake.named_children = [ty]
        walk(fake, scope, False)

    walk(tree.root_node, [], False)
    return syms, n_err


def python_symbols(text):
    """Symbols of a Python source text with ast (parsing only). Returns (symbols, error)."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError, MemoryError) as e:
        return [], f"{type(e).__name__}: {str(e)[:120]}"
    syms = []

    def walk(node, scope, in_class):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    args = ast.unparse(ch.args)
                except Exception:
                    args = "..."
                kind = "method" if in_class else "function"
                q = ".".join(scope + [ch.name])
                start = min([ch.lineno] + [d.lineno for d in ch.decorator_list])
                syms.append({"name": ch.name, "qualname": q, "kind": kind,
                             "signature": f"{'async ' if isinstance(ch, ast.AsyncFunctionDef) else ''}def {ch.name}({args})"[:400],
                             "line_start": start, "line_end": ch.end_lineno,
                             "doc": (ast.get_docstring(ch) or None) and ast.get_docstring(ch)[:1500], "body": True})
                walk(ch, scope + [ch.name], False)
            elif isinstance(ch, ast.ClassDef):
                q = ".".join(scope + [ch.name])
                try:
                    bases = ", ".join(ast.unparse(b) for b in ch.bases)
                except Exception:
                    bases = ""
                start = min([ch.lineno] + [d.lineno for d in ch.decorator_list])
                syms.append({"name": ch.name, "qualname": q, "kind": "class",
                             "signature": f"class {ch.name}({bases})"[:400], "line_start": start,
                             "line_end": ch.end_lineno,
                             "doc": (ast.get_docstring(ch) or None) and ast.get_docstring(ch)[:1500], "body": True})
                walk(ch, scope + [ch.name], True)
            elif isinstance(ch, (ast.If, ast.Try, ast.With)):
                walk(ch, scope, in_class)

    walk(tree, [], False)
    return syms, None


F_START = re.compile(
    r"^\s*(?:(?:pure|elemental|recursive|impure|module)\s+)*"
    r"(?:(?:integer|real|logical|complex|double\s+precision|character|type\s*\(\s*\w+\s*\)|class\s*\(\s*\w+\s*\))"
    r"(?:\s*\*\s*\d+|\s*\([^)]*\))?\s+)?"
    r"(?P<kind>subroutine|function)\s+(?P<name>\w+)", re.I)
F_MOD = re.compile(r"^\s*(?P<kind>module|program|submodule\s*\([^)]*\))\s+(?P<name>\w+)\s*(?:!.*)?$", re.I)
F_END = re.compile(r"^\s*end\s*(?P<kind>subroutine|function|module|program|submodule)?\b(?:\s+(?P<name>\w+))?", re.I)


def fortran_symbols(text, fixed_form=False):
    syms = []
    stack = []
    lines = text.splitlines()
    for i, raw in enumerate(lines, 1):
        if fixed_form and raw[:1] in ("c", "C", "*", "!"):
            continue
        line = raw.split("!", 1)[0]
        if not line.strip():
            continue
        m = F_START.match(line)
        if m and not re.match(r"^\s*end\b", line, re.I):
            stack.append({"name": m.group("name"), "kind": m.group("kind").lower(), "line_start": i,
                          "signature": re.sub(r"\s+", " ", line.strip())[:400]})
            continue
        m = F_MOD.match(line)
        if m and not re.match(r"^\s*module\s+procedure\b", line, re.I):
            kind = "module" if m.group("kind").lower().startswith(("module", "submodule")) else "program"
            stack.append({"name": m.group("name"), "kind": kind, "line_start": i,
                          "signature": re.sub(r"\s+", " ", line.strip())[:400]})
            continue
        m = F_END.match(line)
        if m and stack and (m.group("kind") or re.match(r"^\s*end\s*$", line, re.I)):
            s = stack.pop()
            s["line_end"] = i
            s["qualname"] = "::".join([x["name"] for x in stack] + [s["name"]])
            s["doc"] = None
            s["body"] = True
            syms.append(s)
    for s in stack:                                    # unterminated: keep the start line
        s.update({"line_end": None, "qualname": s["name"], "doc": None, "body": True})
        syms.append(s)
    return sorted(syms, key=lambda s: s["line_start"])
