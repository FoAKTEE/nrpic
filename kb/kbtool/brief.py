"""Machine extraction of the manifests (brief section 17) and the schema (brief 12.2).

The brief is read by script, never by eye: the blocks are found by their headings and code
fences, every row is validated, and the provenance (file, sha256, line range) is written to
kb/manifests/SOURCE.json so that each manifest row has a locator (brief line number =
first data line + row index).
"""
import hashlib
import json
import os
import re

ARXIV_NEW = re.compile(r"^\d{4}\.\d{4,5}$")
ARXIV_OLD = re.compile(r"^[a-z\-]+(\.[A-Z]{2})?/\d{7}$")
GROUP = re.compile(r"^G\d{2}$")
REPO = re.compile(r"^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$")
ROLES = {"core", "dep", "ref", "tool"}


class BriefFormatError(ValueError):
    pass


def valid_arxiv_id(aid):
    return bool(ARXIV_NEW.match(aid) or ARXIV_OLD.match(aid))


def _fence_after(lines, start, marker, lang):
    """Index range (first data line, closing fence) of the first ```lang fence after the
    line that starts with `marker`, searching from `start`."""
    i = start
    while i < len(lines) and not lines[i].startswith(marker):
        i += 1
    if i == len(lines):
        raise BriefFormatError(f"marker {marker!r} not found after line {start + 1}")
    while i < len(lines) and lines[i].strip() != "```" + lang:
        i += 1
    if i == len(lines):
        raise BriefFormatError(f"no ```{lang} fence after {marker!r}")
    j = i + 1
    while j < len(lines) and lines[j].strip() != "```":
        j += 1
    if j == len(lines):
        raise BriefFormatError(f"unclosed ```{lang} fence after {marker!r}")
    return i + 1, j


def _section_start(lines, heading):
    for i, line in enumerate(lines):
        if line.startswith(heading):
            return i
    raise BriefFormatError(f"heading {heading!r} not found")


def read_brief(path):
    blob = open(path, "rb").read()
    return blob.decode("utf-8").split("\n"), hashlib.sha256(blob).hexdigest()


def extract_manifests(path):
    """Returns (arxiv_rows, github_rows, provenance). Rows are tuples of strings in the
    column order of the brief; provenance gives the 1-based line ranges."""
    lines, sha = read_brief(path)
    s17 = _section_start(lines, "## 17.")
    a0, a1 = _fence_after(lines, s17, "**arXiv manifest.**", "tsv")
    g0, g1 = _fence_after(lines, a1, "**GitHub repository manifest.**", "tsv")
    arxiv, github, problems = [], [], []
    seen = set()
    for k in range(a0, a1):
        f = lines[k].split("\t")
        if len(f) != 3:
            problems.append(f"line {k + 1}: {len(f)} columns in arXiv manifest")
            continue
        aid, grp, pri = (x.strip() for x in f)
        if not valid_arxiv_id(aid):
            problems.append(f"line {k + 1}: bad arXiv id {aid!r}")
        if not GROUP.match(grp):
            problems.append(f"line {k + 1}: bad group {grp!r}")
        if pri not in ("1", "2", "3"):
            problems.append(f"line {k + 1}: bad priority {pri!r}")
        if aid in seen:
            problems.append(f"line {k + 1}: duplicate id {aid}")
        seen.add(aid)
        arxiv.append((aid, grp, pri))
    seen = set()
    for k in range(g0, g1):
        f = lines[k].split("\t")
        if len(f) != 4:
            problems.append(f"line {k + 1}: {len(f)} columns in GitHub manifest")
            continue
        repo, role, owners, desc = f
        if not REPO.match(repo):
            problems.append(f"line {k + 1}: bad repository {repo!r}")
        if role not in ROLES:
            problems.append(f"line {k + 1}: bad role {role!r}")
        if repo.lower() in seen:
            problems.append(f"line {k + 1}: duplicate repository {repo}")
        seen.add(repo.lower())
        github.append((repo, role, owners, desc))
    if problems:
        raise BriefFormatError("; ".join(problems))
    prov = {"brief": os.path.abspath(path), "brief_sha256": sha,
            "arxiv": {"first_line": a0 + 1, "last_line": a1, "rows": len(arxiv),
                      "columns": ["id", "group", "priority"]},
            "github": {"first_line": g0 + 1, "last_line": g1, "rows": len(github),
                       "columns": ["repo", "role", "owners", "description"]},
            "locator_rule": "brief line of row i (0-based) = first_line + i"}
    return arxiv, github, prov


def extract_schema(path):
    """The SQL block of brief 12.2 and its line range."""
    lines, sha = read_brief(path)
    s = _section_start(lines, "### 12.2")
    b0, b1 = _fence_after(lines, s, "Database schema", "sql")
    return "\n".join(lines[b0:b1]) + "\n", {"brief_sha256": sha, "first_line": b0 + 1, "last_line": b1}


def write_tsv(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    os.replace(tmp, path)


def write_manifests(brief_path, outdir):
    arxiv, github, prov = extract_manifests(brief_path)
    os.makedirs(outdir, exist_ok=True)
    write_tsv(os.path.join(outdir, "arxiv.tsv"), arxiv)
    write_tsv(os.path.join(outdir, "github.tsv"), github)
    prov["files"] = {}
    for name in ("arxiv.tsv", "github.tsv"):
        prov["files"][name] = hashlib.sha256(open(os.path.join(outdir, name), "rb").read()).hexdigest()
    prov["brief"] = os.path.basename(brief_path)
    with open(os.path.join(outdir, "SOURCE.json"), "w") as f:
        json.dump(prov, f, indent=1)
        f.write("\n")
    return arxiv, github, prov


def load_arxiv_manifest(path):
    rows = []
    for line in open(path):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        aid, grp, pri = line.split("\t")
        rows.append({"id": aid, "group": grp, "priority": int(pri)})
    return rows


def load_github_manifest(path):
    rows = []
    for line in open(path):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        repo, role, owners, desc = line.split("\t")
        rows.append({"repo": repo, "role": role, "owners": owners, "description": desc})
    return rows
