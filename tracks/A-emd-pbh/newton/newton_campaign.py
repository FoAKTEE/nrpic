#!/usr/bin/env python3
"""Run a set of AthenaK Newtonian-mode cases (release executable, processors) for the
precursor scan of track A: the spherical top-hat against the cycloid and the first points
of SCAN.md against the homogeneous-ellipsoid references.

    newton_campaign.py --campaign NAME [--jobs J] [--only a,b] [--nlim N] [--out DIR]

Run through `harness/bin/nrpic-run submit --launcher local --cores J -- python3 ...` from
the worktree root: the output root is $NRPIC_RUN_DIR (or --out). Each case gets its own
directory with the particle file and its JSON (make_deformed_ball.py), the AthenaK
output (`newton.newton.hst`, `newton.nrpic.hst`, snapshots) and `case.json` (command,
wall time, exit code). `campaign.json` lists all cases. The executable is the release
processor build of core-v0.3 (serial Kokkos backend: one core per case; J cases at once).

Nothing here simulates: the gravity, the deposit and the push are AthenaK's
(decision 0010). The input deck is problems/newton/isolated.athinput of core; every
change is a command-line override listed in case.json.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402

import ellipsoid as el  # noqa: E402
import make_deformed_ball as mdb  # noqa: E402
from nrpic import io as nio  # noqa: E402

EXE_CPU = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
DECK = os.path.join(ROOT, "problems", "newton", "isolated.athinput")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- cases
def tophat_case(name, nx, hxi, cfl=0.2, half=3.0, snaps=3):
    """Zel'dovich sphere lambda = 0.1 at a0 = 1 (a0 lambda = 0.1): expands from R = 0.9 to
    R_max = 2.12, turns around at t = 4.86 and collapses at t = 9.72 (cycloid)."""
    return dict(name=name, kind="tophat", abg=(0.1, 0.1, 0.1), a0=1.0, nx=nx, hxi=hxi,
                cfl=cfl, half=half, t_end_over_tc=1.06, snaps=snaps, rotate=None)


def ell_case(name, dL, e, p, nx=128, hxi=0.025, cfl=0.2, rotate=None, half_fac=1.5,
             t_end_over_t1=1.35, snaps=8):
    return dict(name=name, kind="ellipsoid", abg=tuple(el.abg_from_dep(dL, e, p)), a0=None,
                dep=(dL, e, p), nx=nx, hxi=hxi, cfl=cfl, half_fac=half_fac,
                t_end_over_t1=t_end_over_t1, snaps=snaps, rotate=rotate)


CAMPAIGNS = {
    # cost per cycle on one core (30 cycles each)
    "cost": [tophat_case("th_n064_h050", 64, 0.05), tophat_case("th_n128_h025", 128, 0.025),
             tophat_case("th_n256_h025", 256, 0.025), tophat_case("th_n128_h0125", 128, 0.0125),
             ell_case("e0p2_n128_h025", 0.2, 0.2, 0.0)],
    # spherical top-hat on processors: mesh {32, 64, 128}^3 x lattice spacing {0.1, 0.05,
    # 0.025} (4.2e3, 3.4e4, 2.7e5 particles), and the step (cfl 0.1 against 0.2)
    "tophat": [tophat_case(f"th_n{nx:03d}_h{int(round(h * 1000)):03d}", nx, h)
               for nx in (32, 64, 128) for h in (0.1, 0.05, 0.025)]
              + [tophat_case("th_n128_h050_cfl01", 128, 0.05, cfl=0.1)],
    # on a card: 2.1e6 particles (lattice spacing 0.0125) at 64^3 and 128^3
    "tophat_card": [tophat_case("th_n064_h0125", 64, 0.0125),
                    tophat_case("th_n128_h0125", 128, 0.0125)],
    # first points of SCAN.md: ellipticity at delta_L = 0.2 (p = 0), prolateness at e = 0.2,
    # amplitude at e = 0.1, lattice rotation, mesh and particle number at e = 0.1 and 0.2
    "scan": [ell_case("e0p05", 0.2, 0.05, 0.0), ell_case("e0p1", 0.2, 0.1, 0.0),
             ell_case("e0p2", 0.2, 0.2, 0.0), ell_case("e0p3", 0.2, 0.3, 0.0),
             ell_case("e0p2_pp", 0.2, 0.2, 0.2), ell_case("e0p2_pm", 0.2, 0.2, -0.2),
             ell_case("e0p1_dL0p05", 0.05, 0.1, 0.0), ell_case("e0p1_dL0p6", 0.6, 0.1, 0.0),
             ell_case("e0p2_rot", 0.2, 0.2, 0.0, rotate=7),
             ell_case("e0p1_n064", 0.2, 0.1, 0.0, nx=64), ell_case("e0p2_n064", 0.2, 0.2, 0.0, nx=64),
             ell_case("e0p1_h050", 0.2, 0.1, 0.0, hxi=0.05),
             ell_case("e0p2_h050", 0.2, 0.2, 0.0, hxi=0.05)],
    # on a card: particle number 2.1e6 at e = 0.2 (third point of the N series)
    "scan_card": [ell_case("e0p2_h0125", 0.2, 0.2, 0.0, hxi=0.0125)],
}
CAMPAIGNS["card"] = CAMPAIGNS["tophat_card"] + CAMPAIGNS["scan_card"]


def prepare(case, root, nlim=None):
    d = os.path.join(root, case["name"])
    os.makedirs(d, exist_ok=True)
    lams = np.asarray(case["abg"], dtype=float)
    b = mdb.build(lams, case["a0"], case["hxi"], case["rotate"])
    pfile = os.path.join(d, "ball.nrp")
    nio.write_nrp(pfile, b["x"], b["v"], b["m"])
    ref = mdb.references(lams, b["a0"], b["r_vol"])
    e, p = el.ep_from_abg(*lams)
    meta = dict(case=case, abg=lams.tolist(), deltaL=float(lams.sum()), e=float(e),
                p=float(p), a0=b["a0"], t0=b["t0"], H0=b["H0"], n=b["n"], mass=mdb.M_PATCH,
                r_vol=b["r_vol"], r_mom=b["r_mom"], rotation=b["rot"], reference=ref)
    t0 = b["t0"]
    if case["kind"] == "tophat":
        t_end = case["t_end_over_tc"] * ref["cycloid"]["t_c"]
        half = case["half"]
    else:
        t1 = ref["ellipsoid_isolated"]["collapses"][0]["t"]
        t_end = case["t_end_over_t1"] * t1
        ev = el.evolve(lams, a0=b["a0"], model="isolated", RL=(b["r_vol"],) * 3,
                       M=mdb.M_PATCH, n_collapse=3, t_end=t_end)
        amax = float(np.abs(ev["A"][ev["t"] <= t_end]).max())
        half = case["half_fac"] * amax
    tlim = t_end - t0
    nx = case["nx"]
    mb = 32 if nx <= 128 else 64
    dtmax = tlim / 400.0
    snap_dt = tlim / case["snaps"] if case["snaps"] else -1.0
    meta.update(t_end=t_end, tlim_code=tlim, half_width=half, dx=2.0 * half / nx, dt_max=dtmax,
                snap_dt=snap_dt)
    with open(os.path.join(d, "ball.json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    args = [EXE_CPU, "-i", DECK, "-d", d, "job/basename=newton",
            f"mesh/nx1={nx}", f"mesh/nx2={nx}", f"mesh/nx3={nx}",
            f"mesh/x1min={-half!r}", f"mesh/x1max={half!r}", f"mesh/x2min={-half!r}",
            f"mesh/x2max={half!r}", f"mesh/x3min={-half!r}", f"mesh/x3max={half!r}",
            f"meshblock/nx1={mb}", f"meshblock/nx2={mb}", f"meshblock/nx3={mb}",
            f"time/tlim={tlim!r}", "time/ndiag=50",
            f"particles/dt={dtmax!r}", f"particles/newton_cfl={case['cfl']!r}",
            "particles/newton_mg_tol=1e-6", f"particles/snap_dt={snap_dt!r}",
            f"particles/particle_file={pfile}", "particles/hist_dcycle=1",
            "output1/dt=1.0e30"]
    if nlim is not None:
        args.append(f"time/nlim={nlim}")
    return d, args, pfile, b["n"]


def run_case(d, args, pfile, n=None):
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        rc = subprocess.run(args, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                            env=dict(os.environ, OMP_NUM_THREADS="1")).returncode
    wall = time.time() - t0
    info = dict(command=args, cwd=d, exit_code=rc, wall_s=round(wall, 2), cores=1,
                card_hours=0.0, inputs=[dict(path=DECK, sha256=sha256(DECK)),
                                        dict(path=EXE_CPU, sha256=sha256(EXE_CPU)),
                                        dict(path=pfile, sha256=sha256(pfile))])
    with open(os.path.join(d, "case.json"), "w") as f:
        json.dump(info, f, indent=1)
        f.write("\n")
    return os.path.basename(d), rc, wall


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", required=True, choices=sorted(CAMPAIGNS))
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--only", default=None)
    ap.add_argument("--nlim", type=int, default=None)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--prepare-only", action="store_true",
                    help="write the particle files and batch.list (lines `<name> <deck> "
                         "[args]` for `nrpic-run submit --launcher batch --list`) and stop")
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: set NRPIC_RUN_DIR or --out")
    cases = CAMPAIGNS[a.campaign]
    if a.only:
        keep = set(a.only.split(","))
        cases = [c for c in cases if c["name"] in keep]
    nlim = a.nlim if a.nlim is not None else (30 if a.campaign == "cost" else None)
    prepared = [prepare(c, a.out, nlim) for c in cases]
    if a.prepare_only:
        # card runs: the harness writes each run into <its run dir>/<name>/ and passes the
        # executable; keep the deck and the overrides, drop the executable and -d
        with open(os.path.join(a.out, "batch.list"), "w") as f:
            for (d, args, pfile, n), c in zip(prepared, cases):
                f.write(" ".join([c["name"], DECK] + args[5:]) + "\n")
        inputs = [dict(path=pfile, sha256=sha256(pfile), n=n) for d, args, pfile, n in prepared]
        with open(os.path.join(a.out, "prepared.json"), "w") as f:
            json.dump(dict(campaign=a.campaign, deck=DECK, deck_sha256=sha256(DECK),
                           inputs=inputs), f, indent=1)
            f.write("\n")
        print(open(os.path.join(a.out, "batch.list")).read())
        return
    # longest cases first
    order = sorted(range(len(prepared)), key=lambda k: -(cases[k]["nx"] ** 3 + 30 * prepared[k][3]))
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        res = list(pool.map(lambda k: run_case(*prepared[k]), order))
    summary = dict(campaign=a.campaign, jobs=a.jobs, nlim=nlim, wall_s=round(time.time() - t0, 2),
                   cases=[dict(name=n, exit_code=rc, wall_s=round(w, 2)) for n, rc, w in res])
    with open(os.path.join(a.out, "campaign.json"), "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    print(json.dumps(summary, indent=1))
    sys.exit(0 if all(rc == 0 for _, rc, _ in res) else 1)


if __name__ == "__main__":
    main()
