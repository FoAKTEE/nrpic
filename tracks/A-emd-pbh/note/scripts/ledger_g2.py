"""Ledger of the gate-G2 numbers of the note (Appendix, Table ledger_g2).

Every value is read from the output of a registered run, checked against the sha256 the run
recorded (common.run_file); the table names the run of each row. Writes tables/ledger_g2.tex.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

common.RUNS.update({
    "conv": "A-20261121-120257-a2eb839",        # conv_ball analysis (time errors)
    "szk64": "A-20261126-024724-425ed7f",       # Szekeres reader, N64 and N128
    "szk256": "A-20261126-023245-1dd80ad",      # Szekeres reader, N128 and N256
    "edge": "A-20261126-212340-4ea9fb2",        # C3: smoothed member, mesh and particle-number legs
    "s1l": "A-20261126-022438-a08cc5f",         # S1L, shift-invariant crossing measure
    "s1lh": "A-20261126-213147-f274b2e",        # S1L-h, the same at half amplitude
    "zel": "A-20261126-022631-dafbb4f",         # Zel'dovich reference of S1L
})


TO = " $\\to$ "


def f(v, nd=3):
    return f"{v:.{nd}g}"


def main():
    out = common.out_dir("tables")
    rows = []
    conv = common.load_json("conv", "convergence.json")["legs"]["mesh"]
    for name, h, dd, dt in zip(conv["members"], conv["x"], conv["ddet"]["values"], conv["dtrap"]["values"]):
        rows.append((f"ball, mesh {name} ($h = {f(h)}\\,M$): $\\Delta t_{{\\rm det}}$, $\\Delta t_{{\\rm trap}}$ ($M$)",
                     f"{f(dd)}, {f(dt)}", common.RUNS["conv"]))
    rows.append(("ball, mesh orders of $\\Delta t_{\\rm det}$ (fiducial interpolation)",
                 ", ".join(f(o, 2) for o in conv["ddet"]["orders"]), common.RUNS["conv"]))
    # gate review section 6 item 4: orders as ranges under the three interpolations at the core edge
    # (VERIFIER-C18 5e; lead's answer run A-20261125-151126-7f79a83, CHECKLIST C2)
    rows.append(("ball, mesh orders of $\\Delta t_{\\rm det}$, range over three interpolations",
                 "1.2--1.5, 1.75--2.1", "A-20261125-151126-7f79a83"))
    rows.append(("ball, mesh orders of $\\Delta t_{\\rm trap}$", ", ".join(f(o, 2) for o in conv["dtrap"]["orders"]),
                 common.RUNS["conv"]))
    for key, fn in (("szk64", "code_runs_n64n128.json"), ("szk256", "code_runs_n128n256.json")):
        d = common.load_json(key, fn)
        for nm, m in d["members"].items():
            if key == "szk256" and nm == "N128":
                continue
            for r in m["dumps"]:
                if r["tau"] in (10.0, 20.0, 30.0):
                    rows.append((f"Szekeres {nm}, $\\tau = {r['tau']:.0f}$: shell rms $|K-K_{{\\rm ex}}|/H$, same-cell signal max",
                                 f"{f(r['shell']['K_err_over_H_rms'])}, {f(r['shell']['signal_K_over_H_max'])}",
                                 common.RUNS[key]))
        for o in d["orders"]:
            if o["tau1"] > 0:
                pair = o["pair"].replace("->", TO)
                rows.append((f"Szekeres {pair}, $\\tau = {o['tau1']:.0f}$: order of shell $K$, $H$",
                             f"{f(o['shell']['K_err_over_H_rms'], 3)}, {f(o['shell']['H_over_16pirho_rms'], 3)}",
                             common.RUNS[key]))
    e = common.load_json("edge", "edge.json")["members"]
    for nm in ("S2c-A", "S2c-B", "S2c-A8"):
        rr = dict((round(t, 3), v) for t, v in e[nm]["ratio"])
        vals = [rr.get(t) for t in (0.0, 1.0, 2.0)]
        rows.append((f"smoothed member {nm}: line ratio at $t = 0, 1, 2\\,M$",
                     ", ".join("--" if v is None else f(v) for v in vals), common.RUNS["edge"]))
    zel = common.load_json("zel", "a2_compare.json")
    rows.append(("S1L: Zel'dovich first-axis time ($t_H$)", f(zel["zeldovich_t_sc_over_tH"]), common.RUNS["zel"]))
    for key, lab in (("s1l", "S1L"), ("s1lh", "S1L-h")):
        x = common.load_json(key, "a2x.json")
        lp, fn_ = x["first"]["fwd"]["last_positive"], x["first"]["fwd"]["first_nonpositive"]
        rows.append((f"{lab}: first crossing bracket ($t_H$; reference {f(x['reference_t_over_tH'])})",
                     f"({f(lp['coord'])}, {f(fn_['coord'])}]", common.RUNS[key]))
    lines = [r"\begin{table*}", r"\caption{\label{tab:ledger_g2}Numbers behind the verification section, each with the registered run that produced it.}",
             r"\begin{ruledtabular}", r"\begin{tabular}{lll}", r"Quantity & Value & Run \\ \hline"]
    for q, v, run in rows:
        lines.append(f"{q} & {v} & \\texttt{{{run}}} \\\\")
    lines += [r"\end{tabular}", r"\end{ruledtabular}", r"\end{table*}"]
    with open(os.path.join(out, "ledger_g2.tex"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"ledger_g2: {len(rows)} rows")
    common.report_checks("ledger_g2")


if __name__ == "__main__":
    main()
