"""Run a list of INSPIRE queries one after the other through harness/bin/nrpic-fetch-arxiv.

Usage: python3 -I run_queries.py <spec-file> <log-tsv>
Spec lines: <label> | <INSPIRE query>   (lines starting with "#" are comments)
For each line the fetch command is called once (it holds the machine-wide INSPIRE lock and
keeps three seconds between requests; nothing runs in parallel); the label, the query, the
UTC time, the path of the query record it wrote and the total number of hits are appended
to the log. The records are untrusted data: only parsed as JSON. Standard library only.
"""
import datetime
import json
import subprocess
import sys

FETCH = "/data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv"


def main(spec, log):
    with open(spec) as fh:
        items = [l.rstrip("\n") for l in fh if l.strip() and not l.lstrip().startswith("#")]
    for l in items:
        label, q = [p.strip() for p in l.split(" | ", 1)]
        t = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p = subprocess.run(["python3", "-I", FETCH, "--inspire-query", q, "--size", "25"],
                           capture_output=True, text=True)
        path = (p.stdout.strip().splitlines() or [""])[-1]
        total, status = "", "failed"
        try:
            with open(path) as fh:
                d = json.load(fh)
            total, status = d.get("hits_total"), d.get("status")
        except (OSError, ValueError):
            path = "(none) " + p.stderr.strip()[:200]
        with open(log, "a") as fh:
            fh.write("\t".join([label, t, str(total), status, path, q]) + "\n")
        print(label, total, status, path, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
