#!/usr/bin/env python3
"""Test H of the work package "gauge" (tracks/core/JOURNAL-gauge.md): the lapse relaxation
in a homogeneous dust universe, where it reduces to an ordinary differential equation.

With zero shift, dust at rest and H(tau) = H_0/(1 + 3 H_0 tau/2) along the normal
observers (proper time tau, a = (1 + 3 H_0 tau/2)^(2/3)), the condition
    d_t alpha = -2 alpha K - lapse_leak alpha max(ln alpha, 0),   K = -3 H,
gives d ln(alpha)/dt = 6 H(tau) - lapse_leak max(ln alpha, 0), d tau/dt = alpha.
lapse_leak = 0 gives alpha = 1 + 6 ln a exactly.  The run's history (<base>.nrpic.hst:
alpha_min, alpha_max, proper volume, mean K) is compared with that solution, integrated
here with a fine fourth-order Runge-Kutta step.

    flrw_leak.py --exe ATHENA [--out DIR] [--rates 0,20,5] [--name N] [--extra ARGS...]

Runs problems/cosmo/flrw_leak.athinput once per rate in DIR/rate<r>/ (particles from
cosmo/ic/make_lattice.py), writes DIR/flrw_leak_numbers.json and the figure
tracks/core/analysis/gauge/figs/flrw_leak.png|pdf.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

INPUT = os.path.join(WT, "problems/cosmo/flrw_leak.athinput")
H0, L = 1.0, 4.0


def hst(path):
    with open(path) as f:
        names = None
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                names = [tok.split("=")[1] for tok in line[1:].split() if "=" in tok]
    data = np.loadtxt(path)
    return {n: data[:, i] for i, n in enumerate(names)}


def reference(rate, tmax, dt=1.0e-4):
    """(t, alpha, a) of the homogeneous solution, RK4 in coordinate time."""
    def rhs(y):
        la, tau = y
        H = H0 / (1.0 + 1.5 * H0 * tau)
        return np.array([6.0 * H - rate * max(la, 0.0), np.exp(la)])
    n = int(round(tmax / dt))
    y = np.array([0.0, 0.0])
    out = [(0.0, 1.0, 1.0)]
    for i in range(n):
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        out.append(((i + 1) * dt, np.exp(y[0]), (1.0 + 1.5 * H0 * y[1]) ** (2.0 / 3.0)))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--rates", default="0,20,5")
    ap.add_argument("--name", default="flrw_leak", help="name of the figure and numbers")
    ap.add_argument("--extra", nargs="*", default=[], help="more athena arguments")
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run under nrpic-run (NRPIC_RUN_DIR)")
    os.makedirs(a.out, exist_ok=True)
    rates = [float(r) for r in a.rates.split(",")]
    numbers = {}
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.32)
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"], fs.PAL["yellow"]]
    for rate, c in zip(rates, cols):
        d = os.path.join(a.out, f"rate{rate:g}")
        os.makedirs(d, exist_ok=True)
        subprocess.run([sys.executable, os.path.join(WT, "cosmo/ic/make_lattice.py"),
                        "--n", "32", "--ppc", "1", "--L", repr(L), "--H0", repr(H0),
                        "--out", d], check=True, capture_output=True)
        with open(os.path.join(d, "athena.log"), "w") as log:
            rc = subprocess.run([a.exe, "-i", INPUT, "-d", d, f"z4c/lapse_leak={rate!r}"] + a.extra,
                                cwd=d, stdout=log, stderr=subprocess.STDOUT).returncode
        if rc != 0:
            sys.exit(f"athena failed for rate {rate} (exit {rc}); see {d}/athena.log")
        h = hst(os.path.join(d, "flrwleak.nrpic.hst"))
        t = h["time"]
        ref = reference(rate, float(t[-1]))
        al_ref = np.interp(t, ref[:, 0], ref[:, 1])
        a_ref = np.interp(t, ref[:, 0], ref[:, 2])
        a_num = (h["proper_volume"] / L ** 3) ** (1.0 / 3.0)
        e_al = np.abs(h["alpha_max"] / al_ref - 1.0)
        e_a = np.abs(a_num / a_ref - 1.0)
        spread = np.abs(h["alpha_max"] - h["alpha_min"])
        numbers[f"{rate:g}"] = dict(
            T=(1.0 / rate if rate > 0 else None), t_end=float(t[-1]),
            alpha_end=float(h["alpha_max"][-1]), alpha_ref_end=float(al_ref[-1]),
            a_end=float(a_num[-1]), a_ref_end=float(a_ref[-1]),
            max_rel_err_alpha=float(e_al.max()), max_rel_err_a=float(e_a.max()),
            max_alpha_spread=float(spread.max()),
            plain_1log_end=float(1.0 + 6.0 * np.log(a_ref[-1])))
        lab = "plain 1+log" if rate == 0 else r"$T=%g/H_0$" % (1.0 / rate)
        ax[0].plot(t, h["alpha_max"], color=c, label=lab)
        ax[0].plot(ref[:, 0], ref[:, 1], color="k", ls=":", lw=0.8)
        ax[1].semilogy(t[1:], np.maximum(e_al[1:], 1e-16), color=c)
        ax[1].semilogy(t[1:], np.maximum(e_a[1:], 1e-16), color=c, ls="--")
        print(f"rate {rate:g}: alpha(t_end) {numbers[f'{rate:g}']['alpha_end']:.8f} "
              f"(reference {al_ref[-1]:.8f}), a {a_num[-1]:.8f} ({a_ref[-1]:.8f}); "
              f"largest relative error alpha {e_al.max():.2e}, a {e_a.max():.2e}; "
              f"alpha_max - alpha_min {spread.max():.1e}")
    ax[0].plot([], [], color="k", ls=":", lw=0.8, label="exact (ODE)")
    ax[0].set_xlabel(r"coordinate time $t\,H_0$", labelpad=-2)
    ax[0].set_ylabel(r"lapse $\alpha$")
    ax[0].legend(fontsize=7)
    ax[1].plot([], [], color="k", label=r"$\alpha$")
    ax[1].plot([], [], color="k", ls="--", label=r"$a$")
    ax[1].legend(fontsize=7)
    ax[1].set_xlabel(r"coordinate time $t\,H_0$", labelpad=-2)
    ax[1].set_ylabel("relative difference from the exact solution")
    fs.save(fig, os.path.join(HERE, "figs", a.name))
    with open(os.path.join(a.out, a.name + "_numbers.json"), "w") as f:
        json.dump(numbers, f, indent=1)
        f.write("\n")
    with open(os.path.join(HERE, a.name + "_numbers.json"), "w") as f:
        json.dump(numbers, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
