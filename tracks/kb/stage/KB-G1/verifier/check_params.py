"""Test K of the KB-G1 verifier: the parameter index of this repository's AthenaK.

Usage: python3 check_params.py <outdir>
(1) Ten rows of `params` (repo local/nrpic), seed 20261119: the recorded line of the file at
    the indexed commit must hold a parameter-reading call with the recorded block, name,
    type and default; the same call is looked up on today's `main`.
(2) Recall on every file under athenak/src/particles/ and athenak/src/pgen/nrpic/ at the
    indexed commit: each call with literal block and name has a row with that line.
Writes <outdir>/params.json and prints a table. Reads git objects only (git show, ls-tree).
"""
import json
import os
import random
import re
import sqlite3
import subprocess
import sys

ROOT = "/data/haiyangw/nrpic/kb-data"
DB = os.path.join(ROOT, "db", "current")
GIT = "/data/haiyangw/nrpic/wt/kb"
SEED = 20261119

CALL = re.compile(
    r"(?:->|\.)\s*(GetOrAdd|Get)(Real|Integer|Boolean|String)\s*\(\s*"
    r"(\"[^\"]*\"|[^,()]+?)\s*,\s*(\"[^\"]*\"|[^,()]+?)\s*"
    r"(?:,\s*((?:[^()]|\((?:[^()]|\([^()]*\))*\))*?))?\s*\)",
    re.S)


def git_show(rev, path):
    r = subprocess.run(["git", "-C", GIT, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def blank_comments(text):
    """Blank C++ comments, keeping newlines (string literals with // are rare here)."""
    def rep(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    return re.sub(r"//[^\n]*|/\*.*?\*/", rep, text, flags=re.S)


def calls(text):
    res = []
    text = blank_comments(text)
    for m in CALL.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        blk, name = m.group(3).strip(), m.group(4).strip()
        res.append({
            "line": line, "kind": m.group(1), "type": m.group(2),
            "block": blk[1:-1] if re.fullmatch(r'"[^"]*"', blk) else None, "block_expr": blk,
            "name": name[1:-1] if re.fullmatch(r'"[^"]*"', name) else None, "name_expr": name,
            "default": (m.group(5) or "").strip() or None,
        })
    return res


def key_of(lit, expr):
    """Block or name as the knowledge base writes it: the literal, or {expression}."""
    return lit if lit is not None else "{" + re.sub(r"\s+", "", expr) + "}"


def norm_kb(v):
    return v if v is None or not v.startswith("{") else "{" + re.sub(r"\s+", "", v[1:-1]) + "}"


def norm_default(v):
    if v is None:
        return None
    v = v.strip()
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return v


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    sha = c.execute("select commit_sha from repos where repo_id='local/nrpic'").fetchone()[0]
    main_sha = subprocess.run(["git", "-C", GIT, "rev-parse", "main"], capture_output=True,
                              text=True).stdout.strip()
    rows = c.execute("select p.param_id, p.block, p.name, p.type, p.default_value, f.path, p.line "
                     "from params p join code_files f using(file_id) where p.repo_id='local/nrpic' "
                     "order by p.param_id").fetchall()
    pick = sorted(random.Random(SEED).sample(rows, 10))
    sample = []
    for (pid, blk, name, typ, dflt, path, line) in pick:
        text = git_show(sha, path)
        cs = calls(text) if text else []
        at = [x for x in cs if x["line"] == line]
        hit = [x for x in at if key_of(x["name"], x["name_expr"]) == norm_kb(name)]
        ok_line = bool(hit)
        h = hit[0] if hit else None
        ok_block = bool(h) and key_of(h["block"], h["block_expr"]) == norm_kb(blk)
        ok_type = bool(h) and h["type"] == typ
        ok_default = bool(h) and norm_default(h["default"]) == norm_default(dflt)
        now = git_show(main_sha, path)
        now_lines = [x["line"] for x in calls(now)
                     if key_of(x["name"], x["name_expr"]) == norm_kb(name)
                     and key_of(x["block"], x["block_expr"]) == norm_kb(blk)] if now else []
        src_line = text.split("\n")[line - 1].strip() if text and 0 < line <= text.count("\n") + 1 else None
        sample.append({"param_id": pid, "block": blk, "name": name, "type": typ, "default": dflt,
                       "path": path, "line": line, "source_line": src_line, "found": h,
                       "ok_line": ok_line, "ok_block": ok_block, "ok_type": ok_type,
                       "ok_default": ok_default, "main_lines": now_lines})
    # recall on the NRPIC files
    ls = subprocess.run(["git", "-C", GIT, "ls-tree", "-r", "--name-only", sha, "--",
                         "athenak/src/particles", "athenak/src/pgen/nrpic"],
                        capture_output=True, text=True).stdout.split()
    recall = []
    for path in ls:
        if not path.endswith((".cpp", ".hpp")):
            continue
        text = git_show(sha, path)
        cs = calls(text)
        kb = c.execute("select p.block, p.name, p.line, p.type, p.default_value from params p "
                       "join code_files f using(file_id) where p.repo_id='local/nrpic' and f.path=?",
                       (path,)).fetchall()
        kbset = {(norm_kb(b), norm_kb(n), l) for (b, n, l, _, _) in kb}
        lit = [x for x in cs if x["block"] is not None and x["name"] is not None]
        nonlit = [x for x in cs if x["block"] is None or x["name"] is None]
        mine = {(key_of(x["block"], x["block_expr"]), key_of(x["name"], x["name_expr"]), x["line"]): x
                for x in cs}
        missed = [x for k, x in mine.items() if k not in kbset]
        extra = [k for k in kbset if k not in mine]
        # type and default of every matched call
        kbfull = {(norm_kb(b), norm_kb(n), l): (t, d) for (b, n, l, t, d) in kb}
        mism = [(k, kbfull[k], (x["type"], x["default"])) for k, x in mine.items() if k in kbfull and
                (kbfull[k][0] != x["type"] or norm_default(kbfull[k][1]) != norm_default(x["default"]))]
        if cs or kb:
            recall.append({"path": path, "calls": len(cs), "literal": len(lit), "nonliteral": len(nonlit),
                           "kb_rows": len(kb), "missed": missed, "extra": extra, "type_default_mismatch": mism,
                           "nonliteral_calls": nonlit})
    # (3) staleness: (block, name) pairs read on today's main under athenak/src that the
    # index (taken at the indexed commit) does not have
    kb_pairs = {(norm_kb(b), norm_kb(n)) for (b, n) in c.execute(
        "select block, name from params where repo_id='local/nrpic'").fetchall()}
    ls_main = subprocess.run(["git", "-C", GIT, "ls-tree", "-r", "--name-only", main_sha, "--",
                              "athenak/src"], capture_output=True, text=True).stdout.split()
    new_pairs = {}
    n_main_calls = 0
    for path in ls_main:
        if not path.endswith((".cpp", ".hpp")):
            continue
        text = git_show(main_sha, path)
        if not text or "Get" not in text:
            continue
        for x in calls(text):
            n_main_calls += 1
            k = (key_of(x["block"], x["block_expr"]), key_of(x["name"], x["name_expr"]))
            if k not in kb_pairs:
                new_pairs.setdefault(path, []).append((k[0], k[1], x["line"]))
    stale = {"main_calls": n_main_calls, "files_with_new": len(new_pairs),
             "new_pairs": sum(len(v) for v in new_pairs.values()), "by_file": new_pairs}
    res = {"seed": SEED, "db": os.path.realpath(DB), "indexed_commit": sha, "main": main_sha,
           "population": len(rows), "sample": sample, "recall": recall, "stale": stale}
    with open(os.path.join(out, "params.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(f"indexed commit {sha[:12]}, main {main_sha[:12]}, population {len(rows)}")
    for s in sample:
        print(f"{s['param_id']:6d} {s['block']:>14s}/{s['name']:<28s} {s['type']:8s} {str(s['default']):>12s} "
              f"{s['path']}:{s['line']}  line={int(s['ok_line'])} block={int(s['ok_block'])} "
              f"type={int(s['ok_type'])} default={int(s['ok_default'])} main_lines={s['main_lines']}")
    tl = sum(r["literal"] for r in recall)
    tm = sum(len(r["missed"]) for r in recall)
    te = sum(len(r["extra"]) for r in recall)
    tn = sum(r["nonliteral"] for r in recall)
    tc = sum(r["calls"] for r in recall)
    tx = sum(len(r["type_default_mismatch"]) for r in recall)
    print(f"recall: {len(recall)} files, {tc} calls ({tl} literal, {tn} non-literal), {tm} missed, "
          f"{te} extra rows, {tx} type/default mismatches")
    print(f"staleness: {n_main_calls} calls on main; {stale['new_pairs']} (block, name) pairs in "
          f"{len(new_pairs)} files are not in the index")
    for pth, v in sorted(new_pairs.items(), key=lambda kv: -len(kv[1]))[:15]:
        print(f"   {len(v):4d} {pth}  e.g. {v[:3]}")
    for r in recall:
        if r["missed"] or r["extra"] or r["type_default_mismatch"]:
            print("  ", r["path"], "missed", [(x["block"], x["name"], x["line"]) for x in r["missed"]][:8],
                  "extra", r["extra"][:8], "mismatch", r["type_default_mismatch"][:4])


if __name__ == "__main__":
    main()
