# Journal of work package "novelty" (kb brief check, wave 3a)

Owner kb (helper). Brief lines 394-444 (S4 to S10) and 1749 (novelty searches of section 15
item 5). Times are local (PST, UTC-8) from `date`.

## Entry 1, 2026-11-19 07:30: predictions before any source is read

Written after reading the brief lines and the titles and abstracts of the cited papers
(metadata only), before any TeX source, INSPIRE query or web search of this package.

Statements in scope with a label: L398 r^(-9/4) [BACKGROUND] (already errata row 1.7, not
repeated); L410 neutrino decoupling, horizon mass, neutrino fraction [BACKGROUND]; L414 S5 state
of the art [TO VERIFY]; L426 AthenaK single time step [VERIFIED] and NRPIC keeps it [TO VERIFY]
(the latter answered by errata row 3.7 for line 134); L437 S7 state of the art [TO VERIFY].
Unlabelled specific claims about cited papers in lines 398-443 are checked as well (marked
"(unl.)" in CHECK.md), as the sibling packages do.

- P1 (L410). The sources give neutrino decoupling at T of about 1 to 2 MeV; the horizon mass at
  T = 1 MeV is between 3e4 and 3e5 solar masses; the neutrino share of the radiation energy
  density is about 0.41 after e+e- annihilation and about 0.49 before (so "forty to fifty per
  cent" holds). Refuted if a source puts M_H(1 MeV) outside [3e4, 3e5] M_sun or the share
  outside [0.35, 0.55].
- P2 (L414, S5). No full-GR kinetic (Einstein-Vlasov or particle) calculation of
  primordial-black-hole formation with a free-streaming relativistic component exists. The
  closest work: fluid calculations with a softened equation of state (QCD, e+e-), two-fluid or
  imperfect-fluid treatments, and collisionless (dust-like, non-relativistic) particles in the
  matter era (2609.14218). Refuted by any paper that evolves PBH formation with relativistic
  collisionless particles or massless Vlasov matter coupled to the Einstein equations.
- P3 (L437, S7). No 3+1 numerical test of the Burnett conjecture with massless Vlasov matter
  exists. Closest: full-NR evolutions of nonlinear gravitational waves in cosmology
  (1505.02959, 1801.08362), short-wavelength or geometric-optics numerics without a Vlasov
  counterpart. Refuted by a paper comparing a coarse-grained high-frequency vacuum solution
  with an Einstein-null-dust or Einstein-massless-Vlasov evolution in 3+1.
- P4 (L434, unlabelled). "All existing proofs assume U(1) symmetry" is wrong as stated: I expect
  results without symmetry for special cases (null-dust limits in double-null gauge,
  geometric-optics constructions in generalized wave gauge), while the general conjecture stays
  open. Refuted if every rigorous high-frequency-limit result found assumes U(1) symmetry (or
  another symmetry).
- P5 (S4 null test). No numerical-relativity evolution has tested the cosmological coupling of
  black holes (k = 3) against horizon-mass growth in an expanding background; the rebuttals
  are analytic (exact solutions, junction conditions, observational counter-arguments).
  Refuted by an NR evolution of a black hole in an expanding background that measures the
  horizon mass against the scale factor with the coupling claim as its stated target.
- P6 (binary black holes in a particle dark-matter environment). No full-NR binary-black-hole
  evolution with collisionless particle dark matter exists; the closest are NR binaries in
  scalar-field (wave) dark matter and in gas, and the two-overdensity merger in a cluster of
  2611.12831 (black holes formed from the particles, not a binary in a dark-matter halo).
  Refuted by a full-NR binary evolved inside a particle or Vlasov dark-matter distribution.
- P7 (unlabelled claims about cited papers, L398-L443). Most are right as written; I expect one
  to three that need a precision (what the cited paper actually computes) and at most one
  outright correction.

Searches: knowledge base (`kb/bin/kb search`, read-only snapshot `db/current`), TeX sources of
the store, INSPIRE through `harness/bin/nrpic-fetch-arxiv --inspire-query` (one request at a
time), generic web searches. Nothing about the project or the user goes into a request.

## Entry 2, 2026-11-19 07:58: prediction for run R1 (scripts/check_numbers.py), before it runs

R1 recomputes the numbers of line 410 from first principles and from scalings printed in the
knowledge base, and the bound on the coupling index k that a vacuum black-hole lattice in
numerical relativity already gives (line 400; found during the S4 search, 1903.01490).
- R1a: M_H at T = 1 MeV with g_* = 10.75 lies in [1.2e5, 1.8e5] M_sun; the value implied by
  1607.00612 (M_BH = M_H / 3^(3/2), t = 2.4 g_*^(-1/2) (T/MeV)^(-2) s, i.e. M_H = c^3 t / G, the
  same formula as mine) agrees with mine within 3 per cent; 2109.04896 (1e5) within a factor 2;
  2006.16182 (~ m_P^2 t, 4.8e4) lower by a factor of about 3 (an order-of-magnitude "~").
  Refuted if M_H(1 MeV) is outside [1e5, 2e5] or the 1607.00612 value differs by more than 5 per
  cent.
- R1b: neutrino share 0.488 before and 0.409 after e+e- annihilation (both in [0.40, 0.50]).
- R1c: |k| <= 5.0e-4 from the lattice (0.1 per cent over a growth of e^2 in a).
Figure: left M_H(T) with the three printed scalings; right M/M_i against a/a_i for k = 0, 0.5,
3.11 with the lattice band.
