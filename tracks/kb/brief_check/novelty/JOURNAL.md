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

## Entry 2, 2026-11-19 07:45: prediction for run R1 (scripts/check_numbers.py), before it runs

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

## Entry 3, 2026-11-19 07:55: outcome of R1 and of the source predictions P1-P7

R1 = run kb-20261119-154605-3ee42d2 (`scripts/check_numbers.py`, 1 core, seconds; figure
`scratch/kb/kb-20261119-154605-3ee42d2/fig_numbers.png`, looked at):
- R1a held: M_H(1 MeV, g_* = 10.75) = 1.499e5 M_sun; 1607.00612 implies 1.461e5 (2.5 per cent
  lower, within the 3 per cent predicted); 2109.04896 1e5 (factor 1.5); 2006.16182 4.8e4 (factor
  3.1). At 1.5 and 2 MeV: 6.7e4 and 3.7e4.
- R1b held: 0.4884 and 0.4088.
- R1c held: abs(k) <= 4.9975e-4; a k = 3.11 black hole would have grown by a factor 503 over the
  same expansion.
- Figure: the left panel is right (the 1607.00612 scaling lies on top of mine); in the right panel
  the lattice band was invisible (1e-3 wide on a log axis) and the label crossed the k = 0.5
  line. Script changed (thick segment, label below); the rerun is R1' (entry 4).

Source predictions (from entry 1):
- P1 held (decoupling 1-2 MeV in the sources; M_H in band; share 0.41-0.49). The four
  [BACKGROUND] parts of line 410 are confirmed (CHECK #7-#10).
- P2 held, more strongly than predicted: no full-GR kinetic calculation found, and the field says
  so itself (2303.07980 :367, 2406.11417 :507-508). Not foreseen: the leading group expects
  suppression rather than enhancement, and names the opposite effect too.
- P3 held for the test itself, with a closer prior than predicted: 1505.02959 is a 3+1 NR test of
  Isaacson's radiation average (the trace part), more than "related" work.
- P4 held: the line-434 premise is wrong; and the forward conjecture is now a theorem without
  symmetry in generalized wave coordinates (2403.03470), which I had not predicted (I expected only
  special cases).
- P5 failed in part. No NR test framed against the coupling claim was found (as predicted), but
  the prediction "the rebuttals are analytic" missed an NR result that already bounds k for
  ordinary black holes: the vacuum lattice of 1903.01490 (masses constant to 0.1 per cent over a
  growth of e^2). The null test is partly done.
- P6 failed. I predicted no full-NR binary in collisionless particles exists and named the
  two-overdensity run of 2611.12831 as "black holes formed from the particles, not a binary in a
  dark-matter halo". Reading its section 4 shows a full-NR binary inspiral and merger inside a
  collisionless envelope, with angular-momentum transfer to the envelope measured: the broad item
  of line 1749 is done. Only the narrower configuration (pre-existing quasi-circular binary in a
  light dark-matter distribution, dephasing against vacuum) is open.
- P7 held: 33 statements, 2 corrected (lines 434 and 1749), 16 with a precision.

## Entry 4, 2026-11-19 07:56: prediction for R1' and R2, before they run

- R1': rerun of check_numbers.py after the figure change; numbers identical to R1 to all printed
  digits (pure arithmetic, no randomness). Refuted by any change in numbers.json.
- R2 (`scripts/check_package.py`): CHECK.md has 33 rows, 15/16/2/0, equal to its header; every
  locator in CHECK.md, ERRATA_ROWS.md and NOVELTY.md resolves (file present, lines within the
  file; metadata, run manifests, INSPIRE query labels with status ok); every arXiv id in the three
  files is in the store or among logged INSPIRE hits; the 22 quoted phrases stand at their lines.
  Two unregistered dry runs (scratch/kb/tmp/novelty/dry, to debug the script) already found and
  fixed one wrong file name (2409.01939 is `LRCosmo.tex`, not `main.tex`) and four non-locator
  words; the registered run is predicted to report no problem. Refuted by any entry in
  "problems". Figures: verdicts per line and label; closest papers per item by arXiv year.

## Entry 5, 2026-11-19 07:57: outcomes of R1', R2, R1''; cross-check with s5_s6; prediction for R2'

- R1' (kb-20261119-155605-d5dbd0d) held: numbers.json byte-identical to R1 (sha256 5ae5617f...).
  The figure now shows the lattice band, but its label crossed the k = 0 line; label moved,
  rerun R1'' (kb-20261119-155658-4acf70b): numbers.json identical again, figure looked at and
  clear (label below the band, inside the axes).
- R2 (kb-20261119-155610-7573cf0) held: 33 rows, 15/16/2/0 equal to the header; 80 + 40 + 53
  locators resolve; all 75 arXiv ids are in the store or among logged INSPIRE hits; 22 quotes at
  their lines; no problem. Figures looked at: verdicts per line and per label (the corrections sit
  on lines 434 and 1749; most rows are unlabelled paper claims) and the landscape of closest
  papers (the only "GR with particles" points are 2609.14218 for S5, which is non-relativistic
  matter, and 2611.12831 for the binary item).
- Cross-check: after my rows were final I read `../s5_s6/CHECK.md` rows 1-27 (lines 406-444,
  checked independently by another helper at the same time). Agreement on all facts and on the one
  correction (line 434). Verdict classes differ on eight statements; seven are CONFIRMED against
  CONFIRMED (precision), one is line 437 (CORRECTED there, CONFIRMED (precision) here, same
  evidence 1505.02959). Numbers agree (1.50e5 M_sun; 0.405 there with N_eff = 3, 0.409 here with
  N_eff = 3.045). Written into the README for the lead.
- After R2 the headers of CHECK.md and ERRATA_ROWS.md got run references and README.md was
  written. Prediction for the final run R2' of check_package.py: identical tally and no problem,
  with one more run-id locator in CHECK.md (81). Refuted by any problem.

## Entry 6, 2026-11-19 07:58: outcome of R2'; state at the end of the package

- R2' (kb-20261119-155812-87eced9) held: 33 rows 15/16/2/0; 81 + 40 + 53 locators resolve
  (one more run id in CHECK.md than in R2); 75 arXiv ids known; 22 quotes at their lines; no
  problem. Figures identical in content to R2's. Afterwards only the run id of R2' itself was
  written into the headers of CHECK.md and ERRATA_ROWS.md and into the README (its manifest
  exists); no row changed.
- Not done: the knowledge-base vector search (model not installed in this worktree; BM25 only);
  INSPIRE responses above 25 hits read only for the 25 most recent (five queries); conference
  proceedings and theses seen only as titles; the S8 sentence of line 441 had one query only.
  No card was used; no run is pending.
