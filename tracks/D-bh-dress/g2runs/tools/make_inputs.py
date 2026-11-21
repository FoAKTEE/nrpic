#!/usr/bin/env python3
"""Build the inputs of the g2runs package from committed inputs, one change each.

ES-1GB = es_runs/inputs/es1g_dx8.athinput with the root level of
         drift_controls/inputs/v1b_bnd384.athinput (outer faces at +-384 M, one coarser
         root level, every old level moved up by one; the mesh inside +-192 M unchanged).
V-1GB  = drift_controls/inputs/v1b_bnd384.athinput with <z4c> lapse_leak = 0.5,
         lapse_leak_alpha = 1.0 (the two lines of ES-1G).

Each replacement is asserted to happen exactly once; the script then prints the diff of
the produced files against their parents so that the change can be read off.
Usage: python3 make_inputs.py [--check]   (--check: compare with the files on disk)
"""
import difflib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRK = os.path.dirname(PKG)
ES1G = os.path.join(TRK, "es_runs", "inputs", "es1g_dx8.athinput")
V1B = os.path.join(TRK, "drift_controls", "inputs", "v1b_bnd384.athinput")
OUT_ES = os.path.join(PKG, "inputs", "es1gb_bnd384.athinput")
OUT_V = os.path.join(PKG, "inputs", "v1gb_bnd384.athinput")


def rep(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"expected {count} occurrence(s) of {old!r}, found {n}")
    return text.replace(old, new)


def strip_header(text):
    """Drop the leading comment block (lines starting with '#') before <comment>."""
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines) and (lines[i].startswith("#") or lines[i].strip() == ""):
        i += 1
    return "".join(lines[i:]), "".join(lines[:i])


def es1gb():
    src = open(ES1G).read()
    body, old_header = strip_header(src)
    # outer faces +-192 -> +-384 (nx1..3 = 96 stays: root dx 4 -> 8 M)
    for ax in ("x1", "x2", "x3"):
        body = rep(body, f"{ax}min     = -192.0", f"{ax}min     = -384.0")
        body = rep(body, f"{ax}max     = 192.0", f"{ax}max     = 384.0")
    # old levels 1, 2, 5 -> 2, 3, 6 and a new level 1 on +-191.9 (as V-1B)
    body = rep(body, "<refined_region3>\nlevel = 5", "<refined_region4>\nlevel = 6")
    body = rep(body, "<refined_region2>\nlevel = 2", "<refined_region3>\nlevel = 3")
    new1 = ("<refined_region1>\nlevel = 1\n"
            "x1min = -191.9\nx1max = 191.9\nx2min = -191.9\nx2max = 191.9\n"
            "x3min = -191.9\nx3max = 191.9\n\n<refined_region2>\nlevel = 2")
    body = rep(body, "<refined_region1>\nlevel = 1", new1)
    body = rep(body, "basename  = es\n", "basename  = es1gb\n")
    header = (
        "# ES-1GB (Track D, package g2runs): ES-1G with the outer faces at +-384 M.\n"
        "# Built by tracks/D-bh-dress/g2runs/tools/make_inputs.py from\n"
        "# es_runs/inputs/es1g_dx8.athinput and the root level of\n"
        "# drift_controls/inputs/v1b_bnd384.athinput: one coarser root level (dx = 8 M on\n"
        "# +-384 M) below the old root, every old level moved up by one, so the mesh inside\n"
        "# +-192 M (and the nest at the hole) is ES-1G's; basename es1gb. The table's\n"
        "# Painleve-Gullstrand exterior continues the data to the new faces. Executable:\n"
        "# release core-v0.4 (.work/build_gpu_v04/src/athena; lapse_leak is merged from\n"
        "# core/gauge). Predictions: g2runs/JOURNAL.md entry 1. Original header follows.\n#\n")
    return header + old_header + body


def v1gb():
    src = open(V1B).read()
    body, old_header = strip_header(src)
    body = rep(body, "basename  = v1b\n", "basename  = v1gb\n")
    body = rep(body, "chi_div_floor   = 1.0e-5\n",
               "chi_div_floor   = 1.0e-5\n")  # anchor check only
    anchor = "damp_kappa2     = 0.0\n"
    body = rep(body, anchor, anchor +
               "lapse_leak      = 0.5      # 1/T, T = 2 M (as ES-1G and ES-1GB)\n"
               "lapse_leak_alpha = 1.0     # reference lapse (as ES-1G)\n")
    header = (
        "# V-1GB (Track D, package g2runs): V-1B with the relaxed lapse of ES-1G, the vacuum\n"
        "# control of ES-1GB (same mesh, faces at +-384 M, same gauge). One change against\n"
        "# drift_controls/inputs/v1b_bnd384.athinput: <z4c> lapse_leak = 0.5,\n"
        "# lapse_leak_alpha = 1.0; basename v1gb. Built by g2runs/tools/make_inputs.py.\n"
        "# Executable: release core-v0.4. Predictions: g2runs/JOURNAL.md entry 1.\n"
        "# Original header of V-1B follows.\n#\n")
    return header + old_header + body


def main():
    check = "--check" in sys.argv
    for out, text, parent in ((OUT_ES, es1gb(), ES1G), (OUT_V, v1gb(), V1B)):
        if check:
            same = open(out).read() == text
            print(f"{os.path.basename(out)}: {'matches' if same else 'DIFFERS'}")
            if not same:
                sys.exit(1)
        else:
            open(out, "w").write(text)
        d = difflib.unified_diff(open(parent).read().splitlines(), text.splitlines(),
                                 os.path.basename(parent), os.path.basename(out), n=0,
                                 lineterm="")
        body = [l for l in d if not l.startswith(("+#", "-#"))]
        print("\n".join(body))
        print()


if __name__ == "__main__":
    main()
