# Journal of work package s31_32 (brief lines 140-163 and items 3, 4 of lines 1747-1748)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`.

## Entry 1 (2026-11-19 06:2x PST): set-up, metadata pass, predictions

Done before this entry: merged main (already up to date), read CLAUDE.md, the charter to
"Owners", decisions 0010, 0016, 0017, `coord/BRIEF_ERRATA.md`, brief lines 30-68, 138-165,
1738-1752, and (to know what item 4 bears on) the M3 paragraph at brief line 510-512 and the
dGREM hits of a grep of the brief (lines 96-97, 512, 700, 1785-1786).

All 56 papers cited in lines 144-162 are in the store (`kb-data/raw/arxiv/<id>/<v>/src`,
old-style ids as `gr-qc_9804040` etc.). Titles, authors and abstracts were dumped from
`kb-data/meta/arxiv-api/` with `scripts/meta_dump.py` (outputs in
`scratch/kb/tmp/s31_32/meta{1,2,3}.txt`). The abstracts were read; the predictions below
are written after that reading and before any check at the TeX source.

Predictions (each is checked at the TeX source; a locator file:line is required for a
CONFIRMED or CORRECTED verdict; what would refute the prediction is in brackets):

P1. arXiv:1409.5176 (Akbarian-Choptuik) is NOT a particle-in-cell study: it integrates the
    Vlasov equation directly in phase space. So the brief's "PIC studies ... 1409.5176"
    (line 156) is wrong. [Refuted if the source describes particles/shells as the method.]
P2. arXiv:1611.03437 (Daverio, Dirian, Mitsou 2016) treats a perfect fluid, not particles,
    so it does not belong in the "Full NR + particles (Einstein-Vlasov)" row (line 149).
    [Refuted if the paper evolves N-body particles or a Vlasov distribution.]
P3. arXiv:2307.15194 is SPH (a fluid discretisation), not Einstein-Vlasov; the row's
    "SPH particles" is a fair label but the paper's matter model is a fluid. [Refuted if the
    paper says its SPH particles are collisionless (pressureless, interpenetrating).]
P4. GRAMSES (1905.08890): fully constrained formulation, CMC slicing plus minimal
    distortion, ten elliptic equations, tensor modes neglected by the conformal-flatness
    approximation. "Does not evolve the radiative degrees of freedom" is CONFIRMED.
    [Refuted if GRAMSES evolves the tensor (hyperbolic) equations.]
P5. gevolution (1604.06065) evolves the tensor perturbation h_ij with a wave equation
    (hyperbolic); "elliptic/parabolic solves" (line 145) is then incomplete. [Refuted if
    gevolution's h_ij is solved by a constraint-type (elliptic) equation.]
P6. arXiv:1711.06681 (East, Wojtak, Abel) evolves a pressureless fluid with the generalized
    harmonic formulation; 1511.05124 (Bentivegna-Bruni) is BSSN plus dust. The "dust fluid"
    row is then right for both. [Refuted if either uses particles.]
P7. arXiv:2003.08014 (code comparison) includes codes that are not full NR (gevolution,
    GRAMSES); citing it as the code comparison of the "Full NR + dust fluid" row is
    imprecise. [Refuted if all compared codes are full-NR fluid codes.]
P8. arXiv:1810.05203 (Giblin et al., "collisionless matter") uses particles in
    CosmoGRaPH. [Refuted if it uses a fluid.]
P9. arXiv:2409.01939 is published in Living Reviews in Relativity. [Refuted if the source or
    the INSPIRE record names another journal or none.] Expectation: the TeX source may not
    say; then NOT FOUND in the source, check INSPIRE.
P10. arXiv:1901.04498 (East) studies prolate AND oblate spheroids. Uncertain (50 per cent):
    the abstract mentions "prolate" only. [Refuted if no oblate case appears.]
P11. math/0209336 states that the source terms enter the field equations pointwise, unlike
    Vlasov-Poisson where they are smoothed by the inverse Laplacian. [Refuted if absent.]
P12. "No universal critical solution" is stated in gr-qc/0601112; Type I with static critical
    solutions in gr-qc/0107076 and 1409.5176; finite mass at threshold in gr-qc/9804040.
P13. Item 4: the original dGREM paper (2111.05282) leaves hyperbolicity open; 2211.13659
    shows symmetric hyperbolicity for the equivalent vacuum pure-tetrad TEGR system on the
    constraint surface with suitable gauge, not for the system with matter; no paper
    evolves dGREM numerically as of 2026-11-19 (2504.15978 and 2611.12831 evolve Z4c).
    [Refuted if a citing paper reports a strong-hyperbolicity proof with matter or a
    numerical dGREM evolution.]

## Entry 2 (2026-11-19, about 06:30-07:20 PST): outcomes of P1-P13

Checked at the TeX sources (locators in CHECK.md; scripts `scripts/locate.py` with the spec
files in `specs/`, outputs in `scratch/kb/tmp/s31_32/loc_*.txt`). INSPIRE queries (through
`nrpic-fetch-arxiv --inspire-query`, sequential): citations of 2111.05282 (recid 1964693,
15 records), of 2211.13659 (recid 2593379, 7 records), GRAMSES papers (two queries, 6 records
each). A first query `refersto:arxiv:2111.05282` was not understood by INSPIRE (25290
unrelated hits) and was replaced by the record-id form; it is kept in the store as served.
Fetched two missing sources: 2602.01830 (v2) and 2505.00286 (v3).

- P1 CONFIRMED: 1409.5176 integrates the Vlasov equation directly in phase space
  (`paper.tex:132-133, 711`). Brief line 156 corrected (CHECK #40).
- P2 CONFIRMED: 1611.03437 is a perfect-fluid scheme (`Main_v3.tex:41, 330`). CHECK #30.
- P3 REFUTED in part: 2307.15194 presents its dust SPH particles as collisionless matter
  followed past shell crossing (`aipsamp.tex:280, 741`), so the brief's "SPH particles" in the
  Einstein-Vlasov row is defensible; kept as CONFIRMED with a precision (CHECK #32).
- P4 CONFIRMED, with more detail than predicted: conformal flatness plus A_TT = 0, CMC with a
  fiducial H, minimal distortion; also two numerical approximations of the particle update
  (CHECK #60).
- P5 CONFIRMED: gevolution's h_ij obeys "a hyperbolic wave-equation" (`compendium:487`).
  CHECK #9 corrected.
- P6 CONFIRMED: 1711.06681 generalized harmonic plus HRSC fluid; 1511.05124 McLachlan BSSN
  plus dust in synchronous-comoving gauge.
- P7 CONFIRMED: 2003.08014 compares gevolution, GRAMSES, Einstein Toolkit, CosmoGRaPH (with
  particles). CHECK #25 corrected.
- P8 CONFIRMED with a precision: N-body in harmonic and Newtonian gauges, a fluid in
  comoving-synchronous gauge (CHECK #29).
- P9 CONFIRMED through INSPIRE (Living Rev. Rel. 28 (2025) 5); the TeX source says "this
  Living Review" (`LRCosmo.tex:1106`). My expectation that the source would not say it was wrong.
- P10 REFUTED (the 50 per cent case went the other way): 1901.04498 has prolate data only;
  "oblate" refers to the ringing horizons. Brief line 159 corrected (CHECK #51).
- P11 CONFIRMED (`math_0209336 main.tex:369-376`), with the wording "integrated in
  space(time)" rather than "elliptic operator".
- P12 CONFIRMED, with the review's reservation (Vlasov listed as type "I?") and the early
  hint of universality in gr-qc/0107076 (`paper.tex:853-856`) that later work contradicts.
- P13 CONFIRMED: no hyperbolicity proof with matter, no numerical dGREM evolution found;
  new since the brief: 2211.13659 is at v4 (2025-10) with the vacuum symmetric-hyperbolic
  result and its caveats, and 2602.01830 (linearised Hamiltonian TEGR: non-hyperbolic sector
  removable by gauge fixing).

Not done: field-by-field comparison of the titles of lines 144-162 with §16 (out of scope;
every identifier resolves to the paper the brief means). The earlier 1999 3D paper of Shibata
cited by GRAMSES and Giblin et al. was not looked up.

## Entry 3 (2026-11-19 07:2x PST): prediction for the registered figure run

The run of `scripts/fig_verdicts.py` on the committed CHECK.md is a consistency test: it
asserts consecutive row numbers and classifies every verdict. Prediction (from an unregistered
development run into `scratch/kb/tmp/s31_32/dev/`): 61 rows; CONFIRMED 45, CONFIRMED with a
precision 9, CORRECTED 5 (rows 9, 25, 30, 40, 51), ANSWERED 2, NOT FOUND 0. Refuted if the
tally differs or the script raises on an unknown verdict.

Outcome (run kb-20261119-143638-79805cd, processors, one core, exit 0): prediction CONFIRMED,
tally identical (61 rows: 45, 9, 5, 2, 0; corrected rows 9, 25, 30, 40, 51). Figure
`figures/fig_verdicts.png` (copy of the run's output) looked at: left, verdicts per brief line,
the corrections sit on lines 145, 148, 149, 156, 159; right, per label, the 5 corrections are
3 on cells labelled [BACKGROUND] (via line 152) and 2 on unlabelled claims; none on [VERIFIED].
