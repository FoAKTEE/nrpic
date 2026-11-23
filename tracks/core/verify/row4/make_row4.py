#!/usr/bin/env python3
"""Initial data of ladder row 4 on the M/8 mesh (batch 5): kicked members and their controls.

For every y_c: the protocol of wave 2 (`../ladder2/make_ics.py`: 10^4 stratified particles,
seed 1, equilibrium table, --no-consistent-table) with the one-percent uniform inward kick
(member, vp0p01) and without it (control: same seed, same positions, no kick). Writes into
OUT (default $NRPIC_RUN_DIR):
  st_<tag>_kick/, st_<tag>_ctrl/   make_ic.py output (.nrp, .tab, make_ic.out)
  models.json                      turning point and E_b/M_0, R/M, alpha_c, z_c of every model
  chain_args.txt                   per run: name and the athena arguments for the chain launcher
  sha256.txt                       checksums of every file written

    python3 make_row4.py [--out DIR] [--yc 0.605 0.680 0.755]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(WT / "python"))
from nrpic import st_cluster as stc  # noqa: E402

MAKE_IC = WT / "problems" / "ic" / "make_ic.py"


def tag(y):
    return f"yc{y:.3f}".replace(".", "p")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gen(out, y, vpert, kind):
    d = out / f"st_{tag(y)}_{kind}"
    d.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(MAKE_IC), "st", "--yc", f"{y}", "--N", "10000",
           "--sampler", "stratified", "--seed", "1", "--vpert", f"{vpert}",
           "--no-consistent-table", "--out", str(d)]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    (d / "make_ic.out").write_text(" ".join(cmd) + "\n" + r.stdout + r.stderr)
    return sorted(d.glob("*.nrp"))[0], sorted(d.glob("*.tab"))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--yc", type=float, nargs="+", default=[0.605, 0.680, 0.755])
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    tp = {k: float(v) for k, v in stc.binding_energy_maximum().items()}
    models, args = {}, []
    for y in a.yc:
        g = stc.st_global(y)
        models[tag(y)] = dict(yc=y, Eb_over_M0=float(g["Eb_over_M0"]), R_over_M=float(g["R_over_M"]),
                              alpha_c=float(g["alpha_c"]), zc=float(g["zc"]))
        for vpert, kind in ((0.01, "kick"), (0.0, "ctrl")):
            nrp, tab = gen(out, y, vpert, kind)
            models[tag(y)][kind] = dict(nrp=str(nrp), tab=str(tab))
            args.append(f"st_{tag(y)}_{kind} particles/particle_file={nrp} problem/comp0_file={tab}")
    (out / "models.json").write_text(json.dumps(dict(turning_point=tp, models=models), indent=1))
    (out / "chain_args.txt").write_text("\n".join(args) + "\n")
    with open(out / "sha256.txt", "w") as f:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p.name != "sha256.txt" and ".nrpic" not in p.parts:
                f.write(f"{sha(p)}  {p.relative_to(out)}\n")
    print(json.dumps(tp))
    for k, v in models.items():
        print(k, f"alpha_c={v['alpha_c']:.4f} Eb/M0={v['Eb_over_M0']:.6f} R/M={v['R_over_M']:.3f} "
                 f"zc={v['zc']:.4f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
