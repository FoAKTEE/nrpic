"""K2 steps 1-3: comments, main file, flattening with a source map, path safety."""
import json
import os

import pytest

from kbtool import tex_files as F


def write(root, rel, text, mode="w"):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode) as f:
        f.write(text)
    return p


def body(text):
    return F.strip_comments_text(text)


def test_comment_semantics():
    assert body("a % c\nb\n") == "a b\n"                 # % removes the end of line too
    assert body("50\\% of x\n") == "50\\% of x\n"          # escaped percent
    assert body("a\\\\% c\nb") == "a\\\\b"                 # \\ then a comment
    assert body("\\verb|%x| y % z\n") == "\\verb|%x| y "
    assert body("% whole line\nnext\n") == "next\n"
    pieces, comments = F.strip_comments("x % note\n")
    assert comments == [(1, " note")]


def test_comment_blocks_and_verbatim():
    t = "a\n\\begin{comment}\nhidden \\input{x}\n\\end{comment}\nb\n\\iffalse\nold \\ifx a b \\fi text\n\\fi\nc\n"
    out = body(t)
    assert "hidden" not in out and "old" not in out
    assert out.split() == ["a", "b", "c"]
    v = "\\begin{verbatim}\n50% kept\n\\end{verbatim}\n"
    assert "50% kept" in body(v)


def test_safe_join_refuses_escapes(tmp_path):
    root = str(tmp_path / "src")
    write(root, "a.tex", "x")
    write(str(tmp_path), "outside.tex", "secret")
    os.symlink(os.path.join(root, "a.tex"), os.path.join(root, "link.tex"))
    assert F.safe_join(root, "a.tex")
    for bad in ("../outside.tex", "/etc/passwd", "link.tex", "~/x", "sub/../../outside.tex", "a.tex#1"):
        assert F.safe_join(root, bad) is None, bad


def test_flatten_inputs_and_source_map(tmp_path):
    root = str(tmp_path)
    write(root, "main.tex", "\\documentclass{article}\n\\begin{document}\nA\\input{sec/one}B\n"
                            "\\include{two}\n\\input three.tex\n\\import{parts/}{four}\n"
                            "\\input{../escape}\n\\input{missing}\n% \\input{commented}\n\\end{document}\n")
    write(root, "sec/one.tex", "ONE % c1\n")
    write(root, "two.tex", "TWO\n")
    write(root, "three.tex", "THREE\n")
    write(root, "parts/four.tex", "FOUR \\input{five}\n")
    write(root, "parts/five.tex", "FIVE\n")
    write(root, "commented.tex", "NEVER\n")
    write(str(tmp_path.parent), "escape.tex", "ESCAPED\n")
    fl = F.flatten(root, "main.tex")
    flat = fl["flat"]
    for w in ("ONE", "TWO", "THREE", "FOUR", "FIVE"):
        assert w in flat
    assert "NEVER" not in flat and "ESCAPED" not in flat
    assert {u["name"] for u in fl["unresolved"]} == {"../escape", "missing"}
    loc = fl["source_map"].locate(flat.index("FIVE"))
    assert loc["file"] == "parts/five.tex" and loc["line"] == 1 and loc["col"] == 0
    loc = fl["source_map"].locate(flat.index("B\n"))
    assert loc["file"] == "main.tex" and loc["line"] == 3
    assert any(c["file"] == "sec/one.tex" and c["text"] == " c1" for c in fl["comments"])


def test_flatten_cycle_and_depth(tmp_path):
    root = str(tmp_path)
    write(root, "main.tex", "\\documentclass{article}\\begin{document}\\input{a}\\end{document}")
    write(root, "a.tex", "A \\input{b}")
    write(root, "b.tex", "B \\input{a}")
    fl = F.flatten(root, "main.tex")
    assert fl["flat"].count("A ") == 1 and any("cycle" in n for n in fl["notes"])


def test_input_inside_definition_not_expanded(tmp_path):
    root = str(tmp_path)
    write(root, "main.tex", "\\newcommand{\\inc}[1]{\\input{#1}}\\begin{document}x\\end{document}")
    fl = F.flatten(root, "main.tex")
    assert "\\input{#1}" in fl["flat"] and not fl["unresolved"]


def test_find_main_variants(tmp_path):
    r1 = str(tmp_path / "one")
    write(r1, "paper.tex", "\\documentclass{revtex4-2}\n\\begin{document}\nx\\end{document}")
    write(r1, "macros.tex", "\\newcommand{\\x}{y}")
    assert F.find_main(r1)["main"] == "paper.tex"
    # 00README.json names the top-level file
    r2 = str(tmp_path / "two")
    write(r2, "a.tex", "\\documentclass{article}\\begin{document}a\\end{document}" + " " * 500)
    write(r2, "b.tex", "\\documentclass{article}\\begin{document}b\\end{document}")
    write(r2, "00README.json", json.dumps({"sources": [{"usage": "toplevel", "filename": "b.tex"}]}))
    assert F.find_main(r2) == {"main": "b.tex", "candidates": ["a.tex", "b.tex"], "reason": "00README toplevel",
                               "notes": []}
    # two candidates, one \input by the other (a supplement compiled inside the main file)
    r3 = str(tmp_path / "three")
    write(r3, "main.tex", "\\documentclass{article}\\begin{document}\\input{supp}\\end{document}")
    write(r3, "supp.tex", "\\documentclass{article}\\begin{document}" + "s" * 5000 + "\\end{document}")
    assert F.find_main(r3)["main"] == "main.tex"
    # commented-out documentclass does not count
    r4 = str(tmp_path / "four")
    write(r4, "old.tex", "%\\documentclass{article}\n%\\begin{document}\n")
    write(r4, "new.tex", "\\documentstyle[aps]{revtex}\n\\begin{document}\nx\n\\end{document}\n")
    assert F.find_main(r4)["main"] == "new.tex"
    # no LaTeX main file: largest .tex
    r5 = str(tmp_path / "five")
    write(r5, "x.tex", "plain tex \\bye")
    m = F.find_main(r5)
    assert m["main"] == "x.tex" and m["notes"]


def test_latin1_file(tmp_path):
    root = str(tmp_path)
    write(root, "main.tex", "\\begin{document}caf\xe9\\end{document}".encode("latin-1"), mode="wb")
    fl = F.flatten(root, "main.tex")
    assert "caf\xe9" in fl["flat"] and fl["files"][0]["encoding"] == "latin-1"


def test_file_size_limit(tmp_path, monkeypatch):
    root = str(tmp_path)
    write(root, "main.tex", "\\begin{document}\\input{big}\\end{document}")
    write(root, "big.tex", "x" * 2000)
    monkeypatch.setattr(F, "MAX_FILE_BYTES", 1000)
    with pytest.raises(OSError):
        F.flatten(root, "main.tex")
