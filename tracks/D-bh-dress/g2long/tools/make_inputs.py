#!/usr/bin/env python3
"""Build the inputs of the g2long package (long card runs toward G2, plain 1+log).

Every input is a committed parent with a stated list of changes; each replacement is
asserted to happen exactly once.

  add_root(text)  one coarser root level below the old root: faces +-F -> +-2F (nx = 96
                  stays, so the root dx doubles), every <refined_regionK> renumbered K+1
                  with its level +1, a new region 1 (level 1) on +-(F - 0.1). The mesh
                  inside +-F is unchanged. Self-check: add_root(es_runs V-1) must give the
                  body of drift_controls/inputs/v1b_bnd384.athinput (V-1B) up to basename.
  add_m16(text)   one finer level (M/16) on +-2.9 M around the puncture (the level-7
                  blocks of 1.5 M snap to +-3 M), as the last refined region.

Runs (basename, parent, changes):
  v1l    es_runs/inputs/v1_dx8      add_root twice (faces +-768 M), tlim 500
  es1l   es_runs/inputs/es1_dx8     add_root twice, tlim 500
  esfl   flux_tools/inputs/esf_dx8  add_root twice, tlim 500
  v1l16  v1l                         add_m16, tlim 300
  es1l16 es1l                        add_m16, tlim 300
No input sets <z4c> lapse_leak (decision 0025 item 3).
Usage: python3 make_inputs.py [--check]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRK = os.path.dirname(PKG)
P_V1 = os.path.join(TRK, "es_runs", "inputs", "v1_dx8.athinput")
P_ES1 = os.path.join(TRK, "es_runs", "inputs", "es1_dx8.athinput")
P_ESF = os.path.join(TRK, "flux_tools", "inputs", "esf_dx8.athinput")
P_V1B = os.path.join(TRK, "drift_controls", "inputs", "v1b_bnd384.athinput")
OUT = os.path.join(PKG, "inputs")
SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
OLD_ESF_DATA = SCR + "/D-20261119-145022-2208a19"
NEW_ESF_DATA = SCR + "/D-20261121-203042-82deeec"


def rep(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"expected {count} occurrence(s) of {old!r}, found {n}")
    return text.replace(old, new)


def split_header(text):
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines) and (lines[i].startswith("#") or lines[i].strip() == ""):
        i += 1
    return "".join(lines[:i]), "".join(lines[i:])


def faces(body):
    m = re.findall(r"^x1max {5}= ([0-9.]+)\s*$", body, flags=re.M)   # <mesh> only
    assert len(m) == 1, m
    return float(m[0])


def add_root(body):
    F = faces(body)
    G = 2 * F
    for ax in ("x1", "x2", "x3"):
        body = rep(body, f"{ax}min     = -{F:.1f}", f"{ax}min     = -{G:.1f}")
        body = rep(body, f"{ax}max     = {F:.1f}", f"{ax}max     = {G:.1f}")
    regs = re.findall(r"^<refined_region(\d+)>\nlevel = (\d+)$", body, flags=re.M)
    assert regs, "no refined regions"
    for k, lev in sorted(((int(k), int(l)) for k, l in regs), reverse=True):
        body = rep(body, f"<refined_region{k}>\nlevel = {lev}\n",
                   f"<refined_region{k + 1}>\nlevel = {lev + 1}\n")
    b = F - 0.1
    new1 = (f"<refined_region1>\nlevel = 1\n"
            f"x1min = -{b:.1f}\nx1max = {b:.1f}\nx2min = -{b:.1f}\nx2max = {b:.1f}\n"
            f"x3min = -{b:.1f}\nx3max = {b:.1f}\n\n<refined_region2>\nlevel = 2\n")
    body = rep(body, "<refined_region2>\nlevel = 2\n", new1)
    return body


def add_m16(body):
    regs = re.findall(r"^<refined_region(\d+)>\nlevel = (\d+)$", body, flags=re.M)
    kmax = max(int(k) for k, _ in regs)
    lmax = max(int(l) for _, l in regs)
    block = (f"<refined_region{kmax + 1}>\nlevel = {lmax + 1}\n"
             "x1min = -2.9\nx1max = 2.9\nx2min = -2.9\nx2max = 2.9\n"
             "x3min = -2.9\nx3max = 2.9\n\n<time>\n")
    return rep(body, "<time>\n", block)


def set_basename(body, old, new):
    return rep(body, f"basename  = {old}\n", f"basename  = {new}\n")


def set_tlim(body, old, new):
    return rep(body, f"tlim       = {old}\n", f"tlim       = {new}\n")


HDR = {
    "v1l": "V-1L: vacuum control of ES-1L and ES-FL; V-1 (es_runs) with the faces at +-768 M",
    "es1l": "ES-1L: the vacuum-bubble null test; ES-1 (es_runs) with the faces at +-768 M",
    "esfl": "ES-FL: dust filling the bubble; ES-F (flux_tools) with the faces at +-768 M",
    "v1l16": "V-1L16: V-1L with one finer level (M/16) on +-3 M around the puncture",
    "es1l16": "ES-1L16: ES-1L with one finer level (M/16) on +-3 M around the puncture",
}


def header(name, parent, changes):
    return (f"# {HDR[name]} (Track D, package g2long).\n"
            f"# Built by tracks/D-bh-dress/g2long/tools/make_inputs.py from {parent}:\n"
            f"# {changes}. Gauge plain 1+log (no lapse_leak, decision 0025 item 3).\n"
            "# Executable: release core-v0.6 (.work/build_gpu_v06/src/athena).\n"
            "# Predictions and criteria: g2long/JOURNAL.md entry 1. Parent header follows.\n#\n")


def build():
    out = {}
    h1, v1 = split_header(open(P_V1).read())
    h2, es1 = split_header(open(P_ES1).read())
    h3, esf = split_header(open(P_ESF).read())
    # self-check against V-1B (drift_controls), the matched control of the G1 floor
    _, v1b = split_header(open(P_V1B).read())
    mine = set_basename(add_root(v1), "v1", "v1b")
    if mine != v1b:
        raise SystemExit("add_root(V-1) differs from V-1B: transformation not the one of V-1B")
    two = "two coarser root levels (+-192 -> +-768 M, root dx 16 M), tlim 200 -> 500 M"
    b = set_tlim(set_basename(add_root(add_root(v1)), "v1", "v1l"), "200.0", "500.0")
    out["v1l"] = header("v1l", "es_runs/inputs/v1_dx8.athinput", two) + h1 + b
    b = set_tlim(set_basename(add_root(add_root(es1)), "es", "es1l"), "200.0", "500.0")
    out["es1l"] = header("es1l", "es_runs/inputs/es1_dx8.athinput", two) + h2 + b
    b = set_tlim(set_basename(add_root(add_root(esf)), "esf", "esfl"), "200.0", "500.0")
    # the ES-F table ends at rbar = 345 M with exterior = zero (covers the +-192 M corner
    # only); the +-768 M corner is at 1330 M: table and particles of the data run with
    # --rbar_max 1340 (rows to 345 M and particles identical to the ES-F data run)
    b = rep(b, OLD_ESF_DATA + "/esf.nrp", NEW_ESF_DATA + "/esf.nrp")
    b = rep(b, OLD_ESF_DATA + "/esf.tab", NEW_ESF_DATA + "/esf.tab")
    out["esfl"] = header("esfl", "flux_tools/inputs/esf_dx8.athinput",
                         two + "; data run " + os.path.basename(NEW_ESF_DATA)
                         + " (table to 1340 M)") + h3 + b
    m16 = "add one level (M/16) on +-2.9 M (snaps to +-3 M), tlim 500 -> 300 M"
    for name, base in (("v1l16", "v1l"), ("es1l16", "es1l")):
        hb, bb = split_header(out[base])
        bb = set_tlim(set_basename(add_m16(bb), base, name), "500.0", "300.0")
        out[name] = header(name, f"g2long/inputs/{base}.athinput", m16) + hb + bb
    return out


def main():
    check = "--check" in sys.argv
    bad = 0
    for name, text in build().items():
        path = os.path.join(OUT, f"{name}.athinput")
        if check:
            same = os.path.exists(path) and open(path).read() == text
            print(f"{name}.athinput: {'matches' if same else 'DIFFERS'}")
            bad += not same
        else:
            open(path, "w").write(text)
            print(f"wrote {path}")
    print("self-check add_root(V-1) == V-1B: passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
