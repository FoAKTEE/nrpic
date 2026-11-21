#!/usr/bin/env python3
"""Quick tests of release candidate core-v0.6 on processors: one example per merged
branch from its READY against the executable the branch published, the stock values of
the new options against the release before, the combination the merge creates, and the
never-set bytes of the mesh header of restart files.

    quick_v06.py --new ATHENA --base ATHENA_V05 --out DIR [--cores N] [--regress DIR]
                 [--groups newton,faces,combo,header]

Group newton (Qn; branch executable core_newton-2/athena_cpu):
  n_sp, n_7p   problems/newton/periodic_fft.athinput, wave of 32^3 particles, tlim = 1,
               newton_fft_symbol = spectral and seven_point, one group history, restart
               files at the start and the end
Group faces (Qf):
  f_full       problems/tests/z4c_faces.athinput, 8 steps, as written (the full set):
               against the branch executable core_z4c-faces/athena_cpu
  f_stock      the same with extrap_order = 2, ghost_falloff = false, sbc_variant =
               sommerfeld, sbc_speed = unit: against the release executable (--base)
Group combo (C; the candidate only): problems/idsolve/puncture.athinput at 32 cells
  (Bowen-York puncture solved by id_solve) followed by 8 steps,
  c_st0, c_st1   id_residual = stencil without and with the full set of faces options
  c_cd0, c_cd1   id_residual = code, id_puncture_radius = 3, without and with
  The record of the solve punc.idsolve.txt is compared between 0 and 1.
Group header (H): every mesh restart file below --regress DIR/<case>/new and of the
  runs of this call: the nine members cnx1 .. cke of Mesh::mesh_indcs must be zero.
Every file AthenaK writes is compared byte for byte (classes of regress_v04.py).  The
initial-data solver's own regressions run with the scripts of its package
(analysis/idsolve2/regress_m1.py, regress_r2.py).  Writes DIR/summary.json and
DIR/fig_quick_v06.{pdf,png}; exit status 0 if every run ended with status 0, no file of
the groups newton and faces is of class "other" and no header byte is set.
"""
import argparse
import concurrent.futures as cf
import glob
import json
import os
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(HERE, "..", "cosmo_amr"))
import regress_v04 as rg                      # noqa: E402
import amrlib as A                            # noqa: E402

EXE_DIR = "/data/haiyangw/nrpic/scratch/core/exe"
PROB = os.path.join(REPO, "problems")
FACES = dict(extrap_order=4, ghost_falloff=True, sbc_variant="nonwave", sbc_speed="metric")
STOCK = dict(extrap_order=2, ghost_falloff=False, sbc_variant="sommerfeld",
             sbc_speed="unit")


def deck_newton(d, symbol):
    nrp = os.path.join(d, "wave32.nrp")
    if not os.path.exists(nrp):
        subprocess.run([sys.executable, os.path.join(PROB, "newton/make_ic.py"), "wave",
                        "--out", nrp, "--n", "32"], check=True, stdout=subprocess.DEVNULL)
    b = A.Inp(os.path.join(PROB, "newton/periodic_fft.athinput"))
    b.set("particles", particle_file=nrp, newton_fft_symbol=symbol)
    return b.set("time", tlim=1.0)


def deck_faces(d, stock):
    b = A.Inp(os.path.join(PROB, "tests/z4c_faces.athinput"))
    if stock:
        b.set("z4c", **STOCK)
    return b.set("time", nlim=8)


def deck_combo(d, code, faces):
    b = A.Inp(os.path.join(PROB, "idsolve/puncture.athinput"))
    b.set("mesh", nx1=32, nx2=32, nx3=32)
    b.set("meshblock", nx1=16, nx2=16, nx3=16)
    b.set("time", nlim=8)
    if code:
        b.set("particles", id_residual="code", id_puncture_radius=3.0)
    if faces:
        b.set("z4c", **FACES)
    return b


# name -> (group, deck maker, [(label, executable key)])
CASES = {
    "n_sp": ("newton", lambda d: deck_newton(d, "spectral"), ["new", "newton"]),
    "n_7p": ("newton", lambda d: deck_newton(d, "seven_point"), ["new", "newton"]),
    "f_full": ("faces", lambda d: deck_faces(d, False), ["new", "faces"]),
    "f_stock": ("faces", lambda d: deck_faces(d, True), ["new", "base"]),
    "c_st0": ("combo", lambda d: deck_combo(d, False, False), ["new"]),
    "c_st1": ("combo", lambda d: deck_combo(d, False, True), ["new"]),
    "c_cd0": ("combo", lambda d: deck_combo(d, True, False), ["new"]),
    "c_cd1": ("combo", lambda d: deck_combo(d, True, True), ["new"]),
}


def run_one(job):
    name, who, exe, top = job
    d = os.path.join(top, name, who)
    os.makedirs(d, exist_ok=True)
    CASES[name][1](os.path.join(top, name)).write(os.path.join(d, "in.athinput"))
    rc, sec = rg.run(exe, d, (os.path.join(d, "in.athinput"), [], []))
    return name, who, rc, sec


def header_bytes(path):
    """the nine never-set ints of the mesh header of a restart file, or None."""
    with open(path, "rb") as f:
        data = f.read(1 << 20)
    i = data.find(b"<par_end>\n")
    if i < 0:
        return None
    s = i + len(b"<par_end>\n") + 2*4 + 9*8 + 10*4
    return list(struct.unpack("<9i", data[s:s + 36]))


def idsolve_record(path):
    out = dict(lines=0, outer=None, H_last=None)
    if not os.path.exists(path):
        return out
    rows = [ln.split() for ln in open(path) if ln.strip() and not ln.startswith("#")]
    out["lines"] = len(rows)
    if rows:
        out["outer"] = int(rows[-1][0])
        out["H_last"] = float(rows[-1][4])
        out["psi_max"] = float(rows[-1][9])
    return out


def hist_finite(d):
    ok, hmax = True, 0.0
    for p in glob.glob(os.path.join(d, "*.hst")):
        try:
            a = np.atleast_2d(np.loadtxt(p))
        except ValueError:
            return False, float("nan")
        ok = ok and bool(np.isfinite(a).all())
        if p.endswith(".cstat.hst") and a.size:
            hmax = float(a[-1, 9])            # H_mean of the last record
    return ok, hmax


def figure(rep, out):
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.4))
    names = [c for c in rep["byte"]]
    y = np.arange(len(names))
    tot = [rep["byte"][c]["n_files"] for c in names]
    same = [rep["byte"][c]["classes"].get("identical", 0) for c in names]
    axs[0].barh(y, tot, color=fs.PAL["red"], label="files compared")
    axs[0].barh(y, same, color=fs.PAL["blue"], label="byte-identical")
    axs[0].set_yticks(y)
    axs[0].set_yticklabels(["%s (%s)" % (c, rep["byte"][c]["against"]) for c in names],
                           fontsize=6)
    axs[0].invert_yaxis()
    axs[0].set_xlabel("files")
    axs[0].legend(fontsize=5, loc="lower right")
    axs[0].set_title("(a) candidate against branch or release", fontsize=7)
    cn = [c for c in rep["combo"]]
    x = np.arange(len(cn))
    axs[1].bar(x - 0.2, [max(rep["combo"][c]["H_last"] or 1e-18, 1e-18) for c in cn], 0.4,
               color=fs.PAL["blue"], label=r"max$|H|$ after the solve")
    axs[1].bar(x + 0.2, [max(rep["combo"][c]["cstat_max"] or 1e-18, 1e-18) for c in cn],
               0.4, color=fs.PAL["orange"], label=r"mean $|H|$ of the mesh after 8 steps")
    axs[1].set_yscale("log")
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(cn, fontsize=6)
    axs[1].legend(fontsize=5, loc="upper left")
    axs[1].set_title("(b) solved puncture, without (0) and with (1) the faces options",
                     fontsize=7)
    fig.tight_layout()
    p = os.path.join(out, "fig_quick_v06")
    fs.save(fig, p)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cores", type=int, default=3)
    ap.add_argument("--regress", default="")
    ap.add_argument("--groups", default="newton,faces,combo,header")
    a = ap.parse_args()
    exe = dict(new=os.path.abspath(a.new), base=os.path.abspath(a.base),
               newton=os.path.join(EXE_DIR, "core_newton-2/athena_cpu"),
               faces=os.path.join(EXE_DIR, "core_z4c-faces/athena_cpu"))
    groups = a.groups.split(",")
    os.makedirs(a.out, exist_ok=True)
    jobs = [(n, w, exe[w], a.out) for n, (g, _, who) in CASES.items() if g in groups
            for w in who]
    for n in {j[0] for j in jobs}:           # particle files before the threads start
        os.makedirs(os.path.join(a.out, n), exist_ok=True)
        CASES[n][1](os.path.join(a.out, n))
    status = {}
    with cf.ThreadPoolExecutor(max_workers=a.cores) as ex:
        for name, who, rc, sec in ex.map(run_one, jobs):
            status["%s/%s" % (name, who)] = dict(exit=rc, wall_s=sec)
            print("%-8s %-7s exit %d  %.0f s" % (name, who, rc, sec), flush=True)
    rep = dict(exe=exe, status=status, byte={}, combo={}, header={})
    bad = [k for k, v in status.items() if v["exit"] != 0]
    # byte comparisons
    for name, (g, _, who) in CASES.items():
        if g not in groups or len(who) < 2:
            continue
        da, db = (os.path.join(a.out, name, w) for w in who)
        fa, fb = rg.out_files(da), rg.out_files(db)
        cls, other = {}, []
        for f in sorted(set(fa) | set(fb)):
            if f == "in.athinput":
                continue
            if f not in fa or f not in fb:
                c, info = "other", {"why": "in one run only"}
            else:
                c, info = rg.classify(f, open(os.path.join(da, f), "rb").read(),
                                      open(os.path.join(db, f), "rb").read())
            cls[c] = cls.get(c, 0) + 1
            if c != "identical":
                other.append([f, c, info])
        rep["byte"][name] = dict(against=who[1], n_files=sum(cls.values()), classes=cls,
                                 not_identical=other)
        print("%-8s against %-7s files %2d  %s" % (name, who[1], sum(cls.values()), cls))
        if cls.get("other", 0) or cls.get("a", 0) or cls.get("b", 0) or not cls:
            bad.append(name + ": files differ")
    # combination
    for name, (g, _, who) in CASES.items():
        if g != "combo" or g not in groups:
            continue
        d = os.path.join(a.out, name, "new")
        e = idsolve_record(os.path.join(d, "punc.idsolve.txt"))
        e["finite"], e["cstat_max"] = hist_finite(d)
        e["guard"] = bool(glob.glob(os.path.join(d, "*.guard.txt")))
        rep["combo"][name] = e
    for p in ("c_st", "c_cd"):
        if p + "0" in rep["combo"]:
            f0, f1 = (os.path.join(a.out, p + s, "new", "punc.idsolve.txt") for s in "01")
            same = (os.path.exists(f0) and os.path.exists(f1) and
                    open(f0, "rb").read() == open(f1, "rb").read())
            rep["combo"][p + "_record_identical"] = same
            print("%s: record of the solve identical with and without the faces options: "
                  "%s; %s | %s" % (p, same, rep["combo"][p + "0"], rep["combo"][p + "1"]))
    # header bytes
    if "header" in groups:
        files = glob.glob(os.path.join(a.out, "*", "new", "**", "*.rst"), recursive=True)
        if a.regress:
            files += glob.glob(os.path.join(a.regress, "*", "new", "**", "*.rst"),
                               recursive=True)
        nset = 0
        for p in sorted(files):
            h = header_bytes(p)
            rep["header"][p] = h
            if h is None or any(h):
                nset += 1
        rep["header_files"] = len(files)
        rep["header_not_zero"] = nset
        print("header: %d mesh restart files, %d with a non-zero or unreadable header"
              % (len(files), nset))
        if nset or not files:
            bad.append("header")
    rep["bad"] = bad
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(rep, f, indent=1)
    combo = {k: v for k, v in rep["combo"].items() if isinstance(v, dict)}
    if rep["byte"] and combo:
        rep["combo"] = combo
        figure(rep, a.out)
    print("QUICK", "FAIL: %s" % bad if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
