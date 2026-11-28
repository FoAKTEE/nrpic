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
    return 0


if __name__ == "__main__":
    sys.exit(main())
