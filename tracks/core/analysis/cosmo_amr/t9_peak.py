#!/usr/bin/env python3
"""T9 of the work package cosmo-amr: adaptive refinement on Track A's curvature peak, on
processors (prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t9_peak.py --new NEW_EXE --rel REL_EXE --ic DIR --out DIR [--cores N]

--ic: a directory with particles.nrp and fields.bin of the peak on 32^3 cells (Track A's
make_peak_ic.py; default: ic_peak0.5 of run A-emd-pbh-20261115-154740-69e8f8b).
Root 32^3, MeshBlocks 8^3, at most two refinement levels, 10 cycles, input
problems/cosmo_amr/peak_amr.athinput.  Cases:
  lohner     <z4c_amr> method = lohner, no <particles_amr> (the track's request)
  lohnerrel  the same with the release executable (null refinement function)
  ladder     lapse ladder of the example input, coarse clouds reconstructed
  ladderc    the same with the released constant spreading
  chi        chi_ratio_1 = 0.9
  ppc        ppc_refine = 1.05 (cells that hold more than 1.05 particles)
Writes DIR/t9_summary.json and DIR/fig_t9_peak.{pdf,png}."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A

DEF_IC = ("/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-154740-69e8f8b/"
          "ic_peak0.5")


def base(ic, rel=False):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo_amr/peak_amr.athinput"))
    for d in "123":
        b.set("mesh", **{f"nx{d}": 32})
        b.set("meshblock", **{f"nx{d}": 8})
    b.set("mesh_refinement", num_levels=3, max_nmb_per_rank=600, ncycle_check=2,
          refinement_interval=4)
    b.set("time", tlim=10.0, nlim=10)
    b.set("particles", particle_file=os.path.join(ic, "particles.nrp"), cstat_dcycle=1,
          region_dcycle=1, hist_dcycle=1)
    b.set("problem", id_file=os.path.join(ic, "fields.bin"))
    b.drop("fastflow")
    for k in list(b.blocks):
        if k.startswith("output"):
            b.drop(k)
    b.set("output1", file_type="hst", dt=0.1)
    if rel:
        b.drop("particles_amr").drop("z4c_guard").drop("z4c", "dt_lightspeed")
        b.drop("particles", "deposit_fine_shape", "region_dcycle", "region_radius1",
               "region_radius2", "region_horizon")
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--rel", required=True)
    ap.add_argument("--ic", default=DEF_IC)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=6)
    a = ap.parse_args()
    a.out, a.new, a.rel = (os.path.abspath(v) for v in (a.out, a.new, a.rel))
    os.makedirs(a.out, exist_ok=True)
    loh = dict(method="lohner", lohner_refine=0.2, lohner_derefine=0.02, lohner_eps=0.01)
    cs = {}
    cs["lohner"] = base(a.ic).drop("particles_amr").set("z4c_amr", **loh)
    cs["lohnerrel"] = base(a.ic, rel=True).set("z4c_amr", **loh)
    cs["ladder"] = base(a.ic)
    cs["ladderc"] = base(a.ic).set("particles", deposit_fine_shape=False)
    c = base(a.ic).drop("particles_amr")
    c.set("particles_amr", chi_ratio_1=0.9, verbose=True)
    cs["chi"] = c
    c = base(a.ic).drop("particles_amr")
    c.set("particles_amr", ppc_refine=1.05, ppc_derefine=0.1, verbose=True)
    cs["ppc"] = c
    names = list(cs)
    rcs = A.run_many([((a.rel if n.endswith("rel") else a.new), cs[n],
                       os.path.join(a.out, n), "peak", (), None) for n in names], a.cores)
    res, hist = {}, {}
    for n, rc in zip(names, rcs):
        d = os.path.join(a.out, n)
        r = dict(exit=rc[0], wall=round(rc[1], 1))
        hp = os.path.join(d, "peak.nrpic.hst")
        if os.path.exists(hp):
            h, s = A.read_hst(hp), A.read_hst(os.path.join(d, "peak.cstat.hst"))
            r.update(records=len(h["time"]), nmb=[int(v) for v in h["nmb"]],
                     np_first=int(h["np"][0]), np_last=int(h["np"][-1]),
                     rest_mass_change=float(abs(h["sum_m"][-1]/h["sum_m"][0] - 1.0)),
                     identity_E=float(np.max(np.abs(h["int_E"]/h["sum_mW"] - 1.0))),
                     Hr_max=[float(v) for v in s["Hr_max"]],
                     H_max=[float(v) for v in s["H_max"]],
                     E_min=float(np.min(s["E_min"])))
            hist[n] = dict(t=h["time"], nmb=h["nmb"], ts=s["time"], hr=s["Hr_max"])
            rp = os.path.join(d, "peak.region.hst")
            if os.path.exists(rp):
                g = A.read_hst(rp)
                r["H2_over_E2_in_rm"] = [float(v) for v in g["H2_in_s1"]/g["E2_in_s1"]]
                r["H2_over_E2_out_rm"] = [float(v) for v in g["H2_out_s1"]/g["E2_out_s1"]]
                hist[n].update(tr=g["time"], hin=g["H2_in_s1"]/g["E2_in_s1"],
                               hout=g["H2_out_s1"]/g["E2_out_s1"])
        with open(os.path.join(d, "log.txt"), errors="replace") as f:
            txt = f.read().splitlines()
        r["refine_log"] = [x for x in txt if x.startswith("NRPIC refine")][:6]
        r["log_tail"] = [x for x in txt[-8:] if "MeshBlocks" in x or "Terminating" in x
                         or "FATAL" in x]
        res[n] = r
        print(n, "exit", rc[0], r.get("nmb"), r.get("identity_E"))
    res["ic"] = a.ic
    with open(os.path.join(a.out, "t9_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(8.0, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.95, wspace=0.36)
    cols = fs.SERIES + ["k", "grey"]
    for i, n in enumerate([m for m in names if m in hist]):
        ax[0].plot(hist[n]["t"], hist[n]["nmb"], color=cols[i], label=n)
        ax[1].semilogy(hist[n]["ts"], hist[n]["hr"], color=cols[i], label=n)
        if "hin" in hist[n]:
            ax[2].semilogy(hist[n]["tr"], hist[n]["hin"], color=cols[i], label=n)
            ax[2].semilogy(hist[n]["tr"], hist[n]["hout"], "--", color=cols[i])
    ax[0].set_ylabel("MeshBlocks")
    ax[1].set_ylabel("largest relative Hamiltonian constraint")
    ax[2].set_ylabel(r"$\|H\|_2/\|16\pi E\|_2$ (solid: $r<r_m$, dashed: outside)")
    for q in ax:
        q.set_xlabel("conformal time")
    ax[0].legend(frameon=False, fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_t9_peak"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
