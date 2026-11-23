#!/usr/bin/env python3
"""Follow-up inputs of g2long (entry 6 of g2long/JOURNAL.md), each one change from a long input.

  v1l4   from v1l    finest level 7 (M/8) -> 6 (M/4) on the same +-1.5 M region; tlim 500 -> 300
  es1l4  from es1l   the same change
  esfl4  from esfl   the same change, tlim 500 kept
  esflk  from esfl   fastflow initial_radius_0 0.8 -> 1.6 (horizon excision stays on while the
                     smallest horizon radius is below 4 x 1.6 = 6.4 M, nrpic.cpp:451-455);
                     tlim 500 -> 400

Writes g2long/inputs/<name>.athinput. Step (cfl_number 0.25), gauge (plain 1+log, Gamma-driver
shift_eta 2, no lapse_leak) and outputs are those of the parent (decisions 0025 item 3, 0027
item 2).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(os.path.dirname(HERE), "inputs")


def rep(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"expected {count} occurrence(s) of {old!r}, found {n}")
    return text.replace(old, new)


def coarsen(body):
    regs = re.findall(r"^<refined_region(\d+)>\nlevel = (\d+)$", body, flags=re.M)
    k, lev = max(regs, key=lambda r: int(r[1]))
    if lev != "7":
        raise SystemExit(f"finest refined region has level {lev}, expected 7")
    return rep(body, f"<refined_region{k}>\nlevel = 7\n", f"<refined_region{k}>\nlevel = 6\n")


def header(name, parent, change):
    return (f"# {name}: {change} (Track D, package g2long, follow-up of entry 6).\n"
            f"# Built by tracks/D-bh-dress/g2long/tools/make_followups.py from g2long/inputs/{parent}.athinput.\n"
            f"# Executable: release core-v0.6 (.work/build_gpu_v06/src/athena). Gauge plain 1+log, no lapse_leak.\n"
            f"# Predictions: g2long/JOURNAL.md entry 6. Parent header follows.\n#\n")


def main():
    src = {n: open(os.path.join(INP, n + ".athinput")).read() for n in ("v1l", "es1l", "esfl")}
    out = {}
    for name, par, tl in (("v1l4", "v1l", "300.0"), ("es1l4", "es1l", "300.0"), ("esfl4", "esfl", None)):
        b = coarsen(src[par])
        b = rep(b, f"basename  = {par}\n", f"basename  = {name}\n")
        if tl:
            b = rep(b, "tlim       = 500.0\n", f"tlim       = {tl}\n")
        out[name] = header(name, par, "finest level M/8 -> M/4 on +-1.5 M" + (f", tlim {tl}" if tl else "")) + b
    b = src["esfl"]
    b = rep(b, "initial_radius_0  = 0.8\n", "initial_radius_0  = 1.6\n")
    b = rep(b, "basename  = esfl\n", "basename  = esflk\n")
    b = rep(b, "tlim       = 500.0\n", "tlim       = 400.0\n")
    out["esflk"] = header("esflk", "esfl", "finder initial_radius_0 0.8 -> 1.6 (horizon excision kept to 6.4 M), tlim 400") + b
    for name, text in out.items():
        with open(os.path.join(INP, name + ".athinput"), "w") as f:
            f.write(text)
        print("wrote", name)


if __name__ == "__main__":
    main()
