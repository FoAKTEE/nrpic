#!/usr/bin/env python3
"""Readers for every output file of the NRPIC module, written from the layouts in
tracks/core/interfaces/diagnostics.md and particle_id.md, and the check of test D1
(tracks/core/interfaces/JOURNAL.md).

    python3 read_outputs.py RUN1 RUN2 PARTICLE_FILE FIGDIR

RUN1 is the uninterrupted run, RUN2 the run restarted from RUN1/rst/<base>.00001.rst.
Prints one line per check (PASS/FAIL) and writes summary.json and two figures.
"""
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "python")))


# ------------------------------------------------------------------------------------
# readers (layouts of diagnostics.md and particle_id.md)
# ------------------------------------------------------------------------------------
def read_nrp(path):
    """Particle input file: 'NRPIC001', int64 N, N x 7 float64 (x y z u_x u_y u_z m),
    N int32 species."""
    with open(path, "rb") as f:
        magic = f.read(8)
        n = struct.unpack("<q", f.read(8))[0]
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        sp = np.frombuffer(f.read(4 * n), dtype="<i4")
        rest = f.read()
    return dict(magic=magic, n=n, rec=rec, species=sp, trailing=len(rest))


def read_text_hst(path):
    """Text history: '#' lines are header; the last header line names the columns as
    [k]=name. Returns (names, array)."""
    names, rows = [], []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                toks = [t for t in line[1:].split() if t.startswith("[")]
                if toks:
                    names = [t.split("=", 1)[1] for t in toks]
                continue
            if line.strip():
                rows.append([float(v) for v in line.split()])
    return names, np.array(rows)


def read_snapshot(path):
    """'NRPSNAP1', float64 time, int64 N, int64 cycle, N x 7 float64 (x^i u_i m),
    N int32 tag, N int32 species, N float64 proper time."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t = struct.unpack("<d", f.read(8))[0]
        n, cyc = struct.unpack("<qq", f.read(16))
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype="<i4")
        sp = np.frombuffer(f.read(4 * n), dtype="<i4")
        tau = np.frombuffer(f.read(8 * n), dtype="<f8")
        rest = f.read()
    return dict(magic=magic, t=t, n=n, cycle=cyc, rec=rec, tag=tag, species=sp,
                tau=tau, trailing=len(rest))


def read_records(path, nd):
    a = np.fromfile(path, dtype="<f8")
    return a.reshape(-1, nd), a.size % nd


def read_field(path):
    """'NRFIELD1' or 'NRFIELD2', float64 time, 3 int64 (n1 n2 n3), float32 E and chi
    (first index fastest); NRFIELD2 adds 7 float64 arrays H, M_x, M_y, M_z, Khat,
    Theta, alpha."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t = struct.unpack("<d", f.read(8))[0]
        n1, n2, n3 = struct.unpack("<qqq", f.read(24))
        nc = n1 * n2 * n3
        shp = (n3, n2, n1)
        out = dict(magic=magic, t=t, dims=(n1, n2, n3))
        out["E"] = np.frombuffer(f.read(4 * nc), dtype="<f4").reshape(shp)
        out["chi"] = np.frombuffer(f.read(4 * nc), dtype="<f4").reshape(shp)
        if magic == b"NRFIELD2":
            for name in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[name] = np.frombuffer(f.read(8 * nc), dtype="<f8").reshape(shp)
        out["trailing"] = len(f.read())
    return out


def read_curv_slice(path):
    """'NRPCURV1', float64 time, int64 nrec, nrec x 7 float64
    (x, z, dx, I, E, alpha, sqrt(gamma))."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t = struct.unpack("<d", f.read(8))[0]
        n = struct.unpack("<q", f.read(8))[0]
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        rest = f.read()
    return dict(magic=magic, t=t, n=n, rec=rec, trailing=len(rest))


def read_prt(path):
    """Particle restart file, format NRPRST05: magic, int64 N, 7 float64 state,
    4 int64 counters, N x 7 float64, N x 3 int32 (gid tag species), N float64 tau,
    24 float64 probe state, 9 float64 probe lapse history, float64 previous step,
    int64 has_ts, [5 int64 dims, prod(dims) float64 source densities]."""
    with open(path, "rb") as f:
        magic = f.read(8)
        n = struct.unpack("<q", f.read(8))[0]
        dstate = struct.unpack("<7d", f.read(56))
        istate = struct.unpack("<4q", f.read(32))
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        ids = np.frombuffer(f.read(12 * n), dtype="<i4").reshape(n, 3)
        tau = np.frombuffer(f.read(8 * n), dtype="<f8")
        pstate = struct.unpack("<24d", f.read(192))
        aold = struct.unpack("<9d", f.read(72))
        dtold = struct.unpack("<d", f.read(8))[0]
        has_ts = struct.unpack("<q", f.read(8))[0]
        dims, ts = None, None
        if has_ts == 1:
            dims = struct.unpack("<5q", f.read(40))
            ts = np.frombuffer(f.read(8 * int(np.prod(dims))), dtype="<f8")
        rest = f.read()
    return dict(magic=magic, n=n, dstate=dstate, istate=istate, rec=rec, ids=ids,
                tau=tau, pstate=pstate, aold=aold, dtold=dtold, has_ts=has_ts,
                dims=dims, ts=ts, trailing=len(rest))


# ------------------------------------------------------------------------------------
# check of test D1
# ------------------------------------------------------------------------------------
def main():
    run1, run2, pfile, figdir = sys.argv[1:5]
    base = "flrw"
    N, n = 4096, 16
    res = {}
    ok_all = True

    def check(key, cond, info):
        nonlocal ok_all
        res[key] = dict(ok=bool(cond), info=info)
        ok_all = ok_all and bool(cond)
        print(("PASS " if cond else "FAIL ") + key + ": " + str(info))

    p = read_nrp(pfile)
    check("nrp", p["magic"] == b"NRPIC001" and p["n"] == N and p["trailing"] == 0,
          dict(magic=p["magic"].decode(), n=p["n"], trailing=p["trailing"]))
    msum = float(p["rec"][:, 6].sum())

    # 1. history
    names, h = read_text_hst(os.path.join(run1, base + ".nrpic.hst"))
    check("hst_columns", len(names) == 38 and h.shape == (9, 38),
          dict(ncol_header=len(names), shape=list(h.shape), last=names[-1]))
    c = {nm: i for i, nm in enumerate(names)}
    rel_m = float(np.max(np.abs(h[:, c["sum_m"]] / msum - 1.0)))
    rel_e = float(np.max(np.abs(h[:, c["int_E"]] / h[:, c["sum_mW"]] - 1.0)))
    same_f = bool(np.all(h[:, c["int_E_filtered"]] == h[:, c["int_E"]]))
    check("hst_sum_m", rel_m < 1e-14, dict(max_rel=rel_m))
    check("hst_int_E", rel_e < 1e-13, dict(max_rel=rel_e))
    check("hst_filtered_equal", same_f, dict(equal=same_f))

    # 2. constraint statistics
    names_c, cs = read_text_hst(os.path.join(run1, base + ".cstat.hst"))
    check("cstat", cs.shape == (9, 16) and len(names_c) == 16,
          dict(ncol_header=len(names_c), shape=list(cs.shape), names=names_c))

    # 3. conservation records
    names_k, ck = read_text_hst(os.path.join(run1, base + ".cons.hst"))
    t_k = ck[:, 0].tolist()
    check("cons", ck.shape == (7, 7) and abs(t_k[0] - 0.0625) < 1e-12
          and abs(t_k[-1] - 0.4375) < 1e-12, dict(shape=list(ck.shape), t=t_k))

    # 4. line records
    with open(os.path.join(run1, base + ".line.txt")) as f:
        lt = [ln for ln in f if not ln.startswith("#")]
    nline = int(lt[0])
    xc = np.array([float(v) for v in lt[1:]])
    lb, extra = read_records(os.path.join(run1, base + ".line.bin"), 1 + 5 * nline)
    check("line", nline == n and abs(xc[0] - 0.125) < 1e-12 and abs(xc[-1] - 3.875) < 1e-12
          and lb.shape == (9, 81) and extra == 0,
          dict(n=nline, x0=float(xc[0]), x1=float(xc[-1]), shape=list(lb.shape)))

    # 5. field dumps
    fd = []
    for k in (0, 1):
        fdk = read_field(os.path.join(run1, f"{base}.field.{k:05d}.bin"))
        fd.append(fdk)
        check(f"field_{k}", fdk["magic"] == b"NRFIELD2" and fdk["dims"] == (n, n, n)
              and fdk["trailing"] == 0, dict(magic=fdk["magic"].decode(), t=fdk["t"],
                                             dims=fdk["dims"]))

    # 6. trajectories
    tr, e1 = read_records(os.path.join(run1, base + ".traj.bin"), 8)
    tm, e2 = read_records(os.path.join(run1, base + ".trajmet.bin"), 17)
    same_tt = bool(np.array_equal(tr[:, :2], tm[:, :2]))
    check("traj", tr.shape == (90, 8) and tm.shape == (90, 17) and e1 == 0 and e2 == 0
          and same_tt, dict(traj=list(tr.shape), trajmet=list(tm.shape),
                            same_time_tag=same_tt, tags=sorted(set(tr[:, 1].astype(int)))))

    # 7. snapshots
    snaps = []
    for k in (0, 1, 2):
        s = read_snapshot(os.path.join(run1, f"{base}.part.{k:05d}.bin"))
        snaps.append(s)
        mass_ok = bool(np.array_equal(np.sort(s["rec"][:, 6]), np.sort(p["rec"][:, 6])))
        check(f"snap_{k}", s["magic"] == b"NRPSNAP1" and s["n"] == N and s["trailing"] == 0
              and mass_ok, dict(t=s["t"], cycle=s["cycle"], masses_equal=mass_ok,
                                tau_range=[float(s["tau"].min()), float(s["tau"].max())]))

    # 8. curvature
    names_v, cv = read_text_hst(os.path.join(run1, base + ".curv.hst"))
    check("curv_hst", cv.shape == (3, 10), dict(shape=list(cv.shape), names=names_v))
    cslices = []
    for k in (0, 1, 2):
        cs_k = read_curv_slice(os.path.join(run1, f"{base}.curv.{k:05d}.bin"))
        cslices.append(cs_k)
        check(f"curv_slice_{k}", cs_k["magic"] == b"NRPCURV1" and cs_k["n"] == n * n
              and cs_k["trailing"] == 0, dict(t=cs_k["t"], n=cs_k["n"]))

    # 9. particle restart files
    for k in (0, 1, 2):
        r = read_prt(os.path.join(run1, "rst", f"{base}.{k:05d}.rst.prt"))
        check(f"prt_{k}", r["magic"] == b"NRPRST05" and r["n"] == N and r["has_ts"] == 1
              and r["dims"] == (8, 10, 16, 16, 16) and r["trailing"] == 0,
              dict(n=r["n"], has_ts=r["has_ts"], dims=r["dims"], dtold=r["dtold"],
                   tau_probe=r["dstate"][0]))

    # 10. restart: records after t = 0.25 equal
    _, h2 = read_text_hst(os.path.join(run2, base + ".nrpic.hst"))
    t1 = h[:, 0]
    rows = []
    for row in h2:
        j = int(np.argmin(np.abs(t1 - row[0])))
        rows.append(bool(np.array_equal(row, h[j])))
    check("restart_hst", h2.shape[0] == 4 and all(rows),
          dict(records=int(h2.shape[0]), identical=rows))
    _, cs2 = read_text_hst(os.path.join(run2, base + ".cstat.hst"))
    rows_c = [bool(np.array_equal(row, cs[int(np.argmin(np.abs(cs[:, 0] - row[0])))]))
              for row in cs2]
    check("restart_cstat", all(rows_c), dict(identical=rows_c))
    s2 = read_snapshot(os.path.join(run2, f"{base}.part.00002.bin"))
    same_snap = bool(np.array_equal(s2["rec"], snaps[2]["rec"])
                     and np.array_equal(s2["tau"], snaps[2]["tau"]))
    check("restart_snapshot", same_snap, dict(identical=same_snap))

    # 11. physics for the figure: probe lapse against a(t) = (1 + t/2)^2
    a_ex = (1.0 + 0.5 * h[:, 0]) ** 2
    rel_a = float(abs(h[-1, c["alpha_probe"]] / a_ex[-1] - 1.0))
    check("lapse_vs_a", rel_a < 1e-3, dict(rel_at_end=rel_a))

    res["all_ok"] = ok_all
    os.makedirs(figdir, exist_ok=True)
    with open(os.path.join(figdir, "d1_summary.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    make_figures(h, c, cs, names_c, fd, cslices, figdir)
    print("ALL PASS" if ok_all else "SOME CHECKS FAILED")


def make_figures(h, c, cs, names_c, fd, cslices, figdir):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    t = h[:, 0]
    a_ex = (1.0 + 0.5 * t) ** 2
    fig, axs = plt.subplots(3, 1, figsize=(fs.FULL_WIDTH / 2, 6.0), sharex=True)
    fig.subplots_adjust(left=0.22, right=0.96, bottom=0.08, top=0.97, hspace=0.0)
    ax = axs[0]
    for k, lab, col in ((c["alpha_probe"], "probe 0", fs.PAL["red"]),
                        (c["alpha_probe1"], "probe 1", fs.PAL["yellow"]),
                        (c["alpha_probe2"], "probe 2", fs.PAL["green"])):
        ax.plot(t, h[:, k] / a_ex - 1.0, color=col, label=lab)
    ax.axhline(0.0, **fs.GUIDE)
    ax.set_ylabel(r"$\alpha/a - 1$")
    ax.legend(ncol=1)
    ax = axs[1]
    ax.semilogy(t, np.abs(h[:, c["int_E"]] / h[:, c["sum_mW"]] - 1.0) + 1e-17,
                color=fs.PAL["red"], marker="o", ms=3, label=r"$|\int E\sqrt{\gamma}dV/\sum mW-1|$")
    ax.semilogy(t, np.abs(h[:, c["sum_m"]] / h[0, c["sum_m"]] - 1.0) + 1e-17,
                color=fs.PAL["blue"], ls="--", marker="s", ms=3, label=r"$|\sum m/\sum m_0-1|$")
    ax.set_ylabel("relative error")
    ax.set_ylim(1e-18, 1e-12)
    ax.legend()
    ax = axs[2]
    ic = {nm: i for i, nm in enumerate(names_c)}
    ax.semilogy(cs[:, 0], cs[:, ic["Hr_mean"]], color=fs.PAL["red"], label=r"$H_r$ mean")
    ax.semilogy(cs[:, 0], cs[:, ic["Mr_mean"]], color=fs.PAL["red"], ls="--",
                label=r"$M_r$ mean")
    ax.set_ylabel("constraint (relative)")
    ax.set_xlabel(r"$t$", labelpad=-2)
    ax.legend()
    fs.save(fig, os.path.join(figdir, "d1_history"))
    plt.close(fig)

    # slices of the field dump at t = 0.25 and of the curvature cut at t = 0.25
    f1 = fd[1]
    k0 = 4
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.06, right=0.94, bottom=0.17, top=0.88, wspace=0.45)
    ext = [0, 4, 0, 4]
    e = f1["E"][:, k0, :]          # z, x at y index k0
    im = axs[0].imshow(e / e.mean() - 1.0, origin="lower", extent=ext, cmap="RdBu_r",
                       vmin=-np.abs(e / e.mean() - 1).max(), vmax=np.abs(e / e.mean() - 1).max(),
                       interpolation="none", rasterized=True)
    axs[0].set_title(r"$E/\langle E\rangle-1$, $t=%.3g$" % f1["t"])
    fs.side_colorbar(fig, axs[0], im, "")
    hh = f1["H"][:, k0, :]
    im = axs[1].imshow(hh, origin="lower", extent=ext, cmap="RdBu_r",
                       vmin=-np.abs(hh).max(), vmax=np.abs(hh).max(), interpolation="none",
                       rasterized=True)
    axs[1].set_title(r"$\mathcal{H}$, $t=%.3g$" % f1["t"])
    fs.side_colorbar(fig, axs[1], im, "")
    cr = cslices[1]["rec"]
    xs, zs, kr = cr[:, 0], cr[:, 1], cr[:, 3]
    ix = np.round((xs - 0.125) / 0.25).astype(int)
    iz = np.round((zs - 0.125) / 0.25).astype(int)
    img = np.full((16, 16), np.nan)
    img[iz, ix] = kr
    im = axs[2].imshow(img, origin="lower", extent=ext, cmap="magma", interpolation="none",
                       rasterized=True)
    axs[2].set_title(r"$I$ on $y=1$, $t=%.3g$" % cslices[1]["t"])
    fs.side_colorbar(fig, axs[2], im, "")
    for ax in axs:
        ax.set_xlabel(r"$x$")
        ax.set_aspect("equal")
    axs[0].set_ylabel(r"$z$")
    fs.save(fig, os.path.join(figdir, "d1_slices"))
    plt.close(fig)


if __name__ == "__main__":
    main()
