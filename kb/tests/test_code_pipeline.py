"""K6-K7 end to end on synthetic repositories served from a local file:// remote:
fetch-repos (clone, record, unresolved name), ingest repo (files, symbols, parameters,
chunks, licence, database rows), kb code queries, kb watch upstream, kb link check/load."""
import json
import os
import stat
import subprocess

import pytest

from kbtool import code_fetch, code_index, code_query, code_watch, db, links_paper_code, paths

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@example.invalid", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

HPP = """#ifndef P_HPP_
#define P_HPP_
namespace particles {
enum class ParticlesPusher {drift, leap_frog};
class ParameterInput;
class Particles {
 public:
  void Init(ParameterInput *pin);
};
}  // namespace particles
#endif
"""
CPP = """// Copyright (c) synthetic test
namespace particles {
//! \\brief reads the options
void Particles::Init(ParameterInput *pin) {
  int n = pin->GetInteger("particles", "nparticles");
  Real tol = pin->GetOrAddReal("particles", "tolerance", 1.0e-7);
  for (int i = 0; i < 2; ++i) {
    pin->GetOrAddString(block, "file_type", "hst");
  }
}
}  // namespace particles
"""
PIN = "class ParameterInput {\n public:\n  int GetInteger(std::string b, std::string n);\n};\n"
COUPLED = CPP.replace("int n =", "auto &u = pmy_pack->pz4c->tmunu; int n =")


def git(args, cwd):
    subprocess.run(["git"] + args, cwd=cwd, env=ENV, check=True, capture_output=True)


def make_upstream(tmp):
    """A remote tree <tmp>/remote/IAS-Astrophysics/athenak (bare) with branches main,
    particles_gr (src/particles mentions tmunu) and feature/nrpic-deposit."""
    work = tmp / "src_repo"
    (work / "src" / "particles").mkdir(parents=True)
    (work / "src" / "z4c").mkdir()
    (work / "inputs").mkdir()
    (work / "LICENSE").write_text("Copyright (c) X\nRedistribution and use in source and binary forms, with or "
                                  "without modification... Neither the name of the copyright holder\n")
    (work / "src" / "particles" / "particles.hpp").write_text(HPP)
    (work / "src" / "particles" / "particles.cpp").write_text(CPP)
    (work / "src" / "parameter_input.hpp").write_text(PIN)
    (work / "src" / "z4c" / "z4c.cpp").write_text("int z4c_rhs() { return 0; }\n")
    (work / "inputs" / "athinput.test").write_text("<particles>\nnparticles = 4\ntolerance = 1e-8\n"
                                                   "<output1>\nfile_type = hst\n<particles>\ntypo_param = 1\n")
    (work / "tool.py").write_text('def helper(x):\n    """help"""\n    return x\n')
    git(["init", "-q", "-b", "main"], work)
    git(["add", "-A"], work)
    git(["commit", "-q", "-m", "initial"], work)
    git(["checkout", "-q", "-b", "particles_gr"], work)
    (work / "src" / "particles" / "particles.cpp").write_text(COUPLED)
    git(["commit", "-q", "-am", "couple"], work)
    git(["checkout", "-q", "-b", "feature/nrpic-deposit", "main"], work)
    git(["checkout", "-q", "main"], work)
    remote = tmp / "remote" / "IAS-Astrophysics"
    remote.mkdir(parents=True)
    git(["clone", "-q", "--bare", str(work), str(remote / "athenak")], tmp)
    return work, tmp / "remote"


@pytest.fixture
def env(tmp_path, monkeypatch):
    work, remote = make_upstream(tmp_path)
    monkeypatch.setenv("KB_GITHUB_BASE", "file://" + str(remote))
    monkeypatch.setenv("KB_DATA_ROOT", str(tmp_path / "kb-data"))
    monkeypatch.setenv("KB_LOCK", str(tmp_path / "kb-writer.lock"))
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    (mdir / "github.tsv").write_text("IAS-Astrophysics/athenak\tcore\tall\tAthenaK\nnobody/does-not-exist\tref\t-\tx\n")
    lay = paths.layout()
    for d in lay.dirs():
        os.makedirs(d, exist_ok=True)
    db.init_db(lay)
    monkeypatch.setattr(code_index, "kb_manifest_dir", lambda: str(mdir))
    return {"lay": lay, "work": work, "tmp": tmp_path, "mdir": str(mdir)}


def test_fetch_ingest_query_watch_links(env):
    lay, tmp = env["lay"], env["tmp"]
    recs = code_fetch.fetch_repos(lay, str(tmp / "w"), manifest_dir=env["mdir"], log=lambda s: None)
    by = {r["repo"]: r for r in recs}
    assert by["nobody/does-not-exist"]["status"] == "unresolved"
    assert not os.path.exists(os.path.join(lay.raw_github, "nobody__does-not-exist"))
    a = by["IAS-Astrophysics/athenak"]
    assert a["status"] == "ok" and a["default_branch"] == "main" and a["license_spdx"] == "BSD-3-Clause"
    head = subprocess.run(["git", "-C", str(env["work"]), "rev-parse", "main"], capture_output=True, text=True,
                          env=ENV).stdout.strip()
    assert a["commit_sha"] == head == a["remote_head_sha"] and a["commit_subject"] == "initial"
    assert {b["name"] for b in a["branches"]} == {"main", "particles_gr", "feature/nrpic-deposit"}
    clone = os.path.join(lay.raw_github, "IAS-Astrophysics__athenak")
    st = os.stat(os.path.join(clone, "src", "particles", "particles.cpp"))
    assert not st.st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    rec = json.load(open(os.path.join(lay.meta_github, "IAS-Astrophysics__athenak.json")))
    assert rec["commit_sha"] == head
    # a second run skips the present clone
    again = code_fetch.fetch_repos(lay, str(tmp / "w2"), manifest_dir=env["mdir"], repos=["IAS-Astrophysics/athenak"],
                                   log=lambda s: None)
    assert again[0]["commit_sha"] == head

    res = code_index.ingest(lay, repos=["IAS-Astrophysics/athenak"], log=lambda s: None)
    assert res[0]["status"] == "ok"
    s = res[0]["summary"]
    assert s["license_spdx"] == "BSD-3-Clause" and s["defines_parameter_input"] and s["param_reads"] == 3
    assert s["input_params"] == 4
    con = db.connect_ro(lay.db_work)
    rows = con.execute("SELECT block, name, type, default_value, line FROM params ORDER BY line").fetchall()
    assert rows == [("particles", "nparticles", "Integer", None, 5), ("particles", "tolerance", "Real", "1.0e-7", 6),
                    ("{block}", "file_type", "String", '"hst"', 8)]
    nchunks = con.execute("SELECT count(*) FROM code_chunks").fetchone()[0]
    assert nchunks > 0
    # chunks cover every line of a chunked file exactly once
    for fid, loc in con.execute("SELECT file_id, loc FROM code_files WHERE path = 'src/particles/particles.cpp'"):
        spans = sorted(con.execute("SELECT line_start, line_end FROM code_chunks WHERE file_id=?", (fid,)))
        covered = [i for a, b in spans for i in range(a, b + 1)]
        assert covered == list(range(1, loc + 1))
    con.close()
    build = os.path.join(lay.build, "code", "IAS-Astrophysics__athenak")
    assert {"files.jsonl", "symbols.jsonl", "params.jsonl", "inputs.jsonl", "summary.json"} <= set(os.listdir(build))

    hits = code_query.search(lay, "Init", db=lay.db_work)
    assert hits[0]["label"] == "particles::Particles::Init" and hits[0]["kind"] == "method" and hits[0]["line"] == 4
    hits = code_query.search(lay, "particles/tolerance", kind="param", db=lay.db_work)
    assert [(h["label"], h["line"]) for h in hits] == [("<particles> tolerance", 6)]
    hits = code_query.search(lay, "helper", repo="athenak", db=lay.db_work)
    assert hits and hits[0]["kind"] == "function"
    assert code_query.search(lay, "nosuchthingzz", db=lay.db_work) == []

    snap = code_watch.watch(lay, str(tmp / "watch"), log=lambda s: None)
    insp = snap["inspection"]
    assert set(insp) == {"main", "particles_gr", "feature/nrpic-deposit"}
    assert insp["main"]["coupling_hits"] == [] and insp["main"]["pushers"] == ["drift", "leap_frog"]
    assert len(insp["particles_gr"]["coupling_hits"]) == 1 and "tmunu" in insp["particles_gr"]["coupling_hits"][0]
    assert snap["flagged_names"] == ["feature/nrpic-deposit"]
    assert snap["added"] == [] and snap["moved"] == {}
    # the branch moves upstream: the next watch reports it and the changed file
    w = env["work"]
    git(["checkout", "-q", "feature/nrpic-deposit"], w)
    (w / "src" / "particles" / "deposit.cpp").write_text("// deposit\n")
    git(["add", "-A"], w)
    git(["commit", "-q", "-m", "deposit"], w)
    git(["push", "-q", str(tmp / "remote" / "IAS-Astrophysics" / "athenak"), "feature/nrpic-deposit"], w)
    snap2 = code_watch.watch(lay, str(tmp / "watch2"), log=lambda s: None)
    assert list(snap2["moved"]) == ["feature/nrpic-deposit"]
    assert snap2["inspection"]["feature/nrpic-deposit"]["changed_paths"] == ["src/particles/deposit.cpp"]
    assert "Something to look at" in code_watch.report_md(snap2)

    # curated links against a synthetic paper source
    src = os.path.join(lay.raw_arxiv, "2611.12831", "v1", "src")
    os.makedirs(src)
    open(os.path.join(src, "main.tex"), "w").write(
        "\\documentclass{x}\n\\begin{document}\nA\n\\begin{equation}x\\label{eq:tol}\\end{equation}\n"
        "see https://github.com/IAS-Astrophysics/athenak.\n\\end{document}\n")
    tsv = tmp / "links.tsv"
    cols = links_paper_code.COLUMNS
    good = dict(link_key="T1", paper_id="2611.12831", lines="L3-5", eq_label="eq:tol", statement="tolerance option",
                repo_id="IAS-Astrophysics/athenak", symbol="Particles::Init", path="src/particles/particles.cpp",
                params="<particles> tolerance", relation="implements", status="claimed", evidence="e", tests="-")
    bad = dict(good, link_key="T2", lines="L40-50", eq_label="eq:none", symbol="Nope", params="<particles> nope")
    tsv.write_text("\t".join(cols) + "\n" + "\n".join("\t".join(r[c] for c in cols) for r in (good, bad)) + "\n")
    rep = links_paper_code.check_links(lay, str(tsv), db=lay.db_work)
    r1, r2 = rep["links"]
    assert r1["problems"] == [] and r1["symbol"]["line_start"] == 4 and r1["params"][0]["default"] == "1.0e-7"
    assert len(r2["problems"]) == 4 and rep["n_bad"] == 1
    assert links_paper_code.load_curated(lay, str(tsv)) == 2
    assert len(links_paper_code.list_links(lay, db=lay.db_work)) == 2
    ex = links_paper_code.explicit_links(lay, ["IAS-Astrophysics/athenak"])
    assert ex == [("2611.12831", "v1", "main.tex", 5, "IAS-Astrophysics/athenak", "IAS-Astrophysics/athenak")]


def test_chunk_ranges_cover_once():
    syms = [{"kind": "function", "line_start": 10, "line_end": 400, "body": True, "doc": "a\nb"},
            {"kind": "function", "line_start": 20, "line_end": 30, "body": True, "doc": None},     # nested
            {"kind": "class", "line_start": 1, "line_end": 500, "body": True, "doc": None}]
    r = code_index.chunk_ranges(500, syms)
    covered = [i for a, b, _ in r for i in range(a, b + 1)]
    assert covered == list(range(1, 501))
    assert max(b - a + 1 for a, b, _ in r) <= code_index.CHUNK_MAX
    assert (8, 157, 0) in r                                          # doc comment of 2 lines included


@pytest.mark.parametrize("text,spdx", [
    ("This project is dual-licensed under the Unlicense and MIT licenses.", "MIT OR Unlicense"),
    ("Permission is hereby granted, free of charge, to any person", "MIT"),
    ("This software is in the public domain; it is not subject to copyright", "LicenseRef-public-domain"),
])
def test_licence_rules(text, spdx):
    assert code_index.repo_licence({"COPYING": text})[0] == spdx
    assert code_index.repo_licence({"license.txt": text})[0] == spdx       # case-insensitive file name
    assert code_index.repo_licence({}) == ("none", [])
