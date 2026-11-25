"""Claim-by-claim tables (markdown) from the verifier's registered outputs.
Usage: python -I vtable.py --conv DIR --thresh DIR --out DIR"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vconv import CLAIM as CC
from vthresh import CLAIM as TC


def digits(claim, mine):
    """Agreement in decimal places of the claim as printed: 'to the printed digits' when the
    difference is at most half a unit of the claim's last digit, else the difference."""
    if claim is None or mine is None:
        return "-"
    s = "%r" % claim
    if "e" in s:
        mant, ex = s.split("e")
        dec = (len(mant.split(".")[1]) if "." in mant else 0) - int(ex)
    else:
        dec = len(s.split(".")[1]) if "." in s else 0
    half = 0.5 * 10 ** (-dec)
    d = mine - claim
    return "yes (printed digits)" if abs(d) <= half * 1.0001 else "diff %+.2g" % d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conv", required=True)
    ap.add_argument("--thresh", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cv = json.load(open(os.path.join(a.conv, "vconv.json")))
    th = json.load(open(os.path.join(a.thresh, "vthresh.json")))
    L = ["## conv_ball (claims: README table; verifier: run %s)" % os.path.basename(a.conv.rstrip("/")), "",
         "| member | t1 claim / mine | ddet claim / v2 [v1, v3] | dtrap claim / mine | mass median claim / mine [bracket] |",
         "|---|---|---|---|---|"]
    for n, c in CC.items():
        r = cv["members"][n]
        d = r["ddet"]
        L.append("| %s | %.3f / %.4f (%s) | %+.3f / %+.4f [%+.4f, %+.4f] (%s) | %+.4f / %+.4f (%s) | %+.2e / %+.2e [%+.1e, %+.1e] (%s) |" % (
            n, c[0], d["t"], digits(c[0], d["t"]), c[1], d["ddet_v2"], d["ddet_v1"], d["ddet_v3"],
            digits(c[1], d["ddet_v2"]), c[2], r["dtrap"]["dtrap_mean"], digits(c[2], r["dtrap"]["dtrap_mean"]),
            c[3], r["dm_median"], r["dm_median_bounds"][0], r["dm_median_bounds"][1], digits(c[3], r["dm_median"])))
    L += ["", "Orders (log2 of neighbour ratios, A->B, B->C):", ""]
    for q, o in cv["orders"].items():
        L.append("- %s: %.2f, %.2f" % (q, o["p_AB"], o["p_BC"]))
    L += ["", "## threshold_ball (claims: README table; verifier: run %s)" % os.path.basename(a.thresh.rstrip("/")), "",
          "| member | BH (rule) | persistent from claim / mine | tau_det claim / mine | ddet claim / v2 [v1, v3] | dmmed claim / mine [bracket] | exact tau_AH claim / mine | H/16piE r^2 (first; t=0) |",
          "|---|---|---|---|---|---|---|---|"]
    for n, c in TC.items():
        r = th["members"][n]
        if "first" not in r:
            L.append("| %s | no (no find to %.2f) | none / none | - | - | - | %.3f / %.6f | - |" % (
                n, r["last_summary_time"], c[0], r["exact_tau_ah_edge"]))
            continue
        f = r["first"]
        ln = r.get("line", {})
        pc = c[1] if c[1] is not None else "none"
        pm = r["rule"]["persistent_from"]
        L.append("| %s | %s | %s / %s | %.3f / %.4f (%s) | %+.3f / %+.4f [%+.3f, %+.3f] | %s / %s [%s] | %.3f / %.6f | %.2f; %.3f |" % (
            n, "yes" if r["rule"]["bh"] else "no (%d finds, last search %.3f, tlim %g)" % (
                r["rule"]["n_found"], r["rule"]["last_search"], r["tlim"]),
            pc, "%.5f" % pm if (pm is not None and r["rule"]["bh"]) else "none",
            c[2], f["tau_det"], digits(c[2], f["tau_det"]), c[3], f["ddet_v2"], f["ddet_v1"], f["ddet_v3"],
            "%+.1e" % c[4] if c[4] is not None else "-", "%+.1e" % r["dm_median"] if r["dm_median"] is not None else "-",
            "%+.1e, %+.1e" % tuple(r["dm_median_bounds"]) if r["dm_median_bounds"] else "-",
            c[0], r["exact_tau_ah_edge"],
            ln.get("first", {}).get("ratio_all", {}).get("r2", float("nan")),
            ln.get("t0", {}).get("ratio_all", {}).get("r2", float("nan"))))
    L += ["", "Bracket at t_end = 45: " + json.dumps(th["bracket"])]
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
