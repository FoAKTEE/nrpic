#!/usr/bin/env python3
"""Schematic of core's verification ladder (C3 of the core sheet; brief section 10, rows
marked CORE) with the verdict of each row, for stage check C8.

Style: /sleep-paper-figure-style (paperfig.py, copied here from harness/style/).
Status colours (legend): green = PASS, slate = PARTIAL, red = open or blocked.
Verdicts and evidence lines are read from ladder_status.json next to this script, so the
figure follows LADDER.md without editing the drawing code.

    python3 schem_ladder.py [--out tracks/core/verify/figs/schem_ladder]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paperfig as pf  # noqa: E402

COL = {"PASS": pf.GREEN_DARK, "PARTIAL": pf.SLATE, "OPEN": pf.RED, "BLOCKED": pf.RED,
       "FAIL": pf.RED}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "figs", "schem_ladder"))
    a = ap.parse_args()
    st = json.load(open(os.path.join(HERE, "ladder_status.json")))
    rows = st["rows"]

    fig, ax = pf.canvas(38, 16.6)
    pf.legend_box(ax, 9.0, 15.0, 20.0, 1.1,
                  [("pill:" + pf.GREEN_DARK, "PASS"), ("pill:" + pf.SLATE, "PARTIAL"),
                   ("pill:" + pf.RED, "open / blocked"), ("solid", "rests on")], size=9.5)

    # ---- the ladder: C2 steps at the bottom, rows 1-4 above (y grows upward)
    x0, w = 0.9, 14.0
    pf.text(ax, x0 + w / 2, 13.95, "Verification ladder of core (C3)", size=12, bold=True)
    steps = ["metric at particles", "pushers", "deposit", "Z4c coupling",
             "refinement", "initial data", "restart"]
    pf.panel(ax, x0 - 0.3, 0.5, w + 0.6, 2.6, radius=0.8)
    pf.text(ax, x0 + w / 2, 2.65, "C2 steps, each with its own test", size=9.5, italic=True)
    bw = (w - 0.2 * (len(steps) - 1)) / len(steps)
    for i, s in enumerate(steps):
        pf.sub_box(ax, x0 + i * (bw + 0.2), 0.75, bw, 1.55, s.replace(" ", "\n", 1), size=7.5,
                   rot=0, fill=pf.WHITE)
    pf.arrow(ax, (x0 + w / 2, 3.1), (x0 + w / 2, 3.7), lw=1.3)
    pf.block(ax, x0, 3.7, w, 1.1, "NRPIC module in AthenaK, release core-v0.3",
             fill=pf.GREEN_LIGHT, tcolor=pf.INK, size=10)
    y = 5.4
    h, gap = 1.25, 0.65
    boxes = {}
    for key in ("1", "2", "3", "4"):
        r = rows[key]
        if key == "3":
            hw = (w - 0.3) / 2
            pf.pill(ax, x0, y, hw, h, r["label_a"], fill=COL[r["status_a"]], size=9.5)
            pf.pill(ax, x0 + hw + 0.3, y, hw, h, r["label_b"], fill=COL[r["status_b"]], size=9.5)
        else:
            pf.pill(ax, x0, y, w, h, r["label"], fill=COL[r["status"]], size=10)
        boxes[key] = (x0, y, w, h)
        pf.arrow(ax, (x0 + w / 2, y - gap), (x0 + w / 2, y), lw=1.2)
        y += h + gap

    # ---- evidence callouts, one per row, staggered, right of the ladder
    cx, cw, ch = 15.9, 21.4, 2.75
    for i, key in enumerate(("4", "3", "2", "1")):
        r = rows[key]
        bx, by, bw_, bh = boxes[key]
        yy = 11.55 - i * 3.3
        bar = pf.RED if i % 2 == 0 else pf.OLIVE
        pf.callout(ax, cx + (0.6 if i % 2 else 0.0), yy, cw - 0.6, ch,
                   f"Row {key}: {r['title']}  [{r['verdict']}]", r["evidence"],
                   bar=bar, size=9.6, title_size=10.2, band=0.68)
        pf.line(ax, (bx + bw_, by + bh / 2), (cx - 0.15 + (0.6 if i % 2 else 0.0), yy + ch / 2),
                color=pf.GREY_LINE, lw=0.8, dashed=True)
    pf.text(ax, cx + cw / 2, 0.75, st.get("footer", ""), size=8, italic=True)
    pf.save(fig, os.path.abspath(a.out))
    print("font:", pf.FONT, "->", os.path.abspath(a.out) + ".png")


if __name__ == "__main__":
    main()
