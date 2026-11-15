#!/usr/bin/env python3
"""Input options read by the source tree at a commit, for the release CHANGELOG.

Scans every athenak/src/**/*.cpp file at the given commits (git show, nothing checked
out) for calls pin->Get*/GetOrAdd*("block", "name", default) and prints, per block, the
options that differ between commits. Blocks matched with a variable (for example the
numbered horizon options of fastflow) are listed under '<variable>'.

    python3 options_at.py 338bcb1 7daed19 52c44eb [--json out.json]

338bcb1 is the vendored AthenaK c5a0d7f (the import commit); the later commits are the
proposed tags. Prints what each commit adds and removes relative to the one before.
"""
import argparse
import json
import re
import subprocess

CALL = re.compile(r'(?:pin|pinput|pin_)\s*->\s*(Get(?:OrAdd)?(?:Real|Integer|Boolean|String))'
                  r'\s*\(\s*("([^"]*)"|[A-Za-z_][\w.\->]*)\s*,\s*"([^"]+)"\s*(?:,\s*([^;]*?))?\)\s*;',
                  re.S)


def files_at(commit):
    out = subprocess.run(["git", "ls-tree", "-r", "--full-tree", "--name-only", commit, "--",
                          "athenak/src"],
                         check=True, capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith((".cpp", ".hpp"))]


def options_at(commit):
    opts = {}
    for f in files_at(commit):
        txt = subprocess.run(["git", "show", f"{commit}:{f}"], check=True, capture_output=True,
                             text=True, errors="replace").stdout
        for m in CALL.finditer(txt):
            kind, blk_raw, blk, name, default = m.groups()
            block = blk if blk is not None else f"<{blk_raw}>"
            key = (block, name)
            d = None if default is None else " ".join(default.split())
            opts.setdefault(key, set()).add((kind, d, f))
    return opts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("commits", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args()
    res = {c: options_at(c) for c in a.commits}
    report = {}
    for prev, cur in zip(a.commits[:-1], a.commits[1:]):
        added = sorted(set(res[cur]) - set(res[prev]))
        removed = sorted(set(res[prev]) - set(res[cur]))
        changed = sorted(k for k in set(res[cur]) & set(res[prev])
                         if {(x[0], x[1]) for x in res[cur][k]} != {(x[0], x[1]) for x in res[prev][k]})
        rep = dict(added=[dict(block=b, name=n, defaults=sorted({str(x[1]) for x in res[cur][(b, n)]}),
                               files=sorted({x[2] for x in res[cur][(b, n)]}))
                          for b, n in added],
                   removed=[dict(block=b, name=n) for b, n in removed],
                   default_changed=[dict(block=b, name=n,
                                         before=sorted({str(x[1]) for x in res[prev][(b, n)]}),
                                         after=sorted({str(x[1]) for x in res[cur][(b, n)]}))
                                    for b, n in changed])
        report[f"{prev}..{cur}"] = rep
        print(f"== {prev}..{cur}: {len(added)} added, {len(removed)} removed, "
              f"{len(changed)} with changed default")
        blocks = {}
        for e in rep["added"]:
            blocks.setdefault(e["block"], []).append(f"{e['name']}={'/'.join(e['defaults'])}")
        for b, names in sorted(blocks.items()):
            print(f"  + <{b}> " + ", ".join(names))
        for e in rep["removed"]:
            print(f"  - <{e['block']}> {e['name']}")
        for e in rep["default_changed"]:
            print(f"  ~ <{e['block']}> {e['name']}: {e['before']} -> {e['after']}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=1)


if __name__ == "__main__":
    main()
