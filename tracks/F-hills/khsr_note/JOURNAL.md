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
