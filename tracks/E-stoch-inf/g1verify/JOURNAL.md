# Journal of g1verify (independent verifier of Track E's G1 material)

Helper of E-stoch-inf, wave 3, package g1verify (decision 0016 item 4; item C16 of the G1
checklist). Predictions are written before the runs they concern; outcomes after, including
the failed ones. Labels: [VERIFIED] recomputed here with a run id, [JUDGEMENT] my inference,
[BACKGROUND] standard, [TO VERIFY] open.

## Entry 0 (2026-11-20 14:21 PST, 22:21Z): set-up, what was read

Worktree commit at start: bc5e277 (merge of main), e2f926e when this directory was made
(other helpers commit in the same worktree).

Read: CLAUDE.md; coord/CHARTER.md to "Owners" and section 9.8; decisions 0010, 0013 (Track E
item), 0016-0019; SCOPE.md section 4 item 4 (A1-A8 definitions and thresholds; the amendment
note under A2 quotes two numbers of the ladder, 6.2e-3 and 1.2e-4 at 256^3, which I could
not avoid seeing) and section 4b (A4', A5' as proposals); SPEC.md sections 1-7; core's
interface `scalar_field_2.md` and the READY of core_scalar-2 (both quote core's own test
numbers at 32^3-128^3; they are core's verification, not the track's G1 results); the run
manifests and the ladder inputs (`ladder/inputs/*.athinput, *.list, modes_n*.txt`);
P1 = arXiv:2512.14649 v2 PRD_v2.tex lines 400-545 and 690-790; BZ = arXiv:2606.14853 v2
Manuscript.tex lines 140-290; TH = arXiv:2610.32592 v1 appendix.tex 380-525; P2 =
arXiv:2502.06783 v3 main_V2PRD.tex 395-460 (all from kb-data/raw/arxiv, read only);
coord/INTERFACES/rng.md sections 2-3; athenak/src/utils/rng.hpp (Philox, CellEntity,
DiskPoint, NegLog52, Normal2) and the header comment and NoiseDrawAlpha of
core/scalar-2:athenak/src/scalar_field/scalar_field_noise.cpp (to rebuild alpha_n and the
phase convention x0 = lower corner, cell centres (g + 1/2) dx).

Not read (before the verdicts): STATUS, HANDOFF, JOURNAL, RISKS, PLAN-wave3 of the owner;
stage/REVIEW-wave2.md; everything under stage/G1/; ladder/README.md, JOURNAL.md, results/,
fig/; note/; the packages a4res, ladder (beyond inputs), usr, window; spec/ref/ (the track's
reference), the wave reports of scratch/orch.

Set-ups confirmed from the lists (`ladder/inputs/job{A,B,C}.list`, `proc32.list`,
`proc64.list`, `a6proc.list`) [VERIFIED by reading]: L = noise_nmax2 64 (k_max/dk = 8) with
modes_n64.txt; Q64 = nmax2 256, Q128 = 1024, P256 = 4096 (k_max = N/4, P1's set-up);
p/m = noise_mode_scale +1/-1; ph/mh = +-0.5; NC = noise_pi_sign -1. The m, h and NC runs
have dump_metric = false (no gt_ij, At_ij in their dumps), so R^NR (needs gt_ij) is
measured on the p runs only. Run ends: P256, L32p/m, L64p/m (card), L128p/m, Q64p, Q128p at
t = 8.5; P256m, L256p/m, Q-m/h, NC, L32ph/mh, L64p/m (processors) at t = 4.5. Dumps every
0.5 in t at the first cycle past each multiple, so dump times differ between resolutions
(at most one step); the Courant runs dump at common cycles x (0.25/theta).

Own code (scripts/): `nrsf.py` (reader of NRSFDMP2 and the records), `alpha.py` (Philox
4x64-10 vectorised in numpy, polar Box-Muller of rng.md; alpha_n per wave vector),
`ref.py` (physical background with P2's potential-position fixing, Bunch-Davies modes from
N0, code-unit background, full and deformed MS in cosmic time, window). Smoke tests before
any registered run (not evidence): own Philox equals numpy.random.Philox on all 1054 modes of
nmax2 = 64; own BD integration reproduces modes_n64.txt at n = 1, 2, 8 to 1e-13 in modulus
and relative phase; own fixing gives the input's phi0, pi0, mass to rounding.

## Entry 1 (2026-11-20 14:45 PST): predictions for C0 (infrastructure), V1, V2, V3

Written before run C0/V1-V3 (no NR dump has been read by my code yet).

C0 infrastructure.
- P-C0a: my reader and core's `read_dump` (core/scalar-2) give bit-identical arrays for all
  22 variables of a single-MeshBlock dump. Refuted by any differing element.
- P-C0b: my Philox words equal numpy.random.Philox (independent implementation) for every
  sampled key, also for nmax2 = 4096; the AGM and library logarithms give alpha within
  1e-12 relative; <|alpha|^2> = 1 within 3/sqrt(M).
- P-C0c: at t = 0 my extraction of R^NR (Phi from chi and gt_ij by TH appendix.tex:518,
  R = Phi - <K>/(3<alpha><Pi>) (phi - <phi>), TH:520, P1:524) equals L^(-3/2) W(0) R_n(0)
  alpha_n with the phase exp(i pi (n_x + n_y + n_z)/N) of the cell centres, within 1e-9
  relative for |n| = 1 (W = 1/2); for smaller W the relative error grows as rounding/W.
  Refuted if |n| = 1 is off by more than 1e-6 or the phase is wrong (then my convention or
  alpha is wrong, not necessarily the code).

V1 (A1, threshold 1e-4 relative).
- P-V1: on every rung the box means of phi, Pi, K (records every cycle, and my own means of
  the dumps) follow my Friedmann + Klein-Gordon integration to between 1e-13 and 1e-9
  relative; the deviation falls with the step (Courant runs) until the second-order mean of
  the perturbations (~R^2 ~ 1e-10) or rounding takes over. e-folds -ln<chi>/2 = ln a within
  1e-8. Refuted: any deviation above 1e-4 (A1 fails), or a deviation that does not fall
  with the step while above 1e-10.

V2 (A2, threshold 0.02 for k <= k_max/2 at N_f).
- P-V2a: per mode |R^NR_n/(L^(-3/2) W R_n alpha_n) - 1| at the last dump, maximum over
  k <= k_max/2: L32 1e-4 to 1e-3 (sixth-order dispersion at k dx = pi/4, 3.8e-4 in k^2 by
  SPEC 7.2's arithmetic), L64 ~ 64 times less, L128 and L256 at a floor of order 1e-6 (the
  second-order part of R^NR, ~R ~ 1e-5 times O(0.1)); P256 at k <= 32: 1e-4 to 1e-3 (again
  k dx = pi/4). All pass 0.02. Refuted: any mode above 0.02, or no fall from L32 to L64.
- P-V2b: the alpha-normalised shell spectrum at N_f over the analytic slow-roll power at
  crossing H_k^2/(8 pi^2 eps1_k Mpl^2) is 1 + O(eps1), between 0.98 and 1.03 for every shell;
  the raw shell spectrum scatters around that by 1/sqrt(M_shell).

V3 (A3, threshold 1 percent in the ratio; drift below 2.5e-3 per e-fold).
- P-V3: for every mode with N_f - N_k >= 6 (k <~ 7.9 at N_f = 8.1) the NR power ratio
  between the first dump past N_k + 4 and N_f equals the full-MS ratio within 1e-4 (it is a
  ratio of one mode, no alpha needed); the NR drift d ln|R_n|^2/dN over that interval is
  below 1e-3 per e-fold and within 1e-4 of the full MS, and far from the deformed
  (FLRW-lattice) drift -4 eps1 ~ -0.045 to -0.054. Refuted: ratio off by more than 1 percent
  (A3 fails), or a drift near the deformed one.

## Entry 2 (2026-11-20 19:00 PST, 03:00Z on 11-21): second session; C0 outcome; pass 1 closed

Second session of this package (the first was cut at 14:35 PST by the five-hour limit). I
re-read CLAUDE.md, CHARTER to "Owners" and 9.8, decisions 0010, 0013 (E), 0016-0020, SCOPE 4
item 4 and 4b, SPEC 1-7 and the interface scalar_field_2.md sections 2-4 myself; nothing of
the forbidden list (entry 0) was opened. The worktree held, from session 1: scripts nrsf,
alpha, ref, rnr, catalog, check_infra, permode, v123 (committed d42de1a) and constraints.py
(uncommitted, a dev run in scratch/E-stoch-inf/g1verify_tmp/condev, not evidence).

C0 outcome (run E-20261120-222844-dbca87f, completed, exit 0) [VERIFIED]:
- P-C0a CONFIRMED: my reader and core's read_dump (core/scalar-2) give 0 differing elements
  in all 22 variables of dump 5 of L32p, L64p, L128p.
- P-C0b CONFIRMED: 0 of 7160 sampled Philox keys differ from numpy.random.Philox at nmax2 =
  4096 (548958 modes); AGM against numpy.log: 7.6e-10 relative at most (inside 1e-12? NO:
  the prediction said 1e-12; the AGM form of rng.hpp is an approximation of the logarithm at
  that level, so my "bit-exact intent" AGM and the library log differ by 7.6e-10. Failed
  sub-prediction, harmless: alpha from the AGM agrees with core's twin mode_alpha to 5.0e-16
  absolute, which is what matters). <|alpha|^2> = 1.00057, inside 3/sqrt(M) = 4.0e-3.
- Background: my fixing gives the deck's phi0, pi0, mass to 1.2e-15 relative; H(0) = 1 in
  code units; N(t = 8.5) = 8.0989, N(4.5) = 4.3876.
- Mode files: modes_n64.txt equals my Bunch-Davies integration to 6e-13 (modulus) and 2e-13
  (phase). modes_n256/1024/4096.txt equal mine to 1.6e-6 (modulus) and 2.7e-6 rad (phase):
  integrated with a looser tolerance, 1e4 below the A2 threshold and 1e3 below A3's. Noted.
- Lists and manifests: all six lists unchanged since submission (sha256 equal), mode-file
  checksums equal, card list copies in the run directories equal.
- P-C0c CONFIRMED: at t = 0, |R^NR_n/(L^-3/2 W R_n alpha_n) - 1| = 1.1e-10 to 7.5e-10 for
  |n| = 1 (W = 1/2) on L32p, L64p, L128p, 0.8e-9 to 2.2e-9 for |n|^2 = 2, 3; 1e-7 to 1.6e-6
  for |n|^2 >= 4 where W < 1e-3 (rounding/W as predicted). Phase within 1.5e-6 rad. So my
  extraction, the phase convention and alpha are right.

Pass 1 (run E-20261120-223154-d42de1a, completed exit 0 at 23:02Z, closed with nrpic-run
finish now): R^NR_n per mode and box means from all 18 dumps of P256 and all 10 of L256p,
the sha256 of every dump equal to the run's sha256sums.txt (18 + 10 of 28). Wall 1851 s.
No analysis of these numbers yet.
