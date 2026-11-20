"""V1 (background), V2 (R^NR per mode, shell spectrum), V3 (freezing) from my own passes.

usage: v123.py OUTDIR PERMODE_DIR [PERMODE_DIR ...]
Reads permode_<KEY>.npz (my extraction) and the records <basename>.sf.hst/.sf.con.hst of
every catalogue run (V1), integrates my own background and MS references, and writes
OUTDIR/v123.json (numbers) and OUTDIR/v123_fig.npz (what the figure scripts plot).
"""
import os
import sys
import glob
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, alpha as A, ref, catalog as C  # noqa: E402

out = sys.argv[1]
pdirs = sys.argv[2:]
os.makedirs(out, exist_ok=True)
runs = C.catalog()
DECK = dict(phi0=-2.66679478988261254e+00, pi0=2.97300406808996935e-02,
            mass=1.82877655899024605e-01)
bg = ref.CodeBackground(DECK["phi0"], DECK["pi0"], DECK["mass"], t_end=9.0)
L = 2.0 * np.pi
SEED = 20261115
fix = ref.quadratic_fix()
bgp = ref.phys_background(fix)
HSTAR = float(ref.phys_state(bgp, fix, 5.0)["H"])
res = dict(HSTAR=HSTAR)
figd = {}

# ------------------------------------------------------------------ V1 from the records
v1 = {}
for key, r in sorted(runs.items()):
    p = os.path.join(r["dir"], "sr.sf.hst")
    if not os.path.exists(p):
        v1[key] = "no record"
        continue
    cols, d = nrsf.read_record(p)
    t = d[:, cols.index("time")]
    b = bg(t)
    dev = {}
    for nm, ref_ in (("<phi>", b["phi"]), ("<Pi>", b["Pi"]), ("<K>", b["K"])):
        x = d[:, cols.index(nm)]
        rel = np.abs(x / ref_ - 1.0)
        dev[nm] = dict(max=float(rel.max()), t_at_max=float(t[rel.argmax()]), final=float(rel[-1]))
        figd[f"v1_{key}_{nm}"] = np.stack([t, rel])
    chi = d[:, cols.index("<chi>")]
    ef = -0.5 * np.log(chi)
    dev["efolds"] = dict(max_abs=float(np.max(np.abs(ef - b["lna"]))))
    al = d[:, cols.index("<alpha>")]
    dev["alpha"] = dict(max_abs=float(np.max(np.abs(al - 1.0))))
    dev["t_end"] = float(t[-1])
    dev["ncycles"] = int(len(t))
    # the lockstep background the code integrates beside the fields (record columns 19-21)
    if "phi_b" in cols:
        dev["lockstep_phi_b"] = float(np.max(np.abs(d[:, cols.index("phi_b")] / b["phi"] - 1)))
        dev["lockstep_Pi_b"] = float(np.max(np.abs(d[:, cols.index("Pi_b")] / b["Pi"] - 1)))
        dev["lockstep_ln_a"] = float(np.max(np.abs(d[:, cols.index("ln_a")] - b["lna"])))
    v1[key] = dev
res["V1_records"] = v1

# ------------------------------------------------------------------ per-mode data
pm = {}
for d_ in pdirs:
    for f in glob.glob(os.path.join(d_, "permode_*.npz")):
        key = os.path.basename(f)[len("permode_"):-4]
        pm[key] = dict(np.load(f))

v1d, v2, v3 = {}, {}, {}
for key, z in sorted(pm.items()):
    r = runs[key]
    t = z["time"]
    b = bg(t)
    mm = z["means"]
    v1d[key] = {nm: float(np.max(np.abs(mm[:, i] / b[ref_] - 1)))
                for i, (nm, ref_) in enumerate((("<phi>", "phi"), ("<Pi>", "Pi")))}
    v1d[key]["<K>"] = float(np.max(np.abs(mm[:, 3] / b["K"] - 1)))
    v1d[key]["efolds"] = float(np.max(np.abs(-0.5 * np.log(mm[:, 2]) - b["lna"])))
    v1d[key]["alpha"] = float(np.max(np.abs(mm[:, 4] - 1)))

    # my MS reference from the run's own mode file (initial data at N*)
    n2f, R0, dR0 = ref.read_mode_file(r["mode_file"])
    keep = n2f <= r["nmax2"]
    n2f, R0, dR0 = n2f[keep], R0[keep], dR0[keep]
    k = np.sqrt(n2f.astype(float))
    Rms, _ = ref.ms_code(bg, k, R0, dR0, t)
    Rdf, _ = ref.ms_code(bg, k, R0, dR0, t, deformed=True)
    nv = z["n"]
    q2 = np.sum(nv * nv, axis=1)
    lut = {int(q): i for i, q in enumerate(n2f)}
    idx = np.array([lut[int(q)] for q in q2])
    al = A.alphas(nv, SEED)
    W = ref.window(np.sqrt(q2)[None, :], b["a"][:, None], b["H"][:, None])
    pred = L ** -1.5 * r["scale"] * W * Rms[:, idx] * al[None, :]
    RN = z["R"]
    rel = np.abs(RN / pred - 1.0)
    half = q2 <= r["nmax2"] / 4.0
    kmax = np.sqrt(r["nmax2"])
    # last dump and the dump at t = 4.5 (last dump common to all rungs)
    i45 = int(np.argmin(np.abs(t - 4.5)))
    def summary(i):
        return dict(time=float(t[i]), N=float(b["lna"][i]),
                    max_rel_khalf=float(rel[i, half].max()),
                    n_at_max=nv[half][rel[i, half].argmax()].tolist(),
                    median_rel_khalf=float(np.median(rel[i, half])),
                    max_rel_all=float(rel[i].max()),
                    n_at_max_all=nv[rel[i].argmax()].tolist(),
                    frac_all_below_002=float(np.mean(rel[i] < 0.02)),
                    nmodes_khalf=int(half.sum()), nmodes=int(len(nv)))
    v2[key] = dict(last=summary(len(t) - 1), t45=summary(i45),
                   max_rel_khalf_vs_t=[float(x) for x in rel[:, half].max(axis=1)],
                   time=[float(x) for x in t], N=[float(x) for x in b["lna"]])
    # per shell at the last dump: max |rel|, alpha-normalised and raw spectra
    il = len(t) - 1
    sh = np.unique(q2)
    shmax = np.array([rel[il, q2 == q].max() for q in sh])
    shmed = np.array([np.median(rel[il, q2 == q]) for q in sh])
    figd[f"v2_{key}_shell"] = np.stack([np.sqrt(sh), shmax, shmed])
    figd[f"v2_{key}_vs_t"] = np.stack([b["lna"], rel[:, half].max(axis=1), rel[:, ~half].max(axis=1)
                                       if (~half).any() else rel[:, half].max(axis=1)])
    # spectrum at the last dump: Delta = k^3 L^3 |c|^2/(2 pi^2) (raw), and with |alpha|^2 out
    c2 = np.abs(RN[il]) ** 2 * L ** 3
    raw = np.array([np.mean(c2[q2 == q]) for q in sh])
    nrm = np.array([np.mean(c2[q2 == q] / np.abs(al[q2 == q]) ** 2) for q in sh])
    msk = np.array([abs(Rms[il, lut[int(q)]]) ** 2 for q in sh])
    M = np.array([np.sum(q2 == q) for q in sh])
    ks = np.sqrt(sh.astype(float))
    cr = ref.crossing_time(bg, ks)
    bc = bg(cr[:, 0])
    dsr = HSTAR ** 2 * bc["H"] ** 2 / (8 * np.pi ** 2 * bc["eps1"])
    fac = ks ** 3 / (2 * np.pi ** 2)
    sel = ks <= kmax / 2
    figd[f"v2_{key}_spec"] = np.stack([ks, fac * raw / dsr, fac * nrm / dsr, fac * msk / dsr, M])
    v2[key]["spectrum_last"] = dict(
        N=float(b["lna"][il]),
        nr_alpha_norm_over_sr=[float(x) for x in (fac * nrm / dsr)[sel][[0, -1]]],
        nr_alpha_norm_over_sr_range=[float((fac * nrm / dsr)[sel].min()), float((fac * nrm / dsr)[sel].max())],
        ms_over_sr_range=[float((fac * msk / dsr)[sel].min()), float((fac * msk / dsr)[sel].max())],
        nr_alpha_norm_over_ms_maxdev=float(np.max(np.abs(nrm[sel] / msk[sel] - 1))),
        raw_over_ms_pull_rms=float(np.sqrt(np.mean(((raw[sel] / msk[sel] - 1) * np.sqrt(M[sel])) ** 2))),
        raw_over_ms_pull_max=float(np.max(np.abs((raw[sel] / msk[sel] - 1) * np.sqrt(M[sel])))))

    # V3: freezing, modes with N_f - N_k >= 6
    Nf = float(b["lna"][-1])
    if Nf > 7.0:
        crm = ref.crossing_time(bg, np.sqrt(q2.astype(float)))
        Nk = crm[:, 1]
        sel3 = (Nf - Nk >= 6.0)
        rows = []
        Nd = b["lna"]
        for j in np.where(sel3)[0]:
            i4 = int(np.searchsorted(Nd, Nk[j] + 4.0))
            pN = np.abs(RN[:, j]) ** 2
            pM = np.abs(pred[:, j]) ** 2
            pD = np.abs(Rdf[:, idx[j]]) ** 2
            rNR = pN[-1] / pN[i4]
            rMS = pM[-1] / pM[i4]
            rDF = pD[-1] / pD[i4]
            sl = slice(i4, None)
            x = Nd[sl]
            dNR = np.polyfit(x, np.log(pN[sl]), 1)[0]
            dMS = np.polyfit(x, np.log(pM[sl]), 1)[0]
            dDF = np.polyfit(x, np.log(pD[sl]), 1)[0]
            rows.append([np.sqrt(q2[j]), Nk[j], Nd[i4], rNR, rMS, rDF, dNR, dMS, dDF])
        rows = np.array(rows)
        figd[f"v3_{key}"] = rows.T
        dev = np.abs(rows[:, 3] / rows[:, 4] - 1)
        v3[key] = dict(N_f=Nf, nmodes=int(len(rows)), k_max_tested=float(rows[:, 0].max()),
                       max_ratio_dev=float(dev.max()), median_ratio_dev=float(np.median(dev)),
                       k_at_max=float(rows[dev.argmax(), 0]),
                       drift_NR_range=[float(rows[:, 6].min()), float(rows[:, 6].max())],
                       drift_MS_range=[float(rows[:, 7].min()), float(rows[:, 7].max())],
                       drift_NR_minus_MS_max=float(np.max(np.abs(rows[:, 6] - rows[:, 7]))),
                       drift_deformed_range=[float(rows[:, 8].min()), float(rows[:, 8].max())],
                       ratio_deformed_over_MS_range=[float((rows[:, 5] / rows[:, 4]).min()),
                                                     float((rows[:, 5] / rows[:, 4]).max())])
        # time series of three modes for the figure
        for qq in (1, 2, 7):
            j = int(np.where(q2 == qq * qq)[0][0]) if (q2 == qq * qq).any() else None
            if j is None:
                continue
            figd[f"v3_{key}_mode{qq}"] = np.stack([Nd, np.abs(RN[:, j]) ** 2, np.abs(pred[:, j]) ** 2,
                                                   (L ** -1.5 * np.abs(Rdf[:, idx[j]] * al[j])) ** 2,
                                                   np.full(len(Nd), Nk[j])])

res["V1_dumps"] = v1d
res["V2"] = v2
res["V3"] = v3
with open(os.path.join(out, "v123.json"), "w") as f:
    json.dump(res, f, indent=1)
np.savez(os.path.join(out, "v123_fig.npz"), **figd)
print(json.dumps({"V1_dumps": v1d, "V2": {k: (v["last"], v["t45"]) for k, v in v2.items()},
                  "V3": v3}, indent=1))
