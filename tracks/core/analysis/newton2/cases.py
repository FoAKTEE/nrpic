#!/usr/bin/env python3
"""Test cases of work package newton2 (Newtonian mode, second pass): particle files,
input decks and AthenaK runs of the tests T1 to T8 and T10 of
tracks/core/JOURNAL-newton2.md. Nothing here integrates particles; AthenaK does.

    cases.py <test> [--out DIR] [--jobs N] [--exe ATHENA]

<test>: t1 (Fourier solver against multigrid and numpy), t2 (Track B's pancake), t3
(group history on the exact pancake, restart), t4a (deformed-ball generator), t4b
(embedded ellipsoid), t5 (point-mass infall of Track D), t6 (refined mesh), t7 (energy
against the step), t8 (self-force), t10 (regression against the branch start and the
release).  Output in --out (default $NRPIC_RUN_DIR, set by harness/bin/nrpic-run): one
directory per case with input.athinput, athena.log and the files of the run, and
cases.json (commands, wall times, exit codes).

Scripts of the tracks are used unchanged as generators and references: they are taken
from the tips of the track branches with git archive into <out>/refs/<track>/ (commit
ids in cases.json) and run from there.
"""
import argparse
import filecmp
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MAIN = "/data/haiyangw/nrpic"
EXE_NEW = os.path.join(ROOT, ".work", "build_cpu", "src", "athena")
EXE_BASE = os.path.join(MAIN, "scratch", "core", "exe", "core_requests-adf", "athena_cpu")
EXE_REL = os.path.join(MAIN, ".work", "build_cpu_v03", "src", "athena")
NEWTON = os.path.join(ROOT, "problems", "newton")
PY = sys.executable

sys.path.insert(0, os.path.join(ROOT, "python"))

ENV = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
           MPLBACKEND="Agg",
           PYTHONPATH=os.pathsep.join([os.path.join(ROOT, "python"),
                                       os.path.join(ROOT, "cosmo", "newton"),
                                       os.path.join(ROOT, "cosmo", "ic")]))

REFS = {
    "B-emd-gw": ["tracks/B-emd-gw/newton_tests/scripts", "tracks/B-emd-gw/newton_tests/inputs",
                 "tracks/B-emd-gw/verify_cosmo/scripts", "tracks/B-emd-gw/baseline/scripts"],
    "A-emd-pbh": ["tracks/A-emd-pbh/newton"],
    "D-bh-dress": ["tracks/D-bh-dress/secondary_infall"],
}


def sh(cmd, cwd=None, log=None):
    if log:
        with open(log, "w") as f:
            return subprocess.run(cmd, cwd=cwd, env=ENV, stdout=f,
                                  stderr=subprocess.STDOUT).returncode
    return subprocess.run(cmd, cwd=cwd, env=ENV, check=True)


def refs(out, track):
    """Scripts of a track from the tip of its branch; returns (directory, commit)."""
    d = os.path.join(out, "refs", track)
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "track/" + track],
                            capture_output=True, text=True, check=True).stdout.strip()
    if not os.path.isdir(d):
        os.makedirs(d)
        ar = subprocess.Popen(["git", "-C", ROOT, "archive", "track/" + track] + REFS[track],
                              stdout=subprocess.PIPE)
        subprocess.run(["tar", "-x", "-C", d], stdin=ar.stdout, check=True)
        ar.wait()
    return d, commit


def set_params(text, block, params):
    """Replace the values of parameters in <block> of an input deck, or append them."""
    lines = text.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "<%s>" % block)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("<")),
               len(lines))
    todo = dict(params)
    for i in range(start + 1, end):
        key = lines[i].split("=")[0].strip()
        if key in todo and "=" in lines[i] and not lines[i].lstrip().startswith("#"):
            lines[i] = "%s = %s" % (key, todo.pop(key))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    lines[end:end] = ["%s = %s" % (k, v) for k, v in todo.items()]
    return "\n".join(lines)


def deck(path, changes):
    text = open(path).read()
    for block, params in changes.items():
        text = set_params(text, block, params)
    return text


def cube(n, mb, lo=None, hi=None):
    m = {"nx1": n, "nx2": n, "nx3": n}
    if lo is not None:
        m.update({"x1min": lo, "x2min": lo, "x3min": lo, "x1max": hi, "x2max": hi,
                  "x3max": hi})
    return {"mesh": m, "meshblock": {"nx1": mb, "nx2": mb, "nx3": mb}}


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, {}).update(v)
    return out


class Case:
    def __init__(self, name, text=None, exe=None, args=(), restart=None, after=None):
        self.name, self.text, self.exe, self.args = name, text, exe, list(args)
        self.restart, self.after = restart, after


def run_case(out, c, exe):
    d = os.path.join(out, c.name)
    os.makedirs(d, exist_ok=True)
    e = c.exe or exe
    if c.restart:
        cmd = [e, "-r", c.restart, "-d", d] + c.args
    else:
        with open(os.path.join(d, "input.athinput"), "w") as f:
            f.write(c.text)
        cmd = [e, "-i", "input.athinput", "-d", d] + c.args
    t0 = time.time()
    rc = sh(cmd, cwd=d, log=os.path.join(d, "athena.log"))
    wall = time.time() - t0
    print("%-22s exit %d  %.1f s" % (c.name, rc, wall), flush=True)
    return dict(name=c.name, cmd=cmd, exit=rc, wall_s=wall)


def run_all(out, cases, exe, jobs, record):
    first = [c for c in cases if c.after is None]
    later = [c for c in cases if c.after is not None]
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(lambda c: run_case(out, c, exe), first))
        res += list(ex.map(lambda c: run_case(out, c, exe), later))
    record["cases"] = record.get("cases", []) + res
    return all(r["exit"] == 0 for r in res)


# ----------------------------------------------------------------------------- tests
def t1(out, exe, jobs, rec):
    import numpy as np
    from nrpic import io as nio
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    sh([PY, os.path.join(NEWTON, "make_ic.py"), "wave", "--out", os.path.join(ic, "wave32.nrp"),
        "--n", "32"])
    wave = {"particles": {"particle_file": os.path.join(ic, "wave32.nrp")}}
    per = os.path.join(NEWTON, "periodic.athinput")
    fft = os.path.join(NEWTON, "periodic_fft.athinput")
    nog = {"particles": {"newton_ngroup": 0}}
    cases = [
        Case("mg", deck(per, wave)),
        Case("fft7", deck(fft, merge(wave, nog, {"particles": {"newton_fft_symbol":
                                                               "seven_point"}}))),
        Case("fftsp", deck(fft, merge(wave, nog))),
    ]
    # T1c: 48 x 80 x 112 cells (factors 3, 5, 7), 2000 massive particles, one step
    rng = np.random.default_rng(11)
    n = 2000
    box = np.array([3.0, 5.0, 7.0])
    x = rng.uniform(0.0, 1.0, size=(n, 3))*box
    m = rng.uniform(0.5, 1.5, size=n)/n
    nio.write_nrp(os.path.join(ic, "random.nrp"), x, np.zeros((n, 3)), m)
    mixed = {"mesh": {"nx1": 48, "nx2": 80, "nx3": 112, "x1max": 3.0, "x2max": 5.0,
                      "x3max": 7.0},
             "meshblock": {"nx1": 16, "nx2": 16, "nx3": 16},
             "time": {"nlim": 1},
             "particles": {"particle_file": os.path.join(ic, "random.nrp"), "dt": 1e-6,
                           "snap_dt": 1e-6, "newton_expansion": "none", "newton_ngroup": 0,
                           "probe1_x1": 1.0, "probe1_x2": 1.0, "probe1_x3": 1.0}}
    cases += [
        Case("mixed_sp", deck(fft, mixed)),
        Case("mixed_7", deck(fft, merge(mixed, {"particles": {"newton_fft_symbol":
                                                              "seven_point"}}))),
    ]
    return run_all(out, cases, exe, jobs, rec)


def pancake_deck(bdir, n, extra, tlim):
    src = os.path.join(bdir, "tracks", "B-emd-gw", "newton_tests", "inputs", "pancake.athinput")
    ch = merge(cube(n, n//2), {"time": {"tlim": tlim},
                               "particles": {"dt": repr(1.0/(4*n)), "traj_ntrack": n}}, extra)
    return deck(src, ch)


def t2(out, exe, jobs, rec):
    bdir, commit = refs(out, "B-emd-gw")
    rec["refs"] = {"B-emd-gw": commit}
    gen = os.path.join(bdir, "tracks", "B-emd-gw", "newton_tests", "scripts", "make_particles.py")
    cases = []
    # n = 64 runs on a card (test "card"): two hours on one core
    for n, sym in ((16, "spectral"), (32, "spectral"), (32, "seven_point")):
        name = "east%d%s" % (n, "" if sym == "spectral" else "_7pt")
        d = os.path.join(out, name)
        sh([PY, gen, "pancake-east", "--n", str(n), "--delta", "0.05", "--L", "1", "--out", d])
        cases.append(Case(name, pancake_deck(bdir, n, {"particles": {
            "newton_poisson": "fft", "newton_fft_symbol": sym}}, 7.0)))
    cases.sort(key=lambda c: -int("".join(ch for ch in c.name[:6] if ch.isdigit())))
    return run_all(out, cases, exe, jobs, rec)


def t3(out, exe, jobs, rec):
    bdir, commit = refs(out, "B-emd-gw")
    rec["refs"] = {"B-emd-gw": commit}
    gen = os.path.join(bdir, "tracks", "B-emd-gw", "newton_tests", "scripts", "make_particles.py")
    n = 32
    grp = {"newton_ngroup": 2, "newton_group1_species": -1,
           "newton_group2_tag_min": (n//4)*n*n, "newton_group2_tag_max": (3*n//4)*n*n - 1,
           "hist_dcycle": 1, "traj_ntrack": 0, "traj_dcycle": 0}
    cases = []
    for name, sym in (("sin32_sp", "spectral"), ("sin32_7pt", "seven_point")):
        d = os.path.join(out, name)
        sh([PY, gen, "pancake-sin", "--n", str(n), "--delta", "0.05", "--L", "1", "--out", d])
        p = dict(grp, newton_poisson="fft", newton_fft_symbol=sym)
        text = pancake_deck(bdir, n, {"particles": p, "output1": {"dt": 2.34375}}, 3.5)
        text = set_params(text, "particles", {"traj_ntrack": 0})
        cases.append(Case(name, text))
    # continuation of the spectral run from its dump at cycle 300
    cases.append(Case("sin32_sp_cont", restart=os.path.join(out, "sin32_sp", "rst",
                                                            "newton.00001.rst"),
                      after="sin32_sp"))
    return run_all(out, cases, exe, jobs, rec)


def t4a(out, exe, jobs, rec):
    import numpy as np
    from nrpic import io as nio
    adir, commit = refs(out, "A-emd-pbh")
    rec["refs"] = {"A-emd-pbh": commit}
    gen_a = os.path.join(adir, "tracks", "A-emd-pbh", "newton", "make_deformed_ball.py")
    res = {}
    for label, rot in (("plain", None), ("rot3", 3)):
        fa = os.path.join(out, "a_%s.nrp" % label)
        cmd = [PY, gen_a, "--out", fa, "--dep", "0.2", "0.2", "0", "--hxi", "0.05"]
        if rot is not None:
            cmd += ["--rotate", str(rot)]
        sh(cmd)
        ja = json.load(open(os.path.join(out, "a_%s.json" % label)))
        lam = np.array(ja["abg"])
        a0, h0 = ja["a0"], ja["H0"]
        S = a0*(1.0 - a0*lam)
        D = h0*a0*(1.0 - 2.0*a0*lam)
        fb = os.path.join(out, "core_%s.nrp" % label)
        cmd = [PY, os.path.join(NEWTON, "make_ic.py"), "ball", "--out", fb, "--radius", "1",
               "--mass", "0.5", "--spacing", "0.05", "--ntracer", "0",
               "--axes"] + [repr(float(v)) for v in S] + ["--vgrad"] + [repr(float(v)) for v in D]
        if rot is not None:
            cmd += ["--rotate", str(rot)]
        sh(cmd)
        jb = json.load(open(os.path.join(out, "core_%s.json" % label)))
        xa, ua, ma, _ = nio.read_nrp(fa)
        xb, ub, mb, _ = nio.read_nrp(fb)
        scale_x = np.abs(xa).max()
        scale_u = np.abs(ua).max()
        res[label] = dict(n_a=len(ma), n_b=len(mb),
                          dx=float(np.abs(xa - xb).max()/scale_x) if len(ma) == len(mb) else None,
                          du=float(np.abs(ua - ub).max()/scale_u) if len(ma) == len(mb) else None,
                          dm=float(np.abs(ma - mb).max()/ma.max()) if len(ma) == len(mb) else None,
                          r_vol_a=ja["r_vol"], r_vol_b=jb["r_vol"], r_mom_a=ja["r_mom"],
                          r_mom_b=jb["r_mom"])
        print(label, res[label], flush=True)
    rec["t4a"] = res
    with open(os.path.join(out, "t4a.json"), "w") as f:
        json.dump(res, f, indent=1)
    return all(r["dx"] is not None and max(r["dx"], r["du"], r["dm"]) < 1e-10
               for r in res.values())


def t4b(out, exe, jobs, rec, which="fft"):
    import numpy as np
    bdir, commit = refs(out, "B-emd-gw")
    rec["refs"] = {"B-emd-gw": commit}
    sys.path.insert(0, os.path.join(bdir, "tracks", "B-emd-gw", "baseline", "scripts"))
    import ellipsoid as el
    lam = np.array([0.11122237, 0.06683367, 0.02194397])      # benchmark of 2605.04487
    t0, R0, V0 = el.initial_state(lam)
    H = 2.0/(3.0*t0)
    S = R0/el.RL
    D = (V0/R0 - H)*S
    L, n = 48.0, 64
    rho_b = float(el.rho_b(t0))
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    pf = os.path.join(ic, "embedded.nrp")
    sh([PY, os.path.join(NEWTON, "make_ic.py"), "ball", "--out", pf, "--center",
        repr(L/2), repr(L/2), repr(L/2), "--radius", repr(el.RL), "--mass", repr(el.MASS),
        "--spacing", "0.125", "--ntracer", "0", "--axes"] + [repr(float(v)) for v in S]
       + ["--vgrad"] + [repr(float(v)) for v in D]
       + ["--background", "0.0", repr(L), str(n), repr(rho_b)])
    meta = dict(lam=lam.tolist(), t_turn=float(t0), R0=R0.tolist(), V0=V0.tolist(), H=H,
                S=S.tolist(), D=D.tolist(), L=L, n=n, rho_b=rho_b, mass=el.MASS, RL=el.RL)
    with open(os.path.join(ic, "embedded_setup.json"), "w") as f:
        json.dump(meta, f, indent=1)
    base = merge(cube(n, 32, 0.0, L), {"time": {"tlim": 11.2}, "particles": {
        "particle_file": pf, "dt": 0.04, "newton_hubble": repr(H), "hist_dcycle": 1,
        "snap_dt": 1.4, "newton_ngroup": 1, "newton_group1_species": 0,
        "newton_group1_x1": L/2, "newton_group1_x2": L/2, "newton_group1_x3": L/2,
        "probe_x1": L/2, "probe_x2": L/2, "probe_x3": L/2,
        "probe1_x1": 1.0, "probe1_x2": 1.0, "probe1_x3": 1.0}})
    src = os.path.join(NEWTON, "embedded_ellipsoid.athinput")
    if which == "fft":
        cases = [Case("emb_fft", deck(src, base))]
    else:
        cases = [Case("emb_mg", deck(src, merge(base, {"particles": {"newton_poisson":
                                                                      "multigrid"}})))]
    return run_all(out, cases, exe, jobs, rec)


def t4c(out, exe, jobs, rec):
    """The embedded ellipsoid of t4b with the multigrid solver."""
    return t4b(out, exe, jobs, rec, which="mg")


def t5(out, exe, jobs, rec):
    from nrpic import io as nio
    ddir, commit = refs(out, "D-bh-dress")
    rec["refs"] = {"D-bh-dress": commit}
    sdir = os.path.join(ddir, "tracks", "D-bh-dress", "secondary_infall")
    nx, half = 64, 68.0
    dx = 2.0*half/nx
    cases = []
    for name, shift in (("pm_vertex", 0.0), ("pm_centre", 0.5*dx)):
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        sh([PY, os.path.join(sdir, "nm_ic.py"), "--out", d, "--kind", "infall", "--eps", "0.03",
            "--aend", "4", "--L", repr(half), "--edge_fac", "1.2", "--ndust", "1e5",
            "--nclump", "2e4", "--rclump", "0.3", "--shift", repr(shift), repr(shift),
            repr(shift)], log=os.path.join(d, "nm_ic.log"))
        setup = json.load(open(os.path.join(d, "setup.json")))
        x, u, m, sp = nio.read_nrp(os.path.join(d, "particles.nrp"))
        nc = setup["n_clump"]
        nio.write_nrp(os.path.join(d, "dust.nrp"), x[nc:], u[nc:], m[nc:])
        os.remove(os.path.join(d, "particles.nrp"))
        tlim = setup["tlim"]
        ch = merge(cube(nx, 32, -half, half), {
            "time": {"tlim": repr(tlim)},
            "particles": {"particle_file": "dust.nrp", "dt": 0.25, "newton_cfl": 0.15,
                          "snap_dt": repr(tlim/50), "newton_pm_mass": 1.0,
                          "newton_pm_x1": repr(shift), "newton_pm_x2": repr(shift),
                          "newton_pm_x3": repr(shift), "newton_pm_soft": 0.5,
                          "newton_pm_soft_frame": "comoving"}})
        cases.append(Case(name, deck(os.path.join(sdir, "nm_infall.athinput"), ch)))
    return run_all(out, cases, exe, jobs, rec)


def t6(out, exe, jobs, rec):
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    pf = os.path.join(ic, "spin.nrp")
    sh([PY, os.path.join(NEWTON, "make_ic.py"), "ball", "--out", pf, "--center", "0.3", "-0.2",
        "0.1", "--spacing", "0.0625", "--ntracer", "0", "--velocity", "-0.2", "0.15", "-0.1",
        "--omega", "0.2", "-0.3", "0.6"])
    p = {"time": {"tlim": 0.8}, "particles": {"particle_file": pf, "dt": 0.002,
                                               "snap_dt": 0.2, "hist_dcycle": 1}}
    cases = [Case("spin_uni64", deck(os.path.join(NEWTON, "isolated.athinput"),
                                     merge(cube(64, 16), p))),
             Case("spin_smr", deck(os.path.join(NEWTON, "isolated_smr.athinput"),
                                   merge(cube(64, 16), p)))]
    return run_all(out, cases, exe, jobs, rec)


def t6b(out, exe, jobs, rec):
    """T6 with the ball scaled to radius 0.7 and mass 0.343 (same density), inside the
    refined MeshBlocks for the whole run: uniform 64^3, uniform 128^3, 64^3 + one level."""
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    pf = os.path.join(ic, "spin.nrp")
    sh([PY, os.path.join(NEWTON, "make_ic.py"), "ball", "--out", pf, "--center", "0.05",
        "-0.05", "0.03", "--radius", "0.7", "--mass", "0.343", "--spacing", "0.0625",
        "--ntracer", "0", "--velocity", "-0.2", "0.15", "-0.1", "--omega", "0.2", "-0.3",
        "0.6"])
    p = {"time": {"tlim": 0.8}, "particles": {"particle_file": pf, "dt": 0.002,
                                               "snap_dt": 0.2, "hist_dcycle": 1}}
    iso = os.path.join(NEWTON, "isolated.athinput")
    cases = [Case("spin_in_uni128", deck(iso, merge(cube(128, 32), p))),
             Case("spin_in_uni64", deck(iso, merge(cube(64, 16), p))),
             Case("spin_in_smr", deck(os.path.join(NEWTON, "isolated_smr.athinput"),
                                      merge(cube(64, 16), p)))]
    return run_all(out, cases, exe, jobs, rec)


def t7(out, exe, jobs, rec):
    """Plane wave, N = 32: half the step for the multigrid and the spectral solver
    (their runs at the full step are mg and fftsp of test t1), and the cubic cloud with
    the cubic-spline gather at both steps."""
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    pf = os.path.join(ic, "wave32.nrp")
    sh([PY, os.path.join(NEWTON, "make_ic.py"), "wave", "--out", pf, "--n", "32"])
    per = os.path.join(NEWTON, "periodic.athinput")
    fft = os.path.join(NEWTON, "periodic_fft.athinput")
    w = {"particles": {"particle_file": pf}}
    nog = {"particles": {"newton_ngroup": 0}}
    half = {"particles": {"dt": 0.0025}}
    pcs = {"mesh": {"nghost": 4}, "particles": {"deposit_shape": "pcs", "interp": "bspline"}}
    cases = [Case("w32_dth_mg", deck(per, merge(w, half))),
             Case("w32_dth_sp", deck(fft, merge(w, nog, half)))]
    if os.environ.get("NEWTON2_T7_PCS"):
        cases += [Case("w32_dth_sp_pcs", deck(fft, merge(w, nog, half, pcs))),
                  Case("w32_dt1_sp_pcs", deck(fft, merge(w, nog, pcs)))]
    return run_all(out, cases, exe, jobs, rec)


def t8(out, exe, jobs, rec):
    import numpy as np
    from nrpic import io as nio
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    dx = 4.0/32
    diag = [0.0, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.475, 0.5]
    xline = [0.0, 0.1, 0.2, 0.3, 0.4, 0.45, 0.475]
    pts = [("d%05.3f" % s, (s, s, s)) for s in diag] + \
          [("x%05.3f" % s, (s, 0.5, 0.5)) for s in xline] + \
          [("e%05.3f" % s, (s, 0.0, 0.0)) for s in (0.025, 0.05, 0.1, 0.25, 0.5)]
    iso = os.path.join(NEWTON, "isolated.athinput")
    fft = os.path.join(NEWTON, "periodic_fft.athinput")
    one = {"time": {"nlim": 1}, "particles": {"dt": 1e-6, "snap_dt": 1e-6, "hist_dcycle": 1}}
    cases, table = [], []
    for name, off in pts:
        pf = os.path.join(ic, name + ".nrp")
        x = np.array([off])*dx
        nio.write_nrp(pf, x, np.zeros((1, 3)), np.ones(1))
        pp = {"particles": {"particle_file": pf}}
        cases.append(Case("iso_cic_" + name, deck(iso, merge(cube(32, 16), one, pp))))
        cases.append(Case("iso_pcs_" + name, deck(iso, merge(cube(32, 16), one, pp, {
            "mesh": {"nghost": 4}, "particles": {"deposit_shape": "pcs",
                                                 "interp": "bspline"}}))))
        # periodic box [0, 4)^3 with the particle near its middle (a vertex of the mesh)
        pfp = os.path.join(ic, name + "_per.nrp")
        nio.write_nrp(pfp, x + 2.0, np.zeros((1, 3)), np.ones(1))
        cases.append(Case("per_cic_" + name, deck(fft, merge(one, {"particles": {
            "particle_file": pfp, "newton_expansion": "none", "newton_ngroup": 0}}))))
        table.append(dict(name=name, offset=list(off)))
    rec["t8_points"] = table
    rec["t8_dx"] = dx
    return run_all(out, cases, exe, jobs, rec)


def compare_dirs(da, db, skip=("athena.log", "input.athinput")):
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    same, differ = [], []
    for nme in sorted(names):
        if os.path.basename(nme) in skip:
            continue
        fa, fb = os.path.join(da, nme), os.path.join(db, nme)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(nme + " (missing in one run)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(nme)
        else:
            differ.append(nme)
    return same, differ


def t10(out, exe, jobs, rec):
    """Existing set-ups with the executable of this branch, of the branch start and of
    the release: every output file byte for byte."""
    import shutil
    sys.path.insert(0, os.path.join(ROOT, "tracks", "core", "tools"))
    sys.path.insert(0, os.path.join(ROOT, "tracks", "core", "analysis", "dfix"))
    import regress_relativistic as rr
    import t6_regress as t6r
    exes = {"new": exe, "base": EXE_BASE, "rel": EXE_REL}
    jobs_list = []          # (case, label, dir, cmd)
    for case, c in rr.CASES.items():
        for label, e in exes.items():
            d = os.path.join(out, case, label)
            os.makedirs(d, exist_ok=True)
            shutil.copy(os.path.join(ROOT, c["inp"]), d)
            for f in c["files"]:
                shutil.copy(f, d)
            jobs_list.append((case, label, d,
                              [e, "-i", os.path.basename(c["inp"])] + c["args"]))
    nc = t6r.newton_cases(out)
    for case, args in nc.items():
        for label, e in exes.items():
            d = os.path.join(out, case, label)
            os.makedirs(d, exist_ok=True)
            jobs_list.append((case, label, d, [e, "-i", args[0], "-d", d] + args[1:]))

    def one(j):
        case, label, d, cmd = j
        t0 = time.time()
        rc = sh(cmd, cwd=d, log=os.path.join(d, "athena.log"))
        return dict(name="%s/%s" % (case, label), cmd=cmd, exit=rc, wall_s=time.time() - t0)

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(one, jobs_list))
    rec["cases"] = res
    report, bad = {}, 0
    for case in list(rr.CASES) + list(nc):
        r = {}
        for other in ("base", "rel"):
            same, differ = compare_dirs(os.path.join(out, case, "new"),
                                        os.path.join(out, case, other),
                                        skip=("athena.log", "input.athinput", "run.log"))
            r[other] = dict(identical=len(same), differ=differ)
            if other == "base":
                bad += len(differ) + (0 if same else 1)
        la = rr.log_results(os.path.join(out, case, "new", "athena.log"))
        lb = rr.log_results(os.path.join(out, case, "base", "athena.log"))
        r["log_result_lines"] = len(la)
        r["log_results_equal_base"] = (la == lb)
        if la != lb:
            bad += 1
        report[case] = r
        print("%-13s vs base: %d identical, differ %s | vs release: %d identical, differ %s"
              % (case, r["base"]["identical"], r["base"]["differ"] or "none",
                 r["rel"]["identical"], r["rel"]["differ"] or "none"), flush=True)
    rec["t10"] = report
    with open(os.path.join(out, "t10.json"), "w") as f:
        json.dump(report, f, indent=1)
    return bad == 0 and all(r["exit"] == 0 for r in res)


def card(out, exe, jobs, rec):
    """Decks, particle files and the batch list of the card job: the checks of the
    Fourier solver and of the group history against the processor runs, Track B's
    pancake at n = 64, and the throughput cases (2e6 particles, 20 steps each)."""
    import numpy as np
    from nrpic import io as nio
    bdir, commit = refs(out, "B-emd-gw")
    rec["refs"] = {"B-emd-gw": commit}
    gen = os.path.join(bdir, "tracks", "B-emd-gw", "newton_tests", "scripts", "make_particles.py")
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    per = os.path.join(NEWTON, "periodic.athinput")
    fft = os.path.join(NEWTON, "periodic_fft.athinput")
    iso = os.path.join(NEWTON, "isolated.athinput")
    decks = {}
    # checks: the cases mg, fft7, fftsp of t1 and sin32_sp of t3
    pf = os.path.join(ic, "wave32.nrp")
    sh([PY, os.path.join(NEWTON, "make_ic.py"), "wave", "--out", pf, "--n", "32"])
    wave = {"particles": {"particle_file": pf}}
    nog = {"particles": {"newton_ngroup": 0}}
    decks["chk_fftsp"] = deck(fft, merge(wave, nog))
    decks["chk_fft7"] = deck(fft, merge(wave, nog, {"particles": {"newton_fft_symbol":
                                                                  "seven_point"}}))
    decks["chk_mg"] = deck(per, wave)
    for name, kind, n in (("east64", "pancake-east", 64), ("chk_sin32", "pancake-sin", 32)):
        d = os.path.join(ic, name)
        sh([PY, gen, kind, "--n", str(n), "--delta", "0.05", "--L", "1", "--out", d])
    decks["east64"] = pancake_deck(bdir, 64, {"particles": {
        "newton_poisson": "fft", "newton_fft_symbol": "spectral",
        "particle_file": os.path.join(ic, "east64", "particles.nrp")}}, 7.0)
    n = 32
    grp = {"newton_ngroup": 2, "newton_group1_species": -1,
           "newton_group2_tag_min": (n//4)*n*n, "newton_group2_tag_max": (3*n//4)*n*n - 1,
           "hist_dcycle": 1, "traj_dcycle": 0, "newton_poisson": "fft",
           "newton_fft_symbol": "spectral",
           "particle_file": os.path.join(ic, "chk_sin32", "particles.nrp")}
    decks["chk_sin32"] = set_params(pancake_deck(bdir, n, {"particles": grp}, 5.0),  # card list of run core-20261119-145326-d509829: to t = 5
                                    "particles", {"traj_ntrack": 0})
    # throughput: 2e6 particles at rest, 20 steps
    rng = np.random.default_rng(5)
    npart = 2000000
    xp = rng.uniform(0.0, 4.0, size=(npart, 3))
    nio.write_nrp(os.path.join(ic, "box2e6.nrp"), xp, np.zeros((npart, 3)),
                  np.full(npart, 1.0/npart))
    r = 1.0*rng.uniform(0.0, 1.0, size=npart)**(1.0/3.0)
    dvec = rng.normal(size=(npart, 3))
    dvec /= np.sqrt((dvec*dvec).sum(axis=1))[:, None]
    nio.write_nrp(os.path.join(ic, "ball2e6.nrp"), r[:, None]*dvec, np.zeros((npart, 3)),
                  np.full(npart, 1.0/npart))
    quiet = {"time": {"nlim": 20}, "particles": {"dt": 0.001, "snap_dt": -1.0,
                                                 "hist_dcycle": 1, "newton_mg_tol": 1e-6}}
    pbox = {"particles": {"particle_file": os.path.join(ic, "box2e6.nrp"),
                          "newton_expansion": "none"}}
    pball = {"particles": {"particle_file": os.path.join(ic, "ball2e6.nrp")}}
    decks["bench_per256_fft"] = deck(fft, merge(cube(256, 64), quiet, pbox, nog))
    decks["bench_per256_mg"] = deck(per, merge(cube(256, 64), quiet, pbox))
    decks["bench_iso256_mg"] = deck(iso, merge(cube(256, 64), quiet, pball))
    decks["bench_per384_fft"] = deck(fft, merge(cube(384, 64), quiet, pbox, nog))
    decks["bench_iso384_mg"] = deck(iso, merge(cube(384, 128), quiet, pball))
    order = ["chk_fftsp", "chk_fft7", "chk_mg", "east64", "chk_sin32", "bench_per256_fft",
             "bench_per256_mg", "bench_iso256_mg", "bench_per384_fft", "bench_iso384_mg"]
    lines = ["# card job of work package newton2 (cases.py card): <name> <athinput>"]
    for name in order:
        path = os.path.join(out, name + ".athinput")
        with open(path, "w") as f:
            f.write(decks[name])
        lines.append("%s %s" % (name, path))
    with open(os.path.join(out, "card.list"), "w") as f:
        f.write("\n".join(lines) + "\n")
    rec["card_list"] = os.path.join(out, "card.list")
    print("\n".join(lines))
    return True


TESTS = dict(card=card, t1=t1, t2=t2, t3=t3, t4a=t4a, t4b=t4b, t4c=t4c, t5=t5, t6=t6, t6b=t6b,
             t7=t7, t8=t8, t10=t10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("test", choices=sorted(TESTS))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--exe", default=os.environ.get("NEWTON2_EXE", EXE_NEW))
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    rec = dict(test=a.test, exe=a.exe,
               exe_sha256=subprocess.run(["sha256sum", a.exe], capture_output=True,
                                         text=True).stdout.split()[0])
    t0 = time.time()
    ok = TESTS[a.test](a.out, a.exe, a.jobs, rec)
    rec["wall_s"] = time.time() - t0
    rec["ok"] = bool(ok)
    with open(os.path.join(a.out, "cases.json"), "w") as f:
        json.dump(rec, f, indent=1)
    print("%s: %s in %.0f s" % (a.test, "all cases ran" if ok else "FAILED", rec["wall_s"]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
