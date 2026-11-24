"""Item 4: ten parameter reads of the code index (repo local/nrpic) and ten curated paper-code
links, drawn with the seed and printed next to the source at the indexed commit.

python3 -I draw_code.py --seed SEED --links kb/curated/paper_code_links.tsv --out DIR
Writes DIR/params_draw.tsv, DIR/links_draw.tsv and DIR/code_view.txt (the source lines to
read by hand). Git objects are read with `git show <commit>:<path>`; nothing is checked out.
"""
import argparse
import csv
import json
import os
import random
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcommon as vc  # noqa: E402


def git_file(commit, path):
    r = subprocess.run(["git", "-C", vc.REPO, "show", "%s:%s" % (commit, path)],
                       capture_output=True, text=True, errors="replace")
    return r.stdout.split("\n") if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--links", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = random.Random(a.seed)
    c = vc.connect()
    commit = c.execute("select commit_sha from repos where repo_id='local/nrpic'").fetchone()[0]
    view = open(os.path.join(a.out, "code_view.txt"), "w")
    view.write("indexed commit of local/nrpic: %s\n" % commit)
    rows = c.execute("select p.param_id, p.block, p.name, p.type, p.default_value, f.path, p.line"
                     " from params p join code_files f using(file_id) where p.repo_id='local/nrpic'"
                     " order by p.param_id").fetchall()
    pick = sorted(rng.sample(rows, 10))
    with open(os.path.join(a.out, "params_draw.tsv"), "w") as f:
        f.write("param_id\tblock\tname\ttype\tdefault\tpath\tline\tsource_line\n")
        for pid, blk, nm, ty, de, path, line in pick:
            src = git_file(commit, path)
            sl = src[line - 1].strip() if src and 0 < line <= len(src) else "<no line>"
            f.write("\t".join(str(x) for x in (pid, blk, nm, ty, de, path, line, sl)) + "\n")
            view.write("\n=== param %d  <%s> %s  type %s  default %r  %s:%d\n" % (pid, blk, nm, ty, de, path, line))
            if src:
                for i in range(max(1, line - 3), min(len(src), line + 3) + 1):
                    view.write("%s%5d| %s\n" % (">" if i == line else " ", i, src[i - 1][:200]))
    with open(a.links) as fh:
        lines = [l for l in fh if not l.startswith("#")]
    links = list(csv.DictReader(lines, delimiter="\t"))
    lpick = sorted(rng.sample(links, 10), key=lambda r: r["link_key"])
    paper = vc.source_lines("2611.12831", "v1", "main.tex")
    db = {}
    for lid, ev, st, sym in c.execute("select link_id, evidence, status, sym_id from impl_links"):
        e = json.loads(ev)
        db[e.get("link_key")] = (st, sym, e)
    with open(os.path.join(a.out, "links_draw.tsv"), "w") as f:
        f.write("link_key\tlines\tstatement\tsymbol\tpath\tstatus_tsv\tstatus_db\tsymbol_lines_db\n")
        for r in lpick:
            st, sym, e = db.get(r["link_key"], (None, None, {}))
            f.write("\t".join([r["link_key"], r["lines"], r["statement"], r["symbol"], r["path"], r["status"],
                               str(st), str(e.get("symbol_lines"))]) + "\n")
            view.write("\n=== link %s  status tsv %s db %s  %s  %s\n    statement: %s\n    params: %s\n    evidence: %s\n"
                       % (r["link_key"], r["status"], st, r["symbol"], r["path"], r["statement"], r["params"], r["evidence"][:900]))
            for part in r["lines"].split(","):
                m = re.match(r"L(\d+)(?:-(\d+))?", part.strip())
                if m and paper:
                    a0, b0 = int(m.group(1)), int(m.group(2) or m.group(1))
                    view.write("  -- paper main.tex L%d-%d\n" % (a0, b0))
                    for i in range(a0, min(b0, a0 + 25) + 1):
                        view.write("  %5d| %s\n" % (i, paper[i - 1][:220]))
            src = git_file(commit, r["path"])
            sl = e.get("symbol_lines")
            if src and sl:
                s0, s1 = sl
                view.write("  -- code %s L%d-%d at %s\n" % (r["path"], s0, s1, commit[:8]))
                for i in range(s0, min(s1, s0 + 60) + 1):
                    view.write("  %5d| %s\n" % (i, src[i - 1][:200]))
            elif src:
                hits = [i + 1 for i, l in enumerate(src) if r["symbol"].split("::")[-1] in l]
                view.write("  -- code %s: symbol name on lines %s\n" % (r["path"], hits[:10]))
            else:
                view.write("  -- code %s: NOT FOUND at %s\n" % (r["path"], commit[:8]))
    view.close()


if __name__ == "__main__":
    main()
