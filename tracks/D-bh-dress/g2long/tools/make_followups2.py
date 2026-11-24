#!/usr/bin/env python3
"""Second follow-up inputs of g2long (entry 10 of g2long/JOURNAL.md), one change each from a
long input, plus constraint norms in spheres outside the horizon (release core-v0.5,
`<particles> region_*`, coord/INTERFACES/cosmo_amr.md section 2.5).

  esflk4n  from esflk  dust lattice h_p 1 M -> 4^(-1/3) M (4N particles), data run DATA_4N
  esflkq   from esflk  dust lattice h_p 1 M -> 4^(1/3) M (N/4 particles), data run DATA_Q
  esfl16   from esfl   one finer level (M/16) on +-2.9 M (snaps to +-3 M), as es1l16 from es1l;
                       tlim 500 -> 300
Every one of them gains
  region_dcycle 160, region_horizon 0, region_horizon_factor 1.2, region_radius1..4 = 6, 12, 30, 60 M
(diagnostic output only). Step (cfl_number 0.25), gauge (plain 1+log, Gamma-driver shift_eta 2,
no lapse_leak) and all other outputs are the parent's (decisions 0025 item 3, 0027 item 2).

    make_followups2.py --data4n <run dir of esf_data.py --hp 0.62996> --dataq <run dir of --hp 1.5874>
"""
import argparse
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(os.path.dirname(HERE), "inputs")
DATA_N = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261121-203042-82deeec"

REGION = ("region_dcycle  = 160\nregion_horizon = 0\nregion_horizon_factor = 1.2\n"
          "region_radius1 = 6.0\nregion_radius2 = 12.0\nregion_radius3 = 30.0\nregion_radius4 = 60.0\n")
L8 = ("<refined_region6>\nlevel = 8\nx1min = -2.9\nx1max = 2.9\nx2min = -2.9\nx2max = 2.9\n"
      "x3min = -2.9\nx3max = 2.9\n\n")


def rep(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"expected {count} occurrence(s) of {old!r}, found {n}")
    return text.replace(old, new)


def header(name, parent, change):
    return (f"# {name}: {change} (Track D, package g2long, follow-up of entry 10).\n"
            f"# Built by tracks/D-bh-dress/g2long/tools/make_followups2.py from g2long/inputs/{parent}.athinput.\n"
            f"# Executable: release core-v0.6 (.work/build_gpu_v06/src/athena). Gauge plain 1+log, no lapse_leak.\n"
            f"# Predictions: g2long/JOURNAL.md entry 10. Parent header follows.\n#\n")


def add_region(b):
    return rep(b, "removal_record = true\n", "removal_record = true\n" + REGION)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data4n", required=True)
    ap.add_argument("--dataq", required=True)
    a = ap.parse_args()
    src = {n: open(os.path.join(INP, n + ".athinput")).read() for n in ("esflk", "esfl")}
    out = {}
    for name, d, what in (("esflk4n", a.data4n, "dust lattice h_p 4^(-1/3) M (4N)"),
                          ("esflkq", a.dataq, "dust lattice h_p 4^(1/3) M (N/4)")):
        b = src["esflk"]
        b = rep(b, f"particle_file  = {DATA_N}/esf.nrp\n", f"particle_file  = {d}/esf.nrp\n")
        b = rep(b, f"comp0_file = {DATA_N}/esf.tab\n", f"comp0_file = {d}/esf.tab\n")
        b = rep(b, "basename  = esflk\n", f"basename  = {name}\n")
        out[name] = header(name, "esflk", what + "; region norms") + add_region(b)
    b = src["esfl"]
    b = rep(b, "\n<time>\n", "\n" + L8 + "<time>\n")
    b = rep(b, "basename  = esfl\n", "basename  = esfl16\n")
    b = rep(b, "tlim       = 500.0\n", "tlim       = 300.0\n")
    out["esfl16"] = header("esfl16", "esfl", "one finer level M/16 on +-3 M, tlim 300; region norms") + add_region(b)
    for name, text in out.items():
        with open(os.path.join(INP, name + ".athinput"), "w") as f:
            f.write(text)
        print("wrote", name)


if __name__ == "__main__":
    main()
