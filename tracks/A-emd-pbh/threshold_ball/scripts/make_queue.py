#!/usr/bin/env python3
"""Writes the sequencer queue (queue.txt) and the batch list of the A-mesh members
(lists/A.list) of package threshold_ball from the data run's prep_summary.json.

Members (DESIGN.md section 2): mesh B (finest cells M/32, deck conv_ball/decks/nest32_L32,
outer boundary 32 M) for every contrast; mesh A (M/16, nest16_L32) and C (M/64, nest64_L32)
for the bracket members; conv_ball's C-R1.25 (nest64_L16, executable core_gauge, its series).

    python3 tracks/A-emd-pbh/threshold_ball/scripts/make_queue.py --prep <data run dir>
"""
import argparse
import json
import os
import shlex

PKG = "tracks/A-emd-pbh/threshold_ball"
DECKS = "tracks/A-emd-pbh/threshold_ball/decks"
DECKS_CONV = "tracks/A-emd-pbh/conv_ball/decks"
V06 = "/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena"
GAUGE = "/data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu"
T_END = 45.0          # end time of the threshold definition (DESIGN.md section 1)

# name, data set, mesh, tlim, card-hours requested (chain segments = floor(h / 59 min))
B_MEMBERS = [("B-d0.42", "dc0p42", 51.0, 2.0), ("B-d0.40", "dc0p4", 54.0, 2.0),
             ("B-d0.45", "dc0p45", 47.0, 2.0), ("B-d0.50", "dc0p5", 42.0, 2.0),
             ("B-d1.00", "dc1p0", 23.0, 1.0), ("B-d0.70", "dc0p7", 31.0, 1.0),
             ("B-d0.35", "dc0p35", 62.0, 2.0), ("B-d0.20", "dc0p2", 70.0, 2.0)]
A_MEMBERS = [("A-d0.42", "dc0p42", 51.0), ("A-d0.40", "dc0p4", 54.0)]
C_MEMBER = ("C-d0.42", "dc0p42", 51.0, 14.0)


def q(x):
    return shlex.quote(str(x))


def overrides(ent, lattice, tlim):
    lat = ent["lattices"][lattice]
    pre = ent["dir"]
    tab = os.path.join(pre, ent["stem"] + ".tab")
    nrp = os.path.join(pre, lattice, f"{ent['stem']}_{lattice}_track.nrp")
    tau_ah, tau_ta = ent["tau_AH"], ent["tau_ta"]
    start = round(max(2.0, 0.5 * min(tau_ah, tlim)) * 4) / 4
    f = [round(x * 4) / 4 for x in (tau_ta, tau_ah - 2.0, tau_ah, tau_ah + 4.0)]
    f = [min(x, tlim) for x in f]
    return [f"problem/comp0_file={tab}", f"particles/particle_file={nrp}",
            f"particles/traj_ntrack={lat['n_track']}", f"time/tlim={tlim}",
            "fastflow/hmean_tol_0=1e30", "fastflow/diagnostics=true", "fastflow/find_every=8",
            f"fastflow/start_time_0={start}"] + [f"particles/field_time{i + 1}={x}" for i, x in enumerate(f)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    a = ap.parse_args()
    with open(os.path.join(a.prep, "prep_summary.json")) as f:
        S = json.load(f)
    for k, v in S.items():
        v["dir"] = os.path.join(a.prep, k)
    lines = ["# threshold_ball queue (scripts/make_queue.py; data run " + os.path.basename(a.prep) + ").",
             "# One line per card run: the arguments of harness/bin/nrpic-run submit. Read by scripts/sequencer.sh."]
    pre = f"--kind scouting --gate G2 --package {PKG} --parent {os.path.basename(a.prep)}"
    for name, ds, tlim, gh in B_MEMBERS[:2]:
        e = S[ds]
        side = "BH" if e["tau_AH"] <= T_END else "NO-BH (late) at t_end = 45, horizon expected later"
        purp = (f"threshold_ball {name}: compensated top-hat ball delta_c = {name[3:]}, mesh B (finest M/32, outer 32 M), "
                f"v0.6 release, relaxed 1+log (lapse_leak 8), to t = {tlim}; exact tau_AH = {e['tau_AH']:.3f}; expected {side} "
                f"(JOURNAL entry 1)")
        lines.append(f"{pre} --launcher chain --exe {V06} --gpu-hours {gh} --purpose {q(purp)} -- "
                     f"{DECKS}/nest32_L32.athinput " + " ".join(q(x) for x in overrides(e, "nestB", tlim)))
    # A-mesh pair in one batch job (about 10 min)
    lines.append(f"{pre} --launcher batch --exe {V06} --wall 00:40:00 --gpu-hours 0.67 --list {PKG}/lists/A.list "
                 f"--purpose " + q("threshold_ball A-d0.42, A-d0.40: the bracket members on mesh A (finest M/16, outer 32 M), "
                                   "v0.6 release (JOURNAL entry 1)"))
    for name, ds, tlim, gh in B_MEMBERS[2:]:
        e = S[ds]
        side = "BH" if e["tau_AH"] <= T_END else "NO-BH (late) at t_end = 45"
        purp = (f"threshold_ball {name}: compensated top-hat ball delta_c = {name[3:]}, mesh B (finest M/32, outer 32 M), "
                f"v0.6 release, relaxed 1+log (lapse_leak 8), to t = {tlim}; exact tau_AH = {e['tau_AH']:.3f}; expected {side} "
                f"(JOURNAL entry 1)")
        lines.append(f"{pre} --launcher chain --exe {V06} --gpu-hours {gh} --purpose {q(purp)} -- "
                     f"{DECKS}/nest32_L32.athinput " + " ".join(q(x) for x in overrides(e, "nestB", tlim)))
    # conv_ball's ball-radius leg at the finest mesh (its executable and deck)
    r = S["R1p25"]
    latc = r["lattices"]["nestC"]
    purp = ("conv_ball member C-R1.25 (queued by threshold_ball): data set 3 core in a ball 1.25 times larger, nested mesh C "
            "(finest M/64, outer 16 M), core_gauge executable as the conv_ball series, t = 0 -> 16 (threshold_ball JOURNAL entry 1)")
    lines.append(f"{pre} --launcher chain --exe {GAUGE} --gpu-hours 4 --purpose {q(purp)} -- {DECKS_CONV}/nest64_L16.athinput "
                 + " ".join(q(x) for x in [f"problem/comp0_file={os.path.join(r['dir'], r['stem'] + '.tab')}",
                                           f"particles/particle_file={os.path.join(r['dir'], 'nestC', r['stem'] + '_nestC_track.nrp')}",
                                           f"particles/traj_ntrack={latc['n_track']}"]))
    name, ds, tlim, gh = C_MEMBER
    e = S[ds]
    purp = (f"threshold_ball {name}: delta_c = 0.42 on mesh C (finest M/64, outer 32 M), v0.6 release, to t = {tlim}; "
            f"exact tau_AH = {e['tau_AH']:.3f}; third mesh of the bracket's BH member (JOURNAL entry 1)")
    lines.append(f"{pre} --launcher chain --exe {V06} --gpu-hours {gh} --purpose {q(purp)} -- "
                 f"{DECKS}/nest64_L32.athinput " + " ".join(q(x) for x in overrides(e, "nestC", tlim)))
    with open(os.path.join(PKG, "queue.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    os.makedirs(os.path.join(PKG, "lists"), exist_ok=True)
    with open(os.path.join(PKG, "lists", "A.list"), "w") as f:
        f.write("# threshold_ball: bracket members on mesh A (make_queue.py)\n")
        for name, ds, tlim in A_MEMBERS:
            f.write(f"{name} {DECKS}/nest16_L32.athinput -t 00:15:00 "
                    + " ".join(overrides(S[ds], "nestA", tlim)) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
