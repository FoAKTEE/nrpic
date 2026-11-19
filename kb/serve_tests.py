"""Tests of kb/serve_locate.py (standard library only):  python3 -I kb/serve_tests.py

They use synthetic inputs only; nothing under kb-data is read or written.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import serve_locate as S  # noqa: E402


class Lines(unittest.TestCase):
    def test_ranges(self):
        self.assertEqual(S.parse_lines("491"), [[491, 491]])
        self.assertEqual(S.parse_lines("667-673, 680-692"), [[667, 673], [680, 692]])
        self.assertEqual(S.parse_lines("1101-03"), [[1101, 1103]])
        with self.assertRaises(ValueError):
            S.parse_lines("abc")


class Numbers(unittest.TestCase):
    def test_claim_numbers_skip_locators_ids_runs_small_ints(self):
        t = ("C = 1.41053e-2 for M/R = 1.141e-2 at main.tex:491 (run C-sidm-20261115-120722-38ab057), "
             "see 2108.11967 and gr-qc/0601112; N = 3, L1101-1103, 580 t_0")
        vals = sorted(round(v, 9) for v, _, _ in S.claim_numbers(t))
        self.assertEqual(vals, [0.01141, 0.0141053, 580.0])

    def test_source_numbers_forms(self):
        tex = r"$1.41053\times10^{-2}$, $19\%$, \mu\geq0.05, $\sim 10^{-3}$, 2.5e-4, 1{,}5"
        pool = S.source_numbers(tex)
        for v in (0.0141053, 0.19, 0.05, 1e-3, 2.5e-4, 1.5):
            self.assertTrue(any(abs(p - v) <= 1e-12 * max(1, v) for p in pool), v)

    def test_rounding_match(self):
        self.assertTrue(S.number_found(0.035, 2, [0.0352]))
        self.assertFalse(S.number_found(0.036, 2, [0.0352]))
        self.assertTrue(S.number_found(0.0352, 3, [0.0352]))
        self.assertTrue(S.number_found(1.0, 1, [-1.0]))


class Span(unittest.TestCase):
    def pm(self):
        pm = S.PaperMap.__new__(S.PaperMap)
        sm = [[0, "main.tex", 1, 0], [10, "main.tex", 2, 0], [20, "main.tex", 4, 0],
              [30, "sec/a.tex", 1, 0], [40, "main.tex", 5, 0]]
        pm.flat_len = 50
        pm.starts = [s for s, *_ in sm]
        pm.by_line, pm.lines_of = {}, {}
        for i, (s, f, ln, _c) in enumerate(sm):
            e = sm[i + 1][0] if i + 1 < len(sm) else 50
            pm.by_line[(f, ln)] = (s, e)
            pm.lines_of.setdefault(f, []).append(ln)
        pm.files = sorted(pm.lines_of)
        return pm

    def test_exact_partial_next(self):
        pm = self.pm()
        self.assertEqual(pm.span("main.tex", 2, 2), (10, 20, "exact"))
        self.assertEqual(pm.span("main.tex", 2, 4)[:2], (10, 30))
        self.assertEqual(pm.span("main.tex", 2, 4)[2], "exact")        # both ends kept, line 3 dropped
        self.assertEqual(pm.span("main.tex", 2, 3), (10, 20, "partial"))  # the last line was dropped
        self.assertEqual(pm.span("main.tex", 3, 3), (20, 30, "next-line 4"))
        self.assertEqual(pm.span("a.tex", 1, 1), (30, 40, "exact"))     # file named without its directory
        self.assertEqual(pm.span("other.tex", 1, 1)[2], "file-not-in-flat")
        self.assertIsNone(pm.span("main.tex", 90, 95)[0])


class Labels(unittest.TestCase):
    def st(self, **kw):
        base = dict(key="X/1", owner="X", paper_id="1", file="main.tex", text="t", track_label="VERIFIED",
                    kb=[dict(status="resolved", lines_in_file=True, file="main.tex", lo=1, hi=1, version="v1",
                             paper_id="1", chunks=[], flat=[0, 5])],
                    numbers={"n": 0})
        base.update(kw)
        return base

    def test_rules(self):
        self.assertEqual(S.decide_label(self.st())[0], "fulltext")
        self.assertEqual(S.decide_label(self.st(numbers={"n": 2, "found": 1, "near": 1, "missing": ["5.1"]}))[0],
                         "to_verify")
        self.assertEqual(S.decide_label(self.st(kb=[dict(status="unmapped", map="x")]))[0], "to_verify")
        self.assertEqual(S.decide_label(self.st(track_label="JUDGEMENT"))[0], "judgement")
        self.assertEqual(S.decide_label(self.st(track_label="TO VERIFY", promote_on_numbers=True,
                                                numbers={"n": 2, "found": 2, "near": 2}))[0], "fulltext")
        self.assertEqual(S.decide_label(self.st(track_label="TO VERIFY", promote_on_numbers=True,
                                                numbers={"n": 2, "found": 1, "near": 2}))[0], "to_verify")
        self.assertEqual(S.decide_label(self.st(label="refuted", expect_found={"a": False}))[0], "refuted")
        self.assertEqual(S.decide_label(self.st(label="fulltext", expect_found={"a": False}))[0], "to_verify")


if __name__ == "__main__":
    unittest.main(verbosity=1)
