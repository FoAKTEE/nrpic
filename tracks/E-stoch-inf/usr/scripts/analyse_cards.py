#!/usr/bin/env python3
"""Analysis of the card runs of the USR case against the pre-registration of JOURNAL entry 9
(package tracks/E-stoch-inf/usr).

    python3 analyse_cards.py --group g1   --run RUNDIR --ref ../results --out OUT [--workers 3]
    python3 analyse_cards.py --group u256 --run RUNDIR [--run RUNDIR2] --ref ../results --out OUT

RUNDIR is the output directory of a batch run (one sub-directory per entry of the list:
U64p, U64m, U128p, U128m, U128hp, U128hm; or U256, U256m). Dumps are read sequentially
(card_lib.read_fields). Writes OUT/summary.json, OUT/<group>_coeffs.npz and OUT/fig/*.png.

Quantities (entry 9.1): U-A0, U-A1 from the record; U-A2 per mode at N_f (odd part of a pair,
or the single run), with the worst mode, per shell and in time; U-A2n even/odd; U-A3 k <= 3 dk;
lockstep record; constraints: the parts of H and M_i odd and even in s with box means removed
(dumps), the record of H' = H - <H> (con_signed), halving factors, order 64 -> 128, strict A4;
U-A5 shell spectrum; U-A6/P-h one-point statistics of R^NR(x) against the linear realisation
field; cost from athena.log.
"""
import argparse
import csv
import json
import os
import time

import numpy as np

import card_lib as cl
import usr_lib as ul

PKG = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MODEFILE = {64: "modes_usr_n64.txt", 4096: "modes_usr_n4096.txt"}
GROUPS = {
    "g1": dict(runs={"U64p": 1.0, "U64m": -1.0, "U128p": 1.0, "U128m": -1.0,
                     "U128hp": 0.5, "U128hm": -0.5}, nmax2=64,
               pairs=[("U64p", "U64m"), ("U128p", "U128m"), ("U128hp", "U128hm")],
               halving=[("U128p", "U128hp")], ladder=[("U64p", "U128p")], kmask=None,
               onepoint=False),
    "u256": dict(runs={"U256": 1.0, "U256m": -1.0}, nmax2=4096, pairs=[("U256", "U256m")],
                 halving=[], ladder=[], kmask=32.0, onepoint=True),
}
BAR = {"H": 3e-13, "M": 1e-12}   # entry 9.1 and 10, U-A4: parts judged only above these fractions of <[C]>
ENTRY_CN = np.log(8.0)
USR = (2.5235, 6.5503)


def jdump(obj, path):
    with open(path, "w") as fp:
        json.dump(obj, fp, indent=1, default=lambda x: x.tolist() if hasattr(x, "tolist") else float(x))


def load_ref(refdir):
    r = json.load(open(os.path.join(refdir, "usr_reference.json")))
    lm = []
    with open(os.path.join(refdir, "landmarks.csv")) as fp:
        rows = [l for l in fp if not l.startswith("#")]
    for row in csv.DictReader(rows):
        lm.append(dict(label=row["label"], cN=float(row["cN"]), t=float(row["t"])))
    return r, r["code_inputs"], lm


# ----------------------------------------------------------------------------- record
def record_checks(con, ci, lm):
    t = con[:, cl.C["t"]]
    ex = ul.exact_background(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"], ci["K0"], t)
    rel = lambda a, b: np.abs(a - b) / np.abs(b)
    out = dict(U_A1_phi_rel_max=float(rel(con[:, cl.C["phi"]], ex[0]).max()),
               U_A1_Pi_rel_max=float(rel(con[:, cl.C["Pi"]], ex[1]).max()),
               U_A1_Pi_rel_end=float(rel(con[-1, cl.C["Pi"]], ex[1][-1])),
               U_A1_K_rel_max=float(rel(con[:, cl.C["K"]], ex[2]).max()),
               efolds_end=float(con[-1, cl.C["efolds"]]),
               efolds_exact_end=float(-0.5 * ex[3][-1]), t_end=float(t[-1]),
               cycles=int(con[-1, cl.C["cycle"]]))
    nr = con[:, cl.C["efolds"]]
    lmo = []
    for m in lm:
        if m["t"] <= t[-1] + 1e-12 and m["t"] > 0:
            i = int(np.clip(np.searchsorted(t, m["t"]) - 2, 0, t.size - 4))
            p = np.polyfit(t[i:i + 4] - m["t"], nr[i:i + 4], 3)
            lmo.append(dict(label=m["label"], cN=m["cN"], N_run=float(p[-1]), dN=float(p[-1] - m["cN"])))
    out["U_A0_landmarks"] = lmo
    out["U_A0_max_abs_dN"] = float(max(abs(x["dN"]) for x in lmo)) if lmo else None
    rec = dict(H_ratio_max=float(con[:, cl.C["H_ratio"]].max()),
               M_ratio_max=float(con[:, cl.C["M_ratio"]].max()),
               M_ratio_end=float(con[-1, cl.C["M_ratio"]]))
    cn = nr
    for lab, sel in (("entry", cn <= ENTRY_CN), ("usr", (cn > USR[0]) & (cn < USR[1])),
                     ("late", cn > 7.0)):
        if sel.any():
            rec[f"M_ratio_max_{lab}"] = float(con[sel, cl.C["M_ratio"]].max())
            if con.shape[1] > cl.C["Hp_ratio"]:
                rec[f"Hp_ratio_max_{lab}"] = float(con[sel, cl.C["Hp_ratio"]].max())
    if con.shape[1] > cl.C["Hp_ratio"]:
        rec["Hp_ratio_max"] = float(con[:, cl.C["Hp_ratio"]].max())
    out["record"] = rec
    return out, dict(t=t, cN=cn, Pi_rel=rel(con[:, cl.C["Pi"]], ex[1]),
                     phi_rel=rel(con[:, cl.C["phi"]], ex[0]), K_rel=rel(con[:, cl.C["K"]], ex[2]))


def shell_norm(modes, cref):
    p = np.abs(cref)**2
    ms = np.bincount(modes.shell_of, weights=p) / np.bincount(modes.shell_of)
    return np.sqrt(ms[modes.shell_of])


# ----------------------------------------------------------------------------- one mesh
def analyse_mesh(names, rundir, cfg, ci, workers, out_dir):
    """All runs of one mesh size: dump loop, then per-run and pair metrics."""
    dirs = {n: os.path.join(rundir, n) for n in names}
    dumps = {n: cl.dump_list(dirs[n]) for n in names}
    nd = min(len(v) for v in dumps.values())
    hdrs = {n: [ul.read_header(p) for p in dumps[n][:nd]] for n in names}
    times = np.array([h["time"] for h in hdrs[names[0]]])
    cycles = np.array([h["cycle"] for h in hdrs[names[0]]])
    for n in names[1:]:
        tn = np.array([h["time"] for h in hdrs[n]])
        if not np.array_equal(np.array([h["cycle"] for h in hdrs[n]]), cycles) or \
                np.abs(tn - times).max() > 1e-12:
            raise SystemExit(f"dump times of {n} differ from {names[0]}")
    N = hdrs[names[0]][0]["nx"][0] * 1
    nvar_names = hdrs[names[0]][0]["names"]
    has_cons = all(v in nvar_names for v in cl.CONS)
    modes = ul.Modes(N, cfg["nmax2"])
    alpha = modes.alpha()
    ext = cl.Extractor(modes, workers)
    t0 = time.time()
    sref = cl.ShellReference(ci, os.path.join(PKG, "inputs", MODEFILE[cfg["nmax2"]]), cfg["nmax2"], times)
    cref = np.empty((nd, modes.M), dtype=complex)
    bgref = []
    for i in range(nd):
        cref[i], st = sref.modes_ref(modes, alpha, i)
        bgref.append(dict(a=st["a"], H=st["H"], cN=float(st["lna"])))
    print(f"N={N}: {modes.M} modes, {nd} dumps, reference {time.time() - t0:.1f} s", flush=True)
    cons = {n: cl.read_con(os.path.join(dirs[n], "usr.sf.con.hst")) for n in names}
    S = {n: dict(s=cfg["runs"][n], N=N, nmodes=int(modes.M), ndumps=nd) for n in names}
    coeff = {n: np.empty((nd, modes.M), dtype=complex) for n in names}
    coeff_log = {n: np.empty((nd, modes.M), dtype=complex) for n in names}
    parts = {n: [] for n in names}
    cpart = {n: [] for n in names}
    pairs = [p for p in cfg["pairs"] if p[0] in names and p[1] in names]
    ppart = {p: [] for p in pairs}
    onept = {n: [] for n in names}
    hist = {}
    for i in range(nd):
        last = i == nd - 1
        keep = {}
        for n in names:
            want = cl.CURV + (cl.CONS if has_cons else [])
            h, f = cl.read_fields(dumps[n][i], want)
            full = cfg["onepoint"]
            r = ext.curvature(f, full=full)
            coeff[n][i] = r["lin"]
            coeff_log[n][i] = r["log"]
            tot = np.sqrt(np.sum(np.abs(r["lin"])**2))
            parts[n].append(dict(chi=float(np.sqrt(np.sum(np.abs(r["chi_part"])**2)) / tot),
                                 phi=float(np.sqrt(np.sum(np.abs(r["phi_part"])**2)) / tot),
                                 aniso=float(np.sqrt(np.sum(np.abs(r["aniso"])**2)) / tot),
                                 log_minus_lin=float(np.sqrt(np.sum(np.abs(r["log"] - r["lin"])**2)) / tot),
                                 bg=r["bg"]))
            row = cons[n][np.nonzero(cons[n][:, cl.C["cycle"]] == h["cycle"])[0][0]]
            if has_cons:
                Hm = f["H"].mean()
                hp = f["H"] - Hm
                cpart[n].append(dict(H_mean=float(Hm), Hmag=float(row[cl.C["Hmag"]]),
                                     Mmag=float(row[cl.C["Mmag"]]),
                                     Hp_rms=float(np.sqrt(np.mean(hp * hp))),
                                     M_rms=float(np.sqrt(np.mean(f["Mx"]**2 + f["My"]**2 + f["Mz"]**2))),
                                     M_mean=[float(f[c].mean()) for c in ("Mx", "My", "Mz")]))
                keep[n] = {c: f[c] for c in cl.CONS}
                keep[n]["Hmag"], keep[n]["Mmag"] = row[cl.C["Hmag"]], row[cl.C["Mmag"]]
            if full:
                Rf = ext.field(r["F"])                       # whole lattice
                Rb = ext.field(r["F"], cfg["nmax2"])          # band of the injected modes
                Rl = cl.synth_field(modes, cfg["runs"][n] * cref[i], workers)   # linear field
                d = Rb - Rl
                op = dict(cN=bgref[i]["cN"], full=cl.moments(Rf), band=cl.moments(Rb),
                          lin=cl.moments(Rl), diff_rms=float(np.sqrt(np.mean(d * d))),
                          diff_maxabs=float(np.abs(d).max()),
                          band_minus_full_rms=float(np.sqrt(np.mean((Rf - Rb)**2))))
                onept[n].append(op)
                if last:
                    lim = 8.0 * op["lin"]["rms"]
                    edges = np.linspace(-lim, lim, 161)
                    hist[n] = dict(edges=edges, full=np.histogram(Rf, edges)[0],
                                   band=np.histogram(Rb, edges)[0], lin=np.histogram(Rl, edges)[0],
                                   diff_edges=np.linspace(-6 * op["diff_rms"], 6 * op["diff_rms"], 121))
                    hist[n]["diff"] = np.histogram(d, hist[n]["diff_edges"])[0]
                    # a slice through the extreme cell for the figure
                    iz = np.unravel_index(np.argmax(np.abs(Rf)), Rf.shape)[0]
                    hist[n]["slice"] = Rf[iz].astype(np.float32)
                    hist[n]["slice_lin"] = Rl[iz].astype(np.float32)
                    hist[n]["slice_z"] = int(iz)
                del Rf, Rb, Rl, d, r["F"]
            del f, r
        for p in pairs:
            if not has_cons:
                continue
            a, b = keep[p[0]], keep[p[1]]
            hmag = 0.5 * (a["Hmag"] + b["Hmag"])
            mmag = 0.5 * (a["Mmag"] + b["Mmag"])
            ho = 0.5 * (a["H"] - b["H"])
            he = 0.5 * (a["H"] + b["H"])
            he = he - he.mean()
            mo2 = sum((0.5 * (a[c] - b[c]))**2 for c in ("Mx", "My", "Mz"))
            me2 = 0.0
            for c in ("Mx", "My", "Mz"):
                e = 0.5 * (a[c] + b[c])
                me2 = me2 + (e - e.mean())**2
            ppart[p].append(dict(H_odd=float(np.sqrt(np.mean(ho * ho))), H_even=float(np.sqrt(np.mean(he * he))),
                                 M_odd=float(np.sqrt(np.mean(mo2))), M_even=float(np.sqrt(np.mean(me2))),
                                 Hmag=float(hmag), Mmag=float(mmag),
                                 H_mean_p=float(a["H"].mean()), H_mean_m=float(b["H"].mean())))
            del ho, he, mo2, me2
        del keep
        print(f"  dump {i + 1}/{nd} t={times[i]:.4f} cN={bgref[i]['cN']:.3f} ({time.time() - t0:.0f} s)", flush=True)
    cN = np.array([b["cN"] for b in bgref])
    # --------------------------------------------------------------- per run
    km = np.ones(modes.M, bool) if cfg["kmask"] is None else modes.k <= cfg["kmask"] + 1e-9
    k3 = modes.n2 <= 9
    snorm = np.array([shell_norm(modes, cref[i]) for i in range(nd)])
    arank = np.argsort(np.argsort(np.abs(alpha))) / float(modes.M)     # 0 = smallest |alpha|
    curves = {}
    for n in names:
        s = cfg["runs"][n]
        c = coeff[n]
        rel = np.abs(c / (s * cref) - 1.0)
        dsh = np.abs(c - s * cref) / (abs(s) * snorm)
        relN = rel[-1]
        w = int(np.argmax(np.where(km, relN, -1.0)))
        sh_max = np.array([relN[(modes.shell_of == j) & km].max() if np.any((modes.shell_of == j) & km) else np.nan
                           for j in range(modes.shell_n2.size)])
        fr = np.abs(c[-1])**2 / np.abs(s * cref[-1])**2
        rec, rc = record_checks(cons[n], ci, LM)
        lock = []
        for i, p in enumerate(dumps[n][:nd]):
            mp = p[:-5] + ".modes"
            if os.path.exists(mp):
                hd, n2r, rr, drr = ul.read_modes_record(mp)
                st = sref.state(i)
                idx = np.searchsorted(sref.n2, n2r)
                rref = st["R"][idx] * s
                lock.append(float(np.max(np.abs(rr - rref) / np.abs(rref))))
        S[n].update(rec)
        S[n].update(dict(
            t_end=float(times[-1]), cN_end=float(cN[-1]),
            U_A2=dict(max_end=float(relN[km].max()), rms_end=float(np.sqrt(np.mean(relN[km]**2))),
                      median_end=float(np.median(relN[km])), worst_mode=modes.n[w].tolist(),
                      worst_alpha_abs=float(np.abs(alpha[w])), worst_alpha_rank=float(arank[w]),
                      max_run_over_dumps_after_cN4=float(np.nanmax(np.where(cN[:, None] > 4.0, np.where(km, rel, np.nan), np.nan)))
                      if np.any(cN > 4.0) else None),
            U_A2_shellnorm=dict(max_end=float(dsh[-1][km].max()), rms_end=float(np.sqrt(np.mean(dsh[-1][km]**2))),
                                max_t=[float(x) for x in np.max(np.where(km, dsh, 0.0), axis=1)],
                                rms_t=[float(x) for x in np.sqrt(np.mean(np.where(km, dsh, 0.0)**2, axis=1) * modes.M / km.sum())]),
            U_A2_shell_max_end={int(modes.shell_n2[j]): float(sh_max[j]) for j in range(modes.shell_n2.size)},
            U_A3_power_ratio_k_le_3=dict(min=float(fr[k3].min()), max=float(fr[k3].max())),
            lock_max_end=lock[-1] if lock else None, lock_max=max(lock) if lock else None,
            rms_R_end=float(np.sqrt(2.0 * np.sum(np.abs(c[-1])**2))),
            rms_R_ref_end=float(abs(s) * np.sqrt(2.0 * np.sum(np.abs(cref[-1])**2))),
            parts_end=parts[n][-1], log_minus_lin_max=float(max(x["log_minus_lin"] for x in parts[n])),
            chi_part_max=float(max(x["chi"] for x in parts[n])),
            cost=cl.athena_cost(dirs[n])))
        if onept[n]:
            S[n]["onepoint"] = onept[n]
        if cpart[n]:
            S[n]["constraint_fields"] = cpart[n]
        curves[n] = dict(rel=rel, dsh=dsh, rc=rc, lock=np.array(lock), con=cons[n])
    # --------------------------------------------------------------- pairs
    P = {}
    for p in pairs:
        s = cfg["runs"][p[0]]
        odd = 0.5 * (coeff[p[0]] - coeff[p[1]]) / s
        even = 0.5 * (coeff[p[0]] + coeff[p[1]])
        rel = np.abs(odd / cref - 1.0)
        dev = np.abs(odd - cref) / np.abs(cref).max(axis=0)[None, :]    # entry 2: over the run
        relN = rel[-1]
        w = int(np.argmax(np.where(km, relN, -1.0)))
        ratio_t = np.sqrt(np.sum(np.abs(even)**2, axis=1) / np.sum(np.abs(s * odd)**2, axis=1))
        fr = np.abs(odd[-1])**2 / np.abs(cref[-1])**2
        sh_max = np.array([relN[modes.shell_of == j].max() for j in range(modes.shell_n2.size)])
        key = f"{p[0]}_{p[1]}"
        d = dict(U_A2s=dict(max_end=float(relN[km].max()), rms_end=float(np.sqrt(np.mean(relN[km]**2))),
                            worst_mode=modes.n[w].tolist(), worst_shell_n2=int(modes.n2[w]),
                            max_all_modes_end=float(relN.max()),
                            dev_max_t=[float(x) for x in np.max(np.where(km, dev, 0.0), axis=1)],
                            dev_max_run=float(np.max(np.where(km, dev, 0.0)))),
                 U_A2s_shell_max_end={int(modes.shell_n2[j]): float(sh_max[j]) for j in range(modes.shell_n2.size)},
                 U_A2n_even_over_odd_end=float(ratio_t[-1]), U_A2n_even_over_odd_max=float(ratio_t.max()),
                 U_A2n_max_at_cN=float(cN[np.argmax(ratio_t)]), U_A2n_t=ratio_t.tolist(),
                 U_A3_odd_power_ratio_k_le_3=dict(min=float(fr[k3].min()), max=float(fr[k3].max())),
                 even_rms_t=np.sqrt(np.sum(np.abs(even)**2, axis=1)).tolist(),
                 odd_rms_t=np.sqrt(np.sum(np.abs(s * odd)**2, axis=1)).tolist())
        if ppart[p]:
            pp = ppart[p]
            Ho = np.array([x["H_odd"] / x["Hmag"] for x in pp])
            He = np.array([x["H_even"] / x["Hmag"] for x in pp])
            Mo = np.array([x["M_odd"] / x["Mmag"] for x in pp])
            Me = np.array([x["M_even"] / x["Mmag"] for x in pp])
            hmp = np.array([x["H_mean_p"] for x in pp])
            hmm = np.array([x["H_mean_m"] for x in pp])
            d["constraints"] = dict(cN=cN.tolist(), H_odd=Ho.tolist(), H_even=He.tolist(),
                                    M_odd=Mo.tolist(), M_even=Me.tolist(),
                                    H_odd_abs=[x["H_odd"] for x in pp], H_even_abs=[x["H_even"] for x in pp],
                                    M_odd_abs=[x["M_odd"] for x in pp], M_even_abs=[x["M_even"] for x in pp],
                                    H_mean_rel_diff=(np.abs(hmp - hmm) / np.maximum(np.abs(hmp), 1e-300)).tolist())
            ent = (cN <= ENTRY_CN) & (cN > 0)
            for lab, o, e in (("H", Ho, He), ("M", Mo, Me)):
                ok = ent & (o > BAR[lab]) & (e > BAR[lab])
                d["constraints"][f"strictA4_{lab}_odd_over_even_entry_max"] = float((o[ok] / e[ok]).max()) if ok.any() else None
                usr = (cN > USR[0]) & (cN < USR[1])
                d["constraints"][f"{lab}_odd_usr_max"] = float(o[usr].max()) if usr.any() else None
                d["constraints"][f"{lab}_even_usr_max"] = float(e[usr].max()) if usr.any() else None
                d["constraints"][f"{lab}_odd_over_even_max"] = float(np.max(o[1:] / np.maximum(e[1:], 1e-300)))
                d["constraints"][f"{lab}_odd_over_even_first_above1_cN"] = (
                    float(cN[1:][np.argmax(o[1:] > e[1:])]) if np.any(o[1:] > e[1:]) else None)
        P[key] = d
        curves[key] = dict(odd=odd, even=even, rel=rel, dev=dev, ratio_t=ratio_t)
    # --------------------------------------------------------------- halving
    for (p1, ph) in cfg["halving"]:
        q1 = next((p for p in pairs if p[0] == p1), None)
        qh = next((p for p in pairs if p[0] == ph), None)
        if q1 is None or qh is None:
            continue
        k1, kh = f"{q1[0]}_{q1[1]}", f"{qh[0]}_{qh[1]}"
        r = cfg["runs"][p1] / cfg["runs"][ph]
        o1 = np.sqrt(np.sum(np.abs(curves[k1]["odd"])**2, axis=1)) * cfg["runs"][p1]
        oh = np.sqrt(np.sum(np.abs(curves[kh]["odd"])**2, axis=1)) * cfg["runs"][ph]
        e1 = np.sqrt(np.sum(np.abs(curves[k1]["even"])**2, axis=1))
        eh = np.sqrt(np.sum(np.abs(curves[kh]["even"])**2, axis=1))
        hv = dict(scale_ratio=r, cN=cN.tolist(), R_odd=(o1 / oh).tolist(), R_even=(e1 / eh).tolist())
        if "constraints" in P[k1]:
            c1, ch = P[k1]["constraints"], P[kh]["constraints"]
            for lab in ("H_odd", "H_even", "M_odd", "M_even"):
                a1 = np.array(c1[lab + "_abs"])
                ah = np.array(ch[lab + "_abs"])
                fac = a1 / np.maximum(ah, 1e-300)
                nm = np.array(ch[lab])            # normalised part of the halved pair
                ok = (nm > BAR[lab[0]]) & (cN > 0)
                hv[lab] = fac.tolist()
                tgt = 2.0 if lab.endswith("odd") else 4.0
                hv[lab + "_judged"] = dict(n=int(ok.sum()), min=float(fac[ok].min()) if ok.any() else None,
                                           max=float(fac[ok].max()) if ok.any() else None,
                                           median=float(np.median(fac[ok])) if ok.any() else None,
                                           within_005=int(np.sum(np.abs(fac[ok] - tgt) <= 0.05)))
        P[f"halving_{p1}_over_{ph}"] = hv
    # coefficients for later use
    np.savez_compressed(os.path.join(out_dir, f"coeffs_N{N}.npz"), t=times, cN=cN, n=modes.n,
                        alpha=alpha, cref=cref, **{f"c_{n}": coeff[n] for n in names},
                        **{f"clog_{n}": coeff_log[n][-1] for n in names})
    return dict(N=N, S=S, P=P, curves=curves, modes=modes, cN=cN, times=times, cref=cref,
                alpha=alpha, hist=hist, km=km)


# ----------------------------------------------------------------------------- ladder
def ladder(m64, m128, p64, p128):
    """Order of the odd-part errors (per shell at N_f) and of the odd constraint parts."""
    out = {}
    k64, k128 = f"{p64[0]}_{p64[1]}", f"{p128[0]}_{p128[1]}"
    e64 = m64["P"][k64]["U_A2s_shell_max_end"]
    e128 = m128["P"][k128]["U_A2s_shell_max_end"]
    out["order_per_shell_end"] = {k: float(np.log2(e64[k] / e128[k])) for k in e64 if k in e128}
    if "constraints" in m64["P"][k64] and "constraints" in m128["P"][k128]:
        c64, c128 = m64["P"][k64]["constraints"], m128["P"][k128]["constraints"]
        t64, t128 = m64["times"], m128["times"]
        for lab in ("H_odd", "M_odd", "H_even", "M_even"):
            y64 = np.array(c64[lab])
            y128 = np.array(c128[lab])
            ok = y64 > 0
            yi = np.exp(np.interp(t128, t64[ok], np.log(y64[ok])))
            out[f"order_{lab}"] = dict(cN=m128["cN"].tolist(),
                                       order=np.log2(yi / np.maximum(y128, 1e-300)).tolist())
    return out


# ----------------------------------------------------------------------------- figures
def figures(out, group, meshes, lad):
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fd = os.path.join(out, "fig")
    os.makedirs(fd, exist_ok=True)
    cols = fs.series_colors(6)
    if group == "g1":
        # ---- per-mode errors of the odd parts
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0))
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.3)
        for (N, key, lab), col in zip(((64, "U64p_U64m", "64^3, s = +-1"), (128, "U128p_U128m", "128^3, s = +-1"),
                                       (128, "U128hp_U128hm", "128^3, s = +-1/2")), cols):
            if N not in meshes or key not in meshes[N]["curves"]:
                continue
            M = meshes[N]
            md = M["modes"]
            relN = M["curves"][key]["rel"][-1]
            ax[0].semilogy(md.k + (0.08 if "h" in key else 0.0), relN, ".", ms=2.5, color=col, label=lab)
            ax[1].semilogy(M["cN"][1:], M["curves"][key]["dev"][1:].max(axis=1), color=col,
                           label=lab + r": max$_n$ |odd-ref|/max$_t$|ref|")
            ax[1].semilogy(M["cN"][1:], M["curves"][key]["ratio_t"][1:], color=col, ls="--", lw=1.0,
                           label=lab + ": even/odd rms")
        ax[0].axhline(0.02, **fs.GUIDE, label="U-A2 0.02")
        ax[0].set_xlabel(r"$|n| = k/dk$")
        ax[0].set_ylabel(r"odd part at $N_f$: $|c/c_{\rm ref}-1|$")
        ax[0].legend(loc="upper left", fontsize=7, ncol=2)
        ax[1].axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        ax[1].axhline(0.02, **fs.GUIDE)
        ax[1].set_xlabel(r"$N-N_*$")
        ax[1].set_ylabel("per-mode error; even/odd")
        ax[1].legend(loc="lower left", fontsize=6, ncol=2)
        fs.save(fig, os.path.join(fd, "fig_card_g1_modes"))
        plt.close(fig)
        # ---- constraint parts
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.2), sharex=True)
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
        for x in ax:
            x.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
            x.axvline(ENTRY_CN, **fs.MASK_LINE)
        for (N, key, lab), col in zip(((64, "U64p_U64m", "64, +-1"), (128, "U128p_U128m", "128, +-1"),
                                       (128, "U128hp_U128hm", "128, +-1/2")), cols):
            if N not in meshes or key not in meshes[N]["P"] or "constraints" not in meshes[N]["P"][key]:
                continue
            c = meshes[N]["P"][key]["constraints"]
            cn = np.array(c["cN"])
            for j, part in enumerate(("H", "M")):
                ax[j].semilogy(cn[1:], np.array(c[part + "_odd"])[1:], color=col, marker="o", ms=2.5, label=f"{lab} odd")
                ax[j].semilogy(cn[1:], np.array(c[part + "_even"])[1:], color=col, ls="--", marker="s", ms=2.5,
                               mfc="none", label=f"{lab} even")
            con = meshes[N]["curves"][key.split("_")[0]]["con"]
            if con.shape[1] > cl.C["Hp_ratio"]:
                ax[0].semilogy(con[1:, cl.C["efolds"]], con[1:, cl.C["Hp_ratio"]], color=col, lw=0.6, alpha=0.6)
                ax[0].semilogy(con[1:, cl.C["efolds"]], con[1:, cl.C["H_ratio"]], color=col, lw=0.6, ls=":", alpha=0.8)
            ax[1].semilogy(con[1:, cl.C["efolds"]], con[1:, cl.C["M_ratio"]], color=col, lw=0.6, alpha=0.6)
        ax[0].axhline(BAR["H"], **fs.GUIDE)
        ax[1].axhline(BAR["M"], **fs.GUIDE)
        ax[0].set_ylabel(r"rms part of ${\cal H}$ / $\langle[{\cal H}]\rangle$" + "\n(thin: record H', dotted: |H|)")
        ax[1].set_ylabel(r"rms part of ${\cal M}$ / $\langle[{\cal M}]\rangle$" + "\n(thin: record |M|/[M])")
        ax[1].set_xlabel(r"$N-N_*$")
        ax[0].legend(loc="upper right", fontsize=6, ncol=3)
        fs.save(fig, os.path.join(fd, "fig_card_g1_constraints"))
        plt.close(fig)
        # ---- halving factors
        hk = "halving_U128p_over_U128hp"
        if 128 in meshes and hk in meshes[128]["P"]:
            hv = meshes[128]["P"][hk]
            cn = np.array(hv["cN"])
            fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.6))
            fig.subplots_adjust(left=0.13, right=0.97, top=0.96, bottom=0.14)
            ax.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
            for y in (2.0, 4.0):
                ax.axhspan(y - 0.05, y + 0.05, color="0.85", lw=0)
            for (lab, mk), col in zip((("H_odd", "o"), ("H_even", "s"), ("M_odd", "^"), ("M_even", "v"),
                                       ("R_odd", "x"), ("R_even", "+")), cols):
                if lab in hv:
                    ax.plot(cn[1:], np.array(hv[lab])[1:], marker=mk, ms=4, lw=0.8, color=col, label=lab)
            ax.set_ylim(0.0, 6.0)
            ax.set_xlabel(r"$N-N_*$")
            ax.set_ylabel(r"part($s=1$) / part($s=1/2$)")
            ax.legend(loc="upper left", fontsize=7, ncol=3)
            fs.save(fig, os.path.join(fd, "fig_card_g1_halving"))
            plt.close(fig)
        # ---- background, lockstep, order
        fig, ax = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 7.6))
        fig.subplots_adjust(left=0.15, right=0.97, top=0.98, bottom=0.07, hspace=0.35)
        for (N, n), col in zip(((64, "U64p"), (128, "U128p"), (128, "U128hp")), cols):
            if N in meshes and n in meshes[N]["curves"]:
                rc = meshes[N]["curves"][n]["rc"]
                ax[0].semilogy(rc["cN"][1:], rc["Pi_rel"][1:], color=col, label=f"{n}: <Pi>")
                ax[0].semilogy(rc["cN"][1:], np.maximum(rc["phi_rel"][1:], 1e-17), color=col, ls=":", lw=0.8)
                lk = meshes[N]["curves"][n]["lock"]
                if lk.size:
                    ax[1].semilogy(meshes[N]["cN"][1:], lk[1:], color=col, marker="o", ms=2.5, label=f"{n}: lockstep")
        ax[0].axhline(1e-3, **fs.GUIDE, label="U-A1 1e-3")
        ax[0].set_xlabel(r"$N-N_*$")
        ax[0].set_ylabel("|mean - exact|/|exact|\n(dotted: phi)")
        ax[0].legend(loc="upper left", fontsize=7)
        ax[1].set_xlabel(r"$N-N_*$")
        ax[1].set_ylabel("lockstep record vs ref")
        ax[1].legend(loc="upper left", fontsize=7)
        if lad and "order_per_shell_end" in lad:
            o = lad["order_per_shell_end"]
            k2 = np.array(sorted(o))
            ax[2].plot(np.sqrt(k2), [o[k] for k in k2], "o", ms=3, color=cols[0], label="odd part of R per shell, N_f")
            ax[2].axhspan(4.0, 6.0, color="0.88", lw=0)
            ax[2].set_xlabel(r"$|n|$ of the shell")
            ax[2].set_ylabel("order 64 -> 128")
            ax[2].legend(loc="lower right", fontsize=7)
        fs.save(fig, os.path.join(fd, "fig_card_g1_background"))
        plt.close(fig)
        # ---- order of the odd constraint parts in time
        if lad and "order_H_odd" in lad:
            fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
            fig.subplots_adjust(left=0.13, right=0.97, top=0.96, bottom=0.15)
            ax.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
            ax.axhspan(4.0, 6.0, color="0.88", lw=0)
            for (lab, mk), col in zip((("order_H_odd", "o"), ("order_M_odd", "^"), ("order_H_even", "s"),
                                       ("order_M_even", "v")), cols):
                ax.plot(np.array(lad[lab]["cN"])[1:], np.array(lad[lab]["order"])[1:], marker=mk, ms=4, lw=0.8,
                        color=col, label=lab.replace("order_", ""))
            ax.axhline(0.0, color="0.5", lw=0.5)
            ax.set_xlabel(r"$N-N_*$ (dumps of 128$^3$)")
            ax.set_ylabel(r"$\log_2$(part$_{64}$/part$_{128}$)")
            ax.legend(loc="lower left", fontsize=7, ncol=2)
            fs.save(fig, os.path.join(fd, "fig_card_g1_order"))
            plt.close(fig)
    else:
        M = meshes[max(meshes)]
        md, cN = M["modes"], M["cN"]
        names = [n for n in ("U256", "U256m") if n in M["curves"]]
        n0 = names[0]
        cur = M["curves"][n0]
        # ---- per-mode at N_f and in time
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.2))
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.3)
        relN = cur["rel"][-1]
        dshN = cur["dsh"][-1]
        sh = md.shell_of
        ks = np.sqrt(md.shell_n2)
        for y, col, lab in ((relN, cols[0], "relative |c/c_ref - 1|"), (dshN, cols[2], "shell-normalised |c - c_ref|/rms")):
            mx = np.bincount(sh, weights=None, minlength=ks.size) * 0
            mx = np.full(ks.size, 0.0)
            np.maximum.at(mx, sh, y)
            med = np.array([np.median(y[sh == j]) for j in range(ks.size)])
            ax[0].semilogy(ks, mx, color=col, lw=0.8, label=lab + ": shell max")
            ax[0].semilogy(ks, med, color=col, lw=0.8, ls="--", label="shell median")
        if "U256_U256m" in M["curves"]:
            ro = M["curves"]["U256_U256m"]["rel"][-1]
            mx = np.full(ks.size, 0.0)
            np.maximum.at(mx, sh, ro)
            ax[0].semilogy(ks, mx, color=cols[4], lw=0.8, label="odd part: shell max")
        ax[0].axhline(0.02, **fs.GUIDE, label="U-A2 0.02")
        ax[0].axvline(32.0, **fs.MASK_LINE)
        ax[0].set_xlabel(r"$|n| = k/dk$")
        ax[0].set_ylabel(r"at $N_f$")
        ax[0].legend(loc="upper left", fontsize=6, ncol=2)
        km = M["km"]
        ax[1].axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        ax[1].semilogy(cN[1:], np.max(np.where(km, cur["dsh"], 0), axis=1)[1:], color=cols[2], marker="o", ms=3,
                       label="shell-normalised, max k<=32")
        ax[1].semilogy(cN[1:], np.sqrt(np.mean(np.where(km, cur["dsh"], 0)**2, axis=1) * md.M / km.sum())[1:],
                       color=cols[2], ls="--", label="shell-normalised, rms k<=32")
        ax[1].semilogy(cN[1:], np.median(np.where(km, cur["rel"], np.nan)[:, km], axis=1)[1:], color=cols[0],
                       ls=":", label="relative, median k<=32")
        if "U256_U256m" in M["curves"]:
            ax[1].semilogy(cN[1:], M["curves"]["U256_U256m"]["ratio_t"][1:], color=cols[4], label="even/odd rms")
        lv = np.array([o["band"]["rms"] for o in M["S"][n0].get("onepoint", [])])
        if lv.size:
            ax[1].semilogy(cN, lv, color="k", lw=0.8, label="rms R^NR(x), band")
        ax[1].axhline(0.02, **fs.GUIDE)
        ax[1].set_xlabel(r"$N-N_*$")
        ax[1].set_ylabel("deviation from linear")
        ax[1].legend(loc="lower right", fontsize=6, ncol=2)
        fs.save(fig, os.path.join(fd, "fig_card_u256_modes"))
        plt.close(fig)
        # ---- spectrum at several times
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0), sharex=True,
                               gridspec_kw=dict(height_ratios=[2, 1]))
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.06)
        c = np.load(os.path.join(out, f"coeffs_N{M['N']}.npz"))[f"c_{n0}"]
        s0 = M["S"][n0]["s"]
        kfac = md.shell_n2**1.5 * (2 * np.pi)**3 / (2 * np.pi**2)
        cnt = np.bincount(sh)
        targets = [2.0, 4.0, 5.0, 6.0, 7.0, 10.0]
        for col, tt in zip(fs.series_colors(len(targets)), targets):
            i = int(np.argmin(np.abs(cN - tt)))
            pnr = np.bincount(sh, weights=np.abs(c[i])**2) / cnt
            pre = np.bincount(sh, weights=np.abs(s0 * M["cref"][i])**2) / cnt
            ax[0].loglog(ks, kfac * pre, color=col, lw=1.0)
            ax[0].loglog(ks, kfac * pnr, "o", ms=1.5, color=col, label=f"N-N* = {cN[i]:.2f}")
            ax[1].semilogx(ks, pnr / pre - 1.0, ".", ms=1.5, color=col)
        ax[0].set_ylabel(r"shell mean $k^3 L^3|c_n|^2/(2\pi^2)$")
        ax[0].legend(loc="lower right", fontsize=7, ncol=2)
        ax[1].set_xlabel(r"$k/dk$")
        ax[1].set_ylabel("NR / linear - 1")
        ax[1].set_ylim(-0.02, 0.02)
        fs.save(fig, os.path.join(fd, "fig_card_u256_spectrum"))
        plt.close(fig)
        # ---- one-point statistics
        if n0 in M["hist"]:
            hh = M["hist"][n0]
            fig, ax = plt.subplots(2, 2, figsize=(fs.COLUMN_WIDTH * 2.0, 6.0))
            fig.subplots_adjust(left=0.1, right=0.97, top=0.95, bottom=0.09, hspace=0.35, wspace=0.3)
            e = hh["edges"]
            xc = 0.5 * (e[1:] + e[:-1])
            dx = e[1] - e[0]
            ncell = hh["full"].sum()
            sig = M["S"][n0]["onepoint"][-1]["lin"]["rms"]
            gauss = ncell * dx * np.exp(-0.5 * (xc / sig)**2) / np.sqrt(2 * np.pi) / sig
            a = ax[0, 0]
            a.semilogy(xc, np.maximum(hh["lin"], 0.5), color=cols[0], drawstyle="steps-mid", label="linear field")
            a.semilogy(xc, np.maximum(hh["full"], 0.5), color=cols[2], drawstyle="steps-mid", label="R^NR, lattice")
            a.semilogy(xc, np.maximum(hh["band"], 0.5), color=cols[4], drawstyle="steps-mid", ls="--", label="R^NR, band")
            a.semilogy(xc, gauss, **fs.GUIDE, label="Gaussian, same rms")
            a.set_ylim(0.5, None)
            a.set_xlabel(r"${\cal R}(x)$ at $N_f$")
            a.set_ylabel("cells")
            a.legend(loc="lower center", fontsize=6)
            a = ax[0, 1]
            de = hh["diff_edges"]
            a.semilogy(0.5 * (de[1:] + de[:-1]), np.maximum(hh["diff"], 0.5), color=cols[1], drawstyle="steps-mid")
            a.set_xlabel(r"${\cal R}^{\rm NR}_{\rm band}-{\cal R}_{\rm lin}$ at $N_f$")
            a.set_ylabel("cells")
            ops = M["S"][n0]["onepoint"]
            a = ax[1, 0]
            a.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
            cn1 = np.array([o["cN"] for o in ops])
            a.semilogy(cn1, [o["lin"]["rms"] for o in ops], color=cols[0], label="rms linear")
            a.semilogy(cn1, [o["full"]["rms"] for o in ops], color=cols[2], ls="--", label="rms R^NR")
            a.semilogy(cn1, [o["full"]["maxabs"] for o in ops], color=cols[2], marker="o", ms=3, label="max|R^NR|")
            a.semilogy(cn1, [o["lin"]["maxabs"] for o in ops], color=cols[0], marker="x", ms=3, label="max|R_lin|")
            a.semilogy(cn1, [o["diff_rms"] for o in ops], color=cols[1], label="rms(band - lin)")
            a.set_xlabel(r"$N-N_*$")
            a.legend(loc="lower right", fontsize=6)
            a = ax[1, 1]
            im = a.imshow(hh["slice"], origin="lower", cmap="RdBu_r",
                          vmin=-4 * sig, vmax=4 * sig, extent=(0, 2 * np.pi, 0, 2 * np.pi))
            fig.colorbar(im, ax=a, fraction=0.046)
            a.set_title(f"R^NR at N_f, slice z-index {hh['slice_z']}", fontsize=8)
            fs.save(fig, os.path.join(fd, "fig_card_u256_onepoint"))
            plt.close(fig)
        # ---- constraints and background
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0), sharex=True)
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
        for x in ax:
            x.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        con = cur["con"]
        e = con[:, cl.C["efolds"]]
        ax[0].semilogy(e[1:], con[1:, cl.C["H_ratio"]], color=cols[0], label="<|H|/[H]>")
        if con.shape[1] > cl.C["Hp_ratio"]:
            ax[0].semilogy(e[1:], con[1:, cl.C["Hp_ratio"]], color=cols[2], label="<|H'|/[H]> (H' = H - <H>)")
        ax[0].semilogy(e[1:], con[1:, cl.C["M_ratio"]], color=cols[4], label="<|M|/[M]>")
        if "U256_U256m" in M["P"] and "constraints" in M["P"]["U256_U256m"]:
            cc = M["P"]["U256_U256m"]["constraints"]
            cn = np.array(cc["cN"])
            for lab, col, mk in (("H_odd", cols[1], "o"), ("H_even", cols[1], "s"), ("M_odd", cols[5], "o"),
                                 ("M_even", cols[5], "s")):
                ax[0].semilogy(cn[1:], np.array(cc[lab])[1:], color=col, marker=mk, ms=3, ls="none", label=lab)
        ax[0].set_ylabel("constraint ratios")
        ax[0].legend(loc="lower left", fontsize=6, ncol=2)
        rc = cur["rc"]
        ax[1].semilogy(rc["cN"][1:], rc["Pi_rel"][1:], color=cols[0], label="<Pi>")
        ax[1].semilogy(rc["cN"][1:], np.maximum(rc["phi_rel"][1:], 1e-17), color=cols[2], label="<phi>")
        ax[1].semilogy(rc["cN"][1:], np.maximum(rc["K_rel"][1:], 1e-17), color=cols[4], label="<K>")
        ax[1].axhline(1e-3, **fs.GUIDE, label="U-A1 1e-3")
        ax[1].set_xlabel(r"$N-N_*$")
        ax[1].set_ylabel("|mean - exact|/|exact|")
        ax[1].legend(loc="upper left", fontsize=7)
        fs.save(fig, os.path.join(fd, "fig_card_u256_constraints"))
        plt.close(fig)


def main():
    global LM
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", required=True, choices=sorted(GROUPS))
    ap.add_argument("--run", required=True, action="append", help="batch run directory (repeatable)")
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--nmax2", type=int, default=None, help="code tests only: other mode cut")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    r, ci, LM = load_ref(a.ref)
    cfg = dict(GROUPS[a.group])
    if a.nmax2:
        cfg["nmax2"] = a.nmax2
    found = {}
    for n in cfg["runs"]:
        for d in a.run:
            if os.path.exists(os.path.join(d, n, "usr.sf.con.hst")) and cl.dump_list(os.path.join(d, n)):
                found[n] = d
                break
    if not found:
        raise SystemExit("no run of the group found")
    bymesh = {}
    for n, d in found.items():
        N = ul.read_header(cl.dump_list(os.path.join(d, n))[0])["nx"][0]
        bymesh.setdefault((N, d), []).append(n)
    meshes = {}
    S = dict(group=a.group, ref_run=r.get("run_id"), runs=a.run, found=found, bar=BAR)
    for (N, d), names in sorted(bymesh.items()):
        names = [n for n in cfg["runs"] if n in names]
        m = analyse_mesh(names, d, cfg, ci, a.workers, a.out)
        meshes[N] = m
        S.update(m["S"])
        S.update(m["P"])
    lad = None
    for p64, p128 in cfg["ladder"]:
        q64 = next((p for p in cfg["pairs"] if p[0] == p64), None)
        q128 = next((p for p in cfg["pairs"] if p[0] == p128), None)
        if 64 in meshes and 128 in meshes and f"{q64[0]}_{q64[1]}" in meshes[64]["P"] \
                and f"{q128[0]}_{q128[1]}" in meshes[128]["P"]:
            lad = ladder(meshes[64], meshes[128], q64, q128)
            S["ladder_64_128"] = lad
    jdump(S, os.path.join(a.out, "summary.json"))
    figures(a.out, a.group, meshes, lad)
    print("done", flush=True)


LM = []
if __name__ == "__main__":
    main()
