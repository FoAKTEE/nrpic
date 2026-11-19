"""Run the INSPIRE queries of a spec file one after the other through the harness fetch tool.

Usage: python3 -I run_inspire.py <spec> <out.tsv>
Spec lines: <tag> | <INSPIRE query> (comments with #). For each query the harness command
`python3 -I harness/bin/nrpic-fetch-arxiv --inspire-query <q> --size 25` is called (it holds the
machine-wide INSPIRE lock and spaces the requests); the path it prints is written to out.tsv as
<tag>\t<query>\t<path>\t<exit status>. Standard library only; nothing downloaded is executed.
"""
import subprocess
import sys

FETCH = "/data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv"


def main(spec, out):
    rows = []
    with open(spec) as fh:
        for l in fh:
            l = l.strip()
            if not l or l.startswith("#"):
                continue
            tag, q = [p.strip() for p in l.split(" | ", 1)]
            rows.append((tag, q))
    with open(out, "w") as fo:
        for tag, q in rows:
            p = subprocess.run(["python3", "-I", FETCH, "--inspire-query", q, "--size", "25"],
                               capture_output=True, text=True, timeout=600)
            path = (p.stdout.strip().splitlines() or [""])[-1]
            fo.write("%s\t%s\t%s\t%d\n" % (tag, q, path, p.returncode))
            fo.flush()
            if p.returncode:
                sys.stderr.write("query failed: %s\n%s\n" % (q, p.stderr[-500:]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
