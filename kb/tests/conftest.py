"""Fixtures: a synthetic kb-data store laid out exactly as harness/bin/nrpic-fetch-arxiv
writes it (its extraction functions are loaded from this worktree's copy of the harness,
which is this repository's code at the tested commit), with its own writer lock, so no test
touches the real kb-data."""
import gzip
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tarfile
import time

import pytest

KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KB_DIR)

from kbtool import paths  # noqa: E402

# The worktree's own copy (kb/ sits at the repository root), not the main checkout's: the
# fixture must match the code of the commit under test, whatever NRPIC_HOME says.
FETCH = os.path.join(os.path.dirname(KB_DIR), "harness", "bin", "nrpic-fetch-arxiv")


def load_fetch_module():
    loader = importlib.machinery.SourceFileLoader("nrpic_fetch_arxiv", FETCH)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


FETCHMOD = load_fetch_module()


def fetch_unpack(blob, dest):
    """Extract an e-print into dest (new) as the fetch command does; returns (kind, skipped).

    The command of wave 1 had `unpack(blob, dest)`; main's f9ab6c7 replaced it by
    `check_eprint` + `safe_extract` inside `fetch_source`. This mirrors fetch_source's
    layout: pdf -> src/paper.pdf, tar -> safe extraction, otherwise src/main.tex. A blob the
    new command refuses (HTML, empty) is stored as main.tex, as the wave-1 command stored it,
    so tests of old store entries keep their meaning."""
    if hasattr(FETCHMOD, "unpack"):
        return FETCHMOD.unpack(blob, dest)
    os.makedirs(dest)
    try:
        kind, data, _content = FETCHMOD.check_eprint(blob)
    except FETCHMOD.Refused:
        data = gzip.decompress(blob) if blob[:2] == b"\x1f\x8b" else blob
        with open(os.path.join(dest, "main.tex"), "wb") as f:
            f.write(data)
        return "single-file", []
    if kind == "pdf":
        with open(os.path.join(dest, "paper.pdf"), "wb") as f:
            f.write(data)
        return "pdf", []
    if kind == "tar":
        skipped, oversize, _has_tex = FETCHMOD.safe_extract(data, dest)
        return "tar", skipped + oversize
    with open(os.path.join(dest, "main.tex"), "wb") as f:
        f.write(data)
    return "single-file", []

TEX = b"\\documentclass{revtex4-2}\n\\begin{document}\n\\title{T}\n\\section{A}\nx\n\\end{document}\n"


def make_tar(members, gz=True):
    """members: list of (name, bytes) for files or (name, TarInfo-type, linkname)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        for m in members:
            if len(m) == 2:
                name, data = m
                ti = tarfile.TarInfo(name)
                ti.size = len(data)
                ti.mtime = 0
                t.addfile(ti, io.BytesIO(data))
            else:
                name, typ, link = m
                ti = tarfile.TarInfo(name)
                ti.type = typ
                ti.linkname = link
                t.addfile(ti)
    raw = buf.getvalue()
    return gzip.compress(raw, mtime=0) if gz else raw


def disposition(aid, version, ext=".tar.gz"):
    return f'attachment; filename="arXiv-{aid.replace("/", "")}{version}{ext}"'


class Store:
    def __init__(self, root):
        self.home = os.path.join(root, "home")
        self.data = os.path.join(self.home, "kb-data")
        self.lock = os.path.join(self.home, "locks", "kb-writer.lock")
        os.makedirs(os.path.join(self.data, "raw", "arxiv"))
        os.makedirs(os.path.join(self.data, "meta", "arxiv"))
        self.mdir = os.path.join(root, "manifests")
        os.makedirs(self.mdir)
        self.layout = paths.Layout(home=self.home, data=self.data, lock=self.lock)

    def manifest(self, arxiv_rows, github_rows=()):
        with open(os.path.join(self.mdir, "arxiv.tsv"), "w") as f:
            for r in arxiv_rows:
                f.write("\t".join(r) + "\n")
        with open(os.path.join(self.mdir, "github.tsv"), "w") as f:
            for r in github_rows:
                f.write("\t".join(r) + "\n")

    def add(self, aid, blob, version="v1", record=True, disp=None, status="ok"):
        """Store one e-print as the fetch command does; returns the version directory."""
        key = aid.replace("/", "_")
        vdir = os.path.join(self.data, "raw", "arxiv", key, version)
        os.makedirs(vdir)
        with open(os.path.join(vdir, "source.bin"), "wb") as f:
            f.write(blob)
        kind, skipped = fetch_unpack(blob, os.path.join(vdir, "src"))
        if record:
            v = version.split(".")[0]           # the fetch records "v1" for a directory "v1.retry1"
            rec = {"id": aid, "status": status, "url": "https://arxiv.org/e-print/" + aid, "version": v,
                   "kind": kind, "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
                   "content_disposition": disposition(aid, v) if disp is None else disp,
                   "skipped_members": skipped, "source": os.path.join(vdir, "source.bin"),
                   "src": os.path.join(vdir, "src"),
                   "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            self.record(aid, rec)
        return vdir

    def record(self, aid, rec):
        with open(os.path.join(self.data, "meta", "arxiv", aid.replace("/", "_") + ".json"), "w") as f:
            json.dump(rec, f)

    def failed(self, aid):
        self.record(aid, {"id": aid, "status": "failed", "url": "https://arxiv.org/e-print/" + aid,
                          "error": "HTTPError(404)", "tried_utc": "2026-11-15T00:00:00Z"})


@pytest.fixture
def store(tmp_path, monkeypatch):
    s = Store(str(tmp_path))
    monkeypatch.setenv("KB_DATA_ROOT", s.data)
    monkeypatch.setenv("KB_LOCK", s.lock)
    monkeypatch.setenv("NRPIC_HOME", s.home)
    paths.nrpic_home.cache_clear()
    yield s
    paths.nrpic_home.cache_clear()
