#!/usr/bin/env python3
"""Card lists of the G2 series (package conv_ball, Track A, wave 3; DESIGN.md section 3):
lists/job1.list and lists/job3.list for `nrpic-run submit --launcher batch` (lines
`<name> <athinput> [athena args...]`), and lists/C.args, the deck and arguments of the chain
of member C. Data: the prep runs named below (registered).

    make_lists.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DECKS = os.path.join(PKG, "decks")
SCR = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
PREP = {"3": os.path.join(SCR, "A-20261121-075356-1ad4c81"),      # data set 3, nested lattices
        "1.25": os.path.join(SCR, "A-20261121-075401-1412a08"),   # ball 1.25 times larger
        "1.35": os.path.join(SCR, "A-20261121-075404-ac51b7e")}   # ball 1.35 times larger

# member: (deck, data, lattice)
MEMBERS = {
    "A": ("nest16_L16", "3", "nestA"),
    "B": ("nest32_L16", "3", "nestB"),
    "C": ("nest64_L16", "3", "nestC"),
    "A-N8": ("nest16_L16", "3", "nestA8"),
    "A-N64": ("nest16_L16", "3", "nestA64"),
    "B-N8": ("nest32_L16", "3", "nestB8"),
    "A-R1.25": ("nest16_L16", "1.25", "nestA"),
    "A-R1.35": ("nest16_L16", "1.35", "nestA"),
    "B-R1.25": ("nest32_L16", "1.25", "nestB"),
    "B-R1.35": ("nest32_L16", "1.35", "nestB"),
    "A-L32": ("nest16_L32", "3", "nestA"),
    "B-L32": ("nest32_L32", "3", "nestB"),
}
# job 3 of DESIGN.md split after job 1 (JOURNAL entry 6): particles cost about 2e-7 card-seconds per
# particle and step (A-N8 against A), three times the model, so B-N8 and A-N64 fill one job; B-R1.35
# is added and B-L32 goes last (A-L32 equalled A to 1e-7; the ball-radius leg is the open one)
JOBS = {"job1": ["A", "B", "A-L32", "A-R1.25", "A-R1.35", "A-N8"],
        "job3a": ["B-N8", "A-N64"],
        "job3b": ["B-R1.25", "B-R1.35", "B-L32"]}


def args_of(name):
    deck, data, lat = MEMBERS[name]
    prep = PREP[data]
    tr = json.load(open(os.path.join(prep, lat, "tracked.json")))
    ex = json.load(open(os.path.join(prep, "exact.json")))
    tab = os.path.join(prep, ex["table"])
    assert os.path.exists(tab) and os.path.exists(tr["particle_file"])
    return (os.path.join(DECKS, deck + ".athinput"),
            [f"problem/comp0_file={tab}", f"particles/particle_file={tr['particle_file']}",
             f"particles/traj_ntrack={tr['n_track']}"], os.path.join(prep, lat))


def main():
    os.makedirs(os.path.join(PKG, "lists"), exist_ok=True)
    index = {}
    for job, names in JOBS.items():
        with open(os.path.join(PKG, "lists", job + ".list"), "w") as f:
            f.write(f"# conv_ball {job} (DESIGN.md section 3); written by scripts/make_lists.py\n")
            for n in names:
                deck, args, prep = args_of(n)
                f.write(" ".join([n, deck] + args) + "\n")
                index[n] = dict(job=job, deck=deck, args=args, prep=prep)
    deck, args, prep = args_of("C")
    with open(os.path.join(PKG, "lists", "C.args"), "w") as f:
        f.write(" ".join([deck] + args) + "\n")
    index["C"] = dict(job="job2 (chain)", deck=deck, args=args, prep=prep)
    with open(os.path.join(PKG, "lists", "members.json"), "w") as f:
        json.dump(index, f, indent=1)
    print(json.dumps(index, indent=1))


if __name__ == "__main__":
    main()
