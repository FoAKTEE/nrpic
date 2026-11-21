#!/usr/bin/env python3
"""Lead review, wave 3 (B-emd-gw), checks L1 and L2 of ../JOURNAL.md: G1 criterion 1.

L1: every last-dump TT error that both the waves package and verifier3 give, compared after
    checking that the committed JSON copies equal the registered run outputs.
L2: a third reading of test X at N = 64 (x1 and x10) from the raw double-precision dumps:
    H_p = 2 e_p:c(K)/(e_p:e_p) with c(K) = mean[(gt - 1) exp(-i K.x)] over the cell centres,
    H_p' the same of -2 alpha At (zero shift), Z = H + i H'/|K|, against A_p (T + i T'/|K|),
    T from T'' + 4 T'/(t+2) + K^2 T = 0, T(0) = 0, T'(0) = 1 (numerical, DOP853).
    Basis (theta-hat, phi-hat) of K, checked against the t = 0 data.

    python3 lw3_crit1.py            (through nrpic-run; writes $NRPIC_RUN_DIR/lw3_crit1.json
                                     and lw3_crit1.{png,pdf})
Only numpy, scipy, matplotlib, the repository's python/nrpic/figstyle.py and gw_diag's byte
reader (gwdiag/binio.py; nothing of its projections) are used.
"""
import filecmp
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
sys.path.insert(0, os.path.join(TRACK, "gw_diag"))
sys.path.insert(0, os.path.join(REPO, "python"))
from gwdiag import binio  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(SCR, "tmp", "lw3"))
os.makedirs(OUT, exist_ok=True)

# registered outputs and their committed copies
COPIES = [
    (os.path.join(SCR, "B-20261119-164402-7438a99", "final_results.json"),
     os.path.join(TRACK, "waves", "results", "final_results.json")),
    (os.path.join(SCR, "B-20261120-221708-d8eae03", "x10_64_results.json"),
     os.path.join(TRACK, "waves", "results", "x10_64_results.json")),
    (os.path.join(SCR, "B-20261121-030121-58fe5dc", "v3_summary.json"),
     os.path.join(TRACK, "stage", "G1", "verifier3", "results", "v3_summary.json")),
]
XDUMPS = {
    "x1": (os.path.join(SCR, "B-20261119-142124-feb2daf", "expN64", "bin"), 1.0),
    "x10": (os.path.join(SCR, "B-20261119-155758-458cf17", "expN64x10", "bin"), 10.0),
}


def find_copy(reg, com):
    """The registered output may sit in a subdirectory of the run directory."""
    if os.path.exists(reg):
        return reg
    d = os.path.dirname(reg)
    for root, _, files in os.walk(d):
        if os.path.basename(reg) in files:
            return os.path.join(root, os.path.basename(reg))
    return None


def l1():
    res = {"copies": []}
    for reg, com in COPIES:
        r = find_copy(reg, com)
        res["copies"].append({"registered": r, "committed": com,
                              "identical": bool(r and filecmp.cmp(r, com, shallow=False))})
    w = json.load(open(COPIES[0][1]))
    w10 = json.load(open(COPIES[1][1]))
    v = json.load(open(COPIES[2][1]))
    rows = []
    for test, wk, vk in (("F", "flat", "F"), ("X", "exp", "X")):
        for n in ("16", "32", "48", "64"):
            for pol, wp in (("+", "p"), ("x", "x")):
                for q, vq in (("amp", "amp_err_final"), ("phase", "phase_err_final")):
                    a = w[wk][n]["tt"][f"{q}_{wp}_end"]
                    b = v[vk][n][f"TT {pol}"][vq]
                    rows.append(dict(test=test, N=int(n), pol=pol, q=q, waves=a, verifier=b,
                                     diff=a - b, rel=(a - b) / abs(b)))
    for pol, wp in (("+", "p"), ("x", "x")):
        for q, vq in (("amp", "amp_err_final"), ("phase", "phase_err_final")):
            a = w10["exp"]["64"]["tt"][f"{q}_{wp}_end"]
            b = v["X10"]["64"][f"TT {pol}"][vq] if "64" in v["X10"] else v["X10"][f"TT {pol}"][vq]
            rows.append(dict(test="X10", N=64, pol=pol, q=q, waves=a, verifier=b,
                             diff=a - b, rel=(a - b) / abs(b)))
    res["rows"] = rows
    return res


def exact_T(tq, k):
    f = lambda t, y: [y[1], -4.0 * y[1] / (t + 2.0) - k * k * y[0]]
    s = solve_ivp(f, (0.0, float(max(tq))), [0.0, 1.0], method="DOP853", rtol=1e-13,
                  atol=1e-16, t_eval=np.sort(np.unique(tq)), dense_output=True)
    y = s.sol(tq)
    return y[0], y[1]


def basis(khat):
    th = np.arccos(khat[2])
    ph = np.arctan2(khat[1], khat[0])
    t = np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
    p = np.array([-np.sin(ph), np.cos(ph), 0.0])
    ep = np.outer(t, t) - np.outer(p, p)
    ex = np.outer(t, p) + np.outer(p, t)
    return {"+": ep, "x": ex}


COMP = {(0, 0): "xx", (0, 1): "xy", (0, 2): "xz", (1, 1): "yy", (1, 2): "yz", (2, 2): "zz"}


def coeffs(d, K, E):
    z, y, x = np.meshgrid(d["x3v"], d["x2v"], d["x1v"], indexing="ij")
    ph = np.exp(-1j * (K[0] * x + K[1] * y + K[2] * z))
    alpha = d["alpha"]
    cg, ca = np.zeros((3, 3), complex), np.zeros((3, 3), complex)
    for (i, j), s in COMP.items():
        g = d["g" + s] - (1.0 if i == j else 0.0)
        cg[i, j] = cg[j, i] = np.mean(g * ph)
        ca[i, j] = ca[j, i] = np.mean(-2.0 * alpha * d["A" + s] * ph)
    out = {}
    for p, e in E.items():
        nn = np.sum(e * e)
        out[p] = (2 * np.sum(e * cg) / nn, 2 * np.sum(e * ca) / nn)
    return out


def l2():
    K = (np.pi / 2) * np.array([1.0, 1.0, 0.0])
    k = np.linalg.norm(K)
    E = basis(K / k)
    res = {}
    for tag, (d0, scale) in XDUMPS.items():
        files = sorted(f for f in os.listdir(d0) if f.endswith(".bin"))
        A = {"+": 2e-6 * scale, "x": 1e-6 * scale * np.exp(1j)}
        ts, H = [], {"+": [], "x": []}
        for f in files:
            dd = binio.read_bin(os.path.join(d0, f), strip_prefix=True)
            ts.append(dd["time"])
            c = coeffs(dd, K, E)
            for p in H:
                H[p].append(c[p])
        ts = np.array(ts)
        T, Tp = exact_T(ts, k)
        r = {"t": ts.tolist(), "files": len(files)}
        for p in H:
            h = np.array([a for a, _ in H[p]])
            hp = np.array([b for _, b in H[p]])
            Z = h + 1j * hp / k
            Zex = A[p] * (T + 1j * Tp / k)
            ratio = Z / Zex
            r[p] = {"t0_Hprime_over_A": [float((hp[0] / A[p]).real), float((hp[0] / A[p]).imag)],
                    "t0_H": float(abs(h[0])),
                    "amp_err": (np.abs(ratio) - 1).tolist(),
                    "phase_err": np.angle(ratio).tolist(),
                    "amp_err_end": float(abs(ratio[-1]) - 1),
                    "phase_err_end": float(np.angle(ratio[-1]))}
        zx = np.array([a for a, _ in H["x"]]) + 1j * np.array([b for _, b in H["x"]]) / k
        zp = np.array([a for a, _ in H["+"]]) + 1j * np.array([b for _, b in H["+"]]) / k
        R = zx / zp
        r["pol_ratio_arg_err_end"] = float(np.angle(R[-1]) - 1.0)
        r["pol_ratio_mod_err_end"] = float(abs(R[-1]) / 0.5 - 1.0)
        res[tag] = r
    return res


def figure(r1, r2, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.35, 3.0))
    ax = axs[0]
    mk = {"F": "o", "X": "s", "X10": "D"}
    for i, row in enumerate(r1["rows"]):
        col = fs.PAL["blue"] if row["pol"] == "+" else fs.PAL["red"]
        x = row["N"] + (0 if row["q"] == "amp" else 2) + (0 if row["test"] != "X10" else 4)
        ax.semilogy(x, max(abs(row["rel"]), 1e-12), mk[row["test"]], color=col,
                    mfc=col if row["q"] == "amp" else "none", ms=5)
    ax.axhline(0.01, **fs.GUIDE)
    ax.set_xlabel("N (amplitude filled, phase open; X x10 shifted)")
    ax.set_ylabel("|waves - verifier3| / |verifier3|")
    ax.set_title("(a) two readings, last dump", loc="left")
    ax.plot([], [], "o", color="k", label="F")
    ax.plot([], [], "s", color="k", label="X")
    ax.plot([], [], "D", color="k", label="X x10")
    ax.plot([], [], "-", color=fs.PAL["blue"], label="plus")
    ax.plot([], [], "-", color=fs.PAL["red"], label="cross")
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    for j, (q, lab) in enumerate((("amp_err", "amplitude error"), ("phase_err", "phase error (rad)"))):
        ax = axs[1 + j]
        for tag, ls in (("x1", "-"), ("x10", "--")):
            t = np.array(r2[tag]["t"])
            for p, col in (("+", fs.PAL["blue"]), ("x", fs.PAL["red"])):
                ax.plot(t[1:], np.array(r2[tag][p][q])[1:], ls, color=col,
                        label=f"{'plus' if p == '+' else 'cross'} {tag}")
        ax.set_xlabel("t")
        ax.set_ylabel(lab)
        ax.set_title(f"({'b' if j == 0 else 'c'}) X at N = 64, third reading", loc="left")
        ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fs.save(fig, path)


def main():
    r1 = l1()
    r2 = l2()
    out = {"L1": r1, "L2": {t: {k: v for k, v in r2[t].items() if k not in ("t",)}
                            for t in r2}}
    # compact L2 summary
    summ = {}
    for t in r2:
        summ[t] = {p: {"amp_err_end": r2[t][p]["amp_err_end"],
                       "phase_err_end": r2[t][p]["phase_err_end"],
                       "t0_Hprime_over_A": r2[t][p]["t0_Hprime_over_A"]} for p in ("+", "x")}
        summ[t]["pol_ratio_arg_err_end"] = r2[t]["pol_ratio_arg_err_end"]
        summ[t]["pol_ratio_mod_err_end"] = r2[t]["pol_ratio_mod_err_end"]
    out["L2_summary"] = summ
    out["L1_max_rel_excluding_X_plus_amp_N48_64_x1"] = max(
        abs(r["rel"]) for r in r1["rows"]
        if not (r["test"] == "X" and r["pol"] == "+" and r["q"] == "amp" and r["N"] >= 48))
    with open(os.path.join(OUT, "lw3_crit1.json"), "w") as f:
        json.dump(out, f, indent=1)
    figure(r1, r2, os.path.join(OUT, "lw3_crit1"))
    print(json.dumps({"copies": r1["copies"], "L2_summary": summ,
                      "L1_max_rel_other": out["L1_max_rel_excluding_X_plus_amp_N48_64_x1"],
                      "L1_X_plus_amp": [(r["N"], r["waves"], r["verifier"]) for r in r1["rows"]
                                        if r["test"] in ("X", "X10") and r["pol"] == "+"
                                        and r["q"] == "amp"]}, indent=1))


if __name__ == "__main__":
    main()
