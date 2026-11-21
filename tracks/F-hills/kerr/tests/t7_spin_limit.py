"""T7: the spin -> 0 limit of the inclined HRNA set-up (hrna_incl), and its coordinate dependence.

(i)  Convergence in a: the same encounter (r_p = 10, orbit inclination 0.6 from the equatorial
     maximum L_z, binary iota/Omega/phase fixed) with a = 1e-1 ... 1e-6 against a = 0 in the
     chart 'bks' of hrna_bks.py (Boyer-Lindquist time, Kerr-Schild space; JOURNAL entry 2):
     final binary energy, eccentricity, orientation and CM direction differ from a = 0 by an
     amount proportional to a (slope 1 on log-log).
(ii) Spin breaks the orbit-inclination symmetry: the orbit with L_z = +L_max(a) and its mirror
     L_z = L_min(a) (same r_p, same binary orientation in the orbit frame), compared after the
     rotation by pi about x that maps one orbit onto the other.  At a = 0 they are the same
     encounter rotated (T5); the difference grows from 0 like a.
(iii) Coordinate dependence at a = 0: 'cks' against 'sch' (Schwarzschild in Cartesian form) over
     64 binary orientations (8 iota x 8 phases, Omega = 0.5) at r_p = 7, 10, 13: count of
     survival outcomes that differ, and the spread of a_fin.

Run: <venv>/bin/python -I tests/t7_spin_limit.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "scripts"))
import hrna_incl as H  # noqa: E402

P = dict(mb=6.25e-6, q12=2 / 3, a0=0.125, r0=100.0)       # 2402.02178 fiducial (main.tex:486, 504-515)
BIN = [dict(iota=2.0, Omega=0.7, phase=0.4), dict(iota=1.3, Omega=0.2, phase=2.1)]


def enc(coords, spin, rp, Lz, b, **kw):
    r = H.run_incl("hrna", coords, spin, P["mb"], P["q12"], P["a0"], rp, Lz, b["iota"], b["Omega"],
                   b["phase"], P["r0"], record=1, **kw)
    y = r["rec_y"][-1]
    m1 = P["mb"] / (1 + P["q12"])
    m2 = P["mb"] - m1
    xc = (m1 * y[0:3] + m2 * y[6:9]) / P["mb"]
    el = H.binary_elements(y, m1, m2)
    return dict(survived=r["survived"], Eb=r["Eb_fin"], e=r["e_fin"], a_fin=r["a_fin"],
                Lhat=np.array(el["Lhat"]), cdir=xc / np.linalg.norm(xc), plunged=r["plunged"],
                r_peri=r["r_peri"])


def dist(A, B, R=None):
    """Differences of the final binary between two encounters (relative energy, e, angles);
    R rotates B's vectors first."""
    R = np.eye(3) if R is None else R
    return dict(dEb_rel=abs(A["Eb"] - B["Eb"]) / abs(B["Eb"]), de=abs(A["e"] - B["e"]),
                dLhat=float(np.linalg.norm(A["Lhat"] - R @ B["Lhat"])),
                dcdir=float(np.linalg.norm(A["cdir"] - R @ B["cdir"])),
                dr_peri=abs(A["r_peri"] - B["r_peri"]))


CH = "bks"


def part_i_ii():
    rp, io = 10.0, 0.6
    spins = [1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 1e-4, 1e-5, 1e-6]
    out = []
    for kb, b in enumerate(BIN):
        Lmax0 = H.lz_range(rp, 0.0)[1]
        ref = enc(CH, 0.0, rp, Lmax0 * math.cos(io), b)
        ref_eq = enc(CH, 0.0, rp, Lmax0, b)
        Rx = H.rot_x(math.pi)
        for s in spins:
            lo, hi = H.lz_range(rp, s)
            A = enc(CH, s, rp, hi * math.cos(io), b)           # (i) inclined orbit, spin s
            Bp = enc(CH, s, rp, hi, b)                         # (ii) equatorial, L_z > 0
            Bm = enc(CH, s, rp, lo, b)                         # (ii) mirror, L_z < 0
            out.append(dict(binary=kb, spin=s, i=dist(A, ref), ii=dist(Bp, Bm, Rx),
                            ii_vs_a0=dist(Bp, ref_eq), survived=(A["survived"], ref["survived"],
                                                                 Bp["survived"], Bm["survived"]),
                            e_ref=ref["e"], Eb_ref=ref["Eb"]))
        # (ii) at a = 0.9: the mirror pair differs at order one
        lo, hi = H.lz_range(rp, 0.9)
        Bp = enc(CH, 0.9, rp, hi, b)
        Bm = enc(CH, 0.9, rp, lo, b)
        out.append(dict(binary=kb, spin=0.9, ii=dist(Bp, Bm, Rx), survived=(None, None, Bp["survived"],
                                                                         Bm["survived"])))
    return out


def part_iii():
    res = []
    iotas = np.linspace(0, math.pi, 8)
    phases = np.linspace(0, math.pi, 8, endpoint=False)
    for rp in (7.0, 10.0, 13.0):
        Lmax = H.lz_range(rp, 0.0)[1]
        rows = []
        for io in iotas:
            for ph in phases:
                b = dict(iota=float(io), Omega=0.5, phase=float(ph))
                c = enc("cks", 0.0, rp, Lmax, b)
                s = enc("sch", 0.0, rp, Lmax, b)
                rows.append(dict(iota=float(io), phase=float(ph), surv_cks=c["survived"],
                                 surv_sch=s["survived"], afin_cks=c["a_fin"], afin_sch=s["a_fin"],
                                 e_cks=c["e"], e_sch=s["e"]))
        ndiff = sum(r["surv_cks"] != r["surv_sch"] for r in rows)
        both = [r for r in rows if r["surv_cks"] and r["surv_sch"]]
        da = [abs(r["afin_cks"] - r["afin_sch"]) for r in both]
        res.append(dict(rp=rp, n=len(rows), n_outcome_diff=int(ndiff),
                        surv_frac_cks=float(np.mean([r["surv_cks"] for r in rows])),
                        surv_frac_sch=float(np.mean([r["surv_sch"] for r in rows])),
                        median_dafin=float(np.median(da)) if da else None,
                        max_dafin=float(np.max(da)) if da else None, rows=rows))
    return res


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    r12 = part_i_ii()
    r3 = part_iii()
    # slopes of log|diff| against log a for (i) and (ii), spins <= 1e-2 (asymptotic range)
    slopes = {}
    for kb in range(len(BIN)):
        rows = [r for r in r12 if r["binary"] == kb and r["spin"] <= 1e-2]
        s = np.log10([r["spin"] for r in rows])
        for part, key in (("i", "dEb_rel"), ("i", "dLhat"), ("ii", "dEb_rel"), ("ii", "dLhat")):
            v = np.log10([max(r[part][key], 1e-300) for r in rows])
            slopes[f"bin{kb}_{part}_{key}"] = float(np.polyfit(s, v, 1)[0])
    # pass rule of JOURNAL entry 2: orientation converges like a (slope 0.8-1.2); energies and
    # eccentricities, whose final values carry a noise floor from the step at which the run stops
    # (about 1e-4 relative), are within 1e-3 of a = 0 for a <= 1e-3
    ok_slope = all(0.8 < v < 1.2 for k, v in slopes.items() if k.endswith("dLhat"))
    small = [r for r in r12 if r["spin"] <= 1e-3]
    ok_floor = all(r["i"]["dEb_rel"] < 1e-3 and r["ii"]["dEb_rel"] < 1e-3 for r in small) and \
        all(r["ii"]["de"] < 1e-3 for r in small if r["survived"][2])
    ok_i = bool(ok_slope and ok_floor)
    # (iii) has no pass rule since entry 2 (it records the 'cks' defect); entry 1's rule kept as info
    ok_iii = all(r["n_outcome_diff"] <= 5 for r in r3)
    res = dict(i_ii=r12, iii=[{k: v for k, v in r.items() if k != "rows"} for r in r3],
               iii_rows=r3, slopes=slopes, pass_i_ii_slope=bool(ok_i),
               info_iii_entry1_rule_at_most_5_differ=bool(ok_iii))
    with open(os.path.join(outdir, "t7_spin_limit.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o))
    print(json.dumps(dict(slopes=slopes, iii=res["iii"], pass_i_ii_slope=ok_i, info_iii=ok_iii),
                     indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.9))
    ax1 = fs.inch_axes(fig, 0.7, 0.5, 2.15, 2.2)
    ax2 = fs.inch_axes(fig, 3.35, 0.5, 2.15, 2.2)
    ax3 = fs.inch_axes(fig, 6.0, 0.5, 1.9, 2.2)
    cols = fs.series_colors(4)
    for kb, ls in zip(range(len(BIN)), ("-", "--")):
        rows = [r for r in r12 if r["binary"] == kb and r["spin"] < 0.5]
        s = np.array([r["spin"] for r in rows])
        for k, (key, lab) in enumerate((("dEb_rel", r"$|\Delta E_b|/|E_b|$"), ("dLhat", r"$|\Delta\hat L_b|$"))):
            ax1.loglog(s, [r["i"][key] for r in rows], ls, color=cols[k], marker="o", ms=3,
                       label=lab if kb == 0 else None)
            ax2.loglog(s, [r["ii"][key] for r in rows], ls, color=cols[k], marker="o", ms=3)
        r9 = [r for r in r12 if r["binary"] == kb and r["spin"] == 0.9][0]
        ax2.plot([0.9], [r9["ii"]["dEb_rel"]], marker="s", color=cols[0], ls="none")
        ax2.plot([0.9], [r9["ii"]["dLhat"]], marker="s", color=cols[1], ls="none")
    for ax in (ax1, ax2):
        xs = np.array([1e-6, 1e-1])
        ax.loglog(xs, 1e-1 * xs, ":", color="0.5", label=r"$\propto a$")
        ax.set_xlabel(r"spin $a/M$")
    ax1.set_ylabel(r"difference to $a=0$")
    ax1.set_title("(i) inclined orbit vs $a=0$", fontsize=8)
    ax2.set_title(r"(ii) $L_z>0$ vs mirror $L_z<0$", fontsize=8)
    ax1.legend(fontsize=6)
    for k, r in enumerate(r3):
        ax3.bar(k - 0.2, r["surv_frac_cks"], 0.4, color=cols[2], label="cks" if k == 0 else None)
        ax3.bar(k + 0.2, r["surv_frac_sch"], 0.4, color=cols[3], label="sch" if k == 0 else None)
        ax3.text(k, max(r["surv_frac_cks"], r["surv_frac_sch"]) + 0.03,
                 f"{r['n_outcome_diff']}/64", ha="center", fontsize=6)
    ax3.set_xticks(range(len(r3)))
    ax3.set_xticklabels([f"{r['rp']:g}" for r in r3])
    ax3.set_xlabel(r"$r_p$ [$r_g$], $a=0$")
    ax3.set_ylabel("survival fraction (64 orientations)")
    ax3.set_ylim(0, 1.15)
    ax3.set_title("(iii) cks vs sch", fontsize=8)
    ax3.legend(fontsize=6, loc="lower right")
    fs.save(fig, os.path.join(outdir, "t7_spin_limit"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
