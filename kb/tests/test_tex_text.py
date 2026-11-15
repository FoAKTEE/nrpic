"""K2 steps 4, 6, 7: macros, plain text, sentences, chunks, equation normalisation."""
import pytest

from kbtool import tex_macros as M
from kbtool import tex_structure as S
from kbtool import tex_text as T


def test_macro_collection_and_expansion():
    pre = (r"\newcommand{\be}{\begin{equation}}\newcommand\ee{\end{equation}}"
           r"\newcommand{\vect}[1]{\mathbf{#1}}\newcommand{\pd}[2][t]{\partial_{#1} #2}"
           r"\def\half{\frac{1}{2}}\def\pair#1#2{(#1,#2)}\DeclareMathOperator{\Tr}{Tr}"
           r"\providecommand{\vect}[1]{WRONG}\renewcommand{\half}{\tfrac12}")
    mac = M.collect(pre)
    assert mac["vect"]["nargs"] == 1 and mac["pd"]["default"] == "t" and mac["pair"]["nargs"] == 2
    assert mac["half"]["body"] == r"\tfrac12"                      # \renewcommand overrides
    assert mac["vect"]["body"] == r"\mathbf{#1}"                   # \providecommand does not
    out, st = M.expand(r"\vect{v} + \pd{f} + \pd[x]{g} + \pair{a}{b} + \Tr A + \half", mac)
    # the space after a zero-argument macro is kept (TeX would drop it; text reads better with it)
    assert out == r"\mathbf{v} + \partial_{t} f + \partial_{x} g + (a,b) + \operatorname{Tr} A + \tfrac12"
    assert M.env_aliases(mac) == {"be": r"\begin{equation}", "ee": r"\end{equation}"}


def test_recursive_macro_is_bounded():
    mac = M.collect(r"\newcommand{\loop}{x\loop}")
    out, st = M.expand(r"\loop", mac)
    assert st["depth"] == M.MAX_DEPTH or st["truncated"]
    assert len(out) < 1000


def test_aliased_equations_are_found():
    doc = (r"\newcommand{\be}{\begin{equation}}\newcommand{\ee}{\end{equation}}"
           r"\begin{document}\section{A} text \be a=b \label{e1}\ee more $x$ and $$y$$ \end{document}")
    st = S.extract(doc)
    assert [(e["env"], e["number"], e["labels"]) for e in st["equations"]] == [("equation", "1", ["e1"]),
                                                                                ("$$", None, [])]


def test_dollar_and_escaped_dollar():
    st = S.extract(r"\begin{document}costs \$5 and $a$ then \[ b \] \end{document}")
    assert [e["env"] for e in st["equations"]] == ["\\["]


def test_to_text_refs_and_cites():
    labels = {"eq:x": {"number": "3"}, "sec:a": {"number": "2.1"}}
    t = T.to_text(r"As shown in Eq.~\eqref{eq:x} of Sec.~\ref{sec:a} \cite{a,b}, \emph{this} holds.", labels)
    assert t == "As shown in Eq. (3) of Sec. 2.1 [cit.], this holds."


def test_sentences():
    s = T.sentences("We use Eq. (3) of Smith et al. here. Then we stop! A. B. Author wrote it. Last one")
    assert s == ["We use Eq. (3) of Smith et al. here.", "Then we stop!", "A. B. Author wrote it.", "Last one"]


def test_normalize_equation():
    mac = M.collect(r"\newcommand{\dd}{\mathrm{d}}")
    n = T.normalize_equation(r"\begin{align} \dd x &= \dfrac{1}{2}\, \left( a + b \right) \label{q} \nonumber\\"
                             r" y &= \alpha\beta \quad z, \end{align}", mac)
    assert n == r"\mathrm{d}x=\frac{1}{2}(a+b)y=\alpha\beta z"
    assert T.symbols(n) == ["\\alpha", "\\beta", "\\mathrm{d}", "a", "b", "x", "y", "z"]


def test_chunks_respect_targets_and_equations():
    sent = "This is a sentence with exactly ten words in it. "
    para = sent * 12                                            # 120 words
    eq = "\\begin{equation} " + " + ".join(f"x_{k}" for k in range(50)) + " \\end{equation}"
    text = "\n\n".join([para, para + eq + " " + para, para, para * 4, para])
    prot = [(text.index(eq), text.index(eq) + len(eq))]
    chunks = T.chunk_section(text, 0, len(text), prot, lambda t: T.to_text(t))
    sizes = [c["n_tokens"] for c in chunks]
    assert all(s <= T.TARGET_MAX + 120 for s in sizes), sizes        # one unit may overshoot
    assert all(s >= T.TARGET_MIN // 2 for s in sizes[:-1]), sizes
    for c in chunks:                                                  # never inside the equation
        assert not (prot[0][0] < c["start"] < prot[0][1]) and not (prot[0][0] < c["end"] < prot[0][1])
    # overlap: consecutive chunks share text, about 15 % of the target
    shared = [max(0, chunks[k]["end"] - chunks[k + 1]["start"]) for k in range(len(chunks) - 1)]
    assert any(x > 0 for x in shared)
    covered = set()
    for c in chunks:
        covered |= set(range(c["start"], c["end"]))
    assert len(covered) >= 0.95 * len(text.strip())


def test_split_lines_nested():
    inner = r"a &= \begin{cases} 1 \\ 2 \end{cases} \\[3pt] b &= {x \\ y} \\* c"
    parts = [inner[a:b].strip() for a, b in S.split_lines(inner)]
    assert parts == [r"a &= \begin{cases} 1 \\ 2 \end{cases}", r"b &= {x \\ y}", "c"]
