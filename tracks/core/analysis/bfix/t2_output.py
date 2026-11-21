#!/usr/bin/env python3
"""T2: output for the gravitational-wave analysis (predictions P2a, P2c, P2d of
tracks/core/JOURNAL-bfix.md; P2b is tracks/core/tools/regress_relativistic.py, P2e is
part of t3_thin_jitter.py).

Stages:
  bin      `bin` output in double precision against the restart file and against the
           single-precision output of the same times (oblique linear wave, 16^3)
  padding  restart files of identical runs, of the baseline executable, and a restart
           of a baseline file with both executables
  weyl     labels of the extracted waveforms with and without
           <z4c> waveform_at_new_time, read from the two reruns of Track B's deck in
           the output directory of T1 (--t1-dir)

    python3 t2_output.py --exe-new EXE --exe-base EXE --t1-dir DIR [--out DIR]
"""
import argparse
import glob
import json
import os
import subprocess

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import fs, athena_bin  # noqa: E402

A0 = 1.0e-6
INP = os.path.join(bc.REPO, "problems", "tests", "lw_oblique.athinput")
EXTRA = """
<output3>
file_type   = rst
dt          = 0.1

<output4>
file_type   = bin
variable    = z4c
id          = z4c_single
dt          = 0.1

<output5>
file_type        = bin
variable         = adm
double_precision = true
id               = adm_double
dt               = 0.1
"""
Z4C = ["chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Khat", "Axx", "Axy", "Axz", "Ayy",
       "Ayz", "Azz", "Gamx", "Gamy", "Gamz", "Theta", "alpha", "betax", "betay", "betaz"]


def make_input(out):
    p = os.path.join(out, "lw_out.athinput")
    with open(INP) as f:
        txt = f.read()
    with open(p, "w") as f:
        f.write(txt + EXTRA)
    return p


def by_time(files, reader):
    return {round(reader(p)["time"], 12): p for p in files}


def stage_bin(res, B, exe, out):
    ad = B["ad"]
    inp = make_input(out)
    ov = bc.mesh_overrides(16) + ["time/tlim=0.6", "output1/dt=0.1"]
    rec = bc.run_many({"bin": (exe["new"], inp, os.path.join(out, "bin_new"), ov)}, 1)["bin"]
    rd = rec["rundir"]
    dbl = sorted(glob.glob(os.path.join(rd, "bin", "lwo.z4c.0*.bin")))
    sgl = sorted(glob.glob(os.path.join(rd, "bin", "lwo.z4c_single.*.bin")))
    adm = sorted(glob.glob(os.path.join(rd, "bin", "lwo.adm_double.*.bin")))
    rst = sorted(glob.glob(os.path.join(rd, "rst", "*.rst")))
    rows = []
    keep = None
    for pd, ps, pa in zip(dbl, sgl, adm):
        d = athena_bin.read_bin(pd)
        s = athena_bin.read_bin(ps)
        a = athena_bin.read_bin(pa)
        r = None
        for p in rst:
            q = ad.read_rst(p)
            if q["time"] == d["time"]:
                r = q
                break
        ncell = 16**3
        hdr_d = os.path.getsize(pd) - (40 + 48 + 22*8*ncell)
        hdr_s = os.path.getsize(ps) - (40 + 48 + 22*4*ncell)
        row = {"time": d["time"], "cycle": d["cycle"], "var_size_double": d["var_size"],
               "var_size_single": s["var_size"], "restart_found": r is not None,
               "header_bytes_double": hdr_d, "header_bytes_single": hdr_s,
               "size_double": os.path.getsize(pd), "size_single": os.path.getsize(ps)}
        if r is not None:
            row["max_abs_double_minus_restart"] = max(
                float(np.abs(d["z4c_" + n] - r[n]).max()) for n in Z4C)
            row["n_values_differ_double_restart"] = int(sum(
                np.count_nonzero(d["z4c_" + n] != r[n]) for n in Z4C))
        row["n_values_differ_single_vs_rounded_double"] = int(sum(
            np.count_nonzero(s["z4c_" + n] != d["z4c_" + n].astype(np.float32))
            for n in Z4C))
        row["single_dtype"] = str(s["z4c_gxx"].dtype)
        row["double_dtype"] = str(d["z4c_gxx"].dtype)
        # ADM dump against the conversion of the Z4c dump (chi = 1 to second order here)
        dd = bc.z4c_from_bin(d)
        gam, K, _, _ = B["readers"].z4c_to_adm(dd)
        row["adm_gxx_minus_converted"] = float(np.abs(a["adm_gxx"] - gam[0, 0]).max())
        row["adm_Kxy_minus_converted"] = float(np.abs(a["adm_Kxy"] - K[0, 1]).max())
        row["adm_var_size"] = a["var_size"]
        rows.append(row)
        keep = (d, s)
    d, s = keep
    line = {"x": d["x1v"].tolist(),
            "hxx_double": ((d["z4c_gxx"][0, 0] - 1.0)/A0).tolist(),
            "hxx_single": ((s["z4c_gxx"][0, 0].astype(np.float64) - 1.0)/A0).tolist(),
            "hxy_double": (d["z4c_gxy"][0, 0]/A0).tolist(),
            "hxy_single": (s["z4c_gxy"][0, 0].astype(np.float64)/A0).tolist(),
            "time": d["time"]}
    res["bin"] = {"rows": rows, "line": line, "n_dumps": len(rows), "rundir": rd}
    for r in rows:
        print("bin:", r)


def diff_offsets(pa, pb):
    a = np.fromfile(pa, np.uint8)
    b = np.fromfile(pb, np.uint8)
    if a.size != b.size:
        return None, a.size, b.size
    return np.flatnonzero(a != b), a.size, b.size


def pad_window(path):
    with open(path, "rb") as f:
        raw = f.read(200000)
    hdr = raw.find(b"<par_end>") + len(b"<par_end>\n")
    lo = hdr + 8 + 72 + 40          # nmb, root level; mesh_size; ng nx1-3 is..ke
    return lo, lo + 36, np.frombuffer(raw, np.uint8, 36, lo)


def stage_padding(res, B, exe, out):
    """Restart files of the periodic cosmology case of the regression set (east, 16^3 in
    eight MeshBlocks, particles with deposit; the generator fix does not enter), with a
    restart output added."""
    ic = "/data/haiyangw/nrpic/scratch/core/regress/ic/east16"
    inp = os.path.join(out, "east_rst.athinput")
    with open(os.path.join(bc.REPO, "problems", "cosmo", "east.athinput")) as f:
        txt = f.read()
    with open(inp, "w") as f:
        f.write(txt + "\n<output2>\nfile_type = rst\ndcycle    = 5\n")
    ov = ["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8", "meshblock/nx2=8",
          "meshblock/nx3=8", "time/nlim=20", "particles/snap_dt=0.2",
          "particles/traj_ntrack=46"]
    jobs = {}
    for name, tag in (("new_a", "new"), ("new_b", "new"), ("base", "base")):
        rd = os.path.join(out, f"pad_{name}")
        os.makedirs(rd, exist_ok=True)
        for fn in ("particles.nrp", "fields.bin"):
            if not os.path.exists(os.path.join(rd, fn)):
                os.symlink(os.path.join(ic, fn), os.path.join(rd, fn))
        jobs[name] = (exe[tag], inp, rd, ov)
    recs = bc.run_many(jobs, 3)

    def listing(rd):
        return sorted(os.path.relpath(p, rd)
                      for p in glob.glob(os.path.join(rd, "**", "*"), recursive=True)
                      if os.path.isfile(p) and not os.path.islink(p)
                      and os.path.basename(p) != "athena.log")

    names = listing(recs["new_a"]["rundir"])
    r = {"files": len(names), "restart_files": [], "other_files_differing": []}
    for n in names:
        fa = os.path.join(recs["new_a"]["rundir"], n)
        fb = os.path.join(recs["new_b"]["rundir"], n)
        fc = os.path.join(recs["base"]["rundir"], n)
        dab, _, _ = diff_offsets(fa, fb)
        dac, sa, sc = diff_offsets(fa, fc) if os.path.exists(fc) else (None, 0, 0)
        if n.endswith(".rst"):
            lo, hi, bytes_new = pad_window(fa)
            _, _, bytes_base = pad_window(fc)
            r["restart_files"].append({
                "file": n, "window": [lo, hi], "size": sa,
                "new_a_vs_new_b_differing_bytes": int(len(dab)),
                "new_vs_base_differing_bytes": None if dac is None else int(len(dac)),
                "new_vs_base_all_inside_window": None if dac is None else
                bool(np.all((dac >= lo) & (dac < hi))),
                "new_window_all_zero": bool(np.all(bytes_new == 0)),
                "base_window_nonzero_bytes": int(np.count_nonzero(bytes_base))})
        elif dab is None or len(dab) or dac is None or len(dac):
            r["other_files_differing"].append(n)
    # restart of the baseline's restart file of cycle 10 with both executables
    src = [p for p in sorted(glob.glob(os.path.join(recs["base"]["rundir"], "rst", "*.rst")))
           if p.endswith(".00002.rst")][0]
    cont = {}
    for tag in ("new", "base"):
        rd = os.path.join(out, f"pad_restart_{tag}")
        os.makedirs(rd, exist_ok=True)
        for fn in ("particles.nrp", "fields.bin"):
            if not os.path.exists(os.path.join(rd, fn)):
                os.symlink(os.path.join(ic, fn), os.path.join(rd, fn))
        with open(os.path.join(rd, "athena.log"), "w") as log:
            p = subprocess.run([exe[tag], "-r", src, "-d", rd], cwd=rd, stdout=log,
                               stderr=subprocess.STDOUT)
        if p.returncode != 0:
            raise SystemExit(f"restart with {tag} failed: {rd}/athena.log")
        cont[tag] = rd
    rr = {"source": os.path.relpath(src, out), "files": [], "differing": []}
    for n in listing(cont["new"]):
        fa, fb = os.path.join(cont["new"], n), os.path.join(cont["base"], n)
        dd, sa, sb = diff_offsets(fa, fb) if os.path.exists(fb) else (None, 0, 0)
        if n.endswith(".rst"):
            lo, hi, bytes_new = pad_window(fa)
            rr["files"].append({"file": n, "size": sa,
                                "differing_bytes": None if dd is None else int(len(dd)),
                                "all_inside_window": None if dd is None else
                                bool(np.all((dd >= lo) & (dd < hi))),
                                "new_window_all_zero": bool(np.all(bytes_new == 0))})
        elif dd is None or len(dd):
            rr["differing"].append(n)
    rr["n_files"] = len(listing(cont["new"]))
    r["restart_from_baseline_file"] = rr
    res["padding"] = r
    for q in r["restart_files"]:
        print("padding:", q)
    print("padding: other files differing (new twice, new against baseline):",
          r["other_files_differing"] or "none", "of", r["files"])
    print("padding restart:", rr)


def stage_regress(res, report):
    """The report of tracks/core/tools/regress_relativistic.py: every file that differs
    between the baseline and the new executable must be a restart file that differs only
    inside the 36 padding bytes."""
    with open(report) as f:
        rep = json.load(f)
    r = {"report": report, "cases": {}}
    for case, v in rep.items():
        da = os.path.join("/data/haiyangw/nrpic/scratch/core", v["baseline"])
        db = os.path.join("/data/haiyangw/nrpic/scratch/core", v["new"])
        rows = []
        for n in v["differ"]:
            fa, fb = os.path.join(da, n), os.path.join(db, n)
            row = {"file": n, "restart_file": n.endswith(".rst")}
            if n.endswith(".rst") and os.path.exists(fa) and os.path.exists(fb):
                lo, hi, bytes_new = pad_window(fb)
                dd, sa, sb = diff_offsets(fa, fb)
                row.update({"differing_bytes": None if dd is None else int(len(dd)),
                            "all_inside_window": None if dd is None else
                            bool(np.all((dd >= lo) & (dd < hi))),
                            "new_window_all_zero": bool(np.all(bytes_new == 0))})
            rows.append(row)
        r["cases"][case] = {"baseline": v["baseline"], "new": v["new"],
                            "identical_files": len(v["identical"]), "differing": rows}
    r["all_differences_are_padding"] = all(
        q.get("all_inside_window") is True for c in r["cases"].values()
        for q in c["differing"])
    res["regress"] = r
    for case, v in r["cases"].items():
        print("regress:", case, v["baseline"], v["new"], "identical", v["identical_files"],
              "differing", v["differing"])
    print("regress: all differences are the padding bytes:", r["all_differences_are_padding"])


def fit_wave(t, s, omega):
    """Least squares s = a cos(omega t) + b sin(omega t): amplitude, phase of
    C cos(omega t + phi)."""
    M = np.array([np.cos(omega*t), np.sin(omega*t)]).T
    a, b = np.linalg.lstsq(M, s, rcond=None)[0]
    resid = s - M @ np.array([a, b])
    return float(np.hypot(a, b)), float(np.arctan2(-b, a)), float(np.abs(resid).max())


def stage_weyl(res, t1dir):
    r = {}
    series = {}
    for tag, name in (("default", "lw3d_dump_N32"), ("new_time", "lw3d_dump_N32_newtime")):
        wd = os.path.join(t1dir, "trackb", name, "waveforms")
        re = np.loadtxt(os.path.join(wd, "rpsi4_real_00.3.txt"))
        im = np.loadtxt(os.path.join(wd, "rpsi4_imag_00.3.txt"))
        col = 1 + int(np.argmax(np.abs(re[:, 1:]).max(axis=0)))
        amp, ph, rs = fit_wave(re[:, 0], re[:, col], 2*np.pi)
        series[tag] = (re[:, 0], re[:, col])
        r[tag] = {"rows": int(len(re)), "first_label": float(re[0, 0]),
                  "second_label": float(re[1, 0]), "column": col + 1, "amplitude": amp,
                  "phase": ph, "max_residual_over_amp": rs/amp,
                  "imag_max_over_real_max": float(np.abs(im[:, col]).max()
                                                  / np.abs(re[:, col]).max())}
    dph = np.angle(np.exp(1j*(r["default"]["phase"] - r["new_time"]["phase"])))
    r["phase_default_minus_new_time"] = float(dph)
    r["omega_dt_expected"] = 2*np.pi/128.0
    r["ratio_to_expected"] = float(dph/(2*np.pi/128.0))
    res["weyl"] = r
    print("weyl:", r)
    return series


def figures(res, out, series):
    fs.use_style()
    C = fs.PAL
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    a1 = fs.inch_axes(fig, 0.7, 0.55, 3.0, 2.5)
    a2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
    made = []
    if "bin" in res:
        ln = res["bin"]["line"]
        x = np.array(ln["x"])
        a1.plot(x, ln["hxx_double"], "-", color=C["blue"],
                label=r"$(\tilde\gamma_{xx}-1)/A$, double_precision = true")
        a1.plot(x, ln["hxx_single"], "o", ms=3.5, color=C["red"],
                label=r"$(\tilde\gamma_{xx}-1)/A$, default (float32)")
        a1.plot(x, ln["hxy_double"], "--", color=C["blue"], label=r"$\tilde\gamma_{xy}/A$, double")
        a1.plot(x, ln["hxy_single"], "s", ms=3.5, mfc="none", color=C["red"],
                label=r"$\tilde\gamma_{xy}/A$, float32")
        a1.set_xlabel("x (first line of cells in y and z)")
        a1.set_ylabel(f"bin dump at t = {ln['time']:.3f}, A = 1e-6")
        a1.set_ylim(-1.5, 2.1)
        a1.legend(loc="upper center", fontsize=6.5)
    if series:
        for tag, col, lab in (("default", C["blue"], "default (upstream labels)"),
                              ("new_time", C["red"], "waveform_at_new_time = true")):
            t, s = series[tag]
            w = res["weyl"][tag]
            a2.plot(t, s/w["amplitude"], "o" if tag == "default" else "s", ms=3,
                    mfc=("none" if tag == "new_time" else col), color=col, label=lab)
            tt = np.linspace(0.0, 0.5, 400)
            a2.plot(tt, np.cos(2*np.pi*tt + w["phase"]), color=col, lw=1.0)
        a2.set_xlim(0.0, 0.5)
        a2.set_xlabel("time label of the row in waveforms/rpsi4_real_00.3.txt")
        a2.set_ylabel(r"largest mode of $r\Psi_4$ / amplitude")
        a2.text(0.03, 0.05, r"phase lead of the default: %.4f rad ($\omega\,dt$ = %.4f)"
                % (res["weyl"]["phase_default_minus_new_time"],
                   res["weyl"]["omega_dt_expected"]), transform=a2.transAxes, fontsize=7)
        a2.legend(loc="upper right", fontsize=7)
    made += fs.save(fig, os.path.join(out, "t2_output"))
    plt.close(fig)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe-new", required=True)
    ap.add_argument("--exe-base", required=True)
    ap.add_argument("--t1-dir", default="")
    ap.add_argument("--bdir", default=bc.B_DEFAULT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--regress-report", default="")
    ap.add_argument("--stages", default="bin,padding,weyl,regress")
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    B = bc.track_b(a.bdir)
    exe = {"new": os.path.abspath(a.exe_new), "base": os.path.abspath(a.exe_base)}
    res = {"meta": {"exe": exe, "commit": bc.git_rev(), "t1_dir": a.t1_dir}}
    st = a.stages.split(",")
    series = None
    if "bin" in st:
        stage_bin(res, B, exe, out)
    if "padding" in st:
        stage_padding(res, B, exe, out)
    if "weyl" in st and a.t1_dir:
        series = stage_weyl(res, a.t1_dir)
    if "regress" in st and a.regress_report:
        stage_regress(res, a.regress_report)
    bc.save_json(res, os.path.join(out, "results_t2.json"))
    print("figures:", figures(res, out, series))


if __name__ == "__main__":
    main()
