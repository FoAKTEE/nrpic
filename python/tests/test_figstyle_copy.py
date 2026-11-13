"""The manuscript carries its own copy of the figure style so that its scripts run from
a checkout of the manuscript alone; the two files must stay identical."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_paper_figstyle_is_the_same_file():
    a = (ROOT / "python" / "nrpic" / "figstyle.py").read_text()
    b = (ROOT / "paper" / "scripts" / "figstyle.py").read_text()
    assert a == b
