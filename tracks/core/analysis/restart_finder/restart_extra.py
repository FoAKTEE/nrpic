#!/usr/bin/env python3
"""Two further checks of the outputs of continued runs (core/restart-finder, item 1).

    python restart_extra.py --exe NEW --ref-exe RELEASE --out DIR

S2, S1   the cases of tracks/core/analysis/preempt/term_test.py (stop on SIGTERM at cycle
         25 of problems/tests/term_signal_particles.athinput, cycle 100 of
         term_signal_periodic.athinput, continuation), with the new executable and with
         the release: with the new one no file of the continued run may differ from the
         uninterrupted run; with the release the mesh history (header lines) and, for
         S2, *.cons.hst (the record at t = 1.6875) differ.
back     a restart file of the new executable whose .prt ends with the block NRPCNS01
         (problems/tests/restart_outputs.athinput stopped at cycle 27), continued with
         the release executable: it must run to the end (status 0); it loses the record
         as the release does.  And the other way: a restart file of the release (cycle
         27, no block) continued with the new executable runs to the end and lacks that
         one record only.

Writes DIR/summary.json and DIR/fig_restart_extra.{pdf,png}; exit status 0 if the checks
hold.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "preempt"))
import restart_test as rt          # noqa: E402
import term_test as tt             # noqa: E402


def cons_times(d, base):
    return [ln.split()[0].decode() for ln in rt.data_lines(os.path.join(d, base + ".cons.hst"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--ref-exe", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    ck, res = {}, {}
    for tag, exe in (("new", a.exe), ("release", a.ref_exe)):
        for case in ("S2", "S1"):
            r = tt.run_case(case, exe, os.path.join(out, "term_" + tag))
            res["%s_%s" % (case, tag)] = r
            if tag == "new":
                ck["%s, new executable: stopped with status 143 and continued to the end" % case] = (
                    r.get("B_seg1_rc") == 143 and r.get("B_seg2_rc") == 0)
                ck["%s, new executable: no file of the continued run differs (%d files, "
                   "stop at cycle %s)" % (case, r.get("files_compared", 0), r.get("B_seg1_cycle"))] = (
                    r.get("files_differing") == [] and r.get("files_only_in_B") == [])
            else:
                want = ["tsq.cons.hst", "tsq.z4c.user.hst"] if case == "S2" else None
                d = sorted(r.get("files_differing", []))
                ck["%s, release: differing files are the histories only (%s)" % (case, d)] = (
                    d == want if want else all(x.endswith(".hst") for x in d) and len(d) > 0)
    # the record at t = 1.6875 of S2
    for tag in ("new", "release"):
        d = os.path.join(out, "term_" + tag, "S2")
        ta, tb = cons_times(os.path.join(d, "A"), "tsq"), cons_times(os.path.join(d, "B"), "tsq")
        res["S2_%s" % tag]["cons_record_times_A"] = len(ta)
        res["S2_%s" % tag]["cons_missing_in_B"] = [t for t in ta if t not in tb]
    ck["S2, new executable: the record at t = 1.6875 is present"] = (
        res["S2_new"]["cons_missing_in_B"] == [])
    ck["S2, release: that record is missing (%s)" % res["S2_release"]["cons_missing_in_B"]] = (
        res["S2_release"]["cons_missing_in_B"] == ["1.687500000000000e+00"])
    # restart files across the two executables
    f = rt.make_ic(out)
    args = ["-i", rt.DECK, "particles/particle_file=" + f]
    da = os.path.join(out, "A")
    res["A_rc"] = rt.run(a.exe, args, da, "athena.log")
    ta = cons_times(da, rt.BASE)
    for name, first, second in (("back", a.exe, a.ref_exe), ("forward", a.ref_exe, a.exe)):
        d = os.path.join(out, name)
        rc1 = rt.run_to_signal(first, args, d, "athena.seg1.log", 27)
        rst = rt.rst_files(d)[-1]
        prt = os.path.getsize(rst + ".prt")
        rc2 = rt.run(second, ["-r", rst], d, "athena.seg2.log")
        start = rt.first_cycle(os.path.join(d, "athena.seg2.log"))
        tb = cons_times(d, rt.BASE)
        res[name] = dict(first=first, second=second, rcs=[rc1, rc2], continued_at_cycle=start,
                         prt_bytes=prt, cons_missing=[t for t in ta if t not in tb],
                         cons_extra=[t for t in tb if t not in ta])
    ck["back: the restart file of the new executable at cycle %d carries the block "
       "(.prt %d bytes)" % (res["back"]["continued_at_cycle"], res["back"]["prt_bytes"])] = (
        res["back"]["prt_bytes"] > res["forward"]["prt_bytes"])
    ck["back: the release continues it to the end (status 0)"] = (res["back"]["rcs"] == [143, 0])
    ck["forward: the new executable continues a restart file of the release (status 0)"] = (
        res["forward"]["rcs"] == [143, 0])
    for name in ("back", "forward"):
        ok = res[name]["continued_at_cycle"] % 4 == 3
        ck["%s: cut one cycle before a record (cycle %d): that record is missing, no other "
           "(%s)" % (name, res[name]["continued_at_cycle"], res[name]["cons_missing"])] = (
            ok and len(res[name]["cons_missing"]) == 1 and res[name]["cons_extra"] == [])
    # figure: record times of cons.hst
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.8))
    fig.subplots_adjust(left=0.36, right=0.97, bottom=0.18, top=0.96)
    rows = [("S2, uninterrupted", os.path.join(out, "term_new", "S2", "A"), "tsq", fs.PAL["blue"]),
            ("S2, v0.7 continued", os.path.join(out, "term_release", "S2", "B"), "tsq", fs.PAL["yellow"]),
            ("S2, new continued", os.path.join(out, "term_new", "S2", "B"), "tsq", fs.PAL["red"]),
            ("new file, v0.7 continues", os.path.join(out, "back"), rt.BASE, fs.PAL["yellow"]),
            ("v0.7 file, new continues", os.path.join(out, "forward"), rt.BASE, fs.PAL["orange"])]
    for y, (lab, d, base, col) in enumerate(rows):
        t = [float(x) for x in cons_times(d, base)]
        ax.plot(t, [y]*len(t), ls="none", marker="|", ms=8, color=col)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlim(0.9, 2.6); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("t of the records of cons.hst")
    figs = fs.save(fig, os.path.join(out, "fig_restart_extra"))
    summary = dict(exe=a.exe, exe_sha256=rt.sha(a.exe), ref_exe=a.ref_exe,
                   ref_exe_sha256=rt.sha(a.ref_exe), checks=ck, cases=res, figures=figs,
                   all_ok=all(ck.values()))
    with open(os.path.join(out, "summary.json"), "w") as fo:
        json.dump(summary, fo, indent=1, default=str)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    print("ALL OK" if summary["all_ok"] else "SOME CHECK FAILED")
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
