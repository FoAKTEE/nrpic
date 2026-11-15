#!/usr/bin/env python3
"""Start-time check of the Einstein-Straus data inside AthenaK (nrpic_cf with the
format-2 reader of branch core/id-extrinsic): the code's own Hamiltonian and momentum
residuals at t = 0 on a uniform mesh, against resolution, next to the offline values.

    code_t0_check.py prep --tab TABLE --dx DX --half HALF --out DIR
        writes DIR/es_box.nrp (lattice dust at the cell centres, hp = dx, only inside the
        mesh; CIC then deposits the exact density at cell centres) and DIR/es_t0.athinput
    code_t0_check.py analyse --runs RUN_DIR [RUN_DIR ...] --out DIR
        reads es.field.00000.bin of each run, writes DIR/code_t0.json and the figure
        figs/code_t0.(png,pdf)

Regions (r = coordinate radius of the cell centre; cells within 4 cells of the mesh
boundary are left out): puncture r < 3, transition 4 < r < 30, inner dust edge
34 < r < 46, plateau 46 < r < HALF - 4 dx (when the mesh reaches it).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))
import es_model as em  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

FIGS = os.path.join(HERE, "figs")

INPUT = """# t = 0 constraint check of the Einstein-Straus data (D-pre-1), uniform mesh.
<job>
basename  = es

<mesh>
nghost    = 4
nx1       = {n}
x1min     = {lo!r}
x1max     = {hi!r}
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = {n}
x2min     = {lo!r}
x2max     = {hi!r}
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = {n}
x3min     = {lo!r}
x3max     = {hi!r}
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = {nb}
nx2       = {nb}
nx3       = {nb}

<time>
evolution  = dynamic
integrator = rk4
cfl_number = 0.25
nlim       = 0
tlim       = 1.0
ndiag      = 1

<z4c>
lapse_oplog     = 2.0
lapse_harmonicf = 1.0
lapse_harmonic  = 0.0
lapse_advect    = 1.0
shift_Gamma     = 0.75
shift_eta       = 2.0
shift_advect    = 1.0
diss            = 0.5
chi_div_floor   = 1.0e-5
damp_kappa1     = 0.02
damp_kappa2     = 0.0
excise_chi      = 0.0

<particles>
particle_type  = nrpic
pusher         = midpoint
metric         = mesh
interp         = hermite
tolerance      = 1.0e-10
max_iterations = 50
deposit        = true
deposit_shape  = cic
nfilter        = 0
filter_compensate = false
source_density = false
source_extrap  = false
alpha_exc      = -1.0
hist_dcycle    = 1
cstat_dcycle   = 1
traj_dcycle    = 0
traj_ntrack    = 0
snap_dt        = -1.0
field_constraints = true
field_time1    = 1.0e9
particle_file  = {nrp}

<problem>
pgen_name  = nrpic_cf
ncomp      = 2
comp0_type = table
comp0_file = {tab}
comp1_type = puncture
comp1_mass = {m_p!r}
lapse      = table
lapse_comp = 0
shift      = zero

<output1>
file_type = hst
dt        = 1.0
"""


def prep(a):
    os.makedirs(a.out, exist_ok=True)
    model = em.EinsteinStrausBH()
    _, hdr = em.read_tab2(a.tab)
    m_p = float(hdr["m_p"])
    assert abs(m_p - model.m_p) < 1e-14, "table and model disagree"
    n = int(round(2 * a.half / a.dx))
    k = (np.arange(-n // 2, n // 2) + 0.5) * a.dx               # cell centres
    xs, ms = [], []
    for xi in k:
        Y, Z = np.meshgrid(k, k, indexing="ij")
        r = np.sqrt(xi * xi + Y * Y + Z * Z)
        sel = (r > model.Rin) & (r < model.Rout)
        if not np.any(sel):
            continue
        rho = model.density(r[sel])
        keep = rho > 0
        xs.append(np.stack([np.full(np.count_nonzero(keep), xi), Y[sel][keep], Z[sel][keep]], 1))
        ms.append(rho[keep] * a.dx ** 3)
    x, m = np.concatenate(xs), np.concatenate(ms)
    pn = os.path.join(a.out, "es_box.nrp")
    em.write_nrp(pn, x, np.zeros_like(x), m)
    nb = 32 if n % 32 == 0 else (16 if n % 16 == 0 else n)
    with open(os.path.join(a.out, "es_t0.athinput"), "w") as fo:
        fo.write(INPUT.format(n=n, lo=-a.half, hi=a.half, nb=nb, nrp=pn, tab=os.path.abspath(a.tab),
                              m_p=m_p))
    print(f"n = {n}, dx = {a.dx}, particles {len(m)}, dust mass in the box {m.sum():.6f}")


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        time = np.frombuffer(f.read(8), "<f8")[0]
        n = np.frombuffer(f.read(24), "<i8")
        nc = int(n[0] * n[1] * n[2])
        shape = (int(n[2]), int(n[1]), int(n[0]))
        out = dict(time=float(time), n=tuple(int(v) for v in n), magic=magic)
        out["E"] = np.frombuffer(f.read(4 * nc), "<f4").reshape(shape).astype(float)
        out["chi"] = np.frombuffer(f.read(4 * nc), "<f4").reshape(shape).astype(float)
        for name in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
            out[name] = np.frombuffer(f.read(8 * nc), "<f8").reshape(shape)
    return out


def analyse(a):
    model = em.EinsteinStrausBH()
    res = {}
    for rd in a.runs:
        inp = open(os.path.join(rd, "es_t0.athinput")).read() if os.path.exists(
            os.path.join(rd, "es_t0.athinput")) else None
        fld = read_field(os.path.join(rd, "es.field.00000.bin"))
        n = fld["n"][0]
        half = a.half
        dx = 2 * half / n
        xc = -half + (np.arange(n) + 0.5) * dx
        Z, Y, X = np.meshgrid(xc, xc, xc, indexing="ij")
        r = np.sqrt(X * X + Y * Y + Z * Z)
        inner = (np.abs(X) < half - 4 * dx) & (np.abs(Y) < half - 4 * dx) & (np.abs(Z) < half - 4 * dx)
        chi = fld["chi"]
        Mabs = np.sqrt(chi * (fld["Mx"] ** 2 + fld["My"] ** 2 + fld["Mz"] ** 2))
        rho = model.profiles(r.ravel())["rho"].reshape(r.shape)
        regs = {"puncture r < 3": r < 3.0, "transition 4 < r < 30": (r > 4) & (r < 30),
                "inner dust edge 34 < r < 46": (r > 34) & (r < 46),
                "plateau r > 46": (r > 46)}
        rec = {"dx": dx, "n": n, "run": rd}
        for name, sel in regs.items():
            s = sel & inner
            if not np.any(s):
                continue
            rec[name] = dict(cells=int(s.sum()), H_max=float(np.max(np.abs(fld["H"][s]))),
                             H_rms=float(np.sqrt(np.mean(fld["H"][s] ** 2))),
                             M_max=float(np.max(Mabs[s])), M_rms=float(np.sqrt(np.mean(Mabs[s] ** 2))),
                             E_minus_rho_max=float(np.max(np.abs(fld["E"][s] - rho[s]))),
                             rho_max=float(np.max(rho[s])) if np.any(rho[s] > 0) else 0.0,
                             Khat_max=float(np.max(np.abs(fld["Khat"][s]))))
        res[f"dx={dx:g}"] = rec
        # radial profiles along the diagonal-ish ray for the figure
        rec["_profile"] = (r[inner].ravel(), np.abs(fld["H"][inner]).ravel(), Mabs[inner].ravel())
    names = sorted(res, key=lambda k: -res[k]["dx"])
    if len(names) >= 2:
        for reg in ("transition 4 < r < 30", "inner dust edge 34 < r < 46", "plateau r > 46", "puncture r < 3"):
            for key in ("H_max", "H_rms", "M_max", "M_rms"):
                v = [res[nm][reg][key] for nm in names if reg in res[nm]]
                d = [res[nm]["dx"] for nm in names if reg in res[nm]]
                if len(v) >= 2:
                    res.setdefault("orders", {}).setdefault(reg, {})[key] = [
                        math.log(v[i] / v[i + 1]) / math.log(d[i] / d[i + 1]) if v[i + 1] > 0 else float("inf")
                        for i in range(len(v) - 1)]
    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.09, top=0.97, hspace=0.06)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"]]
    for nm, c in zip(names, cols):
        rr, Hh, Mm = res[nm]["_profile"]
        o = np.argsort(rr)
        rr, Hh, Mm = rr[o], Hh[o], Mm[o]
        bins = np.linspace(0, rr.max(), 200)
        idx = np.digitize(rr, bins)
        hb = np.array([Hh[idx == i].max() if np.any(idx == i) else np.nan for i in range(1, len(bins))])
        mb = np.array([Mm[idx == i].max() if np.any(idx == i) else np.nan for i in range(1, len(bins))])
        rc = 0.5 * (bins[1:] + bins[:-1])
        axs[0].semilogy(rc, hb, color=c, label=fr"$\Delta x = {res[nm]['dx']:g}\,M$")
        axs[1].semilogy(rc, mb, color=c)
    for ax in axs:
        for x in (model.rbar0, model.Rin, model.Rw, model.Rw + model.w_in):
            ax.axvline(x, **fs.MASK_LINE)
    axs[0].set_ylabel(r"max $|\mathcal{H}|$ in shells (code)")
    axs[1].set_ylabel(r"max $|\mathcal{M}|$ in shells (code)")
    axs[1].set_xlabel(r"coordinate radius $r/M$")
    axs[0].legend(loc="upper right")
    fs.save(fig, os.path.join(FIGS, "code_t0"))
    for nm in names:
        res[nm].pop("_profile")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "code_t0.json"), "w") as fo:
        json.dump(res, fo, indent=1)
    print(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep")
    p.add_argument("--tab", required=True)
    p.add_argument("--dx", type=float, required=True)
    p.add_argument("--half", type=float, default=48.0)
    p.add_argument("--out", required=True)
    q = sub.add_parser("analyse")
    q.add_argument("--runs", nargs="+", required=True)
    q.add_argument("--half", type=float, default=48.0)
    q.add_argument("--out", required=True)
    a = ap.parse_args()
    prep(a) if a.cmd == "prep" else analyse(a)


if __name__ == "__main__":
    main()
