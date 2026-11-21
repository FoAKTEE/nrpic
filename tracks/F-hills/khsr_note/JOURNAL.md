# JOURNAL of package khsr_note (F-hills, wave 3 batch 6)

Helper of F-hills. Three items (task brief, `HANDOFF.md` "Packages"): (1) one result of KHSR
(arXiv:1201.4794) with newton3 on processors; (2) P1 (run F-20261119-150017-b45ec5f) read to
its end, t = 280 M; (3) the note's close-out. Writes only `tracks/F-hills/khsr_note/` and
`tracks/F-hills/runs/`; the note itself (`note/`) and `p1/` belong to other packages, so items
(2) and (3) are delivered here for the lead to carry over (README "Requests").

## 2026-11-21 21:20Z entry 0: state found

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

## 2026-11-21 21:25Z K. KHSR with newton3: prediction (before any run)

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

## 2026-11-21 21:35Z P. P1 from t = 112.4 M to its end (280 M): prediction

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

### 21:40Z correction of entry P, before any analysis output was read

I misread the history: H-norm2 is a volume integral; the norm p1/checks.py reports is
sqrt(H-norm2 / Volume) (nrread.read_hst adds H2 = H-norm2 / Volume). The last row gives
sqrt(0.296953 / 1.36586e8) = 4.66e-5, i.e. no growth: the t = 112 value is 6.0e-5 and t = 0
4.7e-5. So the sentence "the constraints grew by four orders of magnitude" is wrong, and P1-e
was written on that wrong premise. P1-e stays on record as written (it now predicts a rise
that the end value already makes unlikely); replacement prediction for the part I have not
seen, P1-e': between t = 112 and 280 the H norm never exceeds the start transient's maximum
3.2e-4 (t = 1) and never exceeds ten times its t = 112 value; the M norm likewise stays within
a factor ten of its t = 112 value. Refuted by any such excursion.
