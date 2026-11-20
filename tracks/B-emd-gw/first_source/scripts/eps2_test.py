#!/usr/bin/env python3
"""Advance test of note/README.md Request 4 (JOURNAL.md, wave 3 round 1, prediction (a)).

    python3 eps2_test.py <set>/<case>=<case.json>[:<kind>] ... (output: $NRPIC_RUN_DIR)

<set> is a label of one mesh (n32, n64); <case> one of d01_e1, d01_e0p3, d0025_e1, d0025_e0p3
(delta = 0.01 or 0.0025, eps = 1 or 0.3); <kind> the double-precision dumps of the case JSON of
analyze_scan.py (rst or dbin). The single-precision dumps (bin) of the same JSON are read too.

dev = c_+(K1)/(s g) - 1 (fslib.reference). At a = 20, 30, 40, 50, 60:
  (a1) R(a) = dev(0.01, a)/dev(0.0025, a), predicted in 12-20 (1/16 of a pure (delta a)^2 law);
  (a2) Q(a) = [dev(eps = 1)/2] / [dev(eps = 0.3)/1.09] at delta = 0.0025, predicted in 0.95-1.05
       (and, as a reading, at delta = 0.01).
dev at a target a: cubic spline through dev(tau) of the double-precision dumps (every 1.0 in
tau), and, as a check, the mean of the single-precision dumps within +-3 percent in a. The
spline is checked against the single-precision mean at delta = 0.01, where the float32 noise
is small. Writes eps2_summary.json and eps2_test.{png,pdf}.
"""
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import reference as ref  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

CASES = {"d01_e1": (0.01, 1.0), "d01_e0p3": (0.01, 0.3),
         "d0025_e1": (0.0025, 1.0), "d0025_e0p3": (0.0025, 0.3)}
A_T = (20.0, 30.0, 40.0, 50.0, 60.0)


def rows_of(path, kind):
    c = json.load(open(path))
    rows = [r for r in c["rows"] if r.get("kind") == kind and "error" not in r]
    rows.sort(key=lambda r: r["time"])
    out, last = [], None
    for r in rows:
        if last is None or r["time"] > last + 1e-9:
            out.append(r)
            last = r["time"]
    return out


def dev_series(rows, delta, eps):
    t = np.array([r["time"] for r in rows])
    c = np.array([r["h_K1_plus"][0] for r in rows])
    s = ref.static_amplitude(delta, eps)
    g, _ = ref.g_of_tau(t)
    return t, ref.a_of_tau(t), c / (s * g) - 1.0


def at_targets(t, a, dv, how):
    out = {}
    if how == "spline":
        m = a >= 2.0
        cs = CubicSpline(t[m], dv[m])
        for aa in A_T:
            tt = float(ref.tau_of_a(aa))
            out[aa] = float(cs(tt)) if t[m][0] <= tt <= t[m][-1] else None
    else:
        for aa in A_T:
            m = (a >= aa * 0.97) & (a <= aa * 1.03)
            out[aa] = float(np.mean(dv[m])) if m.any() else None
    return out


def ratio(x, y):
    return None if (x is None or y is None or y == 0.0) else x / y


def main():
    od = os.environ.get("NRPIC_RUN_DIR", ".")
    sets = {}
    for arg in sys.argv[1:]:
        key, path = arg.split("=", 1)
        st, case = key.split("/", 1)
        kind = "rst"
        if path.endswith((":dbin", ":rst")):
            path, kind = path.rsplit(":", 1)
        delta, eps = CASES[case]
        d = {}
        for k, how in ((kind, "spline"), ("bin", "window")):
            rows = rows_of(path, k)
            t, a, dv = dev_series(rows, delta, eps)
            d[how] = {"t": t, "a": a, "dev": dv, "at": at_targets(t, a, dv, how), "kind": k,
                      "n": len(rows)}
        d["file"] = path
        sets.setdefault(st, {})[case] = d

    S = {"targets_a": list(A_T), "sets": {}}
    fs.use_style()
    import matplotlib.pyplot as plt
    ns = len(sets)
    fig, ax = plt.subplots(ns, 3, figsize=(10.0, 3.0 * ns), squeeze=False)
    for i, (st, C) in enumerate(sorted(sets.items())):
        out = {"files": {c: C[c]["file"] for c in C}}
        for c in C:
            out[f"dev_{c}"] = {how: {str(int(aa)): C[c][how]["at"][aa] for aa in A_T}
                               for how in ("spline", "window")}
            m = (C[c]["spline"]["a"] >= 2.0) & (C[c]["spline"]["a"] <= 9.5)
            out[f"maxabs_dev_double_a2_9_{c}"] = float(np.max(np.abs(C[c]["spline"]["dev"][m])))
        # interpolation check at delta = 0.01
        for c in ("d01_e1", "d01_e0p3"):
            if c in C:
                sp, wi = C[c]["spline"]["at"], C[c]["window"]["at"]
                out[f"spline_minus_window_over_dev_{c}"] = {
                    str(int(aa)): (None if sp[aa] is None or wi[aa] is None else (sp[aa] - wi[aa]) / wi[aa])
                    for aa in A_T}
        verdict = {}
        for how in ("spline", "window"):
            for e in ("e1", "e0p3"):
                n1, n2 = f"d01_{e}", f"d0025_{e}"
                if n1 in C and n2 in C:
                    R = {str(int(aa)): ratio(C[n1][how]["at"][aa], C[n2][how]["at"][aa]) for aa in A_T}
                    out[f"R_{e}_{how}"] = R
                    if how == "spline":
                        ok = all(v is not None and 12.0 <= v <= 20.0 for v in R.values())
                        verdict[f"a1_R_{e}_in_12_20"] = ok
            for dl in ("d0025", "d01"):
                n1, n2 = f"{dl}_e1", f"{dl}_e0p3"
                if n1 in C and n2 in C:
                    Q = {str(int(aa)): ratio(None if C[n1][how]["at"][aa] is None else C[n1][how]["at"][aa] / 2.0,
                                             None if C[n2][how]["at"][aa] is None else C[n2][how]["at"][aa] / 1.09)
                         for aa in A_T}
                    out[f"Q_{dl}_{how}"] = Q
                    if how == "spline" and dl == "d0025":
                        verdict["a2_Q_d0025_in_0.95_1.05"] = all(v is not None and 0.95 <= v <= 1.05
                                                                 for v in Q.values())
        out["verdict_double_spline"] = verdict
        S["sets"][st] = out

        # figures
        col = {"e1": "C0", "e0p3": "C1"}
        for c in C:
            delta, eps = CASES[c]
            e = c.split("_")[1]
            ls = "-" if delta == 0.01 else "--"
            w, sp = C[c]["window"], C[c]["spline"]
            mw, msp = w["a"] >= 2.0, sp["a"] >= 2.0
            f = 1.0 if delta == 0.01 else 16.0
            lab = f"delta={delta}, eps={eps}" + ("" if f == 1.0 else " (x16)")
            ax[i, 0].plot(w["a"][mw], f * np.abs(w["dev"][mw]), color=col[e], ls=ls, lw=0.6, alpha=0.6)
            ax[i, 0].plot(sp["a"][msp], f * np.abs(sp["dev"][msp]), color=col[e], ls="none",
                          marker="o" if delta == 0.01 else "s", ms=3, label=lab)
        for e in ("e1", "e0p3"):
            for how, mk, lw in (("spline", "o", 0.0), ("window", None, 0.8)):
                R = out.get(f"R_{e}_{how}")
                if R:
                    ys = [R[str(int(aa))] for aa in A_T]
                    ax[i, 1].plot(A_T, ys, color=col[e], marker=mk, ls="-" if mk is None else "none",
                                  lw=lw, ms=4, label=f"eps={'1' if e == 'e1' else '0.3'} ({how})")
        for dl, mk in (("d0025", "s"), ("d01", "o")):
            for how, ls in (("spline", "-"), ("window", ":")):
                Q = out.get(f"Q_{dl}_{how}")
                if Q:
                    ys = [Q[str(int(aa))] for aa in A_T]
                    ax[i, 2].plot(A_T, ys, color="C2" if dl == "d0025" else "C3", marker=mk, ls=ls,
                                  lw=0.8, ms=4, label=f"delta={'0.0025' if dl == 'd0025' else '0.01'} ({how})")
        ax[i, 0].set_xscale("log")
        ax[i, 0].set_yscale("log")
        ax[i, 0].set_xlabel("a")
        ax[i, 0].set_ylabel(f"|dev| ({st}; delta=0.0025 x16)")
        ax[i, 0].axvspan(20, 60, color="0.9", zorder=0)
        ax[i, 0].legend(fontsize=5)
        ax[i, 1].axhspan(12, 20, color="0.9", zorder=0)
        ax[i, 1].axhline(16, color="0.6", lw=0.6)
        ax[i, 1].set_xlabel("a")
        ax[i, 1].set_ylabel("R = dev(0.01)/dev(0.0025)")
        ax[i, 1].legend(fontsize=5)
        ax[i, 2].axhspan(0.95, 1.05, color="0.9", zorder=0)
        ax[i, 2].axhline(1.0, color="0.6", lw=0.6)
        ax[i, 2].set_xlabel("a")
        ax[i, 2].set_ylabel("Q = [dev(1)/2] / [dev(0.3)/1.09]")
        ax[i, 2].legend(fontsize=5)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"eps2_test.{ext}"), dpi=150)
    plt.close(fig)
    with open(os.path.join(od, "eps2_summary.json"), "w") as f:
        json.dump(S, f, indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
