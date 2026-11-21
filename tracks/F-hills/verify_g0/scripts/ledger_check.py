"""verify_g0 C18: every row of the note's ledger tables 1 and 2 recomputed.

Reads note/tables/ledger.tex (tab:ledger1, tab:ledger2), and for each row recomputes the value
from the raw arrays or logs of the run it names (sha256 checked against the run's record where
one exists), from my own runs (R1 closed forms, R3 passages, R4 scan, R5 restricted problem,
R7 2404 set-up), or from the paper source. My code here is independent of newton3/,
geodesic_binary/ and note/scripts/: the comparisons that use third-party digitised curves
(SKR fig. 4, BKRS fig. 2, 2404 fig. of the separation fraction) read the digitised points the
track's runs wrote to scratch, and say so.

Usage: python3 ledger_check.py --out DIR --mine R1=<run>,R3=<run>,R4=<run>,R5=<run>,R7=<run>
Writes DIR/ledger_check.json, DIR/ledger_check.md, DIR/fig_ledger_mesh.png, DIR/fig_ledger_passages.png.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

WT = "/data/haiyangw/nrpic/wt/F-hills"
TR = os.path.join(WT, "tracks/F-hills")
SCR = "/data/haiyangw/nrpic/scratch/F-hills"
KB = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
LEDGER = os.path.join(TR, "note/tables/ledger.tex")
CHECKED = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rf(run, rel):
    """Path of output rel of run, checked against the run's sha256sums.txt when it has one."""
    p = os.path.join(SCR, run, rel)
    s = os.path.join(SCR, run, "sha256sums.txt")
    st = "no sha256 record (wave-1 run)"
    if os.path.isfile(s):
        tab = {}
        for ln in open(s):
            parts = ln.split(None, 1)
            if len(parts) == 2:
                tab[parts[1].strip().lstrip("*").removeprefix("./")] = parts[0]
        if rel in tab:
            st = "sha256 ok" if tab[rel] == sha(p) else "SHA256 MISMATCH"
        else:
            st = "not listed in sha256sums.txt"
    CHECKED.append((run, rel, st))
    return p


def src_line(arx, ver, fn, lines):
    txt = open(os.path.join(KB, arx, ver, "src", fn), errors="replace").read().splitlines()
    return " ".join(txt[i - 1] for i in lines)


# ----------------------------------------------------------------------------- ledger parsing
def parse_ledger():
    tex = open(LEDGER).read()
    rows = []
    for lab in ("tab:ledger1", "tab:ledger2"):
        i = tex.index(r"\label{" + lab + "}")
        j = tex.index(r"\end{tabular}", i)
        body = tex[i:j]
        group = None
        for ln in body.splitlines():
            ln = ln.strip()
            m = re.match(r"\\multicolumn\{3\}\{l\}\{\\emph\{(.*)\}\} \\\\", ln)
            if m:
                group = m.group(1)
                continue
            if ln.endswith(r"\\") and "&" in ln and not ln.startswith("Quantity"):
                q, v, s = [x.strip() for x in ln[:-2].split("&")]
                s = re.sub(r"\\texttt\{\\detokenize\{(.*)\}\}", r"\1", s)
                rows.append(dict(table=lab, group=group, quantity=q, value=v, source=s))
    return rows


def nums(s):
    """Numbers of a ledger value string, in order (10^{-5} -> 1e-5)."""
    s = s.replace("10^{-5}", "1e-5").replace("$", "")
    s = re.sub(r"(?<=\d)-(?=\d)", " ", s)          # ranges "37-42.3"
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", s)]


def agree(ledger_vals, mine, rel=None, absd=None, digits=True):
    """Each ledger number equals mine when rounded the way the ledger prints it (digits=True),
    or within rel / absd."""
    out = []
    for lv, mv in zip(ledger_vals, mine):
        if mv is None:
            out.append(False)
            continue
        if digits:
            s = repr(lv)
            nd = len(s.split(".")[1]) if "." in s and "e" not in s else 0
            if float(lv).is_integer() and abs(lv) >= 1:
                nd = 0
            if "e" in s:
                ok = abs(mv - lv) <= 0.5 * 10 ** (int(np.floor(np.log10(abs(lv)))) - 1) + 1e-15
            else:
                ok = abs(round(mv, nd) - lv) <= 0.51 * 10 ** (-nd) or abs(mv - lv) <= 0.5 * 10 ** (-nd) + 1e-12
            out.append(bool(ok))
        else:
            tol = max(absd or 0.0, (rel or 0.0) * abs(lv))
            out.append(bool(abs(mv - lv) <= tol))
    return all(out) and len(ledger_vals) == len(mine)


# ----------------------------------------------------------------------------- recomputations
def coplanar():
    Z = np.load(rf("F-hills-20261115-130237-cbfaf6b", "coplanar.npz"))
    Y = np.load(rf("F-hills-20261115-132156-efddfc0", "coplanar.npz"))
    keep = Z["D"] >= 1e-3 * (1 - 1e-9)
    D = np.concatenate([Y["D"], Z["D"][keep]])
    o = np.argsort(D)
    A = {}
    for k in Z.files:
        if k.endswith("_pro") or k.endswith("_ret"):
            A[k] = np.concatenate([Y[k], np.asarray(Z[k])[keep]])[o]
    D = D[o]
    out = {"D": D, "A": A, "main": Z}
    for t in ("pro", "ret"):
        ok, dis, E = A[f"ok_{t}"], A[f"disrupted_{t}"], A[f"E2_{t}"]
        P = np.array([dis[i][ok[i]].mean() for i in range(D.size)])
        Ex = np.array([np.abs(E[i][dis[i] & ok[i]]).max() if (dis[i] & ok[i]).any() else 0.0 for i in range(D.size)])
        Em = np.array([np.abs(E[i][dis[i] & ok[i]]).mean() if (dis[i] & ok[i]).any() else np.nan for i in range(D.size)])
        out[t] = dict(P=P, Ex=Ex, Em=Em, last=float(D[P > 0].max()), P_deep=float(P[0]), D_deep=float(D[0]),
                      Emax=float(Ex.max()), D_Emax=float(D[np.argmax(Ex)]), Pmax=float(P.max()),
                      D_Pmax=float(D[np.argmax(P)]),
                      n_fail=int((~np.asarray(ok, bool)).sum()), n_total=int(ok.size),
                      n_fail_main_only=int((~np.asarray(Z[f"ok_{t}"], bool)).sum()))
    return out


def bkrs_P(D):
    A = [0.8830, -0.0809, -1.0541, 1.5377, -0.9249, 0.1881]       # mnras.tex:375-376
    return sum(a * D ** k for k, a in enumerate(A))


def bkrs_E(D):
    A = [0.9582, 3.3268, -6.6801, 5.2785, -1.8731, 0.2260]        # mnras.tex:437
    return sum(a * D ** k for k, a in enumerate(A))


def mesh_tree(run, case):
    """n(t) recounted from the per-time `athena -m` stdout files of the mesh run."""
    out = []
    for d in glob.glob(os.path.join(SCR, run, "cases", case + "_t*")):
        t = float(os.path.basename(d).split("_t")[-1])
        n = None
        for ln in open(os.path.join(d, "stdout.txt")):
            m = re.search(r"Total number of MeshBlocks = (\d+)", ln)
            if m:
                n = int(m.group(1))
        CHECKED.append((run, os.path.relpath(os.path.join(d, "stdout.txt"), os.path.join(SCR, run)), "no sha256 record (wave-1 run)"))
        out.append((t, n))
    out.sort()
    return np.array([x[0] for x in out]), np.array([x[1] for x in out], float)


def input_hmin(path):
    blk, cur = {}, None
    for ln in open(path):
        s = ln.split("#")[0].strip()
        if s.startswith("<"):
            cur = s.strip("<>")
            blk[cur] = {}
        elif "=" in s and cur:
            k, v = [x.strip() for x in s.split("=", 1)]
            blk[cur][k] = v
    L = float(blk["mesh"]["x1max"]) - float(blk["mesh"]["x1min"])
    return L / int(blk["mesh"]["nx1"]) / 2 ** (int(blk["mesh_refinement"]["num_levels"]) - 1), float(blk["time"]["cfl_number"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mine", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mine = dict(kv.split("=") for kv in a.mine.split(","))
    R1 = json.load(open(rf(mine["R1"], "closed_forms.json")))
    R3 = json.load(open(rf(mine["R3"], "passages.json")))
    R4 = {(r["q"], r["rp"]): r for r in json.load(open(rf(mine["R4"], "scan.json")))}
    R5 = json.load(open(rf(mine["R5"], "restricted.json")))
    R7 = json.load(open(rf(mine["R7"], "s1check.json"))) if "R7" in mine else []
    rows = parse_ledger()
    cop = coplanar()
    res = []

    def put(i, mine_vals, route, ok=None, note="", **kw):
        r = rows[i]
        lv = nums(r["value"])
        if ok is None:
            ok = agree(lv, mine_vals, **kw)
        res.append(dict(i=i, table=r["table"], group=r["group"], quantity=r["quantity"], ledger=r["value"],
                        source=r["source"], mine=[None if v is None else float(v) for v in mine_vals],
                        route=route, agree=bool(ok), note=note))

    idx = {r["quantity"]: i for i, r in enumerate(rows)}

    def find(sub, start=0):
        for i, r in enumerate(rows):
            if i >= start and sub in r["quantity"]:
                return i
        raise KeyError(sub)

    # ---- Scales
    pb = R1["K6_plunge_bound"]
    put(find("plunge bound"), [10, 100, 1000, pb["q10"], pb["q100"], pb["q1000"]],
        "closed form 4 q^(2/3) (R1)", ok=agree([18.57, 86.18, 400], [pb["q10"], pb["q100"], pb["q1000"]]))
    mb = R1["K6_marginally_bound"]
    put(find("marginally bound"), [mb["r_mb"], mb["L_mb"]], "max of V^2 = 1 numerically (R1)", digits=False, rel=1e-4)
    put(find("Peters time"), [30, 10, R1["K7_peters_time_M"]], "closed form (5/256) a^4/(m1 m2 m_b) (R1)",
        ok=abs(R1["K7_peters_time_M"] - 6328) < 0.5)
    # ---- Restricted Newton
    for t, lab in (("pro", "prograde"), ("ret", "retrograde")):
        c = cop[t]
        put(find(f"last disrupting $D$, {lab}"), [c["last"]], "largest D with P > 0 in coplanar.npz (main + deep)")
        put(find(f"deep-limit disruption probability, {lab}"), [c["P_deep"]], f"P at D = {c['D_deep']:g} (deep supplement npz)")
        put(find(f"largest ejection energy, {lab}"), [c["Emax"], c["D_Emax"]], "max |E2| of disrupted samples over D (npz)")
        put(find(f"failed integrations, {lab}"), [c["n_fail"], c["n_total"]],
            "count of ok == False in the combined arrays (deep supplement below D = 1e-3, main run above)",
            note=f"main run alone: {c['n_fail_main_only']}")
    c = cop["pro"]
    put(find("largest disruption probability (prograde)"), [c["Pmax"], c["D_Pmax"]], "max of P(D) (npz)")
    # printed values at the source
    t1 = src_line("0911.1136", "v1", "prp.tex", range(735, 739))
    t2 = src_line("0911.1136", "v1", "prp.tex", range(846, 850))
    t3 = src_line("0911.1136", "v1", "prp.tex", [854])
    have = [("2.1" in t1 + t2), ("0.44" in t1 + t2), ("27.3" in t1 + t2 + t3), ("1.8" in t1 + t2 + t3),
            ("80" in t1 + t2 + t3 or "0.8" in t1 + t2 + t3), ("0.15" in t1 + t2 + t3)]
    put(find("printed: last disrupting"), [float(x) for x in have], "strings found in prp.tex 735-738, 846-849, 854",
        ok=all(have), note=" | ".join(s[:300] for s in (t1, t2, t3)))
    # digitised SKR curve (fig4) against P(D)
    dig = json.load(open(rf("F-hills-20261115-132703-0bfc352", "skr_digitised.json")))

    def pick(k):
        d = dig[k]
        o = np.argsort(d["D"])
        return np.array(d["D"])[o], np.array(d["v"])[o]
    D = cop["D"]
    for t, rgb in (("pro", "(1.0, 0.0, 0.0)"), ("ret", "(0.0, 0.0, 1.0)")):
        Dr, vr = pick(f"fig4|panel335|rgb{rgb}|SO")
        sel = (Dr >= D.min()) & (Dr <= D.max())
        dv = np.interp(np.log(Dr[sel]), np.log(D), cop[t]["P"]) - vr[sel]
        cop[t]["skr"] = (float(np.median(np.abs(dv))), float(np.max(np.abs(dv))), float(Dr[sel][np.argmax(np.abs(dv))]))
    s = cop["pro"]["skr"]
    put(find("against the digitised curve: median"), [s[0], s[1], s[2]],
        "my interpolation of P(D) (npz) at the digitised SKR fig. 4 points (track's digitisation, scratch)")
    # H1: retrograde with bound binaries wider than 3.5 a_b counted as disrupted
    A = cop["A"]
    Dr, vr = pick("fig4|panel335|rgb(0.0, 0.0, 1.0)|SO")
    ok_, dis, sv, af = A["ok_ret"], A["disrupted_ret"], A["survived_ret"], A["af_ret"]
    Palt = np.array([(dis[i] | (sv[i] & (af[i] > 3.5)))[ok_[i]].mean() for i in range(D.size)])
    sel = (Dr >= 1e-3) & (Dr <= 0.6)
    dv = np.interp(np.log(Dr[sel]), np.log(D), Palt) - vr[sel]
    put(find("wider than $3.5"), [float(np.max(np.abs(dv))), float(D[Palt > 0].max())],
        "coplanar.npz with af > 3.5 counted as disrupted, against the digitised SKR retrograde curve")
    s = cop["ret"]["skr"]
    put(find("against the digitised curve: largest $|\\Delta P|$, retrograde"), [s[1], s[2]],
        "as the prograde row")
    # isotropic against the BKRS fits
    G = np.load(rf("F-hills-20261115-130239-cbfaf6b", "general.npz"))
    kA = G["D_A"] >= 1e-3 * (1 - 1e-9)
    Dg = G["D_A"][kA]
    okA, disA, EA = G["ok_A"][kA], G["disrupted_A"][kA], G["E2_A"][kA]
    Pg = np.array([disA[i][okA[i]].mean() for i in range(Dg.size)])
    Eg = np.array([np.abs(EA[i][disA[i] & okA[i]]).mean() for i in range(Dg.size)])
    s1 = Dg <= 1 + 1e-12
    fP = float(np.max(np.abs(Pg[s1] / bkrs_P(Dg[s1]) - 1)))
    fE = float(np.max(np.abs(Eg[s1] / bkrs_E(Dg[s1]) - 1)))
    put(find("isotropic orientations"), [1, fP, fE, G["theta_A"].size, G["phase_A"].size],
        "general.npz set A against my evaluation of the BKRS polynomials (mnras.tex:372-377, 433-437)",
        ok=agree([0.015, 0.017], [fP, fE]) and G["theta_A"].size == 512 and G["phase_A"].size == 64)
    cop["iso"] = dict(D=Dg, P=Pg, E=Eg)
    t4 = src_line("1804.02911", "v1", "mnras.tex", [368, 377, 440])
    have = ["88" in t4, "1\\%" in t4]
    put(find("printed: plateau"), [float(x) for x in have], "strings at mnras.tex 368, 377, 440", ok=all(have),
        note=t4[:400])
    # V4: nine points (independent code of the lead) from its sample arrays and the npz reference
    V4 = np.load(rf("F-hills-20261115-145246-090f5dc", "v4_samples.npz"))
    v4s = json.load(open(rf("F-hills-20261115-145246-090f5dc", "v4_summary.json")))
    dPs, dEs = [], []
    for row in v4s["rows"]:
        k = f"{row['sense']}_{row['D']}"
        st, E = V4[k + "_state"], V4[k + "_E"]
        Pm = float(np.mean(st == "disrupted"))
        Em = float(np.mean(np.abs(E[st == "disrupted"])))
        t = row["sense"]
        i = int(np.argmin(np.abs(cop["D"] - row["D"])))
        okr, disr, Er = A[f"ok_{t}"][i], A[f"disrupted_{t}"][i], A[f"E2_{t}"][i]
        Pr = float(disr[okr].mean())
        Er_ = float(np.abs(Er[disr & okr]).mean())
        dPs.append(abs(Pm - Pr))
        dEs.append(abs(Em / Er_ - 1))
    put(find("independent code, nine points"), [max(dPs), max(dEs), 0.38],
        "v4_samples.npz (600 phases per point) against coplanar.npz at the same D",
        note=f"per point dP {['%.4f' % x for x in dPs]}, dE/E {['%.4f' % x for x in dEs]}")
    v4b = json.load(open(rf("F-hills-20261115-145544-a314517", "v4b_summary.json")))
    dPb = [abs(r["P_dis"] - r["P_dis_ref"]) for r in v4b["rows"]]
    dEb = [abs(r["Emean_dis"] / r["Emean_dis_ref"] - 1) for r in v4b["rows"]]
    r5 = {(r["sense"], r["D"]): r for r in R5["rows"]}
    put(find("wide binaries followed on"), [max(dPb), max(dEb)],
        "v4b_summary rows (no sample arrays in that run); my R5 at ret D = 0.3 with wide binaries followed "
        f"gives P = {r5[('ret', 0.3)]['P_mine']:.4f} against the npz {r5[('ret', 0.3)]['P_track']:.4f}",
        note="transcription only for D = 0.38; D = 0.3 also by my own integration")
    # ---- Geodesic baseline (S1)
    S1 = np.load(rf("F-hills-20261115-130405-ce17dcf", "s1.npz"))
    meta = json.loads(str(S1["meta"]))
    laws, senses = meta["laws"], meta["senses"]
    betas = S1["betas"]
    sep = S1["separated"] > 0
    sf = {}
    for law in laws:
        for s_, sn in ((1, "pro"), (-1, "retro")):
            sf[(sn, law)] = sep[laws.index(law), senses.index(s_)].mean(-1)
    put(find("encounters of the scan"), [S1["status"].size], "size of the outcome arrays of s1.npz (F-hills-20261115-130405-ce17dcf)")
    on = {law: float(betas[np.argmax(sf[("retro", law)] > 0.01)]) for law in laws}
    put(find("retrograde onset"), [on["hrna"], on["newton"]], "first beta with retro separated fraction > 0.01 (s1.npz)")
    for b in (3, 10):
        k = int(np.argmin(np.abs(betas - b)))
        vals = [sf[("pro", "newton")][k], sf[("retro", "newton")][k], sf[("pro", "hrna")][k], sf[("retro", "hrna")][k]]
        put(find(f"separated fraction at $\\beta={b}$"), [b] + vals, "count fraction of 400 phases (s1.npz)",
            ok=agree(nums(rows[find(f"separated fraction at $\\beta={b}$")]["value"]), vals))
    # digitised 2404 curves
    ddir = os.path.join(SCR, "F-hills-20261115-142554-c10b371", "digitized")
    spj = json.load(open(os.path.join(ddir, "sep_fraction.json")))
    CHECKED.append(("F-hills-20261115-142554-c10b371", "digitized/sep_fraction.json", "no sha256 record (wave-1 run)"))
    # x calibration checked against the tick marks of the file (0..10 in beta); y: 0..1 at the
    # axis ends used by the track (39.97, 191.17 in file units); curve order: retro Newton, 1PN,
    # HRNA, pro Newton, 1PN, HRNA (identified below by the values at beta = 10)
    tx = sorted({round(t[0][0], 3) for t in spj["ticks"] if abs(t[0][0] - t[1][0]) < 1e-6})
    x0, x1, y0, y1 = 36.285756, 259.485756, 39.971353, 191.171353
    names = ["retro_newton", "retro_1pn", "retro_hrna", "pro_newton", "pro_1pn", "pro_hrna"]
    dev, at10 = {}, {}
    for nm, c in zip(names, spj["curves"]):
        P_ = np.array(c["points"])
        x = (P_[:, 0] - x0) / (x1 - x0) * 10
        y = (P_[:, 1] - y0) / (y1 - y0)
        o = np.argsort(x)
        x, y = x[o], y[o]
        at10[nm] = float(np.interp(9.95, x, y))
        if "1pn" in nm:
            continue
        sn, law = nm.split("_")
        selb = (betas >= x.min()) & (betas <= x.max())
        dev[nm] = float(np.max(np.abs(np.interp(betas[selb], x, y) - sf[(sn, law)][selb])))
    put(find("largest $|\\Delta|$ of the fraction"), [max(dev.values())],
        "my interpolation of the digitised 2404 curves (track's digitisation in scratch; calibration constants of "
        "the track, x ticks checked) against s1.npz", ok=agree([0.0225], [max(dev.values())]),
        note=json.dumps(dict(dev=dev, curve_values_at_beta_9_95=at10, x_ticks_file_units=tx[:12])))
    s1s = json.load(open(rf("F-hills-20261115-142554-c10b371", "s1_summary.json")))["checks"]
    vdev = max(v for k, v in s1s.items() if k.startswith("digitized_vmean_max_rel_dev") and not k.endswith("onset"))
    put(find("mean $v_\\infty$"), [vdev], "transcription of s1_summary.json checks only (speed curves not recomputed)",
        note="transcription only")
    k10 = int(np.argmin(np.abs(betas - 10)))
    il = laws.index("hrna")
    amax = float(max(S1["alpha_max"][il, j, k10].max() for j in range(2)))
    aall = float(max(S1["alpha_all"][il, j, k10].max() for j in range(2)))
    put(find("largest $a_b/R_{\\rm curv}$"), [10, amax], "max of alpha_max (a/R while the Newtonian pair energy < 0) at beta = 10, HRNA, s1.npz",
        ok=agree([0.0056], [amax]),
        note=f"the same parameter at any time (alpha_all) reaches {aall:.3f} at beta = 10 (pericentre)")
    # ---- Pericentre scan: transcription of v7 and my own scan R4
    v7 = json.load(open(rf("F-hills-20261115-145915-71abf93", "v7_summary.json")))
    for key, q in (("q10", 10.0), ("q4", 4.0)):
        for r in v7[key]:
            lab = f"$q={int(q)}$, $r_p={r['rp']:g}$"
            try:
                i = find(lab)
            except KeyError:
                continue
            tv = [r["newton_full"]["separated"], r["newton_full"]["member_below_4M"], r["hrna"]["separated"], r["hrna"]["plunge"]]
            m4 = R4.get((q, r["rp"]))
            mv = None if m4 is None else [m4["newton"]["separated"], m4["newton"]["member_below_4M"],
                                          m4["hrna_handoff"]["separated"], m4["hrna_handoff"]["plunge"]]
            lv = nums(rows[i]["value"])[-4:]
            tr_ok = agree(lv, tv)
            sig = [np.sqrt(max(p * (1 - p), 1 / 180) / 180) for p in tv]
            own_ok = None if mv is None else all(abs(x - y) <= 3 * s + 1e-12 for x, y, s in zip(mv, tv, sig))
            put(i, tv, "transcription of v7_summary; independent: my scan R4 (180 phases)", ok=tr_ok,
                note=("R4: " + ", ".join(f"{x:.3f}" for x in mv) + f"; within 3 binomial sigma of v7: {own_ok}") if mv else "no R4 case")
    # ---- First passages: raw curves of N1 and my R3
    n1 = json.load(open(rf("F-20261115-174648-25514db", "passage_summary.json")))
    PC = np.load(rf("F-20261115-174648-25514db", "passage_curves.npz"))
    for key, q in (("q4", 4), ("q10", 10)):
        s = n1[key]
        mineN = R3[key]["newton"]
        t = PC[f"{key}_newton_t"]
        Ebc = PC[f"{key}_newton_E{s['newton']['ejected']}_bc"]
        EM = PC[f"{key}_newton_E{s['newton']['ejected']}_M"]
        late = t >= 300
        unit = R1["K8_scales"][f"q{q}"]["E_unit"]
        put(find(f"${'q=' + str(q)}$: energy unit"), [unit], "closed form (m1 m2/a_b) q^(1/3) at a_b = nominal (R1)")
        raw_bc, raw_sp = float(Ebc[-1]), float(np.ptp(Ebc[late]))
        put(find(f"${'q=' + str(q)}$, Newton: ejected member, energy"),
            [s["newton"]["ejected"], raw_bc, raw_sp], "N1 curves (passage_curves.npz, last sample, ptp after t = 300) ; R3: "
            f"m{mineN['ejected']}, {mineN['E_ej_bary_u']:.5f}, {mineN['E_ej_bary_spread_late_u']:.2g}",
            ok=agree(nums(rows[find(f"${'q=' + str(q)}$, Newton: ejected member, energy")]["value"])[1:], [raw_bc, raw_sp])
            and agree(nums(rows[find(f"${'q=' + str(q)}$, Newton: ejected member, energy")]["value"])[1:2], [mineN["E_ej_bary_u"]]))
        put(find(f"${'q=' + str(q)}$, Newton: two-body energy"), [float(EM[late].min()), float(EM[late].max())],
            f"N1 curves (t >= 300); R3: {mineN['E_ej_M_late_min_u']:.4f} to {mineN['E_ej_M_late_max_u']:.4f}")
        rcap = PC[f"{key}_newton_r{s['newton']['captured']}"]
        put(find(f"${'q=' + str(q)}$, Newton: captured member"), [s["newton"]["captured"], mineN["E_cap_u"], mineN["rmin_cap"]],
            f"R3 (own integration); N1 curve min r of the captured member {float(rcap.min()):.4f}")
        hr = R3[key]["hrna"]
        i = find(f"${'q=' + str(q)}$, geodesic: ejected member")
        if q == 10:
            mv = [2, hr["E2_u_end"], hr["plunge_t"][0]]
            put(i, mv, "R3 (own HRNA; plunge time = crossing of r = 2.5 M, interpolated)",
                ok=abs(hr["E2_u_end"] - 1.159) < 0.0006 and abs(hr["plunge_t"][0] - 97.1) < 1.0,
                note=f"ledger 97.1 is the first sample inside 2.5 M (N1 first_pericentre_1 = {n1[key]['hrna']['first_pericentre_1']})")
        else:
            mv = [2, hr["E2_u_t600"], hr["E1_u_t600"], hr["first_pericentre_1"][1]]
            put(i, mv, "R3 (own HRNA)", ok=abs(hr["E2_u_t600"] - 0.9703) / 0.9703 < 0.02 and abs(hr["E1_u_t600"] + 0.5) < 0.01
                and abs(hr["first_pericentre_1"][1] - 7.262) < 0.01,
                note=f"ejected energy drifts with time: {hr['E2_u_t600']:.4f} at t = 600, {hr['E2_u_end']:.4f} at t = 1500 (pair force of the bound member)")
        nf = R3[key]["newton_fixed"]
        put(find(f"${'q=' + str(q)}$, Newton with $M$ fixed"), [max(nf["E1_u"], nf["E2_u"]), min(nf["rmin_1"], nf["rmin_2"])],
            "R3 (own integration, energy at t = 600)", digits=False, rel=0.005,
            note=f"N1 evaluates at t_end = {n1[key]['newton_fixed']['t_end']:.0f}")
    e6 = json.load(open(rf("F-20261115-174102-ffa764f", "baselines_p1.json")))
    put(find("reproduces the earlier run"), [R3["q4"]["newton"]["E_ej_bary_u"]], f"R3; E6 file {e6['newton']['E_ejected_bc_u']:.6f}")
    put(find("displacement of the heavy black hole"), [R3["q4"]["newton"]["hole_displacement_t280"], 280],
        f"R3 at t = 280; E6 file {e6['newton']['at_t_run']['hole_displacement']:.4f}")
    e4 = json.load(open(rf("F-20261115-173821-b2c969a", "test_nrread_synthetic.json")))
    put(find("readers on a synthetic"), [sum(bool(r["ok"]) for r in e4["results"]), len(e4["results"])],
        "count of ok in test_nrread_synthetic.json (the test itself not rerun)")
    co = R3["q10"]["newton"]["captured_orbit_t1500"]
    put(find("captured orbit of Newton"), [10, co["a"], co["e"], co["rp"]], "R3 osculating orbit at t = 1500",
        ok=agree([7.55, 0.247, 5.68], [co["a"], co["e"], co["rp"]]))
    # ---- Mesh and cost
    nov = json.load(open(rf("F-hills-20261115-045438-f62d553", "results.json")))
    rates = sorted(v["R_mbcyc_per_s"] for v in nov["vacuum"].values() if isinstance(v, dict) and "R_mbcyc_per_s" in v)
    rmed = float(np.median(rates))
    hq10, cfl10 = input_hmin(os.path.join(TR, "three_punctures/inputs/hills_q10_m8.athinput"))
    hq4, cfl4 = input_hmin(os.path.join(TR, "nr_first/inputs/p1_q4.athinput"))
    trees = {}
    for run, case, lab, h, span in (("F-hills-20261115-131348-634fb86", "D205_m8_r1.8", "$q=10$, $m/8$:", hq10, 240.0),
                                    ("F-hills-20261115-131348-634fb86", "D205_m16_r1.8", "$q=10$, $m/16$:", hq10 / 2, 240.0),
                                    ("F-hills-20261115-131348-634fb86", "D205_m16_r1.2", "$q=10$, $m/16$, small", hq10 / 2, 240.0),
                                    ("F-hills-20261115-131933-907e5fe", "D256q4_m8_r1.8", "$q=4$, $m/8$:", hq4, 270.0),
                                    ("F-hills-20261115-131933-907e5fe", "D256q4_m16_r1.8", "$q=4$, $m/16$:", hq4 / 2, 270.0),
                                    ("F-hills-20261115-131933-907e5fe", "D256q4_m16_r1.2", "$q=4$, $m/16$, small", hq4 / 2, 270.0)):
        t, n = mesh_tree(run, case)
        trees[case] = (t, n)
        cyc = span / (0.25 * h)
        ch = [n.mean() * cyc / r / 3600 for r in (rmed, max(rates), min(rates))]
        chT = np.trapezoid(n, t) / (t[-1] - t[0]) * cyc / rmed / 3600
        put(find(lab), [n[0], n.max(), n.mean(), ch[0], ch[1], ch[2]],
            f"n(t) recounted from {len(n)} athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min {h:g}; "
            f"rates of the novelty run; card-hours plain mean (trapezoid {chT:.4g})",
            ok=agree(nums(rows[find(lab)]["value"])[-6:-3], [n[0], n.max(), n.mean()]) and
            all(abs(x - y) / y < 0.01 for x, y in zip([ch[0]] + ch[1:], nums(rows[find(lab)]["value"])[-3:])))
    put(find("rate, MeshBlock-cycles"), [rmed, min(rates), max(rates)], "median, min, max of R_mbcyc_per_s over the novelty run's vacuum logs",
        note=json.dumps(rates))
    cnt = {}
    for ln in open(rf("F-20261115-173543-29e87e8", "counts.txt")):
        p = dict(x.split("=") for x in ln.split()[1:] if "=" in x)
        cnt[int(p["num_levels"])] = int(p["t0_tree"])
    raw = {}
    for lv in (9, 10, 11):
        lg = os.path.join(SCR, "F-20261115-173543-29e87e8", f"q4_L{lv}", "athena_m.log")
        CHECKED.append(("F-20261115-173543-29e87e8", f"q4_L{lv}/athena_m.log", "listed in sha256sums.txt?"))
        for ln in open(lg):
            m = re.search(r"Total number of MeshBlocks = (\d+)", ln)
            if m:
                raw[lv] = int(m.group(1))
    put(find("input at the start, release executable"), [4, raw.get(9), raw.get(10), raw.get(11)],
        "recounted from q4_L9..L11/athena_m.log", ok=agree([1128, 1716, 2514], [raw.get(9), raw.get(10), raw.get(11)]),
        note=f"counts.txt {cnt}")
    ln229 = open(os.path.join(WT, "coord/INTERFACES/multi_puncture.md")).read().splitlines()[228:230]
    put(find("card memory, MeshBlock slots"), [3000.0 if "about 3000" in " ".join(ln229) else None],
        "coord/INTERFACES/multi_puncture.md lines 229-230 read", note=" ".join(ln229))

    # ---- extras for claims K8, K14, K18 (not ledger rows)
    extras = {}
    P4 = np.load(rf("F-hills-20261115-131801-907e5fe", "p4.npz"))
    for qq in ("1e+06", "10"):
        ref = P4[f"outcome_q{qq}_k40"]
        extras[f"K18_q{qq}"] = {f"k{k}_same_outcome_as_k40": float(np.mean(P4[f"outcome_q{qq}_k{k}"] == ref))
                                for k in (5, 10, 20) if f"outcome_q{qq}_k{k}" in P4.files}
    k85 = int(np.argmin(np.abs(betas - 8.5)))
    extras["K8_alpha_hrna"] = {"beta10_alpha_all_max": aall, "beta10_alpha_bound_max": amax,
                               "beta8.5_alpha_all_max": float(max(S1["alpha_all"][il, j, k85].max() for j in range(2)))}
    smoke = os.path.join(SCR, "F-20261115-174602-c6879fe", "batch.list.last.log")
    peak = None
    if os.path.isfile(smoke):
        for ln in open(smoke):
            m = re.search(r"gpu_mem_peak_MiB=(\d+)", ln)
            if m:
                peak = int(m.group(1))
    extras["K14_card_memory"] = {"smoke_peak_MiB_at_2700_slots": peak, "card_MiB": 81920,
                                 "MiB_per_slot_all_in": None if peak is None else peak / 2700,
                                 "slots_if_linear_all_in": None if peak is None else 81920 / (peak / 2700)}
    mj10 = json.load(open(rf("F-hills-20261115-131348-634fb86", "mesh_count_b.json")))
    mj4 = json.load(open(rf("F-hills-20261115-131933-907e5fe", "mesh_count_b.json")))
    eq = {}
    for case, (t, n) in trees.items():
        mj = mj10 if case.startswith("D205") else mj4
        tj, nj = np.array(mj["tracks"][case]["t"], float), np.array(mj["tracks"][case]["n"], float)
        eq[case] = bool(len(tj) == len(t) and np.allclose(tj, t, atol=0.05) and np.array_equal(nj, n))
    extras["K14_mesh_recount_equals_run_json"] = eq
    print(json.dumps(extras))

    # ---- write
    done = {r["i"] for r in res}
    for i, r in enumerate(rows):
        if i not in done:
            res.append(dict(i=i, table=r["table"], group=r["group"], quantity=r["quantity"], ledger=r["value"],
                            source=r["source"], mine=[], route="NOT RECOMPUTED", agree=False, note=""))
    res.sort(key=lambda x: x["i"])
    json.dump(dict(rows=res, extras=extras, inputs_checked=CHECKED, ledger_sha256=sha(LEDGER)), open(os.path.join(a.out, "ledger_check.json"), "w"), indent=1)
    with open(os.path.join(a.out, "ledger_check.md"), "w") as f:
        f.write("| # | table | quantity | ledger value | source | my value | agree | route |\n|---|---|---|---|---|---|---|---|\n")
        for r in res:
            mv = ", ".join("-" if v is None else f"{v:.6g}" for v in r["mine"])
            f.write(f"| {r['i'] + 1} | {r['table'][-1]} | {r['quantity'][:90]} | {r['ledger']} | {r['source'][:40]} | {mv} | "
                    f"{'yes' if r['agree'] else 'NO'} | {r['route'][:160]}{(' NOTE: ' + r['note'][:300]) if r['note'] else ''} |\n")
    print(sum(r["agree"] for r in res), "of", len(res), "rows agree")
    for r in res:
        if not r["agree"]:
            print("DISAGREE/NOT RECOMPUTED:", r["i"] + 1, r["quantity"][:80], r["ledger"], r["mine"], r["note"][:200])

    # ---- figures: trees and passages
    fs.use_style()
    import matplotlib.pyplot as plt
    mj10 = json.load(open(rf("F-hills-20261115-131348-634fb86", "mesh_count_b.json")))
    mj4 = json.load(open(rf("F-hills-20261115-131933-907e5fe", "mesh_count_b.json")))
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    fig.subplots_adjust(wspace=0.35, left=0.08, right=0.98, bottom=0.14, top=0.9)
    for k, (case, (t, n)) in enumerate(trees.items()):
        mj = mj10 if case.startswith("D205") else mj4
        axx = ax[0] if case.startswith("D205") else ax[1]
        col = fs.SERIES[k % 3]
        axx.plot(t, n, "o", mfc="none", color=col, label=f"{case}: recount")
        axx.plot(mj["tracks"][case]["t"], mj["tracks"][case]["n"], "-", color=col, lw=1.0, label=f"{case}: run's JSON")
    for axx, title in zip(ax, ("q = 10", "q = 4")):
        axx.axhline(3000, **fs.MASK_LINE)
        axx.axhline(2700, **fs.GUIDE)
        axx.set_xlabel("t / M (0 at the pericentre)")
        axx.set_ylabel("MeshBlocks")
        axx.set_title(title, fontsize=10)
        axx.legend(fontsize=5, loc="lower right", ncol=2)
    fs.save(fig, os.path.join(a.out, "fig_ledger_mesh"))
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    fig.subplots_adjust(wspace=0.35, left=0.08, right=0.98, bottom=0.14, top=0.9)
    MC = np.load(rf(mine["R3"], "passage_curves.npz"))
    for axx, key in zip(ax, ("q4", "q10")):
        s = n1[key]
        ej = s["newton"]["ejected"]
        axx.plot(PC[f"{key}_newton_t"], PC[f"{key}_newton_E{ej}_bc"], color=fs.PAL["blue"], lw=2.2, alpha=0.5, label="N1, barycentric")
        axx.plot(MC[f"{key}_t"], MC[f"{key}_Eout"], color=fs.PAL["red"], lw=1.0, ls="--", label="R3, Jacobi outer")
        axx.plot(PC[f"{key}_newton_t"], PC[f"{key}_newton_E{ej}_M"], color=fs.PAL["green"], lw=2.2, alpha=0.5, label="N1, two-body with M")
        axx.plot(MC[f"{key}_t"], MC[f"{key}_EejM"], color=fs.PAL["orange"], lw=1.0, ls="--", label="R3, two-body with M")
        axx.set_xlim(0, 700)
        axx.set_xlabel("t / M")
        axx.set_ylabel("energy of the ejected member [unit]")
        axx.set_title(key, fontsize=10)
        axx.legend(fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_ledger_passages"))


if __name__ == "__main__":
    main()
