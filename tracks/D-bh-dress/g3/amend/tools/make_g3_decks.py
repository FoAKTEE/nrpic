#!/usr/bin/env python3
"""Write the G3 decks of the amended scope (SCOPE_G3.md, amendment A1 of 2026-11-27) from EG8's deck.

G-8   (g3g8.athinput)      : excguard/inputs/esflg8.athinput with tlim 400 M, FK's excision remedy
                             (initial_radius_0 = 1.6, ah_exc_max_growth = 4.0: guard radius 6.4 M, verified
                             to 399.5 M by g2long entry 19), z4c slices every 5 M (snapshots every 25 M fall on
                             a slice), basename g3g8.
G-12u (g3g12u.athinput)    : G-8 with the root at 144 cells and blocks of 36: the same 456 blocks and level
                             extents, cell size 2/3 of G-8 everywhere (run D-20261128-020346-c4079e9).
G-16u (g3g16u.athinput)    : G-8 with the root at 192 cells and blocks of 48: cell size 1/2 everywhere.
*_t2.athinput              : the same decks with tlim 2 M, for the card timing runs (memory, seconds per M,
                             finder at t = 0) that replace a processor smoke test of the finer decks.
A6 (2026-11-28, decision 0051 item 3): g3g6u, g3g6u_t2 (root 72, blocks of 18) and the null pair at M/6,
n6es and n6v (function write_m6).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACK = HERE.parents[2]
SRC = TRACK / "excguard" / "inputs" / "esflg8.athinput"
OUT = HERE.parent / "decks"


def rep(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f"expected one occurrence of {old!r}")
    return text.replace(old, new)


def set_key(text, block, key, value):
    pat = re.compile(r"(<%s>[^<]*?\n)(%s\s*=\s*)([^\n#]*)" % (re.escape(block), re.escape(key)), re.S)
    new, n = pat.subn(lambda m: m.group(1) + m.group(2) + str(value), text, count=1)
    if n != 1:
        raise SystemExit(f"{block}/{key} not found")
    return new


def main():
    OUT.mkdir(exist_ok=True)
    src = SRC.read_text()
    body = src[src.index("<comment>"):]
    body = rep(body, "tlim       = 260.0\n", "tlim       = 400.0\n")
    body = rep(body, "initial_radius_0  = 0.8\n", "initial_radius_0  = 1.6\n")
    body = rep(body, "ah_exc_max_growth = 8.0\n", "ah_exc_max_growth = 4.0\n")
    body = rep(body, "variable  = z4c\nslice_x3  = 0.001\ndt        = 10.0\n",
               "variable  = z4c\nslice_x3  = 0.001\ndt        = 5.0\n")
    decks = {"g3g8": (body, "G-8: M/8 (root 96, blocks of 24)")}
    b12 = body
    b16 = body
    for ax in ("nx1", "nx2", "nx3"):
        b12 = set_key(b12, "mesh", ax, 144)
        b12 = set_key(b12, "meshblock", ax, 36)
        b16 = set_key(b16, "mesh", ax, 192)
        b16 = set_key(b16, "meshblock", ax, 48)
    decks["g3g12u"] = (b12, "G-12u: M/12 everywhere (root 144, blocks of 36)")
    decks["g3g16u"] = (b16, "G-16u: M/16 everywhere (root 192, blocks of 48)")
    for name, (txt, what) in list(decks.items()):
        decks[name + "_t2"] = (rep(txt, "tlim       = 400.0\n", "tlim       = 2.0\n"), what + ", timing run to 2 M")
    for name, (txt, what) in decks.items():
        base = name.replace("_t2", "")
        txt = set_key(txt, "job", "basename", base)
        hdr = (f"# {name}: {what}. Track D, G3 (scope/SCOPE_G3.md amendment A1, 2026-11-27).\n"
               "# Written by tracks/D-bh-dress/g3/amend/tools/make_g3_decks.py from excguard/inputs/esflg8.athinput:\n"
               "# tlim 400 M, initial_radius_0 1.6 with ah_exc_max_growth 4 (FK's guard radius 6.4 M), z4c slices every 5 M.\n"
               "# Executable: release core-v0.8 (.work/build_gpu_v08/src/athena). EG8's header follows.\n#\n")
        head = src[:src.index("<comment>")]
        (OUT / f"{name}.athinput").write_text(hdr + head + txt)
        print(OUT / f"{name}.athinput")
    write_m6(body, src)
    return 0


def write_m6(body, src):
    """Decks of amendment A6 (decision 0051 item 3, 2026-11-28): the coarser uniform member G-6u and
    the null-test pair at M/6. Root 72 cells over +-768 M with blocks of 18: G-8's 456 blocks and level
    extents with cell size 4/3 of G-8's everywhere (counted with athena -m before any run).
    G-6u   (g3g6u.athinput, g3g6u_t2.athinput): G-8's deck with root 72 and blocks of 18.
    N6-ES, N6-V (n6es.athinput, n6v.athinput): g2long's ES-1L and V-1L decks (the null test of G2 at
    M/8) with root 72 and blocks of 18, tlim 300 M, the polished finder with its diagnostics
    (polish_iterations_0 = 100, diagnostics = true); everything else as G2's pair.
    Executable of every A6 deck: release core-v0.9."""
    head = src[:src.index("<comment>")]
    b6 = body
    for ax in ("nx1", "nx2", "nx3"):
        b6 = set_key(b6, "mesh", ax, 72)
        b6 = set_key(b6, "meshblock", ax, 18)
    decks = {"g3g6u": (b6, "G-6u: M/6 everywhere (root 72, blocks of 18)"),
             "g3g6u_t2": (rep(b6, "tlim       = 400.0\n", "tlim       = 2.0\n"),
                          "G-6u: M/6 everywhere (root 72, blocks of 18), timing run to 2 M")}
    for name, (txt, what) in decks.items():
        txt = set_key(txt, "job", "basename", "g3g6u")
        hdr = (f"# {name}: {what}. Track D, G3 (scope/SCOPE_G3.md amendment A6, 2026-11-28; decision 0051 item 3).\n"
               "# Written by tracks/D-bh-dress/g3/amend/tools/make_g3_decks.py from excguard/inputs/esflg8.athinput:\n"
               "# G-8's deck (tlim 400 M, initial_radius_0 1.6, ah_exc_max_growth 4, z4c slices every 5 M) with root 72, blocks of 18.\n"
               "# Executable: release core-v0.9 (.work/build_gpu_v09/src/athena). EG8's header follows.\n#\n")
        (OUT / f"{name}.athinput").write_text(hdr + head + txt)
        print(OUT / f"{name}.athinput")
    g2 = TRACK / "g2long" / "inputs"
    for name, srcname, what in (("n6es", "es1l", "N6-ES: ES-1L (vacuum bubble in expanding dust) at M/6"),
                                ("n6v", "v1l", "N6-V: V-1L (vacuum control) at M/6")):
        s = (g2 / f"{srcname}.athinput").read_text()
        h0, t = s[:s.index("<comment>")], s[s.index("<comment>"):]
        for ax in ("nx1", "nx2", "nx3"):
            t = set_key(t, "mesh", ax, 72)
            t = set_key(t, "meshblock", ax, 18)
        t = rep(t, "tlim       = 500.0\n", "tlim       = 300.0\n")
        t = rep(t, "mass_tol_0        = 1.0e-5\n", "mass_tol_0        = 1.0e-5\npolish_iterations_0 = 100\n")
        t = rep(t, "verbose           = false\n", "verbose           = false\ndiagnostics       = true\n")
        t = set_key(t, "job", "basename", name)
        hdr = (f"# {name}: {what}. Track D, G3 (scope/SCOPE_G3.md amendment A6, 2026-11-28; decision 0051 item 3).\n"
               f"# Written by tracks/D-bh-dress/g3/amend/tools/make_g3_decks.py from g2long/inputs/{srcname}.athinput:\n"
               "# root 72 and blocks of 18 (M/6 at the puncture), tlim 300 M, polish_iterations_0 = 100, diagnostics = true.\n"
               "# Executable: release core-v0.9 (.work/build_gpu_v09/src/athena). G2's header follows.\n#\n")
        (OUT / f"{name}.athinput").write_text(hdr + h0 + t)
        print(OUT / f"{name}.athinput")


if __name__ == "__main__":
    sys.exit(main())
