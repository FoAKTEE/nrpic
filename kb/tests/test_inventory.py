"""T3: verify-downloads on a synthetic store laid out exactly as the fetch command writes it."""
import gzip
import os
import subprocess

from conftest import TEX, make_tar
from kbtool import inventory as inv

ROWS = [("2611.12831", "G01", "3"), ("2111.05282", "G01", "3"), ("gr-qc/9804040", "G02", "2"),
        ("1109.0546", "G01", "2"), ("2504.15978", "G01", "1"), ("2409.16053", "G01", "2"),
        ("2409.10383", "G01", "2"), ("0912.2920", "G01", "2"), ("1212.2901", "G01", "1"),
        ("1106.2254", "G01", "1"), ("2404.01137", "G01", "1"), ("2505.15912", "G01", "1")]
REPOS = [("IAS-Astrophysics/athenak", "core", "all", "AthenaK"), ("kokkos/kokkos", "dep", "all", "Kokkos")]


def by_id(result):
    return {p["id"]: p for p in result["papers"] + result["extras"]}


def build(store):
    store.manifest(ROWS, REPOS)
    good = make_tar([("main.tex", TEX), ("figs/f1.pdf", b"%PDF-1.4 fig")])
    store.add("2611.12831", good, "v1")                                     # ok, tar
    store.add("gr-qc/9804040", gzip.compress(TEX), "v2")                     # ok, single gzip TeX, old-style id
    store.add("1109.0546", b"%PDF-1.4 only", "v3")                           # ok, pdf
    store.failed("2111.05282")                                               # failed
    store.add("2409.16053", good, "v1", record=False)                        # incomplete: no record
    vd = store.add("2409.10383", good, "v2")                                 # sha mismatch
    with open(os.path.join(vd, "source.bin"), "ab") as f:
        f.write(b"\0")
    store.add("0912.2920", b"<!DOCTYPE html><html>slow down</html>", "v1")   # html stored as e-print
    vd = store.add("1212.2901", good, "v1")                                  # planted file + removed member
    with open(os.path.join(vd, "src", "planted.tex"), "wb") as f:
        f.write(b"x")
    os.remove(os.path.join(vd, "src", "figs", "f1.pdf"))
    vd = store.add("1106.2254", good, "v1")                                  # symlink inside src
    os.symlink("/etc/passwd", os.path.join(vd, "src", "pw"))
    store.add("2404.01137", good, "vX")                                      # version unknown
    store.add("2505.15912", good, "v1", disp='attachment; filename="arXiv-2505.15913v1.tar.gz"')  # wrong id
    store.add("2306.11810", good, "v2")                                      # extra (not in manifest)
    store.add("gr-qc/0606037", gzip.compress(TEX), "v2")                     # extra, old style


def test_classification(store):
    build(store)
    r = inv.verify(store.layout, store.mdir)
    p = by_id(r)
    assert p["2611.12831"]["status"] == "ok"
    assert p["2611.12831"]["sniffed_kind"] == "gzip-tar" and p["2611.12831"]["source_kind"] == "tex"
    assert p["2611.12831"]["version"] == "v1" and p["2611.12831"]["version_source"] == "content-disposition"
    assert p["gr-qc/9804040"]["status"] == "ok" and p["gr-qc/9804040"]["sniffed_kind"] == "gzip-tex"
    assert p["1109.0546"]["status"] == "ok" and p["1109.0546"]["source_kind"] == "pdf"
    assert p["2111.05282"]["status"] == "failed"
    assert p["2504.15978"]["status"] == "missing"
    assert p["2409.16053"]["status"] == "incomplete"
    assert any("sha256" in x for x in p["2409.10383"]["problems"])
    assert any("not an e-print" in x for x in p["0912.2920"]["problems"])
    probs = " ".join(p["1212.2901"]["problems"])
    assert "not in the archive" in probs and "not extracted" in probs
    assert any("symlink" in x for x in p["1106.2254"]["problems"])
    assert any("version unknown" in x for x in p["2404.01137"]["problems"])
    assert any("Content-Disposition names" in x for x in p["2505.15912"]["problems"])
    for k in ("2409.10383", "0912.2920", "1212.2901", "1106.2254", "2404.01137", "2505.15912"):
        assert p[k]["status"] == "problem", k
    extras = {e["id"]: e for e in r["extras"]}
    assert set(extras) == {"2306.11810", "gr-qc/0606037"}
    assert all(e["status"] == "ok" and not e["in_manifest"] for e in extras.values())
    assert r["arxiv"]["status"] == {"ok": 3, "failed": 1, "missing": 1, "incomplete": 1, "problem": 6}
    assert r["arxiv"]["by_priority"]["3"] == {"ok": 1, "failed": 1}
    assert {x["repo"]: x["status"] for x in r["repos"]} == {"IAS-Astrophysics/athenak": "missing",
                                                          "kokkos/kokkos": "missing"}


def test_missing_ids_for_fetch(store):
    build(store)
    r = inv.verify(store.layout, store.mdir)
    assert inv.missing_ids(r, priority=3) == ["2111.05282"]
    assert inv.missing_ids(r, priority=3, include_failed=False) == []
    assert inv.missing_ids(r, priority=1) == ["2504.15978"]


def test_unsafe_members_refused_by_the_fetch_are_noted(store):
    store.manifest([("2611.12831", "G01", "3")])
    import tarfile
    blob = make_tar([("main.tex", TEX), ("../evil.tex", b"e"), ("ln", tarfile.SYMTYPE, "/etc/passwd")])
    store.add("2611.12831", blob, "v1")
    p = by_id(inv.verify(store.layout, store.mdir))["2611.12831"]
    assert p["status"] == "ok"
    assert sorted(p["refused_members"]) == ["../evil.tex", "ln"]
    assert any("unsafe archive members refused" in x for x in p["notes"])
    assert not os.path.exists(os.path.join(store.data, "raw", "arxiv", "2611.12831", "v1", "evil.tex"))


def test_retry_directories_follow_the_record(store):
    store.manifest([("2611.12831", "G01", "3")])
    good = make_tar([("main.tex", TEX)])
    store.add("2611.12831", good, "v1")
    store.add("2611.12831", good, "v1.retry1")
    p = by_id(inv.verify(store.layout, store.mdir))["2611.12831"]
    assert p["current"] == "v1.retry1" and p["version"] == "v1" and p["status"] == "ok"
    assert any("2 version directories" in x for x in p["notes"])


def test_sha256sums_verify_with_coreutils(store):
    build(store)
    r = inv.verify(store.layout, store.mdir)
    lines = inv.sha256sums(r, store.data)
    path = os.path.join(store.data, "SUMS")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    out = subprocess.run(["sha256sum", "-c", path], cwd=store.data, capture_output=True, text=True)
    # the sums are recomputed from the bytes on disk: every line verifies, one line per stored e-print
    assert out.returncode == 0, out.stdout + out.stderr
    assert len(lines) == 12 and all(l.endswith("/source.bin") for l in lines)
    # while the tampered entry's sum is not the one its download record holds
    p = by_id(r)["2409.10383"]
    import json
    rec = json.load(open(os.path.join(store.data, "meta", "arxiv", "2409.10383.json")))
    assert p["sha256"] != rec["sha256"]


def test_report_has_no_paper_text(store):
    build(store)
    md = inv.report_md(inv.verify(store.layout, store.mdir))
    assert "\\documentclass" not in md and "slow down" not in md
    assert "| 2611.12831 | G01 | 3 | v1 |" in md


def test_repo_checkout_read_without_git(store, tmp_path):
    store.manifest([], REPOS)
    repo = os.path.join(store.data, "raw", "github", "IAS-Astrophysics__athenak")
    os.makedirs(os.path.join(repo, ".git", "refs", "heads"))
    sha = "c5a0d7f" + "0" * 33
    with open(os.path.join(repo, ".git", "HEAD"), "w") as f:
        f.write("ref: refs/heads/main\n")
    with open(os.path.join(repo, ".git", "packed-refs"), "w") as f:
        f.write(f"# pack-refs with: peeled\n{sha} refs/heads/main\n")
    with open(os.path.join(repo, "LICENSE"), "w") as f:
        f.write("Redistribution and use in source and binary forms, with or without modification ...\n"
                "Neither the name of the copyright holder nor the names of its contributors ...\n")
    r = {x["repo"]: x for x in inv.verify(store.layout, store.mdir)["repos"]}
    a = r["IAS-Astrophysics/athenak"]
    assert a["commit_sha"] == sha and a["license_spdx_guess"] == "BSD-3-Clause"
    assert a["status"] == "incomplete"          # no meta/github record yet
    assert r["kokkos/kokkos"]["status"] == "missing"
