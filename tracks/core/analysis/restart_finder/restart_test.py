#!/usr/bin/env python3
"""Outputs of a continued run against the uninterrupted run (core/restart-finder, item 1).

    python restart_test.py --exe NEW --ref-exe RELEASE --out DIR [--by-binary]

Deck: problems/tests/restart_outputs.athinput (periodic box, particles, Z4c, a tracker
that moves, conservation record every four cycles).  Run A goes to the end without
interruption.  Each case B receives SIGTERM once its log shows cycle K-1 (the code then
finishes the cycle in progress, writes a restart file and exits with status 143; the
cycle it stopped at is read back and reported), is continued with -r <restart file>, and
every file of B is compared with A byte for byte, except the logs and the restart files.
(A cut by time/nlim is not used: a run that ends by itself writes final outputs of every
kind, an extra table and history record that an interrupted run does not have.)

  K24, K25, K26, K27   one cut, aimed at every residue of the record interval of *.cons.hst
  chain                two cuts (14, then 27)
  older                cut at 27, continued from the restart file BEFORE the newest (the
                       first segment has run past it, as after a kill from outside):
                       only the tracker file is required to equal A
  ref-K24 .. ref-K27   the same cuts with the release executable: what a restart changed
                       before this work

--by-binary adds the two-puncture deck problems/puncture/by_binary.athinput reduced to
three refinement levels and 24 cycles, cut at 12 by time/nlim (outflow faces and refinement: a restart
is exact only up to round-off there, so the tracker files are compared by cycle numbers
and by the largest difference of a value).

Writes DIR/summary.json and DIR/fig_restart_test.{pdf,png}; exit status 0 if every check
of the new executable holds.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DECK = os.path.join(REPO, "problems", "tests", "restart_outputs.athinput")
BASE = "rso"
SKIP = re.compile(r"(^|/)(athena[^/]*\.log|rst/.*)$")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def run(exe, args, rundir, log):
    os.makedirs(rundir, exist_ok=True)
    with open(os.path.join(rundir, log), "ab") as f:
        return subprocess.run([exe] + args + ["-d", rundir], stdout=f,
                              stderr=subprocess.STDOUT, cwd=rundir).returncode


def rst_files(rundir):
    return sorted(glob.glob(os.path.join(rundir, "rst", "*.rst")))


def lines(path):
    with open(path, "rb") as f:
        return f.read().splitlines()


def data_lines(path):
    return [ln for ln in lines(path) if not ln.startswith(b"#")]


def header_count(path):
    return sum(1 for ln in lines(path) if ln.startswith(b"#"))


def split_rst(path):
    with open(path, "rb") as f:
        b = f.read()
    i = b.find(b"<par_end>")
    return b[:i], b[i:]


def files_of(d):
    fs = sorted(os.path.relpath(os.path.join(r, x), d) for r, _, xs in os.walk(d) for x in xs)
    return [x for x in fs if not SKIP.search(x)]


def compare(da, db):
    """Files of A and B: which differ and how."""
    fa, fb = files_of(da), files_of(db)
    diff, how, nbytes = [], {}, 0
    for x in fa:
        pa, pb = os.path.join(da, x), os.path.join(db, x)
        nbytes += os.path.getsize(pa)
        if not os.path.exists(pb):
            diff.append(x); how[x] = "missing in B"
            continue
        if sha(pa) == sha(pb):
            continue
        diff.append(x)
        if x.endswith(".hst") or x.endswith(".txt"):
            la, lb = data_lines(pa), data_lines(pb)
            ca, cb = header_count(pa), header_count(pb)
            sa, sb = set(la), set(lb)
            only_a = [ln.split()[0].decode() for ln in la if ln not in sb]
            only_b = [ln.split()[0].decode() for ln in lb if ln not in sa]
            dup = len(lb) - len(set(lb))
            how[x] = dict(header_lines=[ca, cb], records=[len(la), len(lb)],
                          only_in_A=len(only_a), only_in_B=len(only_b),
                          first_only_in_A=only_a[:4], repeated_in_B=dup)
        else:
            how[x] = "bytes differ"
    return dict(files_compared=len(fa), bytes_compared=nbytes, files_differing=diff,
                how=how, files_only_in_B=[x for x in fb if x not in fa],
                same_file_set=(fa == fb))


def last_rst_checks(da, db):
    ra, rb = rst_files(da), rst_files(db)
    out = dict(A_rst=len(ra), B_rst=len(rb))
    if ra and rb:
        (_, ba), (_, bb) = split_rst(ra[-1]), split_rst(rb[-1])
        out["last_rst_data_identical"] = (ba == bb)
        out["last_prt_identical"] = (os.path.exists(rb[-1] + ".prt")
                                     and sha(ra[-1] + ".prt") == sha(rb[-1] + ".prt"))
        out["prt_bytes"] = sorted(set(os.path.getsize(x + ".prt") for x in rb))
    return out


def make_ic(out):
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    f = os.path.join(ic, "particles.nrp")
    if not os.path.exists(f):
        subprocess.run([sys.executable, os.path.join(REPO, "cosmo", "ic", "make_lattice.py"),
                        "--n", "16", "--ppc", "1", "--L", "4", "--noise-x", "0.05",
                        "--noise-u", "0.05", "--seed", "7", "--out", ic], check=True,
                       cwd=os.path.join(REPO, "cosmo", "ic"))
    return f


def last_cycle(log):
    try:
        with open(log, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 4000))
            tail = f.read().decode(errors="replace")
    except OSError:
        return -1
    m = re.findall(r"cycle=(\d+)", tail)
    return int(m[-1]) if m else -1


def first_cycle(log):
    with open(log, errors="replace") as f:
        m = re.search(r"cycle=(\d+)", f.read())
    return int(m.group(1)) if m else -1


def run_to_signal(exe, args, d, log, k):
    """Starts a run and sends SIGTERM once its log shows cycle k - 1."""
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, log)
    with open(path, "ab") as f:
        p = subprocess.Popen([exe] + args + ["-d", d], stdout=f, stderr=subprocess.STDOUT,
                             cwd=d)
        while p.poll() is None and last_cycle(path) < k - 1:
            time.sleep(0.005)
        if p.poll() is None:
            os.kill(p.pid, signal.SIGTERM)
        return p.wait()


def cut_case(exe, args, d, cuts, older=False):
    """Segments stopped by SIGTERM near the cycles of `cuts`, then one to the end.
    Returns the exit statuses, the restart file of the last continuation and the cycles
    the continuations started with."""
    rcs, starts, rst = [], [], None
    rcs.append(run_to_signal(exe, args, d, "athena.seg1.log", cuts[0]))
    for n, k in enumerate(list(cuts[1:]) + [-1]):
        rs = rst_files(d)
        if not rs:
            return rcs, None, starts
        rst = rs[-2] if (older and n == 0) else rs[-1]
        log = "athena.seg%d.log" % (n + 2)
        if k > 0:
            rcs.append(run_to_signal(exe, ["-r", rst], d, log, k))
        else:
            rcs.append(run(exe, ["-r", rst], d, log))
        starts.append(first_cycle(os.path.join(d, log)))
    return rcs, os.path.relpath(rst, d), starts


def periodic_cases(exe, ref_exe, out):
    res = {}
    f = make_ic(out)
    args = ["-i", DECK, "particles/particle_file=" + f]
    da = os.path.join(out, "A")
    t0 = time.time()
    rc = run(exe, args, da, "athena.log")
    res["A"] = dict(rc=rc, wall_s=round(time.time() - t0, 2), exe=exe,
                    particle_file_sha256=sha(f), deck_sha256=sha(DECK))
    dr = os.path.join(out, "A_ref")
    rc = run(ref_exe, args, dr, "athena.log")
    cr = compare(da, dr)
    res["A_ref"] = dict(rc=rc, exe=ref_exe, uninterrupted_new_equals_release=(
        cr["files_differing"] == [] and cr["same_file_set"]),
        files_compared=cr["files_compared"], files_differing=cr["files_differing"])
    plan = [("K%d" % k, exe, [k], False, da) for k in (24, 25, 26, 27)]
    plan += [("chain", exe, [14, 27], False, da), ("older", exe, [27], True, da)]
    plan += [("ref-K%d" % k, ref_exe, [k], False, dr) for k in (24, 25, 26, 27)]
    for name, x, cuts, older, dref in plan:
        d = os.path.join(out, name)
        rcs, rst, starts = cut_case(x, args, d, cuts, older)
        r = dict(exe=x, cuts=cuts, rcs=rcs, continued_from=rst, continued_at_cycle=starts)
        r.update(compare(dref, d))
        r.update(last_rst_checks(dref, d))
        res[name] = r
    return res


def tracker_table(path):
    rows = []
    for ln in data_lines(path):
        p = ln.split()
        rows.append((int(p[0]), [float(v) for v in p[1:]]))
    return rows


def by_binary_cut(exe, deck, d):
    rc1 = run(exe, ["-i", deck, "time/nlim=12"], d, "athena.seg1.log")
    rs = rst_files(d)
    rc2 = run(exe, ["-r", rs[-1], "time/nlim=24"], d, "athena.seg2.log")
    return [rc1, rc2], os.path.relpath(rs[-1], d)


def by_binary(exe, ref_exe, out):
    """Two punctures, outflow faces, refinement: tracker files across one restart."""
    src = open(os.path.join(REPO, "problems", "puncture", "by_binary.athinput")).read()
    src = src.replace("num_levels          = 6", "num_levels          = 3")
    src += "\n<output3>\nfile_type = rst\ndt        = 1000.0\n"
    d0 = os.path.join(out, "by")
    os.makedirs(d0, exist_ok=True)
    deck = os.path.join(d0, "by_binary_l3.athinput")
    with open(deck, "w") as f:
        f.write(src)
    by = dict(deck_sha256=sha(deck))
    t0 = time.time()
    by["A_rc"] = run(exe, ["-i", deck, "time/nlim=24"], os.path.join(d0, "A"), "athena.log")
    by["A_wall_s"] = round(time.time() - t0, 1)
    for name, x in (("B", exe), ("B_ref", ref_exe)):
        d = os.path.join(d0, name)
        rcs, rst = by_binary_cut(x, deck, d)
        r = dict(rcs=rcs, continued_from=rst, exe=x)
        for n in (0, 1):
            fa = os.path.join(d0, "A", "by2.co_%d.txt" % n)
            fb = os.path.join(d, "by2.co_%d.txt" % n)
            ta, tb = tracker_table(fa), tracker_table(fb)
            same = [t[0] for t in ta] == [t[0] for t in tb]
            dmax = 0.0
            if same:
                for (_, va), (_, vb) in zip(ta, tb):
                    dmax = max(dmax, max(abs(p - q) for p, q in zip(va, vb)))
            r["co_%d" % n] = dict(records_A=len(ta), records_B=len(tb),
                                  first_cycle_B=(tb[0][0] if tb else None),
                                  same_cycles=same, max_abs_diff=dmax,
                                  header_lines_B=header_count(fb),
                                  byte_identical=(sha(fa) == sha(fb)))
        by[name] = r
    return by


def judge(res):
    ck = {}
    ck["A ended with status 0"] = (res["A"]["rc"] == 0)
    ck["uninterrupted run: new executable equals the release byte for byte"] = \
        res["A_ref"]["uninterrupted_new_equals_release"]
    for name in ("K24", "K25", "K26", "K27", "chain"):
        r = res[name]
        ck["%s: cut segments status 143, last segment status 0" % name] = (
            all(c == 143 for c in r["rcs"][:-1]) and r["rcs"][-1] == 0)
        ck["%s: every output file byte-identical to A" % name] = (
            r["files_differing"] == [] and r["same_file_set"])
        ck["%s: last restart file and .prt identical" % name] = (
            r.get("last_rst_data_identical") is True and r.get("last_prt_identical") is True)
    resid = sorted(set(res["K%d" % k]["continued_at_cycle"][0] % 4 for k in (24, 25, 26, 27)))
    ck["the four cuts cover every residue of the record interval (cycles %s)" % [
        res["K%d" % k]["continued_at_cycle"][0] for k in (24, 25, 26, 27)]] = (resid == [0, 1, 2, 3])
    r = res["older"]
    ck["older: tracker file byte-identical to A"] = (BASE + ".co_0.txt" not in r["files_differing"])
    ck["older: the other differing files are appended histories with repeated records"] = all(
        isinstance(r["how"][x], dict) and r["how"][x]["only_in_A"] == 0 for x in r["files_differing"]
        if x.endswith(".hst"))
    # the release, for the record (not part of the verdict of the new executable)
    ref = {}
    for k in (24, 25, 26, 27):
        r = res["ref-K%d" % k]
        h = r["how"]
        ref["K%d" % k] = dict(
            continued_at_cycle=r["continued_at_cycle"],
            files_differing=r["files_differing"],
            tracker_records_missing=h.get(BASE + ".co_0.txt", {}).get("only_in_A")
            if isinstance(h.get(BASE + ".co_0.txt"), dict) else None,
            mesh_history_headers=h.get(BASE + ".z4c.user.hst", {}).get("header_lines")
            if isinstance(h.get(BASE + ".z4c.user.hst"), dict) else None,
            cons_records_missing=h.get(BASE + ".cons.hst", {}).get("only_in_A", 0)
            if isinstance(h.get(BASE + ".cons.hst", {}), dict) else None,
            cons_first_missing=h.get(BASE + ".cons.hst", {}).get("first_only_in_A", [])
            if isinstance(h.get(BASE + ".cons.hst", {}), dict) else None)
    return ck, ref


def figure(out, res):
    import numpy as np
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.17, top=0.97, wspace=0.36)

    def trk(d):
        t = np.array([[r[0]] + r[1][:2] for r in tracker_table(os.path.join(out, d, BASE + ".co_0.txt"))])
        return t

    ax = axs[0]
    a = trk("A")
    ax.plot(a[:, 1], a[:, 2], color=fs.PAL["blue"], label="uninterrupted")
    b = trk("ref-K27")
    ax.plot(b[:, 1], b[:, 2] + 0.25, color=fs.PAL["yellow"], label="v0.7, cut (+0.25)")
    c = trk("K27")
    ax.plot(c[:, 1], c[:, 2] + 0.5, color=fs.PAL["red"], ls="--", label="new, cut (+0.5)")
    tcut = a[a[:, 0] == 27][0, 1]
    ax.axvline(tcut, **fs.MASK_LINE)
    ax.set_xlabel("t"); ax.set_ylabel("tracker x (offset)")
    ax.legend(loc="upper right", fontsize=8)

    ax = axs[1]
    rows = [("A", "A", fs.PAL["blue"])]
    for k in (24, 25, 26, 27):
        rows.append(("ref-K%d" % k, "v0.7, %d" % k, fs.PAL["yellow"]))
    for k in (24, 25, 26, 27):
        rows.append(("K%d" % k, "new, %d" % k, fs.PAL["red"]))
    for y, (d, lab, col) in enumerate(rows):
        t = [float(ln.split()[0]) for ln in data_lines(os.path.join(out, d, BASE + ".cons.hst"))]
        ax.plot(t, [y] * len(t), ls="none", marker="|", ms=7, color=col)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[1] for r in rows], fontsize=7)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlim(1.0, 2.2); ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("t of the records of cons.hst")

    ax = axs[2]
    names = ["A"] + ["ref-K%d" % k for k in (24, 25, 26, 27)] + ["K%d" % k for k in (24, 25, 26, 27)] + ["chain"]
    cols = [fs.PAL["blue"]] + [fs.PAL["yellow"]] * 4 + [fs.PAL["red"]] * 5
    h = [header_count(os.path.join(out, d, BASE + ".z4c.user.hst")) for d in names]
    ax.bar(range(len(names)), h, color=cols, width=0.7)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([n.replace("ref-", "r") for n in names], rotation=90, fontsize=7)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylabel("header lines of the mesh history")
    ax.set_ylim(0, 5)
    return fs.save(fig, os.path.join(out, "fig_restart_test"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--ref-exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--by-binary", action="store_true")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    res = periodic_cases(a.exe, a.ref_exe, out)
    checks, ref = judge(res)
    summary = dict(exe=a.exe, exe_sha256=sha(a.exe), ref_exe=a.ref_exe,
                   ref_exe_sha256=sha(a.ref_exe), checks=checks, release_before=ref,
                   cases=res)
    if a.by_binary:
        by = by_binary(a.exe, a.ref_exe, out)
        summary["by_binary"] = by
        for n in (0, 1):
            c = by["B"]["co_%d" % n]
            checks["by_binary: tracker %d of the continued run holds the cycles of A, "
                   "header once" % n] = (c["same_cycles"] and c["header_lines_B"] == 2)
            checks["by_binary: tracker %d values within 1e-9 of A" % n] = (
                c["same_cycles"] and c["max_abs_diff"] < 1.0e-9)
    summary["figures"] = figure(out, res)
    summary["all_ok"] = all(checks.values())
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    for k, v in checks.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    print("release before:", json.dumps(ref, indent=1))
    if a.by_binary:
        print("by_binary:", json.dumps(summary["by_binary"], indent=1))
    print("ALL OK" if summary["all_ok"] else "SOME CHECK FAILED")
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
