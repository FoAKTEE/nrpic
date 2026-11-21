"""Figure of the watch --cycle scenario of the nrpic-usage self-test (coord/digests/harness-wave-3.md).

    python3 -I harness/tests/test_nrpic_usage.py --trace TRACE.json
    harness/bin/nrpic-env exec -- python harness/tests/usage_selftest_fig.py TRACE.json OUTSTEM

Simulated utilisation of the two windows against time (each probe a point of the line), the threshold
(95), --near (88) and --launch-max (90), and the intervals during which locks/PAUSE existed (grey), from
the PAUSE and RESUME lines the tool printed. Nothing here calls the service.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "style"))
from czstyle import *  # noqa: E402,F401,F403


def main():
    tr = json.load(open(sys.argv[1]))
    stem = sys.argv[2]
    t0 = tr["t0"]
    h = [(p["t"] - t0) / 3600.0 for p in tr["trace"]]
    use_style()
    fig, ax = plt.subplots(figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.97)
    on = None
    spans = []
    for t, s in tr["events"]:
        w = s.split()
        if not w:
            continue
        if w[0] == "PAUSE":
            on = (t - t0) / 3600.0
        elif w[0] == "RESUME" and on is not None:
            spans.append((on, (t - t0) / 3600.0))
            on = None
    for k, (a, b) in enumerate(spans):
        ax.axvspan(a, b, color="0.6", alpha=0.25, lw=0, label="locks/PAUSE present" if k == 0 else None)
    # no probe while the flag is up: break the lines there instead of joining across the pause
    hh, seven, five = [], [], []
    for k, p in enumerate(tr["trace"]):
        if k and h[k] - h[k - 1] > 0.25:
            hh.append(float("nan")), seven.append(float("nan")), five.append(float("nan"))
        hh.append(h[k]), seven.append(p["seven"]), five.append(p["five"])
    ax.plot(hh, seven, color=PAL["blue"], marker=".", ms=2.5, lw=1.0, label="weekly window")
    ax.plot(hh, five, color=PAL["red"], marker=".", ms=2.5, lw=1.0, label="five-hour window")
    ax.axhline(tr["threshold"], **dict(GUIDE, lw=1.0), label=f"threshold {tr['threshold']}")
    ax.axhline(tr["launch_max"], color="k", lw=1.0, ls=":", label=f"--launch-max {tr['launch_max']}")
    ax.set(xlabel="simulated time (hours)", ylabel="utilisation (per cent)", xlim=(0, 60), ylim=(0, 105))
    ax.legend(ncol=1, loc="center left", fontsize=8)
    save(fig, stem)


if __name__ == "__main__":
    main()
