# Numbers of the lead's documents checked against the run outputs

Written by `note/scripts/ledger.py`. 59 numbers, 54 agree within half a unit of the last printed digit, 5 differ. Where they differ, the files win.

| Id | Document:line | Printed | Recomputed | Agree | What |
|---|---|---|---|---|---|
| c01 | `spec/scope/SCOPE.md:42` | -14.0950 | -14.095 | yes | SR phi0 |
| c02 | `spec/scope/SCOPE.md:42` | 1.73494e-6 | 1.73494e-06 | yes | SR mass |
| c03 | `spec/scope/SCOPE.md:42` | 1.1107e-2 | 0.0111071 | yes | SR eps1 at N* |
| c04 | `spec/scope/SCOPE.md:42` | 0.102682 | 0.102682 | yes | USR dphi/dN at N0 |
| c05 | `spec/scope/SCOPE.md:42` | 9.5902e-6 | 9.5902e-06 | yes | USR H0 |
| c06 | `spec/scope/SCOPE.md:42` | 2.52 | 2.5237 | yes | USR onset (eps2 = 3), lead's integrator |
| c07 | `spec/scope/SCOPE.md:42` | 6.55 | 6.5498 | yes | USR end (eps2 = 3), lead's integrator |
| c08 | `spec/scope/SCOPE.md:42` | 9.7e-13 | 9.71599e-13 | yes | USR minimum eps1 |
| c09 | `spec/scope/SCOPE.md:48` | 1304 | 1304 | yes | SR steps at 256^3, Courant 0.25 |
| c10 | `spec/scope/SCOPE.md:48` | 1630 | 1630 | yes | USR steps at 256^3, Courant 0.25 |
| c11 | `spec/scope/SCOPE.md:196` | 0.36 | 0.363836 | yes | SR card-hours, model, noise once per step |
| c12 | `spec/scope/SCOPE.md:196` | 0.41 | 0.40721 | yes | SR card-hours, model, noise per stage |
| c13 | `spec/scope/SCOPE.md:197` | 0.45 | 0.454795 | yes | USR card-hours, model, per step |
| c14 | `spec/scope/SCOPE.md:197` | 0.51 | 0.509012 | yes | USR card-hours, model, per stage |
| c15 | `spec/scope/SCOPE.md:196` | 20 | 19.6614 | yes | memory of a 256^3 run, GB |
| c16 | `spec/scope/SCOPE.md:191` | 0.15 | 0.646588 | **no** | overhead of field and sources over Z4c (assumed in SCOPE; measured by core) |
| c17 | `spec/scope/SCOPE.md:202` | 0.5 | 0.706136 | **no** | card-hours of one 256^3 SR realisation (upper end), measured throughput |
| c18 | `spec/scope/SCOPE.md:202` | 0.5 | 0.88267 | **no** | card-hours of one 256^3 USR realisation (upper end), measured throughput |
| c19 | `spec/SPEC.md:499` | 0.30 | 0.646588 | **no** | overhead of field and sources over Z4c (assumed in SPEC 11.2; measured by core) |
| c20 | `spec/SPEC.md:304` | 1.3164e-2 | 0.0131639 | yes | USR eps1 at N*, reference run |
| c21 | `spec/SPEC.md:304` | 1.3164e-2 | 0.0131625 | **no** | USR eps1 at N*, lead's integrator |
| c22 | `spec/SPEC.md:306` | 1.350e-2 | 0.0134959 | yes | SR eps1 at N_f |
| c23 | `spec/SPEC.md:306` | 1.008e-12 | 1.0083e-12 | yes | USR eps1 at N_f |
| c24 | `spec/SPEC.md:308` | -2.69e-2 | -0.0268725 | yes | SR eps2 at N_f |
| c25 | `spec/SPEC.md:308` | -2.76e-2 | -0.0276155 | yes | USR eps2 at N_f |
| c26 | `spec/SPEC.md:395` | 1.010 | 1.01041 | yes | SR full power at N_f over the estimate at crossing, lowest mode value |
| c27 | `spec/SPEC.md:395` | 1.012 | 1.01205 | yes | same, highest |
| c28 | `spec/SPEC.md:399` | -0.051 | -0.0508918 | yes | SR deformed drift per e-fold, smallest magnitude |
| c29 | `spec/SPEC.md:399` | -0.055 | -0.0551558 | yes | SR deformed drift per e-fold, largest magnitude |
| c30 | `spec/SPEC.md:400` | 0.65 | 0.654368 | yes | SR deformed/full at N_f, k = dk |
| c31 | `spec/SPEC.md:400` | 0.79 | 0.793545 | yes | SR deformed/full at N_f, k = 64 dk |
| c32 | `spec/SPEC.md:402` | 8.40 | 8.40165 | yes | USR deformed/full at N_f, k = dk |
| c33 | `spec/SPEC.md:402` | 1.18 | 1.18014 | yes | USR deformed/full, k = 4 dk |
| c34 | `spec/SPEC.md:402` | 1.07 | 1.06739 | yes | USR deformed/full, k = 5.7 dk |
| c35 | `spec/SPEC.md:403` | 1.003 | 1.00279 | yes | USR deformed/full, k = 11.3 dk |
| c36 | `spec/SPEC.md:404` | 1.017 | 1.01676 | yes | USR full power at N_f, k = 64 dk |
| c37 | `spec/SPEC.md:398` | 2.5e-4 | 0.0002533 | yes | SR full drift magnitude, smallest |
| c38 | `spec/SPEC.md:398` | 1.9e-3 | 0.00188775 | yes | SR full drift magnitude, largest |
| c39 | `spec/SPEC.md:367` | 1.0805 | 1.08049 | yes | SR lattice sum over continuum, band dk-64 dk |
| c40 | `spec/SPEC.md:370` | 0.42 | 0.423314 | yes | excess variance at sigma = 1, USR |
| c41 | `spec/SPEC.md:370` | 0.45 | 0.449231 | yes | excess variance at sigma = 1, SR |
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

Inputs (sha256 checked against the run manifests where recorded):

- `E-20261115-135532-3f958a1/bg/lead_bg.json` b12c9c960206ff1a... (manifest)
- `E-20261115-140116-87c1cc5/cost.json` a73db10925fbe980... (manifest)
- `E-20261115-140116-87c1cc5/d2.json` c6845abe4e6844d1... (manifest)
- `E-20261115-140502-2957846/val_frozen/validation.json` 26e80d92dd2fb4a7... (manifest)
- `E-20261115-140502-2957846/val_markov_heaviside/validation.json` b0684e18882f942e... (manifest)
- `E-20261115-140502-2957846/val_markov_tanh/validation.json` 3eb4e982acf26a0a... (manifest)
- `E-20261115-172423-5234cce/val_cf/validation.json` 99bbdb992d370e3f... (manifest)
- `E-20261115-172423-5234cce/val_std/validation.json` 09c344d70c2baa86... (manifest)
- `E-stoch-inf-20261115-122806-ef0d039/inflection.npz` a376e88d7b3da787... (manifest)
- `E-stoch-inf-20261115-122806-ef0d039/quadratic.npz` 6fb64b63ff9455c3... (manifest)
- `E-stoch-inf-20261115-122806-ef0d039/summary.json` 2f9f21ae2235b928... (manifest)
- `E-stoch-inf-20261115-130137-176cdd6/ref_inflection.json` e8becdd6c5358e9a... (manifest)
- `E-stoch-inf-20261115-130139-176cdd6/ref_quadratic.json` 6b3b748896b44e20... (manifest)
- `core-20261115-143907-cea4c86/summary.json` 7e8c64e1852daf88... (not recorded by the run; read value)
