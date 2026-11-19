# G1 of E-stoch-inf: each criterion, met or not (lead of wave 2b, 2026-11-19)

Criteria: the track sheet (brief 798, charter 9.8: "the power spectrum of the slow-roll case
agrees with the analytic result, super-horizon modes freeze by the criterion of
arXiv:2606.14853, the constraints converge"), the common G1 row (charter 9.2), and the
owner's thresholds A1-A7 of `../../spec/scope/SCOPE.md` section 4, which decision 0013
accepted (accepted by the user with decision 0017). Evidence: scouting runs of the slow-roll
(SR) case with core's tested-branch executable `core/scalar-2` a58e95b (decision 0013), not
a release. Details and runs: `EVIDENCE.md`; what is missing: `OPEN.md`.

**Plainly: G1 is not met.** The SR spectrum and the freezing criterion are met; the
constraints converge in the sense of the track sheet, but the owner's accepted A4 fails in
its strict form in P1's set-up and needs the orchestrator's ruling (proposal A4'); and four
products of the package are missing (updated architecture and data-flow schematics, the G1
sections of the note, a fresh-context verifier of the G1 material). The package is not
complete for the orchestrator's review under decision 0016 item 4 (no verifier of the
later material).

| Criterion | Met? | Evidence | Missing, and who |
|---|---|---|---|
| Track: SR power spectrum agrees with the analytic result (A2: every mode with k <= k_max/2 within 2 percent of W R alpha at N_f) | yes | P256 (256^3, P1's set-up, 548958 modes): max deviation 1.21e-4 for |n| <= 32; ladder rungs 1.7e-6 to 9.9e-5; shell spectrum within 1.9e-4 of the reference with the same alpha_n and 1.0104-1.0109 x H_k^2/(8 pi^2 eps1_k Mpl^2) for |n| <= 7 (runs E-20261115-172618-f948386, -194633-9e04ed8; lead's own code on L32p: 8.76e-5, E-20261119-150238-b81e33f) | none |
| Track: super-horizon modes freeze by the criterion of arXiv:2606.14853 (A3: drift of ln Delta after N_k + 4 below 2.5e-3 per e-fold, equal to full MS within 1 percent) | yes | 1051 modes per rung with N_f - N_k >= 6: ratio within 4.6e-6, drift 1.38e-4 to 1.41e-4 per e-fold equal to full MS within 1.8e-6; the FLRW-lattice drift -4 eps1 = -0.05 excluded by a factor 350 (same runs; lead's code 2.7e-6 and 1.38e-4) | none |
| Track: the constraints converge (A5: order 4-6 on N = 32, 64, 128 with k_max/dk = 8, before the floor) | yes, with a caveat | odd (first-order, discretisation) part of H at order 4.20-5.82 and of M at 5.55-5.91; uniform residual H0 at order 4 in the step (3.12e-12, 1.83e-13, 1.12e-14 at N_f); second-order part independent of N within 2.2 percent (P1's plateau) (runs E-20261115-194633-9e04ed8, E-20261119-142713-32c883a; lead: order 32 -> 64 5.54-5.64 during the entry) | caveat: "before the floor" was made operational after the data were seen (floor growing as N^2.5, factor 3), proposal A5' to orch |
| Owner's A4: H/[H], M/[M] of second order during the entry, sign-flip control first order | no, in P1's set-up (k_max = N/4); yes in the convergence set-up from N = 128 | the part of H odd in the amplitude exceeds the even part by up to 385-870 from ln(N/8) e-folds after N* at every N = 32-256 (first-order spatial truncation of the shells with fewer than eight cells per wavelength; A6 shows it does not change with the Courant factor); magnitude <|H|/[H]> at most 5.1e-11, within 10 x P1's 1e-10; negative control 4e4-1.5e5 times the proper run; halving: odd 2.00, even 4.00. A4's "M/[M] second order" contradicts P1:540-541 ([M] is first order) | orchestrator: rule on A4' (SCOPE 4b, outbox 20261119); core: the first-order truncation item of package scalar3 |
| Recommended A1 background | yes | box means within 1.1e-12 (phi), 8.6e-12 (Pi), 2.0e-12 (K) on every rung (threshold 1e-4) | none |
| Recommended A6 temporal order 4 +- 0.5 | yes | orders 3.93-4.08 of R^NR, of the perturbations of phi, chi, K and of <chi> at N = 32 for Courant 0.25/0.125/0.0625 (runs E-20261119-142317-c851f27, -145230-ff0dff2); time error of R^NR at Courant 0.25 below 3e-4 | A6 at 64^3 on a card (L6 asks 64^3) |
| Recommended A7 reproducibility | yes | noise bit-identical across 1, 8, 64 MeshBlocks and restart (U4 = U2 byte for byte on processors and card, run E-20261119-141654-c2a10d1 and the registered checksums); card against processors 2.2e-15 (A14) | rank count (one rank only) |
| Common: baseline results without the NRPIC coupling | yes | linear MS references for both cases (spec/ref; reruns identical), delta-N references (langevin/), the SR ladder itself (field + Z4c, no particles) | none |
| Common: analysis pipeline validated on them | yes | `analysis/sfa.py` T1-T5 (15/15, rerun identical E-20261119-150346-a513bc8); ladder reader bitwise equal to core's, R^NR at t = 0 within 7.5e-10, extraction factor E6 tested (E-20261115-172935-ddfade0, -174214-74becdd); lead's independent extraction agreeing to three digits | none |
| Common: interface proposals submitted | yes | `noise/NOISE_SPEC.md`, `noise/RNG_REQUIREMENTS.md`, `codebase/DESIGN_REVIEW.md` 9, 11, `spec/SPEC.md` 10; requests of 2026-11-15 answered by core (`scalar2-ready`, interface proposal `tracks/core/interfaces/scalar_field_2.md` on core/scalar-2) | release of that interface |
| Downgrade test (SCOPE 4 item 5, brief 462) | not triggered | A3 passes; one 256^3 SR realisation costs 0.503 card-hours (threshold 5) | USR at G2 |
