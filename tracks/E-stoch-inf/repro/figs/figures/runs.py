"""Registry of the runs the figures read, and the analysis groups (one registered run each).

A label maps to (run id, subdirectory, dump basename). A run cut by its segment limit and continued
by package repro/continue is read as one run: its continuation's dumps are listed after the
original's (CONTINUED, filled in when repro/continue/HANDOFF.md names the continuation).

Usage (inside a registered run): runs.py GROUP OUTDIR [--workers W] [--fft-workers F]
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = "/data/haiyangw/nrpic/scratch/E-stoch-inf"

RUNS = {
    # repro/scope (release card build core-v0.6)
    "M64S": ("E-20261123-020704-2b99463", "M64S", "sr"),
    "M64U": ("E-20261123-020704-2b99463", "M64U", "usr"),
    "C32S": ("E-20261123-020704-2b99463", "C32S", "sr"),
    "C64S": ("E-20261123-020704-2b99463", "C64S", "sr"),
    "C128S": ("E-20261123-020704-2b99463", "C128S", "sr"),
    "C32U": ("E-20261123-020704-2b99463", "C32U", "usr"),
    "C64U": ("E-20261123-020704-2b99463", "C64U", "usr"),
    "C128U": ("E-20261123-020704-2b99463", "C128U", "usr"),
    "USF256": ("E-20261123-021204-2f573ec", "", "usr"),
    "RSF256": ("E-20261123-035925-8439d79", "", "sr"),
    "UL1": ("E-20261123-040126-2d0323c", "", "usr"),
    "RL1": ("E-20261123-040327-ccae634", "", "sr"),
    "RNC256": ("E-20261123-045030-c20bcb3", "", "sr"),
    "CL256U": ("E-20261123-065855-265732a", "", "usr"),
    "CL256S": ("E-20261123-090727-4b6e5a5", "", "sr"),
    # earlier registered runs reused (g2prod; release build)
    "P256v6": ("E-20261121-202935-31520bc", "P256", "sr"),
    "U256ap": ("E-20261121-211214-0377aab", "", "usr"),
    # repro/ablation (branch build core/noise-level2, decision 0031 item 3)
    "AL0S": ("E-20261123-153347-18e7c21", "", "sr256_l0m"),
    "AL1S": ("E-20261123-183822-4abbcae", "", "sr256_l1m"),
    "AL2S": ("E-20261123-152119-38957ba", "", "sr256_l2"),
    "AL0U": ("E-20261123-164235-49b0945", "", "usr256_l0m"),
    "AL1U": ("E-20261123-192948-348e2e5", "", "usr256_l1m"),
    "AL2U": ("E-20261123-153146-d965002", "", "usr256_l2"),
}

# continuation runs of package repro/continue (label -> list of run ids), read as the same run:
# their dumps and record lines come after the original's (one line per cycle, the last written wins)
CONTINUED = {}


def cont_dirs(label):
    return [os.path.join(SCR, rid) for rid in CONTINUED.get(label, [])]


def rundir(label):
    rid, sub, _ = RUNS[label]
    return os.path.join(SCR, rid, sub) if sub else os.path.join(SCR, rid)


def base(label):
    return RUNS[label][2]


def con_path(label):
    return os.path.join(rundir(label), base(label) + ".sf.con.hst")


def con_paths(label):
    """The record of the run and of its continuations, in order."""
    return [con_path(label)] + [os.path.join(d, base(label) + ".sf.con.hst")
                                for d in cont_dirs(label)]


def hst_path(label):
    return os.path.join(rundir(label), base(label) + ".sf.hst")


# analysis groups: list of (label, dumppass options)
GROUPS = {
    "usr256": [("USF256", [])],
    "sr256v6": [("P256v6", [])],
    "ablation": [(lab, ["--dumps", "0,17", "--save-modes"]) for lab in ("AL0S", "AL1S", "RL1")]
    + [(lab, ["--dumps", "0,20", "--save-modes"])
       for lab in ("AL0U", "AL1U", "AL2U", "UL1", "U256ap")],
    "p256final": [("P256v6", ["--dumps", "17", "--save-modes"])],
    "rungs": [(lab, []) for lab in ("C32S", "C64S", "C128S", "C32U", "C64U", "C128U")],
}
BITCHECK = {
    "usr256": [("USF256", 0, "U256ap", 0), ("USF256", 20, "U256ap", 10),
               ("USF256", 40, "U256ap", 20)],
    "ablation": [("AL0S", 0, "AL1S", 0), ("AL0S", 0, "P256v6", 0), ("AL0U", 0, "AL1U", 0),
                 ("AL0U", 0, "AL2U", 0), ("AL0U", 0, "U256ap", 0), ("AL0S", 0, "RL1", 0),
                 ("AL0U", 0, "UL1", 0)],
}


def dump(label, i):
    return os.path.join(rundir(label), f"{base(label)}.sf.{i:05d}.dump")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("group")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--fft-workers", type=int, default=2)
    args = ap.parse_args()
    py = sys.executable
    for lab, opts in GROUPS[args.group]:
        cmd = [py, os.path.join(HERE, "dumppass.py"), "--run", rundir(lab), "--base", base(lab),
               "--label", lab, "--out", args.out, "--workers", str(args.workers),
               "--fft-workers", str(args.fft_workers)] + opts
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)
    if args.group in BITCHECK:
        pairs = [f"{dump(a, i)}:{dump(b, j)}" for a, i, b, j in BITCHECK[args.group]]
        subprocess.run([py, os.path.join(HERE, "bitcheck.py"), "--out",
                        os.path.join(args.out, f"bitcheck_{args.group}.json")] + pairs, check=True)
    with open(os.path.join(args.out, f"group_{args.group}.json"), "w") as fp:
        json.dump(dict(group=args.group, runs={lab: RUNS[lab] for lab, _ in GROUPS[args.group]},
                       continued=CONTINUED), fp, indent=1)


if __name__ == "__main__":
    main()
