"""`kb export` prints the heading of every section, also of a section whose text begins
directly with a subsection (it owns no chunk of its own). Found by the kb lead on
2611.12831, where "3 Numerical tests" was missing from the export."""
from conftest import make_tar
from test_papers_ingest import run

PAPER = rb"""\documentclass{article}
\begin{document}
\title{A paper whose second section starts with a subsection}
\begin{abstract}
An abstract long enough to be stored as the abstract chunk of this small synthetic paper.
\end{abstract}
\section{Method}
The method is described here in a few words of plain text.
\section{Numerical tests}
\subsection{First test}
The first test is described here in a few words of plain text.
\subsection{Second test}
The second test is described here in a few words of plain text.
\end{document}
"""


def test_export_prints_parent_heading(store, monkeypatch, capsys):
    store.manifest([("2111.05282", "G01", "3")])
    store.add("2111.05282", make_tar([("main.tex", PAPER)]), "v1")
    assert run(store, ["ingest", "arxiv", "--all", "--jobs", "1"], monkeypatch) == 0
    capsys.readouterr()
    assert run(store, ["export", "--work", "2111.05282"], monkeypatch) == 0
    md = capsys.readouterr().out
    lines = [l for l in md.splitlines() if l.startswith("#")]
    assert "## 1 Method" in lines
    assert "## 2 Numerical tests" in lines
    assert lines.index("## 2 Numerical tests") < lines.index("### 2.1 First test") < lines.index("### 2.2 Second test")
