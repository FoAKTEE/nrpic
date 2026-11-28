#!/usr/bin/env python3
"""Write the mesh members of SCOPE_G3.md section 3 as the scope describes them (for block counts only).

G-8   : g2long/inputs/esfl.athinput unchanged (the ES-FL hierarchy, level 7 to +-6 M).
G-16  : G-8 plus <refined_region6> level 8 over +-5.9 M (scope table, "refined region of level 8 +-5.9 M").
G-12  : G-8 with the root at 144 cells over +-768 M, blocks of 24 (scope table).
G-16b : G-16 with blocks of 12 cells (a cheaper form, not in the scope; informational).
Only the mesh sections matter: the decks are read with `athena -m` (mesh structure, no physics).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACK = HERE.parents[2]
SRC = TRACK / "g2long" / "inputs" / "esfl.athinput"
OUT = HERE.parent / "decks"


def set_block(text, block, key, value):
    pat = re.compile(r"(<%s>.*?\n)(%s\s*=\s*)([^\n#]*)" % (re.escape(block), re.escape(key)), re.S)
    new, n = pat.subn(lambda m: m.group(1) + m.group(2) + str(value), text, count=1)
    if n != 1:
        raise SystemExit(f"{block}/{key} not found")
    return new


def main():
    OUT.mkdir(exist_ok=True)
    base = SRC.read_text()
    region8 = ("\n<refined_region6>\nlevel = 8\nx1min = -5.9\nx1max = 5.9\nx2min = -5.9\nx2max = 5.9\n"
               "x3min = -5.9\nx3max = 5.9\n")
    # insert the level-8 region right after refined_region5
    i = base.index("<refined_region5>")
    j = base.index("\n<", i + 1)
    g16 = base[:j] + "\n" + region8 + base[j:]
    decks = {"g8": base, "g16": g16}
    g12 = base
    for ax in ("nx1", "nx2", "nx3"):
        g12 = set_block(g12, "mesh", ax, 144)
    decks["g12"] = g12
    g16b = g16
    for ax in ("nx1", "nx2", "nx3"):
        g16b = set_block(g16b, "meshblock", ax, 12)
    decks["g16b"] = g16b
    for name, txt in decks.items():
        txt = set_block(txt, "job", "basename", name)
        hdr = f"# scope_review deck {name}: written by tools/make_decks.py from {SRC.relative_to(TRACK)}; mesh only (athena -m)\n"
        (OUT / f"{name}.athinput").write_text(hdr + txt)
        print(OUT / f"{name}.athinput")
    return 0


if __name__ == "__main__":
    sys.exit(main())
