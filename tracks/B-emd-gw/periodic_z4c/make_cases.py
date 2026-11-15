#!/usr/bin/env python3
"""Write the initial-data files (nrpic_cosmo id = file) and the case lists of the
periodic_z4c package.

    python3 make_cases.py            # writes scratch/B-emd-gw/ids/*.bin and cases/*.json

Sets (each case becomes one registered run through launch.py):
  lw_x_prod   TT wave along x, production numerics (ng 4, cfl 0.25, KO 0.5), N 16..128
  lw_x_ref    same wave, numerics of athenak/inputs/tests/linear_wave_z4c.athinput
              (ng 3, cfl 0.3, KO 1, default gauge: 1+log, Gamma driver), N 16..128
  lw_x_nodiss production numerics without Kreiss-Oliger dissipation, N 32, 64
  lw3d_check  3D box, k = (1,1,1) and (1,0,0), constraints of the initial data
  lw3d_dump   3D box 32^3, k = (1,0,0), dumps for gw_diag
  awa_gw      gauge wave A = 0.01, 0.1, N = 50, 100, 200 to t = 20; N = 50 to t = 200
  gauge_lin   pure-gauge data kappa = 1e-6, nine gauge options, N = 64 (and 32, 128)
  gauge_nl    pure-gauge data kappa = 1.5, six gauge options, N = 128
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "analysis"))
import refsol as rs  # noqa: E402

IDS = "/data/haiyangw/nrpic/scratch/B-emd-gw/ids"
CASES = os.path.join(HERE, "cases")


def thin(N, L=1.0, nghost=None):
    """Overrides for a thin box of N x 4 x 4 cubic cells over [0, L)."""
    dx = L/N
    o = [f"mesh/nx1={N}", f"meshblock/nx1={N}", f"mesh/x1max={L!r}",
         f"mesh/x2max={4*dx!r}", f"mesh/x3max={4*dx!r}"]
    return o, 1.5*dx


GAUGES = {
    # name: overrides of <z4c> (all others as in gauge.athinput: everything zero)
    "harmonic":  {"lapse_harmonic": 1.0},
    "onelog":    {"lapse_oplog": 2.0},
    "conformal": {"lapse_harmonic": 0.3333333333333333},
    "volume":    {"lapse_volume": 0.3333333333333333},
    "kdriver":   {"lapse_harmonic": 0.3333333333333333, "lapse_kdriver": 1.0},
    "geodesic":  {},
    "onelog_gd": {"lapse_oplog": 2.0, "shift_Gamma": 1.0, "shift_eta": 2.0,
                  "lapse_advect": 1.0, "shift_advect": 1.0},
    "conf_gd":   {"lapse_harmonic": 0.3333333333333333, "shift_Gamma": 0.75,
                  "shift_eta": 1.0, "shift_advect": 1.0},
    "harm_hs":   {"lapse_harmonic": 1.0, "shift_alpha2Gamma": 1.0, "shift_H": 1.0},
}
# gauge.athinput sets lapse_harmonic = 1/3; every case states its lapse in full
LAPSE_KEYS = ["lapse_oplog", "lapse_harmonic", "lapse_volume", "lapse_kdriver",
              "lapse_advect", "shift_Gamma", "shift_alpha2Gamma", "shift_H",
              "shift_eta", "shift_advect"]


def gauge_overrides(g):
    o = []
    for k in LAPSE_KEYS:
        o.append(f"z4c/{k}={GAUGES[g].get(k, 0.0)!r}")
    return o


def pure_gauge_id(N, kappa):
    path = os.path.join(IDS, f"puregauge_N{N}_k{kappa:g}.bin")
    X = (np.arange(N) + 0.5)/N
    K = kappa*np.sin(2*np.pi*X)
    z = np.zeros(N)
    rs.write_nrcosmo(path, np.ones(N), K, np.ones(N),
                     [2*K/3, z, z, -K/3, z, -K/3], (N, 4, 4))
    return path


def gauge_wave_id(N, A):
    L, X, psi, K, alpha, ahat = rs.gw_initial_fields(N, A)
    path = os.path.join(IDS, f"gaugewave_N{N}_A{A:g}.bin")
    rs.write_nrcosmo(path, psi, K, alpha, ahat, (N, 4, 4))
    return path, L


def main():
    os.makedirs(IDS, exist_ok=True)
    os.makedirs(CASES, exist_ok=True)
    sets = {}

    # ---- TT wave along x
    c = []
    for N in (16, 32, 64, 128):
        o, s = thin(N)
        c.append(dict(name=f"lw_x_prod_N{N}", set="lw_x_prod", input="inputs/lw_x.athinput",
                      overrides=o + [f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}"],
                      purpose="TT wave along x for 10 crossings, production numerics: "
                              "amplitude and phase error, convergence order",
                      kind="scouting"))
    sets["lw_x_prod"] = c
    c = []
    for N in (16, 32, 64, 128):
        o, s = thin(N)
        c.append(dict(name=f"lw_x_ref_N{N}", set="lw_x_ref", input="inputs/lw_x.athinput",
                      overrides=o + [f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                                     "mesh/nghost=3", "time/cfl_number=0.3", "z4c/diss=1.0",
                                     "z4c/damp_kappa1=0.0", "z4c/lapse_oplog=2.0",
                                     "z4c/lapse_harmonic=0.0", "z4c/lapse_advect=1.0",
                                     "z4c/shift_Gamma=1.0", "z4c/shift_eta=2.0",
                                     "z4c/shift_advect=1.0"],
                      purpose="TT wave along x, numerics and gauge of the upstream input "
                              "athenak/inputs/tests/linear_wave_z4c.athinput",
                      kind="scouting"))
    sets["lw_x_ref"] = c
    c = []
    for N in (32, 64):
        o, s = thin(N)
        c.append(dict(name=f"lw_x_nodiss_N{N}", set="lw_x_nodiss", input="inputs/lw_x.athinput",
                      overrides=o + [f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                                     "z4c/diss=0.0"],
                      purpose="TT wave along x without Kreiss-Oliger dissipation: "
                              "amplitude error of RK4 alone",
                      kind="scouting"))
    sets["lw_x_nodiss"] = c
    # follow-up: is the floor at N = 128 roundoff of 1 + h (deviation ~ 1/A)?
    c = []
    refnum = ["mesh/nghost=3", "time/cfl_number=0.3", "z4c/diss=1.0", "z4c/damp_kappa1=0.0"]
    for nm, extra, A in (("prod_A1e-5", [], 1e-5), ("refconf_A1e-6", refnum, 1e-6),
                         ("refconf_A1e-5", refnum, 1e-5), ("prod_A1e-7", [], 1e-7),
                         ("refconf_A1e-7", refnum, 1e-7)):
        o, s = thin(128)
        c.append(dict(name=f"lw_x_{nm}_N128", set="lw_x_roundoff", input="inputs/lw_x.athinput",
                      overrides=o + [f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                                     f"problem/amp={A!r}"] + extra,
                      purpose="TT wave along x at 128 cells: test whether the departure "
                              "from the Fourier prediction scales as 1/A (roundoff of 1+h); "
                              "conformal-time lapse, under which the second-order "
                              "homogeneous drift leaves the coordinate light speed fixed",
                      kind="scouting"))
    sets["lw_x_roundoff"] = c

    # ---- 3D box
    period3 = 1.0/np.sqrt(3.0)
    c = []
    for kv, nm in (((1, 1, 1), "diag"), ((1, 0, 0), "axis")):
        c.append(dict(name=f"lw3d_check_{nm}", set="lw3d_check", input="inputs/lw_3d.athinput",
                      overrides=["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16",
                                 "meshblock/nx1=16", "meshblock/nx2=16", "meshblock/nx3=16",
                                 f"problem/kx1={kv[0]}.0", f"problem/kx2={kv[1]}.0",
                                 f"problem/kx3={kv[2]}.0", "time/tlim=1.0",
                                 "output1/dt=1000.0", "output2/dt=0.0625",
                                 "output3/dt=1000.0", "output4/dt=0.0625",
                                 "output5/dt=1000.0", "output6/dt=0.0625"],
                      purpose="constraints of the initial data of z4c_linear_wave for an "
                              "oblique and an axis-aligned wave vector (polarization tensor)",
                      kind="scouting"))
    sets["lw3d_check"] = c
    sets["lw3d_dump"] = [dict(
        name="lw3d_dump_N32", set="lw3d_dump", input="inputs/lw_3d.athinput", overrides=[],
        purpose="metric dumps of an analytic linear TT wave (k along x, A = 1e-6, 32^3, "
                "two periods, every 1/16 period) for the gw_diag package",
        kind="scouting")]

    # ---- gauge wave (Apples with Apples)
    c = []
    for A in (0.01, 0.1):
        for N, T in ((50, 20.0), (100, 20.0), (200, 20.0), (50, 200.0)):
            path, L = gauge_wave_id(N, A)
            o, s = thin(N, L)
            nm = f"awa_gw_A{A:g}_N{N}_T{T:g}"
            c.append(dict(name=nm, set="awa_gw", input="inputs/gauge.athinput",
                          overrides=o + gauge_overrides("harmonic") + [
                              f"problem/id_file={path}", f"time/tlim={T!r}",
                              f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                              f"output2/slice_x2={s!r}", f"output2/slice_x3={s!r}",
                              f"output1/dt={0.0625 if T <= 20 else 1.0!r}",
                              f"output2/dt={0.0625 if T <= 20 else 1.0!r}"],
                          extra_inputs=[path],
                          purpose=f"Apples-with-Apples gauge wave A = {A}, harmonic slicing, "
                                  f"zero shift, in proper-length coordinates (box {L!r})",
                          kind="scouting"))
    sets["awa_gw"] = c

    # ---- pure-gauge record of the lapse and shift options
    c = []
    for g in GAUGES:
        for N in ((32, 64, 128) if g == "onelog_gd" else (64,)):
            path = pure_gauge_id(N, 1e-6)
            o, s = thin(N)
            c.append(dict(name=f"gauge_lin_{g}_N{N}", set="gauge_lin",
                          input="inputs/gauge.athinput",
                          overrides=o + gauge_overrides(g) + [
                              f"problem/id_file={path}",
                              f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                              f"output2/slice_x2={s!r}", f"output2/slice_x3={s!r}"],
                          extra_inputs=[path],
                          purpose=f"pure-gauge data K_xx = 1e-6 sin(2 pi x), gauge {g}: "
                                  "linear lapse and shift dynamics against the linearized "
                                  "system of refsol.gauge_matrix",
                          kind="scouting"))
    sets["gauge_lin"] = c
    c = []
    for g in ("harmonic", "onelog", "conformal", "volume", "kdriver", "onelog_gd"):
        N = 128
        path = pure_gauge_id(N, 1.5)
        o, s = thin(N)
        c.append(dict(name=f"gauge_nl_{g}_N{N}", set="gauge_nl", input="inputs/gauge.athinput",
                      overrides=o + gauge_overrides(g) + [
                          f"problem/id_file={path}",
                          f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                          f"output2/slice_x2={s!r}", f"output2/slice_x3={s!r}"],
                      extra_inputs=[path],
                      purpose=f"pure-gauge data K_xx = 1.5 sin(2 pi x), gauge {g}: "
                              "nonlinear behaviour (steepening, gauge shocks, failure time)",
                      kind="scouting"))
    sets["gauge_nl"] = c
    # follow-up: is the failure of the conformal-time lapse at t ~ 2.7 a gauge shock
    # (continuum: gradient curves converge, failure time nearly independent of N)?
    c = []
    for N in (64, 256):
        path = pure_gauge_id(N, 1.5)
        o, s = thin(N)
        c.append(dict(name=f"gauge_nl_conformal_N{N}", set="gauge_nl_res",
                      input="inputs/gauge.athinput",
                      overrides=o + gauge_overrides("conformal") + [
                          f"problem/id_file={path}", "time/tlim=4.0",
                          f"output1/slice_x2={s!r}", f"output1/slice_x3={s!r}",
                          f"output2/slice_x2={s!r}", f"output2/slice_x3={s!r}",
                          "output1/dt=0.03125", "output2/dt=0.03125"],
                      extra_inputs=[path],
                      purpose="pure-gauge data K_xx = 1.5 sin(2 pi x), conformal-time lapse: "
                              "resolution dependence of the steepening and of the failure",
                      kind="scouting"))
    sets["gauge_nl_res"] = c

    for k, v in sets.items():
        with open(os.path.join(CASES, f"{k}.json"), "w") as f:
            json.dump(v, f, indent=1)
            f.write("\n")
        print(k, len(v))


if __name__ == "__main__":
    main()
