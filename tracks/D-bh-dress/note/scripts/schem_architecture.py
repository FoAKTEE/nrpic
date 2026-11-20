"""Schematic: architecture of Track D's calculation (note v1, gate G1 item C9).

Three states. Exists = in this repository's AthenaK release core-v0.3 on main, or in the
track's own reference and analysis code; provided by core = on a tested branch of core with
a published executable and a READY file (scratch/core/exe/<branch>/READY); new for Track D
= still to be built or run by the track (inside AthenaK by core, decision 0010, or outside
it as reference and analysis). Below the columns: the chain of runs toward the growth law
and the null test, and the deliverables.

Sources of the classification: CLAUDE.md (release core-v0.3: format-2 tables, punctures,
Newtonian mode), coord/INTERFACES/*.md; scratch/core/exe/core_requests-adf/READY (items 1,
3, 4, 5: tracer rule, analytic-metric excision, removal record and flux spheres, point
mass), core_gauge/READY (option 1, lapse_leak), core_build-openmp/READY (threaded processor
build); the track's packages es_runs, flux_tools, spike, secondary_infall,
puncture_drift and PLAN-wave3.md (round 1). No data are read. A label that is wider than
its block is reported on stdout ("label wider than its block").
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
EXISTS, CORE, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 30.0, 17.5
TOP = H - 0.85
LABELS = []          # (text artist, x0, width) of every block, for the width check


def block(ax, x, y, w, h, label, fill, size=7.0, tcolor=pf.WHITE, edge="none", lw=0.0, radius=0.22):
    pf.rbox(ax, x, y, w, h, fill=fill, edge=edge, lw=lw, radius=radius, z=3)
    t = pf.text(ax, x + w / 2, y + h / 2, label, size=size, color=tcolor)
    LABELS.append((t, x, w))


def column(ax, x, title, sub, items, top=TOP, step=1.0, bh=0.84):
    n = len(items)
    y_bot = top - 1.75 - n * step
    pf.panel(ax, x, y_bot, 9.4, top - y_bot, radius=0.9)
    pf.text(ax, x + 4.7, top - 0.5, title, size=9.5, bold=True)
    pf.text(ax, x + 4.7, top - 1.1, sub, size=7.3, italic=True)
    y = top - 1.75
    for label, state in items:
        block(ax, x + 0.4, y - bh, 8.6, bh, label, state)
        y -= step
    return y_bot


def check_widths(fig, ax):
    fig.canvas.draw()
    inv = ax.transData.inverted()
    bad = []
    for t, x0, w in LABELS:
        bb = t.get_window_extent()
        (xa, _), (xb, _) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
        if xa < x0 + 0.1 or xb > x0 + w - 0.1:
            bad.append((t.get_text(), round(xb - xa, 2), w))
    for b in bad:
        print(f"{STEM}: label wider than its block: {b}")
    print(f"{STEM}: {len(LABELS)} labels checked, {len(bad)} wider than their block")


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    y1 = column(ax, 0.2, "Initial data", "conformally flat tables, particles", [
        ("vacuum bubble in expanding dust (tables)", EXISTS),
        ("punctures with momentum and spin", EXISTS),
        ("lattice dust; vacuum control table", EXISTS),
        ("tracers of zero mass on timelike orbits", CORE),
        ("dust reaching the black hole", NEW),
        ("warm dust: velocity dispersion", NEW),
        ("puncture in a periodic dust box", NEW),
    ])
    y2 = column(ax, 10.3, "Evolution", "AthenaK: Z4c, particles, Newtonian mode", [
        ("Z4c with particles; 1+log, Gamma driver", EXISTS),
        ("moving puncture, horizon finder, removal", EXISTS),
        ("Newtonian mode; geodesics on analytic Kerr", EXISTS),
        ("record of removed particles", CORE),
        ("flux through spheres around the black hole", CORE),
        ("excision on an analytic metric", CORE),
        ("fixed point mass in the Newtonian mode", CORE),
        ("lapse that relaxes in expanding dust", CORE),
        ("threaded processor build", CORE),
    ])
    y3 = column(ax, 20.4, "Analysis", "references and reading of the output", [
        ("exact bubble: wall, infall, constant mass", EXISTS),
        ("probe-limit spike: Schwarzschild and Kerr", EXISTS),
        ("self-similar infall, matched shells", EXISTS),
        ("horizon-mass floor of a vacuum puncture", EXISTS),
        ("tracer areal radius and proper time", EXISTS),
        ("growth against the integrated flux", NEW),
        ("controls of the late horizon drift", NEW),
        ("coupling exponent and its upper limit", NEW),
    ])
    ybot = min(y1, y2, y3)
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, TOP - 5.6), (x1, TOP - 5.6), lw=1.2, head=8)

    # chain of runs toward the science runs
    yc = 3.7
    assert ybot >= yc + 2.1, ybot
    pf.text(ax, 0.6, yc + 1.45, "runs toward the growth law and the null test", size=7.5,
            italic=True, ha="left")
    chain = [("bubble data", "done", pf.GREEN_DARK, pf.WHITE, 3.6),
             ("bubble run, vacuum control", "done", pf.GREEN_DARK, pf.WHITE, 5.6),
             ("relaxed lapse", "ran; analysed now", pf.OLIVE, pf.WHITE, 3.9),
             ("late-drift controls", "pending", pf.GREY_FILL, pf.INK, 4.4),
             ("dust to the black hole", "pending", pf.GREY_FILL, pf.INK, 4.6),
             ("growth law, null test", "goal", pf.PLUM, pf.WHITE, 4.5)]
    gap = (29.6 - 0.4 - sum(c[4] for c in chain)) / (len(chain) - 1)
    x = 0.4
    for i, (lab, state, fill, tc, w) in enumerate(chain):
        edge = pf.GREY_LINE if fill == pf.GREY_FILL else "none"
        block(ax, x, yc, w, 0.9, lab, fill, size=7.0, tcolor=tc, edge=edge,
              lw=0.9 if edge != "none" else 0.0, radius=0.45)
        pf.text(ax, x + w / 2, yc - 0.42, state, size=6.6, color=pf.ROSE, italic=True)
        if i < len(chain) - 1:
            pf.arrow(ax, (x + w + 0.08, yc + 0.45), (x + w + gap - 0.08, yc + 0.45), lw=1.0, head=7)
        x += w + gap

    # deliverables
    yd = 1.6
    labels = ["growth law of the black hole", "spike in the strong field",
              "null test of coupling", "dressed binaries"]
    widths = [8.0, 7.0, 6.2, 5.2]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, yd, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        LABELS.append((ax.texts[-1], x, w))
        x += w + 0.55
    pf.text(ax, 0.6, yd - 0.55, "deliverables of the track", size=7.5, italic=True, ha="left")
    pf.panel(ax, 12.0, 0.15, 17.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((12.5, EXISTS, "exists"), (16.4, CORE, "provided by core"),
                         (23.3, NEW, "new for Track D")):
        pf.rbox(ax, x0, 0.35, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.63, lab, size=7.5, bold=True, ha="left")
    check_widths(fig, ax)
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
