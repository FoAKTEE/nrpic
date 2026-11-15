#!/usr/bin/env python3
"""T1: the corrected linear-wave generator (athenak/src/pgen/tests/z4c_linear_wave.cpp).

Predictions P1a to P1h: tracks/core/JOURNAL-bfix.md. Stages (all by default):
  algebra  the polarization tensors (python twin of the generator), 400 directions
  id       initial data read back from the code and the constraints, Track B's case
           lw3d_check (k = (1,1,1) and (1,0,0)) with the new and the baseline executable,
           amplitude scaling, the general directions (1,2,0) and (2,-1,3)
  evol     oblique wave k = (1,1,1) over one period at N = 16, 32 (--evol-n): gain and
           phase against the Fourier symbol of the scheme, both diagnostics of gw_diag
  pol      cross and circular polarization
  trackb   Track B's own analytic wave tests with the new executable: lw_x_prod N = 16,
           32 (periodic_z4c) and validate_athenak.py on a rerun of lw3d_dump_N32 (gw_diag)
  errs     the error routine at a whole and at half a period, baseline and new

    python3 t1_linear_wave.py --exe-new EXE --exe-base EXE [--out DIR] [--stages ...]

Writes results_t1.json and figures t1_*.{pdf,png} into the output directory
($NRPIC_RUN_DIR when run through nrpic-run).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import fs, athena_bin  # noqa: E402

A0 = 1.0e-6
INP = os.path.join(bc.REPO, "problems", "tests", "lw_oblique.athinput")


def karg(k):
    return [f"problem/kx1={k[0]}", f"problem/kx2={k[1]}", f"problem/kx3={k[2]}"]


def ktag(k):
    return "k" + "".join(str(int(v)).replace("-", "m") for v in k)


# ---------------------------------------------------------------- stage: algebra

def stage_algebra(res):
    rng = np.random.default_rng(20261115)
    worst = dict(tr=0.0, ek=0.0, ee=0.0, dev=0.0, trx=0.0, exk=0.0, exex=0.0, epex=0.0,
                 devx=0.0, up_ek_min=np.inf, up_ek_max=0.0)
    for _ in range(400):
        k = rng.normal(size=3)
        kh, tht, pht = bc.frame(k)
        assert np.allclose(kh, k/np.linalg.norm(k), atol=1e-14)
        ep, ex = bc.pol_tensors(k)
        up, _ = bc.pol_tensors(k, upstream=True)
        worst["tr"] = max(worst["tr"], abs(np.trace(ep)))
        worst["ek"] = max(worst["ek"], np.linalg.norm(ep @ kh))
        worst["ee"] = max(worst["ee"], abs(np.sum(ep*ep) - 2.0))
        worst["dev"] = max(worst["dev"], np.abs(ep - (np.outer(tht, tht)
                                                      - np.outer(pht, pht))).max())
        worst["trx"] = max(worst["trx"], abs(np.trace(ex)))
        worst["exk"] = max(worst["exk"], np.linalg.norm(ex @ kh))
        worst["exex"] = max(worst["exex"], abs(np.sum(ex*ex) - 2.0))
        worst["epex"] = max(worst["epex"], abs(np.sum(ep*ex)))
        worst["devx"] = max(worst["devx"], np.abs(ex - (np.outer(tht, pht)
                                                        + np.outer(pht, tht))).max())
        v = np.linalg.norm(up @ kh)
        worst["up_ek_min"] = min(worst["up_ek_min"], v)
        worst["up_ek_max"] = max(worst["up_ek_max"], v)
    special = {}
    for k in ((1, 1, 1), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 0), (0, 1, 1),
              (1, 2, 0), (2, -1, 3)):
        kh, _, _ = bc.frame(k)
        up, _ = bc.pol_tensors(k, upstream=True)
        ep, _ = bc.pol_tensors(k)
        special[str(k)] = {"upstream_e_khat_norm": float(np.linalg.norm(up @ kh)),
                           "upstream_e_khat_maxcomp": float(np.abs(up @ kh).max()),
                           "fixed_e_khat_norm": float(np.linalg.norm(ep @ kh))}
    res["algebra"] = {"n_directions": 400, "worst": worst, "special": special}
    print("algebra:", json.dumps(res["algebra"], default=float)[:600])


# ---------------------------------------------------------------- stage: id

def fit_tensor(d, k, amp):
    """Least-squares e_ij from h_ij = amp e_ij sin(2 pi k.x) of a t = 0 dump."""
    Z, Y, X = bc.mesh3(d)
    s = np.sin(2*np.pi*(k[0]*X + k[1]*Y + k[2]*Z))
    den = amp*np.sum(s*s)
    e = np.zeros((3, 3))
    for (a, b), c in zip(bc.PAIRS, bc.SYM):
        h = d["g" + c] - (1.0 if a == b else 0.0)
        e[a, b] = e[b, a] = np.sum(h*s)/den
    return e


def con_rows(rundir):
    """Rows of the history with constraint data (Volume > 0), as Track B selects them."""
    names, h = bc.read_hst(glob.glob(os.path.join(rundir, "*.hst"))[0])
    h = h[h[:, 10] > 0]
    return {"t": h[:, 0], "H2": h[:, 3], "M2": h[:, 4]}


def stage_id(res, B, exe, out, nproc):
    ad = B["ad"]
    lw3 = os.path.join(B["pz"], "inputs", "lw_3d.athinput")
    with open(os.path.join(B["pz"], "cases", "lw3d_check.json")) as f:
        cases = {c["name"]: c["overrides"] for c in json.load(f)}
    # Track B's two cases, unchanged, with both executables; restart dumps at t = 0 are
    # written by the deck (output1), the history every 1/16
    jobs = {}
    for tag in ("new", "base"):
        for name in ("lw3d_check_diag", "lw3d_check_axis"):
            jobs[f"{name}_{tag}"] = (exe[tag], lw3, os.path.join(out, "id", f"{name}_{tag}"),
                                     cases[name])
    # amplitude scaling of what remains (new executable, k = (1,1,1), A = 1e-7)
    jobs["diag_A1e-7_new"] = (exe["new"], lw3, os.path.join(out, "id", "diag_A1e-7_new"),
                              cases["lw3d_check_diag"] + ["problem/amp=1.0e-7"])
    # general directions: a few steps are enough (history every step)
    short = ["time/nlim=2", "output1/dt=1000.0", "output2/dt=1000.0", "output3/dt=1000.0",
             "output4/dt=1000.0", "output5/dt=1000.0", "output6/dt=1.0e-9"]
    gen = []
    for k, tag, n in (((1, 2, 0), "new", 16), ((1, 2, 0), "new", 32), ((1, 2, 0), "new", 64),
                      ((1, 2, 0), "base", 16), ((2, -1, 3), "new", 16),
                      ((2, -1, 3), "base", 16), ((2, -1, 3), "new", 32)):
        name = f"{ktag(k)}_N{n}_{tag}"
        gen.append((name, k, tag, n))
        jobs[name] = (exe[tag], lw3, os.path.join(out, "id", name),
                      bc.mesh_overrides(n) + karg(k) + short)
    recs = bc.run_many(jobs, nproc)
    r = {"wall_s": {n: v["wall_s"] for n, v in recs.items()}}

    # tensor read back from the restart dump at t = 0
    rb = {}
    for name, k in (("lw3d_check_diag_new", (1, 1, 1)), ("lw3d_check_diag_base", (1, 1, 1)),
                    ("lw3d_check_axis_new", (1, 0, 0)), ("lw3d_check_axis_base", (1, 0, 0))) \
            + tuple((n, k) for n, k, _, nn in gen if nn == 16):
        d = ad.read_rst(sorted(glob.glob(os.path.join(recs[name]["rundir"], "rst",
                                                      "*.rst")))[0])
        assert d["time"] == 0.0
        e = fit_tensor(d, k, A0)
        ep, _ = bc.pol_tensors(k)
        up, _ = bc.pol_tensors(k, upstream=True)
        kh = np.asarray(k, float)/np.linalg.norm(k)
        rb[name] = {"k": k, "fitted": e.tolist(),
                    "max_dev_from_corrected": float(np.abs(e - ep).max()),
                    "max_dev_from_upstream": float(np.abs(e - up).max()),
                    "e_khat_norm": float(np.linalg.norm(e @ kh)),
                    "trace": float(np.trace(e))}
    r["readback"] = rb

    # constraints: Track B's quantities (first history row with data)
    con = {}
    for name in recs:
        c = con_rows(recs[name]["rundir"])
        con[name] = {"t_first": float(c["t"][0]), "H2_first": float(c["H2"][0]),
                     "M2_first": float(c["M2"][0]), "t": c["t"].tolist(),
                     "H2": c["H2"].tolist(), "M2": c["M2"].tolist()}
    r["constraints"] = con
    # Track B's prediction for the upstream tensor (its ana_check3d.predicted)
    up, _ = bc.pol_tensors((1, 1, 1), upstream=True)
    kv = np.array([1.0, 1.0, 1.0])
    Hamp = (2*np.pi)**2*A0*abs(kv @ up @ kv)
    Mamp = 2*np.pi**2*np.linalg.norm(kv)*A0*np.abs(up @ kv)
    r["upstream_first_order_prediction_k111"] = {"H2": float(Hamp**2/2),
                                                 "M2": float(np.sum(Mamp**2)/2)}
    r["track_b_numbers"] = {"H2_k111": 1.385e-9, "M2_k111": 1.558e-9, "H2_k100": 4e-22,
                            "M2_k100": 1e-22,
                            "source": "B-emd-gw outbox z4c-linear-wave-polarization, runs "
                                      "-113216/-113217-0ea0f74"}
    d = con["lw3d_check_diag_new"]
    a = con["diag_A1e-7_new"]
    r["amplitude_scaling_k111_new"] = {"H2_ratio_A1e-6_over_A1e-7": d["H2_first"]/a["H2_first"],
                                       "M2_ratio": d["M2_first"]/a["M2_first"]}
    k120 = [con[f"k120_N{n}_new"] for n in (16, 32, 64)]
    r["k120_convergence_new"] = {
        "N": [16, 32, 64], "H2": [c["H2_first"] for c in k120],
        "M2": [c["M2_first"] for c in k120],
        "H2_ratio": [k120[i]["H2_first"]/k120[i + 1]["H2_first"] for i in range(2)],
        "M2_ratio": [k120[i]["M2_first"]/k120[i + 1]["M2_first"] for i in range(2)]}
    res["id"] = r
    print("id: readback", {n: (v["max_dev_from_corrected"], v["max_dev_from_upstream"])
                           for n, v in rb.items()})
    print("id: constraints first row", {n: (v["H2_first"], v["M2_first"])
                                        for n, v in con.items()})
    print("id: scaling", r["amplitude_scaling_k111_new"], r["k120_convergence_new"])


# ---------------------------------------------------------------- stage: evol and pol

def predict3d(B, k, N, T, nsteps, ng=4, sigma=0.5, L=1.0):
    """Gain of the Fourier mode k after nsteps RK4 steps to time T: Track B's prediction
    (predict_lw.py) with the second-derivative symbol and the Kreiss-Oliger rate summed
    over the three directions."""
    pl = B["pl"]
    dx = L/N
    th = 2*np.pi*np.asarray(k, float)*dx
    w2 = -sum(pl.symbol_d2(ng, np.array(t)) for t in th)/dx**2
    wh = np.sqrt(w2)
    d = sum(sigma*2.0**(-2*ng)*(2*np.sin(t/2))**(2*ng)/dx for t in th)
    dt = T/nsteps
    z = (-d + 1j*wh)*dt
    R = 1 + z + z**2/2 + z**3/6 + z**4/24
    G = R**nsteps*np.exp(-1j*2*np.pi*np.linalg.norm(k)*T)
    # the code's wave moves as exp(-i w t): numerical phase advance minus exact
    return abs(G) - 1.0, float(np.angle(G))


def analyse_dump(B, path, k, amp, ampx, phx, do_weyl=True):
    """Everything measured on one double-precision z4c dump of a wave run."""
    tt, weyl, readers, Grid = B["tt"], B["weyl"], B["readers"], B["grid"].Grid
    raw = athena_bin.read_bin(path)
    assert raw["var_size"] == 8
    d = bc.z4c_from_bin(raw)
    t = d["time"]
    Z, Y, X = bc.mesh3(d)
    hex_, Aex = bc.exact_wave(X, Y, Z, t, k, amp, ampx, phx)
    h = bc.tensor(d, "g") - np.eye(3)[:, :, None, None, None]
    At = bc.tensor(d, "A")
    atot = max(amp, ampx)
    kn = np.linalg.norm(k)
    out = {"t": t, "cycle": d["cycle"],
           "max_err_gt_over_A": float(np.abs(h - hex_).max()/atot),
           "max_err_At_over_pikA": float(np.abs(At - Aex).max()/(np.pi*kn*atot))}
    # complex gain of the mode: h_c = Re[-i a_c exp(i P)], a_c = amp e+_c + ampx ex_c e^{i phx}
    ep, ex = bc.pol_tensors(k)
    P0 = 2*np.pi*(k[0]*X + k[1]*Y + k[2]*Z)
    zc = np.zeros((3, 3), complex)
    for a in range(3):
        for b in range(3):
            zc[a, b] = 2j*np.mean(h[a, b]*np.exp(-1j*P0))*np.exp(1j*2*np.pi*kn*t)
    aref = amp*ep + ampx*ex*np.exp(1j*phx)
    G = np.sum(np.conj(aref)*zc)/np.sum(np.abs(aref)**2)
    out["gain_abs_minus_1"] = float(abs(G) - 1.0)
    out["gain_phase"] = float(np.angle(G))
    out["tensor_shape_dev"] = float(np.abs(zc - G*aref).max()/atot)
    # diagnostics of gw_diag
    g = Grid((len(d["x"]), len(d["y"]), len(d["z"])),
             tuple(d["xmax"] - d["xmin"]), tuple(d["xmin"]))
    chi, gt, At2, trK, alpha, beta = readers.z4c_tensors(d)
    hTT, hdTT = tt.tt_from_conformal(gt, At2, g)
    hp, hx = tt.polarization_along(hTT, k)
    Xg, Yg, Zg = g.mesh()
    Pg = 2*np.pi*(k[0]*Xg + k[1]*Yg + k[2]*Zg - kn*t)
    hp_ex = amp*np.sin(Pg)
    hx_ex = ampx*np.sin(Pg + phx)
    out["tt_hplus_err_over_A"] = float(np.abs(hp - hp_ex).max()/atot)
    out["tt_hcross_err_over_A"] = float(np.abs(hx - hx_ex).max()/atot)
    out["tt_hplus_max_over_A"] = float(np.abs(hp).max()/atot)
    out["tt_hcross_max_over_A"] = float(np.abs(hx).max()/atot)
    out["nonTT_over_A"] = float(np.abs(h - hTT).max()/atot)
    sp = tt.gw_spectrum(hTT, hdTT, g, chi_bar=float(chi.mean()))
    rho_ref = (2*np.pi*kn)**2*(amp**2 + ampx**2)/(32*np.pi)
    out["rho_tot_over_ref"] = float((sp["rho_kin_total"] + sp["rho_grad_total"])/rho_ref)
    hel = tt.helicity_spectrum(hTT, hdTT, g, chi_bar=float(chi.mean()))
    tot = hel["rho_plus_total"] + hel["rho_minus_total"]
    out["helicity_plus_fraction"] = float(hel["rho_plus_total"]/tot)
    out["helicity_minus_fraction"] = float(hel["rho_minus_total"]/tot)
    prof = None
    if do_weyl:
        gamma, K, _, _ = readers.z4c_to_adm(d)
        E, Bm = weyl.electric_magnetic(gamma, K, g, order=6)
        p4 = weyl.psi4(E, Bm, gamma, g, direction=k)
        # Psi_4 = d_t^2 h_+ - i d_t^2 h_x
        w2 = (2*np.pi*kn)**2
        ana = -w2*amp*np.sin(Pg) + 1j*w2*ampx*np.sin(Pg + phx)
        out["psi4_err_rel"] = float(np.abs(p4 - ana).max()/np.abs(ana).max())
        p4r = weyl.psi4(E, Bm, gamma, g, direction=-np.asarray(k, float))
        out["psi4_reverse_over_max"] = float(np.abs(p4r).max()/np.abs(ana).max())
        prof = {"x": d["x"].tolist(), "psi4_re": (p4.real[0, 0]/w2/atot).tolist(),
                "psi4_im": (p4.imag[0, 0]/w2/atot).tolist(),
                "ana_re": (ana.real[0, 0]/w2/atot).tolist(),
                "ana_im": (ana.imag[0, 0]/w2/atot).tolist(),
                "hp": (hp[0, 0]/atot).tolist(), "hx": (hx[0, 0]/atot).tolist(),
                "hp_ex": (hp_ex[0, 0]/atot).tolist(), "hx_ex": (hx_ex[0, 0]/atot).tolist(),
                "gxy": (h[0, 1][0, 0]/atot).tolist(), "gxy_ex": (hex_[0, 1][0, 0]/atot).tolist(),
                "gxx": (h[0, 0][0, 0]/atot).tolist(), "gxx_ex": (hex_[0, 0][0, 0]/atot).tolist()}
    return out, prof


def stage_evol(res, B, exe, out, nproc, Ns):
    k = (1, 1, 1)
    jobs = {f"evol_N{n}": (exe["new"], INP, os.path.join(out, "evol", f"N{n}"),
                           bc.mesh_overrides(n)) for n in Ns}
    recs = bc.run_many(jobs, nproc)
    r = {}
    for n in Ns:
        rd = recs[f"evol_N{n}"]["rundir"]
        files = sorted(glob.glob(os.path.join(rd, "bin", "*.z4c.*.bin")))
        first, _ = analyse_dump(B, files[0], k, A0, 0.0, 0.0, do_weyl=False)
        last, prof = analyse_dump(B, files[-1], k, A0, 0.0, 0.0)
        pa, pp = predict3d(B, k, n, last["t"], last["cycle"])
        c = con_rows(rd)
        with open(os.path.join(rd, "lwo-errs.dat")) as f:
            errs = f.read().split("\n")[1].split()
        r[str(n)] = {"first": first, "last": last, "profile": prof,
                     "pred_gain_abs_minus_1": pa, "pred_gain_phase": pp,
                     "H2_end": float(c["H2"][-1]), "M2_end": float(c["M2"][-1]),
                     "errs_dat_rms_L1": float(errs[4]), "wall_s": recs[f"evol_N{n}"]["wall_s"]}
        print(f"evol N={n}: gain-1 {last['gain_abs_minus_1']:+.3e} (pred {pa:+.3e}), phase "
              f"{last['gain_phase']:+.3e} (pred {pp:+.3e}), hx/A {last['tt_hcross_max_over_A']:.2e},"
              f" psi4 err {last['psi4_err_rel']:.2e}, shape dev {last['tensor_shape_dev']:.2e}")
    res["evol"] = r


def stage_pol(res, B, exe, out, nproc):
    k = (1, 1, 1)
    n = 16
    cases = {"cross": (0.0, A0, 0.0), "circular": (A0, A0, 0.5*np.pi),
             "circular_other": (A0, A0, -0.5*np.pi)}
    jobs = {}
    for name, (amp, ampx, phx) in cases.items():
        jobs[f"pol_{name}"] = (exe["new"], INP, os.path.join(out, "pol", name),
                               bc.mesh_overrides(n) + [f"problem/amp={amp!r}",
                                                       f"problem/amp_cross={ampx!r}",
                                                       f"problem/phase_cross={phx!r}"])
    recs = bc.run_many(jobs, nproc)
    r = {}
    for name, (amp, ampx, phx) in cases.items():
        rd = recs[f"pol_{name}"]["rundir"]
        files = sorted(glob.glob(os.path.join(rd, "bin", "*.z4c.*.bin")))
        first, _ = analyse_dump(B, files[0], k, amp, ampx, phx, do_weyl=True)
        last, prof = analyse_dump(B, files[-1], k, amp, ampx, phx)
        c = con_rows(rd)
        r[name] = {"amp": amp, "amp_cross": ampx, "phase_cross": phx, "first": first,
                   "last": last, "profile": prof, "H2_first": float(c["H2"][0]),
                   "M2_first": float(c["M2"][0])}
        print(f"pol {name}: t=0 h+ {first['tt_hplus_max_over_A']:.3e} hx "
              f"{first['tt_hcross_max_over_A']:.3e} helicity +{first['helicity_plus_fraction']:.6f}"
              f" -{first['helicity_minus_fraction']:.2e}; end psi4 err {last['psi4_err_rel']:.2e}"
              f" H2 {r[name]['H2_first']:.2e} M2 {r[name]['M2_first']:.2e}")
    res["pol"] = r


# ---------------------------------------------------------------- stage: trackb

def stage_trackb(res, B, exe, out, nproc):
    pz = B["pz"]
    lwx = os.path.join(pz, "inputs", "lw_x.athinput")
    lw3 = os.path.join(pz, "inputs", "lw_3d.athinput")
    with open(os.path.join(pz, "cases", "lw_x_prod.json")) as f:
        cx = {c["name"]: c["overrides"] for c in json.load(f)}
    # deck of lw3d_dump_N32 with the Weyl scalar taken at the end of the step
    os.makedirs(os.path.join(out, "trackb"), exist_ok=True)
    lw3n = os.path.join(out, "trackb", "lw_3d_newtime.athinput")
    with open(lw3) as f:
        txt = f.read()
    key = "waveform_dt          = 0.0625\n"
    assert key in txt
    with open(lw3n, "w") as f:
        f.write(txt.replace(key, key + "waveform_at_new_time = true\n"))
    jobs = {"lw_x_prod_N16": (exe["new"], lwx, os.path.join(out, "trackb", "lw_x_prod_N16"),
                              cx["lw_x_prod_N16"]),
            "lw_x_prod_N32": (exe["new"], lwx, os.path.join(out, "trackb", "lw_x_prod_N32"),
                              cx["lw_x_prod_N32"]),
            "lw3d_dump_N32": (exe["new"], lw3, os.path.join(out, "trackb", "lw3d_dump_N32"), []),
            "lw3d_dump_N32_newtime": (exe["new"], lw3n,
                                      os.path.join(out, "trackb", "lw3d_dump_N32_newtime"), [])}
    recs = bc.run_many(jobs, nproc)
    r = {"wall_s": {n: v["wall_s"] for n, v in recs.items()}}
    # periodic_z4c: its own analysis function on the new runs
    sys.path.insert(0, os.path.join(pz, "analysis"))
    import ana_lw
    table = {16: (-1.72e-4, -2.49e-4), 32: (-1.49e-6, -6.25e-6)}
    lw = {}
    for n in (16, 32):
        a = ana_lw.analyse_run({"output_dir": recs[f"lw_x_prod_N{n}"]["rundir"]}, 0.25, n)
        pa, pp, _, _, _ = B["pl"].predict(4, 0.25, 0.5, a["t"][-1], n)
        lw[str(n)] = {"t_end": float(a["t"][-1]), "amp_err": float(a["amp"][-1]),
                      "phase_err": float(a["ph"][-1]), "track_b_table": table[n],
                      "pred_amp": float(pa), "pred_phase": float(pp)}
    r["lw_x_prod"] = lw
    # gw_diag: its validation script, unchanged, on the two reruns
    va = os.path.join(B["gw"], "scripts", "validate_athenak.py")
    for name in ("lw3d_dump_N32", "lw3d_dump_N32_newtime"):
        od = os.path.join(out, "trackb", "validate_" + name)
        os.makedirs(od, exist_ok=True)
        env = dict(os.environ, RUN_DIR=od, MPLBACKEND="Agg", OMP_NUM_THREADS="4")
        with open(os.path.join(od, "validate.log"), "w") as log:
            p = subprocess.run([sys.executable, va, recs[name]["rundir"]], env=env,
                               stdout=log, stderr=subprocess.STDOUT)
        if p.returncode != 0:
            raise SystemExit(f"validate_athenak.py failed on {name}: see {od}/validate.log")
        with open(os.path.join(od, "results_athenak.json")) as f:
            v = json.load(f)
        rows = v["per_dump"]
        r["validate_" + name] = {
            "amp_ratio_minus_1_range": [min(q["amp_ratio"] for q in rows) - 1,
                                        max(q["amp_ratio"] for q in rows) - 1],
            "phase_err_range": [min(q["phase_err"] for q in rows),
                                max(q["phase_err"] for q in rows)],
            "rho_tot_minus_1_range": [min(q["rho_tot/ref"] for q in rows) - 1,
                                      max(q["rho_tot/ref"] for q in rows) - 1],
            "hx_max_over_A": max(q["hx_over_A"] for q in rows),
            "nonTT_max_over_A": max(q["nonTT_over_A"] for q in rows),
            "psi4x_err_range": [min(w["psi4x_err_vs_analytic"] for w in v["weyl"]),
                                max(w["psi4x_err_vs_analytic"] for w in v["weyl"])],
            "radial_vs_athenak_same_time": [w.get("radial_vs_athenak_max_rel")
                                            for w in v["weyl"]
                                            if w.get("radial_vs_athenak_max_rel") is not None],
            "weyl_output_timing": v["weyl_output_timing"]}
        for fpng in glob.glob(os.path.join(od, "athenak_*.png")):
            shutil.copy(fpng, os.path.join(out, f"trackb_{name}_" + os.path.basename(fpng)))
    r["track_b_readme_numbers"] = {"amp": 3e-7, "phase": 1.2e-6, "rho": 6e-7, "hx": 1e-24,
                                   "nonTT": 2.7e-5, "weyl_lag_steps": -7,
                                   "radial_vs_athenak": [3e-7, 1.8e-6]}
    res["trackb"] = r
    print("trackb lw_x_prod:", lw)
    for name in ("lw3d_dump_N32", "lw3d_dump_N32_newtime"):
        v = r["validate_" + name]
        print(f"trackb validate {name}: amp {v['amp_ratio_minus_1_range']}, phase "
              f"{v['phase_err_range']}, rho {v['rho_tot_minus_1_range']}, weyl best offsets "
              f"{[q['best_offset_steps'] for q in v['weyl_output_timing']['fits']]}, errors "
              f"{[q['err_at_best'] for q in v['weyl_output_timing']['fits']]}, at offset 0 "
              f"{[q['err_at_offset0'] for q in v['weyl_output_timing']['fits']]}")


# ---------------------------------------------------------------- stage: errs

def stage_errs(res, B, exe, out, nproc):
    pz = B["pz"]
    lwx = os.path.join(pz, "inputs", "lw_x.athinput")
    with open(os.path.join(pz, "cases", "lw_x_prod.json")) as f:
        ov = {c["name"]: c["overrides"] for c in json.load(f)}["lw_x_prod_N16"]
    jobs = {}
    for tag in ("new", "base"):
        for tl in ("1.0", "0.5"):
            jobs[f"errs_{tag}_t{tl}"] = (exe[tag], lwx, os.path.join(out, "errs", f"{tag}_t{tl}"),
                                         ov + [f"time/tlim={tl}"])
    recs = bc.run_many(jobs, nproc)
    r = {}
    for name, rec in recs.items():
        with open(os.path.join(rec["rundir"], "lw-errs.dat")) as f:
            lines = f.read().strip().split("\n")
        v = lines[1].split()
        r[name] = {"line": lines[1], "rms_L1": float(v[4]), "Linf": float(v[5]),
                   "gyy_L1": float(v[9]), "gzz_L1": float(v[11])}
    res["errs"] = r
    print("errs:", {n: v["line"] for n, v in r.items()})


# ---------------------------------------------------------------- figures

def figures(res, out):
    fs.use_style()
    C = fs.PAL
    made = []
    if "id" in res:
        con = res["id"]["constraints"]
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
        a1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.6)
        a2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.6)
        for name, col, lab in (("lw3d_check_diag_base", C["blue"], "upstream signs, k = (1,1,1)"),
                               ("lw3d_check_diag_new", C["red"], "corrected, k = (1,1,1)"),
                               ("lw3d_check_axis_new", C["yellow"], "corrected, k = (1,0,0)"),
                               ("lw3d_check_axis_base", C["green"], "upstream, k = (1,0,0)")):
            c = con[name]
            a1.semilogy(c["t"], c["H2"], color=col, ls="-", label=lab)
            a1.semilogy(c["t"], c["M2"], color=col, ls="--")
        a1.axhline(1e-20, **fs.THIN)
        a1.text(0.02, 2e-20, "criterion of Track B", fontsize=7)
        tb = res["id"]["track_b_numbers"]
        a1.plot([0.0625], [tb["H2_k111"]], "o", ms=5, mfc="none", color="k",
                label="Track B (upstream)")
        a1.plot([0.0625], [tb["M2_k111"]], "s", ms=5, mfc="none", color="k")
        a1.set_ylim(1e-25, 1e-6)
        a1.set_xlabel("t")
        a1.set_ylabel(r"$\int H^2 dV$ (solid), $\int M^2 dV$ (dashed)")
        a1.legend(loc="center right", fontsize=7)
        k = res["id"]["k120_convergence_new"]
        N = np.array(k["N"], float)
        a2.loglog(N, k["H2"], "o-", color=C["red"], label=r"$\int H^2 dV$, corrected, k = (1,2,0)")
        a2.loglog(N, k["M2"], "s--", color=C["red"], mfc="none", label=r"$\int M^2 dV$")
        a2.loglog(N, k["M2"][0]*(N/N[0])**-12.0, **dict(fs.GUIDE, lw=1.0), label=r"$N^{-12}$")
        b = con["k120_N16_base"]
        a2.plot([16], [b["H2_first"]], "o", color=C["blue"], label="upstream signs")
        a2.plot([16], [b["M2_first"]], "s", color=C["blue"], mfc="none")
        a2.set_xlabel("cells per box length N")
        a2.set_ylabel("constraint norms after the first step")
        a2.set_xticks([16, 32, 64])
        a2.set_xticklabels(["16", "32", "64"])
        a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        a2.legend(loc="center left", fontsize=7)
        made += fs.save(fig, os.path.join(out, "t1_constraints"))
        plt.close(fig)
    if "evol" in res:
        ev = res["evol"]
        Ns = sorted(int(n) for n in ev)
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
        a1 = fs.inch_axes(fig, 0.7, 0.55, 3.0, 2.6)
        a2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.6)
        p = ev[str(Ns[-1])]["profile"]
        x = np.array(p["x"])
        a1.plot(x, p["gxx_ex"], color=C["blue"], label=r"exact $h_{xx}/A$")
        a1.plot(x, p["gxx"], "o", ms=3, color=C["red"], label=f"code, N = {Ns[-1]}")
        a1.plot(x, p["gxy_ex"], color=C["blue"], ls="--", label=r"exact $h_{xy}/A$")
        a1.plot(x, p["gxy"], "s", ms=3, mfc="none", color=C["red"])
        a1.plot(x, p["psi4_re"], "^", ms=3, color=C["yellow"],
                label=r"Re $\Psi_4/(\omega^2 A)$, gw_diag")
        a1.plot(x, p["ana_re"], color="k", lw=1.0, ls=":", label=r"$\ddot h_+/(\omega^2 A)$")
        a1.set_xlabel("x (line through the first cell in y and z)")
        a1.set_ylabel("after one period, k = (1,1,1)")
        a1.set_ylim(-1.9, 1.9)
        a1.legend(loc="upper center", ncol=2, fontsize=7)
        N = np.array(Ns, float)
        a2.loglog(N, [abs(ev[str(n)]["last"]["gain_abs_minus_1"]) for n in Ns], "o-",
                  color=C["red"], label="|amplitude error|")
        a2.loglog(N, [abs(ev[str(n)]["pred_gain_abs_minus_1"]) for n in Ns],
                  **dict(fs.GUIDE, lw=1.0), label="Fourier symbol of the scheme")
        a2.loglog(N, [abs(ev[str(n)]["last"]["gain_phase"]) for n in Ns], "s--", mfc="none",
                  color=C["blue"], label="|phase error| (rad)")
        a2.loglog(N, [abs(ev[str(n)]["pred_gain_phase"]) for n in Ns], **dict(fs.GUIDE, lw=1.0))
        a2.loglog(N, [ev[str(n)]["last"]["psi4_err_rel"] for n in Ns], "^:", color=C["yellow"],
                  label=r"$\Psi_4$ (gw_diag) vs analytic")
        a2.loglog(N, [ev[str(n)]["last"]["tt_hcross_max_over_A"] + 1e-30 for n in Ns], "d-.",
                  color=C["green"], label=r"max $|h_\times|/A$")
        a2.set_xlabel("cells per box length N")
        a2.set_ylabel("error after one period")
        a2.set_xticks(Ns)
        a2.set_xticklabels([str(n) for n in Ns])
        a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        a2.legend(loc="center left", fontsize=7)
        made += fs.save(fig, os.path.join(out, "t1_evolution"))
        plt.close(fig)
    if "pol" in res:
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
        for i, name in enumerate(("cross", "circular")):
            ax = fs.inch_axes(fig, 0.7 + 4.0*i, 0.55, 3.0, 2.35)
            p = res["pol"][name]["profile"]
            x = np.array(p["x"])
            ax.plot(x, p["hp_ex"], color=C["blue"], label=r"exact $h_+/A$")
            ax.plot(x, p["hp"], "o", ms=3, color=C["red"], label=r"gw_diag $h_+/A$")
            ax.plot(x, p["hx_ex"], color=C["blue"], ls="--", label=r"exact $h_\times/A$")
            ax.plot(x, p["hx"], "s", ms=3, mfc="none", color=C["red"],
                    label=r"gw_diag $h_\times/A$")
            ax.plot(x, p["ana_im"], color="k", lw=1.0, ls=":",
                    label=r"$-\ddot h_\times/(\omega^2 A)$")
            ax.plot(x, p["psi4_im"], "^", ms=3, color=C["yellow"],
                    label=r"Im $\Psi_4/(\omega^2 A)$")
            ax.set_ylim(-1.9, 1.9)
            ax.set_xlabel("x")
            ax.set_title(f"{name} wave, k = (1,1,1), N = 16, one period", fontsize=10)
            if i == 0:
                ax.legend(loc="upper left", ncol=2, fontsize=6.5)
        made += fs.save(fig, os.path.join(out, "t1_polarization"))
        plt.close(fig)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe-new", required=True)
    ap.add_argument("--exe-base", required=True)
    ap.add_argument("--bdir", default=bc.B_DEFAULT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--stages", default="algebra,id,evol,pol,trackb,errs")
    ap.add_argument("--evol-n", default="16,32")
    ap.add_argument("--nproc", type=int, default=8)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    B = bc.track_b(a.bdir)
    exe = {"new": os.path.abspath(a.exe_new), "base": os.path.abspath(a.exe_base)}
    resfile = os.path.join(out, "results_t1.json")
    res = {}
    if os.path.exists(resfile):
        with open(resfile) as f:
            res = json.load(f)
    res["meta"] = {"exe": exe, "bdir": a.bdir, "commit": bc.git_rev(),
                   "track_b_commit": bc.git_rev("track/B-emd-gw")}
    st = a.stages.split(",")
    if "algebra" in st:
        stage_algebra(res)
    if "id" in st:
        stage_id(res, B, exe, out, a.nproc)
    if "evol" in st:
        stage_evol(res, B, exe, out, a.nproc, [int(v) for v in a.evol_n.split(",")])
    if "pol" in st:
        stage_pol(res, B, exe, out, a.nproc)
    if "errs" in st:
        stage_errs(res, B, exe, out, a.nproc)
    if "trackb" in st:
        stage_trackb(res, B, exe, out, a.nproc)
    bc.save_json(res, resfile)
    print("figures:", figures(res, out))


if __name__ == "__main__":
    main()
