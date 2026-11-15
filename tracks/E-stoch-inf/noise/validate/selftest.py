#!/usr/bin/env python3
"""Self-test of the validation (tests T-N2, T-N3, T-N4 of noise/JOURNAL.md).

    python3 selftest.py --out DIR [--quick]

Emulates the code's output of the unit test (NOISE_SPEC.md, section 9) with the reference
(ref/noise_ref.py), with and without deliberate errors ("mutants"), and runs the
validation on it:
  T-N2  calibration: 200 seeds at N = 32; the statistics of A2, A3, A4, A7, A15 must be
        standard normal (mean within 4 standard errors, standard deviation within 20 %);
  T-N3  positive controls: every test passes on correct output (20 seeds of the base case,
        5 each of Markov/tanh, Markov/Heaviside, pair amplitudes, 3 single precision; the
        comparisons A11-A15 on correct pairs);
  T-N4  negative controls: each mutant fails the test written for it.
The emulated code integrates the frozen acc0 with classical RK4 at the stage times
(Simpson's rule for a source that depends on time only).
Writes selftest.json, summary.txt and figures fig_selftest_*.png/pdf.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ref"))
import noise_ref as nr                                    # noqa: E402
import validate_noise as vn                               # noqa: E402
import athenak_io as aio                                  # noqa: E402

NEG_EXPECT = {   # mutant -> tests it must fail (noise/JOURNAL.md, T-N4)
    "norm_2pi": {"A2"},
    "white": {"A2"},
    "corner": {"A1"},
    "fresh_in_frozen": {"A8", "A9"},
    "frozen_in_markov": {"A8"},
    "separate_keys": {"A6"},
    "axis_swap": {"A1", "A2"},
    "block_keys": {"A11"},
    "fixed_modulus": {"A3"},
    "beyond_cut": {"A10"},
    "pair_declared_hemisphere": {"A6"},
    "restart_counter": {"A12"},
    "stage_time_error": {"A9"},
    "seed_ignored": {"A15"},
    "corner_resolution": {"A13"},
}


def emulate(p, mut=(), precision="double", log="agm", gen_seed=None, only_after=None):
    """Run dictionary as the code would write it (p: declared parameters)."""
    mut = set(mut)
    pc = dict(p)                                   # parameters the emulated code uses
    if "beyond_cut" in mut:
        pc["nmax2"] = p["nmax2"] + 40
    if gen_seed is not None:
        pc["seed"] = gen_seed
    lat = nr.Lattice(pc["N"], pc["L"], pc["nmax2"])
    cycles = sorted(p["cycles"])
    amp_scheme = "pair" if "pair_declared_hemisphere" in mut else pc["amplitudes"]
    dofmap = {0: 0, 1: 2, 2: 1, 3: 3} if "separate_keys" in mut else nr.TEST_DOF

    def epoch(cyc):
        if "fresh_in_frozen" in mut:
            return int(cyc)
        if "frozen_in_markov" in mut:
            return 0
        if "restart_counter" in mut and cyc > p["restart_at"]:
            return int(cyc - p["restart_at"])
        return nr.epoch_of(cyc, pc)

    cache = {}

    def amps(dof, ep, seed):
        k = (dof, ep, seed)
        if k not in cache:
            a = nr.amplitudes(lat, seed, dof, ep, amp_scheme, log)
            if "fixed_modulus" in mut:
                a = tuple(None if x is None else x / np.abs(x) for x in a)
            cache[k] = a
        return cache[k]

    def gmod(G):
        if "norm_2pi" in mut:
            G = G * (2 * np.pi)**0.75
        if "white" in mut:
            G = G * lat.q**1.5
        return G

    def all_coeffs(seed):
        co = {}
        for cyc in cycles:
            for c in range(4):
                G = gmod(nr.transfer(lat, c, cyc, pc))
                co[(f"stoch_c{c}", cyc)] = nr.coefficients(G, amps(dofmap[c], epoch(cyc), seed),
                                                           amp_scheme)
        dt = pc["dt"]
        acc = np.zeros(lat.M, dtype=complex)
        if pc["scheme"] == "frozen":
            base = nr.base_amplitude(lat, pc)
            for m in range(max(cycles)):
                t = m * dt
                if "stage_time_error" in mut:
                    incr = dt * nr.window_rate(lat, t, pc)
                else:
                    incr = dt / 6 * (nr.window_rate(lat, t, pc) +
                                     4 * nr.window_rate(lat, t + dt / 2, pc) +
                                     nr.window_rate(lat, t + dt, pc))
                ep = (m + 1) if "fresh_in_frozen" in mut else 0
                acc = acc + nr.coefficients(gmod(base * incr), amps(0, ep, seed), amp_scheme)
                if ep != 0:
                    cache.pop((0, ep, seed), None)
                if m + 1 in cycles:
                    co[("stoch_acc0", m + 1)] = acc.copy()
        else:
            for m in range(1, max(cycles) + 1):
                G = gmod(nr.transfer(lat, 0, m, pc))
                if np.any(G != 0):
                    acc = acc + nr.coefficients(G, amps(0, epoch(m), seed), amp_scheme)
                if m in cycles:
                    co[("stoch_acc0", m)] = acc.copy()
                elif epoch(m) != 0:
                    cache.pop((0, epoch(m), seed), None)
        return co

    pos = "corner" if ("corner" in mut or "corner_resolution" in mut) else "centre"
    co = all_coeffs(pc["seed"])
    fields = {k: nr.synthesise(lat, c, pos)[0] for k, c in co.items()}
    if "block_keys" in mut:                      # each octant from its own realisation
        h = p["N"] // 2
        for b in range(1, 8):
            cob = all_coeffs(pc["seed"] + 1000 * b)
            bx, by, bz = b & 1, (b >> 1) & 1, (b >> 2) & 1
            sl = (slice(bx * h, (bx + 1) * h), slice(by * h, (by + 1) * h),
                  slice(bz * h, (bz + 1) * h))
            for k, c in cob.items():
                fields[k][sl] = nr.synthesise(lat, c, pos)[0][sl]
    if "axis_swap" in mut:
        fields = {k: np.ascontiguousarray(f.transpose(2, 1, 0)) for k, f in fields.items()}
    outputs = {}
    for (v, cyc), f in fields.items():
        if only_after is not None and cyc <= only_after:
            continue
        o = outputs.setdefault(cyc, {"time": nr.out_time(cyc, p), "fields": {}})
        o["fields"][v] = f.astype(np.float32) if precision == "single" else f
    return dict(params=dict(p), N=p["N"], L=p["L"], x0=p["x0"], precision=precision,
                outputs=outputs, files=[])


def failed_ids(res):
    return {r["id"] for r in res if r["passed"] is False}


# ------------------------------------------------------------------ T-N2
def calibration(nseeds, out):
    p0 = nr.default_params(N=32, nmax2=64, cycles=(100, 200))
    zs = {"A2 zpool c0@200": [], "A3 z4 c0@200": [], "A7 z_re@200": [], "A7 z_im@200": [],
          "A15 z_re@200": []}
    lagz = {}
    pvals = []
    prev = None
    for i in range(nseeds):
        p = dict(p0, seed=1000 + i)
        run = emulate(p)
        res, data, a = vn.validate_single(run)
        zs["A2 zpool c0@200"].append(data["A2"]["stoch_c0@200"]["zpool"])
        zs["A3 z4 c0@200"].append(data["A3"]["stoch_c0@200"]["z4"])
        zr, zi = data["A7"]["200"]
        zs["A7 z_re@200"].append(zr)
        zs["A7 z_im@200"].append(zi)
        r4 = data["A4"]["stoch_c0@200"]
        lags = np.array(r4["lags"])
        for j in (0, 1, 4, 8, 16):
            d = r4["lags"][j]
            key = f"A4 lag {tuple(d)}"
            lagz.setdefault(key, []).append((r4["meas"][j] - r4["exp"][j]) / r4["sd"][j])
        # exact Gamma p-values of every shell (uniform under H0)
        r2 = data["A2"]["stoch_c0@200"]
        for sh, ra, M in zip(r2["shells"], r2["ratio"], r2["M"]):
            pvals.append(vn.gamma_p(ra * M, M))
        if prev is not None:
            zr15, _ = vn.indep_z(a.coef[("stoch_c0", 200)], prev,
                                 a.G[("stoch_c0", 200)], a.G[("stoch_c0", 200)])
            zs["A15 z_re@200"].append(zr15)
        prev = a.coef[("stoch_c0", 200)]
    zs.update(lagz)
    table = {}
    ok = True
    for k, v in zs.items():
        v = np.array(v)
        se = 1 / np.sqrt(v.size)
        m, s = float(v.mean()), float(v.std(ddof=1))
        good = abs(m) <= 4 * se and abs(s - 1) <= 0.2
        ok &= good
        table[k] = dict(n=int(v.size), mean=m, std=s, mean_over_se=m / se, holds=bool(good))
    from scipy import stats
    pv = np.array(pvals)
    # two-sided Gamma p-values are not uniform for small M (discrete-like tails are fine,
    # but the two-sided construction is uniform only asymptotically): report the KS
    ks = float(stats.kstest(pv, "uniform").pvalue)
    frac = float(np.mean(pv < 0.01))
    res = dict(seeds=nseeds, stats=table, shell_p_ks=ks, shell_p_frac_below_0p01=frac,
               shell_p_count=int(pv.size), prediction_holds=bool(ok))
    return res, zs, pv


# ------------------------------------------------------------------ T-N3 / T-N4
def full_validation(run, extra=()):
    res, data, a = vn.validate_single(run)
    return res + list(extra), data, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--quick", action="store_true")
    a_ = ap.parse_args()
    t0 = time.time()
    report = {}
    nseeds = 40 if a_.quick else 200
    cal, zs, pv = calibration(nseeds, a_.out)
    report["T-N2"] = cal
    print("T-N2", json.dumps(cal["stats"]), cal["prediction_holds"], f"{time.time()-t0:.0f}s",
          flush=True)

    base = nr.default_params()
    rows = []                        # (label, kind, results)
    # ---- positive controls
    pos_fail = []
    nb = 4 if a_.quick else 20
    cases = [("frozen/tanh/hemisphere", dict(), "double", nb),
             ("markov/tanh/hemisphere", dict(scheme="markov"), "double", 2 if a_.quick else 5),
             ("markov/heaviside/hemisphere", dict(scheme="markov", window="heaviside"),
              "double", 2 if a_.quick else 5),
             ("frozen/tanh/pair", dict(amplitudes="pair"), "double", 2 if a_.quick else 5),
             ("frozen/tanh/hemisphere single", dict(), "single", 1 if a_.quick else 3)]
    saved_base = None
    for label, kw, prec, ns in cases:
        for i in range(ns):
            p = dict(base, seed=base["seed"] + 7919 * i, **kw)
            run = emulate(p, precision=prec)
            res, data, an = full_validation(run)
            if i == 0:
                rows.append((label, "positive", res))
                vn.plot_validation(data, an, a_.out, "pos_" + label.replace("/", "_")
                                   .replace(" ", "_"))
                if label.startswith("frozen/tanh/hemisphere") and prec == "double":
                    saved_base = run
                    aio.write_npz(os.path.join(a_.out, "U1_reference.npz"), run)
            f = failed_ids(res)
            if f:
                pos_fail.append(dict(case=label, seed=p["seed"], failed=sorted(f),
                                     detail=[r for r in res if r["passed"] is False]))
        print("pos", label, ns, "failures so far", len(pos_fail), f"{time.time()-t0:.0f}s",
              flush=True)
    # comparisons on correct pairs
    U1 = saved_base
    U2 = emulate(base)                                   # "8 MeshBlocks": same function
    pm = dict(base, scheme="markov", restart_at=150)
    U6 = emulate(pm)
    U4 = emulate(pm, only_after=150)                     # restarted at 150
    plo, phi = dict(base, N=32, nmax2=64), dict(base, N=64, nmax2=64)
    U5a, U5b = emulate(plo), emulate(phi)
    U8 = emulate(dict(base, seed=base["seed"] + 1))
    comp = [vn.compare_fields(U1, U2, "A11", "MeshBlocks", "bitwise"),
            vn.compare_fields(U6, U4, "A12", "restart (markov)", "bitwise"),
            vn.compare_resolution(U5a, U5b),
            vn.compare_seeds(U1, U8),
            vn.compare_fields(U1, U2, "A14", "card", "tol", 1e-12)]
    rows.append(("comparisons A11-A15", "positive", comp))
    for r in comp:
        if r["passed"] is False:
            pos_fail.append(dict(case="comparison " + r["id"], failed=[r["id"]], detail=[r]))
    report["T-N3"] = dict(failures=pos_fail, n_failures=len(pos_fail),
                          prediction_holds=len(pos_fail) <= 1)
    print("T-N3 failures", len(pos_fail), f"{time.time()-t0:.0f}s", flush=True)

    # ---- negative controls
    neg = {}
    single = ["norm_2pi", "white", "corner", "fresh_in_frozen", "separate_keys",
              "axis_swap", "fixed_modulus", "beyond_cut", "pair_declared_hemisphere",
              "stage_time_error"]
    for m in single:
        run = emulate(base, mut={m})
        res, data, an = full_validation(run)
        if m == "norm_2pi":
            vn.plot_validation(data, an, a_.out, "neg_norm_2pi")
        neg[m] = res
    run = emulate(dict(base, scheme="markov"), mut={"frozen_in_markov"})
    neg["frozen_in_markov"] = full_validation(run)[0]
    blk = emulate(base, mut={"block_keys"})
    neg["block_keys"] = full_validation(blk, [vn.compare_fields(U1, blk, "A11", "MeshBlocks",
                                                                "bitwise")])[0]
    rst = emulate(pm, mut={"restart_counter"}, only_after=150)
    neg["restart_counter"] = [vn.compare_fields(U6, rst, "A12", "restart", "bitwise")]
    sig = emulate(dict(base, seed=base["seed"] + 1), gen_seed=base["seed"])
    neg["seed_ignored"] = [vn.compare_seeds(U1, sig)]
    clo, chi = emulate(plo, mut={"corner_resolution"}), emulate(phi, mut={"corner_resolution"})
    neg["corner_resolution"] = [vn.compare_resolution(clo, chi)]
    negrep, all_caught = {}, True
    for m, res in neg.items():
        f = failed_ids(res)
        caught = NEG_EXPECT[m] <= f
        all_caught &= bool(f)
        negrep[m] = dict(expected=sorted(NEG_EXPECT[m]), failed=sorted(f),
                         expected_all_failed=bool(caught), passes_everything=not f)
        rows.append((m, "negative", res))
    report["T-N4"] = dict(mutants=negrep, prediction_holds=bool(
        all(v["expected_all_failed"] for v in negrep.values())), every_mutant_caught=all_caught)
    report["wall_s"] = time.time() - t0
    with open(os.path.join(a_.out, "selftest.json"), "w") as f:
        json.dump(report, f, indent=1, default=float)
    summ = [f"T-N2 calibration ({nseeds} seeds): holds {cal['prediction_holds']}; " +
            "; ".join(f"{k}: mean {v['mean']:.3f} sd {v['std']:.3f}" for k, v in cal["stats"].items()),
            f"T-N3 positive controls: {len(pos_fail)} failures",
            "T-N4 mutants: " + "; ".join(f"{m}: failed {v['failed']} (expected {v['expected']})"
                                         for m, v in negrep.items())]
    with open(os.path.join(a_.out, "summary.txt"), "w") as f:
        f.write("\n".join(summ) + "\n")
    print("\n".join(summ))
    plot_matrix(rows, a_.out)
    plot_calibration(zs, pv, a_.out)


def plot_matrix(rows, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    sys.path.insert(0, os.path.join(aio.REPO, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    ids = [f"A{i}" for i in range(16)]
    M = np.full((len(rows), len(ids)), np.nan)
    for r, (lab, kind, res) in enumerate(rows):
        for x in res:
            j = ids.index(x["id"])
            v = 1.0 if x["passed"] is True else (0.0 if x["passed"] is False else 0.5)
            M[r, j] = v if np.isnan(M[r, j]) else min(M[r, j], v)
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 0.28 * len(rows) + 1.0))
    cmap = ListedColormap([fs.PAL["red"], "#d9d9d9", fs.PAL["blue"]])
    show = np.where(np.isnan(M), -1, M)
    ax.imshow(np.ma.masked_where(show < 0, show), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for r in range(M.shape[0]):
        for j in range(M.shape[1]):
            if not np.isnan(M[r, j]):
                t = {1.0: "", 0.0: "F", 0.5: "-"}[M[r, j]]
                ax.text(j, r, t, ha="center", va="center", fontsize=7, color="white")
    ax.set_xticks(range(len(ids)))
    ax.set_xticklabels(ids, fontsize=7)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([("+ " if k == "positive" else "- ") + lab for lab, k, _ in rows],
                       fontsize=7)
    ax.tick_params(direction="out", top=False, right=False)
    ax.set_title("validation on correct output (+) and on mutants (-): blue pass, red fail, grey n/a",
                 fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_selftest_matrix"))
    plt.close(fig)


def plot_calibration(zs, pv, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(aio.REPO, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    keys = list(zs)
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    xx = np.linspace(-4, 4, 200)
    for i, k in enumerate(keys[:5]):
        ax[0].hist(zs[k], bins=np.linspace(-4, 4, 25), density=True, histtype="step",
                   lw=1.2, color=fs.series_colors(5)[i], label=k)
    ax[0].plot(xx, np.exp(-xx**2 / 2) / np.sqrt(2 * np.pi), **fs.GUIDE, label="N(0,1)")
    ax[0].set_xlabel("statistic over seeds")
    ax[0].set_ylabel("density")
    ax[0].legend(loc="upper left", fontsize=6)
    ax[1].hist(pv, bins=np.linspace(0, 1, 21), density=True, histtype="step", lw=1.5,
               color=fs.PAL["blue"])
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].set_xlabel("two-sided Gamma p-value per shell")
    ax[1].set_ylabel("density")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_selftest_calibration"))
    plt.close(fig)


if __name__ == "__main__":
    main()
