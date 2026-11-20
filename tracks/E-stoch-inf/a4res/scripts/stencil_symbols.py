#!/usr/bin/env python3
"""Step 1 of package a4res (Track E): the symbols of AthenaK's centred differences, read
from the source, and core's remark on the A2 reference.

    python3 stencil_symbols.py --out DIR [--fd PATH] [--skip-a2]

1. Parses the coefficients of the scalar first difference Dx and the scalar second
   difference Dxx for NGHOST = 2, 3, 4 from athenak/src/utils/finite_diff.hpp (the file
   the Z4c right-hand side and the constraints use: z4c_calcrhs.cpp, z4c_adm.cpp), and
   forms per direction
       D1 exp(i k x) = i q exp(i k x),     Dxx exp(i k x) = -kap exp(i k x),
       q h = Im sum_m c_m e^{i m th},      kap h^2 = -Re sum_m d_m e^{i m th},
   th = k h = 2 pi / (cells per wavelength); the mixed derivative Dxy is the product of
   two first differences (symbol -q_a q_b).  mu = kap - q^2 is the mismatch between the
   second difference and the first difference applied twice; mu/k^2 = (kap h^2 - (q
   h)^2)/th^2.  Core's numbers (git show core/scalar-3:tracks/core/interfaces/
   scalar_field_3.md section 4): mu/k^2 = 0.110, 2.6e-3, 4.4e-5 at 4, 8, 16 cells;
   second difference 1.8 percent low and first difference twice 12.8 percent low at
   k h = pi/2.
2. Core's remark on SCOPE 4 A2: the 'stencil-k^2' reference of the ladder (6.2e-3 at
   256^3, against 1.2e-4 for the continuum one; ../../ladder/results/final/
   P256_judge.json) "may use the second-order stencil symbol".  The reference of
   ladder_lib.py (k2_stencil) is evolved here per wave vector with the continuum k^2,
   with the sixth-order symbol (as ladder_lib), with the fourth-order one and with the
   second-order one, from the rows of the P256 mode file to the last dump of P256
   (t = 8.5), for every wave vector class |n|^2 <= 1024 (|n| <= k_max/2 of P256); the
   largest |R_sym/R_cont - 1| is compared with the ladder's 6.25e-3 (largest relative
   difference of the two references) and 6.16e-3 (largest deviation of the run from the
   stencil reference).
Writes DIR/symbols.json and DIR/fig_symbols.png."""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "ladder", "scripts"))
sys.path.insert(0, HERE)

CORE = dict(mu_over_k2={4: 0.110, 8: 2.6e-3, 16: 4.4e-5}, d2_low_at_pi2=0.018,
            d1sq_low_at_pi2=0.128)
CELLS = [4, 5, 6, 8, 10, 12, 16]


def _function_blocks(text, name):
    """Bodies of the template functions `name` whose stencil is on a scalar quant(m,k,...)
    (the scalar overload: the first argument after m is k)."""
    out = []
    for mt in re.finditer(r"Real\s+%s\s*\(" % name, text):
        start = mt.start()
        end = text.find("return out", start)
        body = text[start:end]
        if re.search(r"quant\(m,\s*k\+", body) or re.search(r"quant\(m,\s*k,", body):
            out.append(body)
    return out


def _ghost_block(body, ng):
    m = re.search(r"NGHOST\s*==\s*%d\s*\)\s*\{(.*?)\n\s*\}" % ng, body, re.S)
    if m is None:
        raise ValueError(f"no NGHOST == {ng} block")
    return m.group(1)


NUM = r"([+-]?\s*\d+\.?\d*(?:\s*/\s*\d+\.?\d*)?)"


def _value(s):
    s = s.replace(" ", "")
    if "/" in s:
        a, b = s.split("/")
        return float(a)/float(b)
    return float(s)


def parse_coefficients(path):
    """{'D1': {ng: {offset: coef}}, 'D2': {...}} from finite_diff.hpp."""
    text = open(path).read()
    res = {}
    for key, name in (("D1", "Dx"), ("D2", "Dxx")):
        body = _function_blocks(text, name)[0]
        res[key] = {}
        for ng in (2, 3, 4):
            blk = _ghost_block(body, ng)
            coef = {}
            for c, off in re.findall(NUM + r"\s*\*\s*quant\(m,\s*k\+\(\s*(-?\d+)\)", blk):
                coef[int(off)] = coef.get(int(off), 0.0) + _value(c)
            for c in re.findall(NUM + r"\s*\*\s*quant\(m,\s*k,", blk):
                coef[0] = coef.get(0, 0.0) + _value(c)
            res[key][ng] = dict(sorted(coef.items()))
    return res


def symbols(coef, th):
    """q h and kap h^2 of the coefficient sets at phases th."""
    th = np.asarray(th, float)
    s1 = sum(c*np.exp(1j*m*th) for m, c in coef["D1"].items())
    s2 = sum(c*np.exp(1j*m*th) for m, c in coef["D2"].items())
    return s1.imag, -s2.real, float(np.abs(s1.real).max()), float(np.abs(s2.imag).max())


def a2_remark(coefs, out):
    """Largest |R_sym/R_cont - 1| at t = 8.5 over the wave-vector classes |n|^2 <= 1024 of
    P256 (N = 256), for the sixth-, fourth- and second-order symbols of k^2."""
    import ladder_lib as LL
    nmesh, n2max, t_f = 256, 1024, 8.5
    mf = os.path.join(TRACK, "ladder", "inputs", "modes_n4096.txt")
    n2f, r0f, dr0f = LL.read_modefile(mf)
    nmax = 32
    r = np.arange(0, nmax + 1)
    a, b, c = np.meshgrid(r, r, r, indexing="ij")
    n = np.stack([a.ravel(), b.ravel(), c.ravel()], axis=1)
    keep = (n[:, 0] >= n[:, 1]) & (n[:, 1] >= n[:, 2])
    n = n[keep]
    n2 = (n*n).sum(axis=1)
    n = n[(n2 >= 1) & (n2 <= n2max)]
    n2 = (n*n).sum(axis=1)
    idx = np.searchsorted(n2f, n2)
    assert np.array_equal(n2f[idx], n2)
    k = np.sqrt(n2.astype(float))
    h = 2.0*np.pi/nmesh
    th = 2.0*np.pi*n/nmesh
    res = dict(N=nmesh, n2max=n2max, t=t_f, classes=int(n.shape[0]),
               modefile=os.path.relpath(mf, REPO))
    ref_c = LL.LinearReference(k, r0f[idx], dr0f[idx], t_f + 0.01, t_eval=[t_f])
    rc, _ = ref_c.modes(t_f)
    curves = {}
    for ng, lab in ((4, "sixth"), (3, "fourth"), (2, "second")):
        kap = symbols(coefs_ng(coefs, ng), th)[1]
        k2 = kap.sum(axis=1)/h**2
        if ng == 4:
            k2_lib = LL.k2_stencil(n, nmesh)
            res["ladder_lib_k2_equals_sixth_order_symbol_max_rel"] = float(
                np.abs(k2_lib/k2 - 1.0).max())
        ref = LL.LinearReference(k, r0f[idx], dr0f[idx], t_f + 0.01, k2_shell=k2,
                                 t_eval=[t_f])
        rs, _ = ref.modes(t_f)
        d = np.abs(rs/rc - 1.0)
        j = int(np.argmax(d))
        res[lab] = dict(max_rel_diff=float(d.max()), worst_n=[int(x) for x in n[j]],
                        k2_rel_error_worst=float(k2[j]/k[j]**2 - 1.0),
                        at_n32_axis=float(d[np.nonzero((n[:, 0] == 32) &
                                                       (n[:, 1] == 0))[0][0]]))
        curves[lab] = d
        print(f"A2 remark: {lab:6s} symbol: largest |R_sym/R_cont - 1| = {d.max():.3e} "
              f"at n = {n[j]}")
    return res, k, curves


def coefs_ng(coefs, ng):
    return dict(D1=coefs["D1"][ng], D2=coefs["D2"][ng])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fd", default=os.path.join(REPO, "athenak", "src", "utils",
                                                 "finite_diff.hpp"))
    ap.add_argument("--skip-a2", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    coefs = parse_coefficients(a.fd)
    res = dict(source=os.path.relpath(a.fd, REPO),
               coefficients={k: {str(ng): {str(o): c for o, c in v.items()}
                                 for ng, v in d.items()} for k, d in coefs.items()})
    # expected sixth-order coefficients (as written in ladder JOURNAL entry 8)
    six = coefs_ng(coefs, 4)
    exp1 = {-3: -1/60, -2: 3/20, -1: -3/4, 1: 3/4, 2: -3/20, 3: 1/60}
    exp2 = {-3: 1/90, -2: -3/20, -1: 3/2, 0: -49/18, 1: 3/2, 2: -3/20, 3: 1/90}
    res["sixth_order_coefficients_as_expected"] = bool(
        all(abs(six["D1"].get(o, 0) - c) < 1e-15 for o, c in exp1.items()) and
        all(abs(six["D2"].get(o, 0) - c) < 1e-15 for o, c in exp2.items()) and
        set(six["D1"]) == set(exp1) and set(six["D2"]) == set(exp2))
    # order of accuracy: Taylor moments
    for ng in (2, 3, 4):
        cf = coefs_ng(coefs, ng)
        m1 = [sum(c*o**p for o, c in cf["D1"].items()) for p in range(0, 9)]
        m2 = [sum(c*o**p for o, c in cf["D2"].items()) for p in range(0, 9)]
        res[f"moments_ng{ng}"] = dict(D1=m1, D2=m2)
    rows = []
    for cells in CELLS + [24, 32]:
        th = 2.0*np.pi/cells
        row = dict(cells_per_wavelength=cells, k_dx=th)
        for ng, lab in ((4, "sixth"), (3, "fourth"), (2, "second")):
            qh, kap, re1, im2 = symbols(coefs_ng(coefs, ng), th)
            row[lab] = dict(q_over_k=float(qh/th), kap_over_k2=float(kap/th**2),
                            q2_over_k2=float(qh**2/th**2),
                            mu_over_k2=float((kap - qh**2)/th**2),
                            antisym_check=re1, sym_check=im2)
        if cells in CORE["mu_over_k2"]:
            row["core_mu_over_k2"] = CORE["mu_over_k2"][cells]
            row["rel_diff_to_core"] = row["sixth"]["mu_over_k2"]/CORE["mu_over_k2"][cells] - 1
        rows.append(row)
    res["table"] = rows
    qh, kap, _, _ = symbols(six, np.pi/2)
    res["at_pi_over_2"] = dict(
        d2_low=float(1 - kap/(np.pi/2)**2), d1sq_low=float(1 - qh**2/(np.pi/2)**2),
        second_order_d2_low=float(1 - symbols(coefs_ng(coefs, 2), np.pi/2)[1]/(np.pi/2)**2),
        core_d2_low=CORE["d2_low_at_pi2"], core_d1sq_low=CORE["d1sq_low_at_pi2"])
    print("cells  mu/k^2 (sixth)   core      kap/k^2-1   q^2/k^2-1")
    for r in rows:
        s = r["sixth"]
        print(f"{r['cells_per_wavelength']:5d}  {s['mu_over_k2']:.4e}  "
              f"{r.get('core_mu_over_k2', float('nan')):.3e}  "
              f"{s['kap_over_k2'] - 1:+.4e}  {s['q2_over_k2'] - 1:+.4e}")
    print("at pi/2:", res["at_pi_over_2"])
    kk = None
    if not a.skip_a2:
        res["a2"], kk, curves = a2_remark(coefs, a.out)
        jd = json.load(open(os.path.join(TRACK, "ladder", "results", "final",
                                         "P256_judge.json")))
        res["a2"]["ladder_P256"] = dict(
            continuum_max_D_half=jd["A2"]["max_D_half"],
            stencil_max_D_half=jd["A2"]["stencil_reference"]["max_D_half"],
            max_rel_diff_references=jd["A2"]["stencil_reference"]["max_rel_diff_references"],
            locator="tracks/E-stoch-inf/ladder/results/final/P256_judge.json "
                    "(run E-20261115-194633-9e04ed8)")
    with open(os.path.join(a.out, "symbols.json"), "w") as fp:
        json.dump(res, fp, indent=1)

    # ---- figure
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    ncol = 3 if kk is not None else 2
    fig, ax = plt.subplots(1, ncol, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.93, wspace=0.42)
    th = np.linspace(2*np.pi/40, np.pi/2*1.02, 400)
    cells = 2*np.pi/th
    cols = {"sixth": fs.PAL["red"], "fourth": fs.PAL["green"], "second": fs.PAL["orange"]}
    for ng, lab in ((4, "sixth"), (3, "fourth"), (2, "second")):
        qh, kap, _, _ = symbols(coefs_ng(coefs, ng), th)
        ax[0].plot(cells, kap/th**2, "-", color=cols[lab], label=f"$\\kappa/k^2$, {lab}")
        ax[0].plot(cells, qh**2/th**2, "--", color=cols[lab], label=f"$q^2/k^2$, {lab}")
        mu = np.abs(kap - qh**2)/th**2
        ax[1].plot(cells, mu, "-", color=cols[lab], label=f"{lab} order")
    ax[0].axhline(1.0, **fs.REF_LINE)
    ax[0].set_xscale("log")
    ax[0].set_xlabel("cells per wavelength")
    ax[0].set_ylabel("symbol over continuum")
    ax[0].set_ylim(0.5, 1.03)
    ax[0].legend(fontsize=5.5, loc="lower right", ncol=1)
    cc = sorted(CORE["mu_over_k2"])
    ax[1].plot(cc, [CORE["mu_over_k2"][c] for c in cc], "o", mfc="none", ms=7,
               color=fs.PAL["blue"], label="core (scalar_field_3.md)")
    ax[1].plot(CELLS, [r["sixth"]["mu_over_k2"] for r in rows if r["cells_per_wavelength"]
                       in CELLS], "x", color="k", ms=5, label="this check, sixth")
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("cells per wavelength")
    ax[1].set_ylabel(r"$|\mu|/k^2 = |\kappa - q^2|/k^2$")
    ax[1].legend(fontsize=5.5, loc="lower left")
    for x in CELLS:
        ax[1].axvline(x, **fs.MASK_LINE)
    if kk is not None:
        for lab in ("sixth", "fourth", "second"):
            ax[2].plot(kk, curves[lab], ".", ms=1.5, color=cols[lab],
                       label=f"{lab}-order $k^2$")
        lp = res["a2"]["ladder_P256"]
        ax[2].axhline(lp["max_rel_diff_references"], color=fs.PAL["blue"], lw=1.2,
                      label="ladder: references differ (P256)")
        ax[2].axhline(lp["continuum_max_D_half"], color=fs.PAL["blue"], lw=1.2, ls=":",
                      label="ladder: run vs continuum ref.")
        ax[2].set_yscale("log")
        ax[2].set_xlabel(r"$|n|$ ($N = 256$)")
        ax[2].set_ylabel(r"$|R_{\rm sym}/R_{\rm cont} - 1|$, $t = 8.5$")
        ax[2].legend(fontsize=5.5, loc="lower right")
    from matplotlib.ticker import FixedLocator, NullFormatter
    for x in ax[:2]:
        x.xaxis.set_major_locator(FixedLocator([4, 8, 16, 32]))
        x.xaxis.set_minor_formatter(NullFormatter())
        x.set_xticklabels(["4", "8", "16", "32"])
    for i, x in enumerate(ax):
        x.set_title("(%s)" % "abc"[i], loc="left", fontsize=8)
    fig.savefig(os.path.join(a.out, "fig_symbols.png"), dpi=200)
    print("wrote", os.path.join(a.out, "symbols.json"))


if __name__ == "__main__":
    main()
