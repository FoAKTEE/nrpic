#!/usr/bin/env python3
"""Quick look at the records of a batch of card runs of the USR case (no dumps read):
U-A0 and U-A1 from <basename>.sf.con.hst, the lockstep record <basename>.sf.NNNNN.modes of
the last dump against the code-time MS reference, the con_signed columns, and the cost from
athena.log. Used to check that a card build ran the case correctly before the next job is
submitted (JOURNAL entry 11); the full analysis is analyse_cards.py.

    python3 quick_records.py --run RUNDIR --ref ../results --out OUT [--names U64p,U64m,...]
"""
import argparse
import json
import os

import numpy as np

import analyse_cards as ac
import card_lib as cl
import usr_lib as ul


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", default="U64p,U64m,U128p,U128m,U128hp,U128hm")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r, ci, lm = ac.load_ref(a.ref)
    out = {}
    for n in a.names.split(","):
        d = os.path.join(a.run, n)
        con = cl.read_con(os.path.join(d, "usr.sf.con.hst"))
        rec, _ = ac.record_checks(con, ci, lm)
        dumps = cl.dump_list(d)
        h = ul.read_header(dumps[-1])
        mp = dumps[-1][:-5] + ".modes"
        hd, n2r, rr, drr = ul.read_modes_record(mp)
        nmax2 = int(n2r.max())
        mf = os.path.join(ac.PKG, "inputs", ac.MODEFILE[64 if nmax2 <= 64 else 4096])
        sref = cl.ShellReference(ci, mf, nmax2, np.array([h["time"]]))
        st = sref.state(0)
        idx = np.searchsorted(sref.n2, n2r)
        s = float(np.sign(np.real(rr[0]) / np.real(st["R"][idx[0]])))
        lock = float(np.max(np.abs(rr - s * st["R"][idx]) / np.abs(st["R"][idx])))
        out[n] = dict(ndumps=len(dumps), last_dump_time=h["time"], last_dump_cycle=h["cycle"],
                      sign=s, lock_max_end=lock, record_columns=int(con.shape[1]),
                      Hp_ratio_finite=bool(np.all(np.isfinite(con[:, cl.C["Hp_ratio"]]))),
                      cost=cl.athena_cost(d), **rec)
        print(f"{n}: dumps {len(dumps)} t_last {h['time']:.12f} lock {lock:.3e} "
              f"Pi_rel_max {rec['U_A1_Pi_rel_max']:.3e} |dN|max {rec['U_A0_max_abs_dN']:.2e} "
              f"M_ratio_max {rec['record']['M_ratio_max']:.3e} Hp_max {rec['record'].get('Hp_ratio_max', float('nan')):.3e}",
              flush=True)
    with open(os.path.join(a.out, "quick_records.json"), "w") as fp:
        json.dump(out, fp, indent=1, default=float)


if __name__ == "__main__":
    main()
