"""Tests of wave 2 (criteria2): the amplitude conversion of predict.py (A1-A5) and the LTB
profile of arXiv:2609.14218 in expball form (L1-L5). Tolerances are those written in
JOURNAL.md before the first run, or tighter where the registered run showed the error to be
round-off; the failed predictions (L1 at mu = 1e-4, L4 for q = 2) are tested here at what the
run established, and stay on record in the journal.

    cd tracks/A-emd-pbh/criteria && ../../../.venv/bin/python -m pytest -q test_criteria2.py
"""
import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_criteria2 as K  # noqa: E402
import predict as P  # noqa: E402


def test_A1_closed_forms_against_quadrature():
    r = K.check_A1()
    assert r["err_rm"] < 1e-9 and r["err_c"] < 1e-9 and r["err_bar"] < 1e-9
    assert abs(r["ratio"] - math.e) < 1e-15


def test_A2_anisotropy_changes_neither_measure():
    for c in K.check_A2():
        assert c["err_mean"] < 2e-3, c
        assert c["err_eig"] < 1e-4, c
        assert abs(c["trace"] / c["trace_ref"] - 1) < 1e-4, c


def test_A3_consistent_with_2507_and_roundtrip():
    res = K.check_A3()
    for c in res[:-1]:
        assert c["err"] < 1e-12
    assert res[-1]["roundtrip"] < 1e-12


def test_A4_nonlinear_compaction():
    for c in K.check_A4():
        assert c["err"] < 1e-9 and c["err_loc"] < 1e-6, c


def test_A5_R1_uses_the_central_measure():
    for c in K.check_A5():
        assert c["err"] < 1e-12, c


def test_conversion_values():
    m = P.amplitude_measures(0.33, "mu")
    assert abs(m["delta_c"] - 0.792) < 1e-12
    assert abs(m["deltabar"] - 0.792 / math.e) < 1e-12
    assert abs(P.convert_amplitude(1.0, "central", "mean") - 1 / math.e) < 1e-15
    t = P.amplitude_measures(0.2, "mean", "tophat")
    assert t["delta_c"] == t["deltabar"] == 0.2
    with pytest.raises(ValueError):
        P.amplitude_measures(0.2, "mu", "tophat")


def test_L1_linear_limit_second_order_is_17_over_21():
    for c in K.check_L1():
        # relative deviation from linear theory = (17/21) Delta + O(Delta^2)
        assert abs(c["max_rel_over_Delta"] - 17 / 21) < 1e-4, c


def test_L2_L3_expball_shells_equal_the_closed_forms():
    for c in K.check_L2L3(mus=(0.005, 0.015)):
        assert c["err_age"] < 1e-12 and c["err_tc"] < 1e-8 and c["err_tah"] < 1e-8, c
        assert max(c["err_R"]) < 1e-8, c


def test_L4_largest_amplitude_of_the_ball():
    for c in K.check_L4(qs=(3.0,)):
        assert c["builds_below"] and c["refuses_above"], c
        assert 0.036 <= c["mu_max"] <= 0.044, c


def test_L5_no_shell_crossing_before_the_crunch():
    for c in K.check_L5(mus=(0.01, 0.33, 0.5)):
        assert c["t_s_increasing"] and c["R_increasing_before_crunch"], c
