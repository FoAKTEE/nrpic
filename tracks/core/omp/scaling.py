#!/usr/bin/env python3
"""Strong scaling of the threaded processor build: runs the scaling cases at several
thread counts and placements and records the time of the step loop that the code prints
("cpu time used", the wall-clock time of the loop) and the zone-cycles per second.

    scaling.py --exe O3 --cases punc,cluster,cosmo,newton --threads 1,4,16
               [--bind spread] [--places cores] [--repeat 2] [--nlim-factor 1.0]
               [--out DIR] [--tag NAME]

Cases (inputs of this repository, initial data from make_ic.sh):
  punc     vacuum puncture on a statically refined mesh with six tracers and the horizon
           finder (problems/puncture/horizon_calib.athinput, dx = M/8 at the puncture)
  cluster  monoenergetic cluster, 1e5 particles, Z4c on a statically refined mesh
           (problems/st/st_cluster.athinput)
  cosmo    64^3 periodic box, eight particles per cell, production options of
           cosmo/README.md (problems/cosmo/daverio_field.athinput)
  newton   Newtonian mode, 128^3 periodic box, 5.12e5 particles (the size of Track D's
           request; problems/newton/periodic.athinput)
The time per step is loop time / cycles; the best of the repeats is the measurement, the
load average of the machine before and after each run is recorded with it.
Output: DIR/<case>/t<threads>_<bind>_<places>_r<k>/ and DIR/scaling.json; DIR defaults
to $NRPIC_RUN_DIR.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omplib as L  # noqa: E402

ST = "st_yc0p819_stratified_N100000_s1"
SCASES = {
    "punc": dict(inp="problems/puncture/horizon_calib.athinput", files=[], nlim=32,
                 args=["output2/dt=1.0e30"]),
    "cluster": dict(inp="problems/st/st_cluster.athinput",
                    files=[L.IC2 + "/st/%s.nrp" % ST, L.IC2 + "/st/%s.tab" % ST], nlim=16,
                    args=["particles/particle_file=%s.nrp" % ST,
                          "problem/comp0_file=%s.tab" % ST, "particles/snap_dt=1.0e30"]),
    "cosmo": dict(inp="problems/cosmo/daverio_field.athinput",
                  files=[L.IC2 + "/dav64/particles.nrp", L.IC2 + "/dav64/fields.bin"],
                  nlim=16,
                  args=["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "meshblock/nx1=32",
                        "meshblock/nx2=32", "meshblock/nx3=32",
                        "particles/deposit_shape=pcs",
                        "particles/deposit_comp_c=0.16666666666666666",
                        "particles/deposit_comp_c2=0.4666666666666667",
                        "particles/interp=bspline", "particles/dt_expansion=0.01",
                        "particles/cons_dcycle=16"]),
    "newton": dict(inp="problems/newton/periodic.athinput",
                   files=[L.IC2 + "/dnewt/wave80.nrp"], nlim=16,
                   args=["mesh/nx1=128", "mesh/nx2=128", "mesh/nx3=128",
                         "meshblock/nx1=32", "meshblock/nx2=32", "meshblock/nx3=32",
                         "particles/particle_file=wave80.nrp", "particles/snap_dt=1.0e30"]),
    # the Z4c benchmark of problems/tests (uniform 128^3, vacuum): the number that
    # docs/TESTLOG.md quotes for one card
    "bench": dict(inp="problems/tests/z4c_bench.athinput", files=[], nlim=8, args=[]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default="O3")
    ap.add_argument("--cases", default="punc,cluster,cosmo,newton")
    ap.add_argument("--threads", default="1,4,16")
    ap.add_argument("--bind", default="spread")
    ap.add_argument("--places", default="cores")
    ap.add_argument("--repeat", type=int, default=2)
    ap.add_argument("--nlim-factor", type=float, default=1.0)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--tag", default="")
    ap.add_argument("--extra", default="", help="more athena arguments, comma-separated")
    ap.add_argument("--mode", default="", choices=["", "priv"],
                    help="priv: deposit_threads = private in the <particles> block")
    ap.add_argument("--profile", action="store_true",
                    help="time per kernel (tools/kernel_timer.cpp) into each run directory")
    a = ap.parse_args()
    if not a.out:
        ap.error("--out or NRPIC_RUN_DIR")
    exe = L.EXES.get(a.exe, a.exe)
    bind = "" if a.bind == "none" else a.bind
    places = "" if a.places == "none" else a.places
    recs = []
    # one file per call (calls of one phase run side by side and must not overwrite
    # each other's records)
    out_json = os.path.join(a.out, "scaling%s_%s%s.json" % (
        ("_" + a.tag) if a.tag else "", a.cases.replace(",", "+"),
        ("_t" + a.threads.replace(",", "+")) if a.threads else ""))
    for case in a.cases.split(","):
        c = SCASES[case]
        nlim = max(1, int(round(c["nlim"]*a.nlim_factor)))
        spec = dict(inp=c["inp"], files=c["files"],
                    args=c["args"] + ["time/nlim=%d" % nlim]
                    + ([x for x in a.extra.split(",") if x]))
        for nt in [int(t) for t in a.threads.split(",")]:
            best = None
            for r in range(a.repeat):
                rd = os.path.join(a.out, case, "%st%d%s_%s_%s_r%d" % (
                    (a.tag + "_") if a.tag else "", nt, "p" if a.mode else "", bind or "nobind",
                    (places or "noplaces")[:12].replace(",", "+").replace(":", "-")
                    .replace("{", "").replace("}", ""), r))
                rec = L.run_case(exe, case, rd, nt, bind, places, spec=spec, profile=a.profile,
                                 mode=a.mode)
                rec.update(exe_label=a.exe, repeat=r, nlim=nlim, tag=a.tag,
                           exe_sha256=L.sha256(exe))
                if rec.get("loop_s") and rec.get("ncycle"):
                    rec["s_per_step"] = rec["loop_s"]/rec["ncycle"]
                recs.append(rec)
                L.dump(recs, out_json)
                if rec.get("s_per_step") and (best is None or rec["s_per_step"] < best):
                    best = rec["s_per_step"]
                print("%-8s %-3s%-2s threads %3d %-7s %-8s r%d  exit %d  loop %8.2f s  "
                      "step %8.4f s  zcps %.3e  load %5.1f -> %5.1f  cpu share %.2f" % (
                          case, a.exe, a.mode[:1], nt, bind or "-", (places or "-")[:8], r,
                          rec["exit"],
                          rec.get("loop_s", float("nan")),
                          rec.get("s_per_step", float("nan")),
                          rec.get("zcps", float("nan")), rec["load_before"],
                          rec["load_after"], rec["cpu_share"]))
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
