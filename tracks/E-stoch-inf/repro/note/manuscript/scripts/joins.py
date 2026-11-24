"""Junction check of the continued runs with the figure scripts' own reader (journal entry 10, J).

For each label of runs.CONTINUED:
(1) figlib.read_con_joined over the raw pieces (original, then each continuation in order) against
    the joined record of repro/continue (runs.JOINED): number of cycles and max |difference| over
    every column and cycle;
(2) each continuation's own lines against the joined record at the same cycles (a continuation that
    a later one superseded must agree where they overlap);
(3) per continuation with c_rst > 0 (first cycle of its file minus one), the step from c_rst to
    c_rst + 1 of N (column 2), <|H|/[H]> (3) and <|M|/[M]> (6), over the mean of the two
    neighbouring steps (c_rst - 1 -> c_rst, c_rst + 1 -> c_rst + 2). Prediction: at most 3.
Writes joins.json and fig_joins.{png,pdf}.

Usage: joins.py OUT
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402
import runs as rr  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

COLS = {"N": 2, "H": 3, "M": 6}
BAR = 3.0


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    res = {}
    labels = list(rr.CONTINUED)
    fig, axes = plt.subplots(1, len(labels), figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.2, top=0.86, wspace=0.45)
    colors = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"]]
    for ax, lab in zip(axes, labels):
        raw = rr.raw_con_paths(lab)
        mine = fl.read_con_joined(raw)
        joined = fl.read_con_joined(rr.con_paths(lab))
        r = dict(raw=raw, joined=rr.con_paths(lab), n_mine=int(mine.shape[0]),
                 n_joined=int(joined.shape[0]),
                 cycles_mine=[int(mine[0, 1]), int(mine[-1, 1])],
                 cycles_joined=[int(joined[0, 1]), int(joined[-1, 1])])
        same_shape = mine.shape == joined.shape
        r["reader_equal"] = bool(same_shape and np.array_equal(mine, joined))
        r["reader_max_abs_diff"] = (float(np.max(np.abs(mine - joined))) if same_shape else None)
        cyc = joined[:, 1].astype(np.int64)
        pos = {c: i for i, c in enumerate(cyc)}
        r["continuations"] = []
        for k, p in enumerate(raw[1:], start=1):
            d = fl.read_con(p)
            c0 = int(d[0, 1])
            c_rst = c0 - 1
            idx = np.array([pos[int(c)] for c in d[:, 1]])
            diff = np.abs(d - joined[idx])
            scale = np.maximum(np.abs(joined[idx]), 1e-300)
            item = dict(file=p, first_cycle=c0, last_cycle=int(d[-1, 1]), c_rst=c_rst,
                        overlap_max_rel=float(np.max(diff / scale)))
            if c_rst > 0:
                j = pos[c_rst]
                for name, col in COLS.items():
                    s = np.diff(joined[j - 1:j + 3, col])   # steps c-1->c, c->c+1, c+1->c+2
                    item[f"step_ratio_{name}"] = float(abs(s[1]) / (0.5 * (abs(s[0]) + abs(s[2]))))
                item["pass"] = bool(all(item[f"step_ratio_{n}"] <= BAR for n in COLS))
            else:
                item["pass"] = None          # the run's own first step; judged by overlap only
            r["continuations"].append(item)
            # picture: <|M|/[M]> around the junction, original and the continuation's lines
            lo, hi = max(c_rst - 25, 0), c_rst + 25
            sel = (cyc >= lo) & (cyc <= hi)
            sd = (d[:, 1] >= lo) & (d[:, 1] <= hi)
            if k == 1:
                o = fl.read_con(raw[0])
                so = (o[:, 1] >= lo) & (o[:, 1] <= c_rst)
                ax.plot(o[so, 1], o[so, 6], "o", ms=2.5, color=colors[0], label="original")
            ax.plot(d[sd, 1], d[sd, 6], "x", ms=3, color=colors[k % 4], label=f"cont. {k}")
            ax.plot(cyc[sel], joined[sel, 6], "-", lw=0.6, color="k")
            ax.axvline(c_rst + 0.5, **fs.MASK_LINE)
        ok = [c["pass"] for c in r["continuations"] if c["pass"] is not None]
        r["junctions_pass"] = bool(all(ok)) if ok else None
        r["overlap_identical"] = bool(all(c["overlap_max_rel"] == 0.0
                                          for c in r["continuations"]))
        res[lab] = r
        ax.set_title(lab, fontsize=8)
        ax.set_xlabel("cycle", fontsize=8)
        ax.tick_params(labelsize=6)
        ax.yaxis.get_offset_text().set_fontsize(6)
    axes[0].set_ylabel(r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$", fontsize=8)
    axes[0].legend(fontsize=5, loc="best")
    fs.save(fig, os.path.join(out, "fig_joins"))
    plt.close(fig)
    # scope P1, record part (journal entry 14): the joined RSF256 record against P256v6's own record
    # (same deck and steps, dumps differ only in output), in their common columns, every cycle
    a = fl.read_con_joined(rr.con_paths("RSF256"))
    b = fl.read_con_joined([rr.con_path("P256v6")])
    nc = min(a.shape[1], b.shape[1])
    common, ia, ib = np.intersect1d(a[:, 1].astype(np.int64), b[:, 1].astype(np.int64),
                                    return_indices=True)
    eq = np.all(a[ia, :nc] == b[ib, :nc], axis=1)
    res["P1_records_RSF256_P256v6"] = dict(
        n_rsf256=int(a.shape[0]), n_p256v6=int(b.shape[0]), n_common=int(common.size),
        common_columns=int(nc), lines_identical=int(eq.sum()),
        max_rel_diff=float(np.max(np.abs(a[ia, :nc] - b[ib, :nc])
                                  / np.maximum(np.abs(b[ib, :nc]), 1e-300))),
        first_differing_cycle=(int(common[~eq][0]) if (~eq).any() else None))
    print("P1 records", res["P1_records_RSF256_P256v6"])
    with open(os.path.join(out, "joins.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    for lab, r in res.items():
        if lab not in rr.CONTINUED:
            continue
        print(lab, "reader_equal", r["reader_equal"], "junctions_pass", r["junctions_pass"],
              "overlap_identical", r["overlap_identical"],
              [(c["c_rst"], {k: round(v, 3) for k, v in c.items() if k.startswith("step_ratio")})
               for c in r["continuations"]])


if __name__ == "__main__":
    main()
