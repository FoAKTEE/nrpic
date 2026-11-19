#!/usr/bin/env python3
"""Outcomes of P11-P14 (JOURNAL.md, second round): jittered null, particle number, mesh,
delta = 0.0025. Reads case JSON files of analyze_scan.py and the prediction of
null_prediction.py; writes conv_summary.json and four figures to $NRPIC_RUN_DIR.

    python3 conv_compare.py name=path.json [name=path.json ...] pred=null_prediction.json

Names used (any missing one skips the parts that need it):
  null0 (cw_eps0, plane-symmetric null, wave 2), jit0p3, jit0p1 (jittered nulls),
  s01 (cw_eps0p1 at delta 0.01, the smallest signal of the scan),
  e1_p1, e1_p8 (cw_eps1 of wave 2), e1_p27, e1_rep, e1_n128, e1_n32 (cw_eps1 at 32^3, P8),
  d01_e1, d01_e0p3 (wave 2, delta 0.01), d0025_e1, d0025_e0p3.
The box-mode amplitude c is the complex h_+ at K1 (c - i s); the crossed-wave signal is its
real part. Series are compared at common conformal times by cubic interpolation of the
finer series (dumps of different runs fall on slightly different steps).
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


def load(path, kind="bin"):
    c = json.load(open(path))
    rows = [r for r in c["rows"] if r.get("kind") == kind and "error" not in r]
    rows.sort(key=lambda r: r["time"])
    # drop repeated times (a dump written twice at the last step)
    out, last = [], None
    for r in rows:
        if last is None or r["time"] > last + 1e-9:
            out.append(r)
            last = r["time"]
    return out


def series(rows, key, part=None):
    v = np.array([r[key] for r in rows], dtype=float)
    if part == "complex":
        return v[:, 0] + 1j * v[:, 1]
    if part == "re":
        return v[:, 0]
    return v


def tau(rows):
    return np.array([r["time"] for r in rows])


def interp(t_src, y_src, t):
    if np.iscomplexobj(y_src):
        return interp(t_src, y_src.real, t) + 1j * interp(t_src, y_src.imag, t)
    cs = CubicSpline(t_src, y_src)
    out = cs(t)
    out[(t < t_src[0]) | (t > t_src[-1])] = np.nan
    return out


def win(a, lo, hi):
    return (a >= lo) & (a <= hi)


def maxabs(x, m):
    x = np.asarray(x)[m]
    x = x[np.isfinite(x)]
    return float(np.max(np.abs(x))) if x.size else None


def rmsv(x, m):
    x = np.asarray(x)[m]
    x = x[np.isfinite(x)]
    return float(np.sqrt(np.mean(np.abs(x) ** 2))) if x.size else None


def main():
    od = os.environ.get("NRPIC_RUN_DIR", ".")
    C, pred = {}, None
    for arg in sys.argv[1:]:
        name, path = arg.split("=", 1)
        if name == "pred":
            pred = json.load(open(path))
        elif path.endswith((":dbin", ":rst")):          # double-precision dumps of a case
            path, kind = path.rsplit(":", 1)
            C[name] = load(path, kind)
        else:
            C[name] = load(path)
    S = {}
    fs.use_style()
    import matplotlib.pyplot as plt
    s1 = ref.static_amplitude(0.01, 1.0)

    # ---------------- P11: jittered null ----------------
    if "jit0p3" in C:
        out = {}
        fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.0))
        t3 = tau(C["jit0p3"])
        a3 = ref.a_of_tau(t3)
        for name, col in (("null0", "0.5"), ("jit0p1", "C1"), ("jit0p3", "C0")):
            if name not in C:
                continue
            r = C[name]
            a = ref.a_of_tau(tau(r))
            ax[0].plot(a, series(r, "max_TT_mode"), color=col, label=name)
            ax[0].plot(a, series(r, "rms_TT"), color=col, ls="--", lw=0.8)
            c1 = series(r, "h_K1_plus", "complex")
            c2 = series(r, "h_K2_plus", "complex")
            ax[1].plot(a, np.abs(c1), color=col, label=f"{name} K1")
            ax[1].plot(a, np.abs(c2), color=col, ls=":", label=f"{name} K2")
            out[name] = {"max_TT_mode_first_after_0": float(series(r, "max_TT_mode")[1]),
                         "min_max_TT_mode_after_first": float(np.min(series(r, "max_TT_mode")[1:]))}
        if "s01" in C:
            r = C["s01"]
            a = ref.a_of_tau(tau(r))
            ax[1].plot(a, np.abs(series(r, "h_K1_plus", "re")), color="k", lw=0.8,
                       label="signal eps=0.1")
        if pred is not None:
            pt = np.array(pred["tau"])
            pa = ref.a_of_tau(pt)
            for name, col in (("jit0p1", "C1"), ("jit0p3", "C0")):
                if name not in pred["cases"]:
                    continue
                pc = pred["cases"][name]
                for K, ls in (("K1", "-"), ("K2", ":")):
                    pr = (complex(*pc[f"cross_{K}_plus"]) * np.array(pred["g_cross"])
                          + complex(*pc[f"nn_{K}_plus"]) * np.array(pred["g_nn"]))
                    ax[1].plot(pa, np.abs(pr), color=col, ls=ls, lw=2.5, alpha=0.35)
                    if name in C:
                        r = C[name]
                        t = tau(r)
                        meas = series(r, f"h_{K}_plus", "complex")
                        p_at = interp(pt, pr, t)
                        a = ref.a_of_tau(t)
                        m = win(a, 3.0, 20.0)
                        ratio = np.abs(meas[m]) / np.abs(p_at[m])
                        dph = np.angle(meas[m] / p_at[m])
                        out.setdefault(name, {})[f"{K}_mod_ratio_3_20"] = [float(ratio.min()), float(np.median(ratio)), float(ratio.max())]
                        out[name][f"{K}_phase_diff_3_20"] = [float(dph.min()), float(np.median(dph)), float(dph.max())]
                        out[name][f"{K}_pred_static_cross"] = pc[f"cross_{K}_plus"]
                        out[name][f"{K}_pred_static_nn"] = pc[f"nn_{K}_plus"]
                        if K == "K1":
                            ax[2].plot(a, np.abs(meas) / np.abs(interp(pt, pr, t)), color=col,
                                       label=f"{name}: |meas|/|pred| K1")
        if "jit0p1" in C:
            t1 = tau(C["jit0p1"])
            c3 = series(C["jit0p3"], "h_K1_plus", "complex")
            c1i = interp(t1, series(C["jit0p1"], "h_K1_plus", "complex"), t3)
            rr = c3 / c1i
            m = win(a3, 1.5, 20.0)
            out["ratio_K1_A03_A01_a1.5_20"] = [float(np.nanmin(np.abs(rr[m]))), float(np.nanmedian(np.abs(rr[m]))), float(np.nanmax(np.abs(rr[m])))]
            out["phase_K1_A03_A01_a1.5_20_maxabs"] = float(np.nanmax(np.abs(np.angle(rr[m]))))
            rt = series(C["jit0p3"], "rms_TT") / interp(t1, series(C["jit0p1"], "rms_TT"), t3)
            for lo, hi in ((1.5, 10.0), (10.0, 40.0), (80.0, 140.0)):
                m = win(a3, lo, hi)
                out[f"ratio_rmsTT_A03_A01_a{lo}_{hi}"] = [float(np.nanmin(rt[m])), float(np.nanmedian(rt[m])), float(np.nanmax(rt[m]))]
            ax[2].plot(a3, np.abs(rr), color="C2", label="|c(A=0.3)/c(A=0.1)| K1")
            ax[2].plot(a3, rt, color="C3", label="rms TT ratio A=0.3/0.1")
        if "s01" in C:
            ts = tau(C["s01"])
            sig = interp(ts, series(C["s01"], "h_K1_plus", "re"), t3)
            nz = np.abs(series(C["jit0p3"], "h_K1_plus", "complex")) / np.abs(sig)
            for lo, hi in ((2.0, 20.0), (20.0, 80.0), (80.0, 140.0)):
                m = win(a3, lo, hi)
                out[f"null03_over_signal01_K1_a{lo}_{hi}_max"] = maxabs(nz, m)
            for key in ("rho_kin", "rho_grad"):
                pass
        # energy of the TT part of the null at the last double-precision dumps
        for name in ("jit0p3", "jit0p1", "null0"):
            if name in C:
                r = C[name][-1]
                out.setdefault(name, {})["last"] = {k: r.get(k) for k in ("a", "rms_TT", "max_TT_mode", "rho_kin", "rho_grad", "rho_bar", "rms_nonTT")}
        ax[0].set_xscale("log")
        ax[0].set_yscale("log")
        ax[0].set_xlabel("a")
        ax[0].set_ylabel("largest TT mode (solid), rms TT (dashed)")
        ax[0].legend(fontsize=6)
        ax[1].set_xscale("log")
        ax[1].set_yscale("log")
        ax[1].set_xlabel("a")
        ax[1].set_ylabel("|h_+| at K1, K2 (thick pale: prediction)")
        ax[1].legend(fontsize=5, ncol=2)
        ax[2].set_xscale("log")
        ax[2].set_xlabel("a")
        ax[2].set_ylabel("ratios")
        ax[2].axhline(3.0, color="0.6", lw=0.6)
        ax[2].axhline(1.0, color="0.6", lw=0.6)
        ax[2].set_ylim(0, 10)
        ax[2].legend(fontsize=6)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(os.path.join(od, f"conv_null.{ext}"), dpi=150)
        plt.close(fig)
        S["P11"] = out

    # ---------------- P12, P13: particle number and mesh (eps = 1) ----------------
    names = [n for n in ("e1_p1", "e1_p8", "e1_p27", "e1_rep", "e1_n128", "e1_n32") if n in C]
    names_d = [n for n in ("e1_rep_d", "e1_p8_d") if n in C]
    if names:
        out = {}
        fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.0))
        lab = {"e1_p1": "64^3, 1/cell", "e1_p8": "64^3, 8/cell (wave 2)", "e1_p27": "64^3, 27/cell",
               "e1_rep": "64^3, 8/cell rerun", "e1_n128": "128^3, 1/cell", "e1_n32": "32^3, 8/cell",
               "e1_rep_d": "rerun (double dumps)", "e1_p8_d": "wave 2 (restart dumps)"}
        for n in names:
            r = C[n]
            ax[0].plot(ref.a_of_tau(tau(r)), series(r, "h_K1_plus", "re") / s1, label=lab[n], lw=0.9)

        def diff(n1, n2):
            """c(n1) - c(n2) on the times of n2 (relative to c(n2) and to |s|)."""
            t2 = tau(C[n2])
            c2 = series(C[n2], "h_K1_plus", "re")
            c1 = interp(tau(C[n1]), series(C[n1], "h_K1_plus", "re"), t2)
            return ref.a_of_tau(t2), (c1 - c2) / c2, (c1 - c2) / abs(s1)
        pairs = [("e1_p1", "e1_p27", 1), ("e1_p8", "e1_p27", 1), ("e1_rep", "e1_p8", 1),
                 ("e1_n128", "e1_p8", 2), ("e1_n128", "e1_p1", 2), ("e1_p8", "e1_n32", 2),
                 ("e1_p1", "e1_p8", 1), ("e1_rep_d", "e1_p8_d", 1)]
        for n1, n2, panel in pairs:
            if n1 in C and n2 in C:
                a, rel, abs_s = diff(n1, n2)
                key = f"{n1}_vs_{n2}"
                d = {}
                for lo, hi in ((2.0, 40.0), (40.0, 80.0), (80.0, 100.0), (80.0, 140.0), (100.0, 140.0)):
                    m = win(a, lo, hi)
                    d[f"maxrel_a{lo}_{hi}"] = maxabs(rel, m)
                    d[f"rmsrel_a{lo}_{hi}"] = rmsv(rel, m)
                    d[f"maxabs_over_s_a{lo}_{hi}"] = maxabs(abs_s, m)
                    d[f"rmsabs_over_s_a{lo}_{hi}"] = rmsv(abs_s, m)
                out[key] = d
                ax[panel].plot(a, np.abs(abs_s), label=f"{lab[n1]} - {lab[n2]}", lw=0.8)
        c27 = series(C["e1_p27"], "h_K1_plus", "re") if "e1_p27" in C else None
        if c27 is not None:
            out["c_over_s_range_p27_a80_140"] = [float(np.min(c27[win(ref.a_of_tau(tau(C['e1_p27'])), 80, 140)] / s1)),
                                                 float(np.max(c27[win(ref.a_of_tau(tau(C['e1_p27'])), 80, 140)] / s1))]
        ax[0].set_xscale("log")
        ax[0].set_xlabel("a")
        ax[0].set_ylabel("c_+(K1) / s  (eps = 1)")
        ax[0].legend(fontsize=6)
        for i, ttl in ((1, "particle number (64^3) and rerun"), (2, "mesh")):
            ax[i].set_xscale("log")
            ax[i].set_yscale("log")
            ax[i].set_xlabel("a")
            ax[i].set_ylabel("|difference| / |s|")
            ax[i].set_title(ttl, fontsize=8)
            ax[i].legend(fontsize=5)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(os.path.join(od, f"conv_eps1.{ext}"), dpi=150)
        plt.close(fig)
        S["P12_P13"] = out

    # ---------------- P14: delta = 0.0025 ----------------
    if any(n in C for n in ("d0025_e1", "d0025_e0p3")):
        out = {}
        fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.0))
        dev = {}
        for n, delta, eps, col, ls in (("d01_e1", 0.01, 1.0, "C0", "-"), ("d01_e0p3", 0.01, 0.3, "C1", "-"),
                                       ("d0025_e1", 0.0025, 1.0, "C0", "--"), ("d0025_e0p3", 0.0025, 0.3, "C1", "--")):
            if n not in C:
                continue
            t = tau(C[n])
            a = ref.a_of_tau(t)
            s = ref.static_amplitude(delta, eps)
            g, _ = ref.g_of_tau(t)
            c = series(C[n], "h_K1_plus", "re")
            dv = c / (s * g) - 1.0
            dev[n] = (t, a, dv)
            ax[0].plot(a, c / s, color=col, ls=ls, lw=0.9, label=f"delta={delta}, eps={eps}")
            ax[1].plot(a, np.abs(dv), color=col, ls=ls, lw=0.9, label=f"delta={delta}, eps={eps}")
            ax[2].plot(a * delta / 0.01, np.abs(dv), color=col, ls=ls, lw=0.9, label=f"delta={delta}, eps={eps}")
            d = {"maxabs_dev_a2_10": maxabs(dv, win(a, 2.0, 10.0))}
            for aa in (10, 20, 30, 40, 60, 80, 100, 140):
                m = win(a, aa * 0.97, aa * 1.03)
                d[f"dev_at_a{aa}"] = float(np.mean(dv[m])) if m.any() else None
            # window: largest a with |dev| <= 0.5 percent for all dumps from a = 2 up to it
            m2 = a >= 2.0
            bad = np.flatnonzero(m2 & (np.abs(dv) > 5e-3))
            d["window_a_dev_le_0p5pct"] = float(a[bad[0] - 1]) if bad.size else float(a[-1])
            bad = np.flatnonzero(m2 & (np.abs(dv) > 1e-2))
            d["window_a_dev_le_1pct"] = float(a[bad[0] - 1]) if bad.size else float(a[-1])
            out[n] = d
        for e in ("e1", "e0p3"):
            n1, n2 = f"d01_{e}", f"d0025_{e}"
            if n1 in dev and n2 in dev:
                t1, a1, v1 = dev[n1]
                t2, a2, v2 = dev[n2]
                R = {}
                for aa in (10, 20, 30, 40, 60):
                    m1 = win(a1, aa * 0.95, aa * 1.05)
                    m2 = win(a2, aa * 0.95, aa * 1.05)
                    R[f"R_a{aa}"] = float(np.mean(v1[m1]) / np.mean(v2[m2])) if m1.any() and m2.any() else None
                C1 = {}
                for aa in (10, 15, 20, 25, 30, 35):
                    m1 = win(a1, aa * 0.97, aa * 1.03)
                    m2 = win(a2, 4 * aa * 0.97, 4 * aa * 1.03)
                    C1[f"dev0025_at_4a_over_dev01_at_a{aa}"] = float(np.mean(v2[m2]) / np.mean(v1[m1])) if m1.any() and m2.any() else None
                out[f"R_{e}"] = R
                out[f"collapse_{e}"] = C1
        ax[0].set_xscale("log")
        ax[0].set_xlabel("a")
        ax[0].set_ylabel("c_+(K1) / s")
        ax[0].legend(fontsize=6)
        for i, xl in ((1, "a"), (2, "a delta / 0.01")):
            ax[i].set_xscale("log")
            ax[i].set_yscale("log")
            ax[i].set_xlabel(xl)
            ax[i].set_ylabel("|c / (s g) - 1|")
            ax[i].axhline(5e-3, color="0.6", lw=0.6)
            ax[i].legend(fontsize=6)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(os.path.join(od, f"conv_delta.{ext}"), dpi=150)
        plt.close(fig)
        S["P14"] = out

    with open(os.path.join(od, "conv_summary.json"), "w") as f:
        json.dump(S, f, indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
