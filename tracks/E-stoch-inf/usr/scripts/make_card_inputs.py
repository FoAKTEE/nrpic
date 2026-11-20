#!/usr/bin/env python3
"""Card inputs and lists of the USR case (package tracks/E-stoch-inf/usr, wave 3, JOURNAL
entry 9): derived from the processor inputs written by make_inputs.py, which stay unchanged.

    python3 make_card_inputs.py            (from usr/scripts; writes into ../inputs)

Changes against usr_base.athinput / usr_256.athinput, nothing else:
- dump_constraints = true (H, M_i, E in the dumps: odd/even split with the box mean removed);
- con_signed = true (core_scalar-3: signed means <H>, <M_i> and the record of H' = H - <H>);
- dump_dt = tlim/40 (64^3) or tlim/20 (128^3, 256^3): the last dump falls on N_f = N* + 10
  itself (the driver shortens the last step to tlim; dumps are written at the first step
  with t >= n dump_dt (1 - 1e-12), scalar_field.cpp:381 on core/scalar-2), and every run of
  a pair has the same tlim and dump_dt.
Lists: card_g1.list (ladder 64^3, 128^3 at nmax2 = 64 with +-1 pairs and the +-1/2 pair at
128^3), card_u256.list (production set-up of P1), card_u256m.list (its mirror).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.abspath(os.path.join(HERE, "..", "inputs"))
REL = "tracks/E-stoch-inf/usr/inputs"
TLIM = 10.437508874065651        # results/usr_reference.json: t_code_end


def derive(src, dst, note, dump_dt):
    txt = open(os.path.join(INP, src)).read()
    txt = re.sub(r"(# Courant 0.25 \(SCOPE 4 item 1\)\.).*\n", r"\1 " + note + "\n", txt, count=1)
    txt = re.sub(r"^dump_constraints = false$", "dump_constraints = true", txt, flags=re.M)
    txt = re.sub(r"^dump_dt( *)= .*$", lambda m: f"dump_dt{m.group(1)}= {dump_dt!r}", txt,
                 flags=re.M)
    txt = re.sub(r"^(noise_mode_scale = .*)$", r"\1\ncon_signed       = true", txt, flags=re.M)
    assert "dump_constraints = true" in txt and "con_signed" in txt
    open(os.path.join(INP, dst), "w").write(txt)
    return dst


def mesh(n):
    return " ".join(f"{b}/nx{i}={n}" for b in ("mesh", "meshblock") for i in (1, 2, 3))


def main():
    base = derive("usr_base.athinput", "usr_card.athinput",
                  "Card ladder of JOURNAL entry 9 (mesh, nmax2, mode file, scale and dump_dt "
                  "set in the lists).", TLIM / 40)
    big = derive("usr_256.athinput", "usr_256s.athinput",
                 "Production set-up of P1 (256^3, k_max = 64 dk), card run of JOURNAL entry 9.",
                 TLIM / 20)
    mf = f"/data/haiyangw/nrpic/wt/E-stoch-inf/{REL}/modes_usr_n64.txt"
    rows = []
    for name, n, s in (("U64p", 64, 1.0), ("U64m", 64, -1.0), ("U128p", 128, 1.0),
                       ("U128m", 128, -1.0), ("U128hp", 128, 0.5), ("U128hm", 128, -0.5)):
        dd = TLIM / 40 if n == 64 else TLIM / 20
        rows.append(f"{name} {REL}/{base} {mesh(n)} scalar_field/noise_nmax2=64 "
                    f"scalar_field/noise_mode_file={mf} scalar_field/noise_mode_scale={s!r} "
                    f"scalar_field/dump_dt={dd!r}")
    head = ("# USR (inflection) case on one card, group 1 of JOURNAL entry 9: ladder 64^3, 128^3 at\n"
            "# nmax2 = 64 (k_max/dk = 8), pairs s = +-1 and the halving pair s = +-1/2 at 128^3.\n"
            "# Written by scripts/make_card_inputs.py. Executable core_scalar-3 (con_signed).\n")
    open(os.path.join(INP, "card_g1.list"), "w").write(head + "\n".join(rows) + "\n")
    for tag, s in (("u256", 1.0), ("u256m", -1.0)):
        name = "U256" if s > 0 else "U256m"
        line = f"{name} {REL}/{big} scalar_field/noise_mode_scale={s!r}"
        open(os.path.join(INP, f"card_{tag}.list"), "w").write(
            f"# USR case, production set-up of P1 (256^3, nmax2 = 4096), alone in one job "
            f"(--wall 00:58:00), JOURNAL entry 9.\n# Written by scripts/make_card_inputs.py.\n"
            + line + "\n")
    print("wrote", base, big, "card_g1.list card_u256.list card_u256m.list")


if __name__ == "__main__":
    main()
