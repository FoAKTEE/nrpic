# JOURNAL of package khsr_note (F-hills, wave 3 batch 6)

Helper of F-hills. Three items (task brief, `HANDOFF.md` "Packages"): (1) one result of KHSR
(arXiv:1201.4794) with newton3 on processors; (2) P1 (run F-20261119-150017-b45ec5f) read to
its end, t = 280 M; (3) the note's close-out. Writes only `tracks/F-hills/khsr_note/` and
`tracks/F-hills/runs/`; the note itself (`note/`) and `p1/` belong to other packages, so items
(2) and (3) are delivered here for the lead to carry over (README "Requests").

## 2026-11-21 21:15Z entry 0 (times UTC, from `date -u`; corrected after the first entries were stamped by estimate): state found

- Worktree merged with main (91ab6280). Pause flag absent. Untracked: only
  `g2mesh/scripts/card_analysis.py` (another package's; left alone).
- KHSR found through the knowledge base: `kb/bin/kb show 1201.4794` (manifest row, v1, sha256
  2f8421cf...), `kb/bin/kb search --text-only "ejection probability eccentricity centre of mass
  orbit"` (hits 3, 5, 6: ms.tex:686-734, 34-62, 739-772). Source read at
  `kb-data/raw/arxiv/1201.4794/v1/src/ms.tex` lines 34-62, 137-436, 572-779, 1086-1171.
- Chosen result (SCOPING 5 as amended by the G0 verifier D8): the dependence of the ejection on
  the eccentricity of the centre-of-mass orbit (KHSR Sec. 6.2, Fig. 4, ms.tex:737-778,
  1140-1152). Nothing is digitised: the comparison values are KHSR's text statements and
  closed forms, each with its line.

## 2026-11-21 21:18Z K. KHSR with newton3: prediction (before any run)

Set-up (KHSR ms.tex:752: M/m = 1e6, m1/m2 = 3; coplanar, circular binary): the full
Newtonian three-body driver of newton3 (`hills3.threebody.scatter`, unchanged) at M/m = 1e6,
m1 = 0.75, m2 = 0.25, a = 1, start 10 r_t, end 30 r_t outbound; elliptic centre-of-mass orbits
with semi-major axis r_a/r_t in {500, 200, 130, 100} (Fig. 4's set), e = 1 - D r_t/r_a, and the
parabolic case; 512 effective phases in [0, 2 pi) at D in {0.1, 0.3, 0.5, 1.0, 1.5, 2.0},
prograde and retrograde. "Parabolic approximation" (KHSR eq. Eipara, ms.tex:364-369, and
ms.tex:586-591): the parabolic energy changes dE(phi) moved by the initial energies
I_i = (m_i/m) E_bar; m1 ejected when I_1 - dE > 0, m2 when I_2 + dE > 0.

K1 (closed form, ms.tex:746-749). E_bar = -(1/2)(M/m)^(1/3) (m^2/(m1 m2)) / (r_a/r_t), so at
M/m = 1e6 and m1/m2 = 3 the coefficient at r_a/r_t = 100 is -2.667, which rounds to KHSR's
-2.7. Refuted if it does not round to -2.7. The same E_bar follows from the driver's start
state: E_orb/unit at the start within 1e-3 relative of -2.667 x 100/(r_a/r_t) (it contains the
binary's tidal coupling at 10 r_t, which is small).

K2 (Kepler times, ms.tex:624-626). Start radii at which a conic with D = 1 reaches its
pericentre at the same time as the parabola from 15 r_t: 12.2 r_t for e = 0.9 and 17.4 r_t for
e = 1.1. I predict 12.2 and 17.4 to the digit shown (refuted if either differs by more than
0.05 r_t). This checks that "time to pericentre" in KHSR means the unperturbed conic, as in
newton3's effective phase.

K3 (the result: Fig. 4 and its text).
- K3a parabolic case: one member is ejected whenever the binary is disrupted, so the ejection
  probability equals P_dis; no preference (ratio primary/secondary 1 within the sampling,
  |ratio - 1| < 0.1 at 512 phases); mean ejection energy equal to the phase-averaged |dE|
  (ms.tex:760-762, 768, 771-772). Refuted if the parabolic ratio is off 1 by more than 0.1 at a
  D where P_dis > 0.3.
- K3b the ejection probability falls as r_a/r_t falls, at every D, and the secondary is
  preferred (ratio < 1) at small r_a/r_t (ms.tex:762-769). Numbers [JUDGEMENT, from SKR's
  plateau of |dE| around zero for prograde binaries, ms.tex:723-727]: at r_a/r_t = 500
  (I_1 = -0.40, I_2 = -0.13) the prograde ejection probability is within 0.05 of P_dis for
  0.3 <= D <= 1.5; at r_a/r_t = 100 (I_1 = -2.0, I_2 = -0.67) it is 0.40-0.70 of P_dis and the
  ratio primary/secondary is below 0.4. KHSR's "rapid decrease around r_a/r_t ~ 400" (ms.tex:
  765-766) is an order-of-magnitude estimate, (M/m)^(1/3)(m/m2) = 400; I expect the half-way
  point of the fall (ejection probability at half its parabolic value) not to be reached above
  r_a/r_t = 100 for prograde binaries at D = 0.5-1, i.e. the fall sets in near 400 but is
  steepest below 200. Refuted if the ejection probability at r_a/r_t = 500 is below 0.9 P_dis
  at D = 0.5 or 1 prograde, or if the ratio at r_a/r_t = 100 is above 1 anywhere with
  P_dis > 0.3.
- K3c (ms.tex:715-722) the parabolic approximation agrees with the direct integration of the
  elliptic orbit: total ejection probability within 0.02 (absolute) and the ratio
  primary/secondary within 15 percent where both counts exceed 20, mean ejection energy
  within 3 percent, at every (D, r_a/r_t) with P_dis > 0.1. Refuted at any point outside.
  (The direct integration at M/m = 1e6 is the restricted limit to 6e-4 in dE: newton3 P3.)
- K3d the mean ejection energy falls with r_a/r_t (the ejected member starts deeper), and the
  direct integration gives (m1/m) E2 - (m2/m) E1 = dE of the parabolic run at the same phase
  up to the phase shift: KHSR's remark that the energy change for |e - 1|/D = 0.1 is "very
  similar" to the parabolic one (ms.tex:613-616) holds a fortiori here, where |e - 1|/D =
  1/(r_a/r_t) <= 0.01. Number: phase-averaged |dE| of the elliptic runs within 2 percent of the
  parabolic one at every point with P_dis > 0.1. Refuted otherwise.

Cost: about 31000 three-body integrations (6 D x 5 orbits x 2 senses x 512) plus the K2
arithmetic: 10-20 min on 4 cores [JUDGEMENT from newton3 P3: 2400 integrations in about 2 min
on 4 cores].

## 2026-11-21 21:22Z P. P1 from t = 112.4 M to its end (280 M): prediction

Run F-20261119-150017-b45ec5f (chain DONE, finished by the lead in nrpic-run, commit eb0b2230).
What I had seen of t > 112.4 before writing this (so these are NOT predictions): the last two
rows of `hills.horizon_summary_0.txt` (t = 279.9: mass 0.2662, |S| = 0.0473), the last row of
`hills.z4c.user.hst` (t = 280: H-norm2 = 0.297, C-norm2 0.54, M-norm2 0.22) and the last row of
`hills.co_2.txt` (t = 280.0, heavy hole at x = -0.75, y = 4.34). Reading: the H norm (as
p1/checks.py takes it, sqrt of H-norm2) is 0.545 at t = 280 against 6.0e-5 at t = 112 (p1
analysis F-20261120-222808-0e709b6 / p1_checks.json): the constraints grew by four orders of
magnitude in the second half. Everything below was written before any other look.

Readers: package p1's `scripts/run_all.sh` (unchanged, registered through this package) for the
health items, horizons, trajectories, segments, energies, ledger; my own `scripts/p1_280.py`
for the remnant, recoil and constraint items.

P1-a remnant orbit. At t = 112.38 the remnant (0.268) is 11.82 M from M approaching at 0.208
(p1_checks.json at_end). Prediction [JUDGEMENT]: a single closest approach between t = 113 and
135 at a coordinate distance of 7-11.8 M, then recession; at t = 280 more than 20 M from M and
receding; no common horizon of the remnant with M by t = 280 (finders 0/1 never report a mass
above 0.5; finder 2 stays at 1.00-1.02). Refuted by a common horizon, a second pericentre
before 280, or a turn inside 7 M.
P1-b recoil. Equal members (horizon masses 0.1370 and 0.1390 just before the merger) and no
spin: the physical kick is zero by symmetry up to the tide of M. Prediction: the remnant's
coordinate velocity, fitted over t = 52-60, equals the extrapolation of the members' mean
velocity fitted over t = 36-46, within 0.01 (units of c) in magnitude. Refuted if larger
(that would be a gauge or tracker artefact of the merger, not a kick).
P1-c remnant horizon. Mass 0.2684-0.2700 from t = 50 to 280 apart from finder scatter, drift
below 0.5 percent over 60-280 M [JUDGEMENT; the remnant has about twice the members' cells per
radius]; dimensionless spin |S|/m^2 of 0.60-0.72, the equal-mass non-spinning remnant value
0.686 [BACKGROUND, NR literature, not looked up here] within the finder's accuracy. (The last
row I saw gives 0.0473/0.2662^2 = 0.667, so the end value is not a prediction; the value at
t = 60-100 is.) Refuted if the spin at t = 60-100 is outside 0.60-0.72.
P1-d heavy hole. Mass growth from the first good search (t = 4) to t = 280 below 1 percent;
spin |S|/M^2 below 0.02 (it starts without spin; the remnant's passage cannot spin it up at
the 1e-2 level).
P1-e constraint history. The rise of the H norm (above ten times its t = 112 value) starts at
t = 170-260 [JUDGEMENT: the 1+log lapse pulse of the start reaches the outer face at 256 M after
about 181 M (speed sqrt(2)), light after 256 M; the faces are where a norm over the whole
volume, 512^3, is dominated]. Refuted if the rise starts before 150 (then the remnant's
encounter with M at 113-135 M, or the merger, would be the place) or after 260.
P1-f radiation at the spheres to t = 280. Finite; ordering E(40) > E(48) > E(70) > E(90)
kept (the dissipation of the coarse wave zone, which already orders the t = 112 values); E(90)
at t = 280 at least ten times its t = 112 value 7.1e-6 M, because the merger burst (t = 48.8
at 19.8 M from the origin) reaches 90 M after t of about 120 [arithmetic]. Refuted otherwise.
P1-g health (P1 prediction item 1 of the lead, JOURNAL.md l. 306-308): trackers to 280 M
without a gap above one step and finite; tree within 1016-1870 MeshBlocks seen so far; card
time below the lead's predicted 17-20 card-hours (12.58 by sacct already recorded by the lead).

### 21:23Z correction of entry P, before any analysis output was read

I misread the history: H-norm2 is a volume integral; the norm p1/checks.py reports is
sqrt(H-norm2 / Volume) (nrread.read_hst adds H2 = H-norm2 / Volume). The last row gives
sqrt(0.296953 / 1.36586e8) = 4.66e-5, i.e. no growth: the t = 112 value is 6.0e-5 and t = 0
4.7e-5. So the sentence "the constraints grew by four orders of magnitude" is wrong, and P1-e
was written on that wrong premise. P1-e stays on record as written (it now predicts a rise
that the end value already makes unlikely); replacement prediction for the part I have not
seen, P1-e': between t = 112 and 280 the H norm never exceeds the start transient's maximum
3.2e-4 (t = 1) and never exceeds ten times its t = 112 value; the M norm likewise stays within
a factor ten of its t = 112 value. Refuted by any such excursion.

## 2026-11-21 21:26Z P. outcome (runs F-20261121-212240-c43f35f: p1 readers; F-20261121-212441-1911b7d: p1_280.py; figures read)

Numbers from `p1_280.json` and `p1_checks.json`, `ledger.json` of these runs; figures
`fig_p1_280.png` (six panels) and p1's `fig_tracks_plane.png` read.
- P1-a REFUTED in its time window and, marginally, in distance; MET on the merger with M. One
  closest approach of the remnant to M after t = 60: t = 154.60 M at 6.99 M (coordinate), not
  113-135 at 7-11.8 M; distance 10.29 at t = 120, 7.47 at 140, 7.03 at 160, 10.62 at 200, 24.25
  at 280, receding at 0.158. The remnant swings round M by about three quarters of a turn
  (fig_tracks_plane). No common horizon: finders 0/1 never above 0.2695 after t = 50, finder 2
  at most 1.0078. [JUDGEMENT] The slow approach is the coordinate lag already seen before t =
  112 (heavy hole moved 5.1 M against Newton's 8.0, p1 entry 3).
- P1-b REFUTED: |v_rem(56) - v_cm,pre(56)| = 0.0218 (> 0.01); the direction changes by 1.8
  degrees; the speed rises from 0.184 (members' mean, extrapolated) to 0.205 (remnant), +11
  percent. The heavy hole's velocity changes by 0.0012 between the same windows. [JUDGEMENT]
  Not a kick (zero by symmetry for equal members without spin): the members' coordinate speeds
  lag their physical ones with eta m = 0.25 (E3, 0.5-0.76 of the boost), and the remnant has
  eta m = 0.54; a gauge readjustment of the coordinate speed. No run here could have shown it
  physical or not.
- P1-c: drift clause MET, range clause REFUTED at the end, spin MET. Remnant mass (median of
  the good rows) 0.26832 (60-100 M), 0.26909 (100-140, during the approach), 0.26794 (140-200),
  0.26720 (240-280): drift -0.42 percent over 60-280 (below 0.5), but the end value is below
  the predicted 0.2684. |S|/m^2 0.660 (60-100; range 0.655-0.665) inside 0.60-0.72; 0.677
  during the approach, 0.662 at the end. Finders 0 and 1 agree to all digits shown.
- P1-d MET: heavy hole +0.315 percent from its first good search (1.00419 at t = 4) to the
  median of 240-280 (1.00736); |S|/M^2 below 3.3e-3 everywhere (medians 1.3e-3 during the
  approach at 100-200, 1.5e-4 at 240-280). The rise and fall of the spin estimate with the
  remnant's passage, and the mass branches 1e-3 apart in 100-260 M, are finder readings of a
  tidally deformed horizon [JUDGEMENT], not a spin-up (it returns to 1.5e-4).
- P1-e REFUTED (written on the misreading, see correction): no rise at all. P1-e' MET: the H
  norm between 112 and 280 M lies within 4.66e-5 and 8.79e-5 (maximum at t = 258.5, 1.46 times
  its t = 112 value 6.02e-5; the start transient's maximum is 3.17e-4 at t = 1); M norm within
  3.65e-5 and 4.97e-5 (1.14 times its t = 112 value). The merger lowered the H norm from
  1.5-1.8e-4 to 5.6e-5 (the members' high-gradient region disappears) [VERIFIED as a reading of
  the curve; cause JUDGEMENT]. History finite, volume constant to 1e-4 (refinement).
- P1-f MET: E(280) = 2.97e-3 (R = 40), 2.17e-3 (48), 2.08e-3 (70), 2.01e-3 (90) M, ordered as
  predicted; E(90) rose from 7.1e-6 (t = 112) to 2.0e-3. Most of it arrives at t = 190-260, i.e.
  from the remnant's pericentre at t = 154.6 (light from 7 M reaches 40-90 M after 33-83 M);
  the four spheres agree within 4 percent from R = 48 on (2.01-2.17e-3), unlike the earlier,
  strongly R-dependent part. [BACKGROUND formula, arithmetic] Peters' energy loss of a
  parabolic passage, (85 pi/(12 sqrt 2)) m1^2 m2^2 (m1+m2)^(1/2) / r_p^(7/2), is 1.4e-3 M for
  1.007 and 0.267 at r_p = 7 M: the same order as the measured 1.8-1.9e-3 added after t = 150
  (coordinate pericentre; no claim beyond the order of magnitude).
- P1-g: trackers MET (71680 common rows to t = 279.996, largest gap one step 3.9e-3, finite);
  tree REFUTED on the low side (736-1870 MeshBlocks; 736 is new, after t = 112); card time
  MET: 12.583 card-hours over 16 jobs (lead's 17-20 predicted, 21-25 segments: also low).
- Not usable: the Newtonian two-body energy of remnant and M from coordinate velocities moves
  from -0.0048 (t = 60) to -0.0173 (pericentre) to -0.0052 (280): it is not conserved through
  the passage, so the coordinate velocities cannot say whether the remnant is bound
  [JUDGEMENT].

## 2026-11-21 21:28Z K. first scan (F-20261121-212049-d91381f) and checks (F-20261121-212703-276a88b): defect found

The checks show mean ejection energies of 50.9 and mean |dE| of 13.7-60.8 units at five
(D, r_a) points, each one with failed integrations (n_fail 1-3 of 512): my script did not
leave out the samples whose integration stopped (integrate_many ok = False), so their
unfinished states entered the statistics. K1 and K2 are not affected (closed forms):
K1 MET (-2.667 rounds to -2.7), K2 MET (12.223 and 17.422 r_t against 12.2 and 17.4).
Correction: khsr_ecc.py now leaves failed samples out of every statistic (count kept as
n_fail) and stores ok in the npz. The scan is rerun; the first run stays on record. The
probabilities of the first run already show the result (K3 judged on the rerun).

## 2026-11-21 21:36Z K. outcome (scan F-20261121-212757-77cdc15, checks and figure F-20261121-213405-6596be1; figure read)

Failed integrations left out: 26 of 23040 (at most 4 of 512 at one point). Every K3 number below
from `results/khsr_checks.json`; figure `figures/fig_khsr_ecc.png` read (lines: parabolic
approximation from the restricted problem; filled circles: three-body integration on the
elliptic orbit; open squares: parabolic approximation from the parabolic three-body runs at the
same phases).
- K1 MET: -2.667 rounds to KHSR's -2.7 (ms.tex:746); the start state's E_orb equals it to 2e-13.
- K2 MET: 12.223 and 17.422 r_t against 12.2 and 17.4 (ms.tex:624-626).
- K3a MET: parabolic ratio primary/secondary 0.979-1.013 at every point (512 phases); ejection
  probability equals P_dis; mean ejection energy equals the phase-averaged |dE| to 0.2 percent.
- K3b MET: prograde ejection probability at r_a/r_t = 500 within 0.006 of P_dis at D = 0.3-1.5
  (0.971/0.971 at D = 0.5, 0.923/0.925 at D = 1); at r_a/r_t = 100 it is 0.565, 0.568, 0.572,
  0.453 of P_dis at D = 0.3, 0.5, 1, 1.5 (predicted 0.40-0.70); primary/secondary 0.08-0.154
  for D <= 1 and 0 at D = 1.5 (predicted < 0.4); never above 1. The half-way point is not
  reached at r_a/r_t = 100 for D = 0.5-1 (as predicted). Retrograde binaries lose their
  ejections much sooner: at D = 0.3 the ejection probability falls from 0.363 (parabolic) to
  0.172 at r_a/r_t = 500 and 0 at 130. Text of KHSR reproduced: no preference for the parabola,
  the secondary preferred at small r_a (ms.tex:768-769); the fall sets in between 500 and 130
  (prograde), "around 400" being KHSR's order-of-magnitude estimate (ms.tex:765-766).
- K3c REFUTED at the edge, MET elsewhere: |P_direct - P_lines| <= 0.012 at every judged point
  except prograde D = 2, r_a/r_t = 100, where the three-body integration ejects nobody (0 of 512)
  and the approximation gives 0.037 (0.027 from the parabolic runs at the same phases, 14 of
  512). Ratio within 15 percent except prograde D = 1.5, r_a/r_t = 130 (0.113 vs 0.138, 22
  primary ejections: within the counting noise, 21 percent). Mean ejection energy within 3
  percent where it is above 0.3 units; 4-11 percent (absolute <= 0.027 units) where it is
  0.03-0.25 units: my relative tolerance was ill-posed for small energies.
- K3d REFUTED at large D: the elliptic runs' phase-averaged |dE| is within 0.5 percent of the
  parabolic one for D <= 1, but 0.8-1.2 percent low at D = 1.5 and 1.6-3.1 percent low at D = 2
  (largest at r_a/r_t = 100, e = 0.98). [JUDGEMENT] KHSR's "non-parabolic results tend toward
  a perfect overlapping with the parabolic results" (ms.tex:633-636) holds to this level; at the
  edge of disruption, where the ejection probability is a threshold on the tail of the dE
  distribution, a 2-3 percent smaller energy change removes the few ejections the
  approximation still finds (the K3c point above).
Verdict for G1 T1 / risk R14 [JUDGEMENT]: one KHSR result reproduced with newton3 on processors
(the ejection against the eccentricity of the centre-of-mass orbit, Sec. 6.2, Fig. 4 and its
text), with KHSR's parabolic approximation confirmed by the full three-body integration to
0.012 in probability except at D = 2. Nothing digitised: comparisons are with KHSR's text and
closed forms.

## 2026-11-21 21:50Z N. Note close-out: plan and prediction of the figure run

The note belongs to package `note/` (another package's directory), so the close-out is built
as a working copy in `khsr_note/note/` (main.tex, references.bib, scripts, figures, tables;
`common.py` finds tracks/F-hills from either place, so the lead can copy the directory back
unchanged; command in README). Changes: Sec. II pericentres with their GR turning points
(lead's correction 5); Sec. III A released parts as of core-v0.6 and the architecture
schematic marked accordingly (correction 7); Sec. III B the post-Newtonian reference reviewed
(R17); new Sec. IV B "elliptic orbits" with fig_khsr (this package's KHSR scan); Sec. IV C Kerr
paragraph (package kerr); correction 6; Sec. V A junk and V B single-member junk (stage/G1
STATUS T3); new Secs. V E "the first passage to its end" (fig_p1_end) and V F "the binary
alone" (fig_binary, package binary_conv, R19); plan, summary, abstract, introduction; ledger:
group "Elliptic orbits" and Kerr rows in table 1, corrections 1-4 (a_b/R_curv at any time,
geodesic q = 4 energy with its drift, q = 10 crossing time 96.9 M, 3100 slots), table 5 (binary
alone, first passage to its end).
Prediction for the registered run of `khsr_note/note/scripts/run_all.py`:
1. Every script exits 0; the three new figures' self-checks hold (separations of the binary
   runs equal analysis.json to 1e-6 at 7.5, 15, 20 M; P1's closest approach, remnant mass and
   radiated energies equal p1_280.json).
2. The PNGs of the nine unchanged figure scripts are byte-identical to the committed note's
   (`note/figures/`, run F-20261120-222908-4ffcfba), schem_dataflow and schem_timeline too;
   schem_architecture differs (statuses changed). Refuted if an unchanged figure differs (the
   environment changed).
3. ledger.tex differs from the committed one only by the added and corrected rows and the new
   table 5; `claims.md` unchanged.
