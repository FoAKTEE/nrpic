# Numbers of the lead's documents checked against the run outputs

Written by `note/scripts/ledger.py`. 104 numbers, 97 agree within half a unit of the last printed digit, 7 differ. Where they differ, the files win. c01-c59: G0 documents (SPEC.md, SCOPE.md, G0 EVIDENCE.md, langevin README); g01 on: G1 documents (stage/G1/STATUS.md, ladder/README.md). An integer with trailing zeros counts as rounded to its last nonzero digit.

| Id | Document:line | Printed | Recomputed | Agree | What |
|---|---|---|---|---|---|
| c01 | `spec/scope/SCOPE.md:43` | -14.0950 | -14.095 | yes | SR phi0 |
| c02 | `spec/scope/SCOPE.md:43` | 1.73494e-6 | 1.73494e-06 | yes | SR mass |
| c03 | `spec/scope/SCOPE.md:43` | 1.1107e-2 | 0.0111071 | yes | SR eps1 at N* |
| c04 | `spec/scope/SCOPE.md:43` | 0.102682 | 0.102682 | yes | USR dphi/dN at N0 |
| c05 | `spec/scope/SCOPE.md:43` | 9.5902e-6 | 9.5902e-06 | yes | USR H0 |
| c06 | `spec/scope/SCOPE.md:43` | 2.52 | 2.5237 | yes | USR onset (eps2 = 3), lead's integrator |
| c07 | `spec/scope/SCOPE.md:43` | 6.55 | 6.5498 | yes | USR end (eps2 = 3), lead's integrator |
| c08 | `spec/scope/SCOPE.md:43` | 9.7e-13 | 9.71599e-13 | yes | USR minimum eps1 |
| c09 | `spec/scope/SCOPE.md:49` | 1304 | 1304 | yes | SR steps at 256^3, Courant 0.25 |
| c10 | `spec/scope/SCOPE.md:49` | 1630 | 1630 | yes | USR steps at 256^3, Courant 0.25 |
| c11 | `spec/scope/SCOPE.md:234` | 0.36 | 0.363836 | yes | SR card-hours, model, noise once per step |
| c12 | `spec/scope/SCOPE.md:234` | 0.41 | 0.40721 | yes | SR card-hours, model, noise per stage |
| c13 | `spec/scope/SCOPE.md:235` | 0.45 | 0.454795 | yes | USR card-hours, model, per step |
| c14 | `spec/scope/SCOPE.md:235` | 0.51 | 0.509012 | yes | USR card-hours, model, per stage |
| c15 | `spec/scope/SCOPE.md:234` | 20 | 19.6614 | yes | memory of a 256^3 run, GB |
| c16 | `spec/scope/SCOPE.md:229` | 0.15 | 0.646588 | **no** | overhead of field and sources over Z4c (assumed in SCOPE; measured by core) |
| c17 | `spec/scope/SCOPE.md:240` | 0.5 | 0.706136 | **no** | card-hours of one 256^3 SR realisation (upper end), measured throughput |
| c18 | `spec/scope/SCOPE.md:240` | 0.5 | 0.88267 | **no** | card-hours of one 256^3 USR realisation (upper end), measured throughput |
| c19 | `spec/SPEC.md:518` | 0.30 | 0.646588 | **no** | overhead of field and sources over Z4c (assumed in SPEC 11.2; measured by core) |
| c20 | `spec/SPEC.md:313` | 1.3164e-2 | 0.0131639 | yes | USR eps1 at N*, reference run |
| c21 | `spec/SPEC.md:313` | 1.3164e-2 | 0.0131625 | **no** | USR eps1 at N*, lead's integrator |
| c22 | `spec/SPEC.md:315` | 1.350e-2 | 0.0134959 | yes | SR eps1 at N_f |
| c23 | `spec/SPEC.md:315` | 1.008e-12 | 1.0083e-12 | yes | USR eps1 at N_f |
| c24 | `spec/SPEC.md:317` | -2.69e-2 | -0.0268725 | yes | SR eps2 at N_f |
| c25 | `spec/SPEC.md:317` | -2.76e-2 | -0.0276155 | yes | USR eps2 at N_f |
| c26 | `spec/SPEC.md:407` | 1.010 | 1.01041 | yes | SR full power at N_f over the estimate at crossing, lowest mode value |
| c27 | `spec/SPEC.md:407` | 1.012 | 1.01205 | yes | same, highest |
| c28 | `spec/SPEC.md:411` | -0.051 | -0.0508918 | yes | SR deformed drift per e-fold, smallest magnitude |
| c29 | `spec/SPEC.md:411` | -0.055 | -0.0551558 | yes | SR deformed drift per e-fold, largest magnitude |
| c30 | `spec/SPEC.md:412` | 0.65 | 0.654368 | yes | SR deformed/full at N_f, k = dk |
| c31 | `spec/SPEC.md:412` | 0.79 | 0.793545 | yes | SR deformed/full at N_f, k = 64 dk |
| c32 | `spec/SPEC.md:414` | 8.40 | 8.40165 | yes | USR deformed/full at N_f, k = dk |
| c33 | `spec/SPEC.md:414` | 1.18 | 1.18014 | yes | USR deformed/full, k = 4 dk |
| c34 | `spec/SPEC.md:414` | 1.07 | 1.06739 | yes | USR deformed/full, k = 5.7 dk |
| c35 | `spec/SPEC.md:415` | 1.003 | 1.00279 | yes | USR deformed/full, k = 11.3 dk |
| c36 | `spec/SPEC.md:416` | 1.017 | 1.01676 | yes | USR full power at N_f, k = 64 dk |
| c37 | `spec/SPEC.md:410` | 2.5e-4 | 0.0002533 | yes | SR full drift magnitude, smallest |
| c38 | `spec/SPEC.md:410` | 1.9e-3 | 0.00188775 | yes | SR full drift magnitude, largest |
| c39 | `spec/SPEC.md:376` | 1.0805 | 1.08049 | yes | SR lattice sum over continuum, band dk-64 dk |
| c40 | `spec/SPEC.md:379` | 0.42 | 0.423314 | yes | excess variance at sigma = 1, USR |
| c41 | `spec/SPEC.md:379` | 0.45 | 0.449231 | yes | excess variance at sigma = 1, SR |
| c42 | `stage/G0/EVIDENCE.md:38` | 1.0108 | 1.01077 | yes | lead's SR mode: full power at N_f over the slow-roll estimate |
| c43 | `stage/G0/EVIDENCE.md:39` | -5.8e-4 | -0.000584854 | yes | lead's SR mode: full slope |
| c44 | `stage/G0/EVIDENCE.md:40` | -0.0519 | -0.05186 | yes | lead's SR mode: deformed slope |
| c45 | `stage/G0/EVIDENCE.md:40` | -0.0513 | -0.0512552 | yes | lead's SR mode: -4 eps1 |
| c46 | `stage/G0/EVIDENCE.md:40` | 0.70 | 0.699454 | yes | lead's SR mode: deformed/full at N_f |
| c47 | `stage/G0/EVIDENCE.md:42` | 2.08 | 2.07995 | yes | lead's USR mode: deformed/full at N_f |
| c48 | `stage/G0/EVIDENCE.md:115` | 4.1e-14 | 4.11329e-14 | yes | frozen scheme, A1 |
| c49 | `stage/G0/EVIDENCE.md:115` | 2.4e-15 | 2.35588e-15 | yes | frozen scheme, A13 |
| c50 | `stage/G0/EVIDENCE.md:115` | 1.07e-10 | 1.06813e-10 | yes | Markov-tanh scheme, A1 |
| c51 | `langevin/README.md:106` | 3.9248e-10 | 3.92476e-10 | yes | SR linear band variance |
| c52 | `langevin/README.md:106` | 0.79884 | 0.798838 | yes | USR linear band variance |
| c53 | `langevin/README.md:107` | 0.9997 | 0.999734 | yes | USR lattice over continuum |
| c54 | `langevin/README.md:109` | 0.9981 | 0.998111 | yes | SR var/var_lin at sigma = 0.01 |
| c55 | `langevin/README.md:109` | 1.0001 | 1.00011 | yes | USR var/var_lin at sigma = 0.01 |
| c56 | `langevin/README.md:116` | 1.0050 | 1.00501 | yes | SR var/var_lin at sigma = 0.1 |
| c57 | `langevin/README.md:116` | 1.0055 | 1.00555 | yes | USR var/var_lin at sigma = 0.1 |
| c58 | `langevin/README.md:117` | 1.4492 | 1.44923 | yes | SR var/var_lin at sigma = 1 |
| c59 | `langevin/README.md:117` | 1.4233 | 1.42331 | yes | USR var/var_lin at sigma = 1 |
| g01 | `stage/G1/STATUS.md:24` | 1.21e-4 | 0.000120776 | yes | A2, 256^3 paper set-up, max D_n for |n| <= 32 |
| g02 | `stage/G1/STATUS.md:24` | 68532 | 68532 | yes | A2, modes with |n| <= 32 at 256^3 |
| g03 | `stage/G1/STATUS.md:24` | 1.7e-6 | 1.73814e-06 | yes | A2, smallest rung maximum |
| g04 | `stage/G1/STATUS.md:24` | 9.9e-5 | 9.9064e-05 | yes | A2, largest rung maximum (Q128) |
| g05 | `stage/G1/STATUS.md:25` | 1051 | 1051 | yes | A3, modes with N_f - N_k >= 6 |
| g06 | `stage/G1/STATUS.md:25` | 4.6e-6 | 4.57173e-06 | yes | A3 ratio, largest over the rungs |
| g07 | `stage/G1/STATUS.md:25` | 1.38e-4 | 0.000137894 | yes | A3 drift, largest at 256^3 (P256) |
| g08 | `stage/G1/STATUS.md:25` | 0.052 | 0.0519817 | yes | drift of the deformed equation, mean over the A3 shells |
| g09 | `stage/G1/STATUS.md:28` | 2.0e-12 | 1.9994e-12 | yes | A1 phi, largest over every rung |
| g10 | `stage/G1/STATUS.md:28` | 8.6e-12 | 8.55316e-12 | yes | A1 Pi, largest over every rung |
| g11 | `stage/G1/STATUS.md:28` | 3.6e-12 | 3.62865e-12 | yes | A1 K, largest over every rung |
| g12 | `stage/G1/STATUS.md:28` | 5.5e-6 | 5.5223e-06 | yes | A1 e-folds from <chi>, 32^3 |
| g13 | `stage/G1/STATUS.md:27` | 745 | 744.776 | yes | largest odd/even of H, 32^3, time-matched dumps |
| g14 | `stage/G1/STATUS.md:27` | 655 | 654.81 | yes | same, 64^3 |
| g15 | `stage/G1/STATUS.md:27` | 869 | 868.899 | yes | same, 128^3 |
| g16 | `stage/G1/STATUS.md:27` | 25 | 25.146 | yes | same, 256^3 (last time-matched dump) |
| g17 | `stage/G1/STATUS.md:27` | 4e4 | 40270.5 | yes | negative control, record H ratio, smallest of the maxima |
| g18 | `stage/G1/STATUS.md:27` | 1.5e5 | 149323 | yes | negative control, record H ratio, largest |
| g19 | `stage/G1/STATUS.md:26` | 2.2 | 2.15234 | yes | even part, 64^3 against 128^3, percent |
| g20 | `stage/G1/STATUS.md:26` | 4.1 | 4.09995 | yes | order of the uniform residual in the time step (lowest) |
| g21 | `stage/G1/STATUS.md:35` | 0.503 | 0.5031 | yes | card-hours of the 256^3 realisation (manifest) |
| g22 | `ladder/README.md:15` | 1.1e-12 | 1.9994e-12 | **no** | A1 phi, largest over every rung |
| g23 | `ladder/README.md:15` | 2.0e-12 | 3.62865e-12 | **no** | A1 K, largest over every rung |
| g24 | `ladder/README.md:15` | 3.3e-7 | 3.31933e-07 | yes | A1 e-folds from <chi>, 64^3 |
| g25 | `ladder/README.md:15` | 2.0e-8 | 2.0356e-08 | yes | same, 128^3 |
| g26 | `ladder/README.md:16` | 8.8e-5 | 8.76226e-05 | yes | A2, 32^3 rung |
| g27 | `ladder/README.md:16` | 9.7e-5 | 9.72572e-05 | yes | A2, 64^3 paper set-up |
| g28 | `ladder/README.md:17` | 4.6e-6 | 4.57173e-06 | yes | A3 ratio, largest over the rungs |
| g29 | `ladder/README.md:17` | 1.8e-6 | 1.75051e-06 | yes | A3 drift, code minus full equation |
| g30 | `ladder/README.md:18` | 1.9e-4 | 0.000186783 | yes | shell ratio against the reference with the same alpha, all rungs |
| g31 | `ladder/README.md:18` | 1.0104 | 1.01041 | yes | linear spectrum over the slow-roll formula, |n| <= 7, lowest |
| g32 | `ladder/README.md:18` | 1.0109 | 1.0109 | yes | same, highest |
| g33 | `ladder/README.md:21` | 4.2 | 4.20239 | yes | A5 order of the odd part of H, lowest |
| g34 | `ladder/README.md:21` | 5.8 | 5.81784 | yes | A5 order of the odd part of H, highest |
| g35 | `ladder/README.md:21` | 5.6 | 5.55216 | yes | A5 order of the odd part of M, lowest |
| g36 | `ladder/README.md:21` | 5.9 | 5.90915 | yes | A5 order of the odd part of M, highest |
| g37 | `ladder/README.md:22` | 3.93 | 3.9332 | yes | A6 orders, lowest |
| g38 | `ladder/README.md:22` | 4.08 | 4.08078 | yes | A6 orders, highest |
| g39 | `ladder/README.md:27` | 0.20 | 0.204352 | yes | negative control <|M|/[M]>, smallest maximum |
| g40 | `ladder/README.md:27` | 0.22 | 0.215628 | yes | negative control <|M|/[M]>, largest maximum |
| g41 | `ladder/README.md:28` | 1.13 | 1.13049 | yes | seconds per step at 256^3, lowest |
| g42 | `ladder/README.md:28` | 1.30 | 1.2998 | yes | seconds per step at 256^3, highest |
| g43 | `ladder/README.md:180` | 1.51 | 1.50885 | yes | first dump with odd > even, 32^3 |
| g44 | `ladder/README.md:180` | 3.44 | 3.43545 | yes | first dump with odd > even, 256^3 |
| g45 | `ladder/README.md:20` | 25 | 25.146 | yes | time-matched odd/even, 256^3 |

Inputs (sha256 checked against the run manifests where recorded):

- `E-20261115-135532-3f958a1/bg/lead_bg.json` b12c9c960206ff1a... (manifest)
- `E-20261115-140116-87c1cc5/cost.json` a73db10925fbe980... (manifest)
- `E-20261115-140116-87c1cc5/d2.json` c6845abe4e6844d1... (manifest)
- `E-20261115-140502-2957846/val_frozen/validation.json` 26e80d92dd2fb4a7... (manifest)
- `E-20261115-140502-2957846/val_markov_heaviside/validation.json` b0684e18882f942e... (manifest)
- `E-20261115-140502-2957846/val_markov_tanh/validation.json` 3eb4e982acf26a0a... (manifest)
- `E-20261115-171445-36152c4/test_sfa.json` e28f23942f066156... (manifest)
- `E-20261115-172423-5234cce/val_cf/validation.json` 99bbdb992d370e3f... (manifest)
- `E-20261115-172423-5234cce/val_std/validation.json` 09c344d70c2baa86... (manifest)
- `E-20261115-172935-ddfade0/selftest.json` 63e95ebb29587201... (manifest)
- `E-20261115-174214-74becdd/extraction_check.json` 2573f5c6fe663d1d... (manifest)
- `E-20261115-180533-24a7781/val_card_frozen/validation.json` 2dbb2b8b2baf1cc6... (manifest)
- `E-20261115-184748-9b010fa/val_a14/validation.json` 15ed3fcd8eca1e6b... (manifest)
- `E-20261115-194633-9e04ed8/res/L128p.npz` 8d4936d4d5d8fe50... (manifest)
- `E-20261115-194633-9e04ed8/res/L32p.npz` 6a3a436d7462b01e... (manifest)
- `E-20261115-194633-9e04ed8/res/L64p.npz` aaa87332fd763fa5... (manifest)
- `E-20261115-194633-9e04ed8/res/P256_judge.json` 0a2d49c7a5e23171... (manifest (committed copy ladder/results/final/P256_judge.json))
- `E-20261115-194633-9e04ed8/res/pair_L128p_L128m.json` db11951acd26b4ab... (manifest (committed copy ladder/results/final/pair_L128p_L128m.json))
- `E-20261115-194633-9e04ed8/res/pair_L256p_L256m.json` 0d6c13cb404bc153... (manifest (committed copy ladder/results/final/pair_L256p_L256m.json))
- `E-20261115-194633-9e04ed8/res/pair_L32p_L32m.json` 49d29e8e1681b9b9... (manifest (committed copy ladder/results/final/pair_L32p_L32m.json))
- `E-20261115-194633-9e04ed8/res/pair_L64p_L64m.json` e33f559edbe18dca... (manifest (committed copy ladder/results/final/pair_L64p_L64m.json))
- `E-20261115-194633-9e04ed8/res/pair_P256_P256m.json` 6e19710d0228a877... (manifest (committed copy ladder/results/final/pair_P256_P256m.json))
- `E-20261115-194633-9e04ed8/res/pair_Q128p_Q128m.json` 17157c17f52ca90f... (manifest (committed copy ladder/results/final/pair_Q128p_Q128m.json))
- `E-20261115-194633-9e04ed8/res/pair_Q64p_Q64m.json` 85b5c70f410291aa... (manifest (committed copy ladder/results/final/pair_Q64p_Q64m.json))
- `E-20261115-194633-9e04ed8/summary.json` a5f46d0b80352035... (manifest (committed copy ladder/results/final/summary.json))
- `E-20261119-141654-c2a10d1/val_card_a12/validation.json` 3de78d25bc1a85b0... (manifest)
- `E-20261119-141654-c2a10d1/val_proc_a12/validation.json` a9f5e26a8c11ac82... (manifest)
- `E-20261119-142713-32c883a/floor.json` 6900a7082279396c... (manifest (committed copy ladder/results/floor/floor.json))
- `E-20261119-145230-ff0dff2/a6.json` d8298859483862da... (manifest (committed copy ladder/results/a6/a6.json))
- `E-20261119-145230-ff0dff2/a6_modes.npz` a2cf7df5bc142d99... (manifest)
- `E-stoch-inf-20261115-122806-ef0d039/inflection.npz` a376e88d7b3da787... (manifest)
- `E-stoch-inf-20261115-122806-ef0d039/quadratic.npz` 6fb64b63ff9455c3... (manifest)
- `E-stoch-inf-20261115-122806-ef0d039/summary.json` 2f9f21ae2235b928... (manifest)
- `E-stoch-inf-20261115-130137-176cdd6/ref_inflection.json` e8becdd6c5358e9a... (manifest)
- `E-stoch-inf-20261115-130139-176cdd6/ref_quadratic.json` 6b3b748896b44e20... (manifest)
- `core-20261115-143907-cea4c86/summary.json` 7e8c64e1852daf88... (not recorded by the run; read value)
