"""`kb ingest arxiv`, `kb resolve-bib`, `kb frontier`, `kb cites`, `kb export`, `kb show`
views and the K2-K3 counts of `kb status`, end to end on a synthetic store built with the
fetch command's own unpack."""
import gzip
import json
import os
import sqlite3

from conftest import make_tar
from kbtool import cli

PAPER_A = rb"""\documentclass[aps,prd]{revtex4-2}
\usepackage{amsmath}
\newcommand{\be}{\begin{equation}}
\newcommand{\ee}{\end{equation}}
\newcommand{\vlasov}{Vlasov}
\begin{document}
\title{Particle methods for the Einstein \vlasov{} system}
\author{A. Author}
\author{B. Author}
\begin{abstract}
We describe a particle-in-cell method for the Einstein Vlasov system and test it on collapse problems, with
second-order deposition and filtering of the stress-energy tensor in a fully dynamical spacetime.
\end{abstract}
\maketitle
\section{Introduction}\label{sec:intro}
Collisionless matter is described by the \vlasov{} equation \cite{Wu2026,East2019}. % a comment
We follow the method of Ref.~\cite{Old}.
\section{Method}\label{sec:method}
\input{method}
\begin{figure}\includegraphics[width=\columnwidth]{fig1.pdf}\caption{The cycle of the method.}\label{fig:cycle}
\end{figure}
\appendix
\section{Convergence}\label{app:conv}
\be E = m c^2 \label{eq:app} \ee
\bibliography{refs}
\end{document}
"""
METHOD = rb"""The geodesic equation reads
\begin{equation}
\frac{d u_\mu}{d t} = -\alpha u^0 \partial_\mu \alpha \label{eq:geo}
\end{equation}
and the deposition uses a cloud of order two\footnote{Triangular shaped cloud.}, see Eq.~\eqref{eq:geo}.
"""
BBL_A = rb"""\begin{thebibliography}{3}
\bibitem [{Wu(2026)}]{Wu2026} J. Wu, \Eprint {https://arxiv.org/abs/2611.12831} {arXiv:2611.12831 [gr-qc]}
\bibitem [{East(2019)}]{East2019} W. East, Phys. Rev. D (2019), arXiv:1908.05683
\bibitem [{Old(1990)}]{Old} A. Old, ``A relativistic particle code for the collapse of clusters of stars,''
  Astrophys. J. (1990).
\end{thebibliography}
"""
PAPER_B = rb"""\documentclass{article}
\begin{document}
\title{A relativistic particle code for the collapse of clusters of stars}
\begin{abstract}An older paper about a relativistic particle code used for collapse of star clusters.\end{abstract}
\section{Code}
Text citing the new method \cite{A}.
\begin{thebibliography}{1}
\bibitem{A} A. Author, arXiv:2111.05282.
\end{thebibliography}
\end{document}
"""


def build(store):
    store.manifest([("2111.05282", "G01", "3"), ("gr-qc/9703066", "G02", "2"), ("2611.12831", "G01", "3")])
    store.add("2111.05282", make_tar([("main.tex", PAPER_A), ("method.tex", METHOD), ("main.bbl", BBL_A),
                                      ("fig1.pdf", b"%PDF-1.4 fake")]), "v3")
    store.add("gr-qc/9703066", gzip.compress(PAPER_B, mtime=0), "v1")
    # write the manifest where the cli reads it
    import kbtool.papers_cli as pc
    import kbtool.cli as c
    return pc, c


def run(store, argv, monkeypatch):
    import kbtool.papers_cli as pc
    import kbtool.cli as c
    monkeypatch.setattr(pc, "kb_manifest_dir", lambda: store.mdir)
    monkeypatch.setattr(c, "kb_manifest_dir", lambda: store.mdir)
    monkeypatch.setenv("KB_NO_REEXEC", "1")
    return cli.main(["--data-root", store.data] + argv)


def test_ingest_end_to_end(store, monkeypatch, capsys):
    build(store)
    assert run(store, ["ingest", "arxiv", "--all", "--jobs", "1"], monkeypatch) == 0
    out = capsys.readouterr().out
    assert "2111.05282" in out and "gr-qc/9703066" in out
    con = sqlite3.connect(store.layout.db_work)
    p = dict(con.execute("SELECT paper_id, title FROM papers").fetchall())
    assert p["2111.05282"] == "Particle methods for the Einstein Vlasov system"
    assert p["gr-qc/9703066"].startswith("A relativistic particle code")
    row = con.execute("SELECT version, source_kind, main_tex, parse_status, grp, priority, flat_sha256 FROM papers "
                      "WHERE paper_id='2111.05282'").fetchone()
    # a short synthetic paper (under 1000 words, 2 equations) scores below the threshold: 'review'
    assert row[:6] == ("v3", "tex", "main.tex", "review", "G01", 3)
    secs = con.execute("SELECT number, title, label FROM sections WHERE paper_id='2111.05282' ORDER BY char_start"
                       ).fetchall()
    assert secs == [("1", "Introduction", "sec:intro"), ("2", "Method", "sec:method"), ("A", "Convergence", "app:conv")]
    eqs = con.execute("SELECT number, label, env, tex_norm, char_start, char_end FROM equations WHERE "
                      "paper_id='2111.05282' ORDER BY char_start").fetchall()
    assert [(e[0], e[1]) for e in eqs] == [("1", "eq:geo"), ("A1", "eq:app")]
    assert eqs[0][3] == r"\frac{du_\mu}{dt}=-\alpha u^0\partial_\mu\alpha"
    # char ranges point into flat.tex, whose sha256 is recorded
    bdir = os.path.join(store.data, "build", "tex", "2111.05282")
    flat = open(os.path.join(bdir, "flat.tex"), encoding="utf-8").read()
    assert flat[eqs[0][4]:eqs[0][5]].startswith(r"\begin{equation}") and "eq:geo" in flat[eqs[0][4]:eqs[0][5]]
    import hashlib
    assert hashlib.sha256(flat.encode()).hexdigest() == row[6]
    # source map: the equation came from method.tex line 2
    smap = json.load(open(os.path.join(bdir, "sourcemap.json")))
    import bisect
    k = bisect.bisect_right([s[0] for s in smap], eqs[0][4]) - 1
    assert smap[k][1] == "method.tex" and smap[k][2] == 2
    kinds = dict(con.execute("SELECT kind, count(*) FROM chunks WHERE paper_id='2111.05282' GROUP BY kind"))
    assert kinds["abstract"] == 1 and kinds["caption"] == 1 and kinds["footnote"] == 1 and kinds["comment"] == 1
    assert kinds.get("appendix", 0) >= 1
    body = " ".join(t for (t,) in con.execute("SELECT text FROM chunks WHERE paper_id='2111.05282' AND kind='body'"))
    assert "Vlasov equation [cit.]" in body and "Eq. (1)" in body and "Triangular" not in body
    fig = con.execute("SELECT kind, number, label, caption, files_json FROM figures").fetchone()
    assert fig == ("figure", "1", "fig:cycle", "The cycle of the method.", '["fig1.pdf"]')
    # full-text search works on chunks and equations
    hits = con.execute("SELECT c.paper_id FROM chunks_fts f JOIN chunks c ON c.chunk_id=f.rowid "
                       "WHERE chunks_fts MATCH 'deposition'").fetchall()
    assert ("2111.05282",) in hits
    assert con.execute("SELECT count(*) FROM equations_fts WHERE equations_fts MATCH 'geodesic'").fetchone()[0] == 1
    # bibliography and citations
    bib = con.execute("SELECT cite_key, target_arxiv, resolved_by, source FROM bib_entries WHERE paper_id="
                      "'2111.05282' ORDER BY bib_id").fetchall()
    assert bib == [("Wu2026", "2611.12831", "arxiv-id", "bbl"), ("East2019", "1908.05683", "arxiv-id", "bbl"),
                   ("Old", "gr-qc/9703066", "title-fuzzy-corpus", "bbl")]
    cits = con.execute("SELECT cite_key, cited_arxiv, in_corpus, context FROM citations WHERE citing='2111.05282' "
                       "ORDER BY char_start, cite_key").fetchall()
    assert [(c[0], c[1], c[2]) for c in cits] == [("East2019", "1908.05683", 0), ("Wu2026", "2611.12831", 0),
                                                  ("Old", "gr-qc/9703066", 1)]
    assert cits[0][3] == "Collisionless matter is described by the Vlasov equation [cit.]."
    back = con.execute("SELECT citing, cited_arxiv, in_corpus FROM citations WHERE citing='gr-qc/9703066'").fetchall()
    assert back == [("gr-qc/9703066", "2111.05282", 1)]
    con.close()

    # re-ingest: same counts, no duplicate rows
    assert run(store, ["ingest", "arxiv", "--id", "2111.05282", "--jobs", "1"], monkeypatch) == 0
    con = sqlite3.connect(store.layout.db_work)
    assert con.execute("SELECT count(*) FROM equations").fetchone()[0] == 2
    assert con.execute("SELECT count(*) FROM bib_entries").fetchone()[0] == 4
    assert con.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'deposition'").fetchone()[0] == \
        con.execute("SELECT count(*) FROM chunks WHERE text LIKE '%deposition%'").fetchone()[0]
    con.close()
    capsys.readouterr()

    # frontier, cites, export, show, status
    assert run(store, ["frontier", "--work", "--json"], monkeypatch) == 0
    fr = json.loads(capsys.readouterr().out)
    assert {r["arxiv"] for r in fr} == {"2611.12831", "1908.05683"}
    assert [r["in_manifest"] for r in fr if r["arxiv"] == "2611.12831"] == [True]
    assert run(store, ["cites", "--work", "gr-qc/9703066", "--in", "--context"], monkeypatch) == 0
    inc = json.loads(capsys.readouterr().out)
    assert [r["citing"] for r in inc] == ["2111.05282"] and inc[0]["context"] == "We follow the method of Ref. [cit.]."
    assert run(store, ["export", "--work", "2111.05282"], monkeypatch) == 0
    md = capsys.readouterr().out
    assert md.startswith("# Particle methods") and "## 1 Introduction" in md and "## A Convergence" in md
    assert run(store, ["show", "2111.05282", "--eq", "eq:geo"], monkeypatch) in (0, 1)
    capsys.readouterr()
    assert run(store, ["status", "--json"], monkeypatch) == 0
    st = json.loads(capsys.readouterr().out)
    assert st["papers_by_parse_status"].get("ok", 0) + st["papers_by_parse_status"].get("review", 0) == 2
    assert st["bib"]["bib_entries"] == 4 and st["bib_resolution_rate"] == 1.0
    assert st["edges_in_corpus_fraction"] == 0.5


def test_ingest_skips_unverified_download(store, monkeypatch, capsys):
    store.manifest([("2111.05282", "G01", "3")])
    vdir = store.add("2111.05282", make_tar([("main.tex", PAPER_A)]), "v1")
    with open(os.path.join(vdir, "src", "planted.tex"), "w") as f:     # tree differs from the archive
        f.write("x")
    assert run(store, ["ingest", "arxiv", "--all", "--jobs", "1"], monkeypatch) == 0
    assert "download-problem" in capsys.readouterr().out
    con = sqlite3.connect(store.layout.db_work)
    assert con.execute("SELECT count(*) FROM papers").fetchone()[0] == 0
