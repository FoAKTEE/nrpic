#!/usr/bin/env python3
"""Figures of package code_kb, from the outputs of registered runs only:
  fig_link_verdicts   verdicts of the 25 paper-code links by area (LINKS.tsv of the
                      evidence run)
  fig_task_order      the task lists of one cycle in the order Driver::Execute runs them,
                      with the particle tasks and the tasks that write or read tmunu, for
                      local/nrpic and upstream AthenaK (modules.json of the modules run)
  fig_watch_summary   the upstream watch: branch counts and the changed files under src/z4c
                      and src/particles per branch (watch_diff.json of run W2)
It also records the parameter-index rows of <z4c> nco (read-only query of the database).

    python figs.py --links LINKS.tsv --modules-local M1.json --modules-upstream M2.json \
        --watch watch_diff.json --db kb.sqlite --out DIR
"""
import argparse
import csv
import json
import os
import sqlite3
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

COL = {"verified": fs.PAL["green"], "claimed": fs.PAL["yellow"], "refuted": fs.PAL["red"]}


def fig_links(path, out):
    rows = list(csv.DictReader(open(path, newline=""), delimiter="\t"))
    areas = list(OrderedDict.fromkeys(r["area"] for r in rows))
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.4))
    for i, a in enumerate(areas):
        left = 0
        for verdict in ("verified", "claimed", "refuted"):
            ks = [r["link_key"] for r in rows if r["area"] == a and r["verdict"] == verdict]
            if not ks:
                continue
            ax.barh(i, len(ks), left=left, color=COL[verdict], edgecolor="k", lw=0.6, height=0.62)
            for j, k in enumerate(ks):
                ax.text(left + j + 0.5, i, k, ha="center", va="center", fontsize=7)
            left += len(ks)
    ax.set_yticks(range(len(areas)))
    ax.set_yticklabels(areas)
    ax.invert_yaxis()
    ax.set_xlabel("links")
    c = Counter(r["verdict"] for r in rows)
    ax.legend(handles=[Patch(fc=COL[v], ec="k", lw=0.6, label=f"{v} ({c[v]})")
                       for v in ("verified", "claimed", "refuted")], loc="lower right", frameon=False)
    ax.set_xlim(0, max(Counter(r["area"] for r in rows).values()) + 0.5)
    ax.set_title("25 curated links of arXiv:2611.12831 to local/nrpic at 47ab19ab", fontsize=9)
    fig.tight_layout()
    return fs.save(fig, os.path.join(out, "fig_link_verdicts"))


def short(f):
    parts = f.split("::")
    return "::".join(parts[-2:]) if len(parts) > 1 else f


def cycle(desc):
    """[(list, when, [(label, role)])] for the lists of one cycle (parabolic lists left out)."""
    order = []
    for c in desc["driver"]["calls"]:
        if "parabolic" in c["list"] or c["list"] in [o[0] for o in order]:
            continue
        order.append((c["list"], c["when"]))
    out = []
    for lst, when in order:
        items = []
        for t in desc["tasks"]:
            if t["task_list"] != lst:
                continue
            fn = short(t["task_function"]).split("<")[0]
            if t["module"] == "particles":
                if desc["repo_id"] == "local/nrpic" and t.get("after_returning_blocks"):
                    continue          # the upstream particle path, skipped for nrpic particles
                role = "write" if t.get("tmunu") and "Deposit" in fn else "particles"
            elif fn.endswith("SetTmunu"):
                role = "write"
            elif t["module"] == "z4c" and t.get("tmunu"):
                role = "read"
            else:
                continue
            lab = fn + (" (if coll.on)" if any("coll.on" in x for x in t.get("conditions") or []) else "")
            if (lab, role) not in items:
                items.append((lab, role))
        out.append((lst, when, items))
    return out


def fig_tasks(paths, out):
    colors = {"particles": fs.PAL["blue"], "write": fs.PAL["red"], "read": fs.PAL["green"]}
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 5.6))
    for ax, p in zip(axes, paths):
        desc = json.load(open(p))
        cyc = cycle(desc)
        y = 0.0
        ax.set_xlim(0, 1)
        stage_top = stage_bot = None
        for lst, when, items in cyc:
            h = 0.075 + 0.052 * max(1, len(items))
            box = FancyBboxPatch((0.08, y - h), 0.88, h - 0.015, boxstyle="round,pad=0.005",
                                 fc="#f4f4f4", ec="k", lw=0.8)
            ax.add_patch(box)
            ax.text(0.11, y - 0.035, f"{lst}", fontsize=8, fontweight="bold", va="center")
            ax.text(0.93, y - 0.035, when, fontsize=6.5, va="center", ha="right", style="italic")
            for k, (lab, role) in enumerate(items):
                ax.text(0.14, y - 0.085 - 0.052 * k, lab, fontsize=7, va="center", color=colors[role])
            if "stage" in when and "explicit" in when:
                stage_top = y if stage_top is None else stage_top
                stage_bot = y - h
            y -= h + 0.02
        if stage_top is not None:
            ax.annotate("", xy=(0.045, stage_top), xytext=(0.045, stage_bot),
                        arrowprops=dict(arrowstyle="<-", lw=1.0))
            ax.text(0.025, 0.5 * (stage_top + stage_bot), "loop over the explicit stages", rotation=90,
                    fontsize=6.5, va="center", ha="center")
        ax.set_ylim(y - 0.02, 0.02)
        ax.axis("off")
        ax.set_title(f"{desc['repo_id']} at {desc['commit_sha'][:8]}", fontsize=9)
    fig.legend(handles=[Patch(fc=colors[r], label=lab) for r, lab in
                        (("particles", "particle task"), ("write", "task that writes tmunu"),
                         ("read", "Z4c task that reads tmunu"))], loc="lower center", ncol=3, frameon=False, fontsize=7)
    fig.suptitle("One cycle of Driver::Execute: task lists in order (extracted by kb code modules)", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    return fs.save(fig, os.path.join(out, "fig_task_order"))


def fig_watch(path, out):
    d = json.load(open(path))
    n = d["n_branches"]
    counts = OrderedDict([("unchanged", n - len(d["moved"]) - len(d["added"])), ("moved", len(d["moved"])),
                          ("new", len(d["added"])), ("removed", len(d["removed"]))])
    per = OrderedDict()
    for r in d["rows"]:
        key = (r["branch"], r["kind"])
        mod = "src/particles" if r["path"].startswith("src/particles/") else "src/z4c"
        e = per.setdefault(key, {"src/z4c": 0, "src/particles": 0, "lines": 0})
        e[mod] += 1
        e["lines"] += int(r.get("added") or 0) + int(r.get("removed") or 0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0), gridspec_kw={"width_ratios": [1, 1.6]})
    a1.bar(range(len(counts)), list(counts.values()), color=fs.SERIES[:4], edgecolor="k", lw=0.6)
    for i, v in enumerate(counts.values()):
        a1.text(i, v, str(v), ha="center", va="bottom", fontsize=8)
    a1.set_xticks(range(len(counts)))
    a1.set_xticklabels(list(counts), fontsize=8)
    a1.set_ylabel("branches")
    a1.set_yscale("log")
    a1.set_ylim(0.5, 400)
    a1.set_title(f"{d['old']} -> {d['new']}", fontsize=8)
    names = [f"{b}\n({k.split(' ')[0]})" for b, k in per]
    z = [v["src/z4c"] for v in per.values()]
    pt = [v["src/particles"] for v in per.values()]
    x = range(len(per))
    a2.bar([i - 0.2 for i in x], z, width=0.4, color=fs.PAL["blue"], edgecolor="k", lw=0.6, label="src/z4c files")
    a2.bar([i + 0.2 for i in x], pt, width=0.4, color=fs.PAL["red"], edgecolor="k", lw=0.6,
           label="src/particles files")
    for i, v in enumerate(per.values()):
        a2.text(i - 0.2, max(z[i], 0.6), f"{v['lines']} lines", ha="center", va="bottom", fontsize=6.5)
    a2.set_xticks(list(x))
    a2.set_xticklabels(names, fontsize=7)
    a2.set_yscale("log")
    a2.set_ylim(0.5, 300)
    a2.set_ylabel("changed files")
    a2.legend(frameon=False, fontsize=7, loc="upper left")
    if not any(pt):
        a2.text(0.98, 0.04, "src/particles: 0 changed files on every branch", transform=a2.transAxes,
                ha="right", va="bottom", fontsize=7, color=fs.PAL["red"])
    a2.set_title("changed files (moved: against the last watch; new: against main)", fontsize=8)
    fig.tight_layout()
    return fs.save(fig, os.path.join(out, "fig_watch_summary"))


def nco_rows(db, out):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute("SELECT p.repo_id, p.block, p.name, f.path, p.line FROM params p JOIN code_files f "
                       "USING(file_id) WHERE p.name = 'nco' OR (p.block = 'z4c' AND p.name LIKE 'nco%')").fetchall()
    rep = con.execute("SELECT commit_sha FROM repos WHERE repo_id = 'local/nrpic'").fetchone()
    con.close()
    with open(os.path.join(out, "nco_params.txt"), "w") as f:
        f.write(f"params rows with name nco (any repository; local/nrpic indexed at {rep[0]}): {len(rows)}\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    for k in ("links", "modules-local", "modules-upstream", "watch", "db", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    files = fig_links(a.links, a.out) + fig_tasks([a.modules_local, a.modules_upstream], a.out) + \
        fig_watch(a.watch, a.out)
    n = nco_rows(a.db, a.out)
    print("\n".join(files))
    print(f"nco parameter-index rows: {n}")


if __name__ == "__main__":
    main()
