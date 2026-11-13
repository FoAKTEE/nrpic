"""Dust collapse: the particles at about six times, projected onto the x-z plane and
coloured by their initial coordinate radius (particles identified by tag).

    python3 os_snapshots.py <label>=<rundir> [...] [--times t1,t2,...] [--base os]
                            [--out NAME]

Rows are runs, columns are times. Without --times, six times evenly spaced between 0
and the last snapshot that still holds particles (over all runs); each panel shows
the snapshot nearest to the column time (within 0.6 M), or says that there is none.
Inner particles are drawn on top, so with nested shells the colour at a projected
radius belongs to the innermost shell that reaches it. Each column has its own extent
(given by the scale bar); the black circle is the apparent horizon (mean coordinate
radius) when one was found within 0.25 M of the snapshot time; the column extent then
includes it. The particle number is printed when it differs from the initial one.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from common import FIGS, initial_radius_by_tag, parse_cli, read_horizon, read_snapshot, \
    run_path, snapshot_files, snapshot_times
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("times", "base", "out"))
base = opts.get("base", "os")
out = opts.get("out", "os_snapshots")

info = []
for label, d in runs:
    files = snapshot_files(d, base)
    if not files:
        print(f"{label}: no snapshots in {d}, skipped")
        continue
    ts = snapshot_times(files)
    nps = np.array([int(np.fromfile(f, dtype=np.int64, count=3)[2]) for f in files])
    r0 = initial_radius_by_tag(d, base, files)
    ah = read_horizon(run_path(d, f"{base}.horizon_summary_0.txt"))
    info.append(dict(label=label, files=files, t=ts, n=nps, r0=r0, ah=ah))
    last = ts[nps > 0].max()
    print(f"{label}: {len(files)} snapshots, t = {ts[0]:.2f} .. {ts[-1]:.2f}, "
          f"last with particles t = {last:.2f}")
if not info:
    sys.exit("nothing to plot")

if "times" in opts:
    times = [float(v) for v in opts["times"].split(",")]
else:
    # six snapshot times of the run that keeps particles longest, evenly spread
    ref = max(info, key=lambda i: i["t"][i["n"] > 0].max())
    tr = ref["t"][ref["n"] > 0]
    times = [tr[np.argmin(np.abs(tr - x))] for x in np.linspace(0.0, tr.max(), 6)]

# pick snapshots and the extent of each column
picks = []
for i in info:
    row = []
    for tc in times:
        k = int(np.argmin(np.abs(i["t"] - tc)))
        ok = abs(i["t"][k] - tc) <= 0.6 and i["n"][k] > 0
        row.append(k if ok else None)
    picks.append(row)
ext = []
for j, tc in enumerate(times):
    e = 0.0
    for i, row in zip(info, picks):
        if row[j] is not None:
            t, a, _, _ = read_snapshot(i["files"][row[j]])
            e = max(e, np.abs(a[:, [0, 2]]).max())
            ah = i["ah"]
            if len(ah) and (np.abs(ah[:, 0] - t) < 0.25).any():
                m = np.abs(ah[:, 0] - t) < 0.25
                e = max(e, ah[m][np.argmin(np.abs(ah[m, 0] - t)), 5])
    ext.append(1.22 * e if e > 0 else 1.0)

nr, nc = len(info), len(times)
P, G, LEFT, BOT = 1.12, 0.04, 0.42, 0.08
fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, BOT + nr * P + (nr - 1) * G + 0.3))
r0max = max(np.nanmax(i["r0"]) for i in info)
norm = Normalize(0.0, r0max)
cmap = fs.truncate_cmap("viridis", 0.05, 0.95)
for a, (i, row) in enumerate(zip(info, picks)):
    y = BOT + (nr - 1 - a) * (P + G)
    for j, (tc, k) in enumerate(zip(times, row)):
        ax = fs.inch_axes(fig, LEFT + j * (P + G), y, P, P)
        L = ext[j]
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        if a == 0:
            ax.set_title(rf"$t={tc:.0f}\,M$", fontsize="medium", pad=3)
        if j == 0:
            ax.text(-0.06, 0.5, i["label"], transform=ax.transAxes, rotation=90,
                    ha="right", va="center")
        if k is None:
            msg = "no snapshot" if np.abs(i["t"] - tc).min() > 0.6 else "all excised"
            ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha="center", va="center",
                    color="grey")
            continue
        t, p, tag, _ = read_snapshot(i["files"][k])
        r0 = i["r0"][tag]
        o = np.argsort(-r0)              # outer first, inner particles on top
        ax.scatter(p[o, 0], p[o, 2], c=r0[o], s=1.0, lw=0, cmap=cmap, norm=norm,
                   rasterized=True)
        ah = i["ah"]
        if len(ah):
            m = np.abs(ah[:, 0] - t) < 0.25
            if m.any():
                rah = ah[m][np.argmin(np.abs(ah[m, 0] - t)), 5]
                ax.add_patch(plt.Circle((0, 0), rah, fill=False, **fs.THIN))
        if abs(t - tc) > 0.05:
            ax.text(0.04, 0.96, f"t = {t:.1f}", transform=ax.transAxes, va="top",
                    fontsize="small")
        if len(tag) != i["n"][0]:
            ax.text(0.96, 0.96, f"N = {len(tag)}", transform=ax.transAxes, va="top",
                    ha="right", fontsize="small")
        # scale bar: a round length near 40 percent of the panel half-width
        s = 10 ** np.floor(np.log10(0.8 * L))
        s = max(v * s for v in (1, 2, 5) if v * s <= 0.8 * L)
        x1 = L * 0.92
        ax.plot([x1 - s, x1], [-0.86 * L] * 2, color="k", lw=1.5)
        ax.text(x1 - s / 2, -0.82 * L, f"{s:g} M", ha="center", va="bottom",
                fontsize="small")
cax = fs.inch_axes(fig, LEFT + nc * (P + G) + 0.04, BOT, 0.08, nr * P + (nr - 1) * G)
cb = fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label(r"initial radius $r_0\,[M]$")
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
