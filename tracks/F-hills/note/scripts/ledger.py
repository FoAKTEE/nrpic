"""Ledger, parameter table and claims check of the note (F-hills, working note v0).

Reads only registered run outputs (common.RUNS, each file checked against its recorded
sha256) and the two passage inputs that run N1 recorded. Writes into DIR (--out, default
../tables):
  ledger.tex      the numerical ledger of the appendix: every number of the note with the run
                  id that produced it, or the locator of a printed value of the literature;
  parameters.tex  the parameter table of the appendix (passages and reference scans);
  claims.md, claims.json
                  numbers of the lead's documents (STATUS.md, stage/G0/SCOPING.md,
                  EVIDENCE.md, stage/G1/STATUS.md) checked against the files.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def g(x, n=4):
    return f"{x:.{n}g}"


def gD(x):
    """A penetration factor for the ledger: powers of ten below 1e-3 as 10^n."""
    if 0 < x < 1e-3:
        n = int(round(np.log10(x)))
        if abs(x / 10.0 ** n - 1) < 1e-9:
            return f"10^{{{n}}}"
    return g(x)


def tex(s):
    return s.replace("_", r"\_").replace("%", r"\%")


def read_problem(rel):
    blocks, cur = {}, None
    for line in open(os.path.join(C.TRACK, rel)):
        s = line.split("#")[0].strip()
        if not s:
            continue
        if s.startswith("<"):
            cur = s.strip("<>")
            blocks[cur] = {}
            continue
        if "=" in s and cur:
            k, v = [t.strip() for t in s.split("=", 1)]
            blocks[cur][k] = v
    return blocks


def main():
    out = C.out_dir("tables")
    scale = C.load_json("scale", "results.json")
    cop = C.load_json("coplanar_an", "summary_coplanar.json")
    skrc = C.load_json("skr", "summary_skr_curves.json")
    s1 = C.load_json("s1_an", "s1_summary.json")
    v5v6 = C.load_json("v5v6", "v5v6_summary.json")
    v5b = C.load_json("v5b", "v5b_summary.json")
    v7 = C.load_json("v7", "v7_summary.json")
    v4b = C.load_json("v4b", "v4b_summary.json") if "v4b" in C.RUNS else None
    m10 = C.load_json("mesh10", "mesh_count_b.json")
    m4 = C.load_json("mesh4", "mesh_count_b.json")
    e6 = C.load_json("e6", "baselines_p1.json")
    e4 = C.load_json("e4", "test_nrread_synthetic.json")
    n1 = C.load_json("n1", "passage_summary.json")
    v4 = C.load_json("v4", "v4_summary.json")
    e1 = {}
    for line in open(C.run_file("e1", "counts.txt")):
        parts = dict(p.split("=") for p in line.split()[1:] if "=" in p)
        e1[int(parts["num_levels"])] = int(parts["t0_tree"])
    R = C.RUNS
    rows = []          # (group, quantity, value, source)

    def add(group, q, v, src):
        rows.append((group, q, v, src))

    # ---- scales
    cf = scale["closed_form_check"]["ab_min_computed"]
    add("Scales", r"plunge bound $4q^{2/3}$ on $a_b/r_{gb}$, $q=10,100,1000$",
        ", ".join(g(cf[k], 4) for k in ("q10", "q100", "q1000")), R["scale"])
    add("Scales", r"marginally bound radius and angular momentum (parabolic)",
        f"{g(scale['schwarzschild_mb']['r_mb'])} $M$, {g(scale['schwarzschild_mb']['L_mb'])} $M$",
        R["scale"])
    add("Scales", r"Peters time at $a_b=30\,r_{gb}$, $q=10$",
        f"{g(scale['peters']['closed_ab30_q10'], 4)} $M$", R["scale"])
    # ---- restricted Newtonian
    for tag, lab in (("pro", "prograde"), ("ret", "retrograde")):
        c = cop[tag]
        add("Restricted Newton", f"last disrupting $D$, {lab}", g(c["Dmax_last_disrupting"]),
            R["coplanar_an"])
        add("Restricted Newton", f"deep-limit disruption probability, {lab}",
            g(c["P_at_Dmin"], 3), R["coplanar_an"])
        add("Restricted Newton", f"largest ejection energy, {lab}", g(c["Emax"], 4) +
            f" at $D={gD(c['D_at_Emax'])}$", R["coplanar_an"])
        add("Restricted Newton", f"failed integrations, {lab}",
            f"{c['n_fail']} of {c['n_total']}", R["coplanar_an"])
    add("Restricted Newton", "largest disruption probability (prograde)",
        f"{g(cop['pro']['P_max'], 3)} at $D={g(cop['pro']['D_at_P_max'])}$", R["coplanar_an"])
    add("Restricted Newton", "printed: last disrupting $D$; largest energy; deep limit; best $D$",
        "2.1/0.44; 27.3/1.8; about 0.8; 0.15",
        "arXiv:0911.1136 prp.tex:735-738, 846-849, 854")
    add("Restricted Newton", "against the digitised curve: median, largest $|\\Delta P|$, prograde",
        f"{g(skrc['P_pro']['median_abs_diff'], 2)}, {g(skrc['P_pro']['max_abs_diff'], 2)} at "
        f"$D={g(skrc['P_pro']['D_of_max'], 3)}$", R["skr"])
    h1 = C.load_json("h1", "summary_bkrs_h1.json")["H1"]["X=3.5"]["ret"]
    add("Restricted Newton", "retrograde, bound binaries wider than $3.5\\,a_b$ counted as disrupted: "
        "largest $|\\Delta P|$ against the digitised curve, last disrupting $D$",
        f"{g(h1['max_abs_diff'], 2)}, {g(h1['last_D_disrupting'], 3)}", R["h1"])
    add("Restricted Newton", "against the digitised curve: largest $|\\Delta P|$, retrograde",
        f"{g(skrc['P_ret']['max_abs_diff'], 2)} at $D={g(skrc['P_ret']['D_of_max'], 3)}$",
        R["skr"])
    gen = C.load_json("general_an", "summary_general.json")
    Dg = np.array(gen["D"])
    sel = Dg <= 1.0 + 1e-12
    frac = np.abs(np.array(gen["P_minus_fit"]) / np.array(gen["P_fit_BKRS"]))[sel]
    add("Restricted Newton", "isotropic orientations, $D\\le1$: largest fractional deviation from the "
        "published fit, probability and mean energy",
        f"{g(frac.max(), 2)}, {g(gen['max_abs_Emean_rel_dev_D<=1'], 2)} "
        f"({gen['N_ori']} orientations $\\times$ {gen['N_pha']} phases)", R["general_an"])
    add("Restricted Newton", "printed: plateau of the isotropic probability; accuracy of the fits for $D\\lesssim1$",
        "about 0.88; one percent", "arXiv:1804.02911 mnras.tex:368, 377, 440")
    dP = [abs(r["P_dis"] - r["P_dis_ref"]) for r in v4["rows"]]
    dE = [abs(r["Emean_dis"] / r["Emean_dis_ref"] - 1) for r in v4["rows"]]
    add("Restricted Newton", "independent code, nine points: largest $|\\Delta P|$, $|\\Delta E|/E$",
        f"{g(max(dP), 2)}, {g(max(dE), 2)} (retrograde $D=0.38$)", R["v4"])
    if v4b:
        dPb = [abs(r["P_dis"] - r["P_dis_ref"]) for r in v4b["rows"]]
        dEb = [abs(r["Emean_dis"] / r["Emean_dis_ref"] - 1) for r in v4b["rows"]]
        add("Restricted Newton", "the same at retrograde $D=0.3, 0.38$, wide binaries followed on",
            f"{g(max(dPb), 2)}, {g(max(dEb), 2)}", R["v4b"])
    # ---- geodesic baseline
    ch = s1["checks"]
    add("Geodesic baseline", "encounters of the scan", str(ch["runs_total"]), R["s1_an"])
    add("Geodesic baseline", r"retrograde onset of separation in $\beta$ (geodesic, Newton)",
        f"{g(ch['P1_retro_onset_hrna'], 2)}, {g(ch['P1_retro_onset_newton'], 2)}", R["s1_an"])
    for b in (3, 10):
        sf = ch[f"sf_beta{b}"]
        add("Geodesic baseline", rf"separated fraction at $\beta={b}$ (N pro, N retro, G pro, G retro)",
            ", ".join(g(sf[k], 3) for k in ("pro_newton", "retro_newton", "pro_hrna", "retro_hrna")),
            R["s1_an"])
    add("Geodesic baseline", "against the figure of arXiv:2404.16270: largest $|\\Delta|$ of the fraction",
        g(max(ch[k] for k in ch if k.startswith("digitized_sf_max_abs_dev")), 3), R["s1_an"])
    add("Geodesic baseline", "the same, mean $v_\\infty$ (relative)",
        g(max(ch[k] for k in ch if k.startswith("digitized_vmean_max_rel_dev") and
              not k.endswith("onset")), 2), R["s1_an"])
    add("Geodesic baseline", r"largest $a_b/R_{\rm curv}$ of a bound binary at $\beta=10$",
        g(max(ch["alpha_bound_max_beta10"].values()), 2), R["s1_an"])
    fb = C.load_json("flat", "flat_binary.json")["summary"]
    add("Geodesic baseline", "binary moving through flat space ($q=10$ members, $a_b=%g$, speed %g): "
        "sideways acceleration in the model; Newtonian law" % (fb["a0"], fb["V"]),
        f"{abs(fb['hrna']['a_fit']):.4g}; {abs(fb['newton']['a_fit']):g}", R["flat"])
    # ---- pericentre scan
    for key, lab in (("q10", "q=10"), ("q4", "q=4")):
        rr = v7[key]
        r0, r1 = rr[0], rr[-1]
        add("Pericentre scan", f"${lab}$, $r_p={g(r0['rp'])}$: Newton sep., inside $4M$; geodesic sep., plunge",
            f"{g(r0['newton_full']['separated'], 2)}, {g(r0['newton_full']['member_below_4M'], 2)}; "
            f"{g(r0['hrna']['separated'], 2)}, {g(r0['hrna']['plunge'], 2)}", R["v7"])
        r8 = [r for r in rr if abs(r["rp"] - (8.0 if key == "q10" else 9.82)) < 1e-6][0]
        if r8 is not r0:
            add("Pericentre scan", f"${lab}$, $r_p={g(r8['rp'])}$: the same",
                f"{g(r8['newton_full']['separated'], 2)}, {g(r8['newton_full']['member_below_4M'], 2)}; "
                f"{g(r8['hrna']['separated'], 2)}, {g(r8['hrna']['plunge'], 2)}", R["v7"])
        add("Pericentre scan", f"${lab}$, $r_p={g(r1['rp'])}$: the same",
            f"{g(r1['newton_full']['separated'], 2)}, {g(r1['newton_full']['member_below_4M'], 2)}; "
            f"{g(r1['hrna']['separated'], 2)}, {g(r1['hrna']['plunge'], 2)}", R["v7"])
    # ---- first passages
    for key, lab in (("q4", "q=4"), ("q10", "q=10")):
        s = n1[key]
        nw, hr, nf = s["newton"], s["hrna"], s["newton_fixed"]
        add("First passages", f"${lab}$: energy unit $(m_1m_2/a_b)q^{{1/3}}$", f"{g(s['unit_E'], 4)} $M$",
            R["n1"])
        add("First passages", f"${lab}$, Newton: ejected member, energy (barycentric), its spread after $t=300M$",
            f"$m_{nw['ejected']}$, {g(nw['E_ej_bc_u'], 5)}, {g(nw['E_ej_bc_range_late_u'], 2)}", R["n1"])
        add("First passages", f"${lab}$, Newton: two-body energy of the same member with $M$, range",
            f"{g(nw['E_ej_M_late_min_u'], 4)} to {g(nw['E_ej_M_late_max_u'], 4)}", R["n1"])
        add("First passages", f"${lab}$, Newton: captured member, energy, closest approach",
            f"$m_{nw['captured']}$, {g(nw['E_cap_M_u'], 4)}, {g(nw['rmin_cap'], 4)} $M$", R["n1"])
        ej = 2 if hr["E2_u"] > hr["E1_u"] else 1
        add("First passages", f"${lab}$, geodesic: ejected member and energy; other member",
            f"$m_{ej}$, {g(max(hr['E1_u'], hr['E2_u']), 4)}; " +
            ("plunges at $t=" + g(hr["first_pericentre_1"][0], 3) + "M$" if hr["plunged"] else
             f"bound, {g(min(hr['E1_u'], hr['E2_u']), 4)}, first pericentre "
             f"{g(hr['first_pericentre_1'][1], 4)} $M$"), R["n1"])
        add("First passages", f"${lab}$, Newton with $M$ fixed: ejected energy, closest approach of the other",
            f"{g(max(nf['E1_u'], nf['E2_u']), 4)}, {g(min(nf['rmin_1'], nf['rmin_2']), 4)} $M$", R["n1"])
    add("First passages", "$q=4$: reproduces the earlier run in every printed digit (ejected energy)",
        f"{g(e6['newton']['E_ejected_bc_u'], 6)}", R["e6"])
    add("First passages", "$q=4$, Newton: displacement of the heavy black hole by the end of the run",
        f"{g(e6['newton']['at_t_run']['hole_displacement'], 3)} $M$ at $t={g(e6['t_run'])}M$", R["e6"])
    add("First passages", "readers on a synthetic three-body run: checks passed",
        f"{sum(r['ok'] for r in e4['results'])} of {len(e4['results'])}", R["e4"])
    add("First passages", "$q=10$: captured orbit of Newton ($a$, $e$, pericentre)",
        f"{g(v5v6['q10']['newton_full']['captured']['a'], 3)}, {g(v5v6['q10']['newton_full']['captured']['e'], 3)}, "
        f"{g(v5v6['q10']['newton_full']['captured']['rp'], 3)} $M$", R["v5v6"])
    # ---- mesh and cost
    for src, run, case, lab in ((m10, "mesh10", "D205_m8_r1.8", "$q=10$, $m/8$"),
                                (m10, "mesh10", "D205_m16_r1.8", "$q=10$, $m/16$"),
                                (m10, "mesh10", "D205_m16_r1.2", "$q=10$, $m/16$, small radius"),
                                (m4, "mesh4", "D256q4_m8_r1.8", "$q=4$, $m/8$"),
                                (m4, "mesh4", "D256q4_m16_r1.8", "$q=4$, $m/16$"),
                                (m4, "mesh4", "D256q4_m16_r1.2", "$q=4$, $m/16$, small radius")):
        t = src["tracks"][case]
        ch_ = t["card_hours"]
        add("Mesh and cost", f"{lab}: MeshBlocks start, largest, mean; card-hours ({g(t['span'], 3)} $M$)",
            f"{int(t['n'][0])}, {t['n_max']}, {g(t['n_mean'], 4)}; {g(ch_['median'], 3)} "
            f"({g(ch_['fast'], 3)}-{g(ch_['slow'], 3)})", C.RUNS[run])
    add("Mesh and cost", "rate, MeshBlock-cycles per second (median, slow, fast)",
        f"{g(m10['rate_MB_cycles_per_s']['median'])}, {g(m10['rate_MB_cycles_per_s']['slow'])}, "
        f"{g(m10['rate_MB_cycles_per_s']['fast'])}", R["mesh10"])
    add("Mesh and cost", "$q=4$ input at the start, release executable: $m/4$, $m/8$, $m/16$",
        f"{e1[9]}, {e1[10]}, {e1[11]}", R["e1"])
    add("Mesh and cost", "card memory, MeshBlock slots", "about 3000",
        "multi\\_puncture.md lines 229--230 of coord/INTERFACES")

    # ---- full relativity (note v1, gate G1)
    import fig_smoke as FS  # log and input readers of the smoke figure
    e2 = C.load_json("e2", "c0_constraints.json")
    gF = "Data at the start"
    for case, lab in (("approx", "corrected"), ("none", "uncorrected")):
        add(gF, f"$\\langle H^2\\rangle^{{1/2}}$ at $t=0$, {lab} data, code: $m/4$, $m/8$, $m/16$",
            ", ".join(f"{e2[f'{case}_L{lv}']['all']['code']:.3g}" for lv in (9, 10, 11)), R["e2"])
    add(gF, "closed-form residual of the data: corrected, uncorrected, plain sum ($m/8$)",
        f"{e2['approx_L10']['all']['closed']:.3g}, {e2['none_L10']['all']['closed']:.3g}, "
        f"{e2['plain_L10']['all']['closed']:.3g}", R["e2"])
    add(gF, "uncorrected over corrected: closed form; code at $m/8$; code at $m/16$",
        f"{e2['none_L11']['all']['closed'] / e2['approx_L11']['all']['closed']:.3g}; "
        f"{e2['none_L10']['all']['code'] / e2['approx_L10']['all']['code']:.3g}; "
        f"{e2['none_L11']['all']['code'] / e2['approx_L11']['all']['code']:.3g}", R["e2"])
    add(gF, "order of the truncation error, $m/4\\to m/8\\to m/16$: corrected; uncorrected",
        f"{e2['order_approx'][0]:.3g}, {e2['order_approx'][1]:.3g}; "
        f"{e2['order_none'][0]:.3g}, {e2['order_none'][1]:.3g}", R["e2"])
    rg = e2["approx_L10"]
    add(gF, "corrected data at $m/8$, code: members ($r<1M$), heavy black hole ($r<4M$), elsewhere",
        f"{rg['members (r < 1 M)']['code']:.3g}, {rg['heavy (r < 4 M)']['code']:.3g}, "
        f"{rg['rest']['code']:.3g}", R["e2"])
    e7an = C.load_json("e7an", "p1_analysis.json")
    add(gF, "the same norm at $t=0$ from the card executable (passage input, $m/8$)",
        f"{e7an['H_t0']:.4g}", R["e7an"])
    # single member
    e3 = C.load_json("e3", "single_analysis.json")
    e10 = C.load_json("e10a", "s2g_compare.json")
    gS = "Single member"
    bl = open(C.run_file("e3raw", "batch.list")).read().split("\n")
    sp = FS.read_problem(C.run_file("e3raw", "S3/single_P025.athinput"))
    blk = {}
    cur = None
    for line in open(C.run_file("e3raw", "S3/single_P025.athinput")):
        t_ = line.split("#")[0].strip()
        if t_.startswith("<"):
            cur = t_.strip("<>")
        elif "=" in t_ and cur:
            k_, v_ = [x.strip() for x in t_.split("=", 1)]
            blk.setdefault(cur, {})[k_] = v_
    eta2 = [x.split("=")[1] for ln in bl if "/S2 " in ln for x in ln.split() if x.startswith("z4c/shift_eta=")]
    add(gS, "set-up: bare mass $m$, momentum $P$; shift damping $\\eta$ of the two runs; slots of the input",
        f"{sp['comp0_mass']}, {sp['comp0_p1']}; {blk['z4c']['shift_eta']}, {eta2[0]}; "
        f"{blk['mesh_refinement']['max_nmb_per_rank']}", R["e3raw"])
    add(gS, "$P/M_{\\rm ADM}$; rest mass of the full solution, $\\sqrt{M_{\\rm ADM}^2-P^2}$ [$m$]",
        f"{e3['reference']['v_boost']:.4g}; {e3['reference']['M_rest_full']:.5g}", R["e3"])
    add(gS, "tracker speed over $P/M_{\\rm ADM}$, mean over $t=10$--$20\\,m$: $\\eta m=2$, $\\eta m=0.25$",
        f"{e3['S3']['f_mean']['10-20']:.3g}, {e3['S2']['f_mean']['10-20']:.3g}", R["e3"])
    add(gS, "largest speed ratio and its time, $\\eta m=0.25$; settling time $\\eta m=0.25$, $\\eta m=2$",
        f"{e3['S2']['f_max']:.3g} at {e3['S2']['t_f_max']:.3g}$\\,m$; "
        f"{e10['runs']['S2']['t_settle']:.3g}, {e10['runs']['S3']['t_settle']:.3g}$\\,m$", R["e3"] + ", " + R["e10a"])
    add(gS, "horizon mass at $t=0$ [$m$] and its offset from the rest mass",
        f"{e3['S3']['horizon']['m_first']:.5g}, "
        f"{e3['S3']['horizon']['m_first'] / e3['reference']['M_rest_full'] - 1:.2g}", R["e3"])
    add(gS, "first search with residual below $10^{-3}$: time [$m$] and mass, $\\eta m=2$; $\\eta m=0.25$",
        f"{e10['runs']['S3']['first_good'][0]:g}, {e10['runs']['S3']['first_good'][1]:.5g}; "
        f"{e10['runs']['S2']['first_good'][0]:g}, {e10['runs']['S2']['first_good'][1]:.5g}", R["e10a"])
    d3 = e10["S2_vs_S3"]["drift_4_6_to_12_14"]
    add(gS, "horizon drift, median of $t=4$--$6\\,m$ to median of $12$--$14\\,m$: $\\eta m=2$, $\\eta m=0.25$, ratio",
        f"{d3['S3']:.3g}, {d3['S2']:.3g}, {d3['S2'] / d3['S3']:.3g}", R["e10a"])
    add(gS, "searches found and missed: $\\eta m=2$; $\\eta m=0.25$",
        f"{e3['S3']['horizon']['found']}/{e3['S3']['horizon']['missed']}; "
        f"{e3['S2']['horizon']['found']}/{e3['S2']['horizon']['missed']}", R["e3"])
    add(gS, "$\\langle H^2\\rangle^{1/2}$, $\\eta m=2$: peak and its time; at $t=10$, $20\\,m$",
        f"{e3['S3']['constraints']['H_max']:.2g} at {e3['S3']['constraints']['t_H_max']:g}$\\,m$; "
        f"{e3['S3']['constraints']['H_at']['10']:.2g}, {e3['S3']['constraints']['H_at']['20']:.2g}", R["e3"])
    add(gS, "end of the runs [$m$] and tracker position there: $\\eta m=2$; $\\eta m=0.25$",
        f"{e3['S3']['t_end']:.4g}, {e3['S3']['x_end']:.4g}; {e3['S2']['t_end']:.4g}, {e3['S2']['x_end']:.4g}",
        R["e3"])
    # mesh tree
    tc = C.load_json("e11", "tree_check.json")
    tp = C.load_json("e11path", "tree_path.json")
    gT = "Mesh tree"
    rs = tc["runs"]["S3"]
    add(gT, "restart trees equal to the rule model, $t=0$, $10$, $20\\,m$ (MeshBlocks)",
        ", ".join(str(r["nmb"]) for r in rs) + " (all levels equal)", R["e11"])
    add(gT, "levels 1, 2, 3 of the tree at $t=10\\,m$",
        " / ".join(str(rs[1]["counts"][k]) for k in ("1", "2", "3")), R["e11"])
    npth = [r["total"] for r in tp["rows"]]
    xs_over = [r["x"] for r in tp["rows"] if r["total"] > 1600]
    add(gT, "rule model along $x=0$--$20\\,m$: tree sizes; first $x$ above the 1600 slots",
        ", ".join(str(v) for v in sorted(set(npth))) + f"; {min(xs_over):g}$\\,m$", R["e11path"])
    # first passage
    gP = "First passage in full relativity"
    rdir7 = os.path.join(C.SCRATCH, C.RUNS["e7"], "P1smoke")
    lg = FS.read_log(C.run_file("e7", FS.LOG))
    mem = np.genfromtxt(C.run_file("e7", FS.MEM), delimiter=",", skip_header=1, usecols=(1,))
    rate = lg["mb_cycles"] / lg["cpu_s"]
    add(gP, "MeshBlocks at the start and at cycle 400 (created, removed)",
        f"{int(lg['nmb_start'])}, {int(lg['nmb_end'])} ({int(lg['created'])}, {int(lg['deleted'])})", R["e7"])
    add(gP, "MeshBlock-cycles per second (MeshBlock-cycles over timed seconds)",
        f"{rate:.4g} ({int(lg['mb_cycles'])}/{lg['cpu_s']:.4g})", R["e7"])
    add(gP, "peak card memory with 2700 MeshBlock slots [MiB]", f"{mem.max():.0f}", R["e7"])
    add(gP, "card memory [MiB] (and per slot)", "81920 (26.2)",
        "tracks/F-hills/nr_first/JOURNAL.md lines 626--627")
    prob = FS.read_problem(C.run_file("e7", FS.INP))
    nr = C.nrread()
    trk = nr.read_trackers(rdir7)
    offs = [float(np.linalg.norm(trk[n]["x"][0] - np.array([float(prob[f"comp{n}_x{i}"]) for i in (1, 2, 3)])))
            for n in range(3)]
    add(gP, "largest offset of a tracker from its input position at $t=0$", f"{max(offs):.2g}", R["e7"])
    fr = []
    for n in range(2):
        pv = np.array([float(prob[f"comp{n}_p{i}"]) for i in (1, 2, 3)])
        fr.append(float(np.linalg.norm(trk[n]["v"][-1]) / (np.linalg.norm(pv) / float(prob[f"comp{n}_mass"]))))
    add(gP, "member tracker speed over $|P|/m$ at $t=1.56M$: $m_1$, $m_2$", f"{fr[0]:.2g}, {fr[1]:.2g}", R["e7"])
    hm = e7an["horizon_median"]
    add(gP, "horizon masses, median of the found searches: $m_1$, $m_2$, $M$",
        f"{hm['0']:.5g}, {hm['1']:.5g}, {hm['2']:.5g}", R["e7an"])
    hz7 = nr.read_horizons(rdir7)
    fg = []
    for n in range(3):
        h_, _ = hz7[n]
        good_ = h_["hrms"] < 1e-3
        fg.append(f"{h_['t'][good_][0]:g}" if good_.any() else f"none of {len(h_['t'])}")
    add(gP, "first search with residual below $10^{-3}$ [$M$]: $m_1$, $m_2$, $M$", ", ".join(fg), R["e7"])
    add(gP, "searches missed of 25: $m_1$, $m_2$, $M$",
        ", ".join(str(e7an["horizon_missed"][k]) for k in ("0", "1", "2")), R["e7an"])
    cyc = int(round(lg["tlim"] / lg["dt"]))
    nbig = int(m4["tracks"]["D256q4_m8_r1.8"]["n_max"])
    add(gP, "cycles of the passage ($t_{\\rm lim}/\\Delta t$); card-hours for a mean tree of "
        f"{int(lg['nmb_end'])} and {nbig} MeshBlocks",
        f"{cyc}; {cyc * lg['nmb_end'] / rate / 3600:.3g}, {cyc * nbig / rate / 3600:.3g}",
        R["e7"] + ", " + R["mesh4"])
    v9 = C.load_json("v9", "review_gr.json")
    vp = v9["tracks/F-hills/nr_first/inputs/p1_q4.athinput"]
    add(gP, "start state, Newtonian conic of the centre of mass: $r_p$, eccentricity",
        f"{vp['newton_conic']['r_p']:.4g}, {vp['newton_conic']['e']:.6g}", R["v9"])
    add(gP, "test-mass reading, heavy black hole's frame: $E$, $L$, turning point $r_S$",
        f"{vp['hole_frame_M']['E']:.5g}, {vp['hole_frame_M']['L']:.4g}, {vp['hole_frame_M']['turning_point_rS']:.3g}", R["v9"])
    add(gP, "the same with the heavy black hole at rest: $E$, $L$, turning point",
        f"{vp['hole_at_rest_M']['E']:.4g}, {vp['hole_at_rest_M']['L']:.4g}, {vp['hole_at_rest_M']['turning_point_rS']:.3g}", R["v9"])
    add(gP, "the same with the total mass: captured",
        "yes" if vp["hole_frame_M_plus_mb"]["captured"] else "no", R["v9"])
    vq = v9["tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput"]
    add(gP, "$q=10$ input: Newtonian $r_p$; turning point in the heavy black hole's frame; captured in the other two readings",
        f"{vq['newton_conic']['r_p']:.4g}; {vq['hole_frame_M']['turning_point_rS']:.3g}; "
        + ("yes" if vq["hole_at_rest_M"]["captured"] and vq["hole_frame_M_plus_mb"]["captured"] else "no"),
        R["v9"])
    ps = C.load_json("newton3_pass", "passages.json")["passage"]["q4"]
    add(gP, "Newton from the start state: captured member's orbit $a$, $e$, pericentre; first pericentre time",
        f"{ps['captured_orbit']['a']:.3g}, {ps['captured_orbit']['e']:.3g}, {ps['captured_orbit']['rp']:.3g}; "
        f"{ps['captured_pericentre_times'][0]:.4g}", R["newton3_pass"])
    add(gP, "prediction recorded before submission (health, outcome, horizons, radiation)",
        "four items", "tracks/F-hills/JOURNAL.md lines 305--320")

    # ---- write ledger.tex: two tables
    def table(groups, label, caption):
        lines = [r"\begin{table*}", r"\caption{" + caption + "}", r"\label{" + label + "}",
                 r"\footnotesize", r"\begin{ruledtabular}",
                 r"\begin{tabular}{p{0.44\textwidth}p{0.19\textwidth}p{0.29\textwidth}}",
                 r"Quantity & Value & Source \\ \hline"]
        cur = None
        for grp, q, v, src in rows:
            if grp not in groups:
                continue
            if grp != cur:
                lines.append(r"\multicolumn{3}{l}{\emph{" + grp + r"}} \\")
                cur = grp
            lines.append(f"{q} & {v} & \\texttt{{\\detokenize{{{src}}}}} \\\\"
                         if src.startswith(("F", "tracks/")) else f"{q} & {v} & {src} \\\\")
        lines += [r"\end{tabular}", r"\end{ruledtabular}", r"\end{table*}"]
        return "\n".join(lines)

    with open(os.path.join(out, "ledger.tex"), "w") as f:
        f.write("% generated from registered run outputs; do not edit\n")
        f.write(table({"Scales", "Restricted Newton", "Geodesic baseline"}, "tab:ledger1",
                      "Ledger of the reference solutions. Energies in units of "
                      r"$(Gm_1m_2/a_b)(M/m_b)^{1/3}$; sources are registered runs or the "
                      "file and line of a paper's text.") + "\n\n")
        f.write(table({"Pericentre scan", "First passages", "Mesh and cost"}, "tab:ledger2",
                      "Ledger of the pericentre scan, the first passages and the cost. "
                      "Fractions are over the sampled binary phases; card-hours are the "
                      "median rate with the fast and slow rates in parentheses.") + "\n\n")
        f.write(table({gF, gS, gT, gP}, "tab:ledger3",
                      "Ledger of the runs in full relativity: the three-black-hole data at the "
                      "start, a single member on a card, its mesh tree, and the first passage "
                      "(set-up, start state, cost). Lengths and times in units of the member "
                      "mass $m$ for the single member and of $M$ otherwise.") + "\n")

    # ---- parameters.tex
    par = []
    for key, lab in (("q4", "$q=4$"), ("q10", "$q=10$")):
        s = n1[key]
        b = read_problem(s["input"])
        par.append((lab, s, b))
    prow = [
        ("heavy black hole $M$, members $m_1=m_2$ (bare)", lambda s, b: f"{g(s['M'])}, {g(s['m1'])}"),
        ("binary semimajor axis $a_b$, eccentricity $e_b$ at the start",
         lambda s, b: f"{g(s['a_b'], 4)}, {g(s['e_b'], 2)}"),
        ("tidal radius $r_t$", lambda s, b: g(s["r_t"], 4)),
        ("pericentre $r_p$ and eccentricity of the centre-of-mass orbit",
         lambda s, b: f"{g(s['cm_rp'], 5)}, {g(s['cm_e'], 6)}"),
        ("start distance of the centre of mass", lambda s, b: g(s["r0"], 4)),
        ("domain half-width, refinement levels",
         lambda s, b: f"{g(float(b['mesh']['x1max']))}, {b['mesh_refinement']['num_levels']}"),
        ("puncture radius of refinement", lambda s, b: b["problem"]["puncture_radius"]),
        ("wave extraction radii",
         lambda s, b: ", ".join(b["z4c"][f"extraction_radius_{i}"].rstrip("0").rstrip(".")
                               for i in range(4))),
        ("shift damping $\\eta$ (one value for all black holes)", lambda s, b: b["z4c"]["shift_eta"]),
        ("end time of the run", lambda s, b: g(float(b["time"]["tlim"]))),
    ]
    lines = [r"\begin{table}", r"\caption{Parameters of the two first passages (units $G=c=M=1$). "
             r"Both are coplanar and prograde with nonspinning black holes and start from the "
             r"Newtonian state integrated in from ten tidal radii.}", r"\label{tab:parameters}",
             r"\footnotesize", r"\begin{ruledtabular}", r"\begin{tabular}{p{0.46\columnwidth}ll}",
             r"Parameter & " + par[0][0] + " & " + par[1][0] + r" \\ \hline"]
    for name, fn in prow:
        lines.append(f"{name} & {fn(par[0][1], par[0][2])} & {fn(par[1][1], par[1][2])} \\\\")
    lines += [r"\end{tabular}", r"\end{ruledtabular}", r"\end{table}"]
    with open(os.path.join(out, "parameters.tex"), "w") as f:
        f.write("% generated from the passage inputs; do not edit\n")
        f.write("\n".join(lines) + "\n")

    # ---- claims of the lead's documents against the files
    q10 = {r["rp"]: r for r in v7["q10"]}
    q4 = {r["rp"]: r for r in v7["q4"]}
    hr_pl = [q10[rp]["hrna"]["plunge"] for rp in (7.0, 8.0, 9.0, 10.0, 11.0, 12.0)]
    claims = []

    def claim(doc, text, file_value, verdict, note=""):
        claims.append(dict(doc=doc, claim=text, files=file_value, verdict=verdict, note=note))

    claim("STATUS.md headline", "for r_p = 7-12 M the geodesic model captures a member in 69-96 percent of phases, Newton in none",
          f"geodesic plunge fraction {min(hr_pl):.3f}-{max(hr_pl):.3f} ({R['v7']}); full Newton: a member inside 4 M in "
          f"{q10[7.0]['newton_full']['member_below_4M']:.2f} of the phases at r_p = 7, {q10[8.0]['newton_full']['member_below_4M']:.3f} at 8",
          "agrees, wording differs",
          "the files count a plunge (a member crosses r = 2.5 M); in Newton a point mass cannot swallow a member, but at r_p = 7 M a member passes inside 4 M in most phases")
    claim("SCOPING.md 4", "a member crosses r = 2.5 M in 94 percent of the phases at r_p = 8 M and in 69 percent at 12 M",
          f"{q10[8.0]['hrna']['plunge']:.4f}, {q10[12.0]['hrna']['plunge']:.4f} ({R['v7']})", "agrees")
    claim("SCOPING.md 4", "full Newton has no member inside 4 M in 94 percent of the phases at 8 M",
          f"{1 - q10[8.0]['newton_full']['member_below_4M']:.4f} ({R['v7']})", "agrees")
    claim("SCOPING.md 4", "at r_p = 13 M (D = 2.0) HRNA separates 98 percent, Newton 22 percent",
          f"D = {q10[13.0]['D']:.3f}; {q10[13.0]['hrna']['separated']:.4f}, {q10[13.0]['newton_full']['separated']:.4f} ({R['v7']})",
          "agrees")
    claim("JOURNAL.md V7", "q = 4: full Newton separates 0.84 to 0.54, HRNA 0.94-0.99 with plunges 0.94 to 0.67",
          f"{q4[9.82]['newton_full']['separated']:.3f} to {q4[16.0]['newton_full']['separated']:.3f}; "
          f"{min(r['hrna']['separated'] for r in v7['q4']):.3f}-{max(r['hrna']['separated'] for r in v7['q4']):.3f}; "
          f"{q4[9.82]['hrna']['plunge']:.3f} to {q4[16.0]['hrna']['plunge']:.3f} ({R['v7']})", "agrees")
    claim("SCOPING.md 4", "plunge bound 4 q^(2/3) = 18.57, 86.18, 400.0; Peters time 6328 GM/c^3",
          f"{cf['q10']:.4f}, {cf['q100']:.4f}, {cf['q1000']:.4f}; {scale['peters']['closed_ab30_q10']} ({R['scale']})",
          "agrees")
    nq = n1["q10"]
    claim("SCOPING.md 6, G1/STATUS.md", "q = 10 input: a_b = 3.036, e = 0.029; conic r_p = 7.9965, e = 1.00006; start 25.85 M",
          f"{nq['a_b']:.4f}, {nq['e_b']:.4f}; {nq['cm_rp']:.5f}, {nq['cm_e']:.6f}; {nq['r0']:.3f} ({R['n1']})", "agrees")
    cap = v5v6["q10"]["newton_full"]["captured"]
    claim("SCOPING.md 6, G1/STATUS.md P1-2", "full Newton: m1 ejected with +1.613 units = +2.90e-3 M; m2 bound, a = 7.55, e = 0.247, pericentre 5.68 M",
          f"{nq['newton']['E_ej_bc_u']:.5f} units = {nq['newton']['E_ej_bc_u'] * nq['unit_E']:.3e} M ({R['n1']}); "
          f"a = {cap['a']:.3f}, e = {cap['e']:.4f}, r_p = {cap['rp']:.3f} ({R['v5v6']})", "agrees")
    hq = nq["hrna"]
    claim("SCOPING.md 6, G1/STATUS.md P1-3", "HRNA: m1 reaches r = 2.5 M at t = 97 M; m2 ejected with +1.16 units (+0.69 in the 2404 construction)",
          f"t = {hq['first_pericentre_1'][0]:.2f}, r = {hq['rmin_1']:.3f}; {hq['E2_u']:.4f} ({R['n1']}); "
          f"{v5v6['q10']['v6b']['hrna']['E2_u']:.4f} ({R['v5v6']})", "agrees")
    nq4 = n1["q4"]
    claim("G1/STATUS.md fallback", "q = 4: full Newton m1 ejected +1.312 units; HRNA m1 bound, first pericentre 7.3 M, m2 ejected +0.97; 93 percent of phases plunge a member",
          f"{nq4['newton']['E_ej_bc_u']:.4f}; {nq4['hrna']['first_pericentre_1'][1]:.3f} M, {nq4['hrna']['E2_u']:.4f} ({R['n1']}); "
          f"{v5v6['q4']['scan']['hrna']['captured_by_hole']:.3f} ({R['v5v6']})", "agrees")
    claim("SCOPING.md 10, JOURNAL.md V5b", "two-body energy with M swings by +-0.19 units (q = 10) and +-0.37 (q = 4); conserved values +1.613 and +1.312",
          f"half-ranges {(nq['newton']['E_ej_M_late_max_u'] - nq['newton']['E_ej_M_late_min_u']) / 2:.3f}, "
          f"{(nq4['newton']['E_ej_M_late_max_u'] - nq4['newton']['E_ej_M_late_min_u']) / 2:.3f}; "
          f"{v5b['q10']['E_bary_end']:.4f}, {v5b['q4']['E_bary_end']:.4f} ({R['n1']}, {R['v5b']})", "agrees")
    allP = max(dP)
    allE = max(dE)
    ret12 = [r for r in v4["rows"] if r["sense"] == "ret" and r["D"] in (0.1, 0.2)]
    claim("G1/STATUS.md T1, EVIDENCE.md V4b, STATUS.md", "independent code agrees at nine (sense, D) points within 0.002 in P_dis and 0.4 percent in energy (V4b): all nine agree",
          "V4b reran only retrograde D = 0.3 and 0.38 (" + R["v4b"] + "): " +
          f"{max(dPb):.4f}, {max(dEb):.4f}; retrograde D = 0.1 and 0.2 come from V4 (" + R["v4"] + "): " +
          ", ".join(f"D = {r['D']}: |dP| = {abs(r['P_dis'] - r['P_dis_ref']):.4f}, |dE|/E = {abs(r['Emean_dis'] / r['Emean_dis_ref'] - 1):.4f}" for r in ret12),
          "differs",
          "at retrograde D = 0.2 the independent code differs by 0.006 in P_dis and 1.2 percent in energy; its 14 wide bound samples were not followed on as in V4b, so the agreement there is plausible but not shown")
    t10 = m10["tracks"]["D205_m8_r1.8"]
    t4 = m4["tracks"]["D256q4_m8_r1.8"]
    claim("SCOPING.md 9", "q = 10, m/8, 240 M: 1800 / 2332 / 2006 MeshBlocks, 38.9 (37.0-42.3) card-hours; q = 4, m/8, 270 M: 1716 / 2080 / 1744, 15.2 (14.5-16.5)",
          f"{int(t10['n'][0])} / {t10['n_max']} / {t10['n_mean']:.0f}, {t10['card_hours']['median']:.1f} "
          f"({t10['card_hours']['fast']:.1f}-{t10['card_hours']['slow']:.1f}) ({R['mesh10']}); "
          f"{int(t4['n'][0])} / {t4['n_max']} / {t4['n_mean']:.0f}, {t4['card_hours']['median']:.1f} "
          f"({t4['card_hours']['fast']:.1f}-{t4['card_hours']['slow']:.1f}) ({R['mesh4']})", "agrees")
    t16 = m4["tracks"]["D256q4_m16_r1.8"]
    t16s = m4["tracks"]["D256q4_m16_r1.2"]
    b4 = read_problem(n1["q4"]["input"])
    claim("SCOPING.md 9", "q = 4, m/16: 2416 / 2654 / 2348 MeshBlocks, 41 card-hours, memory marginal",
          f"puncture radius 1.2: {int(t16s['n'][0])} / {t16s['n_max']} / {t16s['n_mean']:.0f}, {t16s['card_hours']['median']:.1f}; "
          f"radius of the inputs ({b4['problem']['puncture_radius']}): {int(t16['n'][0])} / {t16['n_max']} / {t16['n_mean']:.0f}, "
          f"{t16['card_hours']['median']:.1f} ({R['mesh4']}); E1 at the start {e1[11]} ({R['e1']}); "
          f"max_nmb_per_rank of the input {b4['mesh_refinement']['max_nmb_per_rank']}",
          "differs (definition)",
          "the quoted numbers belong to the smaller puncture radius; with the radius of the inputs the tree reaches more MeshBlocks than the input's max_nmb_per_rank allows, so an m/16 run needs that limit raised and stays memory-marginal")
    claim("STATUS.md budget", "0 card-hours used of 40 (decision 0006)",
          "decision 0014 sets 50 card-hours to the next gate; nrpic-run records gpu_hours_allotted = 50 "
          f"({C.manifest('e6')['budget_at_submit']['gpu_hours_allotted']} in the manifest of {R['e6']})",
          "superseded", "the lead's text predates decision 0014")
    claim("HANDOFF.md, OPEN.md 6, G1/STATUS.md", "core/multi-puncture is not released; F has run none of its code",
          "CLAUDE.md lists several black holes with momentum and spin in release core-v0.3; wave-2 runs "
          f"use the release executables ({R['e1']})", "superseded", "state of wave 1")
    claim("G1/STATUS.md P1 command", "P1 to time/tlim=200 on the q = 10 input",
          f"the q = 10 input has tlim = {read_problem(n1['q10']['input'])['time']['tlim']} (the command overrides it); "
          f"the q = 4 P1 input has tlim = {b4['time']['tlim']}", "agrees (override)")
    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(claims, f, indent=1)
    md = ["# Numbers of the lead's documents checked against the files (note v0)", "",
          "Written by `scripts/ledger.py`; the files win. Verdicts: agrees, differs, superseded.", "",
          "| # | document | claim | files | verdict | note |", "|---|---|---|---|---|---|"]
    for i, c in enumerate(claims, 1):
        md.append(f"| {i} | {c['doc']} | {c['claim']} | {c['files']} | **{c['verdict']}** | {c['note']} |")
    n_ag = sum(c["verdict"].startswith("agrees") for c in claims)
    md += ["", f"{n_ag} of {len(claims)} agree; "
           f"{sum(c['verdict'].startswith('differs') for c in claims)} differ; "
           f"{sum(c['verdict'] == 'superseded' for c in claims)} superseded."]
    with open(os.path.join(out, "claims.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[-1:]))
    C.report_checks("ledger")


if __name__ == "__main__":
    main()
