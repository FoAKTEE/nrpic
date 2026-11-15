#!/usr/bin/env python3
"""Reference delta-N statistics for the two test cases of the reproduction specification.

    python3 ref_spec.py quadratic|inflection [n_realisations]

Set-up (spec/SPEC.md section 5-6; 2512.14649 v2 PRD_v2.tex 403-424, 503-519; 2610.32592
chap_ICsim.tex 63-77, 350-359): background from N0 = 0, a* = 1 at N* (N* - N0 = 5 and 3),
lattice band k in [dk, 64 dk] with dk = a* H* (L k_sigma* = 2 pi, sigma = 1, N = 256,
k_max = N dk / 4). Every band mode is added to the coarse-grained (separate-universe)
phase-space Langevin system when sigma a H reaches k, with the noise covariance of the
linear flat-gauge mode functions (sdn/linear.py), for sigma = 1 (literal lattice timing),
0.1 and 0.01. delta N = first-passage e-folds from N* to the uniform-field surfaces
phi_bg(N_f) and phi_bg(N_e) minus their mean [JUDGEMENT: uniform field = uniform density
once every realisation is on the attractor; tested by comparing the two surfaces].
Variants: de Sitter noise (H/2pi)^2 in phi only; the lattice density of states of the
256^3 box (|n| <= 64) instead of the continuum; linear limit (noise amplitude x 1e-3);
no noise (classical check). Linear references: continuum band variance int P_R dln k and
the lattice sum sum_n P_R(k_n) / (4 pi |n|^3), with P_R from the same mode functions.
"""
import sys
import zlib
import common
from common import np, figstyle, save_results, savefig, pmap, seeds
from sdn import models, linear, langevin
import matplotlib.pyplot as plt

CASE = sys.argv[1]
NREAL = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
CH = 16
NLAT = 64          # |n| <= 64 on the 256^3 lattice
SIGMAS = (1.0, 0.1, 0.01)


def setup(case):
    if case == "quadratic":
        model, phi0, dpdN, H0 = models.quadratic_potential_position()
        N0, Nstar, Nf, Ne, Nextra = 0.0, 5.0, 13.0, 20.0, 80.0
    else:
        model = models.HiggsInflection()
        phi0 = -1.2
        dpdN, H0 = models.h0_fixing(model, phi0)
        N0, Nstar, Nf, Ne, Nextra = 0.0, 3.0, 13.0, 18.0, 250.0
    bg = linear.ClassicalBackground(model, phi0, dpdN, N0=N0, Nstar=Nstar, N_extra=Nextra)
    return model, bg, dict(N0=N0, Nstar=Nstar, Nf=Nf, Ne=Ne, phi0=phi0, dphidN0=dpdN, H0=bg.H0)


MODEL, BG, P = setup(CASE)
KMIN = BG.aH(P["Nstar"])
KMAX = NLAT * KMIN


def window(sigma):
    return BG.N_of_aH(KMIN / sigma), BG.N_of_aH(KMAX / sigma)


def table(sigma, kind):
    Na, Nb = window(sigma)
    grid = np.linspace(Na - 0.01, Nb + 0.01, 181)
    return linear.NoiseTable(BG, sigma, grid, kind=kind)


def lattice_factor_fn(sigma):
    """Variance factor (lattice shell density / continuum) as a function of N."""
    nn, cnt = linear.lattice_shell_counts(NLAT)
    edges = np.arange(0.0, np.log(NLAT) + 0.05 + 1e-9, 0.05)
    lo, hi = np.exp(edges[:-1]), np.exp(edges[1:])
    C = np.bincount(np.clip(np.searchsorted(edges, np.log(nn), side="right") - 1, 0, len(lo) - 1),
                    weights=cnt, minlength=len(lo))
    r = C / (4 * np.pi / 3 * (hi ** 3 - lo ** 3))

    def f(N):
        ln_n = np.log(sigma * BG.aH(N) / KMIN)
        i = int(np.floor(ln_n / 0.05))
        return float(r[i]) if 0 <= i < len(r) else 0.0
    return f, (edges, r)


def run_chunk(n, rng, sigma, kind, amp, latt, dN, tab):
    Na, Nb = window(sigma)
    ps, ws = BG.state(P["Nstar"])
    ends = [BG.state(P["Nf"])[0], BG.state(P["Ne"])[0]]
    var_factor = lattice_factor_fn(sigma)[0] if latt else None
    r = langevin.fpt_phase_space(MODEL, ps, ws, P["Nstar"], ends, dN, n, rng,
                                 noise=tab if kind != "none" else None, window=(Na, Nb),
                                 dN_det=0.01, N_max=P["Ne"] - P["Nstar"] + 60.0,
                                 noise_scale=amp, var_factor=var_factor)
    return r["N"]


VARIANTS = [
    # name, sigma, noise kind, amplitude, lattice DOS, dN, fraction of NREAL
    ("classical", 1.0, "none", 1.0, False, 2e-3, 16 / NREAL),
    ("s1", 1.0, "modes", 1.0, False, 2e-3, 1.0),
    ("s1_dN4e-3", 1.0, "modes", 1.0, False, 4e-3, 0.25),
    ("s0.1", 0.1, "modes", 1.0, False, 2e-3, 1.0),
    ("s0.01", 0.01, "modes", 1.0, False, 2e-3, 1.0),
    ("s0.01_desitter", 0.01, "desitter", 1.0, False, 2e-3, 0.25),
    ("s0.01_lattice", 0.01, "modes", 1.0, True, 2e-3, 1.0),
    ("s0.01_lin", 0.01, "modes", 1e-3, False, 2e-3, 0.25),
]


def moments(x, nb=20):
    m = x.mean()
    c = x - m
    v = np.mean(c ** 2)
    sk = np.mean(c ** 3) / v ** 1.5
    ku = np.mean(c ** 4) / v ** 2 - 3
    bs = np.array_split(x, nb)
    se = lambda f: np.std([f(b) for b in bs], ddof=1) / np.sqrt(nb)
    return dict(mean=m, var=v, skew=sk, exkurt=ku,
                se_mean=se(np.mean), se_var=se(np.var),
                se_skew=se(lambda b: np.mean((b - b.mean()) ** 3) / np.var(b) ** 1.5),
                se_exkurt=se(lambda b: np.mean((b - b.mean()) ** 4) / np.var(b) ** 2 - 3))


def main():
    figstyle.use_style()
    out = dict(case=CASE, params=P, kmin=KMIN, kmax=KMAX, N_end_inflation=BG.N_end,
               phi_end_inflation=BG.phi_end, nreal=NREAL)
    out["background"] = {f"N={N:g}": dict(phi=BG.state(N)[0], dphidN=BG.state(N)[1] / BG.H(N),
                                          H=BG.H(N), eps1=BG.eps1(N), eps2=BG.eps2(N))
                         for N in (P["N0"], P["Nstar"], P["Nf"], P["Ne"])}
    out["windows"] = {str(s): window(s) for s in SIGMAS}
    print("windows", out["windows"], "N_end", BG.N_end, flush=True)

    # ---- linear references
    ks = KMIN * np.exp(np.linspace(0.0, np.log(NLAT), 121))
    PRf = linear.PR_late(BG, ks, P["Nf"])
    PRe = linear.PR_late(BG, ks, P["Ne"])
    lnk = np.log(ks / KMIN)
    out["linear"] = dict(var_cont_Ne=np.trapezoid(PRe, lnk), var_cont_Nf=np.trapezoid(PRf, lnk),
                         PR_min_Ne=PRe.min(), PR_max_Ne=PRe.max(),
                         max_rel_change_Nf_to_Ne=float(np.max(np.abs(PRe / PRf - 1))))
    nn, cnt = linear.lattice_shell_counts(NLAT)
    PRn = np.exp(np.interp(np.log(nn), lnk, np.log(PRe)))
    out["linear"]["var_lattice_Ne"] = float(np.sum(cnt * PRn / (4 * np.pi * nn ** 3)))
    out["linear"]["lattice_over_cont"] = out["linear"]["var_lattice_Ne"] / out["linear"]["var_cont_Ne"]
    print("linear", out["linear"], flush=True)
    sig_lin = np.sqrt(out["linear"]["var_cont_Ne"])

    # ---- noise tables (in parallel)
    kinds = sorted({(v[1], v[2]) for v in VARIANTS if v[2] != "none"})
    tabs = dict(zip(kinds, pmap(table, kinds)))
    tdiag = {}
    for (s, kd), t in tabs.items():
        Hn = np.array([BG.H(N) for N in t.N])
        e1 = np.array([BG.eps1(N) for N in t.N])
        ref = (Hn / (2 * np.pi)) ** 2 * (1 - e1)
        tdiag[f"{s}_{kd}"] = dict(N=t.N, ff_over_dS=t.C[:, 0, 0] / ref,
                                  corr=t.C[:, 0, 1] / np.sqrt(np.maximum(t.C[:, 0, 0] * t.C[:, 1, 1], 1e-300)),
                                  pp_over_ff_H2=t.C[:, 1, 1] / np.maximum(t.C[:, 0, 0] * Hn ** 2, 1e-300))
    out["noise_tables"] = {k: dict(N=v["N"][::20], ff_over_dS=v["ff_over_dS"][::20], corr=v["corr"][::20])
                           for k, v in tdiag.items()}

    # ---- Monte Carlo
    samples = {}
    for name, s, kd, amp, latt, dN, frac in VARIANTS:
        n = max(int(NREAL * frac), 16)
        nch = CH if n >= CH * 100 else 1
        tab = tabs.get((s, kd))
        res = pmap(run_chunk, [(n // nch, r, s, kd, amp, latt, dN, tab)
                               for r in seeds(zlib.crc32(f"{CASE}:{name}".encode()), nch)])
        Nall = np.concatenate(res, axis=0)
        samples[name] = Nall
        rec = dict(n=len(Nall), sigma=s, kind=kd, amp=amp, lattice=latt, dN=dN)
        for j, lab in enumerate(("Nf", "Ne")):
            x = Nall[:, j]
            ok = np.isfinite(x)
            rec[f"n_nan_{lab}"] = int((~ok).sum())
            x = x[ok]
            N_cl = P[lab] - P["Nstar"]
            st = moments(x) if len(x) > 50 else dict(mean=x.mean(), var=np.var(x))
            st["mean_minus_classical"] = st["mean"] - N_cl
            st["surface_after_window"] = bool(P[lab] > window(s)[1] + 0.5)
            if amp != 1.0:
                st["var_rescaled"] = st["var"] / amp ** 2
            if len(x) > 50 and kd != "none":
                d = (x - x.mean()) / sig_lin
                st["tail_gt"] = {str(k): float(np.mean(d > k)) for k in (1, 2, 3, 4, 5, 6)}
                st["tail_lt"] = {str(k): float(np.mean(d < -k)) for k in (1, 2, 3, 4, 5, 6)}
                qs = [1e-5, 1e-4, 1e-3, 1e-2, 0.5, 0.99, 0.999, 0.9999, 1 - 1e-5]
                st["quantiles_dN"] = dict(zip(map(str, qs), np.quantile(x - x.mean(), qs)))
            rec[lab] = st
        if kd == "none":
            rec["classical_error"] = [float(np.nanmax(np.abs(Nall[:, j] - (P[lab] - P["Nstar"]))))
                                      for j, lab in enumerate(("Nf", "Ne"))]
        out[name] = rec
        print(name, {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items()
                                                              if kk in ("mean_minus_classical", "var", "skew", "exkurt", "se_var", "se_skew")})
                     for k, v in rec.items()}, flush=True)
    np.savez_compressed(f"{common.RUN_DIR}/ref_{CASE}_samples.npz", **samples)

    # ratios to linear
    vl = out["linear"]["var_cont_Ne"]
    out["ratios_Ne"] = {name: dict(var_over_lin=(out[name]["Ne"].get("var_rescaled", out[name]["Ne"]["var"]) / vl),
                                   se=out[name]["Ne"].get("se_var", np.nan) / vl / (out[name]["amp"] ** 2))
                        for name, *_ in VARIANTS if name != "classical"}
    out["ratios_Ne"]["s0.01_lattice"]["var_over_lattice_lin"] = (out["s0.01_lattice"]["Ne"]["var"]
                                                                / out["linear"]["var_lattice_Ne"])
    print("ratios", out["ratios_Ne"], flush=True)

    # ---- figure 1: background, noise amplitude, linear band spectrum
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 2.9))
    a1 = figstyle.inch_axes(fig, 0.62, 0.5, 2.0, 2.2)
    a2 = figstyle.inch_axes(fig, 3.25, 0.5, 2.0, 2.2)
    a3 = figstyle.inch_axes(fig, 5.85, 0.5, 2.0, 2.2)
    Ng = np.linspace(P["N0"], P["Ne"], 600)
    a1.semilogy(Ng, [BG.eps1(N) for N in Ng], color=figstyle.PAL["blue"], label="$\\epsilon_1$")
    e2 = np.array([BG.eps2(N) for N in Ng])
    a1.semilogy(Ng, np.abs(e2), color=figstyle.PAL["red"], ls="--", label="$|\\epsilon_2|$")
    cols = [figstyle.PAL["yellow"], figstyle.PAL["green"], figstyle.PAL["orange"]]
    for s, c in zip(SIGMAS, cols):
        a, b = window(s)
        a1.axvspan(a, b, color=c, alpha=0.15)
        a1.text(0.5 * (a + b), 2e-12 if CASE != "quadratic" else 4e-3, f"$\\sigma={s:g}$", fontsize=7,
                ha="center", color="k")
    for lab in ("Nf", "Ne"):
        a1.axvline(P[lab], **figstyle.MASK_LINE)
    a1.set_xlabel("$N$")
    a1.set_ylabel("slow-roll parameters")
    a1.legend(loc="lower left", fontsize=7)
    for (s, c) in zip(SIGMAS, cols):
        d = tdiag[f"{s}_modes"]
        a2.plot(d["N"], d["ff_over_dS"], color=c, label=f"$\\sigma={s:g}$")
        a2.plot(d["N"], d["corr"], color=c, ls=":")
    a2.axhline(1.0, **figstyle.THIN)
    a2.set_xlabel("$N$")
    a2.set_ylabel("$C_{\\phi\\phi}/[(H/2\\pi)^2(1-\\epsilon_1)]$; corr. (dotted)")
    a2.set_yscale("symlog", linthresh=1.0)
    a2.legend(loc="best", fontsize=7)
    a3.loglog(ks / KMIN, PRe, color=figstyle.PAL["blue"], label="$N_e$")
    a3.loglog(ks / KMIN, PRf, color=figstyle.PAL["red"], ls="--", label="$N_f$")
    a3.set_xlabel("$k/\\mathrm{d}k$")
    a3.set_ylabel("$\\mathcal{P}_\\mathcal{R}(k)$")
    a3.legend(loc="best", fontsize=7)
    savefig(fig, f"ref_{CASE}_setup")
    plt.close(fig)

    # ---- figure 2: PDF of delta N and variance ratios
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.1))
    b1 = figstyle.inch_axes(fig, 0.7, 0.5, 3.2, 2.4)
    b2 = figstyle.inch_axes(fig, 4.75, 0.5, 3.0, 2.4)
    lim = 8.0
    edges = np.linspace(-lim, lim, 161) if CASE == "quadratic" else np.linspace(-lim, 3 * lim, 241)
    cc = 0.5 * (edges[1:] + edges[:-1])
    xs = np.linspace(edges[0], edges[-1], 400)
    b1.semilogy(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), **figstyle.GUIDE, label="Gaussian, linear variance")
    show = [("s1", figstyle.PAL["yellow"]), ("s0.1", figstyle.PAL["green"]), ("s0.01", figstyle.PAL["red"]),
            ("s0.01_lattice", figstyle.PAL["orange"])]
    for name, c in show:
        x = samples[name][:, 1]
        x = x[np.isfinite(x)]
        d = (x - x.mean()) / sig_lin
        h, _ = np.histogram(d, edges)
        dens = h / (len(d) * np.diff(edges))
        ok = h >= 10
        b1.errorbar(cc[ok], dens[ok], yerr=np.sqrt(h[ok]) / (len(d) * np.diff(edges)[ok]), fmt="o", ms=1.8,
                    color=c, lw=0.7, label=name.replace("s", "$\\sigma=$", 1).replace("_lattice", ", lattice"))
    b1.set_ylim(1e-7, 1.0)
    b1.set_xlabel("$\\delta\\mathcal{N}/\\sigma_\\mathrm{lin}$")
    b1.set_ylabel("probability density")
    b1.legend(loc="upper right", fontsize=7)
    names = [v[0] for v in VARIANTS if v[0] != "classical"]
    for i, name in enumerate(names):
        r = out["ratios_Ne"][name]
        b2.errorbar(i, r["var_over_lin"], yerr=3 * r["se"], fmt="o", color=figstyle.PAL["blue"], ms=4)
        sk = out[name]["Ne"].get("skew", np.nan)
        b2.errorbar(i + 0.15, 1 + sk, yerr=3 * out[name]["Ne"].get("se_skew", 0), fmt="s",
                    color=figstyle.PAL["red"], ms=3)
    b2.axhline(1.0, **figstyle.THIN)
    b2.axhline(out["linear"]["lattice_over_cont"], **figstyle.MASK_LINE)
    b2.set_xticks(range(len(names)))
    b2.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=6.5)
    b2.minorticks_off()
    b2.set_ylabel("var/var$_\\mathrm{lin}$ (circles), 1+skewness (squares)")
    savefig(fig, f"ref_{CASE}_pdf")
    plt.close(fig)
    save_results(f"ref_{CASE}", out)


if __name__ == "__main__":
    main()
