"""Figure of the dry run of the pre-commit hook over the history (coord/digests/hook-dryrun.md).

    harness/bin/nrpic-env exec -- python harness/tests/precommit_dryrun_fig.py OUTSTEM \
        BEFORE_AT.json BEFORE_TIP.json AFTER_AT.json AFTER_TIP.json AFTER_TIP_ADD.json

The JSON files are written by precommit_dryrun.py --json. Left: commits replayed per owner and the
commits the hook before the corrections would have refused (where it runs, and clean merges that it
would have refused had they conflicted). Right: refused commits by class for the five runs.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "style"))
from czstyle import *  # noqa: E402,F401,F403

OWNERS = ["main", "core", "kb", "A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills"]
CLASSES = [("fixture", "harness fixtures that look like secrets", PAL["blue"]),
           ("ownership-then", "core docs/ before decision 0011", PAL["yellow"]),
           ("ownership-now", "core python/tests/ (OWNERSHIP)", PAL["green"]),
           ("merge", "content a clean merge brings", PAL["red"])]


def owner(branch):
    if branch.startswith("track/"):
        return branch[6:].split("--")[0]
    return branch.split("/")[0] if "/" in branch else branch


def klass(r):
    if r["merge"] == "clean":
        return "merge"
    p = r["problems"][0]
    if p["check"] == "secret":
        return "fixture"
    if p["path"].startswith("docs/"):
        return "ownership-then"
    if p["path"].startswith("python/tests/"):
        return "ownership-now"
    return "other"


def main():
    stem, files = sys.argv[1], sys.argv[2:]
    runs = [json.load(open(f)) for f in files]
    labels = ["before,\nthen", "before,\ntoday", "after,\nthen", "after,\ntoday", "after, today,\n+python/tests"]
    use_style()
    fig = plt.figure(figsize=(8.0, 3.4))
    ax1 = fig.add_axes([0.125, 0.17, 0.34, 0.78])
    ax2 = fig.add_axes([0.56, 0.17, 0.42, 0.78])

    b = runs[0]
    n = {o: 0 for o in OWNERS}
    for br, k in b["by_branch"].items():
        n[owner(br)] = n.get(owner(br), 0) + k
    y = np.arange(len(OWNERS))[::-1]
    ax1.barh(y + 0.2, [n[o] for o in OWNERS], height=0.38, color="0.7")
    left = np.zeros(len(OWNERS))
    for key, lab, col in CLASSES:
        h = np.array([sum(1 for r in b["refusals"] if klass(r) == key and owner(r["branch"]) == o) for o in OWNERS], float)
        ax1.barh(y - 0.2, h, left=left, height=0.38, color=col)
        left += h
    for i, o in enumerate(OWNERS):
        ax1.text(n[o] * 1.15, y[i] + 0.2, f"{n[o]}", va="center", fontsize=8)
        if left[i]:
            ax1.text(left[i] * 1.15, y[i] - 0.2, f"{int(left[i])}", va="center", fontsize=8)
    ax1.set_yticks(y)
    ax1.set_yticklabels(OWNERS)
    ax1.set_xscale("log")
    ax1.set_xlim(0.8, 5000)
    ax1.set_ylim(-0.7, len(OWNERS) - 0.3)
    ax1.set_xlabel("commits since 52c44eb; refused (before)")
    ax1.tick_params(axis="y", which="minor", left=False, right=False)

    x = np.arange(len(runs))
    bottom = np.zeros(len(runs))
    for key, lab, col in CLASSES:
        h = np.array([sum(1 for r in run["refusals"] if klass(r) == key) for run in runs], float)
        ax2.bar(x, h, bottom=bottom, color=col, width=0.6, label=lab)
        bottom += h
    other = [sum(1 for r in run["refusals"] if klass(r) == "other") for run in runs]
    for i, t in enumerate(bottom):
        ax2.text(x[i], t + 0.6, f"{int(t)}" + (f" (+{other[i]} other)" if other[i] else ""), ha="center", fontsize=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8)
    ax2.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax2.set_ylabel("refused commits")
    ax2.set_ylim(0, max(bottom) * 1.35 + 1)
    ax2.legend(loc="upper right", fontsize=8)
    save(fig, stem)


if __name__ == "__main__":
    main()
