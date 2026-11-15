#!/usr/bin/env python3
"""Independent checks of the code index (predictions P2, P3 in kb/JOURNAL.md).

P2 parameters: the index's parser (kbtool.code_params, standard library, masked text) and a
   second extractor written here on the tree-sitter syntax tree (call_expression whose
   function is a field_expression naming a ParameterInput method) must find the same set of
   (path, line, method, block, name).
P3 symbols: AthenaK defines methods out of class at column 0 ("void Z4c::Foo(" ...). A
   line pattern written here finds those definitions in .cpp files; the tree-sitter symbols
   of the index (kind method, line_start) must contain them.

    kb/.venv/bin/python -I kb/scripts/code_crosscheck.py OUTDIR --repo-dir DIR --name NAME
    kb/.venv/bin/python -I kb/scripts/code_crosscheck.py OUTDIR --this-ref main
Writes OUTDIR/crosscheck_<name>.json. Reads the sources as files or git objects only.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from kbtool import code_index as I        # noqa: E402
from kbtool import code_params as P       # noqa: E402
from kbtool import code_symbols as S      # noqa: E402
from kbtool.paths import layout           # noqa: E402

METHODS = re.compile(r"^(GetOrAdd|Get|Set)(Real|Integer|Boolean|String)$|^DoesParameterExist$|^DoesBlockExist$")
COL0_DEF = re.compile(r"^(?![ \t#/{}])(?:[A-Za-z_][\w:<>,\*&\s]*?[\s\*&])?(?P<cls>[A-Za-z_]\w*(?:<[^>]*>)?)::"
                      r"(?P<name>~?[A-Za-z_]\w*|operator\s*\S+)\s*\(")


def ts_calls(text):
    parser = S._cpp_parser()
    src = S.neutralize_macros(text).encode("utf-8", errors="replace")
    tree = parser.parse(src)
    out = set()
    stack = [tree.root_node]
    while stack:
        nd = stack.pop()
        stack.extend(nd.children)
        if nd.type != "call_expression":
            continue
        fn = nd.child_by_field_name("function")
        if fn is None or fn.type != "field_expression":
            continue
        fld = fn.child_by_field_name("field")
        if fld is None:
            continue
        name = src[fld.start_byte:fld.end_byte].decode()
        if not METHODS.match(name):
            continue
        args = nd.child_by_field_name("arguments")
        vals = []
        for a in (args.named_children if args is not None else []):
            if a.type == "comment":
                continue
            t = src[a.start_byte:a.end_byte].decode("utf-8", "replace")
            lit = P.literal(t) if a.type == "string_literal" else None
            vals.append(lit if lit is not None else "{" + re.sub(r"\s+", " ", t.strip()) + "}")
        blk = vals[0] if vals else None
        nm = vals[1] if len(vals) > 1 and name != "DoesBlockExist" else None
        out.add((fld.start_point[0] + 1, name, blk, nm))
    return out


def index_calls(text):
    out = set()
    for c in P.extract_calls(text):
        blk = c["block"] if c["block_literal"] else "{" + str(c["block"]) + "}"
        nm = None if c["access"] == "block_exists" else (c["name"] if c["name_literal"] else "{" + str(c["name"]) + "}")
        out.add((c["line"], c["method"], blk, nm))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--repo-dir")
    ap.add_argument("--name")
    ap.add_argument("--this-ref")
    a = ap.parse_args()
    if a.this_ref:
        files = I.iter_this(layout().home, a.this_ref)
        name = a.name or "local_nrpic"
    else:
        files = I.iter_checkout(a.repo_dir)
        name = a.name or os.path.basename(a.repo_dir.rstrip("/"))
    p_only_index, p_only_ts, p_both = [], [], 0
    m_pattern, m_found, m_missing = 0, 0, []
    n_cpp = 0
    for path, data, size in files:
        if I.language(path) not in ("cpp", "c", "cuda") or size > I.MAX_PARSE_BYTES:
            continue
        n_cpp += 1
        text = data.decode("utf-8", errors="replace")
        A, B = index_calls(text), ts_calls(text)
        p_both += len(A & B)
        p_only_index += [(path,) + x for x in sorted(A - B, key=str)]
        p_only_ts += [(path,) + x for x in sorted(B - A, key=str)]
        if path.endswith((".cpp", ".cc", ".cu")):
            syms, _ = S.cpp_symbols(text)
            starts = {s["line_start"] for s in syms if s["kind"] in ("method", "function")}
            # a definition may start one or two lines above the name (template<...>, return type on its own line)
            for i, line in enumerate(text.splitlines(), 1):
                if COL0_DEF.match(line) and not line.rstrip().endswith(";"):
                    m_pattern += 1
                    if starts & {i, i - 1, i - 2}:
                        m_found += 1
                    else:
                        m_missing.append((path, i, line.strip()[:120]))
    res = {"name": name, "cpp_files": n_cpp,
           "params": {"agree": p_both, "only_index": len(p_only_index), "only_tree_sitter": len(p_only_ts),
                      "examples_only_index": p_only_index[:30], "examples_only_tree_sitter": p_only_ts[:30]},
           "methods": {"pattern_definitions": m_pattern, "found_by_index": m_found,
                       "missing": len(m_missing), "examples_missing": m_missing[:40]}}
    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, f"crosscheck_{name}.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: (v if k in ("name", "cpp_files") else {kk: vv for kk, vv in v.items() if not kk.startswith("examples")})
                      for k, v in res.items()}))


if __name__ == "__main__":
    main()
