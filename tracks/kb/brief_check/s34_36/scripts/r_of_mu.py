"""Check the printed (mu, r) pairs of arXiv:2512.13673 against its own Eq. (r) (work package s34_36).

The paper's T-model relation (main.tex:135) is r = 16 pi mu^2 / (m_P^2 N*^2), with N* = 60 the
number the paper uses (main.tex:138) and m_P the non-reduced Planck mass (main.tex:116). For each
pair printed in the paper this script
  1. checks that the quoted strings for mu and r occur on the stated line of the TeX source
     (read as text; nothing in the store is executed or imported);
  2. computes r from mu with Eq. (r) and the relative difference to the printed r;
  3. flags a pair whose printed r differs by more than TOL (two-digit rounding is below 1.6 %).
The pairs of main.tex:276 are taken as printed ("respectively"), and once more swapped.
Writes r_of_mu.json and fig_r_of_mu.{pdf,png} into $NRPIC_RUN_DIR (or the first argument).
Exit status 1 if a quoted string is not on its line (a locator error), not on a mismatch,
which is the finding the script is meant to report.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TEX = "/data/haiyangw/nrpic/kb-data/raw/arxiv/2512.13673/v1/src/main.tex"
NSTAR = 60.0
TOL = 0.03

# (id, line, mu in m_P, printed r, mu string on the line, r string on the line, what)
SQ = math.sqrt(3.0 / (16.0 * math.pi))
PAIRS = [
    ("abs", 80, 0.02, 1e-6, r"0.02\mpl", r"r_{\text{crit}} \approx 10^{-6}", "abstract"),
    ("L114", 114, 0.020, 5.6e-6, r"0.020\,\mpl", r"5.6\times 10^{-6}", "introduction, out-of-phase"),
    ("L238a", 238, 0.02, 5.6e-6, r"\mu = 0.02\mpl", r"r = 5.6\times10^{-6}", "caption, out-of-phase"),
    ("L238b", 238, 0.025, 8.7e-6, r"\mu = 0.025\mpl", r"r = 8.7\times10^{-6}", "caption, in-phase"),
    ("L273a", 273, 0.01, 1.4e-6, r"0.01\mpl", r"1.4\times10^{-6}", "scan range, lower end"),
    ("L273b", 273, SQ, 8.3e-4, r"\sqrt{3/16\pi}\mpl", r"8.3\times10^{-4}", "scan range, upper end"),
    ("L276a", 276, 0.025, 5.6e-6, r"0.025\,\mpl", r"5.6\times10^{-6}", "text, in-phase as printed"),
    ("L276b", 276, 0.020, 8.7e-6, r"0.020\,\mpl", r"8.7\times10^{-6}", "text, out-of-phase as printed"),
    ("L276a_sw", 276, 0.025, 8.7e-6, r"0.025\,\mpl", r"8.7\times10^{-6}", "text, in-phase swapped"),
    ("L276b_sw", 276, 0.020, 5.6e-6, r"0.020\,\mpl", r"5.6\times10^{-6}", "text, out-of-phase swapped"),
    ("L301a", 301, 0.01, 1.4e-6, r"0.01 \mpl", r"1.4\times 10^{-6}", "gradient-only scan, lower end"),
    ("L301b", 301, 0.04, 2.2e-5, r"0.04 \mpl", r"2.2\times10^{-5}", "gradient-only scan, upper end"),
    ("L305", 305, 0.017, 4.0e-6, r"0.017\mpl", r"4.0\times 10^{-6}", "gradient only"),
    ("L309", 309, 0.02, 5.6e-6, r"0.02\mpl", r"5.6\times 10^{-6}", "summary"),
]


def r_of_mu(mu):
    return 16.0 * math.pi * mu ** 2 / NSTAR ** 2


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    with open(TEX, "rb") as fh:
        lines = fh.read().decode("utf-8", "replace").splitlines()
    rows, locator_problems = [], []
    for pid, ln, mu, rp, smu, sr, what in PAIRS:
        text = lines[ln - 1]
        for s in (smu, sr):
            if s not in text:
                locator_problems.append("%s: %r not on main.tex:%d" % (pid, s, ln))
        rc = r_of_mu(mu)
        rel = rp / rc - 1.0
        rows.append({"id": pid, "line": ln, "mu": mu, "r_printed": rp, "r_eq": rc,
                     "rel_diff": rel, "ok": abs(rel) <= TOL, "what": what})
    log_56 = math.log10(5.6e-6)
    result = {"tex": TEX, "N_star": NSTAR, "tol": TOL, "rows": rows,
              "locator_problems": locator_problems,
              "log10_5.6e-6": log_56,
              "mismatches": [r["id"] for r in rows if not r["ok"]]}
    with open(os.path.join(out, "r_of_mu.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    for r in rows:
        print("%-9s main.tex:%-3d mu=%.4f r_printed=%.2e r_eq=%.3e rel=%+.3f %s  (%s)"
              % (r["id"], r["line"], r["mu"], r["r_printed"], r["r_eq"], r["rel_diff"],
                 "ok" if r["ok"] else "MISMATCH", r["what"]))
    print("log10(5.6e-6) = %.3f" % log_56)
    print("mismatches:", result["mismatches"])
    print("locator problems:", locator_problems)

    fs.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4),
                                   gridspec_kw={"width_ratios": [1.25, 1.0]})
    mus = [0.008 * (SQ / 0.008) ** (i / 200.0) for i in range(201)]
    ax1.loglog(mus, [r_of_mu(m) for m in mus], color="k", lw=1.0,
               label=r"Eq. (r), $N_*=60$")
    ax1.axhline(1e-6, color=fs.PAL["red"], ls="--", lw=0.8, label=r"abstract: $10^{-6}$")
    shown = set()
    for r in rows:
        if r["id"].endswith("_sw"):
            continue
        c = fs.PAL["blue"] if r["ok"] else fs.PAL["red"]
        mk = "o" if r["ok"] else "x"
        lab = "printed, agrees" if r["ok"] else "printed, disagrees"
        ax1.plot(r["mu"], r["r_printed"], mk, color=c, ms=5, mfc="none" if r["ok"] else c,
                 label=None if lab in shown else lab)
        shown.add(lab)
    ax1.set_xlabel(r"$\mu/m_P$")
    ax1.set_ylabel(r"$r$")
    ax1.legend(loc="upper left", fontsize=7)
    ids = [r["id"] for r in rows]
    y = list(range(len(rows)))[::-1]
    cols = [fs.PAL["blue"] if r["ok"] else fs.PAL["red"] for r in rows]
    ax2.barh(y, [100.0 * r["rel_diff"] for r in rows], color=cols, height=0.7)
    ax2.axvspan(-100 * TOL, 100 * TOL, color="0.85", zorder=0)
    ax2.set_yticks(y)
    ax2.set_yticklabels(ids, fontsize=7)
    ax2.tick_params(axis="y", which="minor", left=False, right=False)
    ax2.set_xlabel(r"printed $r$ / Eq. (r) $-1$ [%]")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_r_of_mu"))
    plt.close(fig)
    if locator_problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
