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
    """Half a unit of the last printed digit of a number string such as 1.0805, 9.7e-13."""
    m = re.fullmatch(r"-?(\d+)(?:\.(\d+))?(?:e(-?\d+))?", txt)
    if not m:
        raise ValueError(txt)
    dec = len(m.group(2) or "")
    ex = int(m.group(3) or 0)
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
            ("core", costmodel.CORE, "measured card throughput of the code (core)")]
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
         f"${min(v[f'{q}.drift_ms']):.2e}$ to ${max(v[f'{q}.drift_ms']):.2e}$", rid["spec"]),
        ("Freezing, SR: drift per e-fold, deformed",
         f"${min(v[f'{q}.drift_def']):.4f}$ to ${max(v[f'{q}.drift_def']):.4f}$", rid["spec"]),
        ("Freezing, SR: deformed over full power at the end, $k=\\Delta k$ and $64\\,\\Delta k$",
         f"${v[f'{q}.ratio_def_full'][0]:.3f}$, ${v[f'{q}.ratio_def_full'][-1]:.3f}$", rid["spec"]),
        ("Freezing, USR: deformed over full power at the end, $k=\\Delta k$, $4\\,\\Delta k$",
         f"${v[f'{i}.ratio_def_full'][0]:.2f}$, ${v[f'{i}.ratio_def_full'][8]:.3f}$", rid["spec"]),
        ("Freezing, USR: full power at the end, $k=64\\,\\Delta k$", f"${v[f'{i}.Delta_full_Nf_last']:.4f}$", rid["spec"]),
        ("Freezing, independent check: SR slopes full, deformed; $-4\\epsilon_1$",
         f"${v['lead.sr_slope_full']:.1e}$, ${v['lead.sr_slope_def']:.4f}$; ${v['lead.sr_minus4eps1']:.4f}$", rid["lead"]),
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


def main():
    out = C.out_dir(C.TABDIR)
    os.makedirs(out, exist_ok=True)
    v = gather()
    res = check(v)
    write_ledger(v, res, out)
    write_parameters(v, out)
    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(dict(claims=res, inputs=[dict(run=r, file=p, sha256=h, checksum=how)
                                           for r, p, h, how in C.checked()]), f, indent=1)
    nd = sum(not r["agree"] for r in res)
    md = ["# Numbers of the lead's documents checked against the run outputs",
          "",
          f"Written by `note/scripts/ledger.py`. {len(res)} numbers, {len(res) - nd} agree within half a "
          f"unit of the last printed digit, {nd} differ. Where they differ, the files win.",
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
