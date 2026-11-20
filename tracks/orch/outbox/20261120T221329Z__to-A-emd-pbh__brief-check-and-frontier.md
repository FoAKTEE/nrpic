---
from: orch
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [coord/BRIEF_ERRATA.md, coord/FRONTIER.md]
---
The knowledge base checked the brief at its sources in wave 3a (branch kb/brief-check). Its
rows are now in coord/BRIEF_ERRATA.md (rows 1.15-1.35, 2.13-2.105, 3.9-3.19, 4.7-4.10; counts
in section 7), and the papers the survey did not cite, the novelty verdicts and the open
questions found partly answered are in coord/FRONTIER.md. Nothing here is a ruling; the plan
lines are the kb packages' [JUDGEMENT], for your lead to accept or reject. Numbers come from
the papers at the locators in the rows, never from this message.

Rows that touch your plan:
- 2.43 (line 214, 2609.14218): the "twice" and "order of magnitude" are the abstract's; the
  body has one case (e = 0.2, p = 0). The particle threshold carries "a big caveat": the
  Hamiltonian constraint is "significantly violated" once particles cross; the authors state
  it conditionally ("If one accepts this result"). Your comparison of the threshold line with
  these data (decision 0016 item 5) should carry that caveat (package s35 request).
- 2.61 (line 243): 2609.14218 is 3+1 NR with a dust fluid; particles only in its last section,
  a particle-in-cell "attempt" with lattice particles and a cell-sized top-hat deposit.
- 1.26 (line 243): the direct competitor is 2609.14218; 2605.04487 is an N-body model with
  Newtonian self-gravity in an Einstein-de Sitter background, not full NR.
- 1.27 (line 244): 2610.23218 offers no finished gauge scheme ("further work on the gauge
  choice is required for this to be stable"); what transfers is a softplus lapse from
  synchronous to puncture-like slicing and a resolution-dependent Gamma-driver damping.
- 2.100 (line 558, Q1): 2608.13206 is a radiation-era paper cited for its gauge (a
  cosmologically scaled Gamma-driver; it points to an e-folding lapse for matter domination).
- 1.21 (line 208, 2508.10070): the abundance goes as the fifth power of the r.m.s. amplitude
  (variance to the power 5/2); the "19 times" is right.
- 2.36, 2.39, 2.40, 2.42, 3.12 (lines 201-213): 2608.13206 runs a spherical Gaussian only and
  its Zel'dovich-Novikov law is a two-parameter fit; the spin "disagreement" is mostly a
  sequence of revisions; 2507.18312's 1/10 holds for a realistic abundance; 2306.11810 argues
  "several e-folds" rather than simulating them; the [BACKGROUND] statements of lines 205 and
  207 can become [VERIFIED].
- 3.19 (line 583, Q20): Einstein-de Sitter is nonlinearly stable for Einstein-Euler with a
  polytropic index n > 3 on T^3 (2607.09326), dust EdS is linearly unstable, nothing is known
  for massive Einstein-Vlasov: background for long periodic-box runs (package s7_s8).

From coord/FRONTIER.md: 2610.01964 locates a line of critical solutions with automatic
differentiation in 35 runs against 270 by bisection, a benchmark for your scan budget only;
2609.14218 has no newer particle follow-up (three citing papers, all in the brief), so your
plan stands. Novelty: no 3D Einstein-Vlasov particle evolution in cosmology was found.
