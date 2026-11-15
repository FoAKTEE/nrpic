#!/usr/bin/env python3
"""T-N8: the adapter to core's output (NRSFDMP1 dumps of `<scalar_field> noise = power`).

    python3 dump_selftest.py --out DIR

Writes reference fields of core's power model (frozen increments and Markov increments,
two fields xi_0 and xi_1, noise_pi_dof 1 and 0) as NRSFDMP1 dumps in the layout documented
in `athenak/src/scalar_field/scalar_field_io.cpp` (branch core/scalar-field, lines 12-17)
together with an AthenaK input file, reads them back with athenak_io.read_run(dir, input)
and runs the validation. Cases: frozen (8 and 1 MeshBlocks), Markov with noise_t0 and
noise_tilt set, frozen with a shared degree of freedom, and a mutant whose MeshBlocks are
written under exchanged logical locations. Writes dump_selftest.json, summary.txt and
figures.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ref"))
import noise_ref as nr                                    # noqa: E402
import validate_noise as vn                               # noqa: E402
import athenak_io as aio                                  # noqa: E402
import selftest as stt                                    # noqa: E402


def write_input(path, p):
    lines = ["<job>", "basename = sfnoise", f"rng_seed = {p['seed']}", "<mesh>"]
    for d in ("1", "2", "3"):
        lines += [f"nx{d} = {p['N']}", f"x{d}min = {p['x0']!r}", f"x{d}max = {p['x0'] + p['L']!r}"]
    lines += ["<scalar_field>", "noise = power", f"noise_scheme = {p['scheme']}",
              f"noise_window = {p['window']}", f"noise_sharpness = {p['sharpness']!r}",
              f"noise_nmax2 = {p['nmax2']}", f"noise_amp = {p['amp']!r}",
              f"noise_tilt = {p.get('tilt', 0.0)!r}", f"noise_ksigma0 = {p['ksigma0']!r}",
              f"noise_hubble = {p['hubble']!r}", f"noise_t0 = {p.get('t0w', 0.0)!r}",
              f"noise_pi_dof = {p['pi_dof']}", "dump_dcycle = 100"]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_dump(path, noise, N, x0, L, nb, cycle, time, swap=False):
    """NRSFDMP1: 10 matter/metric fields (zero here) and the noise fields; MeshBlocks of
    (N/nb)^3 cells; swap=True writes the data of blocks (0,0,0) and (1,0,0) under each
    other's logical location (mutant)."""
    b = N // nb
    h = L / N
    nnoise = len(noise)
    nvar = 10 + nnoise
    with open(path, "wb") as f:
        f.write(b"NRSFDMP1")
        f.write(np.array([nb**3, b, b, b, nvar, cycle, nnoise], dtype="<i8").tobytes())
        f.write(np.array([time], dtype="<f8").tobytes())
        for lz in range(nb):
            for ly in range(nb):
                for lx in range(nb):
                    sx = lx
                    if swap and ly == 0 and lz == 0 and lx in (0, 1):
                        sx = 1 - lx                 # data of the other block
                    f.write(np.array([0, lx, ly, lz], dtype="<i8").tobytes())
                    ext = [x0 + lx * b * h, x0 + (lx + 1) * b * h, x0 + ly * b * h,
                           x0 + (ly + 1) * b * h, x0 + lz * b * h, x0 + (lz + 1) * b * h]
                    f.write(np.array(ext, dtype="<f8").tobytes())
                    zero = np.zeros((b, b, b))
                    for v in range(nvar):
                        if v < 10:
                            blk = zero
                        else:
                            blk = noise[v - 10][sx * b:(sx + 1) * b, ly * b:(ly + 1) * b,
                                                lz * b:(lz + 1) * b]
                        f.write(np.ascontiguousarray(np.transpose(blk, (2, 1, 0)))
                                .astype("<f8").tobytes())


def make_case(out, name, p, nb, swap=False):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    run = stt.emulate(p)
    name1 = "stoch_c2" if p["pi_dof"] == 1 else "stoch_c1"
    N = p["N"]
    write_dump(os.path.join(d, "sfnoise.sf.00000.dump"), [np.zeros((N,) * 3)] * 2, N,
               p["x0"], p["L"], nb, 0, 0.0)
    for k, cyc in enumerate(sorted(run["outputs"])):
        o = run["outputs"][cyc]
        write_dump(os.path.join(d, f"sfnoise.sf.{k + 1:05d}.dump"),
                   [o["fields"]["stoch_c0"], o["fields"][name1]], N, p["x0"], p["L"], nb,
                   cyc, cyc * p["dt"], swap)
    inp = os.path.join(d, "sfnoise.athinput")
    write_input(inp, p)
    return d, inp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    base = nr.default_params(frozen_form="increment", phase1=0.0, pi_dof=1,
                             cycles=(100, 200, 300))
    cases = {
        "frozen_pidof1_8mb": (dict(base), 2, False),
        "frozen_pidof1_1mb": (dict(base), 1, False),
        "markov_pidof1_t0_tilt": (dict(base, scheme="markov", t0w=0.2, tilt=-0.04), 2, False),
        "frozen_pidof0": (dict(base, pi_dof=0), 2, False),
        "mutant_swapped_blocks": (dict(base), 2, True),
    }
    runs, report = {}, {}
    for name, (p, nb, swap) in cases.items():
        d, inp = make_case(a.out, name, p, nb, swap)
        run = aio.read_run(d, inp)
        runs[name] = run
        res, data, an = vn.validate_single(run)
        if name in ("frozen_pidof1_8mb", "mutant_swapped_blocks"):
            vn.plot_validation(data, an, a.out, "dump_" + name)
        report[name] = dict(
            failed=sorted(r["id"] for r in res if r["passed"] is False),
            not_applicable=sorted(r["id"] for r in res if r["passed"] is None),
            mapped_params={k: run["params"][k] for k in ("seed", "scheme", "nmax2", "N", "L",
                                                         "x0", "dt", "t0w", "tilt", "pi_dof")},
            results=res)
        print(name, "failed", report[name]["failed"], "n/a", report[name]["not_applicable"],
              flush=True)
    a11 = vn.compare_fields(runs["frozen_pidof1_1mb"], runs["frozen_pidof1_8mb"], "A11",
                            "1 against 8 MeshBlocks", "bitwise")
    a11m = vn.compare_fields(runs["frozen_pidof1_1mb"], runs["mutant_swapped_blocks"], "A11",
                             "1 against swapped", "bitwise")
    report["A11 1 vs 8"] = a11
    report["A11 1 vs swapped"] = a11m
    ok = (all(not report[n]["failed"] for n in cases if not n.startswith("mutant"))
          and a11["passed"] and {"A1"} <= set(report["mutant_swapped_blocks"]["failed"])
          and a11m["passed"] is False)
    report["prediction_holds"] = bool(ok)
    with open(os.path.join(a.out, "dump_selftest.json"), "w") as f:
        json.dump(report, f, indent=1, default=float)
    summ = "; ".join(f"{n}: failed {report[n]['failed']}" for n in cases) + \
        f"; A11 1 vs 8: {a11['passed']}; A11 vs swapped: {a11m['passed']}; holds {ok}"
    with open(os.path.join(a.out, "summary.txt"), "w") as f:
        f.write(summ + "\n")
    print(summ)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(aio.REPO, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    good, bad = runs["frozen_pidof1_8mb"], runs["mutant_swapped_blocks"]
    p = good["params"]
    lat = nr.Lattice(p["N"], p["L"], p["nmax2"])
    ref = nr.reference_outputs(lat, p, [200], comps=(0,), with_acc=False)
    fref, _ = nr.synthesise(lat, ref[("stoch_c0", 200)])
    rms = np.sqrt(np.mean(fref**2))
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.7))
    k = 5
    ext = [p["x0"], p["x0"] + p["L"], p["x0"], p["x0"] + p["L"]]
    im0 = ax[0].imshow(good["outputs"][200]["fields"]["stoch_c0"][:, :, k].T / rms,
                       origin="lower", extent=ext, cmap=fs.CMAP["diverging"], vmin=-3, vmax=3)
    ax[0].set_title(r"read $\xi_0/{\rm rms}$, cycle 200", fontsize=9)
    e1 = (good["outputs"][200]["fields"]["stoch_c0"] - fref)[:, :, k].T / rms
    im1 = ax[1].imshow(e1 / 1e-15, origin="lower", extent=ext, cmap=fs.CMAP["diverging"],
                       vmin=-5, vmax=5)
    ax[1].set_title(r"read $-$ reference, $10^{-15}$ rms", fontsize=9)
    e2 = (bad["outputs"][200]["fields"]["stoch_c0"] - fref)[:, :, k].T / rms
    im2 = ax[2].imshow(e2, origin="lower", extent=ext, cmap=fs.CMAP["diverging"], vmin=-3,
                       vmax=3)
    ax[2].set_title("swapped MeshBlocks $-$ reference", fontsize=9)
    for x in ax:
        x.set_xlabel("x")
    ax[0].set_ylabel("y")
    fs.side_colorbar(fig, ax[0], im0, "")
    fs.side_colorbar(fig, ax[1], im1, "")
    fs.side_colorbar(fig, ax[2], im2, "")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_dump_selftest"))


if __name__ == "__main__":
    main()
