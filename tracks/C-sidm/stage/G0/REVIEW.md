# Lead review of the wave-1 helper packages of C-sidm

Lead session of 2026-11-15. Method: rerun every package's tests and registered reference
runs from the committed artefacts and compare with the registered outputs (run
C-sidm-20261115-131135-3077a99, `review/rerun_packages.sh`, `review/compare_reruns.py`);
independent cross-checks written by the lead (run C-sidm-20261115-131130-3077a99,
`review/crosscheck.py`, X1-X5); reading of the derivations and of the source locators; every
figure of the four packages opened (PNG read). Predictions L1-L6 were written into
`JOURNAL.md` before the runs; outcomes are below and in the journal.

## Outcome of the lead's runs

| Prediction | Outcome |
|---|---|
| L1 reruns identical | RERUN_OUTCOME |
| L2 (X1) closed-form <v_Mol> against a 3D Gauss quadrature over both momenta (no Gondolo-Gelmini reduction), theta = 1e-3..100 | held: largest difference 5.2e-7 (theta = 1e-3, limited by the kink of the angle-averaged speed at |p1| = |p2|; 64 against 128 nodes 1.5e-6), 2.6e-14 at theta = 100; collide's `rate.vmol_mean` equals the closed form exactly. `fig_review_rate.png` |
| L3 (X2) scope's and gravothermal's truncated Maxwell-Boltzmann solvers | held: eps agrees to 2.0e-8 (b = 0.1) and 3.2e-9 (b = 0.5), Z(0) to 2.0e-9; eps maxima at Z(0) = 0.5404128 and 0.5404128 (b = 0.1), 0.5141817 (b = 0.5); against F21 rows `main.tex:492, 495, 498, 501` both within 8.0e-5 in M, E_rest, eps, Z(0), v(0) (largest at w0 = 4.0515, F21's fixed-step RK4 per the gravothermal helper). `fig_review_tmb.png` |
| L4 (X3) scope's solver at b = 1 against equilibria's `evstatic` King model | held: E_b to 3.5e-8, Z_c to 6.5e-10; both y_max = 0.334032 (printed 0.334, 2009.08163 `paper.tex:953`) |
| L5 (X4) Kn definition | held: K = 1/(rho0_c H_c) = 168.895 from the scope solver and 168.895 from equilibria's `knudsen.json`; scope's convention gives 198.6; equilibria's Kn sigma~ = K (l/lambda) to rounding; K = 154-206 over the 13 models |
| L6 (X5) sign of omega_0^2 around gravothermal's onset w0 = 3.5871 (b = 0.1, gamma = 1 + p/u) | held: +0.327, +0.0296 at w0 = 3.50, 3.58; -2e-6 (N = 600), -4.5e-6 (N = 1200) at 3.5871; -0.0336, -0.441 at 3.595, 3.68; N = 600 and 1200 agree to 1e-5 relative. `fig_review_onset.png` |

## Per package

### scope (`tracks/C-sidm/scope/`, G0 scoping note)
- Confirmed: the three scripts reproduce their registered outputs (L1); the monoenergetic
  threshold y_c = 0.67961 and the reproduction of the five Wu-Most models (2611.12831
  `main.tex:1024-1028`, re-read by the lead); the King solver against F21 and 2009.08163,
  now also against two independent solvers (X2, X3); the cost table from the first paper's
  logs; every locator of SCOPE.md re-read by the lead in `REPORT.md` section 6 (all
  correct; the mean-free-path direction of brief 384 re-read at `SIDM_MS.tex:62-63`).
- Not confirmed: astro-ph/0111176 `:289-291` (not re-read); the G2/G3 card-hour estimates
  (assumed multipliers; nothing to rerun).
- Wrong or changed: (1) SCOPE.md section 4 defines H with the energy density rho; the
  literature's H uses the (rest-)mass density (`SIDMGT_Xiv2.tex:403-405`), so the track's
  definition is now the equilibria one with lambda (REPORT decision 2); scope's Kn numbers
  are larger by K_scope/K = 198.6/168.9 = 1.18 for the King threshold model and are quoted
  with that caveat. (2) Scope's G1 item (a) (monoenergetic threshold scan) is moved to G2
  work in wave 2 (REPORT decision 4). (3) The particle-number requirement used Koda &
  Shapiro's k = 32 neighbour rule; with the cell-based operator of SPEC.md the requirement
  is N >= 1.7e3-2.3e4 Kn^-3 for the King threshold model (REPORT section 3). (4) Commit
  5aacad7's message miscounts the sources (15 for 14), recorded in its journal.
- Figures opened: `fig_seq_monoenergetic`, `fig_king_check`, `fig_king_sequence`,
  `fig_knudsen`, `fig_costs`: no defect.

### collide (`tracks/C-sidm/collide/`, C-pre-1 and C-pre-2 specifications)
- Confirmed: 62 reference tests and 3 pipeline tests pass on rerun (L1); the T6-0 AthenaK
  collisionless run is reproduced bit for bit (L1); the derivation of (R) re-done by the lead
  (integrals int x^2 K1 = a^2 K2, int x^4 K1 = a^4 K2 + 2 a^3 K3 with a = 2 zeta; the
  4 zeta^2 a^2 K2 term cancels a^4 K2) and checked numerically by an independent quadrature
  (X1); the pair-probability (P) gives the per-particle rate n sigma <v_Mol> and the event
  rate n^2 sigma <v_Mol>/2 (checked by hand), the odd-N triangle keeps the expected count
  per particle; the b-constant sources (`sidm1.tex:408-412`, `SIDM_MS.tex:233`,
  `SIDMGT_Xiv2.tex:394`, `smbh.tex:116`) and 2602.17487 `results.tex:18` re-read.
- Not confirmed: anything about core's implementation (not committed); the unequal-weight
  no-go (SPEC 4.4, [JUDGEMENT]); the relativistic conduction and the Sonine factor
  (no source read).
- Wrong or to fix: (1) `RNG_REQUIREMENTS.md` was written against core's uncommitted draft;
  core's committed `rng.md` (branch `core/rng`) still leaves stream 2 "to be fixed by the
  collision package"; the table is now requested from core (outbox). (2) core's draft
  collision interface uses a symmetric triad by default; T0b must set `triad = cholesky` or
  the replay must follow (outbox, G1 STATUS). (3) Cosmetic: `figs/ref_relax.png` left
  y-label reads "(theta_1 - theta-dot_2)/NR" for d(theta_1 - theta_2)/dt over the
  non-relativistic form; `figs/T6_0_step_collisionless.png` left y-label is clipped and the
  legend covers data. Not redrawn this session (listed in HANDOFF). (4) Commit e0bbac2
  committed four manifests of other helpers by a glob (harmless; reported to orch).
- Figures opened: `ref_rate`, `ref_kinematics`, `ref_relax`, `ref_conduction`,
  `ref_entropy`, `T6_0_step_collisionless`, `pipeline_relax_synthetic`.

### gravothermal (`tracks/C-sidm/gravothermal/`, C-pre-3 baseline)
- Confirmed: unit tests pass and the polytrope turning-point check is reproduced (zero of
  omega_0^2 at the mass maximum to 2.7e-8, 1.5e-8, 2.5e-8 for N = 300, 600, 1200) (L1);
  the F21 sequence against a second independent solver (X2) and four rows transcribed by the
  lead; the onset Z(0) = 0.6348 (X5); the transcription of F21's pulsation equation into
  the Sturm-Liouville form of `tmb.fem_lowest` (P, Q, W re-derived by the lead from
  `main.tex:202-204`); the e^{2 Phi} misprint claim (`main.tex:197`) is consistent with the
  source as printed.
- Not confirmed: the 1.3e-4 offset of F21's eps_c(0) column (open in the package);
  G26's time-scale numbers other than those re-read (`SIDM_MS.tex:384, 476`).
- Wrong or to fix: nothing found. The manifests use a third schema (fields `git`,
  `resources`, `started`/`ended`); fine for the record, but `nrpic-run` cannot read any of
  the hand schemas (outbox to orch). Cosmetic: `fig_profiles_b0.1.png` uses orange and red
  for two different criteria.
- Figures opened: `fig_onset`, `fig_polytrope_check`, `fig_sequence_b0.1`,
  `fig_table_residuals`, `fig_criteria_vs_b`, `fig_timescales`, `fig_profiles_b0.1`; not
  opened: `fig_eos`, `fig_sequence_b0.2/0.3/0.5` (same construction as b = 0.1).

### equilibria (`tracks/C-sidm/equilibria/`, C-pre-4 initial data)
- Confirmed: EQUILIBRIA_OUTCOME; the King y_max 0.334032 against two other solvers (X3);
  the 2009.08163 table (`paper.tex:953-956`) and the gr-qc/0601112 Z_c line (`:694`)
  re-read; the Kn conversion numbers (X4).
- Not confirmed: the AthenaK smoke run (run C-sidm-20261115-125308-54870b9) was not
  rerun; the cause of its momentum-constraint ratio 1.42 is open (package and OPEN item 12).
- Wrong or to fix: (1) its Kn uses the transport mean free path l = 0.77 lambda instead of
  the literature's lambda; the track's definition (REPORT decision 2) converts with
  Kn_track = Kn_equilibria/(l/lambda). (2) Test-design note: the three model families are
  sampled with the same seed, so the plain Monte Carlo shell statistics in
  `figs/sampling_threshold.png` are identical across the three columns (the radial draw
  depends only on the uniforms); the three checks are not independent. Not a defect of the
  samples.
- Figures opened: `binding_energy`, `constraint_residual`, `athenak_smoke`,
  `sampling_threshold`, `knudsen_conversion`, `king_mass_radius`, `profiles_threshold`;
  not opened: `shell_angular_momentum`, `knudsen_profiles`.
