"""K1: `kb verify-downloads`, the inventory of kb-data/raw against the manifests.

Layout it builds on (fixed by harness/bin/nrpic-fetch-arxiv, which every session uses):

    kb-data/raw/arxiv/<id_>/<vN>/source.bin     the e-print as downloaded
    kb-data/raw/arxiv/<id_>/<vN>/src/            its extraction (paper.pdf, main.tex or the tar tree)
    kb-data/meta/arxiv/<id_>.json                the download record (status, version, sha256, ...)

with <id_> the arXiv id with "/" replaced by "_"; a second download of the same version
goes into <vN>.retry<k>. Other sessions add entries at any time, so entries that are not in
the manifest are reported as "extra", never treated as errors, and a directory without a
record is reported as "incomplete" (it may be a fetch in progress).

For every entry the check recomputes from the bytes, without trusting the record:
  - sha256 of source.bin, compared with the record;
  - the file type from the content (kbtool.sniff), compared with the kind the fetch recorded;
  - the version from the directory name, the record and the Content-Disposition file name
    (whose id part must be the requested id);
  - the extracted tree against the archive listing: every safe regular member present with
    its size, nothing else present, no symlinks, devices, executable bits or oversized files.
Nothing under kb-data/raw is executed, compiled or imported; only bytes are read.
"""
import hashlib
import json
import os
import re
import time

from . import __version__
from . import sniff
from .brief import load_arxiv_manifest, load_github_manifest
from .gitmeta import read_checkout

VERSION_DIR = re.compile(r"^v(\d+)(\.retry(\d+))?$")
DISPOSITION = re.compile(r'filename="?arXiv-(?P<id>[^"]+?)v(?P<v>\d+)(?P<ext>\.[A-Za-z.]+)?"?')

STATUS_ORDER = ["ok", "problem", "incomplete", "failed", "missing"]


def id_key(aid):
    return aid.replace("/", "_")


def key_to_id(key):
    """Inverse of id_key for the two arXiv id formats (old style: archive/7 digits)."""
    m = re.match(r"^([a-z\-]+(?:\.[A-Z]{2})?)_(\d{7})$", key)
    return f"{m.group(1)}/{m.group(2)}" if m else key


def sha256_file(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _read_json(path):
    try:
        with open(path) as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError) as e:
        return None, f"unreadable record: {e!r}"[:200]


def version_dirs(base):
    """Version directories of one paper, ordered by (version, retry)."""
    out = []
    try:
        names = os.listdir(base)
    except FileNotFoundError:
        return out
    for n in names:
        m = VERSION_DIR.match(n)
        p = os.path.join(base, n)
        if os.path.isdir(p) and not os.path.islink(p):
            if m:
                out.append((int(m.group(1)), int(m.group(3) or 0), n))
            else:
                out.append((-1, 0, n))                 # vX or anything unexpected
    return [n for _, _, n in sorted(out)]


def expected_tree(kind, data):
    """Files the extraction of a sniffed e-print must contain: {relpath: size}, plus the
    names of members a safe extraction refuses."""
    if kind in ("pdf",):
        return {"paper.pdf": len(data)}, []
    if kind in ("gzip-pdf", "gzip-tex", "gzip-other", "tex", "html", "unknown", "empty"):
        return {"main.tex": len(data)}, []
    if kind in ("gzip-tar", "tar"):
        files, refused = {}, []
        for name, typ, size, prob in sniff.tar_members(data):
            if prob:
                # the fetch command refuses links, devices, absolute and parent paths, long names;
                # it does NOT refuse oversized files: those are reported by the tree scan instead
                if prob.startswith("file larger"):
                    files[os.path.normpath(name)] = size
                else:
                    refused.append(name)
                continue
            if typ == "file":
                files[os.path.normpath(name)] = size
        return files, refused
    return {}, []


def check_version_dir(vdir, record):
    """All checks of one <id_>/<vN> directory. Returns a dict (no exception escapes)."""
    out = {"dir": vdir, "problems": [], "notes": []}
    src_bin = os.path.join(vdir, "source.bin")
    src = os.path.join(vdir, "src")
    if not os.path.isfile(src_bin) or os.path.islink(src_bin):
        out["problems"].append("source.bin missing")
        return out
    st = os.lstat(src_bin)
    out["bytes"] = st.st_size
    out["sha256"] = sha256_file(src_bin)
    try:
        with open(src_bin, "rb") as f:
            blob = f.read()
        kind, data = sniff.sniff(blob)
    except sniff.TooLarge as e:
        out["problems"].append(str(e))
        kind, data = "unknown", b""
    except Exception as e:                                   # zlib.error, EOFError, ...: a finding
        out["problems"].append(f"unreadable e-print: {e!r}"[:200])
        kind, data = "unknown", b""
    out["sniffed_kind"] = kind
    members = None
    if kind in ("gzip-tar", "tar"):
        try:
            members = sniff.tar_members(data)
        except Exception as e:                               # a broken archive is a finding
            out["problems"].append(f"tar listing failed: {e!r}"[:200])
            members = []
    out["source_kind"] = sniff.source_kind(kind, members)
    if kind in ("html", "empty", "unknown", "gzip-other"):
        out["problems"].append(f"not an e-print: content is {kind}")
    # tree against the archive
    if not os.path.isdir(src) or os.path.islink(src):
        out["problems"].append("src/ missing")
    else:
        scan = sniff.scan_tree(src)
        out["n_files"] = scan["files"]
        out["src_bytes"] = scan["bytes"]
        for rel, why in scan["problems"]:
            out["problems"].append(f"src/{rel}: {why}")
        try:
            exp, refused = expected_tree(kind, data)
        except Exception as e:
            exp, refused = {}, []
            out["problems"].append(f"listing failed: {e!r}"[:200])
        got = scan["names"]
        missing = sorted(set(exp) - set(got))
        extra = sorted(set(got) - set(exp))
        wrong = sorted(n for n in set(exp) & set(got) if exp[n] != got[n])
        if missing:
            out["problems"].append(f"{len(missing)} archive members not extracted (first: {missing[0]})")
        if extra:
            out["problems"].append(f"{len(extra)} files in src/ not in the archive (first: {extra[0]})")
        if wrong:
            out["problems"].append(f"{len(wrong)} extracted files differ in size (first: {wrong[0]})")
        out["refused_members"] = refused
        if record is not None:
            rec_sk = set(record.get("skipped_members") or [])
            if rec_sk != set(refused):
                out["notes"].append(f"refused members: record lists {len(rec_sk)}, archive check finds {len(refused)}")
        if refused:
            out["notes"].append(f"{len(refused)} unsafe archive members refused (first: {refused[0]})")
    return out


def check_paper(lay, aid, row=None):
    """Status of one arXiv id in the store. `row` is its manifest row (None for extras)."""
    key = id_key(aid)
    base = os.path.join(lay.raw_arxiv, key)
    record, rec_err = _read_json(os.path.join(lay.meta_arxiv, key + ".json"))
    vdirs = version_dirs(base)
    res = {"id": aid, "key": key, "in_manifest": row is not None,
           "group": row["group"] if row else None, "priority": row["priority"] if row else None,
           "record_status": record.get("status") if record else None,
           "versions_present": vdirs, "problems": [], "notes": []}
    if rec_err:
        res["problems"].append(rec_err)
    if not vdirs:
        if record and record.get("status") == "failed":
            res["status"] = "failed"
            res["notes"].append(f"last attempt failed at {record.get('tried_utc')}: {record.get('error', '')[:120]}")
        elif record and record.get("status") == "ok":
            res["status"] = "incomplete"
            res["problems"].append("record says ok but no version directory exists")
        else:
            res["status"] = "missing"
        return res
    # the directory the record points at is the current one; otherwise the newest
    current = None
    if record and record.get("status") == "ok" and record.get("src"):
        cur_dir = os.path.dirname(os.path.normpath(record["src"]))
        if os.path.dirname(cur_dir) == os.path.normpath(base) and os.path.basename(cur_dir) in vdirs:
            current = os.path.basename(cur_dir)
        else:
            res["problems"].append(f"record points outside the store entry: {record.get('src')}")
    if current is None:
        current = vdirs[-1]
        if record is None:
            res["notes"].append("no download record (a fetch may be in progress)")
    if len(vdirs) > 1:
        res["notes"].append(f"{len(vdirs)} version directories: {', '.join(vdirs)}")
    chk = check_version_dir(os.path.join(base, current), record)
    res["current"] = current
    for k in ("bytes", "sha256", "sniffed_kind", "source_kind", "n_files", "src_bytes", "refused_members"):
        if k in chk:
            res[k] = chk[k]
    res["problems"] += chk["problems"]
    res["notes"] += chk["notes"]
    # version: directory name, record, Content-Disposition
    m = VERSION_DIR.match(current)
    v_dir = f"v{m.group(1)}" if m else None
    res["version"] = v_dir
    res["version_source"] = "directory"
    if v_dir is None:
        res["problems"].append(f"version unknown (directory {current!r})")
    if record:
        if record.get("version") and v_dir and record["version"] != v_dir:
            res["problems"].append(f"record version {record['version']} differs from directory {v_dir}")
        if record.get("sha256") and res.get("sha256") and record["sha256"] != res["sha256"]:
            res["problems"].append("sha256 of source.bin differs from the download record")
        if record.get("bytes") is not None and res.get("bytes") is not None and record["bytes"] != res["bytes"]:
            res["problems"].append("size of source.bin differs from the download record")
        disp = record.get("content_disposition") or ""
        dm = DISPOSITION.search(disp)
        if dm:
            if dm.group("id") != aid.replace("/", ""):
                res["problems"].append(f"Content-Disposition names {dm.group('id')!r}, not {aid!r}")
            if v_dir and f"v{dm.group('v')}" != v_dir:
                res["problems"].append(f"Content-Disposition version v{dm.group('v')} differs from {v_dir}")
            else:
                res["version_source"] = "content-disposition"
        else:
            res["notes"].append("no arXiv file name in Content-Disposition: version not confirmed")
        fk = record.get("kind")
        sk = res.get("sniffed_kind")
        consistent = {"tar": ("gzip-tar", "tar"), "pdf": ("pdf",),
                      "single-file": ("gzip-tex", "gzip-other", "gzip-pdf", "tex", "html", "unknown", "empty")}
        if fk and sk and sk not in consistent.get(fk, ()):
            res["problems"].append(f"fetch recorded kind {fk!r} but content is {sk!r}")
        res["fetched_utc"] = record.get("fetched_utc")
    res["status"] = "problem" if res["problems"] else "ok"
    if record is None and res["status"] == "ok":
        res["status"] = "incomplete"
    return res


def legacy_copies(lay):
    """arXiv ids with an older copy under $NRPIC_HOME/refs/arxiv_<id_> (not part of the store)."""
    out = {}
    try:
        for n in os.listdir(lay.legacy_refs):
            if n.startswith("arxiv_") and os.path.isdir(os.path.join(lay.legacy_refs, n)):
                out[key_to_id(n[len("arxiv_"):])] = os.path.join(lay.legacy_refs, n)
    except FileNotFoundError:
        pass
    return out


def check_repo(lay, row):
    repo = row["repo"]
    key = repo.replace("/", "__")
    path = os.path.join(lay.raw_github, key)
    meta, err = _read_json(os.path.join(lay.meta_github, key + ".json"))
    res = {"repo": repo, "key": key, "role": row["role"], "owners": row["owners"],
           "problems": [], "notes": []}
    if err:
        res["problems"].append(err)
    if not os.path.isdir(path) or os.path.islink(path):
        res["status"] = "missing"
        return res
    info = read_checkout(path)
    res.update({k: info.get(k) for k in ("commit_sha", "head_ref", "license_files", "license_spdx_guess")})
    res["problems"] += info.get("problems", [])
    if meta:
        for k in ("commit_sha", "commit_date", "default_branch", "license_spdx", "branches"):
            if k in meta:
                res["meta_" + k] = meta[k] if k != "branches" else len(meta[k])
        if meta.get("commit_sha") and info.get("commit_sha") and meta["commit_sha"] != info["commit_sha"]:
            res["problems"].append("checkout HEAD differs from the pinned commit of the record")
        if repo.lower() == "ias-astrophysics/athenak" and not meta.get("branches"):
            res["notes"].append("AthenaK record lacks the remote branch tips needed by the upstream watch")
    else:
        res["notes"].append("no record in meta/github (commit date, default branch, licence not recorded)")
    res["status"] = "problem" if res["problems"] else ("ok" if meta else "incomplete")
    return res


def verify(lay, manifest_dir):
    """The full inventory: a dict ready for JSON."""
    t0 = time.time()
    arxiv = load_arxiv_manifest(os.path.join(manifest_dir, "arxiv.tsv"))
    github = load_github_manifest(os.path.join(manifest_dir, "github.tsv"))
    by_key = {id_key(r["id"]): r for r in arxiv}
    papers = [check_paper(lay, r["id"], r) for r in arxiv]
    present = set()
    for d in (lay.raw_arxiv, lay.meta_arxiv):
        try:
            for n in os.listdir(d):
                present.add(n[:-5] if n.endswith(".json") else n)
        except FileNotFoundError:
            pass
    extras = [check_paper(lay, key_to_id(k)) for k in sorted(present - set(by_key)) if not k.startswith(".")]
    legacy = legacy_copies(lay)
    for p in papers:
        if p["status"] in ("missing", "failed") and p["id"] in legacy:
            p["notes"].append(f"older copy outside the store: {legacy[p['id']]}")
    repos = [check_repo(lay, r) for r in github]
    try:
        extra_repos = sorted(set(os.listdir(lay.raw_github)) - {r["repo"].replace("/", "__") for r in github})
    except FileNotFoundError:
        extra_repos = []

    def counts(rows, key="status"):
        c = {}
        for r in rows:
            c[r[key]] = c.get(r[key], 0) + 1
        return c

    by_pri = {}
    for p in papers:
        d = by_pri.setdefault(str(p["priority"]), {})
        d[p["status"]] = d.get(p["status"], 0) + 1
    by_grp = {}
    for p in papers:
        d = by_grp.setdefault(p["group"], {})
        d[p["status"]] = d.get(p["status"], 0) + 1
    return {
        "tool": f"kbtool {__version__}", "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data_root": lay.data, "manifest_dir": manifest_dir,
        "arxiv": {"manifest_rows": len(arxiv), "status": counts(papers), "by_priority": by_pri,
                  "by_group": by_grp, "extra": len(extras),
                  "source_kind": counts([p for p in papers + extras if p.get("source_kind")], "source_kind")},
        "github": {"manifest_rows": len(github), "status": counts(repos), "extra": extra_repos},
        "papers": papers, "extras": extras, "repos": repos,
        "elapsed_s": round(time.time() - t0, 3),
    }


def missing_ids(inv, priority=None, include_failed=True):
    """Manifest ids to fetch: missing (and failed) entries, optionally of one priority."""
    want = {"missing", "failed"} if include_failed else {"missing"}
    return [p["id"] for p in inv["papers"]
            if p["status"] in want and (priority is None or p["priority"] == priority)]


def sha256sums(inv, data_root):
    """Lines of manifests/SHA256SUMS (sha256sum -c format, paths relative to the data root)."""
    lines = []
    for p in inv["papers"] + inv["extras"]:
        if p.get("sha256") and p.get("current"):
            rel = os.path.join("raw", "arxiv", p["key"], p["current"], "source.bin")
            lines.append(f"{p['sha256']}  {rel}")
    return sorted(lines, key=lambda s: s.split("  ", 1)[1])


def report_md(inv):
    """Human-readable report (ids, kinds, hashes only; no paper text)."""
    a, g = inv["arxiv"], inv["github"]
    L = [f"# kb verify-downloads report", "",
         f"Checked {inv['checked_at']} by {inv['tool']} against `{os.path.basename(inv['manifest_dir'])}/` "
         f"(data root `{inv['data_root']}`).", "",
         "## arXiv", "",
         f"Manifest rows: {a['manifest_rows']}. Status: " +
         ", ".join(f"{k} {a['status'].get(k, 0)}" for k in STATUS_ORDER) + f". Extra entries (not in the manifest): {a['extra']}.",
         "", "| priority | " + " | ".join(STATUS_ORDER) + " |", "|---|" + "---|" * len(STATUS_ORDER)]
    for pri in ("3", "2", "1"):
        d = a["by_priority"].get(pri, {})
        L.append(f"| {pri} | " + " | ".join(str(d.get(k, 0)) for k in STATUS_ORDER) + " |")
    L += ["", "Source kinds (content-sniffed): " + ", ".join(f"{k} {v}" for k, v in sorted(a["source_kind"].items())), ""]
    L += ["### Present entries", "", "| id | group | pri | version | kind | source_kind | files | bytes | sha256 (12) | status |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for p in sorted(inv["papers"] + inv["extras"], key=lambda r: (r["priority"] is None, -(r["priority"] or 0), r["id"])):
        if p["status"] in ("missing", "failed"):
            continue
        L.append(f"| {p['id']} | {p['group'] or '-'} | {p['priority'] or '-'} | {p.get('version') or '?'} "
                 f"| {p.get('sniffed_kind', '?')} | {p.get('source_kind', '?')} | {p.get('n_files', '?')} "
                 f"| {p.get('bytes', '?')} | {(p.get('sha256') or '')[:12]} | {p['status']}"
                 f"{'' if p['in_manifest'] else ' (extra)'} |")
    probs = [p for p in inv["papers"] + inv["extras"] if p["problems"] or p["notes"]]
    if probs:
        L += ["", "### Problems and notes", ""]
        for p in probs:
            for x in p["problems"]:
                L.append(f"- {p['id']}: PROBLEM {x}")
            for x in p["notes"]:
                L.append(f"- {p['id']}: note {x}")
    for status in ("failed", "missing"):
        rows = [p for p in inv["papers"] if p["status"] == status]
        if rows:
            L += ["", f"### {status.capitalize()} ({len(rows)})", ""]
            for pri in (3, 2, 1):
                ids = [p["id"] for p in rows if p["priority"] == pri]
                if ids:
                    L.append(f"- priority {pri} ({len(ids)}): " + " ".join(ids))
    L += ["", "## GitHub", "", f"Manifest rows: {g['manifest_rows']}. Status: " +
          ", ".join(f"{k} {v}" for k, v in sorted(g["status"].items())) +
          f". Extra checkouts: {len(g['extra'])}.", ""]
    for r in inv["repos"]:
        if r["status"] != "missing":
            L.append(f"- {r['repo']}: {r['status']} commit {r.get('commit_sha')} licence {r.get('license_spdx_guess')}"
                     + "".join(f"; PROBLEM {x}" for x in r["problems"]) + "".join(f"; note {x}" for x in r["notes"]))
    miss = [r["repo"] for r in inv["repos"] if r["status"] == "missing"]
    if miss:
        L.append(f"- missing ({len(miss)}): " + " ".join(miss))
    L.append("")
    return "\n".join(L)
