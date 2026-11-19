"""T2: file type from content, safe extraction."""
import gzip
import os
import tarfile

import pytest

from conftest import TEX, make_tar
from kbtool import sniff


@pytest.mark.parametrize("blob,kind,sk", [
    (make_tar([("main.tex", TEX), ("fig.pdf", b"%PDF-1.4 x")]), "gzip-tar", "tex"),
    (make_tar([("main.tex", TEX)], gz=False), "tar", "tex"),
    (make_tar([("only.pdf", b"%PDF-1.4")]), "gzip-tar", "pdf"),
    (make_tar([("README", b"hello")]), "gzip-tar", "none"),
    (gzip.compress(TEX), "gzip-tex", "tex"),
    (gzip.compress(b"%PDF-1.5 stuff"), "gzip-pdf", "pdf"),
    (b"%PDF-1.7\n...", "pdf", "pdf"),
    (TEX, "tex", "tex"),
    (b"<!DOCTYPE html><html><body>rate limited</body></html>", "html", "none"),
    (gzip.compress(b"\x00\x01binary"), "gzip-other", "none"),
    (b"", "empty", "none"),
    (b"\x00\x01\x02 garbage", "unknown", "none"),
])
def test_kind_from_content(blob, kind, sk):
    k, data = sniff.sniff(blob)
    assert k == kind
    members = sniff.tar_members(data) if k in ("gzip-tar", "tar") else None
    assert sniff.source_kind(k, members) == sk


def test_gzip_bomb_is_bounded():
    blob = gzip.compress(b"\0" * (4 << 20))
    with pytest.raises(sniff.TooLarge):
        sniff.gunzip_bounded(blob, limit=1 << 20)
    assert len(sniff.gunzip_bounded(blob, limit=8 << 20)) == 4 << 20


def test_concatenated_gzip_members():
    blob = gzip.compress(b"\\documentclass{a}") + gzip.compress(b"\\begin{document}")
    assert sniff.gunzip_bounded(blob) == b"\\documentclass{a}\\begin{document}"


def _unsafe_archive():
    return make_tar([
        ("ok/main.tex", TEX),
        ("/etc/abs.tex", b"abs"),
        ("../up.tex", b"up"),
        ("a/../../up2.tex", b"up2"),
        ("link", tarfile.SYMTYPE, "/etc/passwd"),
        ("hard", tarfile.LNKTYPE, "ok/main.tex"),
        ("dev", tarfile.CHRTYPE, ""),
        ("fifo", tarfile.FIFOTYPE, ""),
    ])


def test_safe_extract_refuses_unsafe_members(tmp_path):
    dest = tmp_path / "src"
    kind, skipped = sniff.safe_extract(_unsafe_archive(), str(dest))
    assert kind == "gzip-tar"
    reasons = dict(skipped)
    assert reasons["/etc/abs.tex"] == "absolute path"
    assert reasons["../up.tex"] == "parent reference"
    assert reasons["a/../../up2.tex"] == "parent reference"
    for n in ("link", "hard", "dev", "fifo"):
        assert reasons[n].startswith("not a regular file")
    on_disk = sorted(os.path.relpath(os.path.join(d, f), dest) for d, _, fs in os.walk(dest) for f in fs)
    assert on_disk == ["ok/main.tex"]
    assert not (tmp_path / "up.tex").exists() and not (tmp_path / "up2.tex").exists()
    scan = sniff.scan_tree(str(dest))
    assert scan["problems"] == [] and scan["files"] == 1


def test_safe_extract_size_limits(tmp_path, monkeypatch):
    monkeypatch.setattr(sniff, "MAX_FILE", 100)
    monkeypatch.setattr(sniff, "MAX_TOTAL", 150)
    blob = make_tar([("a.tex", b"x" * 90), ("big.tex", b"y" * 200), ("b.tex", b"z" * 90)])
    kind, skipped = sniff.safe_extract(blob, str(tmp_path / "src"))
    reasons = dict(skipped)
    assert reasons["big.tex"].startswith("file larger")
    assert reasons["b.tex"].startswith("total beyond")
    assert os.listdir(tmp_path / "src") == ["a.tex"]


def test_safe_extract_never_writes_into_existing_dir(tmp_path):
    (tmp_path / "src").mkdir()
    with pytest.raises(FileExistsError):
        sniff.safe_extract(make_tar([("a.tex", TEX)]), str(tmp_path / "src"))


def test_scan_tree_flags_links_and_exec_bits(tmp_path):
    root = tmp_path / "src"
    root.mkdir()
    (root / "a.tex").write_bytes(TEX)
    (root / "run.sh").write_bytes(b"#!/bin/sh\n")
    os.chmod(root / "run.sh", 0o755)
    os.symlink("/etc/passwd", root / "pw")
    os.symlink(str(tmp_path), root / "up")
    probs = dict(sniff.scan_tree(str(root))["problems"])
    assert probs["pw"] == "symlink"
    assert probs["up"] == "symlink (directory)"
    assert probs["run.sh"] == "executable bit set"
