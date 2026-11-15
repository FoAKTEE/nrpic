#!/usr/bin/env python3
"""T3: thin periodic boxes, the lattice jitter and the sources in double precision
(predictions P3a-P3d, P4a-P4d, P2e of tracks/core/JOURNAL-bfix.md).

Initial data: problems/cosmo/make_waves.py (solver python/nrpic/torus_id.py), compared
with cosmo/ic/make_east.py for the cube. Runs: crossed waves (1, 0.5, 0), delta = 0.1,
16 cells per wavelength, two particles per cell and direction, production configuration
of cosmo/README.md, from a = 1 to conformal time 5.5 (past the first shell crossing):
  cube   16 x 16 x 16            thin8  16 x 16 x 8          thin4  16 x 16 x 4
  thinx  4 x 16 x 16 with the waves (0, 1, 0.5): the thin4 run with the axes exchanged
  plane4 16 x 16 x 4, plane wave (1, 0, 0)      jit4   the same with the lattice displaced
                                                       by 0.3 cells in y and z (seed 7)

    python3 t3_thin_jitter.py --exe EXE [--out DIR] [--stages ic,run,ana]
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import fs, athena_bin  # noqa: E402

sys.path.insert(0, os.path.join(bc.REPO, "problems", "cosmo"))
import make_waves as mw  # noqa: E402
from nrpic import torus_id as tid  # noqa: E402
from nrpic.io import write_nrp  # noqa: E402

DELTA = 0.1
PPC = 2
H = 0.25                      # cell size: 16 cells on the wavelength 4
TLIM = 5.5
DEP = dict(shape="pcs", dep_comp_c=0.16666666666666666, dep_comp_c2=0.4666666666666667)
CASES = {
    "cube": dict(n=(16, 16, 16), ratios=(1.0, 0.5, 0.0)),
    "thin8": dict(n=(16, 16, 8), ratios=(1.0, 0.5, 0.0)),
    "thin4": dict(n=(16, 16, 4), ratios=(1.0, 0.5, 0.0)),
    "thinx": dict(n=(4, 16, 16), ratios=(0.0, 1.0, 0.5)),
    "plane4": dict(n=(16, 16, 4), ratios=(1.0, 0.0, 0.0)),
    "jit4": dict(n=(16, 16, 4), ratios=(1.0, 0.0, 0.0), jitter=0.3, jitter_axes=(1, 2),
                 seed=7),
}
IC_ONLY = {
    "jit4_again": dict(n=(16, 16, 4), ratios=(1.0, 0.0, 0.0), jitter=0.3,
                       jitter_axes=(1, 2), seed=7),
    "jit4_seed8": dict(n=(16, 16, 4), ratios=(1.0, 0.0, 0.0), jitter=0.3,
                       jitter_axes=(1, 2), seed=8),
    "jit4_zero": dict(n=(16, 16, 4), ratios=(1.0, 0.0, 0.0), jitter=0.0,
                      jitter_axes=(1, 2), seed=7),
    "jitcube": dict(n=(16, 16, 16), ratios=(1.0, 0.0, 0.0), jitter=0.3,
                    jitter_axes=(1, 2), seed=7),
}
EXTRA = """
<output2>
file_type        = bin
variable         = z4c
double_precision = true
dt               = 0.5

<output3>
file_type        = bin
variable         = tmunu
double_precision = true
dt               = 0.5

<output4>
file_type   = bin
variable    = tmunu
id          = tmunu_single
dt          = 0.5

<output5>
file_type   = bin
variable    = con
dt          = 0.5
"""


def make_ic(out, name, spec):
    d = os.path.join(out, "ic", name)
    if os.path.exists(os.path.join(d, "id.json")):
        return d
    os.makedirs(d, exist_ok=True)
    n = spec["n"]
    x, u, m, r, K, alpha, info, fid = mw.build(
        DELTA, n, PPC, L=n[0]*H, ratios=spec["ratios"], dep=tid.Deposit(**DEP),
        jitter=spec.get("jitter", 0.0), jitter_axes=spec.get("jitter_axes", ()),
        seed=spec.get("seed", 1), verbose=False)
    write_nrp(os.path.join(d, "particles.nrp"), x, u, m)
    mw.write_fields(os.path.join(d, "fields.bin"), r["psi"], K, alpha, r["A"])
    np.savez(os.path.join(d, "fiducial.npz"), **fid)
    with open(os.path.join(d, "id.json"), "w") as f:
        json.dump(info, f, indent=1)
    return d


def read_nrp(path):
    b = open(path, "rb").read()
    n = int(np.frombuffer(b, "<i8", 1, 8)[0])
    return np.frombuffer(b, "<f8", 7*n, 16).reshape(n, 7)


def read_fields(path):
    b = open(path, "rb").read()
    n = tuple(int(v) for v in np.frombuffer(b, "<i8", 3, 8))
    # each array is stored with the first index fastest
    a = np.frombuffer(b, "<f8", 9*n[0]*n[1]*n[2], 32).reshape(9, n[2], n[1], n[0])
    return a.transpose(0, 3, 2, 1)             # [field, i, j, k]


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        t = np.fromfile(f, "<f8", 1)[0]
        n = int(np.fromfile(f, "<i8", 1)[0])
        np.fromfile(f, "<i8", 1)
        d = np.fromfile(f, "<f8", 7*n).reshape(n, 7)
        tag = np.fromfile(f, "<i4", n)
    return float(t), d, tag


# ---------------------------------------------------------------- stage ic

def stage_ic(res, out):
    r = {}
    dirs = {name: make_ic(out, name, spec) for name, spec in {**CASES, **IC_ONLY}.items()}
    # P3a: the cube against cosmo/ic/make_east.py (same arguments)
    east = os.path.join(out, "ic", "east_cube")
    if not os.path.exists(os.path.join(east, "id.json")):
        cmd = [sys.executable, "make_east.py", "--delta", str(DELTA), "--n", "16", "--ppc",
               str(PPC), "--ratios", "1,0.5,0", "--shape", "pcs", "--dep-comp-c",
               repr(DEP["dep_comp_c"]), "--dep-comp-c2", repr(DEP["dep_comp_c2"]),
               "--out", east]
        with open(os.path.join(out, "ic", "east_cube.log"), "w") as log:
            subprocess.run(cmd, cwd=os.path.join(bc.REPO, "cosmo", "ic"), stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    pa, pb = read_nrp(os.path.join(east, "particles.nrp")), \
        read_nrp(os.path.join(dirs["cube"], "particles.nrp"))
    fa, fb = read_fields(os.path.join(east, "fields.bin")), \
        read_fields(os.path.join(dirs["cube"], "fields.bin"))
    r["cube_vs_make_east"] = {
        "n_particles": [len(pa), len(pb)],
        "max_abs_dx": float(np.abs(pa[:, :3] - pb[:, :3]).max()),
        "max_abs_du": float(np.abs(pa[:, 3:6] - pb[:, 3:6]).max()),
        "max_rel_dm": float(np.abs(pa[:, 6]/pb[:, 6] - 1).max()),
        "max_abs_dfield": [float(v) for v in np.abs(fa - fb).reshape(9, -1).max(axis=1)],
        "field_scale": [float(v) for v in np.abs(fa).reshape(9, -1).max(axis=1)]}
    # P3b: thin data against the layers of the cube
    for name in ("thin8", "thin4"):
        ft = read_fields(os.path.join(dirs[name], "fields.bin"))
        n3 = ft.shape[3]
        dmax = np.zeros(9)
        for k in range(16):
            dmax = np.maximum(dmax, np.abs(fb[:, :, :, k] - ft[:, :, :, k % n3])
                              .reshape(9, -1).max(axis=1))
        st = np.load(os.path.join(dirs[name], "fiducial.npz"))["site"]
        sc = np.load(os.path.join(dirs["cube"], "fiducial.npz"))["site"]
        pt = read_nrp(os.path.join(dirs[name], "particles.nrp"))
        key = {tuple(s): i for i, s in enumerate(sc)}
        idx = np.array([key[tuple(s)] for s in st])
        r[f"{name}_vs_cube_layers"] = {
            "max_abs_dfield": [float(v) for v in dmax],
            "max_abs_dx": float(np.abs(pt[:, :3] - pb[idx, :3]).max()),
            "max_abs_du": float(np.abs(pt[:, 3:6] - pb[idx, 3:6]).max()),
            "max_rel_dm": float(np.abs(pt[:, 6]/pb[idx, 6] - 1).max()),
            "n_particles": int(len(pt))}
    # P4: jitter
    p0 = read_nrp(os.path.join(dirs["plane4"], "particles.nrp"))
    pj = read_nrp(os.path.join(dirs["jit4"], "particles.nrp"))
    box = np.array(json.load(open(os.path.join(dirs["jit4"], "id.json")))["box"])
    dxyz = pj[:, :3] - p0[:, :3]
    dxyz = (dxyz + 0.5*box) % box - 0.5*box          # periodic difference
    n = len(pj)

    def same(a, b):
        return all(open(os.path.join(dirs[a], f), "rb").read()
                   == open(os.path.join(dirs[b], f), "rb").read()
                   for f in ("particles.nrp", "fields.bin"))

    ij = json.load(open(os.path.join(dirs["jit4"], "id.json")))
    i0 = json.load(open(os.path.join(dirs["plane4"], "id.json")))
    sj = np.load(os.path.join(dirs["jit4"], "fiducial.npz"))["site"]
    sc = np.load(os.path.join(dirs["jitcube"], "fiducial.npz"))["site"]
    pc = read_nrp(os.path.join(dirs["jitcube"], "particles.nrp"))
    key = {tuple(s): i for i, s in enumerate(sc)}
    idx = np.array([key[tuple(s)] for s in sj])
    dcube = pj[:, 1:3] - pc[idx, 1:3]
    r["jitter"] = {
        "n": n, "x_values_changed": int(np.count_nonzero(dxyz[:, 0] != 0.0)),
        "x_max_abs_change": float(np.abs(dxyz[:, 0]).max()),
        "y_over_h": {"min": float(dxyz[:, 1].min()/H), "max": float(dxyz[:, 1].max()/H),
                     "mean": float(dxyz[:, 1].mean()/H), "rms": float(dxyz[:, 1].std()/H)},
        "z_over_h": {"min": float(dxyz[:, 2].min()/H), "max": float(dxyz[:, 2].max()/H),
                     "mean": float(dxyz[:, 2].mean()/H), "rms": float(dxyz[:, 2].std()/H)},
        "expected_rms": 0.3/np.sqrt(3.0), "standard_error_of_mean": 0.3/np.sqrt(3.0*n),
        "corr_y_z": float(np.corrcoef(dxyz[:, 1], dxyz[:, 2])[0, 1]),
        "same_seed_identical_files": same("jit4", "jit4_again"),
        "other_seed_identical_files": same("jit4", "jit4_seed8"),
        "jitter_zero_identical_to_no_option": same("jit4_zero", "plane4"),
        "id_json": {k: ij[k] for k in ("jitter", "jitter_axes", "seed", "jitter_substream",
                                       "max_jitter_over_h")},
        "ham_residual_over_term": [ij["max_hamiltonian_residual"]/ij["max_hamiltonian_term"],
                                   i0["max_hamiltonian_residual"]/i0["max_hamiltonian_term"]],
        "mom_residual": [ij["max_momentum_residual"], i0["max_momentum_residual"]],
        "thin_vs_cube_same_sites_max_abs_dyz": float(np.abs(dcube).max()),
        "hist_y": np.histogram(dxyz[:, 1]/H, bins=30, range=(-0.3, 0.3))[0].tolist(),
        "hist_z": np.histogram(dxyz[:, 2]/H, bins=30, range=(-0.3, 0.3))[0].tolist()}
    r["id_json"] = {name: {k: v for k, v in json.load(open(os.path.join(d, "id.json"))).items()
                           if k in ("n", "box", "N", "n_fiducial", "max_hamiltonian_residual",
                                    "max_hamiltonian_term", "max_momentum_residual",
                                    "max_abs_Ahat", "mass_min_over_mean",
                                    "mass_max_over_mean")}
                    for name, d in dirs.items()}
    res["ic"] = r
    res["ic_dirs"] = dirs
    print("ic cube vs make_east:", r["cube_vs_make_east"])
    print("ic thin vs cube:", r["thin8_vs_cube_layers"], r["thin4_vs_cube_layers"])
    print("ic jitter:", {k: v for k, v in r["jitter"].items() if not k.startswith("hist")})


# ---------------------------------------------------------------- stage run

def stage_run(res, exe, out, nproc):
    with open(os.path.join(bc.REPO, "problems", "cosmo", "east.athinput")) as f:
        txt = f.read()
    inp = os.path.join(out, "waves.athinput")
    with open(inp, "w") as f:
        f.write(txt + EXTRA)
    jobs = {}
    for name, spec in CASES.items():
        d = res["ic_dirs"][name]
        info = json.load(open(os.path.join(d, "id.json")))
        n, box = info["n"], info["box"]
        rd = os.path.join(out, "run", name)
        os.makedirs(rd, exist_ok=True)
        for fn in ("particles.nrp", "fields.bin"):
            if not os.path.exists(os.path.join(rd, fn)):
                os.symlink(os.path.join(d, fn), os.path.join(rd, fn))
        ov = [f"mesh/nx{a+1}={n[a]}" for a in range(3)] \
            + [f"mesh/x{a+1}max={box[a]!r}" for a in range(3)] \
            + [f"meshblock/nx{a+1}={min(8, n[a])}" for a in range(3)] \
            + [f"time/tlim={TLIM}", "z4c/damp_kappa1=0.5", "z4c/damp_kappa1_over_alpha=true",
               "particles/deposit_shape=pcs", f"particles/deposit_comp_c={DEP['dep_comp_c']!r}",
               f"particles/deposit_comp_c2={DEP['dep_comp_c2']!r}", "particles/interp=bspline",
               "particles/dt_expansion=0.01", "particles/nfilter=0",
               "particles/filter_compensate=false", "particles/snap_dt=0.5",
               f"particles/traj_ntrack={info['n_fiducial']}", "particles/cons_dcycle=8"] \
            + [f"particles/probe_x{a+1}={info['overdensity_point'][a]!r}" for a in range(3)] \
            + [f"particles/probe1_x{a+1}={info['underdensity_point'][a]!r}" for a in range(3)]
        jobs[name] = (exe, inp, rd, ov)
    recs = bc.run_many(jobs, nproc)
    r = {}
    for name, rec in recs.items():
        with open(os.path.join(rec["rundir"], "athena.log")) as f:
            log = f.read()
        zc = [ln for ln in log.splitlines() if "zone-cycles/cpu_second" in ln]
        cyc = [ln for ln in log.splitlines() if "MeshBlock-cycles" in ln]
        cpu = [ln for ln in log.splitlines() if "cpu time used" in ln]
        r[name] = {"rundir": rec["rundir"], "wall_s": rec["wall_s"],
                   "zone_cycles_per_cpu_second": float(zc[-1].split("=")[1]) if zc else None,
                   "meshblock_cycles": float(cyc[-1].split("=")[1]) if cyc else None,
                   "cpu_s": float(cpu[-1].split("=")[1]) if cpu else None,
                   "terminated": [ln for ln in log.splitlines() if "Terminating" in ln][-1:]}
    res["run"] = r
    print("run:", {n: (v["wall_s"], v["zone_cycles_per_cpu_second"], v["terminated"])
                   for n, v in r.items()})


# ---------------------------------------------------------------- stage ana

SCAL = ["z4c_chi", "z4c_alpha", "z4c_Khat", "z4c_Theta", "z4c_Axx", "z4c_Axy", "z4c_gxx",
        "z4c_gxy"]


def dumps(rd, var):
    return sorted(glob.glob(os.path.join(rd, "bin", f"east.{var}.0*.bin")))


def rel(a, b):
    s = max(np.abs(a).max(), np.abs(b).max(), 1e-300)
    return float(np.abs(a - b).max()/s)


def zdep(a, axis=0):
    """Largest departure of any layer along the thin axis from the first one, relative
    to the largest value."""
    a0 = np.take(a, [0], axis=axis)
    return float(np.abs(a - a0).max()/max(np.abs(a).max(), 1e-300))


def hamiltonian_from_dumps(B, zd, td):
    """H = R + K^2 - K_ij K^ij - 16 pi E from one double-precision z4c dump and one
    tmunu dump (sixth-order differences, as the code with nghost = 4)."""
    d = bc.z4c_from_bin(zd)
    g = B["grid"].Grid((len(d["x"]), len(d["y"]), len(d["z"])),
                       tuple(d["xmax"] - d["xmin"]), tuple(d["xmin"]))
    gamma, K, _, _ = B["readers"].z4c_to_adm(d)
    al = B["weyl"].electric_magnetic(gamma, K, g, order=6, return_all=True)
    geo = al["trE_vacuum"]
    E = np.asarray(td["tmunu_E"], dtype=np.float64)
    return geo - 16.0*np.pi*E, geo, E


def stage_ana(res, B, out):
    run = res["run"]
    r = {}
    # ---- thin against cube, every dump
    ref = [athena_bin.read_bin(p) for p in dumps(run["cube"]["rundir"], "z4c")]
    r["times"] = [d["time"] for d in ref]
    r["a_end"] = float(1.0/np.sqrt(ref[-1]["z4c_chi"].mean()))
    for name in ("thin8", "thin4"):
        dd = [athena_bin.read_bin(p) for p in dumps(run[name]["rundir"], "z4c")]
        rows = []
        for c, t in zip(ref, dd):
            n3 = t["z4c_chi"].shape[0]
            row = {"t_cube": c["time"], "t_thin": t["time"], "cycle": [c["cycle"], t["cycle"]]}
            for v in SCAL:
                tile = np.concatenate([t[v]]*(16//n3), axis=0)
                row[v] = rel(c[v], tile)
            row["zdep_thin"] = max(zdep(t[v]) for v in SCAL)
            row["zdep_cube"] = max(zdep(c[v]) for v in SCAL)
            rows.append(row)
        r[f"{name}_vs_cube"] = rows
    # thin in x against thin4 with the axes exchanged: (x, y, z) of thin4 -> (y, z, x)
    tx = [athena_bin.read_bin(p) for p in dumps(run["thinx"]["rundir"], "z4c")]
    t4 = [athena_bin.read_bin(p) for p in dumps(run["thin4"]["rundir"], "z4c")]
    rows = []
    for a, b in zip(t4, tx):
        row = {"t": [a["time"], b["time"]]}
        for v in ("z4c_chi", "z4c_alpha", "z4c_Khat", "z4c_Theta"):
            row[v] = rel(a[v].transpose(1, 2, 0), b[v])
        row["Axx_to_Ayy"] = rel(a["z4c_Axx"].transpose(1, 2, 0), b["z4c_Ayy"])
        row["Axy_to_Ayz"] = rel(a["z4c_Axy"].transpose(1, 2, 0), b["z4c_Ayz"])
        row["zdep_thinx"] = max(zdep(b[v], axis=2) for v in ("z4c_chi", "z4c_alpha", "z4c_Khat"))
        rows.append(row)
    r["thinx_vs_thin4_exchanged"] = rows
    # ---- particles at the last snapshot, matched by lattice site
    def snaps(name):
        return sorted(glob.glob(os.path.join(run[name]["rundir"], "east.part.*.bin")))

    sc = np.load(os.path.join(res["ic_dirs"]["cube"], "fiducial.npz"))["site"]
    tc, dc, tagc = read_snapshot(snaps("cube")[-1])
    oc = np.empty_like(tagc)
    oc[tagc] = np.arange(len(tagc))
    key = {tuple(s): i for i, s in enumerate(sc)}
    part = {}
    for name in ("thin8", "thin4"):
        st = np.load(os.path.join(res["ic_dirs"][name], "fiducial.npz"))["site"]
        tt, dt_, tagt = read_snapshot(snaps(name)[-1])
        ot = np.empty_like(tagt)
        ot[tagt] = np.arange(len(tagt))
        idx = np.array([key[tuple(s)] for s in st])
        a, b = dt_[ot], dc[oc][idx]
        part[name] = {"t": [tc, tt], "n": int(len(tagt)), "n_snapshots": len(snaps(name)),
                      "max_abs_dxy_over_h": float(np.abs(a[:, :2] - b[:, :2]).max()/H),
                      "max_abs_dz": float(np.abs(a[:, 2] - b[:, 2]).max()),
                      "max_abs_du_over_umax": float(np.abs(a[:, 3:6] - b[:, 3:6]).max()
                                                    / np.abs(b[:, 3:6]).max()),
                      "max_abs_uz": float(np.abs(a[:, 5]).max())}
    r["particles_vs_cube"] = part
    r["particles_kept"] = {name: [read_snapshot(snaps(name)[-1])[1].shape[0],
                                  json.load(open(os.path.join(res["ic_dirs"][name],
                                                              "id.json")))["N"]]
                           for name in CASES}
    # shell crossing: sign changes of the x-separation of lattice neighbours along x
    st4 = np.load(os.path.join(res["ic_dirs"]["thin4"], "fiducial.npz"))["site"]
    _, d4, tag4 = read_snapshot(snaps("thin4")[-1])
    o4 = np.empty_like(tag4)
    o4[tag4] = np.arange(len(tag4))
    x4 = d4[o4][:, 0]
    lat = np.full((32, 32, 8), np.nan)
    lat[st4[:, 0], st4[:, 1], st4[:, 2]] = x4
    dxl = (np.roll(lat, -1, axis=0) - lat + 2.0) % 4.0 - 2.0
    r["shell_crossing"] = {"fraction_of_x_neighbours_that_crossed": float((dxl < 0).mean())}
    # ---- P2e: sources in double precision and the constraint from the dumps
    src = []
    for name in ("cube", "thin4"):
        zf, tf = dumps(run[name]["rundir"], "z4c"), dumps(run[name]["rundir"], "tmunu")
        sf, cf_ = dumps(run[name]["rundir"], "tmunu_single"), dumps(run[name]["rundir"], "con")
        for i in sorted(set((1, len(zf)//2, len(zf) - 1))):
            zd, td = athena_bin.read_bin(zf[i]), athena_bin.read_bin(tf[i])
            sd, cd = athena_bin.read_bin(sf[i]), athena_bin.read_bin(cf_[i])
            Hpy, geo, E = hamiltonian_from_dumps(B, zd, td)
            Hc = np.asarray(cd["con_H"], dtype=np.float64)
            src.append({
                "case": name, "t": [zd["time"], td["time"], cd["time"]],
                "var_size": [td["var_size"], sd["var_size"]],
                "E_min": float(E.min()), "E_max": float(E.max()),
                "all_finite": bool(all(np.isfinite(td[v]).all() for v in td["variables"])),
                "single_differs_from_rounded_double": int(sum(
                    np.count_nonzero(sd[v] != td[v].astype(np.float32))
                    for v in td["variables"])),
                "H_python_minus_code_over_term": float(np.abs(Hpy - Hc).max()
                                                       / np.abs(16*np.pi*E).max()),
                "H_code_max_over_term": float(np.abs(Hc).max()/np.abs(16*np.pi*E).max()),
                "H_python_max_over_term": float(np.abs(Hpy).max()/np.abs(16*np.pi*E).max()),
                "H_with_density_instead_over_term": float(np.abs(
                    geo - 16*np.pi*E*np.asarray(zd["z4c_chi"])**1.5 - Hc).max()
                    / np.abs(16*np.pi*E).max())})
    r["sources"] = src
    # ---- jittered against plain plane wave: constraint norms of the history
    con = {}
    for name in ("plane4", "jit4", "thin4", "cube"):
        hs = glob.glob(os.path.join(run[name]["rundir"], "*.z4c.user.hst")) \
            or glob.glob(os.path.join(run[name]["rundir"], "*.hst"))
        names, h = bc.read_hst([p for p in hs if "z4c" in p][0])
        ok = h[:, 10] > 0
        vol = h[ok, 10]
        con[name] = {"t": h[ok, 0].tolist(), "H_rms": np.sqrt(h[ok, 3]/vol).tolist(),
                     "M_rms": np.sqrt(h[ok, 4]/vol).tolist()}
    r["constraints_history"] = con
    r["jitter_run"] = {
        "H_rms_first": [con["jit4"]["H_rms"][0], con["plane4"]["H_rms"][0]],
        "H_rms_last": [con["jit4"]["H_rms"][-1], con["plane4"]["H_rms"][-1]],
        "M_rms_first": [con["jit4"]["M_rms"][0], con["plane4"]["M_rms"][0]]}
    # y-z dependence that the jitter puts into the plane wave (z4c_chi at the end)
    j = athena_bin.read_bin(dumps(run["jit4"]["rundir"], "z4c")[-1])
    p = athena_bin.read_bin(dumps(run["plane4"]["rundir"], "z4c")[-1])
    def yzdep(a):
        return float(np.abs(a - a.mean(axis=(0, 1), keepdims=True)).max()/np.abs(a).max())
    r["jitter_run"]["yz_dependence_chi_end"] = [yzdep(j["z4c_chi"]), yzdep(p["z4c_chi"])]
    r["jitter_run"]["chi_mean_end"] = [float(j["z4c_chi"].mean()), float(p["z4c_chi"].mean())]
    res["ana"] = r
    for name in ("thin8", "thin4"):
        last = r[f"{name}_vs_cube"][-1]
        print(f"ana {name} vs cube at the end:", {k: v for k, v in last.items()})
        print(f"ana {name} worst over dumps:", {v: max(q[v] for q in r[f'{name}_vs_cube'])
                                                for v in SCAL + ['zdep_thin', 'zdep_cube']})
    print("ana thinx vs thin4:", r["thinx_vs_thin4_exchanged"][-1])
    print("ana particles:", part, r["particles_kept"], r["shell_crossing"], "a_end", r["a_end"])
    for s in src:
        print("ana sources:", s)
    print("ana jitter run:", r["jitter_run"])
    return ref


def figures(res, out):
    fs.use_style()
    C = fs.PAL
    run, an = res["run"], res["ana"]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.9))
    # top: energy density of the cube (one layer) and of the thin box at the end
    tc = athena_bin.read_bin(dumps(run["cube"]["rundir"], "tmunu")[-1])
    t4 = athena_bin.read_bin(dumps(run["thin4"]["rundir"], "tmunu")[-1])
    vmax = max(tc["tmunu_E"].max(), t4["tmunu_E"].max())
    vmin = max(min(tc["tmunu_E"][tc["tmunu_E"] > 0].min(), t4["tmunu_E"][t4["tmunu_E"] > 0].min()),
               vmax*1e-3)
    norm = matplotlib.colors.LogNorm(vmin=vmin, vmax=vmax)
    ax = [fs.inch_axes(fig, 0.75 + 1.93*i, 3.35, 1.85, 1.85) for i in range(2)]
    for a, d, lab in ((ax[0], tc, "cube 16 x 16 x 16"), (ax[1], t4, "thin 16 x 16 x 4")):
        im = a.imshow(d["tmunu_E"][0], origin="lower", extent=[0, 4, 0, 4], cmap=fs.CMAP["dens"],
                      norm=norm, interpolation="nearest", rasterized=True, aspect="equal")
        a.set_title(lab, fontsize=9)
        a.set_xticks([1, 2, 3])
        a.set_yticks([1, 2, 3])
        a.set_xlabel("x", labelpad=-2)
    ax[0].set_ylabel("y")
    ax[1].set_yticklabels([])
    cax = fs.inch_axes(fig, 0.75 + 2*1.93 - 0.02, 3.35, 0.08, 1.85)
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r"$E$ (tmunu dump), t = %.2f" % tc["time"], fontsize=8)
    # top right: differences against the cube over time
    a3 = fs.inch_axes(fig, 5.45, 3.35, 2.3, 2.3)
    t = np.array(an["times"])
    for name, col in (("thin8", C["blue"]), ("thin4", C["red"])):
        rows = an[f"{name}_vs_cube"]
        a3.semilogy(t, [max(q[v] for v in SCAL) + 1e-18 for q in rows], "o-", ms=3, color=col,
                    label=f"{name} against cube")
        a3.semilogy(t, [q["zdep_thin"] + 1e-18 for q in rows], "s--", ms=3, mfc="none",
                    color=col, label=f"{name}: z dependence")
    a3.semilogy(t, [max(q["z4c_chi"], q["z4c_alpha"], q["z4c_Khat"]) + 1e-18
                    for q in an["thinx_vs_thin4_exchanged"]], "^:", ms=3, color=C["green"],
                label="thin in x against thin4, axes exchanged")
    a3.axhline(1e-8, **fs.THIN)
    a3.set_ylim(1e-17, 1e-5)
    a3.set_xlabel("conformal time")
    a3.set_ylabel("largest relative difference of the fields")
    a3.legend(loc="upper left", fontsize=6)
    # bottom left: jitter histogram
    b1 = fs.inch_axes(fig, 0.75, 0.55, 2.9, 2.2)
    jit = res["ic"]["jitter"]
    edges = np.linspace(-0.3, 0.3, 31)
    cen = 0.5*(edges[1:] + edges[:-1])
    b1.step(cen, jit["hist_y"], where="mid", color=C["red"], label="y displacement / h")
    b1.step(cen, jit["hist_z"], where="mid", color=C["yellow"], label="z displacement / h")
    b1.axhline(jit["n"]/30.0, **dict(fs.GUIDE, lw=1.0), label="uniform")
    b1.set_ylim(0, 1.6*jit["n"]/30.0)
    b1.set_xlabel("displacement of the lattice (cells), jitter 0.3, seed 7")
    b1.set_ylabel("particles per bin")
    b1.legend(loc="upper center", ncol=3, fontsize=6.5)
    # bottom right: constraint history, jittered against plain
    b2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.2)
    con = an["constraints_history"]
    for name, col, lab in (("plane4", C["blue"], "plane wave, thin 16 x 16 x 4"),
                           ("jit4", C["red"], "the same, lattice jittered in y and z"),
                           ("thin4", C["green"], "crossed waves, thin")):
        b2.semilogy(con[name]["t"], con[name]["H_rms"], color=col, label=lab)
        b2.semilogy(con[name]["t"], con[name]["M_rms"], color=col, ls="--")
    b2.set_xlabel("conformal time")
    b2.set_ylabel("rms of H (solid) and of M (dashed)")
    b2.legend(loc="upper right", fontsize=6.5)
    made = fs.save(fig, os.path.join(out, "t3_thin_jitter"))
    plt.close(fig)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--bdir", default=bc.B_DEFAULT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--stages", default="ic,run,ana")
    ap.add_argument("--nproc", type=int, default=6)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    B = bc.track_b(a.bdir)
    resfile = os.path.join(out, "results_t3.json")
    res = {}
    if os.path.exists(resfile):
        with open(resfile) as f:
            res = json.load(f)
    res["meta"] = {"exe": os.path.abspath(a.exe), "commit": bc.git_rev()}
    st = a.stages.split(",")
    if "ic" in st:
        stage_ic(res, out)
        bc.save_json(res, resfile)
    if "run" in st:
        stage_run(res, os.path.abspath(a.exe), out, a.nproc)
        bc.save_json(res, resfile)
    if "ana" in st:
        stage_ana(res, B, out)
        bc.save_json(res, resfile)
        print("figures:", figures(res, out))


if __name__ == "__main__":
    main()
