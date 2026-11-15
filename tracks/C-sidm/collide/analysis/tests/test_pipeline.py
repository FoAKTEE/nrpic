"""Pipeline tests of the analysis on synthetic snapshots (prediction P-pipe, JOURNAL.md).

The synthetic data are made from the references, not by a collision code: early
snapshots rescale each population's four-velocities so that its mean kinetic energy
equals the two-Maxwell-Juttner model at that time; the last snapshot is a fresh
Maxwell-Juttner sample at theta_eq. Run: python3 -m pytest -q analysis/tests
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.dirname(HERE)
sys.path.insert(0, AN)
sys.path.insert(0, os.path.join(AN, "..", "REFERENCES"))
import snap   # noqa: E402
import mj     # noqa: E402
import relax  # noqa: E402


def scale_to(u, theta):
    target = float(mj.mean_kinetic(theta))
    f = lambda lam: snap.kinetic_flat(lam * u).mean() - target
    lam = optimize.brentq(f, 0.1, 10.0, xtol=1e-15, rtol=1e-15)
    return lam * u


def test_relax_pipeline(tmp_path):
    out = str(tmp_path)
    pre = os.path.join(out, "tt")
    subprocess.check_call([sys.executable, os.path.join(AN, "make_box.py"), "twotemp",
                           "--out", pre, "--n", "200000", "--theta", "3e-3",
                           "--theta2", "1e-3", "--sigma", "1.0", "--seed", "3"],
                          stdout=subprocess.DEVNULL)
    meta = json.load(open(pre + ".json"))
    ini = snap.read_nrp(pre + ".nrp")
    n1 = meta["n_pop1"]
    V = float(np.prod(meta["box"]))
    rho1 = ini["m"][:n1].sum() / V
    rho2 = ini["m"][n1:].sum() / V
    th1 = mj.theta_from_kinetic(snap.kinetic_flat(ini["u"][:n1]).mean())
    th2 = mj.theta_from_kinetic(snap.kinetic_flat(ini["u"][n1:]).mean())
    tau = relax.relaxation_time(rho1, rho2, 1.0, th1, th2)
    times = np.arange(16) * 0.01 * tau
    tm, ym = relax.two_mj_model(rho1, rho2, 1.0, th1, th2, times[-1], len(times))
    for k, t in enumerate(times):
        u = ini["u"].copy()
        if k > 0:
            u[:n1] = scale_to(ini["u"][:n1], ym[0, k])
            u[n1:] = scale_to(ini["u"][n1:], ym[1, k])
        snap.write_snapshot(os.path.join(out, f"tt.part.{k:05d}.bin"), t, k, ini["x"], u,
                            ini["m"])
    teq = relax.theta_eq(rho1, rho2, th1, th2)
    rng = np.random.default_rng(9)
    u_end = mj.sample_u(len(ini["m"]), teq, rng)
    snap.write_snapshot(os.path.join(out, "tt.part.00016.bin"), 12 * tau, 999, ini["x"],
                        u_end, ini["m"])
    subprocess.check_call([sys.executable, os.path.join(AN, "an_box.py"), "relax", out,
                           "tt", pre + ".json", out], stdout=subprocess.DEVNULL)
    r = json.load(open(os.path.join(out, "relax_tt.json")))
    assert r["T4_pass"], r
    assert abs(r["T4_ratio"] - 1) < 0.01, r["T4_ratio"]
    assert r["T3_pass"], r
    assert abs(r["T5_s0"] - r["T5_s_mix"]) < 4 * r["T5_se"]
    assert abs(r["T5_s_end"] - r["T5_s_eq"]) < 4 * r["T5_se"]
    # keep the figure for inspection
    os.makedirs(os.environ.get("PIPE_FIG_DIR", out), exist_ok=True)
    import shutil
    shutil.copy(os.path.join(out, "relax_tt.png"),
                os.path.join(os.environ.get("PIPE_FIG_DIR", out), "pipeline_relax_tt.png"))
    json.dump(r, open(os.path.join(os.environ.get("PIPE_FIG_DIR", out),
                                   "pipeline_relax_tt.json"), "w"), indent=1)


def test_repro_detects_difference(tmp_path):
    rng = np.random.default_rng(1)
    x = rng.uniform(size=(100, 3)); u = rng.normal(size=(100, 3)); m = np.ones(100)
    a = os.path.join(tmp_path, "a.bin"); b = os.path.join(tmp_path, "b.bin")
    c = os.path.join(tmp_path, "c.bin")
    snap.write_snapshot(a, 1.0, 10, x, u, m)
    snap.write_snapshot(b, 1.0, 10, x, u, m)
    u2 = u.copy(); u2[5, 1] = np.nextafter(u2[5, 1], 10)
    snap.write_snapshot(c, 1.0, 10, x, u2, m)
    ok = subprocess.call([sys.executable, os.path.join(AN, "an_box.py"), "repro", a, b],
                         stdout=subprocess.DEVNULL)
    bad = subprocess.call([sys.executable, os.path.join(AN, "an_box.py"), "repro", a, c],
                          stdout=subprocess.DEVNULL)
    assert ok == 0 and bad == 1


def test_mode_pipeline_collisionless_limit(tmp_path):
    """Mode amplitude of a make_box mode sample equals eps at t = 0 (number mode: -eps
    because density is 1 - eps cos kx)."""
    out = str(tmp_path)
    pre = os.path.join(out, "md")
    subprocess.check_call([sys.executable, os.path.join(AN, "make_box.py"), "mode",
                           "--out", pre, "--n", "400000", "--theta", "0.01",
                           "--eps", "0.05", "--sigma", "1.0", "--box", "10", "0.5", "0.5"],
                          stdout=subprocess.DEVNULL)
    meta = json.load(open(pre + ".json"))
    ini = snap.read_nrp(pre + ".nrp")
    k = meta["k"]
    c = np.cos(k * (ini["x"][:, 0] - meta["x0"]))
    A = 2 * (ini["m"] * c).sum() / ini["m"].sum()
    assert abs(A + 0.05) < 4 * np.sqrt(2 / len(c))
    K = snap.kinetic_flat(ini["u"])
    AK = 2 * (ini["m"] * K * c).sum() / (ini["m"] * K).sum()
    # kinetic energy density ~ n T = const at fixed pressure: mode ~ 0 to first order
    assert abs(AK) < 4 * np.sqrt(2 / len(c)) * 1.5
