#!/usr/bin/env python3
"""The lead's own check of the G3 scope review (g3/amend JOURNAL entry 1, C1-C6).

Usage: check_review.py OUTDIR   (run under harness/bin/nrpic-run; one core)

C1  block counts and level extents of candidate mesh members: decks written here from the EG8 deck
    (excguard/inputs/esflg8.athinput), mesh structure from `athena -m` (processor build of core-v0.8).
C2  finder mass at t = 0 of FK (M/8), ES-FL (M/8), FL16 (M/16) and EG8 (M/8, polished), first record.
C3  FK's snapshot at 200 M: per label bin the spread of the particles' own proper times and the offset
    of the nearest surviving tracer label's proper time (the scope's borrowed clock).
C4  Monte Carlo power of G3-G3 as written and as amended (own model, not tools/g3g3_power.py).
C5  high-pass noise of M_AH in FK and FL16 and its correlation (inputs of C4).
C6  cost estimate of each candidate (cells or ghosted cells times step ratio).
Writes OUTDIR/check_review.json and check_review.png/.pdf.
"""
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TRACK = HERE.parents[2]
sys.path.insert(0, str(TRACK / "flux_tools"))
sys.path.insert(0, str(HERE))
import fluxio  # noqa: E402
import figstyle  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v08/src/athena"
S = Path("/data/haiyangw/nrpic/scratch/D-bh-dress")
BASE_DECK = TRACK / "excguard" / "inputs" / "esflg8.athinput"
FK = S / "D-20261123-022725-a553496"
ESFL = S / "D-20261121-203150-15f2bad"
FL16 = S / "D-20261124-172745-72472ed"
EG8 = S / "D-20261127-233719-db5be88"
DATA = S / "D-20261121-203042-82deeec"


# ---------------------------------------------------------------- C1 decks and block counts
def set_key(text, block, key, value):
    pat = re.compile(r"(<%s>[^<]*?\n)(%s\s*=\s*)([^\n#]*)" % (re.escape(block), re.escape(key)), re.S)
    new, n = pat.subn(lambda m: m.group(1) + m.group(2) + str(value), text, count=1)
    if n != 1:
        raise SystemExit(f"{block}/{key} not found")
    return new


def add_region8(text, half):
    reg = (f"\n<refined_region6>\nlevel = 8\nx1min = {-half}\nx1max = {half}\nx2min = {-half}\n"
           f"x2max = {half}\nx3min = {-half}\nx3max = {half}\n")
    i = text.index("<refined_region5>")
    j = text.index("\n<", i + 1)
    return text[:j] + "\n" + reg + text[j:]


def deck_variants():
    base = BASE_DECK.read_text()
    out = {}

    def mk(name, root=None, nb=None, half8=None):
        t = base
        if root:
            for ax in ("nx1", "nx2", "nx3"):
                t = set_key(t, "mesh", ax, root)
        if nb:
            for ax in ("nx1", "nx2", "nx3"):
                t = set_key(t, "meshblock", ax, nb)
        if half8:
            t = add_region8(t, half8)
        t = set_key(t, "job", "basename", name)
        out[name] = ("# g3/amend deck %s (tools/check_review.py) from excguard/inputs/esflg8.athinput: "
                     "root %s, block %s, level-8 half width %s; mesh structure only\n" % (name, root, nb, half8)) + t

    mk("g8")                                 # G-8 = EG8's deck
    mk("g16c", half8=5.9)                    # G-16 as written (cascade)
    mk("g16r", half8=1.4)                    # FL16's form: level 8 over +-3 M
    mk("g16b", nb=12, half8=5.9)             # blocks of 12
    mk("g12u", root=144, nb=36)              # uniform family, 2/3
    mk("g16u", root=192, nb=48)              # uniform family, 1/2
    mk("g12s", root=144, nb=18)              # 2/3 with blocks of 18
    mk("g12c", root=144)                     # G-12 as written (blocks of 24)
    return out


def count_blocks(name, text, outdir):
    d = outdir / "decks" / name
    d.mkdir(parents=True, exist_ok=True)
    deck = d / f"{name}.athinput"
    deck.write_text(text)
    with open(d / "athena.log", "w") as log:
        rc = subprocess.run([EXE, "-i", str(deck), "-m"], cwd=d, stdout=log, stderr=subprocess.STDOUT,
                            env={"OMP_NUM_THREADS": "1", "PATH": "/usr/bin:/bin"}).returncode
    nroot = int(re.search(r"<mesh>.*?\nnx1\s*=\s*(\d+)", text, re.S).group(1))
    nb = int(re.search(r"<meshblock>\s*\nnx1\s*=\s*(\d+)", text).group(1))
    nrbx = nroot // nb
    lroot = int(math.ceil(math.log2(nrbx)))
    ms = (d / "mesh_structure.dat").read_text()
    recs = [tuple(int(g) for g in m.groups()) for m in
            re.finditer(r"Logical level (\d+), location = \((-?\d+) (-?\d+) (-?\d+)\)", ms)]
    lev = Counter(r[0] - lroot for r in recs)
    w0 = 1536.0 / nrbx
    ext = {}
    for L in sorted(lev):
        xs = [r[1] for r in recs if r[0] - lroot == L]
        w = w0 / 2 ** L
        ext[L] = (-768.0 + min(xs) * w, -768.0 + (max(xs) + 1) * w)
    n = sum(lev.values())
    finest = max(lev)
    return dict(returncode=rc, root_nx=nroot, block_nx=nb, n_blocks=n,
                by_level={str(k): lev[k] for k in sorted(lev)},
                extent_by_level={str(k): ext[k] for k in sorted(ext)},
                finest_dx=w0 / nb / 2 ** finest, finest_half_width=ext[finest][1],
                cells=n * nb ** 3, ghosted=n * (nb + 8) ** 3)


# ---------------------------------------------------------------- C2 finder masses at t = 0
def t0_mass(run, base):
    p = run / f"{base}.horizon_summary_0.txt"
    h = fluxio.read_horizon(p)
    i = int(np.argmin(h["time"]))
    return dict(time=float(h["time"][i]), mass=float(h["mass"][i]), offset_from_1=float(h["mass"][i] - 1.0))


# ---------------------------------------------------------------- C3 borrowed clock
def clock_check(snapnum=8):
    lab = np.load(DATA / "esf_labels.npz")
    R0 = lab["R0"]
    sn = fluxio.read_snapshot(FK / f"esflk.part.{snapnum:05d}.bin")
    tag, tau = sn["tag"], sn["tau"]
    tr = tag < 140
    trR0, trtau = R0[tag[tr]], tau[tr]
    labels = np.unique(trR0)
    ltau = np.array([np.median(trtau[trR0 == L]) for L in labels])
    dust = ~tr
    r0, td = R0[tag[dust]], tau[dust]
    rows = []
    for lo in np.arange(6.0, 52.0, 1.0):
        sel = (r0 >= lo) & (r0 < lo + 1.0)
        if sel.sum() < 400:
            continue
        q5, q50, q95 = np.percentile(td[sel], [5, 50, 95])
        mid = lo + 0.5
        k = int(np.argmin(np.abs(labels - mid)))
        rows.append(dict(R0_lo=float(lo), n=int(sel.sum()), tau_median=float(q50), spread_5_95=float(q95 - q5),
                         nearest_label=float(labels[k]), tau_label=float(ltau[k]),
                         offset_label_minus_median=float(ltau[k] - q50)))
    return dict(snapshot_time=float(sn["time"]), tracer_labels_present=labels.tolist(), bins=rows)


# ---------------------------------------------------------------- C5 noise of M_AH
def noise_check():
    a = fluxio.read_horizon(FK / "esflk.horizon_summary_0.txt")
    b = fluxio.read_horizon(FL16 / "esfl16.horizon_summary_0.txt")
    tg = np.arange(50.0, 295.0, 0.5)
    ma = np.interp(tg, a["time"], a["mass"])
    mb = np.interp(tg, b["time"], b["mass"])

    def hp(m, w=40):
        out = np.empty_like(m)
        for i in range(m.size):
            j0, j1 = max(0, i - w // 2), min(m.size, i + w // 2 + 1)
            out[i] = m[i] - np.median(m[j0:j1])
        return out

    ra, rb = hp(ma), hp(mb)
    d = mb - ma
    return dict(t=[50.0, 295.0], sd_hp_fk=float(ra.std()), sd_hp_fl16=float(rb.std()),
                corr_hp=float(np.corrcoef(ra, rb)[0, 1]),
                diff_mean_250_295=float(d[tg >= 250].mean()), sd_hp_diff=float(hp(d).std()),
                series=dict(t=tg[::4].tolist(), fk=ma[::4].tolist(), fl16=mb[::4].tolist()))


# ---------------------------------------------------------------- C4 power of G3-G3
def ar1(rng, n, nt, phi):
    z = rng.standard_normal((n, nt))
    if phi == 0.0:
        return z
    x = np.empty_like(z)
    x[:, 0] = z[:, 0]
    s = math.sqrt(1 - phi * phi)
    for i in range(1, nt):
        x[:, i] = phi * x[:, i - 1] + s * z[:, i]
    return x


def power(A, p, tau_c, sigma=3.9e-4, rho=0.83, ntrial=2000, seed=11):
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, 400.0 + 1e-9, 0.5)
    nt = t.size
    phi = math.exp(-0.5 / tau_c) if tau_c > 0 else 0.0
    h = np.array([1 / 8, 1 / 12, 1 / 16])
    C = A / (h[0] ** p - h[2] ** p) if A > 0 else 0.0
    ramp = np.clip((t - 20.0) / 80.0, 0.0, 1.0)
    sig = [C * hh ** p * ramp for hh in h]
    zc = ar1(rng, ntrial, nt, phi)
    mem = [sigma * (math.sqrt(rho) * zc + math.sqrt(1 - rho) * ar1(rng, ntrial, nt, phi)) + s for s in sig]
    i20 = int(np.searchsorted(t, 20.0))
    a2040 = (t >= 20.0) & (t <= 40.0)
    late = t >= 100.0
    # written form: single-sample anchor at 20 M, max |D| per 50 M window
    dm = [m - m[:, i20:i20 + 1] for m in mem]
    d812, d1216 = dm[0] - dm[1], dm[1] - dm[2]
    ok = np.ones(ntrial, bool)
    for w0 in range(100, 400, 50):
        sel = (t >= w0) & (t < w0 + 50)
        e1 = np.abs(d812[:, sel]).max(axis=1)
        e2 = np.abs(d1216[:, sel]).max(axis=1)
        r = e1 / e2
        ok &= (e1 > e2) & (r >= 1.5) & (r <= 8.0)
    p_written = float(ok.mean())
    # amended form: anchor = mean over 20-40 M, means over 100-400 M, 90 per cent interval of the ratio
    am = [m - m[:, a2040].mean(axis=1, keepdims=True) for m in mem]
    D1 = (am[0] - am[1])[:, late].mean(axis=1)
    D2 = (am[1] - am[2])[:, late].mean(axis=1)
    # noise of the two means (and their covariance) from noise-only realizations of the same model
    zc0 = ar1(rng, 1000, nt, phi)
    n0 = [sigma * (math.sqrt(rho) * zc0 + math.sqrt(1 - rho) * ar1(rng, 1000, nt, phi)) for _ in range(3)]
    n0 = [m - m[:, a2040].mean(axis=1, keepdims=True) for m in n0]
    N1 = (n0[0] - n0[1])[:, late].mean(axis=1)
    N2 = (n0[1] - n0[2])[:, late].mean(axis=1)
    cov = np.cov(np.vstack([N1, N2]))
    L = np.linalg.cholesky(cov + 1e-30 * np.eye(2))
    eps = (L @ rng.standard_normal((2, 400))).T
    ok2 = np.zeros(ntrial, bool)
    for k in range(ntrial):
        r = (D1[k] - eps[:, 0]) / (D2[k] - eps[:, 1])
        lo, hi = np.percentile(r, [5, 95])
        ok2[k] = (lo >= 1.2) and (hi <= 8.0) and np.all(D2[k] - eps[:, 1] > 0)
    return p_written, float(ok2.mean()), float(math.sqrt(cov[0, 0])), float(math.sqrt(cov[1, 1]))


# ---------------------------------------------------------------- main
def main():
    outdir = Path(sys.argv[1])
    res = {}
    # C1
    blocks = {name: count_blocks(name, txt, outdir) for name, txt in deck_variants().items()}
    g8 = blocks["g8"]
    for b in blocks.values():
        b["cells_over_g8"] = b["cells"] / g8["cells"]
        b["ghosted_over_g8"] = b["ghosted"] / g8["ghosted"]
        b["steps_over_g8"] = g8["finest_dx"] / b["finest_dx"]
        # C6 cost to 400 M: mesh part x (cells or ghosted) x steps + particle part x steps
        lo = 1.71 * b["cells_over_g8"] * b["steps_over_g8"] + 0.163 * b["steps_over_g8"]
        hi = 2.54 * b["ghosted_over_g8"] * b["steps_over_g8"] + 0.37 * b["steps_over_g8"]
        b["cost_400M_card_hours"] = [lo, hi]
    res["C1_blocks"] = blocks
    print(json.dumps({k: (v["n_blocks"], v["finest_dx"], v["finest_half_width"]) for k, v in blocks.items()}))
    # C2
    res["C2_t0"] = {"FK_M8": t0_mass(FK, "esflk"), "ESFL_M8": t0_mass(ESFL, "esfl"),
                    "FL16_M16": t0_mass(FL16, "esfl16"), "EG8_M8_polished": t0_mass(EG8, "esflg8")}
    print(json.dumps(res["C2_t0"]))
    # C3
    res["C3_clock"] = clock_check()
    cb = res["C3_clock"]["bins"]
    print("C3 max spread inside 30 M:", max(r["spread_5_95"] for r in cb if r["R0_lo"] < 30),
          "max |offset|:", max(abs(r["offset_label_minus_median"]) for r in cb))
    # C5
    res["C5_noise"] = noise_check()
    print(json.dumps({k: v for k, v in res["C5_noise"].items() if k != "series"}))
    # C4
    grid = [0.0, 2.9e-4, 5.8e-4, 1.2e-3, 2.4e-3]
    pw = {}
    for p in (1, 2):
        for tc in (0.0, 10.0):
            rows = [power(A, p, tc) for A in grid]
            pw[f"p{p}_tauc{tc:g}"] = dict(A=grid, written=[r[0] for r in rows], amended=[r[1] for r in rows],
                                         sd_mean_D812=rows[0][2], sd_mean_D1216=rows[0][3])
            print(f"p={p} tau_c={tc}:", [(A, round(r[0], 3), round(r[1], 3)) for A, r in zip(grid, rows)])
    res["C4_power"] = pw
    (outdir / "check_review.json").write_text(json.dumps(res, indent=1))

    # figure
    figstyle.use_style()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    names = list(blocks)
    lo = [blocks[n]["cost_400M_card_hours"][0] for n in names]
    hi = [blocks[n]["cost_400M_card_hours"][1] for n in names]
    x = np.arange(len(names))
    ax[0, 0].bar(x, hi, color="0.8", label="upper (ghosted cells, FK-based)")
    ax[0, 0].bar(x, lo, color="C0", label="lower (cells, ES-FL-based)")
    for i, n in enumerate(names):
        ax[0, 0].text(i, hi[i] * 1.05, f"{blocks[n]['n_blocks']}\n1/{1 / blocks[n]['finest_dx']:.0f}, "
                      f"+-{blocks[n]['finest_half_width']:.0f}", ha="center", fontsize=6)
    ax[0, 0].set_xticks(x)
    ax[0, 0].set_xticklabels(names, fontsize=7)
    ax[0, 0].set_ylabel("estimated card-hours to 400 M")
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_title("(a) C1/C6: blocks, finest dx and half width, cost", fontsize=8)
    ax[0, 0].legend(fontsize=6)
    r0 = [r["R0_lo"] + 0.5 for r in cb]
    ax[0, 1].plot(r0, [r["spread_5_95"] for r in cb], "o-", ms=3, label="5-95% spread of own proper times")
    ax[0, 1].plot(r0, [abs(r["offset_label_minus_median"]) for r in cb], "s-", ms=3,
                  label="|tracer-label clock - bin median|")
    ax[0, 1].set_xlabel("label R0 [M]")
    ax[0, 1].set_ylabel("proper time [M]")
    ax[0, 1].set_title(f"(b) C3: FK snapshot t = {res['C3_clock']['snapshot_time']:.0f} M", fontsize=8)
    ax[0, 1].legend(fontsize=6)
    for key, st in (("p2_tauc0", "-"), ("p2_tauc10", "--"), ("p1_tauc0", ":")):
        d = pw[key]
        ax[1, 0].plot(d["A"], d["written"], "o" + st, color="C3", ms=3, label=f"written, {key}")
        ax[1, 0].plot(d["A"], d["amended"], "s" + st, color="C2", ms=3, label=f"amended, {key}")
    ax[1, 0].axvline(5.8e-4, color="0.5", lw=0.7)
    ax[1, 0].set_xlabel("deterministic M/8 - M/16 difference A")
    ax[1, 0].set_ylabel("probability the criterion passes")
    ax[1, 0].set_title("(c) C4: G3-G3 as written and as amended (own Monte Carlo)", fontsize=8)
    ax[1, 0].legend(fontsize=5)
    s = res["C5_noise"]["series"]
    ax[1, 1].plot(s["t"], np.array(s["fl16"]) - np.array(s["fk"]), lw=0.8)
    ax[1, 1].set_xlabel("t [M]")
    ax[1, 1].set_ylabel("M_AH(FL16) - M_AH(FK)")
    ax[1, 1].set_title("(d) C5: M/16 - M/8 at N (unpolished finders)", fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "check_review.png", dpi=150)
    fig.savefig(outdir / "check_review.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
