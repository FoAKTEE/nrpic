"""Manifest additions: papers outside brief section 17 that enter the manifest by a decision
(decision 0016 item 6: "The 26 extra papers enter the manifest with a group assigned by kb").

`kb/manifests/arxiv.tsv` stays the exact extraction of the brief (`kb manifests --check`);
the additions live beside it in `kb/manifests/arxiv_additions.tsv`, one row per paper:

    id  group  priority  requested_by  decision  note

`load_full_manifest()` returns the rows of both files in the format of
`brief.load_arxiv_manifest` (id, group, priority) plus `source` ("brief17" or "addition") and,
for additions, the other columns. `check_additions()` lists what is wrong with the file.
"""
import os

from . import brief as _brief
from .paths import kb_manifest_dir

ADDITIONS = "arxiv_additions.tsv"
COLUMNS = ["id", "group", "priority", "requested_by", "decision", "note"]


def additions_path(manifest_dir=None):
    return os.path.join(manifest_dir or kb_manifest_dir(), ADDITIONS)


def load_additions(path=None):
    path = path or additions_path()
    rows = []
    if not os.path.exists(path):
        return rows
    for n, line in enumerate(open(path, encoding="utf-8"), start=1):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] == "id":
            continue                                   # header
        f += [""] * (len(COLUMNS) - len(f))
        r = dict(zip(COLUMNS, f[:len(COLUMNS)]))
        r["priority"] = int(r["priority"]) if r["priority"].isdigit() else None
        r["line"] = n
        r["source"] = "addition"
        rows.append(r)
    return rows


def check_additions(rows, base_ids, groups=None):
    problems, seen = [], set()
    for r in rows:
        where = f"line {r['line']}"
        if not _brief.valid_arxiv_id(r["id"]):
            problems.append(f"{where}: bad arXiv id {r['id']!r}")
        if not _brief.GROUP.match(r["group"] or ""):
            problems.append(f"{where}: bad group {r['group']!r}")
        elif groups is not None and r["group"] not in groups:
            problems.append(f"{where}: group {r['group']} is not a group of brief section 16")
        if r["priority"] not in (1, 2, 3):
            problems.append(f"{where}: bad priority {r['priority']!r}")
        if r["id"] in base_ids:
            problems.append(f"{where}: {r['id']} is already in the brief's manifest")
        if r["id"] in seen:
            problems.append(f"{where}: duplicate id {r['id']}")
        seen.add(r["id"])
        if not r["requested_by"] or not r["decision"]:
            problems.append(f"{where}: requested_by and decision are required")
    return problems


def load_full_manifest(manifest_dir=None):
    d = manifest_dir or kb_manifest_dir()
    base = [{**r, "source": "brief17"} for r in _brief.load_arxiv_manifest(os.path.join(d, "arxiv.tsv"))]
    return base + load_additions(additions_path(d))
