#!/usr/bin/env python3
"""Input of the excision-guard test EG8 (excguard JOURNAL entry 1), from g2long/inputs/esfl.athinput.

Changes from ES-FL (run D-20261121-203150-15f2bad), each named in the journal:
  basename       esfl -> esflg8
  tlim           500 -> 260 M (40 M past ES-FL's end of horizon excision at 219.5 M)
  <particles>    ah_exc_max_growth = 8.0 (guard radius 8 x initial_radius_0 = 6.4 M, as FK's 4 x 1.6)
  <fastflow>     polish_iterations_0 = 100 (converged finder of core-v0.8, mass_tol_0 = 1e-5 kept),
                 diagnostics = true (status file <base>.horizon_status_0.txt)
  <output2> rst  dt 50 -> 25 M (a restart file about every 8 min of card time)
initial_radius_0 = 0.8 is kept (the radius ES-FL used). Mesh, gauge (plain 1+log, Gamma-driver
shift_eta 2, no lapse_leak), step (cfl_number 0.25), data and other outputs are ES-FL's.
Executable: release core-v0.8 (.work/build_gpu_v08/src/athena).

Writes excguard/inputs/esflg8.athinput.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRACK = os.path.dirname(PKG)
PARENT = os.path.join(TRACK, "g2long", "inputs", "esfl.athinput")
OUT = os.path.join(PKG, "inputs", "esflg8.athinput")


def rep(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"expected 1 occurrence of {old!r}, found {n}")
    return text.replace(old, new)


def main():
    body = open(PARENT).read()
    body = rep(body, "basename  = esfl\n", "basename  = esflg8\n")
    body = rep(body, "tlim       = 500.0\n", "tlim       = 260.0\n")
    body = rep(body, "initial_radius_0  = 0.8\n", "initial_radius_0  = 0.8\n")
    body = rep(body, "mass_tol_0        = 1.0e-5\n",
               "mass_tol_0        = 1.0e-5\npolish_iterations_0 = 100\n")
    body = rep(body, "verbose           = false\n", "verbose           = false\ndiagnostics       = true\n")
    body = rep(body, "ah_exc_factor  = 0.8\n", "ah_exc_factor  = 0.8\nah_exc_max_growth = 8.0\n")
    body = rep(body, "file_type = rst\ndt        = 50.0\n", "file_type = rst\ndt        = 25.0\n")
    head = ("# esflg8 (EG8): ES-FL with the excision guard of core-v0.8 at 8 x initial_radius_0 = 6.4 M and\n"
            "# the converged finder (polish_iterations_0 = 100, mass_tol_0 = 1e-5, diagnostics = true); tlim 260 M,\n"
            "# restart every 25 M (Track D, package excguard, entry 1).\n"
            "# Built by tracks/D-bh-dress/excguard/tools/make_input.py from g2long/inputs/esfl.athinput.\n"
            "# Executable: release core-v0.8 (.work/build_gpu_v08/src/athena). Gauge plain 1+log, no lapse_leak.\n"
            "# Parent header follows.\n#\n")
    with open(OUT, "w") as f:
        f.write(head + body)
    print(OUT)


if __name__ == "__main__":
    main()
