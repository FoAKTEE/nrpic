#!/usr/bin/env python3
"""Test S of tracks/core/JOURNAL-scalar3.md: the option <scalar_field> con_signed (signed
box means of H and M_i, and the spread of H about its mean, in <basename>.sf.con.hst;
Track E's request 3 of tracks/E-stoch-inf/usr/README.md).

    python3 s1_signed.py --exe EXE [--out DIR] [--tlim 3.0] [--workers 3]

Runs the inflection case at 32^3 (nmax2 = 64, problems/scalar/usr_stochastic.athinput
with the lines con_signed and dump_magnitudes added, dumps every 0.5 with H, M_i, [H]):
  sig    mode scale 1, con_signed = true
  plain  mode scale 1, con_signed = false
  zsig   mode scale 0, con_signed = true
Checks: (a) every file of sig and plain byte-identical but the record, whose first 20
columns are identical on every line; (b) the new columns against the dumps (means of
H, M_i, rms and ratio of H - <H> with [H] of the dump); (c) the size of H - <H> against
H.  Writes DIR/summary.json and DIR/fig_signed.png."""
import argparse
import filecmp
import os

import s3
from s3 import common, np, sf

INP = os.path.join(common.PROB, "usr_stochastic.athinput")
BASE = "usr"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--nmax2", type=int, default=64)
    ap.add_argument("--tlim", type=float, default=3.0)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    case = s3.case("usr", a.nmax2)
    base = common.write_case(case, out) + common.mesh_args(a.n) + [
        f"scalar_field/noise_nmax2={a.nmax2}", f"time/tlim={a.tlim}"]
    lines = []
    for ln in open(INP).read().splitlines():
        lines.append(ln)
        if ln.split("=")[0].strip() == "con_dcycle":
            lines.append("con_signed       = false")
    lines = [("dump_magnitudes  = true" if x.split("=")[0].strip() == "dump_magnitudes"
              else x) for x in lines]
    inp = os.path.join(out, "usr_signed.athinput")
    with open(inp, "w") as fp:
        fp.write("\n".join(lines) + "\n")
    spec = {"sig": ["scalar_field/con_signed=true"],
            "plain": ["scalar_field/con_signed=false"],
            "zsig": ["scalar_field/con_signed=true", "scalar_field/noise_mode_scale=0.0"]}
    cases = [(os.path.join(out, k), inp, base + v) for k, v in spec.items()]
    walls = common.run_many(os.path.abspath(a.exe), cases, a.workers)
    summ = dict(exe=os.path.abspath(a.exe), spec=spec, base=base,
                wall_s=dict(zip(spec, walls)))

    # (a) byte identity
    ds, dp = os.path.join(out, "sig"), os.path.join(out, "plain")
    names = sorted(set(os.listdir(ds)) | set(os.listdir(dp)))
    same, differ = [], []
    for nm in names:
        if nm == "athena.log":
            continue
        fa, fb = os.path.join(ds, nm), os.path.join(dp, nm)
        if os.path.exists(fa) and os.path.exists(fb) and filecmp.cmp(fa, fb, False):
            same.append(nm)
        else:
            differ.append(nm)
    la = open(os.path.join(ds, BASE + ".sf.con.hst")).read().splitlines()
    lb = open(os.path.join(dp, BASE + ".sf.con.hst")).read().splitlines()
    pref_ok = len(la) == len(lb) and all(
        x.split()[:20] == y.split()[:20] and len(y.split()) == 20 and len(x.split()) == 27
        for x, y in zip(la[2:], lb[2:]))
    head_ok = la[0] == lb[0] and la[1].startswith(lb[1]) and la[1] != lb[1]
    summ["a"] = dict(identical=same, differ=differ, record_first20_identical=pref_ok,
                     header_extends_old=head_ok, lines=len(la))

    # (b) the new columns against the dumps
    rows = []
    for k in ("sig", "zsig"):
        rd = os.path.join(out, k)
        c = sf.read_con_history(os.path.join(rd, BASE + ".sf.con.hst"))
        for cy, d in sorted(s3.dumps(rd, BASE).items()):
            i = int(np.searchsorted(c["cycle"], cy))
            if i >= c["cycle"].size or int(c["cycle"][i]) != cy:
                continue
            f = d["fields"]
            hb = f["H"].mean()
            hp = f["H"] - hb
            r = np.where(f["Hmag"] > 0.0, np.abs(hp)/f["Hmag"], 0.0)
            mrms = np.sqrt(np.mean(f["Mx"]**2 + f["My"]**2 + f["Mz"]**2))
            rows.append(dict(
                run=k, cycle=cy, time=float(d["time"]), efolds=float(c["efolds"][i]),
                H_mean=float(c["H_mean"][i]), H_mean_dump=float(hb),
                H_mean_rel=float(abs(c["H_mean"][i]/hb - 1.0)) if hb != 0 else None,
                M_mean_abs_over_rms=float(max(abs(c[x][i] - f[y].mean())
                                              for x, y in (("Mx_mean", "Mx"),
                                                           ("My_mean", "My"),
                                                           ("Mz_mean", "Mz")))/mrms)
                if mrms > 0 else None,
                M_mean_over_rms=float(max(abs(c[x][i]) for x in
                                          ("Mx_mean", "My_mean", "Mz_mean"))/mrms)
                if mrms > 0 else None,
                Hp_rms=float(c["Hp_rms"][i]), Hp_rms_dump=float(np.sqrt(np.mean(hp**2))),
                Hp_ratio=float(c["Hp_ratio"][i]), Hp_ratio_dump=float(r.mean()),
                Hp_ratio_max=float(c["Hp_ratio_max"][i]), Hp_ratio_max_dump=float(r.max()),
                H_ratio=float(c["H_ratio"][i])))
    for x in rows:
        x["Hp_rms_rel"] = abs(x["Hp_rms"]/x["Hp_rms_dump"] - 1.0) \
            if x["Hp_rms_dump"] > 0 else None
        x["Hp_ratio_rel"] = abs(x["Hp_ratio"]/x["Hp_ratio_dump"] - 1.0) \
            if x["Hp_ratio_dump"] > 0 else None
    summ["b"] = rows
    sig = [x for x in rows if x["run"] == "sig" and x["time"] > 0]
    summ["b_max"] = dict(
        H_mean_rel=max(x["H_mean_rel"] for x in rows if x["H_mean_rel"] is not None),
        M_mean_abs_over_rms=max(x["M_mean_abs_over_rms"] for x in sig),
        Hp_rms_rel=max(x["Hp_rms_rel"] for x in sig),
        Hp_ratio_rel=max(x["Hp_ratio_rel"] for x in sig))
    common.dump_json(summ, os.path.join(out, "summary.json"))

    # figure: the record of H against that of H - <H>
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.95, wspace=0.28)
    cols = dict(sig=fs.PAL["blue"], zsig=fs.PAL["red"])
    labs = dict(sig="mode scale 1", zsig="mode scale 0")
    for k in ("sig", "zsig"):
        c = sf.read_con_history(os.path.join(out, k, BASE + ".sf.con.hst"))
        ax[0].plot(c["efolds"][1:], c["H_ratio"][1:], "-", color=cols[k],
                   label=labs[k] + r": $\langle|\mathcal{H}|/[\mathcal{H}]\rangle$")
        ax[0].plot(c["efolds"][1:], np.maximum(c["Hp_ratio"][1:], 1e-30), "--",
                   color=cols[k], label=labs[k] + r": $\langle|\mathcal{H}'|/"
                   r"[\mathcal{H}]\rangle$")
        ax[1].plot(c["efolds"][1:], np.abs(c["H_mean"][1:]), "-", color=cols[k],
                   label=labs[k] + r": $|\langle\mathcal{H}\rangle|$")
        ax[1].plot(c["efolds"][1:], np.maximum(c["Hp_rms"][1:], 1e-30), "--",
                   color=cols[k], label=labs[k] + r": rms $\mathcal{H}'$")
    xs = [x for x in rows if x["run"] == "sig" and x["time"] > 0]
    ax[0].plot([x["efolds"] for x in xs], [x["Hp_ratio_dump"] for x in xs], "o",
               mfc="none", ms=4, color=fs.PAL["blue"], label="from the dumps")
    ax[1].plot([x["efolds"] for x in xs], [x["Hp_rms_dump"] for x in xs], "o",
               mfc="none", ms=4, color=fs.PAL["blue"], label="from the dumps")
    for x in ax:
        x.set_yscale("log")
        x.set_xlabel("e-folds after $N_*$")
        x.legend(loc="lower right", fontsize=6)
    ax[0].set_ylabel("ratio to the magnitude")
    ax[1].set_ylabel("code units")
    fig.savefig(os.path.join(out, "fig_signed.png"), dpi=200)
    print("S done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
