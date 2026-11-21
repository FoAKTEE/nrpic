"""Steps 5 and 6 of the KB-G2 verifier: C1 (all papers and repositories ingested), C5 / KB-G0
C2 (read-only access by default), C6 / KB-G0 C3 (snapshots, ids, locators), KB-G0 C1 (tools,
directories of brief 12.2) and the manifest part of C9 / KB-G0 C6 (failed runs on record).

The verifier's own code. Reads the frozen snapshot read-only (mode=ro, immutable), the manifests
of kb/manifests and kb-data/manifests, file metadata of kb-data, the run manifests under
tracks/kb/runs, and the code of kb/kbtool (static: the default database of the readers).
Dynamic test of the default database and of `kb snapshot`: a FAKE data root inside the run
directory (KB_DATA_ROOT and KB_LOCK point there), never the real kb-data/db.

The brief is not read by me: rows of the paper and repository manifests are compared with the
brief lines named in kb/manifests/SOURCE.json by code (id contained in that line), and only
counts are printed.
Writes checks.json into $NRPIC_RUN_DIR and prints a summary.
"""
import collections
import glob
import hashlib
import json
import os
import re
import sqlite3
import stat
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402

WT = "/data/haiyangw/nrpic/wt/kb"
HOME = "/data/haiyangw/nrpic"
KBD = C.KBDATA
BRIEF = os.path.join(HOME, "einstein_vlasov_pic_cosmology_agent_brief.en.md")
PY = os.path.join(WT, "kb/.venv/bin/python")
KB = os.path.join(WT, "kb/bin/kb")


def sha256(path, bs=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(bs), b""):
            h.update(b)
    return h.hexdigest()


def read_tsv(path):
    rows = []
    for ln in open(path, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"):
            continue
        rows.append(ln.rstrip("\n").split("\t"))
    return rows


def kb(args, env=None, timeout=600):
    e = dict(os.environ, OMP_NUM_THREADS="1", TOKENIZERS_PARALLELISM="false")
    if env:
        e.update(env)
    p = subprocess.run([PY, "-I", KB] + args, cwd=WT, env=e, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


# ----------------------------------------------------------------------------------------- C1
def check_c1(con, out):
    src = json.load(open(os.path.join(WT, "kb/manifests/SOURCE.json")))
    arx = read_tsv(os.path.join(WT, "kb/manifests/arxiv.tsv"))
    gh = read_tsv(os.path.join(WT, "kb/manifests/github.tsv"))
    add = read_tsv(os.path.join(WT, "kb/manifests/arxiv_additions.tsv"))
    add = [r for r in add if r[0] != "id"]                       # header rows (written twice)
    r = dict(manifest_rows=len(arx), additions_rows=len(add), github_rows=len(gh))
    # the extraction against the brief, by code only (counts)
    r["brief_sha_matches_source_json"] = sha256(BRIEF) == src["brief_sha256"]
    r["arxiv_tsv_sha_matches"] = sha256(os.path.join(WT, "kb/manifests/arxiv.tsv")) == src["files"]["arxiv.tsv"]
    r["github_tsv_sha_matches"] = sha256(os.path.join(WT, "kb/manifests/github.tsv")) == src["files"]["github.tsv"]
    bl = open(BRIEF, encoding="utf-8").read().split("\n")
    a0, g0 = src["arxiv"]["first_line"], src["github"]["first_line"]
    r["arxiv_rows_found_in_brief_line"] = sum(1 for i, row in enumerate(arx)
                                              if row[0] in bl[a0 - 1 + i] and row[1] in bl[a0 - 1 + i])
    r["github_rows_found_in_brief_line"] = sum(1 for i, row in enumerate(gh) if row[0] in bl[g0 - 1 + i])
    r["kb_manifests_equal_kbdata_manifests"] = all(
        sha256(os.path.join(WT, "kb/manifests", f)) == sha256(os.path.join(KBD, "manifests", f))
        for f in ("arxiv.tsv", "github.tsv"))
    want = {row[0]: (row[1], int(row[2])) for row in arx}
    dup = [k for k, v in collections.Counter(row[0] for row in arx + add).items() if v > 1]
    for row in add:
        want[row[0]] = (row[1], int(row[2]))
    r["expected_papers"] = len(want)
    r["duplicate_ids_in_manifests"] = dup
    db = {x["paper_id"]: x for x in con.execute(
        "select paper_id, grp, priority, version, source_kind, parse_status, flat_sha256, main_tex from papers")}
    r["papers_in_snapshot"] = len(db)
    r["missing"] = sorted(set(want) - set(db))
    r["extra"] = sorted(set(db) - set(want))
    r["grp_or_priority_differs"] = sorted(k for k in set(want) & set(db)
                                         if (db[k]["grp"], db[k]["priority"]) != want[k])
    nchunk = dict(con.execute("select paper_id, count(*) from chunks group by 1").fetchall())
    r["papers_without_chunks"] = sorted(k for k in db if not nchunk.get(k))
    r["source_kind"] = dict(collections.Counter(x["source_kind"] for x in db.values()))
    r["parse_status"] = dict(collections.Counter(x["parse_status"] for x in db.values()))
    no_raw, no_flat = [], []
    for k, x in db.items():
        vd = os.path.join(C.RAW_ARXIV, C.id_dir(k), x["version"] or "")
        if not (os.path.isfile(os.path.join(vd, "source.bin")) or os.path.isfile(os.path.join(vd, "source.pdf"))):
            no_raw.append(k)
        if x["source_kind"] == "tex" and not os.path.isfile(os.path.join(C.BUILD_TEX, C.id_dir(k), "flat.tex")):
            no_flat.append(k)
    r["papers_without_raw_file"] = sorted(no_raw)
    rawdirs = sorted(n for n in os.listdir(C.RAW_ARXIV) if not n.startswith("."))
    ids_ = {C.id_dir(k) for k in db}
    r["raw_arxiv_dirs"] = len(rawdirs)
    r["raw_arxiv_dirs_not_in_snapshot"] = [n for n in rawdirs if n not in ids_]
    nemb = con.execute("select count(*) from embeddings where owner_kind='chunk'").fetchone()[0]
    nch = con.execute("select count(*) from chunks where kind != 'comment'").fetchone()[0]
    r["chunk_vectors"], r["chunks_not_comment"] = nemb, nch
    r["chunk_vectors_per_model"] = dict(con.execute(
        "select model, count(*) from embeddings where owner_kind='chunk' group by 1").fetchall())
    r["tex_papers_without_flat"] = sorted(no_flat)
    # repositories: the manifest plus this repository
    want_r = [row[0] for row in gh] + ["local/nrpic"]
    reps = {x["repo_id"]: x for x in con.execute("select repo_id, commit_sha, commit_date, license_spdx, role from repos")}
    nf = dict(con.execute("select repo_id, count(*) from code_files group by 1").fetchall())
    nsym = dict(con.execute("select f.repo_id, count(*) from symbols s join code_files f on f.file_id=s.file_id "
                            "group by 1").fetchall())
    ncc = dict(con.execute("select f.repo_id, count(*) from code_chunks c join code_files f on f.file_id=c.file_id "
                           "group by 1").fetchall())
    r["expected_repos"] = len(want_r)
    r["repos_in_snapshot"] = len(reps)
    r["repos_missing"] = sorted(set(want_r) - set(reps))
    r["repos_extra"] = sorted(set(reps) - set(want_r))
    per = []
    for k in want_r:
        x = reps.get(k)
        sha = (x["commit_sha"] if x else None) or ""
        raw = os.path.isdir(os.path.join(KBD, "raw", "github", k.replace("/", "__")))
        per.append(dict(repo=k, commit=sha[:12], commit_ok=bool(re.fullmatch(r"[0-9a-f]{40}", sha)),
                        files=nf.get(k, 0), symbols=nsym.get(k, 0), code_chunks=ncc.get(k, 0),
                        license=x["license_spdx"] if x else None, raw_dir=raw))
    r["repos"] = per
    r["repos_without_commit"] = [p["repo"] for p in per if not p["commit_ok"]]
    r["repos_without_files"] = [p["repo"] for p in per if p["files"] == 0]
    r["repos_without_chunks"] = [p["repo"] for p in per if p["code_chunks"] == 0]
    r["repos_without_license"] = [p["repo"] for p in per if not p["license"]]
    out["C1"] = r


# ------------------------------------------------------------------------------- C5, C6, G0
def check_modes(out):
    d = os.path.join(KBD, "db")
    files = []
    for p in sorted(glob.glob(os.path.join(d, "*"))):
        st = os.lstat(p)
        e = dict(name=os.path.basename(p), mode=oct(stat.S_IMODE(st.st_mode)), link=os.path.islink(p))
        if e["link"]:
            e["target"] = os.readlink(p)
        files.append(e)
    snaps = [e for e in files if re.fullmatch(r"kb-\d{8}-[0-9a-f]{7}\.sqlite", e["name"])]
    for e in snaps:
        h = sha256(os.path.join(d, e["name"]))
        e["sha256"] = h
        e["sha_prefix_matches_name"] = h[:7] == e["name"][12:19]
    out["db_files"] = files
    out["snapshots_not_0444"] = [e["name"] for e in snaps if e["mode"] != "0o444"]
    out["snapshots_sha_mismatch"] = [e["name"] for e in snaps if not e["sha_prefix_matches_name"]]


def check_default_db_static(out):
    src = open(os.path.join(WT, "kb/kbtool/db.py")).read()
    m = re.search(r"def open_for_read\(.*?\n(?:    .*\n|\n)+", src)
    out["open_for_read_src"] = m.group(0).strip() if m else None
    ro = re.search(r"def connect_ro\(.*?\n(?:    .*\n)+", src)
    out["connect_ro_src"] = ro.group(0).strip() if ro else None
    # every module that opens a database: which call it uses
    uses = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(WT, "kb/kbtool/*.py"))):
        t = open(p).read()
        for name in ("open_for_read", "connect_ro", "connect_rw"):
            n = len(re.findall(r"\b" + name + r"\(", t)) - len(re.findall(r"def " + name + r"\(", t))
            if n:
                uses[os.path.basename(p)].append(f"{name} x{n}")
    out["open_calls"] = dict(uses)
    # what the readers' --help says about the default
    helps = {}
    for sub in ("search", "show", "eq", "cites", "code", "claim list", "frontier", "export"):
        rc, so, se = kb(sub.split() + ["--help"])
        mm = re.search(r"^\s*--db DB\s+([^\n]*)", so, re.M)
        helps[sub] = dict(rc=rc, db_help=" ".join(mm.group(1).split()) if mm else None)
    out["help_db"] = helps


def check_default_db_dynamic(out, rd):
    """A fake data root with two databases that differ: db/current -> snapshot holding the word
    'alphaverifier', db/kb.sqlite then changed to hold 'betaverifier' as well."""
    root = os.path.join(rd, "fake_kbdata")
    os.makedirs(root, exist_ok=True)
    env = dict(KB_DATA_ROOT=root, KB_LOCK=os.path.join(rd, "fake-kb-writer.lock"))
    res = {}
    res["init"] = kb(["init"], env)[0]
    work = os.path.join(root, "db", "kb.sqlite")

    def add(word, cid):
        con = sqlite3.connect(work)
        con.execute("INSERT OR IGNORE INTO papers(paper_id, title, grp, priority, version, source_kind, parse_status) "
                    "VALUES ('9999.00001', 'verifier test paper', 'G01', 1, 'v1', 'tex', 'ok')")
        con.execute("INSERT INTO chunks(chunk_id, paper_id, kind, text, n_tokens, char_start, char_end) "
                    "VALUES (?, '9999.00001', 'body', ?, 3, 0, 30)", (cid, f"the word {word} is here"))
        con.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
        con.commit()
        con.close()
    add("alphaverifier", 1)
    rc, so, se = kb(["snapshot"], env)
    res["snapshot_rc"], res["snapshot_out"] = rc, so.strip()[-300:]
    cur = os.path.join(root, "db", "current")
    res["current_target"] = os.readlink(cur) if os.path.islink(cur) else None
    if res["current_target"]:
        sp = os.path.join(root, "db", res["current_target"])
        res["snapshot_mode"] = oct(stat.S_IMODE(os.stat(sp).st_mode))
        h = sha256(sp)
        res["snapshot_sha_prefix_matches_name"] = h[:7] == res["current_target"][12:19]
        before = h
    add("betaverifier", 2)
    q = {}
    for word in ("alphaverifier", "betaverifier"):
        rc, so, se = kb(["search", word, "--text-only", "-k", "3", "--json"], env)
        try:
            d = json.loads(so)
            q[word] = dict(rc=rc, n_hits=len(d.get("hits", [])), database=d.get("info", {}).get("database"))
        except Exception:
            q[word] = dict(rc=rc, error=(so + se)[-300:])
    res["search_default"] = q
    rc, so, se = kb(["search", "betaverifier", "--text-only", "-k", "3", "--json", "--db", work], env)
    try:
        res["search_explicit_work_db_hits"] = len(json.loads(so).get("hits", []))
    except Exception:
        res["search_explicit_work_db_hits"] = (so + se)[-300:]
    if res["current_target"]:
        res["snapshot_unchanged_by_reads"] = sha256(os.path.join(root, "db", res["current_target"])) == before
        res["files_in_fake_db_dir"] = sorted(os.listdir(os.path.join(root, "db")))
    out["default_db_dynamic"] = res


def check_snapshot_log(con, out):
    rows = [dict(x) for x in con.execute("select at, step, target, status, message from ingest_log "
                                          "where step like '%snapshot%' order by log_id")]
    out["ingest_log_snapshots"] = rows
    last = con.execute("select max(at) from ingest_log").fetchone()[0]
    out["ingest_log_last_at"] = last
    out["ingest_log_status"] = dict(collections.Counter(
        f"{s}:{st}" for s, st in con.execute("select step, status from ingest_log")))


def check_locators(out):
    """Do the reader commands' answers name the snapshot? (C6: locators carry the id)"""
    res = {}
    rc, so, se = kb(["search", "tetrahedra of the dark matter sheet in phase space", "--db", C.SNAP, "-k", "3",
                     "--text-only"])
    res["search_text_rc"] = rc
    res["search_text_names_snapshot"] = C.SNAP_ID in so
    res["search_text_tail"] = so.strip().split("\n")[-1][:300]
    rc, so, se = kb(["search", "tetrahedra of the dark matter sheet in phase space", "--db", C.SNAP, "-k", "3",
                     "--text-only", "--json"])
    try:
        d = json.loads(so)
        res["search_json_info"] = d.get("info")
        res["search_json_hit_keys"] = sorted(d["hits"][0].keys()) if d.get("hits") else []
        res["search_json_hits_name_snapshot"] = any(C.SNAP_ID in json.dumps(h) for h in d.get("hits", []))
    except Exception as e:
        res["search_json_error"] = f"{type(e).__name__}: {(so + se)[-200:]}"
    for name, args in (("show", ["show", "1111.3944", "--abstract", "--db", C.SNAP]),
                       ("eq", ["eq", "geodesic deviation", "-k", "2", "--db", C.SNAP]),
                       ("cites", ["cites", "1111.3944", "--out", "--db", C.SNAP]),
                       ("code", ["code", "Z4c", "-k", "2", "--db", C.SNAP])):
        rc, so, se = kb(args)
        res[f"{name}_rc"] = rc
        res[f"{name}_names_snapshot"] = C.SNAP_ID in so
        res[f"{name}_tail"] = (so.strip().split("\n")[-1] if so.strip() else se.strip()[-200:])[:300]
    out["locators"] = res


def check_dirs(out):
    want_data = ["raw/arxiv", "raw/github", "meta/arxiv", "meta/github", "build/tex", "build/code", "db",
                 "db/kb.sqlite", "db/current", "manifests/arxiv.tsv", "manifests/github.tsv",
                 "manifests/SHA256SUMS", "logs"]
    want_repo = ["pyproject.toml", "uv.lock", "schema.sql", "migrations", "kbtool", "golden/questions.yaml",
                 "curated/paper_code_links.tsv", "curated/equation_tags.yaml", "curated/seed_claims.jsonl",
                 "tests", "QA_REPORT.md", "STATE.json"]            # existence only; contents not opened
    out["dirs_data"] = {p: os.path.exists(os.path.join(KBD, p)) for p in want_data}
    out["dirs_repo"] = {p: os.path.exists(os.path.join(WT, "kb", p)) for p in want_repo}
    # tools: declared dependencies (pyproject) and the locks
    pj = open(os.path.join(WT, "kb/pyproject.toml")).read()
    out["pyproject_dependencies"] = re.findall(r'^\s*"([^"]+)",?\s*$', pj, re.M)
    out["locks"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(WT, "kb/requirements-*.lock")))
    reasons = {}
    for f in ("kb/README.md", "kb/EMBEDDING.md", "kb/pyproject.toml"):
        t = open(os.path.join(WT, f)).read()
        reasons[f] = [" ".join(ln.split())[:200] for ln in t.split("\n")
                      if re.search(r"\b(because|reason|chosen|instead of|rather than|why)\b", ln, re.I)][:12]
    out["tool_reason_lines"] = reasons
    raw_ro = []
    for p in glob.glob(os.path.join(C.RAW_ARXIV, "*", "*", "source.bin"))[:2000]:
        if os.stat(p).st_mode & 0o222:
            raw_ro.append(p)
    out["raw_source_bin_writable"] = len(raw_ro)


def check_runs(out):
    st = collections.Counter()
    failed = []
    for p in sorted(glob.glob(os.path.join(WT, "tracks/kb/runs/*/manifest.json"))):
        try:
            m = json.load(open(p))
        except Exception:
            st["unreadable"] += 1
            continue
        s = str(m.get("status"))
        st[s] += 1
        if re.search(r"fail|stop|cancel|supersed|error|abort", s, re.I):
            failed.append(dict(run_id=m.get("run_id") or os.path.basename(os.path.dirname(p)), status=s,
                               purpose=str(m.get("purpose"))[:120]))
    out["kb_run_status"] = dict(st)
    out["kb_runs_failed_or_stopped"] = failed


def main():
    rd = C.run_dir()
    out = {}
    con = C.open_ro()
    con.row_factory = sqlite3.Row
    check_c1(con, out)
    check_snapshot_log(con, out)
    con.close()
    check_modes(out)
    check_default_db_static(out)
    check_default_db_dynamic(out, rd)
    check_locators(out)
    check_dirs(out)
    check_runs(out)
    with open(os.path.join(rd, "checks.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    c1 = {k: v for k, v in out["C1"].items() if k != "repos"}
    print(json.dumps(c1, indent=1, default=str))
    for k in ("snapshots_not_0444", "snapshots_sha_mismatch", "ingest_log_snapshots", "ingest_log_last_at",
              "default_db_dynamic", "locators", "dirs_data", "dirs_repo", "pyproject_dependencies", "locks",
              "tool_reason_lines", "raw_source_bin_writable", "help_db", "open_calls", "kb_run_status",
              "kb_runs_failed_or_stopped"):
        print(f"== {k}:", json.dumps(out.get(k), indent=1, default=str))
    for e in out["db_files"]:
        print("  db file", e)


if __name__ == "__main__":
    main()
