# G1 of E-stoch-inf: each criterion, met or not (lead of batch 2a, 2026-11-21)

Criteria: the track sheet (brief 798, charter 9.8: "the power spectrum of the slow-roll case
agrees with the analytic result, super-horizon modes freeze by the criterion of
arXiv:2606.14853, the constraints converge"), the common G1 row (charter 9.2), and the
owner's thresholds A1-A7 of `../../spec/scope/SCOPE.md` section 4, accepted by decision 0013
(0017). Evidence: runs of the slow-roll (SR) case with core's tested-branch executable
`core/scalar-2` a58e95b (scouting, decision 0013); scalar-2 is in release core-v0.4 since
2026-11-21 and the release processor build reproduces it at 32^3 (`../REVIEW-wave3.md`
section 3, LR1). Details and runs: `EVIDENCE.md`; missing: `OPEN.md`; the fresh-context
verifier: `VERIFIER.md` (helper g1verify, all from the raw dumps with its own code).

**Plainly: G1 is not met.** Spectrum and freezing are met and confirmed by the verifier; the
constraints converge in the sense of the track sheet (confirmed by the verifier), but the
owner's accepted A4 fails in its strict form in P1's set-up and the orchestrator has not ruled
on A4' (request repeated with the verifier's evidence); and four products are missing (updated
architecture and data-flow schematics, one script per data figure, the G1 sections of the
note: package `note`, cut on 2026-11-20 and not finished). The package is therefore not
complete for the independent gate review of decision 0016 item 4, although its verifier
report now exists.

| Criterion | Met? | Evidence | Missing, and who |
|---|---|---|---|
| Track: SR power spectrum agrees with the analytic result (A2: every mode with k <= k_max/2 within 2 percent of W R alpha at N_f) | yes, verified | P256 (256^3, P1's set-up): 1.21e-4 over 68532 modes with |n| <= 32 (track and verifier agree to three digits); second seed 2.12e-4 (set by a mode with |alpha| = 6.5e-4 of the rms; 1.208e-4 over typical amplitudes); rungs 1.7e-6 to 9.9e-5; shell spectrum 1.0104-1.0116 x the slow-roll formula (the slow-roll correction, which the full MS gives too) (runs E-20261115-172618-f948386, -194633-9e04ed8, E-20261121-032828-fe18c5f, -045105-f797ebb; verifier E-20261121-030207-fb6f090; lead LW1) | none |
| Track: super-horizon modes freeze by the criterion of arXiv:2606.14853 (A3: drift after N_k + 4 below 2.5e-3 per e-fold, ratio equal to full MS within 1 percent) | yes, verified | 1051 modes per rung: ratio within 2.4e-6 to 4.6e-6 of the full MS (the range is the choice of the dump taken as N_k + 4: verifier and track), drift 1.38e-4 per e-fold; FLRW-lattice drift -0.052 per e-fold excluded by 1e4-1e5; second seed 4.4e-6 (runs as above) | none |
| Track: the constraints converge (A5: order 4-6 on N = 32, 64, 128 with k_max/dk = 8, before the floor) | yes, verified, with a caveat | odd (first-order, discretisation) part of H at order 5.54-5.64 (32 -> 64), 5.2-5.9 in band (64 -> 128), 5.8-5.96 in band (128 -> 256); halving 1.9989-2.0000; even (second-order) part halving 3.986-4.000 and independent of N (2.2 percent 64/128 raw; 0.8 percent 128/256 after each run's floor is removed); uniform residual H0 at order 4.1 in the step (verifier E-20261121-031951-82984f8, -030522-c6907b6; ladder E-20261115-194633-9e04ed8, E-20261119-142713-32c883a) | caveat: "before the floor" made operational after the data (A5'); the floor (N^2.45-2.51) is attributed to rounding by measured properties plus judgement |
| Owner's A4: H/[H], M/[M] of second order during the entry, sign-flip control first order | no, in P1's set-up (k_max = N/4); yes in the L set-up from N = 128 | the odd part of H exceeds the even part from ln(N/8) e-folds after N*: up to 745, 655, 869 at N = 32, 64, 128 and 25 at N = 256 at the last time-matched dump (N = 3.93; the P256 peak at N = 4.4 has no time-matched partner; the earlier "385" paired dumps 0.0038 apart, `ladder/results/final2/`); record maxima <|H|/[H]> 4.7-5.1e-11 (within 10 x P1's 1e-10), <|M|/[M]> 3.7-4.0e-4; negative control: record ratio up to 4e4-1.5e5 during the early entry, odd-part ratio at least 89-179 at the end of the entry, ratio of the maxima 1709-1874; core explains the first-order part (Bianchi defect of the stencils, `scalar_field_3.md` 4) | orchestrator: ruling on A4' (outbox `20261121T*__to-orch__a4-ruling-with-verifier.md`; the verifier recommends A4' with (d) on maxima and the floor named as the non-scaling part) |
| Recommended A1 background | yes, verified | box means within 2.0e-12 (phi, P256), 8.6e-12 (Pi), 3.6e-12 (K, L32p) of the Friedmann reference on every rung, threshold 1e-4; e-folds off by 5.5e-6 at N = 32 (RK4 error of chi, order 4.06) | none |
| Recommended A6 temporal order 4 +- 0.5 | yes, verified | N = 32: 3.93-4.10 (fields, R^NR, <H>); N = 64 in P1's set-up: 3.82-4.03 (R^NR, phi, chi, K, <chi>), late-entry odd part of H independent of the Courant factor to 1e-3 (E-20261119-142317-c851f27, E-20261121-025643-02526ff, -034414-bfd0285; verifier -030522-c6907b6; lead LW4) | the second-order part has no resolvable time error (below rounding) |
| Recommended A7 reproducibility | yes, verified | noise bit-identical across 1, 8, 64 MeshBlocks and restart (release core-v0.3 unit test); the G1 executable itself on 8 MeshBlocks and from a restart: all 22 variables bit-identical at 32^3 (verifier E-20261121-031049-27cdc06, -031251-c48670d) | rank count; card build of the G1 executable for layout |
| Common: baseline results without the NRPIC coupling | yes | linear MS references (spec/ref), delta-N references (langevin/), the SR ladder itself (field + Z4c, no particles) | none |
| Common: analysis pipeline validated on them | yes | `analysis/sfa.py` T1-T5; ladder reader bitwise equal to core's; the verifier's independent pipeline (own reader, Philox, MS, R^NR) agrees with the track's numbers to three digits where not explained in VERIFIER.md (nine disagreements above 10 percent, none changes a verdict) | none |
| Common: interface proposals submitted | yes | `noise/NOISE_SPEC.md`, `noise/RNG_REQUIREMENTS.md`, `codebase/DESIGN_REVIEW.md` 9, 11, `spec/SPEC.md` 10; core's answer `scalar_field_2.md`, released in core-v0.4 (`coord/INTERFACES/scalar_field_2.md`) | none |
| Single-kick test L5 (risk R2) | done | H second order (factor 3.99999-4.0000001); kick's projector term = one-step reference within 1.2 percent; remaining first-order M is the fourth-order time error (A/B 15.5-19.5) (E-20261121-034645-02a463e, -040015-436a615; lead LW5, LW6) | none |
| Downgrade test (SCOPE 4 item 5, brief 462) | not triggered | A3 passes; one 256^3 SR realisation costs 0.50 card-hours (two realisations measured: 0.503, 0.501) against 5 | USR at G2 |
