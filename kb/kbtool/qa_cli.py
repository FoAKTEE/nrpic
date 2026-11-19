"""`kb qa run` (brief 12.9, 12.10): the quality report.

    kb qa run [--out kb/QA_REPORT.md] [--json PATH] [--db PATH] [--hybrid] [--eq-sample 40]
    kb qa golden [--yaml PATH]          print (or write) the golden questions as YAML

Runs without the `kb` wiring as
    python3 -I kb/kbtool/qa_cli.py qa run ...
(hybrid retrieval needs kb/.venv: kb/.venv/bin/python -I kb/kbtool/qa_cli.py qa run --hybrid).
"""
import os
import sys

if __name__ == "__main__" and not __package__:                      # run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from kbtool import qa_cli as _self                              # noqa: E402
    sys.exit(_self.main())

import argparse  # noqa: E402
import json  # noqa: E402

from . import qa_golden as _gold  # noqa: E402
from . import qa_report as _rep  # noqa: E402
from .paths import KB_DIR, layout  # noqa: E402

CLAIMS = {"qa"}


def _atomic(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def cmd_run(a):
    lay = layout(a.data_root)
    rep = _rep.run(lay, db_path=a.db, hybrid=a.hybrid, eq_n=a.eq_sample)
    out = a.out or os.path.join(KB_DIR, "QA_REPORT.md")
    _atomic(out, _rep.markdown(rep))
    if a.json:
        _atomic(a.json, json.dumps(rep, indent=1, default=str) + "\n")
    c7 = rep["C7"]["modes"]
    print(f"QA report -> {out}" + (f"; data -> {a.json}" if a.json else ""))
    print(f"C1 counts agree: {rep['C1']['agree']}; C3 not ok: {rep['C3']['not_ok']}; C4 blocked: {rep['C4']['blocked']}; "
          f"C8 equations exact {rep['C8']['exact']}/{rep['C8']['papers']}; " +
          "; ".join(f"C7 {m} paper hits {d['paper_hits']}/{rep['C7']['questions']}, locator {d['locator_hits']}"
                    for m, d in c7.items()))
    return 0


def cmd_golden(a):
    y = _gold.golden_yaml()
    if a.yaml:
        _atomic(a.yaml, y)
        print(f"{len(_gold.QUESTIONS)} questions -> {a.yaml}")
    else:
        sys.stdout.write(y)
    return 0


def register(sub):
    p = sub.add_parser("qa", help="K9: quality report (integrity checks, golden-question retrieval, equation count)")
    qs = p.add_subparsers(dest="qa_cmd", required=True)
    s = qs.add_parser("run", help="write the quality report")
    s.add_argument("--out", help="markdown report (default kb/QA_REPORT.md)")
    s.add_argument("--json", help="also write all numbers as JSON (for the figures)")
    s.add_argument("--db", help="database (default kb.sqlite, the working database)")
    s.add_argument("--hybrid", action="store_true", help="also run the retrieval test in hybrid mode (kb/.venv)")
    s.add_argument("--eq-sample", type=int, default=40, help="papers drawn for the independent equation count")
    s.set_defaults(fn=cmd_run)
    s = qs.add_parser("golden", help="the golden questions as YAML (brief 12.2: kb/golden/questions.yaml)")
    s.add_argument("--yaml")
    s.set_defaults(fn=cmd_golden)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="kb")
    ap.add_argument("--data-root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    register(sub)
    a = ap.parse_args(argv)
    return a.fn(a)
