"""Numerical ledger of the working note v0 of Track E, the parameter table, and a check of
the numbers that the lead's documents print against the files of the registered runs.

Writes into <out> (default note/tables/):
  ledger.tex      the ledger appendix of the note: each number with its run id or locator
  parameters.tex  the parameter table of the two test cases
  claims.md/.json each number printed in spec/SPEC.md, spec/scope/SCOPE.md,
                  stage/G0/EVIDENCE.md and langevin/README.md that the note relies on,
                  recomputed from the run outputs; agreement means within half a unit of
                  the last printed digit. Where they disagree, the files win.
Every input is read through common.path (checksum against the run manifest).
"""
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import costmodel  # noqa: E402

SPEC_RUN = "E-stoch-inf-20261115-122806-ef0d039"
LEAD_RUN = "E-20261115-135532-3f958a1"
DN = {"quadratic": "E-stoch-inf-20261115-130139-176cdd6",
      "inflection": "E-stoch-inf-20261115-130137-176cdd6"}
VAL_RUN = "E-20261115-140502-2957846"


def at(d, key, N):
    return float(np.interp(N, d["N"], d[key]))


def power_end(d, key):
    k = d["k"]
    return k ** 3 * np.abs(d[key][:, -1]) ** 2 / (2 * np.pi ** 2)


def gather():
    """Every number of the note and of the claims check, from the run outputs."""
    v = {}
    s = C.load_json(SPEC_RUN, "summary.json")
    for case in ("quadratic", "inflection"):
        d = np.load(C.path(SPEC_RUN, f"{case}.npz"))
        q = s[case]
        n0 = float(d["Nstar"])
        v[f"{case}.Nstar"] = n0
        v[f"{case}.Nf"] = q["Nf"]
        v[f"{case}.H0"] = q["H0"]
        v[f"{case}.Hstar"] = q["Hstar"]
        v[f"{case}.dphidN0"] = q["dphidN0"]
        v[f"{case}.phi0"] = q["params"]["phi0"]
        v[f"{case}.eps1_star"] = at(d, "eps1", n0)
        v[f"{case}.eps2_star"] = at(d, "eps2", n0)
        v[f"{case}.eps1_Nf"] = q["eps1_at_Nf"]
        v[f"{case}.eps2_Nf"] = q["eps2_at_Nf"]
        v[f"{case}.L"] = q["L"]
        v[f"{case}.dk"] = q["dk"]
        pms, pdef = power_end(d, "R_ms"), power_end(d, "R_def")
        v[f"{case}.ratio_def_full"] = list(pdef / pms)
        v[f"{case}.k_over_dk"] = list(d["k"] / float(d["dk"]))
        v[f"{case}.Delta_full_Nf_last"] = float(pms[-1])
        v[f"{case}.full_over_est"] = list(np.array(q["Delta_ms_Nf"]) / np.array(q["Delta_SR_estimate_at_cross"]))
        v[f"{case}.drift_ms"] = q["drift_ms"]
        v[f"{case}.drift_def"] = q["drift_def"]
    v["quadratic.m"] = s["quadratic"]["params"]["m"]
    v["inflection.eps1_min"] = s["inflection"]["eps1_min"]
    lb = C.load_json(LEAD_RUN, "bg/lead_bg.json")
    v["lead.usr_from"] = lb["inflection"]["usr_from"]
    v["lead.usr_to"] = lb["inflection"]["usr_to"]
    v["lead.inflection_eps1_star"] = lb["inflection"]["eps1_star"]
    v["lead.sr_P_full_end"] = lb["sr_mode"]["P_full_end_over_SR"]
    v["lead.sr_slope_full"] = lb["sr_mode"]["slope_full"]
    v["lead.sr_slope_def"] = lb["sr_mode"]["slope_def"]
    v["lead.sr_minus4eps1"] = lb["sr_mode"]["minus4eps1"]
    v["lead.sr_ratio_def_full"] = lb["sr_mode"]["ratio_def_full_end"]
    v["lead.usr_ratio_def_full"] = lb["usr_mode"]["ratio_def_full_end"]
    for case, run in DN.items():
        r = C.load_json(run, f"ref_{case}.json")
        v[f"dn.{case}.var_lin"] = r["linear"]["var_cont_Ne"]
        v[f"dn.{case}.var_lattice"] = r["linear"]["var_lattice_Ne"]
        v[f"dn.{case}.lattice_over_cont"] = r["linear"]["lattice_over_cont"]
        for sg in ("0.01", "0.1", "1"):
            v[f"dn.{case}.s{sg}"] = r["ratios_Ne"][f"s{sg}"]["var_over_lin"]
            v[f"dn.{case}.s{sg}.se"] = r["ratios_Ne"][f"s{sg}"]["se"]
        v[f"dn.{case}.skew"] = r["s0.01"]["Ne"]["skew"]
        v[f"dn.{case}.Ne"] = r["params"]["Ne"] - r["params"]["Nstar"]
    for sub in ("val_frozen", "val_markov_heaviside", "val_markov_tanh"):
        tests = C.load_json(VAL_RUN, f"{sub}/validation.json")
        v[f"{sub}.failed"] = [t["id"] for t in tests if t["passed"] is False]
        for t in tests:
            if t["id"] in ("A1", "A13"):
                v[f"{sub}.{t['id']}"] = t["value"]
    for sub in ("val_std", "val_cf"):
        tests = C.load_json("E-20261115-172423-5234cce", f"{sub}/validation.json")
        v[f"release.{sub}.A1"] = next(t["value"] for t in tests if t["id"] == "A1")
        v[f"release.{sub}.failed"] = [t["id"] for t in tests if t["passed"] is False]
    rows, meta = costmodel.table()
    for r in rows:
        key = f"cost.{r['case']}.{r['N']}"
        v[key + ".steps"] = r["steps"]
        v[key + ".model"] = r["model"]
        v[key + ".lo"] = r["measured_lo"]
        v[key + ".hi"] = r["measured_hi"]
        v[key + ".s_model"] = r["sec_per_step_model"]
        v[key + ".mem"] = r["memory_GB"]
    cost = C.load_json(costmodel.CODEBASE, "cost.json")
    for r in cost["rows"]:
        if r["N"] == 256 and r["theta"] == 0.25:
            v[f"cost.{r['case']}.256.model_{r['noise_per']}"] = r["card_hours"]
    v.update({f"core.{k}": val for k, val in meta.items()})
    return v


def half_unit(txt):
    """Half a unit of the last printed digit of a number string such as 1.0805, 9.7e-13;
    an integer with trailing zeros (870, 350) counts as rounded to its last nonzero digit."""
    m = re.fullmatch(r"-?(\d+)(?:\.(\d+))?(?:e(-?\d+))?", txt)
    if not m:
        raise ValueError(txt)
    dec = len(m.group(2) or "")
    ex = int(m.group(3) or 0)
    if dec == 0 and m.group(1) != "0":
        ex += len(m.group(1)) - len(m.group(1).rstrip("0"))
    return 0.5 * 10.0 ** (ex - dec)


def claims(v):
    """(id, document, search text, printed value, computed value, what)."""
    rf = v["inflection.ratio_def_full"]
    kd = np.array(v["inflection.k_over_dk"])

    def usr_at(kk):
        return rf[int(np.argmin(np.abs(kd - kk)))]
    q = "quadratic"
    i = "inflection"
    SC, SP, EV, LR = "spec/scope/SCOPE.md", "spec/SPEC.md", "stage/G0/EVIDENCE.md", "langevin/README.md"
    return [
        ("c01", SC, "phi0 = -14.0950 Mpl", "-14.0950", v[f"{q}.phi0"], "SR phi0"),
        ("c02", SC, "m = 1.73494e-6 Mpl", "1.73494e-6", v[f"{q}.m"], "SR mass"),
        ("c03", SC, "eps1(N*) = 1.1107e-2", "1.1107e-2", v[f"{q}.eps1_star"], "SR eps1 at N*"),
        ("c04", SC, "dphi/dN(N0) = 0.102682", "0.102682", v[f"{i}.dphidN0"], "USR dphi/dN at N0"),
        ("c05", SC, "H0 = 9.5902e-6 Mpl", "9.5902e-6", v[f"{i}.H0"], "USR H0"),
        ("c06", SC, "from N* + 2.52 to N* + 6.55", "2.52", v["lead.usr_from"], "USR onset (eps2 = 3), lead's integrator"),
        ("c07", SC, "from N* + 2.52 to N* + 6.55", "6.55", v["lead.usr_to"], "USR end (eps2 = 3), lead's integrator"),
        ("c08", SC, "eps1 min 9.7e-13", "9.7e-13", v[f"{i}.eps1_min"], "USR minimum eps1"),
        ("c09", SC, "| Steps at 256^3 | 1304 | 1630 |", "1304", v[f"cost.{q}.256.steps"], "SR steps at 256^3, Courant 0.25"),
        ("c10", SC, "| Steps at 256^3 | 1304 | 1630 |", "1630", v[f"cost.{i}.256.steps"], "USR steps at 256^3, Courant 0.25"),
        ("c11", SC, "| SR 256^3, theta = 0.25, 1304 steps | 0.36-0.41", "0.36", v[f"cost.{q}.256.model_step"], "SR card-hours, model, noise once per step"),
        ("c12", SC, "| SR 256^3, theta = 0.25, 1304 steps | 0.36-0.41", "0.41", v[f"cost.{q}.256.model_stage"], "SR card-hours, model, noise per stage"),
        ("c13", SC, "| USR 256^3, theta = 0.25, 1630 steps | 0.45-0.51", "0.45", v[f"cost.{i}.256.model_step"], "USR card-hours, model, per step"),
        ("c14", SC, "| USR 256^3, theta = 0.25, 1630 steps | 0.45-0.51", "0.51", v[f"cost.{i}.256.model_stage"], "USR card-hours, model, per stage"),
        ("c15", SC, "1.0-1.1 s per step, 20 GB", "20", v[f"cost.{q}.256.mem"], "memory of a 256^3 run, GB"),
        ("c16", SC, "field, Tmunu and kicks add 15", "0.15", v["core.overhead_measured"], "overhead of field and sources over Z4c (assumed in SCOPE; measured by core)"),
        ("c17", SC, "| Each further 256^3 realisation (G3) | 0.4-0.5", "0.5", v[f"cost.{q}.256.hi"], "card-hours of one 256^3 SR realisation (upper end), measured throughput"),
        ("c18", SC, "| Each further 256^3 realisation (G3) | 0.4-0.5", "0.5", v[f"cost.{i}.256.hi"], "card-hours of one 256^3 USR realisation (upper end), measured throughput"),
        ("c19", SP, "Assuming 30 percent more", "0.30", v["core.overhead_measured"], "overhead of field and sources over Z4c (assumed in SPEC 11.2; measured by core)"),
        ("c20", SP, "| eps1, eps2 at N* | 1.1107e-2, -2.213e-2 | 1.3164e-2, -0.4307 |", "1.3164e-2", v[f"{i}.eps1_star"], "USR eps1 at N*, reference run"),
        ("c21", SP, "| eps1, eps2 at N* | 1.1107e-2, -2.213e-2 | 1.3164e-2, -0.4307 |", "1.3164e-2", v["lead.inflection_eps1_star"], "USR eps1 at N*, lead's integrator"),
        ("c22", SP, "| eps1 at N* + 8 / N* + 10 | 1.350e-2 | 1.008e-12 |", "1.350e-2", v[f"{q}.eps1_Nf"], "SR eps1 at N_f"),
        ("c23", SP, "| eps1 at N* + 8 / N* + 10 | 1.350e-2 | 1.008e-12 |", "1.008e-12", v[f"{i}.eps1_Nf"], "USR eps1 at N_f"),
        ("c24", SP, "| late eps2 | -2.69e-2 | -2.76e-2", "-2.69e-2", v[f"{q}.eps2_Nf"], "SR eps2 at N_f"),
        ("c25", SP, "| late eps2 | -2.69e-2 | -2.76e-2", "-2.76e-2", v[f"{i}.eps2_Nf"], "USR eps2 at N_f"),
        ("c26", SP, "SR, full MS: final Delta_R = 1.010-1.012", "1.010", min(v[f"{q}.full_over_est"]), "SR full power at N_f over the estimate at crossing, lowest mode value"),
        ("c27", SP, "SR, full MS: final Delta_R = 1.010-1.012", "1.012", max(v[f"{q}.full_over_est"]), "same, highest"),
        ("c28", SP, "SR, deformed MS: d ln Delta/dN = -0.051 to -0.055", "-0.051", max(v[f"{q}.drift_def"]), "SR deformed drift per e-fold, smallest magnitude"),
        ("c29", SP, "SR, deformed MS: d ln Delta/dN = -0.051 to -0.055", "-0.055", min(v[f"{q}.drift_def"]), "SR deformed drift per e-fold, largest magnitude"),
        ("c30", SP, "at N_f the deformed spectrum is 0.65 (k = dk)", "0.65", v[f"{q}.ratio_def_full"][0], "SR deformed/full at N_f, k = dk"),
        ("c31", SP, "at N_f the deformed spectrum is 0.65 (k = dk)", "0.79", v[f"{q}.ratio_def_full"][-1], "SR deformed/full at N_f, k = 64 dk"),
        ("c32", SP, "USR: deformed/full at N_f is 8.40 at k = dk", "8.40", usr_at(1.0), "USR deformed/full at N_f, k = dk"),
        ("c33", SP, "USR: deformed/full at N_f is 8.40 at k = dk", "1.18", usr_at(4.0), "USR deformed/full, k = 4 dk"),
        ("c34", SP, "USR: deformed/full at N_f is 8.40 at k = dk", "1.07", usr_at(5.656854), "USR deformed/full, k = 5.7 dk"),
        ("c35", SP, "1.0000 at 64 dk", "1.003", usr_at(11.313708), "USR deformed/full, k = 11.3 dk"),
        ("c36", SP, "Full Delta_R at N_f rises monotonically to 1.017", "1.017", v[f"{i}.Delta_full_Nf_last"], "USR full power at N_f, k = 64 dk"),
        ("c37", SP, "over [N_k + 3, N_f] it is 2.5e-4 to 1.9e-3", "2.5e-4", -max(v[f"{q}.drift_ms"]), "SR full drift magnitude, smallest"),
        ("c38", SP, "over [N_k + 3, N_f] it is 2.5e-4 to 1.9e-3", "1.9e-3", -min(v[f"{q}.drift_ms"]), "SR full drift magnitude, largest"),
        ("c39", SP, "1.0805 times the continuum integral", "1.0805", v[f"dn.{q}.lattice_over_cont"], "SR lattice sum over continuum, band dk-64 dk"),
        ("c40", SP, "overestimate the variance by 42-45 percent", "0.42", v[f"dn.{i}.s1"] - 1.0, "excess variance at sigma = 1, USR"),
        ("c41", SP, "overestimate the variance by 42-45 percent", "0.45", v[f"dn.{q}.s1"] - 1.0, "excess variance at sigma = 1, SR"),
        ("c42", EV, "P_R(N_f) = 1.0108 H^2", "1.0108", v["lead.sr_P_full_end"], "lead's SR mode: full power at N_f over the slow-roll estimate"),
        ("c43", EV, "slope -5.8e-4 per e-fold", "-5.8e-4", v["lead.sr_slope_full"], "lead's SR mode: full slope"),
        ("c44", EV, "slope -0.0519 against -4 eps1 = -0.0513", "-0.0519", v["lead.sr_slope_def"], "lead's SR mode: deformed slope"),
        ("c45", EV, "slope -0.0519 against -4 eps1 = -0.0513", "-0.0513", v["lead.sr_minus4eps1"], "lead's SR mode: -4 eps1"),
        ("c46", EV, "0.70 of the full spectrum at N_f", "0.70", v["lead.sr_ratio_def_full"], "lead's SR mode: deformed/full at N_f"),
        ("c47", EV, "2.08 at N_f", "2.08", v["lead.usr_ratio_def_full"], "lead's USR mode: deformed/full at N_f"),
        ("c48", EV, "A13 (2.4e-15), A15 pass, A1 4.1e-14", "4.1e-14", v["val_frozen.A1"], "frozen scheme, A1"),
        ("c49", EV, "A13 (2.4e-15), A15 pass, A1 4.1e-14", "2.4e-15", v["val_frozen.A13"], "frozen scheme, A13"),
        ("c50", EV, "all pass except A1 1.07e-10", "1.07e-10", v["val_markov_tanh.A1"], "Markov-tanh scheme, A1"),
        ("c51", LR, "| linear band variance, continuum int P_R dln k | 3.9248e-10 | 0.79884 |", "3.9248e-10", v[f"dn.{q}.var_lin"], "SR linear band variance"),
        ("c52", LR, "| linear band variance, continuum int P_R dln k | 3.9248e-10 | 0.79884 |", "0.79884", v[f"dn.{i}.var_lin"], "USR linear band variance"),
        ("c53", LR, "| linear band variance on the 256^3 lattice", "0.9997", v[f"dn.{i}.lattice_over_cont"], "USR lattice over continuum"),
        ("c54", LR, "| sigma = 0.01: var / var_lin | 0.9981", "0.9981", v[f"dn.{q}.s0.01"], "SR var/var_lin at sigma = 0.01"),
        ("c55", LR, "| sigma = 0.01: var / var_lin | 0.9981", "1.0001", v[f"dn.{i}.s0.01"], "USR var/var_lin at sigma = 0.01"),
        ("c56", LR, "| sigma = 0.1: var / var_lin | 1.0050", "1.0050", v[f"dn.{q}.s0.1"], "SR var/var_lin at sigma = 0.1"),
        ("c57", LR, "| sigma = 0.1: var / var_lin | 1.0050", "1.0055", v[f"dn.{i}.s0.1"], "USR var/var_lin at sigma = 0.1"),
        ("c58", LR, "| sigma = 1 (literal NR timing): var / var_lin | 1.4492", "1.4492", v[f"dn.{q}.s1"], "SR var/var_lin at sigma = 1"),
        ("c59", LR, "| sigma = 1 (literal NR timing): var / var_lin | 1.4492", "1.4233", v[f"dn.{i}.s1"], "USR var/var_lin at sigma = 1"),
    ]


def locate(doc, needle):
    p = os.path.join(C.TRACK, doc)
    for n, line in enumerate(open(p), 1):
        if needle in line:
            return n
    return None


def check(v):
    out = []
    for cid, doc, needle, printed, val, what in claims(v):
        line = locate(doc, needle)
        tol = half_unit(printed)
        ok = abs(float(val) - float(printed)) <= tol * (1 + 1e-9)
        out.append(dict(id=cid, doc=doc, line=line, printed=printed, computed=float(val),
                        agree=bool(ok), what=what))
    return out


def fmt(x, sig=4):
    return f"{x:.{sig}g}"


def tex_num(x, sig=4):
    s = f"{x:.{sig}g}"
    if "e" in s:
        m, e = s.split("e")
        return f"${m}\\times10^{{{int(e)}}}$"
    return f"${s}$"


def write_ledger(v, res, out):
    runs = [("spec", SPEC_RUN, "background and mode functions, full and deformed"),
            ("lead", LEAD_RUN, "independent background, freezing and delta-N checks"),
            ("dnq", DN["quadratic"], "stochastic delta N, slow roll"),
            ("dni", DN["inflection"], "stochastic delta N, ultra-slow roll"),
            ("val", VAL_RUN, "validation of the code's noise generator"),
            ("cost", costmodel.CODEBASE, "cost model and synthesis operation counts"),
            ("core", costmodel.CORE, "measured card throughput of the code (core)"),
            ("rel", "E-20261115-172423-5234cce", "Markov-tanh noise of the released code (analysis helper)")]
    rid = {k: f"R{n}" for n, (k, _, _) in enumerate(runs, 1)}
    q, i = "quadratic", "inflection"
    rows = [
        ("Background, SR: first slow-roll parameter at the start", tex_num(v[f"{q}.eps1_star"]), rid["spec"]),
        ("Background, SR: first slow-roll parameter at the end", tex_num(v[f"{q}.eps1_Nf"]), rid["spec"]),
        ("Background, USR: first slow-roll parameter at the start", tex_num(v[f"{i}.eps1_star"]), rid["spec"]),
        ("Background, USR: interval with $\\epsilon_2>3$ (e-folds after the start)",
         f"${v['lead.usr_from']:.3f}$--${v['lead.usr_to']:.3f}$", rid["lead"]),
        ("Background, USR: minimum of the first slow-roll parameter", tex_num(v[f"{i}.eps1_min"]), rid["spec"]),
        ("Freezing, SR: full power at the end over the slow-roll estimate at crossing",
         f"${min(v[f'{q}.full_over_est']):.4f}$--${max(v[f'{q}.full_over_est']):.4f}$", rid["spec"]),
        ("Freezing, SR: drift of $\\ln\\Delta_\\mathcal{R}$ per e-fold, full, from $N_k+3$",
         f"{tex_num(min(v[f'{q}.drift_ms']), 3)} to {tex_num(max(v[f'{q}.drift_ms']), 3)}", rid["spec"]),
        ("Freezing, SR: drift per e-fold, deformed",
         f"${min(v[f'{q}.drift_def']):.4f}$ to ${max(v[f'{q}.drift_def']):.4f}$", rid["spec"]),
        ("Freezing, SR: deformed over full power at the end, $k=\\Delta k$ and $64\\,\\Delta k$",
         f"${v[f'{q}.ratio_def_full'][0]:.3f}$, ${v[f'{q}.ratio_def_full'][-1]:.3f}$", rid["spec"]),
        ("Freezing, USR: deformed over full power at the end, $k=\\Delta k$, $4\\,\\Delta k$",
         f"${v[f'{i}.ratio_def_full'][0]:.2f}$, ${v[f'{i}.ratio_def_full'][8]:.3f}$", rid["spec"]),
        ("Freezing, USR: full power at the end, $k=64\\,\\Delta k$", f"${v[f'{i}.Delta_full_Nf_last']:.4f}$", rid["spec"]),
        ("Freezing, independent check: SR slopes full, deformed; $-4\\epsilon_1$",
         f"{tex_num(v['lead.sr_slope_full'], 2)}, ${v['lead.sr_slope_def']:.4f}$; ${v['lead.sr_minus4eps1']:.4f}$", rid["lead"]),
        ("$\\delta N$, SR: linear variance of the band", tex_num(v[f"dn.{q}.var_lin"], 5), rid["dnq"]),
        ("$\\delta N$, USR: linear variance of the band", f"${v[f'dn.{i}.var_lin']:.5f}$", rid["dni"]),
        ("$\\delta N$: lattice sum over continuum, SR, USR",
         f"${v[f'dn.{q}.lattice_over_cont']:.4f}$, ${v[f'dn.{i}.lattice_over_cont']:.4f}$", rid["dnq"] + ", " + rid["dni"]),
        ("$\\delta N$, SR: variance over linear at $\\sigma=0.01,\\,0.1,\\,1$",
         f"${v[f'dn.{q}.s0.01']:.4f}$, ${v[f'dn.{q}.s0.1']:.4f}$, ${v[f'dn.{q}.s1']:.4f}$", rid["dnq"]),
        ("$\\delta N$, USR: variance over linear at $\\sigma=0.01,\\,0.1,\\,1$",
         f"${v[f'dn.{i}.s0.01']:.4f}$, ${v[f'dn.{i}.s0.1']:.4f}$, ${v[f'dn.{i}.s1']:.4f}$", rid["dni"]),
        ("$\\delta N$: skewness at $\\sigma=0.01$, SR, USR",
         f"${v[f'dn.{q}.skew']:.3f}$, ${v[f'dn.{i}.skew']:.3f}$", rid["dnq"] + ", " + rid["dni"]),
        ("Noise: reconstruction from the keys, frozen, Markov-step, Markov-tanh (tolerance $10^{-11}$)",
         f"{tex_num(v['val_frozen.A1'], 2)}, {tex_num(v['val_markov_heaviside.A1'], 2)}, {tex_num(v['val_markov_tanh.A1'], 3)}", rid["val"]),
        ("Noise: frozen scheme, $N$ against $2N$", tex_num(v["val_frozen.A13"], 2), rid["val"]),
        ("Noise, release, Markov-tanh: reconstruction against the standard; the cancellation-free reference",
         f"{tex_num(v['release.val_std.A1'], 3)}; {tex_num(v['release.val_cf.A1'], 2)}", rid["rel"]),
        ("Cost: Z4c; with field; with sources (zone-cycles per second, $128^3$)",
         f"{tex_num(v['core.z4c'], 3)}; {tex_num(v['core.field'], 3)}; {tex_num(v['core.noise'], 3)}", rid["core"]),
        ("Cost: overhead of field and sources over Z4c, assumed; measured",
         f"${v['core.overhead_assumed']:.2f}$; ${v['core.overhead_measured']:.2f}$", rid["cost"] + ", " + rid["core"]),
        ("Cost, SR $256^3$: steps; card-hours model; measured throughput",
         f"${v['cost.quadratic.256.steps']}$; ${v['cost.quadratic.256.model']:.2f}$; ${v['cost.quadratic.256.lo']:.2f}$--${v['cost.quadratic.256.hi']:.2f}$",
         rid["cost"] + ", " + rid["core"]),
        ("Cost, USR $256^3$: steps; card-hours model; measured throughput",
         f"${v['cost.inflection.256.steps']}$; ${v['cost.inflection.256.model']:.2f}$; ${v['cost.inflection.256.lo']:.2f}$--${v['cost.inflection.256.hi']:.2f}$",
         rid["cost"] + ", " + rid["core"]),
        ("Cost: memory of a $256^3$ run (GB)", f"${v['cost.quadratic.256.mem']:.1f}$", rid["cost"]),
    ]
    L = ["\\begin{table*}",
         "\\caption{\\label{tab:ledger}Numerical ledger: the numbers behind the statements and "
         "figures of this note, each with the registered run that produced it.}",
         "\\begin{ruledtabular}", "\\footnotesize",
         "\\begin{tabular}{p{0.56\\textwidth}p{0.26\\textwidth}p{0.08\\textwidth}}",
         "Quantity & Value & Run \\\\", "\\hline"]
    for a, b, c in rows:
        L.append(f"{a} & {b} & {c} \\\\")
    L += ["\\hline", "\\multicolumn{3}{l}{Registered runs:} \\\\"]
    for n, (k, r, what) in enumerate(runs, 1):
        L.append(f"\\multicolumn{{3}}{{l}}{{R{n}\\quad\\texttt{{{r}}}\\quad {what}}} \\\\")
    L += ["\\end{tabular}", "\\end{ruledtabular}", "\\end{table*}"]
    open(os.path.join(out, "ledger.tex"), "w").write("\n".join(L) + "\n")


def write_parameters(v, out):
    q, i = "quadratic", "inflection"
    L = ["\\begin{table*}",
         "\\caption{\\label{tab:parameters}Parameters of the two test cases.}",
         "\\begin{ruledtabular}", "\\footnotesize",
         "\\begin{tabular}{lll}",
         " & slow roll & ultra-slow roll \\\\", "\\hline",
         "potential & $\\tfrac12 m^2\\phi^2$ & inflection form \\\\",
         "parameters of the source & $\\epsilon_1=0.01$, $\\epsilon_2=-0.02$ & $\\Lambda=1.86\\times10^{-6}$, $v=0.198\\,M_\\mathrm{Pl}$ \\\\",
         f" & $H_0=10^{{-5}}M_\\mathrm{{Pl}}$ & $\\phi_0={v[f'{i}.phi0']:g}\\,M_\\mathrm{{Pl}}$ \\\\",
         f"derived & $\\phi_0={v[f'{q}.phi0']:.4f}\\,M_\\mathrm{{Pl}}$ & $H_0={v[f'{i}.H0']*1e6:.4f}\\times10^{{-6}}M_\\mathrm{{Pl}}$ \\\\",
         f" & $m={v[f'{q}.m']*1e6:.5f}\\times10^{{-6}}M_\\mathrm{{Pl}}$ & $\\mathrm{{d}}\\phi/\\mathrm{{d}}N={v[f'{i}.dphidN0']:.6f}\\,M_\\mathrm{{Pl}}$ \\\\",
         f"$N_*-N_0$, $N_f-N_*$ & ${v[f'{q}.Nstar']:g}$, ${v[f'{q}.Nf']-v[f'{q}.Nstar']:g}$ & ${v[f'{i}.Nstar']:g}$, ${v[f'{i}.Nf']-v[f'{i}.Nstar']:g}$ \\\\",
         "lattice & \\multicolumn{2}{l}{$256^3$ cells, $L\\,k_{\\sigma*}=2\\pi$, $k_\\mathrm{max}=64\\,\\Delta k$} \\\\",
         "window & \\multicolumn{2}{l}{$\\tanh$ profile, steepness $s=5$, $\\sigma=1$} \\\\",
         "gauge & \\multicolumn{2}{l}{geodesic slicing, zero shift, undamped} \\\\",
         "Courant factor & \\multicolumn{2}{l}{$0.25$; tests at $0.125$, $0.0625$} \\\\",
         "noise coefficients & \\multicolumn{2}{l}{Friedmann background; box means as a variant} \\\\",
         "\\end{tabular}", "\\end{ruledtabular}", "\\end{table*}"]
    open(os.path.join(out, "parameters.tex"), "w").write("\n".join(L) + "\n")


# ------------------------------------------------------------------------------ gate G1
FINAL = "ladder/results/final"
FLOOR_JSON = "ladder/results/floor/floor.json"
A6_JSON = "ladder/results/a6/a6.json"
G1 = {"fin": "E-20261115-194633-9e04ed8", "floor": "E-20261119-142713-32c883a",
      "a6": "E-20261119-145230-ff0dff2", "card": "E-20261115-172618-f948386",
      "tests": "E-20261115-171445-36152c4", "self": "E-20261115-172935-ddfade0",
      "e6": "E-20261115-174214-74becdd", "a11": "E-20261115-180533-24a7781",
      "a14": "E-20261115-184748-9b010fa", "a12": "E-20261119-141654-c2a10d1"}
G1_WHAT = {"fin": "final analysis of the slow-roll ladder (A1-A5, spectrum, negative control)",
           "floor": "floor analysis of the odd constraint parts (A5, halving, crossing)",
           "a6": "temporal order A6 (three Courant factors at $32^3$)",
           "card": "$256^3$ slow-roll run in the paper's set-up on one card (cost)",
           "tests": "synthetic tests of the analysis module",
           "self": "reader of the dumps against core's reader",
           "e6": "extraction factor of the anisotropic term of the curvature perturbation",
           "a11": "noise for three MeshBlock layouts on a card",
           "a14": "card against processors",
           "a12": "restart on processors and on a card"}
# core's explanation of the first-order constraint part: written on core/scalar-3 (88544a5),
# released with core-v0.5 as coord/INTERFACES/scalar_field_3.md (read in the repository at the
# lines below; not yet checked by the track: [TO VERIFY], package a4res of round 1 tests it)
CORE_DOC = ("release core-v0.5", "coord/INTERFACES/scalar_field_3.md")
CORE_RUNS = "core-20261119-151758-51d9a71, -152243-1754ebc, -161111-9d05d14"
CORE_NUMBERS = [  # (key, value, line of the document, the text that holds it)
    ("core.mu4", 0.110, 143, "mu/k^2 = 0.110 at 4 cells per wavelength"),
    ("core.mu8", 2.6e-3, 143, "2.6e-3 at 8"),
    ("core.mu16", 4.4e-5, 143, "4.4e-5 at 16"),
    ("core.slope", -5.93, 156, "slope -5.93"),
    ("core.peak4", 692.0, 160, "692, 213, 77"),
    ("core.cells1", 12.7, 162, "below 1 at 12.7 cells"),
    ("core.kmax256", 20.0, 164, "k_max <= 20 dk at 256^3"),
]
# the fresh-context verifier of the G1 material (helper g1verify; its report copied to
# stage/G1/VERIFIER.md by the lead); numbers the note quotes from it, with their lines
VER_DOC = "stage/G1/VERIFIER.md"
VER_RUNS = "E-20261121-030207-fb6f090, -031951-82984f8, -030522-c6907b6, -031049-27cdc06, -031251-c48670d"
VER_NUMBERS = [
    ("ver.nc.point", 89.0, 303, "ratio falls to 89 at the end"),
    ("ver.nc.max.lo", 1709.0, 374, "ratio of maxima 1709-1874"),
    ("ver.nc.max.hi", 1874.0, 374, "ratio of maxima 1709-1874"),
    ("ver.even.128.256", 0.8, 332, "L256 within 0.8 percent"),
]
# reproducibility of the G1 executable (verifier) and of the release against it (lead of batch 2a)
REP_NUMBERS = [  # (key, value, document, line, text)
    ("rep.ver.vars", 22.0, "stage/G1/STATUS.md", 30, "all 22 variables bit-identical at 32^3"),
    ("rep.lr1.words", 18.9e6, "stage/REVIEW-wave3.md", 111, "18.9 million 64-bit words, 0 differing"),
    ("rep.lr1.diff", 0.0, "stage/REVIEW-wave3.md", 111, "18.9 million 64-bit words, 0 differing"),
]
LR1_RUN = "E-20261121-064707-77ec326"
TMAX = 4.5 + 1e-9   # common end time of the s = -1 partners; later dumps pair different times


def doc_check(rel, numbers):
    """Each number on its line of a document of the repository (rel to the repository root
    for coord/, to the track otherwise); None if the document is missing."""
    root = os.path.dirname(C.TRACKS) if rel.startswith("coord/") else C.TRACK
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        return None
    txt = open(p).read().splitlines()
    return {k: (ln <= len(txt) and needle in txt[ln - 1]) for k, _, ln, needle in numbers}


def core_doc_check():
    return doc_check(CORE_DOC[1], CORE_NUMBERS)


def deformed_drift():
    """Drift per e-fold of the deformed equation (FLRW lattice) from N_k + 4 to N_* + 8 for
    the shells of the reference run inside the A3 set (k <= sqrt(62) dk), as in
    fig_sr_freezing.py."""
    d = np.load(C.path(SPEC_RUN, "quadratic.npz"))
    kk = d["k"] / float(d["dk"])
    Nr = d["N"] - float(d["Nstar"])
    out = []
    for s in np.nonzero(kk <= np.sqrt(62.0) + 1e-9)[0]:
        n4 = float(d["Ncross"][s] - d["Nstar"]) + 4.0
        use = Nr >= n4
        out.append(float(np.polyfit(Nr[use], np.log(np.abs(d["R_def"][s][use]) ** 2), 1)[0]))
    return out


def gather_g1():
    s = C.committed_json(f"{FINAL}/summary.json")
    fl = C.committed_json(FLOOR_JSON)
    a6 = C.committed_json(A6_JSON)
    g = {}
    a1 = s["A1"]["per_run"]
    for q in ("phi", "Pi", "K"):
        g[f"A1.{q}"] = max(r[q] for r in a1.values())
        g[f"A1.{q}.argmax"] = max(a1, key=lambda r: a1[r][q])
    for n in (32, 64, 128, 256):
        g[f"A1.efolds.{n}"] = a1[f"L{n}p"]["efolds"]
    rungs_l = ["L32p", "L64p", "L128p", "L256p"]
    rungs_q = ["Q64p", "Q128p", "P256"]
    for r in rungs_l + rungs_q:
        g[f"A2.{r}"] = s["A2"][r]["max_D_half"]
        g[f"A2.all.{r}"] = s["A2"][r]["max_D_all"]
    g["A2.P256.nhalf"] = s["A2"]["P256"]["n_half"]
    g["A2.P256.modes"] = C.committed_json(f"{FINAL}/P256_judge.json")["modes"]
    g["A2.P256.stencil"] = s["A2"]["P256"]["stencil_reference"]["max_D_half"]
    g["A2.rungs.lo"] = min(g[f"A2.{r}"] for r in rungs_l + ["Q64p", "Q128p"])
    g["A2.rungs.hi"] = max(g[f"A2.{r}"] for r in rungs_l + ["Q64p", "Q128p"])
    sp = s["spectrum"]
    g["spec.P256"] = sp["P256"]["shell_ratio_alpha_corrected_max_dev"]
    g["spec.max"] = max(v["shell_ratio_alpha_corrected_max_dev"] for v in sp.values())
    g["spec.sr.lo"], g["spec.sr.hi"] = sp["P256"]["lin_over_sr_k_le_7"]
    a3 = {r: v for r, v in s["A3"].items() if v.get("n_modes")}
    g["A3.n"] = a3["P256"]["n_modes"]
    g["A3.ratio"] = max(v["max_abs_ratio_minus_1"] for v in a3.values())
    g["A3.drift.lo"] = min(v["max_abs_drift_nr"] for v in a3.values())
    g["A3.drift.hi"] = max(v["max_abs_drift_nr"] for v in a3.values())
    g["A3.diff"] = max(v["max_abs_drift_difference"] for v in a3.values())
    g["A3.ratio.P256"] = a3["P256"]["max_abs_ratio_minus_1"]
    g["A3.drift.P256"] = a3["P256"]["max_abs_drift_nr"]
    dd = deformed_drift()
    g["A3.flrw.lo"], g["A3.flrw.hi"] = min(abs(x) for x in dd), max(abs(x) for x in dd)
    g["A3.flrw.factor"] = g["A3.flrw.lo"] / g["A3.drift.hi"]
    g["A3.flrw.mean"] = float(np.mean([abs(x) for x in dd]))
    a4 = s["A4"]
    for n in (32, 64, 128, 256):
        g[f"A4.oe.summary.{n}"] = a4[f"N{n}"]["max_odd_over_even_H"]
        g[f"A4.recH.{n}"] = a4[f"N{n}"]["max_record_H"]
        g[f"A4.recM.{n}"] = a4[f"N{n}"]["max_record_M"]
        g[f"A4.first.{n}"] = fl["crossing"][f"N{n}"]["first_dump_odd_gt_even"]
        g[f"A4.ln.{n}"] = fl["crossing"][f"N{n}"]["ln_N_over_8"]
    pairs = {32: "pair_L32p_L32m", 64: "pair_Q64p_Q64m", 128: "pair_Q128p_Q128m",
             256: "pair_P256_P256m"}
    for n, name in pairs.items():
        rows = [r for r in C.committed_json(f"{FINAL}/{name}.json")["rows"] if r["time"] <= TMAX]
        best = max(rows, key=lambda r: r["H_odd"] / r["H_even"])
        g[f"A4.oe.{n}"] = best["H_odd"] / best["H_even"]
        g[f"A4.oe.at.{n}"] = best["efolds"]
        g[f"A4.lastpaired.{n}"] = rows[-1]["efolds"]
    for n in (64, 128, 256):
        rows = [r for r in C.committed_json(f"{FINAL}/pair_L{n}p_L{n}m.json")["rows"] if r["time"] <= TMAX]
        g[f"A4.L.oe.{n}"] = max(r["H_odd"] / r["H_even"] for r in rows)
        g[f"A4.L.oe.summary.{n}"] = a4[f"L{n}"]["max_odd_over_even_H"]
    h32 = fl["halving"]["N32"]
    g["half.odd.lo"], g["half.odd.hi"] = min(h32["H_odd"][1:]), max(h32["H_odd"][1:])
    g["half.even.lo"], g["half.even.hi"] = min(h32["H_even"]), max(h32["H_even"])
    nc = s["negative_control"]
    g["nc.H.lo"] = min(v["H_record_ratio_max"] for v in nc.values())
    g["nc.H.hi"] = max(v["H_record_ratio_max"] for v in nc.values())
    g["nc.M.lo"] = min(v["M_record_max"] for v in nc.values())
    g["nc.M.hi"] = max(v["M_record_max"] for v in nc.values())
    g["nc.oe"] = min(v["H_odd_over_even_min_first2"] for v in nc.values())
    g["A5.H.lo"], g["A5.H.hi"] = fl["A5"]["H_odd"]["range_used"]
    g["A5.M.lo"], g["A5.M.hi"] = fl["A5"]["M_odd"]["range_used"]
    g["floor.qH"], g["floor.qM"] = fl["floor"]["H_odd"]["q"], fl["floor"]["M_odd"]["q"]
    g["floor.256.first"] = fl["parts"]["H_odd"]["256"][0]
    g["floor.256.last"] = fl["parts"]["H_odd"]["256"][-1]
    g["floor.t.first"], g["floor.t.last"] = fl["efolds"][0], fl["efolds"][-1]
    g["even.64.128"] = max(abs(1 - x) for x in fl["even_check"]["even64_over_even128"])
    for n in (32, 64, 128):
        con = np.load(C.path(G1["fin"], f"res/L{n}p.npz"))["con"]
        g[f"H0.{n}"] = float(con[-1, 3])
    ords = [x for k, v in a6["A6"].items() if v["orders"] for x in v["orders"]]
    g["A6.lo"], g["A6.hi"] = min(ords), max(ords)
    g["A6.Rdiff"] = max(a6["diff"]["T25-T12"]["R_all"])
    zm = np.load(C.path(G1["a6"], "a6_modes.npz"))
    for t in ("T25", "T12", "T06"):
        g[f"A6.top.{t}"] = float(np.max(zm[f"D_last_{t}"][zm["n2"] >= 49]))
    late = a6["orders"]["H_odd_ratio_25_12"][3:] + a6["orders"]["H_odd_ratio_12_06"][3:]
    g["A6.oddH.change"] = max(abs(x - 1.0) for x in late)
    g["A6.H0.order"] = min(x for x in a6["orders"]["H0_diff_order"][1:])
    v11 = C.load_json(G1["a11"], "val_card_frozen/validation.json")
    g["A7.A11"] = max(t["value"] for t in v11 if t["id"] == "A11")
    for plat in ("proc", "card"):
        v12 = C.load_json(G1["a12"], f"val_{plat}_a12/validation.json")
        g[f"A7.A12.{plat}"] = next(t["value"] for t in v12 if t["id"] == "A12")
    v14 = C.load_json(G1["a14"], "val_a14/validation.json")
    g["A7.A14"] = next(t["value"] for t in v14 if t["id"] == "A14")
    ts = C.load_json(G1["tests"], "test_sfa.json")["results"]
    g["T.n"], g["T.pass"] = len(ts), sum(bool(t["passed"]) for t in ts)
    t2 = {t["id"]: t for t in ts}
    g["T2a"], g["T2a.slope"], g["T2b"] = t2["T2a"]["value"], t2["T2a"]["slope"], t2["T2b"]["value"]
    st = C.load_json(G1["self"], "selftest.json")
    g["self.T1"] = st["T1_max_abs_difference"]
    g["self.D0"] = st["dumps_table"][0]["D_max_in"]
    e6 = C.load_json(G1["e6"], "extraction_check.json")["cases"]
    g["E6.quarter"] = e6["factor 1/4 (SPEC E6)"]["max_D_half"]
    g["E6.half"] = e6["factor 1/2"]["max_D_half"]
    g["E6.mquarter"] = e6["factor -1/4"]["max_D_half"]
    g["E6.none"] = e6["without the gt term"]["max_D_half"]
    m = C.manifest(G1["card"])
    g["cost.card_hours"] = m["resources"]["gpu_hours"]
    g["cost.wall"] = m["resources"]["walltime_s"]
    g["cost.steps"] = s["cost"]["P256"]["cycles"]
    sps = [s["cost"][r]["s_per_step"] for r in ("P256", "P256m", "L256p")]
    g["cost.sps.lo"], g["cost.sps.hi"] = min(sps), max(sps)
    for k, val, _, _ in CORE_NUMBERS:
        g[k] = val
    g["core.doc_check"] = core_doc_check()
    for k, val, _, _ in VER_NUMBERS:
        g[k] = val
    g["ver.doc_check"] = doc_check(VER_DOC, VER_NUMBERS)
    for k, val, _, _, _ in REP_NUMBERS:
        g[k] = val
    g["rep.doc_check"] = {}
    for k, _, doc, ln, needle in REP_NUMBERS:
        r = doc_check(doc, [(k, None, ln, needle)])
        g["rep.doc_check"][k] = None if r is None else r[k]
    return g


def claims_g1(g):
    """(id, document, search text, printed, computed, what) for the G1 numbers of the lead's
    stage status (as rewritten by the lead of batch 2a, 2026-11-21) and the ladder's README."""
    ST, LR = "stage/G1/STATUS.md", "ladder/README.md"
    return [
        ("g01", ST, "1.21e-4 over 68532 modes", "1.21e-4", g["A2.P256"], "A2, 256^3 paper set-up, max D_n for |n| <= 32"),
        ("g02", ST, "1.21e-4 over 68532 modes", "68532", g["A2.P256.nhalf"], "A2, modes with |n| <= 32 at 256^3"),
        ("g03", ST, "rungs 1.7e-6 to 9.9e-5", "1.7e-6", g["A2.rungs.lo"], "A2, smallest rung maximum"),
        ("g04", ST, "rungs 1.7e-6 to 9.9e-5", "9.9e-5", g["A2.rungs.hi"], "A2, largest rung maximum (Q128)"),
        ("g05", ST, "1051 modes per rung", "1051", g["A3.n"], "A3, modes with N_f - N_k >= 6"),
        ("g06", ST, "ratio within 2.4e-6 to 4.6e-6", "4.6e-6", g["A3.ratio"], "A3 ratio, largest over the rungs"),
        ("g07", ST, "drift 1.38e-4 per e-fold", "1.38e-4", g["A3.drift.P256"], "A3 drift, largest at 256^3 (P256)"),
        ("g08", ST, "FLRW-lattice drift -0.052 per e-fold", "0.052", g["A3.flrw.mean"], "drift of the deformed equation, mean over the A3 shells"),
        ("g09", ST, "2.0e-12 (phi, P256)", "2.0e-12", g["A1.phi"], "A1 phi, largest over every rung"),
        ("g10", ST, "8.6e-12 (Pi)", "8.6e-12", g["A1.Pi"], "A1 Pi, largest over every rung"),
        ("g11", ST, "3.6e-12 (K, L32p)", "3.6e-12", g["A1.K"], "A1 K, largest over every rung"),
        ("g12", ST, "e-folds off by 5.5e-6 at N = 32", "5.5e-6", g["A1.efolds.32"], "A1 e-folds from <chi>, 32^3"),
        ("g13", ST, "up to 745, 655, 869 at N = 32, 64, 128", "745", g["A4.oe.32"], "largest odd/even of H, 32^3, time-matched dumps"),
        ("g14", ST, "up to 745, 655, 869 at N = 32, 64, 128", "655", g["A4.oe.64"], "same, 64^3"),
        ("g15", ST, "up to 745, 655, 869 at N = 32, 64, 128", "869", g["A4.oe.128"], "same, 128^3"),
        ("g16", ST, "and 25 at N = 256", "25", g["A4.oe.256"], "same, 256^3 (last time-matched dump)"),
        ("g17", ST, "record ratio up to 4e4-1.5e5", "4e4", g["nc.H.lo"], "negative control, record H ratio, smallest of the maxima"),
        ("g18", ST, "record ratio up to 4e4-1.5e5", "1.5e5", g["nc.H.hi"], "negative control, record H ratio, largest"),
        ("g19", ST, "2.2 percent 64/128 raw", "2.2", 100.0 * g["even.64.128"], "even part, 64^3 against 128^3, percent"),
        ("g20", ST, "uniform residual H0 at order 4.1", "4.1", g["A6.H0.order"], "order of the uniform residual in the time step (lowest)"),
        ("g21", ST, "two realisations measured: 0.503", "0.503", g["cost.card_hours"], "card-hours of the 256^3 realisation (manifest)"),
        ("g22", LR, "box means within 1.1e-12 (phi)", "1.1e-12", g["A1.phi"], "A1 phi, largest over every rung"),
        ("g23", LR, "8.6e-12 (Pi), 2.0e-12 (K)", "2.0e-12", g["A1.K"], "A1 K, largest over every rung"),
        ("g24", LR, "e-folds 5.5e-6, 3.3e-7, 2.0e-8", "3.3e-7", g["A1.efolds.64"], "A1 e-folds from <chi>, 64^3"),
        ("g25", LR, "e-folds 5.5e-6, 3.3e-7, 2.0e-8", "2.0e-8", g["A1.efolds.128"], "same, 128^3"),
        ("g26", LR, "8.8e-5 (L32) to 1.7e-6 (L256)", "8.8e-5", g["A2.L32p"], "A2, 32^3 rung"),
        ("g27", LR, "Q64 9.7e-5, Q128 9.9e-5", "9.7e-5", g["A2.Q64p"], "A2, 64^3 paper set-up"),
        ("g28", LR, "power ratio within 4.6e-6", "4.6e-6", g["A3.ratio"], "A3 ratio, largest over the rungs"),
        ("g29", LR, "= full MS within 1.8e-6", "1.8e-6", g["A3.diff"], "A3 drift, code minus full equation"),
        ("g30", LR, "shell ratios within 1.9e-4", "1.9e-4", g["spec.max"], "shell ratio against the reference with the same alpha, all rungs"),
        ("g31", LR, "formula 1.0104-1.0109", "1.0104", g["spec.sr.lo"], "linear spectrum over the slow-roll formula, |n| <= 7, lowest"),
        ("g32", LR, "formula 1.0104-1.0109", "1.0109", g["spec.sr.hi"], "same, highest"),
        ("g33", LR, "odd part order 4.2-5.8 (H)", "4.2", g["A5.H.lo"], "A5 order of the odd part of H, lowest"),
        ("g34", LR, "odd part order 4.2-5.8 (H)", "5.8", g["A5.H.hi"], "A5 order of the odd part of H, highest"),
        ("g35", LR, "5.6-5.9 (M)", "5.6", g["A5.M.lo"], "A5 order of the odd part of M, lowest"),
        ("g36", LR, "5.6-5.9 (M)", "5.9", g["A5.M.hi"], "A5 order of the odd part of M, highest"),
        ("g37", LR, "fall at order 3.93-4.08", "3.93", g["A6.lo"], "A6 orders, lowest"),
        ("g38", LR, "fall at order 3.93-4.08", "4.08", g["A6.hi"], "A6 orders, highest"),
        ("g39", LR, "M/[M] 0.20-0.22", "0.20", g["nc.M.lo"], "negative control <|M|/[M]>, smallest maximum"),
        ("g40", LR, "M/[M] 0.20-0.22", "0.22", g["nc.M.hi"], "negative control <|M|/[M]>, largest maximum"),
        ("g41", LR, "1.13-1.30 card-s per step", "1.13", g["cost.sps.lo"], "seconds per step at 256^3, lowest"),
        ("g42", LR, "1.13-1.30 card-s per step", "1.30", g["cost.sps.hi"], "seconds per step at 256^3, highest"),
        ("g43", LR, "odd > even at N = 1.51, 1.99, 2.96, 3.44", "1.51", g["A4.first.32"], "first dump with odd > even, 32^3"),
        ("g44", LR, "odd > even at N = 1.51, 1.99, 2.96, 3.44", "3.44", g["A4.first.256"], "first dump with odd > even, 256^3"),
        ("g45", LR, "at most 745 (N = 32), 655 (64), 869 (128), 25 (256", "25", g["A4.oe.256"], "time-matched odd/even, 256^3"),
    ]


def e(x, sig=2):
    """x with sig significant digits (trailing zeros kept), scientific below 0.01 or from 1e4."""
    x = float(x)
    if x == 0.0:
        return "$0$"
    ex = int(np.floor(np.log10(abs(x))))
    m = x / 10.0 ** ex
    if round(abs(m), sig - 1) >= 10.0:
        ex, m = ex + 1, m / 10.0
    if -2 <= ex < 4:
        return f"${x:.{max(sig - 1 - ex, 0)}f}$"
    return f"${m:.{sig - 1}f}\\times10^{{{ex}}}$"


def write_ledger_g1(g, out):
    lab = {k: f"R{n}" for n, k in enumerate(G1, 9)}
    q = lambda *ks: ", ".join(lab[k] for k in ks)  # noqa: E731
    rng = lambda a, b, f="{:.2f}": f"${f.format(a)}$--${f.format(b)}$"  # noqa: E731
    rows = [
        # (quantity, value, run, evidence label)
        ("A1: box means of $\\phi$, $\\Pi$, $K$ against the Friedmann reference, largest over the rungs",
         f"{e(g['A1.phi'])}, {e(g['A1.Pi'])}, {e(g['A1.K'])}", q("fin"), "VERIFIED"),
        ("A1: e-folds from $\\langle\\chi\\rangle$ after 8.1 e-folds, $32^3$, $64^3$, $128^3$",
         f"{e(g['A1.efolds.32'])}, {e(g['A1.efolds.64'])}, {e(g['A1.efolds.128'])}", q("fin"), "VERIFIED"),
        ("A2: largest $D_n$ for $k\\leq k_\\mathrm{max}/2$, ladder $32^3$, $64^3$, $128^3$, $256^3$",
         ", ".join(e(g[f"A2.L{n}p"]) for n in (32, 64, 128, 256)), q("fin"), "VERIFIED"),
        ("A2: the same in the paper's set-up, $64^3$, $128^3$, $256^3$",
         f"{e(g['A2.Q64p'])}, {e(g['A2.Q128p'])}, {e(g['A2.P256'], 3)}", q("fin"), "VERIFIED"),
        ("A2: modes of the $256^3$ run, all and with $k\\leq k_\\mathrm{max}/2$",
         f"${g['A2.P256.modes']}$, ${g['A2.P256.nhalf']}$", q("fin"), "VERIFIED"),
        ("A2: largest $D_n$ over all modes, ladder $32^3$, $64^3$, $128^3$",
         ", ".join(e(g[f"A2.all.L{n}p"], 3) for n in (32, 64, 128)), q("fin"), "VERIFIED"),
        ("A2: $256^3$ against a reference with the stencil's wave number",
         e(g["A2.P256.stencil"], 3), q("fin"), "VERIFIED"),
        ("Spectrum: shell ratio against the reference with the same $\\alpha_k$, largest over the rungs",
         e(g["spec.max"]), q("fin"), "VERIFIED"),
        ("Spectrum: linear power over the slow-roll formula, $k\\leq7\\,k_{\\sigma*}$",
         rng(g["spec.sr.lo"], g["spec.sr.hi"], "{:.4f}"), q("fin"), "VERIFIED"),
        ("A3: modes with $N_f-N_k\\geq6$ per rung", f"${g['A3.n']}$", q("fin"), "VERIFIED"),
        ("A3: largest $|Q_n(N_f)/Q_n(N_k+4)-1|$ over the rungs", e(g["A3.ratio"]), q("fin"), "VERIFIED"),
        ("A3: largest drift of $\\ln|\\mathcal{R}_n|^2$ per e-fold, range over the rungs",
         f"{e(g['A3.drift.lo'], 4)}--{e(g['A3.drift.hi'], 4)}", q("fin"), "VERIFIED"),
        ("A3: drift of the code minus that of the full equation, largest", e(g["A3.diff"], 3), q("fin"), "VERIFIED"),
        ("A3: drift of the FLRW lattice for the same shells; over the largest drift of the code",
         f"{rng(g['A3.flrw.lo'], g['A3.flrw.hi'], '{:.4f}')}; ${g['A3.flrw.factor']:.0f}$", "R1, " + q("fin"), "VERIFIED"),
        ("A4: largest odd over even part of $\\mathcal{H}$ at dumps where both runs of the pair share the time, paper set-up, $32^3$, $64^3$, $128^3$, $256^3$",
         ", ".join(f"${g[f'A4.oe.{n}']:.0f}$" for n in (32, 64, 128, 256)), q("fin"), "VERIFIED"),
        ("A4: e-folds of these maxima; last time-matched dump of the $256^3$ pair",
         ", ".join(f"${g[f'A4.oe.at.{n}']:.2f}$" for n in (32, 64, 128, 256)) + f"; ${g['A4.lastpaired.256']:.2f}$",
         q("fin"), "VERIFIED"),
        ("A4: first dump with odd above even part (e-folds); $\\ln(N/8)$, same lattices",
         ", ".join(f"${g[f'A4.first.{n}']:.2f}$" for n in (32, 64, 128, 256)) + "; " +
         ", ".join(f"${g[f'A4.ln.{n}']:.2f}$" for n in (32, 64, 128, 256)), q("floor"), "VERIFIED"),
        ("A4: largest record $\\langle|\\mathcal{H}|/[\\mathcal{H}]\\rangle$; $\\langle|\\mathcal{M}|/[\\mathcal{M}]\\rangle$, paper set-up",
         f"{e(max(g[f'A4.recH.{n}'] for n in (32, 64, 128, 256)))}; {e(max(g[f'A4.recM.{n}'] for n in (32, 64, 128, 256)))}",
         q("fin"), "VERIFIED"),
        ("A4: halving factors at $32^3$, odd part; even part",
         f"{rng(g['half.odd.lo'], g['half.odd.hi'], '{:.4f}')}; {rng(g['half.even.lo'], g['half.even.hi'], '{:.3f}')}",
         q("floor"), "VERIFIED"),
        ("A4: largest odd over even part, convergence set-up, $64^3$, $128^3$, $256^3$",
         f"${g['A4.L.oe.64']:.1f}$, ${g['A4.L.oe.128']:.2f}$, ${g['A4.L.oe.256']:.2f}$", q("fin"), "VERIFIED"),
        ("Negative control: record $\\mathcal{H}$ over the proper run, range of the maxima; $\\langle|\\mathcal{M}|/[\\mathcal{M}]\\rangle$",
         f"{e(g['nc.H.lo'])}--{e(g['nc.H.hi'])}; {rng(g['nc.M.lo'], g['nc.M.hi'])}", q("fin"), "VERIFIED"),
        ("A5: order of the odd part before the floor, $32^3\\to64^3\\to128^3$, $\\mathcal{H}$; $\\mathcal{M}$",
         f"{rng(g['A5.H.lo'], g['A5.H.hi'])}; {rng(g['A5.M.lo'], g['A5.M.hi'])}", q("floor"), "VERIFIED (floor fixed after the data)"),
        ("Floor: growth with the cells per side, exponent for $\\mathcal{H}$; $\\mathcal{M}$",
         f"${g['floor.qH']:.2f}$; ${g['floor.qM']:.2f}$", q("floor"), "VERIFIED (attribution: JUDGEMENT)"),
        ("Floor: odd part of $\\mathcal{H}$ at $256^3$, first and last dump of the comparison",
         f"{e(g['floor.256.first'])}, {e(g['floor.256.last'])}", q("floor"), "VERIFIED"),
        ("Even part: $64^3$ against $128^3$, largest relative difference", e(g["even.64.128"]), q("floor"), "VERIFIED"),
        ("Record $\\langle|\\mathcal{H}|/[\\mathcal{H}]\\rangle$ at $N_f$, $32^3$, $64^3$, $128^3$",
         f"{e(g['H0.32'], 3)}, {e(g['H0.64'], 3)}, {e(g['H0.128'], 3)}", q("fin"), "VERIFIED"),
        ("A6: orders of the differences between Courant factors", rng(g["A6.lo"], g["A6.hi"]), q("a6"), "VERIFIED"),
        ("A6: largest difference of $\\mathcal{R}^\\mathrm{NR}_n$ between $\\theta=0.25$ and $0.125$",
         e(g["A6.Rdiff"]), q("a6"), "VERIFIED"),
        ("A6: largest $D_n$ of the top shells at $\\theta=0.25$, $0.125$, $0.0625$",
         ", ".join(e(g[f"A6.top.{t}"], 3) for t in ("T25", "T12", "T06")), q("a6"), "VERIFIED"),
        ("A6: odd part of $\\mathcal{H}$ in the late entry, largest change per halving of $\\theta$",
         e(g["A6.oddH.change"]), q("a6"), "VERIFIED"),
        ("A6: order of the uniform residual of $\\mathcal{H}$", f"${g['A6.H0.order']:.2f}$", q("a6"), "VERIFIED"),
        ("A7: noise for one, eight, sixty-four MeshBlocks; restart on processors, card; card against processors",
         f"${g['A7.A11']:g}$; ${g['A7.A12.proc']:g}$, ${g['A7.A12.card']:g}$; {e(g['A7.A14'])}",
         q("a11", "a12", "a14"), "VERIFIED"),
        ("A7: variables bit-identical between one and eight MeshBlocks and through a restart, the executable of the slow-roll runs at $32^3$",
         f"${g['rep.ver.vars']:.0f}$ of ${g['rep.ver.vars']:.0f}$", "V", "VERIFIED (by the verifier)"),
        ("A7: released processor build against the executable of the slow-roll runs, $32^3$ pair: 64-bit words compared; differing",
         f"${g['rep.lr1.words'] / 1e6:.1f}\\times10^{{6}}$; ${g['rep.lr1.diff']:.0f}$", "L", "VERIFIED (by the lead)"),
        ("Analysis: synthetic tests passed", f"${g['T.pass']}$ of ${g['T.n']}$", q("tests"), "VERIFIED"),
        ("Analysis: $\\mathcal{R}^\\mathrm{NR}$ at amplitude $10^{-5}$, error and its slope; without the metric term",
         f"{e(g['T2a'], 3)}, ${g['T2a.slope']:.3f}$; ${g['T2b']:.3f}$", q("tests"), "VERIFIED"),
        ("Analysis: reader against core's, largest difference; $D_n$ at the start",
         f"${g['self.T1']:g}$; {e(g['self.D0'])}", q("self"), "VERIFIED"),
        ("Analysis: largest $D_n$ ($32^3$, $k\\leq k_\\mathrm{max}/2$) with the factor $1/4$, $1/2$, $-1/4$, none",
         ", ".join(e(g[k]) for k in ("E6.quarter", "E6.half", "E6.mquarter", "E6.none")), q("e6"), "VERIFIED"),
        ("Cost of one $256^3$ realisation, 8.1 e-folds: card-hours; seconds; steps",
         f"${g['cost.card_hours']:.3f}$; ${g['cost.wall']:.0f}$; ${g['cost.steps']}$", q("card", "fin"), "VERIFIED"),
        ("Cost: seconds per step at $256^3$ on one card", rng(g["cost.sps.lo"], g["cost.sps.hi"]), q("fin"), "VERIFIED"),
        ("Verifier: control over proper first-order part, ratio of the maxima over the entry; pointwise at the end of the entry, lowest",
         f"${g['ver.nc.max.lo']:.0f}$--${g['ver.nc.max.hi']:.0f}$; ${g['ver.nc.point']:.0f}$", "V", "VERIFIED (by the verifier)"),
        ("Verifier: even part, $128^3$ against $256^3$ in the convergence set-up after each run's floor is removed (percent)",
         f"${g['ver.even.128.256']:.1f}$", "V", "VERIFIED (by the verifier)"),
        ("Core: stencil mismatch $\\mu/k^2$ at four, eight, sixteen cells per wavelength",
         f"${g['core.mu4']:.3f}$, {e(g['core.mu8'])}, {e(g['core.mu16'])}", "C", "TO VERIFY"),
        ("Core: largest odd over even part at four cells per wavelength; cells where it falls below one",
         f"${g['core.peak4']:.0f}$; ${g['core.cells1']:.1f}$", "C", "TO VERIFY"),
        ("Core: largest noise cutoff at $256^3$ for second-order constraints", f"${g['core.kmax256']:.0f}\\,\\Delta k$",
         "C", "TO VERIFY"),
    ]
    # two tables: one float of all rows exceeds a page (run E-20261121-080526-7fbe919)
    k = next(i for i, r in enumerate(rows) if r[0].startswith("A7"))
    head = ["\\begin{ruledtabular}", "\\footnotesize",
            "\\begin{tabular}{p{0.56\\textwidth}p{0.27\\textwidth}p{0.08\\textwidth}}",
            "Quantity & Value & Run \\\\", "\\hline"]
    L = ["\\begin{table*}",
         "\\caption{\\label{tab:ledgerG1}Numerical ledger of the slow-roll reproduction, criteria A1 to A6: "
         "each number with the registered run that produced it (runs listed in Table~\\ref{tab:ledgerG1b}, "
         "R1 in Table~\\ref{tab:ledger}).}"] + head
    for a, b, c, _ in rows[:k]:
        L.append(f"{a} & {b} & {c} \\\\")
    L += ["\\end{tabular}", "\\end{ruledtabular}", "\\end{table*}", "",
          "\\begin{table*}",
          "\\caption{\\label{tab:ledgerG1b}Numerical ledger of the slow-roll reproduction, continued: "
          "reproducibility, analysis, cost, the verifier and the code project; the registered runs of both parts.}"] + head
    for a, b, c, _ in rows[k:]:
        L.append(f"{a} & {b} & {c} \\\\")
    L += ["\\hline", "\\multicolumn{3}{l}{Registered runs:} \\\\"]
    for key, r in G1.items():
        L.append(f"\\multicolumn{{3}}{{l}}{{{lab[key]}\\quad\\texttt{{{r}}}\\quad {G1_WHAT[key]}}} \\\\")
    L.append(f"\\multicolumn{{3}}{{p{{0.93\\textwidth}}}}{{V\\quad the verifier's runs \\texttt{{{VER_RUNS}}}, "
             f"its report and the stage status of the gate}} \\\\")
    L.append(f"\\multicolumn{{3}}{{l}}{{L\\quad the lead's check \\texttt{{{LR1_RUN}}}}} \\\\")
    L.append(f"\\multicolumn{{3}}{{p{{0.93\\textwidth}}}}{{C\\quad core's runs \\texttt{{{CORE_RUNS}}}, "
             f"its interface text of {CORE_DOC[0]}}} \\\\")
    L += ["\\end{tabular}", "\\end{ruledtabular}", "\\end{table*}"]
    open(os.path.join(out, "ledger_g1.tex"), "w").write("\n".join(L) + "\n")
    # the same rows with their evidence labels and full locators (labels stay out of the
    # typeset note, ../WRITING_GUIDE.md exception 2)
    md = ["# Ledger of the G1 sections of the note (slow-roll reproduction)", "",
          "Written by `note/scripts/ledger.py`. Every number of the G1 sections with its value, "
          "its source and its evidence label. Run labels: R9-R18 below, R1 of the G0 ledger "
          f"(`{SPEC_RUN}`); V = the verifier's report; C = core's statement in its interface "
          "text (released with core-v0.5, not yet checked by the track).", "",
          "| Quantity | Value | Source | Label |", "|---|---|---|---|"]
    loc = {f"R{n}": r for n, r in enumerate(G1.values(), 9)}
    loc["R1"] = SPEC_RUN
    for a, b, c, labl in rows:
        src = ", ".join(loc.get(x.strip(), x.strip()) for x in c.split(","))
        if c == "C":
            src = f"{CORE_DOC[0]}, `{CORE_DOC[1]}` lines 143-164; runs {CORE_RUNS}"
        if c == "V":
            src = f"`{VER_DOC}` lines 303, 332, 374 and `stage/G1/STATUS.md` line 30; runs {VER_RUNS}"
        if c == "L":
            src = f"`stage/REVIEW-wave3.md` line 111; run {LR1_RUN}"
        md.append(f"| {a} | {b} | {src} | [{labl}] |")
    md += ["", "Runs:", ""] + [f"- R{n} `{r}`: {G1_WHAT[k]}" for n, (k, r) in enumerate(G1.items(), 9)]
    dc = g["core.doc_check"]
    md += ["", "Core's numbers found on their lines: " +
           ("not checked (document missing)" if dc is None else
            ", ".join(f"{k} {'yes' if ok else 'NO'}" for k, ok in dc.items()))]
    md += ["", "Reproducibility numbers found on their lines: " +
           ", ".join(f"{k} {'missing' if ok is None else ('yes' if ok else 'NO')}"
                     for k, ok in g["rep.doc_check"].items())]
    dv = g["ver.doc_check"]
    md += ["", "The verifier's numbers found on their lines: " +
           ("not checked (document missing)" if dv is None else
            ", ".join(f"{k} {'yes' if ok else 'NO'}" for k, ok in dv.items()))]
    open(os.path.join(out, "ledger_g1.md"), "w").write("\n".join(md) + "\n")
    return rows


def main():
    out = C.out_dir(C.TABDIR)
    os.makedirs(out, exist_ok=True)
    v = gather()
    res = check(v)
    g = gather_g1()
    bad = [k for d in (g["core.doc_check"] or {}, g["ver.doc_check"] or {}, g["rep.doc_check"])
           for k, ok in d.items() if ok is False]
    if bad:
        raise SystemExit(f"ledger: numbers not found on their document lines: {bad}")
    res_g1 = []
    for cid, doc, needle, printed, val, what in claims_g1(g):
        line = locate(doc, needle)
        ok = abs(float(val) - float(printed)) <= half_unit(printed) * (1 + 1e-9)
        res_g1.append(dict(id=cid, doc=doc, line=line, printed=printed, computed=float(val),
                           agree=bool(ok), what=what))
    missing = [r["id"] for r in res_g1 if r["line"] is None]
    if missing:
        raise SystemExit(f"ledger: claims not found in their documents: {missing}")
    res = res + res_g1
    write_ledger(v, res, out)
    write_ledger_g1(g, out)
    write_parameters(v, out)
    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(dict(claims=res, inputs=[dict(run=r, file=p, sha256=h, checksum=how)
                                           for r, p, h, how in C.checked()]), f, indent=1)
    nd = sum(not r["agree"] for r in res)
    md = ["# Numbers of the lead's documents checked against the run outputs",
          "",
          f"Written by `note/scripts/ledger.py`. {len(res)} numbers, {len(res) - nd} agree within half a "
          f"unit of the last printed digit, {nd} differ. Where they differ, the files win. "
          "c01-c59: G0 documents (SPEC.md, SCOPE.md, G0 EVIDENCE.md, langevin README); g01 on: "
          "G1 documents (stage/G1/STATUS.md, ladder/README.md). An integer with trailing zeros "
          "counts as rounded to its last nonzero digit.",
          "",
          "| Id | Document:line | Printed | Recomputed | Agree | What |", "|---|---|---|---|---|---|"]
    for r in res:
        md.append(f"| {r['id']} | `{r['doc']}:{r['line']}` | {r['printed']} | {fmt(r['computed'], 6)} | "
                  f"{'yes' if r['agree'] else '**no**'} | {r['what']} |")
    md += ["", "Inputs (sha256 checked against the run manifests where recorded):", ""]
    for r, p, h, how in C.checked():
        md.append(f"- `{r}/{p}` {h[:16]}... ({how})")
    open(os.path.join(out, "claims.md"), "w").write("\n".join(md) + "\n")
    print(f"claims: {len(res)} checked, {nd} differ")
    for r in res:
        if not r["agree"]:
            print("  differs:", r["id"], r["doc"], r["line"], r["printed"], fmt(r["computed"], 6), r["what"])


if __name__ == "__main__":
    main()
