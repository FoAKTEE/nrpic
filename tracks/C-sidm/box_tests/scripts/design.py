#!/usr/bin/env python3
"""Design numbers of the box tests (before any test run): rates, time scales, chosen
cross-sections and steps, and the reference values the predictions quote. Uses only
the track's reference modules (collide/REFERENCES). Writes design.json into
$NRPIC_RUN_DIR and prints it.

Choices (TESTS.md leaves them free):
- T2: sigma such that the largest pair probability of a run is about 0.02 (largest
  Moller speed of 4e6 sampled pairs, times the occupation factor (N_max - 1)/<N> = 1.8
  for Poisson cells of mean 30.5 among 32768); dt such that the rms speed moves a
  particle half a cell (1/64) per step, so that the cell occupations decorrelate within a
  few steps; the sub-cycled variant has sigma x 25 (max P before sub-cycling ~ 0.5).
- T3/T4: sigma = 1, rho_0 = 1, dt = 0.005 tau_rel, 16^3 cells (244 particles per cell:
  core reports a relaxation deficit at few particles per cell, collisions.md section 9).
"""
import json
import os
import sys

import numpy as np

import boxlib as bl  # noqa: F401  (sets the paths)
import mj
import rate
import relax as rx
import entropy as en
import kinematics as kin


def vmol_pairs(theta, n, rng):
    a = mj.sample_u(n, theta, rng)
    b = mj.sample_u(n, theta, rng)
    return kin.vmol(a, b)


def main():
    rng = np.random.default_rng(20261115)
    out = {}
    t2 = {}
    for th in (1e-3, 0.1, 1.0, 10.0):
        v = vmol_pairs(th, 4_000_000, rng)
        u = mj.sample_u(1_000_000, th, rng)
        W = np.sqrt(1 + np.sum(u * u, 1))
        vrms = float(np.sqrt(np.mean(np.sum(u * u, 1) / W ** 2)))
        vmax = float(v.max())
        sdt = 0.02 / (1.8 * vmax)          # sigma * dt for max P ~ 0.02
        dt = (1.0 / 64.0) / vrms
        sig = sdt / dt
        vm = float(rate.vmol_mean(th))
        per_step = 0.5 * 1e6 * 1.0 * sig * vm * dt
        t2[repr(th)] = dict(vmol_mean=vm, vmol_mc=float(v.mean()),
                            vmol_mc_se=float(v.std() / np.sqrt(v.size)), vmol_max_4e6=vmax,
                            v_rms=vrms, dt=dt, sigma=sig, sigma_sub=25 * sig,
                            expected_per_step=per_step,
                            expected_per_step_sub=25 * per_step,
                            expected_total_200=200 * per_step,
                            t_coll=1.0 / (sig * vm))
    out["T2"] = t2
    t34 = {}
    for th2 in (1e-3, 1.0):
        th1 = 3 * th2
        d1, d2 = rx.dtheta_dt(0.5, 0.5, 1.0, th1, th2)
        tau = (th1 - th2) / abs(d1 - d2)
        teq = float(rx.theta_eq(0.5, 0.5, th1, th2))
        smix = float(en.s_mixture(0.5, th1, 0.5, th2))
        seq = float(en.s_mj(1.0, teq))
        nr = float(rx.dT_rate_nr(0.5, 0.5, 1.0, th1, th2))
        t34[repr(th2)] = dict(theta1=th1, theta2=th2, slope_exact=float(d1 - d2),
                              slope_nr=nr, ratio_exact_nr=float((d1 - d2) / nr),
                              tau_rel=float(tau), theta_eq=teq, s_mix=smix, s_eq=seq,
                              gap=seq - smix, dt=0.005 * tau, steps_15tau=3000,
                              t_coll=1.0 / float(rate.vmol_mean(teq)),
                              tau_over_tcoll=float(tau * rate.vmol_mean(teq)))
    out["T3_T4_T5"] = t34
    # T9: classes A (mass M, theta_A = 0.03) and B (4 M, theta_B = 0.01), equal total mass
    thA, thB = 0.03, 0.01
    d1, d2 = rx.dtheta_dt(0.5, 0.5, 1.0, thA, thB)
    out["T9"] = dict(thetaA=thA, thetaB=thB, tau_rel=float((thA - thB) / abs(d1 - d2)),
                     theta_eq=float(rx.theta_eq(0.5, 0.5, thA, thB)))
    # T11: theta = 1, beta = 0.6; make_box's rho0 is the lab rest-mass density
    gb = 1 / np.sqrt(1 - 0.36)
    vm = float(rate.vmol_mean(1.0))
    out["T11"] = dict(theta=1.0, beta=0.6, gamma_b=gb, vmol_mean_rest=vm,
                      rho_rest=1.0 / gb,
                      coll_per_particle_per_lab_time=(1.0 / gb) * vm / gb,
                      t_coll_lab=gb * gb / vm)
    rd = bl.outdir()
    bl.save_json(os.path.join(rd, "design.json"), out)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
