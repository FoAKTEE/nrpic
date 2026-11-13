"""Row of 3D scatter panels of the particles at chosen times, coloured by the initial
coordinate radius (particles identified by tag), for paper-style figures.

    python3 snapshots_3d.py <rundir> --times t1,t2,... [--base os] [--elev 22]
                            [--azim -60] [--common] [--cut] [--s S] [--out NAME]

Each panel shows the snapshot nearest to the requested time (its time is printed).
All panels use the same view angle and an equal-aspect cube centred on the origin;
by default each cube is scaled to its particles and the length of the black bar
(drawn along the screen-horizontal direction, so at its true length) is printed
next to it; --common uses the largest cube for every panel. --cut removes
the half of the particles nearer to the viewer (cut by the plane through the
origin normal to the viewing direction), which shows the interior. --s sets the marker area in points^2 (default from N).
"""
import glob
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from common import FIGS, initial_radius_by_tag, parse_cli, read_snapshot, run_path, \
    snapshot_files, snapshot_times
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("times", "base", "elev", "azim", "s", "out"))
if not runs or "times" not in opts:
    sys.exit(__doc__)
label, d = runs[0]
base = opts.get("base")
if base is None:      # the basename of the first snapshot file found
    found = sorted(glob.glob(run_path(d, "*.part.[0-9][0-9][0-9][0-9][0-9].bin")))
    if not found:
        sys.exit(f"no snapshots in {d}")
    base = re.sub(r"\.part\.\d{5}\.bin$", "", os.path.basename(found[0]))
out = opts.get("out", f"snapshots_3d_{label}")
elev, azim = float(opts.get("elev", 22)), float(opts.get("azim", -60))
want = [float(v) for v in opts["times"].split(",")]

files = snapshot_files(d, base)
ts = snapshot_times(files)
r0 = initial_radius_by_tag(d, base, files)
panels = []
for tw in want:
    k = int(np.argmin(np.abs(ts - tw)))
    t, p, tag, _ = read_snapshot(files[k])
    if abs(ts[k] - tw) > 0.5 * max(np.diff(ts).max() if len(ts) > 1 else 1.0, 1e-12):
        print(f"t = {tw}: nearest snapshot is t = {ts[k]:.3f}")
    if "cut" in opts:
        e, a = np.radians(elev), np.radians(azim)
        view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        keep = p[:, :3] @ view <= 0.0
        p, tag = p[keep], tag[keep]
    half = 1.05 * np.abs(p[:, :3]).max() if len(tag) else 1.0
    panels.append(dict(t=t, p=p, tag=tag, half=half))
    print(f"t = {t:.3f}: N = {len(tag)}, max |x_i| = {half / 1.05 if len(tag) else 0:.4f}")
if "common" in opts:
    hmax = max(q["half"] for q in panels)
    for q in panels:
        q["half"] = hmax

n = len(panels)
fs.use_style()
W, PH, CB = fs.FULL_WIDTH, 1.95, 0.75
pw = (W - CB) / n
fig = plt.figure(figsize=(W, PH + 0.1))
norm = Normalize(0.0, np.nanmax(r0))
cmap = fs.truncate_cmap("viridis", 0.05, 0.95)
s = float(opts.get("s", max(0.15, min(4.0, 6000.0 / max(len(r0), 1)))))
for j, q in enumerate(panels):
    ax = fig.add_axes([j * pw / W, 0.0, pw / W, PH / (PH + 0.1)], projection="3d")
    ax.set_proj_type("ortho")
    h = q["half"]
    if len(q["tag"]):
        rr = r0[q["tag"]]
        # draw far particles first (painter's order along the viewing direction)
        e, a = np.radians(elev), np.radians(azim)
        view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        o = np.argsort(q["p"][:, :3] @ view)
        ax.scatter(q["p"][o, 0], q["p"][o, 1], q["p"][o, 2], c=rr[o], cmap=cmap,
                   norm=norm, s=s, lw=0, depthshade=False, rasterized=True)
    else:
        ax.text2D(0.5, 0.5, "no particles", transform=ax.transAxes, ha="center",
                  color="grey")
    ax.set_xlim(-h, h)
    ax.set_ylim(-h, h)
    ax.set_zlim(-h, h)
    ax.set_box_aspect((1, 1, 1), zoom=1.3)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    # scale bar below the cloud, along the screen-horizontal direction (true length
    # in the orthographic projection)
    L = 10 ** np.floor(np.log10(h))
    L = max(v * L for v in (1, 2, 5) if v * L <= 1.0 * h)
    eh = np.array([-np.sin(np.radians(azim)), np.cos(np.radians(azim)), 0.0])
    c0 = np.array([0.0, 0.0, -1.3 * h])
    b0, b1 = c0 - 0.5 * L * eh, c0 + 0.5 * L * eh
    ax.plot([b0[0], b1[0]], [b0[1], b1[1]], [b0[2], b1[2]], color="k", lw=1.5)
    ax.text(*(b1 + 0.08 * h * eh), f"{L:g} M", ha="left", va="center", zdir=None)
    ax.text2D(0.5, 1.0, rf"$t={q['t']:.1f}\,M$", transform=ax.transAxes, ha="center",
              va="top")
cax = fig.add_axes([(W - CB + 0.12) / W, 0.1, 0.09 / W, 0.8])
cb = fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label(r"initial radius $r_0\,[M]$")
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
