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
CONTINUED = {   # as repro/continue/scripts/conts.json at commit e5581420 (2026-11-24 13:30 PST),
    # plus RSF256's 4th continuation (queue q0034, ended at tlim 14:23 PST), as ../conts_rsf256.json
    "RSF256": ["E-20261124-130529-da8c917", "E-20261124-201031-4c41e7b",
               "E-20261124-202134-0b1ce0c", "E-20261124-214913-5956891"],
    "RNC256": ["E-20261124-130629-61fe0b0"],
    "CL256U": ["E-20261124-130711-a5dec67", "E-20261124-201048-33a3a39"],
    "CL256S": ["E-20261124-130952-4be980b"],
    "AL2S": ["E-20261124-131359-49afe29"],
}
for _lab, _ids in CONTINUED.items():
    RUNS[_lab + "c"] = (_ids[-1], "", RUNS[_lab][2])
# RSF256's dumps 00001-00016 are read from its third continuation (00017-00034 from the fourth)
RUNS["RSF256b"] = ("E-20261124-202134-0b1ce0c", "", "sr")

# joined records of repro/continue (one line per cycle, the last written wins; join check run):
# label -> run id that holds <label>.sf.con.hst and <label>.sf.hst. RSF256 there ends at cycle 895.
JOINED = {lab: "E-20261124-212343-7e9c4b2" for lab in CONTINUED}
# RSF256 to cycle 1386: this package's join check (repro/continue's join_check.py with ../conts_rsf256.json)
JOINED["RSF256"] = "E-20261124-225720-444aecc"


def cont_dirs(label):
    return [os.path.join(SCR, rid) for rid in CONTINUED.get(label, [])]


def raw_con_paths(label):
    """The record of the original and of its continuations, in order (before the join)."""
    return [con_path(label)] + [os.path.join(d, base(label) + ".sf.con.hst")
                                for d in cont_dirs(label)]


def rundir(label):
    rid, sub, _ = RUNS[label]
    return os.path.join(SCR, rid, sub) if sub else os.path.join(SCR, rid)


def base(label):
    return RUNS[label][2]


def con_path(label):
    return os.path.join(rundir(label), base(label) + ".sf.con.hst")


def con_paths(label):
    """The record of the run: the joined file of repro/continue for a continued run, else the
    run's own file (read with figlib.read_con_joined either way)."""
    if label in JOINED:
        p = os.path.join(SCR, JOINED[label], label + ".sf.con.hst")
        if os.path.exists(p):
            return [p]
    return raw_con_paths(label)


def hst_path(label):
    return os.path.join(rundir(label), base(label) + ".sf.hst")


# analysis groups: list of (label, dumppass options)
GROUPS = {
    "usr256": [("USF256", [])],
    "sr256v6": [("P256v6", ["--save-modes"])],
    "ablation": [(lab, ["--dumps", "0,17", "--save-modes"]) for lab in ("AL0S", "AL1S", "RL1")]
    + [(lab, ["--dumps", "0,20", "--save-modes"])
       for lab in ("AL0U", "AL1U", "AL2U", "UL1", "U256ap")],
    "rungs": [(lab, []) for lab in ("C32S", "C64S", "C128S", "C32U", "C64U", "C128U")],
}
# USF256 again at the dumps of Fig. 6b (and N = 4.5) with the invariant Kt spectrum (kt_version 2)
GROUPS["usr256kt"] = [("USF256", ["--dumps", "0,3,5,8,11,14,18,22,40"])]
# and at N = 8.01 (dump 32), next to P1's last Fig. 6b curve at <N> = 7.95 (journal entry 7)
GROUPS["usr256kt8"] = [("USF256", ["--dumps", "32"])]
# SR ablation at t = 7.5 (dump 15), the last dump the cut AL2S wrote (it reached t = 7.53)
GROUPS["ablation75"] = [(lab, ["--dumps", "15", "--save-modes"]) for lab in ("AL0S", "AL1S", "AL2S")]
GROUPS["rsf256"] = [("RSF256", ["--dumps", "0"]),
                    ("RSF256b", ["--dumps", ",".join(str(i) for i in range(1, 17))]),
                    ("RSF256c", ["--save-modes"])]
GROUPS["cl256"] = [("CL256Sc", ["--last"])]
GROUPS["al2s"] = [("AL2Sc", ["--last", "--save-modes"])]
# bit check only, of what RSF256 has written so far (t = 0, 4.0, 5.0) against P256v6
GROUPS["rsf256bit"] = []
BITCHECK = {
    "usr256": [("USF256", 0, "U256ap", 0), ("USF256", 20, "U256ap", 10),
               ("USF256", 40, "U256ap", 20)],
    "rsf256": [("RSF256", 0, "P256v6", 0), ("RSF256b", 16, "P256v6", 8),
               ("RSF256c", 34, "P256v6", 17)],
    # (run E-20261124-213029-e937f69, when RSF256c named the third continuation 0b1ce0c)
    "rsf256bit": [("RSF256", 0, "P256v6", 0), ("RSF256b", 16, "P256v6", 8),
                  ("RSF256b", 20, "P256v6", 10)],
    "ablation75": [("AL2S", 0, "AL0S", 0)],
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
