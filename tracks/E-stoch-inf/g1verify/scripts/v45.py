"""V4 (constraints) and V5 (spatial order, floor) from my constraint pass (g1verify).

usage: v45.py OUTDIR CONSTRAINTS_RUN_DIR
Reads constraints.json (constraints.py) and the records <basename>.sf.con.hst of every run
named there (for <[H]>, <[M]> and the ratios), writes v45.json.

Normalisation: rms of a part of H over the box mean <[H]> of the proper (s = +1) run at the
same cycle (record column <[H]>); M likewise with <[M]>. "Floor": the out band (|n|^2 > 9
nmax2) of the odd part, which no physics fills to third order.
V4 items: odd and even parts (even without its box mean), which dominates and from when,
halving factors (odd: expect 2, even: expect 4) where the part is above 10 times the floor,
negative controls (odd part NC / proper at the same N and dump), record maxima and record
halving factors F_H = R_H(s=1)/R_H(s=1/2) during the entry.
Strict A4 (SCOPE 4 item 4): record H/[H] second order (F_H = 4 within 5 percent, my
operational tolerance) and M/[M] first order (F_M = 2 within 5 percent) at every record row
of the entry window, the sign-flip control first order. A4' (SCOPE 4b): (a) even part
halving 4.00 +- 0.05 above the floor and the two finest resolutions within 5 percent;
(b) odd part halving 2.00 +- 0.05 and converging at the order of A5; (c) record <|H|/[H]>
<= 1e-9 and <|M|/[M]> < 1e-3; (d) NC odd part >= 1e3 x proper.
V5: order log2(odd_N / odd_2N) at equal times (finer run interpolated in log to the coarse
dump times) on L32 -> L64 -> L128 -> L256; floor against N.
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, catalog as C  # noqa: E402

out, cdir = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
con = json.load(open(os.path.join(cdir, "constraints.json")))
runs = C.catalog()
ENTRY_END = {}          # code time when the last shell k_max enters (k = a H), my background
res = dict(sets={}, a4={}, a5={}, figdata={})


def record(key):
    cols, d = nrsf.read_record(os.path.join(runs[key]["dir"], "sr.sf.con.hst"))
    return cols, d


def at_cycles(key, cycles):
    cols, d = record(key)
    cyc = d[:, cols.index("cycle")].astype(int)
    idx = [int(np.where(cyc == c)[0][0]) for c in cycles]
    o = {n: d[idx, cols.index(n)] for n in ("<[H]>", "<[M]>", "<|H|/[H]>", "<|M|/[M]>")}
    o["efolds"] = d[idx, cols.index("efolds=-ln<chi>/2")]
    return o


from ref import CodeBackground, crossing_time  # noqa: E402
bg = CodeBackground(-2.66679478988261254e+00, 2.97300406808996935e-02, 1.82877655899024605e-01, t_end=9.0)

for sname, s in con.items():
    if not isinstance(s, dict) or "rows" not in s:
        continue
    rows = s["rows"]
    keys = s["keys"]
    cyc = [r["cycle"] for r in rows]
    t = np.array([r["time"] for r in rows])
    rec = at_cycles(keys[0], cyc)
    hn, mn = rec["<[H]>"], rec["<[M]>"]
    kmax = np.sqrt(s["nmax2"])
    t_in = float(crossing_time(bg, [kmax])[0][0])
    o = dict(keys=keys, N=s["N"], nmax2=s["nmax2"], time=t.tolist(), efolds=rec["efolds"].tolist(),
             t_kmax_enters=t_in)
    oddH = np.array([r["rms_odd_H"] for r in rows]) / hn
    evenH = np.array([r["rms_even_H_nomean"] for r in rows]) / hn
    meanH = np.array([r["mean_even_H"] for r in rows]) / hn
    floorH = np.array([r["odd_H_bands"]["out"] for r in rows]) / hn
    floorHe = np.array([r["even_H_bands"]["out"] for r in rows]) / hn
    inbH = np.array([r["odd_H_bands"]["inb"] for r in rows]) / hn
    oddM = np.array([r["rms_odd_M"] for r in rows]) / mn
    evenM = np.array([r["rms_even_M"] for r in rows]) / mn
    floorM = np.array([r["odd_M_bands"]["out"] for r in rows]) / mn
    o.update(oddH=oddH.tolist(), evenH=evenH.tolist(), meanH=meanH.tolist(), floorH=floorH.tolist(),
             floorH_even=floorHe.tolist(), inbH=inbH.tolist(), oddM=oddM.tolist(), evenM=evenM.tolist(),
             floorM=floorM.tolist())
    dom = oddH > evenH
    o["odd_dominates_H_from_t"] = float(t[np.argmax(dom)]) if dom.any() else None
    o["odd_dominates_H_at"] = [bool(x) for x in dom]
    o["max_oddH"], o["max_evenH"] = float(oddH.max()), float(evenH.max())
    o["t_max_oddH"], o["t_max_evenH"] = float(t[oddH.argmax()]), float(t[evenH.argmax()])
    o["max_oddM"], o["max_evenM"] = float(oddM.max()), float(evenM.max())
    if "h_rms_odd_H" in rows[0]:
        fo = np.array([r["rms_odd_H"] / r["h_rms_odd_H"] for r in rows])
        fe = np.array([r["rms_even_H_nomean"] / r["h_rms_even_H_nomean"] for r in rows])
        fom = np.array([r["rms_odd_M"] / r["h_rms_odd_M"] for r in rows])
        fem = np.array([r["rms_even_M"] / r["h_rms_even_M"] for r in rows])
        nl_odd = np.array([r["rms_odd_H_minus_2half"] for r in rows]) / hn
        nl_even = np.array([r["rms_even_H_minus_4half"] for r in rows]) / hn
        okH_o = oddH > 10 * floorH
        okH_e = evenH > 10 * floorHe
        o.update(F_oddH=fo.tolist(), F_evenH=fe.tolist(), F_oddM=fom.tolist(), F_evenM=fem.tolist(),
                 nonlinear_odd=nl_odd.tolist(), nonlinear_even=nl_even.tolist(),
                 above_floor_odd=[bool(x) for x in okH_o], above_floor_even=[bool(x) for x in okH_e])
        def rng(a, m):
            a = a[m & (t > 0)]
            return [float(a.min()), float(a.max())] if a.size else None
        o["F_oddH_range_above_floor"] = rng(fo, okH_o)
        o["F_evenH_range_above_floor"] = rng(fe, okH_e)
        o["F_oddM_range"] = rng(fom, np.ones_like(okH_o))
        o["F_evenM_range"] = rng(fem, np.ones_like(okH_o))
    r_ = s["record"]
    o["record_max"] = dict(H_p=r_["maxH_p"], M_p=r_["maxM_p"], H_m=r_["maxH_m"], M_m=r_["maxM_m"])
    if "F_H" in r_:
        th = np.array(r_["time_h"])
        FH, FM = np.array(r_["F_H"]), np.array(r_["F_M"])
        ent = (th > 0.3) & (th <= min(t_in + 1.0, th.max()))
        o["record_F_H_entry"] = [float(FH[ent].min()), float(FH[ent].max())]
        o["record_F_M_entry"] = [float(FM[ent].min()), float(FM[ent].max())]
        o["record_F_H_all"] = [float(FH[th > 0.3].min()), float(FH[th > 0.3].max())]
        res["figdata"][f"{sname}_recF"] = [th.tolist(), FH.tolist(), FM.tolist()]
    res["sets"][sname] = o

# negative controls against the proper runs of the same set-up
nc = {}
for ncs, prop in (("NC32", "L32"), ("NC64", "Q64"), ("NC128", "Q128")):
    if ncs in res["sets"] and prop in res["sets"]:
        a, b = res["sets"][ncs], res["sets"][prop]
        n = min(len(a["time"]), len(b["time"]))
        ra = np.array(a["oddH"][1:n]) / np.array(b["oddH"][1:n])
        rm = np.array(a["oddM"][1:n]) / np.array(b["oddM"][1:n])
        nc[ncs] = dict(proper=prop, time_diff_max=float(np.max(np.abs(np.array(a["time"][:n]) - np.array(b["time"][:n])))),
                       ratio_oddH_range=[float(ra.min()), float(ra.max())],
                       ratio_oddM_range=[float(rm.min()), float(rm.max())],
                       record_max_H=a["record_max"]["H_p"], record_max_M=a["record_max"]["M_p"])
res["negative_controls"] = nc

# ---------------------------------------------------------------- strict A4 and A4'
a4 = {}
for sname in ("L32", "Q64", "Q128"):
    o = res["sets"].get(sname)
    if not o or "record_F_H_entry" not in o:
        continue
    fh, fm = o["record_F_H_entry"], o["record_F_M_entry"]
    a4[sname] = dict(strict_H_second_order=bool(fh[0] >= 3.8 and fh[1] <= 4.2),
                     strict_M_first_order=bool(fm[0] >= 1.9 and fm[1] <= 2.1),
                     record_F_H_entry=fh, record_F_M_entry=fm,
                     Aprime_a_even_halving=o.get("F_evenH_range_above_floor"),
                     Aprime_a_pass=bool(o.get("F_evenH_range_above_floor") and o["F_evenH_range_above_floor"][0] >= 3.95
                                        and o["F_evenH_range_above_floor"][1] <= 4.05),
                     Aprime_b_odd_halving=o.get("F_oddH_range_above_floor"),
                     Aprime_b_pass=bool(o.get("F_oddH_range_above_floor") and o["F_oddH_range_above_floor"][0] >= 1.95
                                        and o["F_oddH_range_above_floor"][1] <= 2.05),
                     Aprime_c_H=o["record_max"]["H_p"], Aprime_c_M=o["record_max"]["M_p"],
                     Aprime_c_pass=bool(o["record_max"]["H_p"] <= 1e-9 and o["record_max"]["M_p"] < 1e-3))
for sname in ("P256", "L64", "L128", "L256", "L64proc"):
    o = res["sets"].get(sname)
    if o:
        a4[sname] = dict(record_max=o["record_max"], Aprime_c_pass=bool(o["record_max"]["H_p"] <= 1e-9 and o["record_max"]["M_p"] < 1e-3),
                         odd_dominates_H_from_t=o["odd_dominates_H_from_t"])
# A4'(a) second clause: even parts of the two finest resolutions within 5 percent where above floor
pairs = {}
for a, b in (("Q128", "P256"), ("L128", "L256"), ("Q64", "Q128")):
    if a in res["sets"] and b in res["sets"]:
        A, B = res["sets"][a], res["sets"][b]
        tb = np.array(B["time"])
        dev = []
        for ti, ea, fa in zip(A["time"], A["evenH"], A["floorH_even"]):
            j = int(np.argmin(np.abs(tb - ti)))
            if ti > 0 and abs(tb[j] - ti) < 0.02 and ea > 10 * fa and B["evenH"][j] > 10 * B["floorH_even"][j]:
                dev.append((ti, B["evenH"][j] / ea - 1))
        pairs[f"{a}-{b}"] = dict(n=len(dev), max_abs_dev=float(max(abs(d) for _, d in dev)) if dev else None,
                                 devs=[[float(x), float(y)] for x, y in dev])
a4["even_resolution_pairs"] = pairs
res["a4"] = a4

# ---------------------------------------------------------------- V5: spatial order and floor
def interp_log(tq, t, y):
    y = np.maximum(np.asarray(y), 1e-300)
    return np.exp(np.interp(tq, t, np.log(y)))


a5 = {}
ladder = [k for k in ("L32", "L64", "L128", "L256") if k in res["sets"]]
for qty in ("oddH", "inbH", "oddM", "floorH"):
    for c, f in zip(ladder[:-1], ladder[1:]):
        A, B = res["sets"][c], res["sets"][f]
        tA = np.array(A["time"])
        tB = np.array(B["time"])
        m = (tA > 0.2) & (tA <= tB.max() + 1e-9)
        yB = interp_log(tA[m], tB, B[qty])
        p = np.log2(np.array(A[qty])[m] / yB)
        a5[f"{qty}_{c}_{f}"] = dict(time=tA[m].tolist(), order=p.tolist(),
                                    coarse=np.array(A[qty])[m].tolist(), fine=yB.tolist(),
                                    fine_floor=interp_log(tA[m], tB, B["floorH"]).tolist())
# floor against N at fixed times (L set) and in the P set
fl = {}
for setlist, tag in ((ladder, "L"), ([k for k in ("Q64", "Q128", "P256") if k in res["sets"]], "P")):
    for tq in (0.5, 1.0, 2.0, 3.0, 4.0):
        vals = []
        for k in setlist:
            o = res["sets"][k]
            tt = np.array(o["time"])
            if tt.max() + 1e-9 < tq:
                continue
            j = int(np.argmin(np.abs(tt - tq)))
            vals.append((o["N"], o["floorH"][j], o["floorH_even"][j], tt[j]))
        if len(vals) >= 2:
            Ns = np.array([v[0] for v in vals], float)
            fo = np.array([v[1] for v in vals])
            slope = np.polyfit(np.log(Ns), np.log(fo), 1)[0] if len(vals) >= 2 else None
            fl[f"{tag}_t{tq}"] = dict(N=Ns.tolist(), floor_odd=fo.tolist(), floor_even=[v[2] for v in vals],
                                      slope_all=float(slope),
                                      slope_last_pair=float(np.log(fo[-1] / fo[-2]) / np.log(Ns[-1] / Ns[-2])))
a5["floor"] = fl
res["a5"] = a5
with open(os.path.join(out, "v45.json"), "w") as f:
    json.dump(res, f, indent=1)
summ = {k: {kk: v[kk] for kk in ("max_oddH", "max_evenH", "t_max_oddH", "t_max_evenH", "odd_dominates_H_from_t",
                                  "record_max", "t_kmax_enters") if kk in v} for k, v in res["sets"].items()}
print(json.dumps(summ, indent=1))
print(json.dumps(res["negative_controls"], indent=1))
print(json.dumps({k: v for k, v in a4.items() if k != "even_resolution_pairs"}, indent=1))
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "devs"} for k, v in pairs.items()}, indent=1))
print(json.dumps(fl, indent=1))
