# Journal of work package s311 (brief lines 267-278, section 3.11)

Owner kb (helper), wave 3a, branch `kb/brief-check`. Times from `date` (PST).

## Entry 1, 2026-11-19 07:40: predictions before the source checks

Read so far: CLAUDE.md, the charter to "Owners", decisions 0010, 0016, 0017, brief lines
30-68 and 267-278, `coord/BRIEF_ERRATA.md` (row 1.5 already covers line 275), Track F's
`tracks/F-hills/novelty/{NOVELTY.md, scope/SCOPE.md, search/SEARCH_LOG.md, README.md}` on
branch `track/F-hills`, and the titles (not the abstracts) of the papers of lines 269-270.
All 52 cited arXiv ids are in the store (`kb-data/raw/arxiv`, metadata in
`kb-data/meta/arxiv-api`); nothing needs fetching.

Predictions (what would refute each in brackets):

- P1 (l. 269, tidal radius). r_t ≈ a_b (M/m_b)^(1/3) is stated, without an exact prefactor,
  in the restricted three-body papers (0911.1136) and the hypervelocity-star papers
  (astro-ph/0309084). [Refuted if the sources define r_t with a different power of M/m_b.]
- P2 (l. 269, ejection speed). v_ej ~ v_b (M/m_b)^(1/6) holds as a scaling with an O(1)
  prefactor (about sqrt(2) and a dependence on the member masses and phase), with v_b the
  binary's orbital speed sqrt(G m_b/a_b). [Refuted if a source gives another exponent, or
  if the 1/6 belongs to a different definition of v_b.]
- P3 (l. 269). The other member is captured on a bound, highly eccentric orbit
  (1 - e of order (m_b/M)^(1/3)); Hills 1988 (Nature) has no arXiv version (1988 predates
  arXiv) and is cited as such by the sources. [Refuted if the sources say both members can
  stay bound in the typical case, or cite an arXiv version.]
- P4 (l. 269). The six hypervelocity-star / S-star papers are on topic (theory: Yu and
  Tremaine; discovery: Brown et al. 2005; velocity spectrum: Bromley et al.; Zhang, Lu, Yu
  twice; Generozov and Madigan). [Refuted if one is about something else.]
- P5 (l. 270, "[titles VERIFIED]"). Titles match; the grouping "restricted three-body /
  full three-body, collisions, double disruptions / repeating partial disruptions" is
  right for most entries, with one or two misplaced (for example 0909.1959 may use
  restricted or N-body plus SPH; 1307.1134 is a velocity-distribution paper).
  [Refuted (in the good direction) if every entry fits its group as stated.]
- P6 (l. 271, "[titles VERIFIED]"). Titles match; at least one entry in "compact binaries
  and massive black holes" or "waveform effects" is about a bound hierarchical triple
  (Kozai-Lidov, Doppler or lensing of a binary orbiting a massive black hole) rather than
  a passage; that is still within "binaries near a massive black hole". [Refuted if an
  entry has nothing to do with binaries near a massive black hole.]
- P7 (l. 272). 2404.16270: "about 100 gravitational radii" confirmed (Track F found it at
  `article.tex` l. 194); 2402.02178: Kerr, parabolic, full NR intractable confirmed
  (Track F: `main.tex` l. 216-226); 1203.6185 perturbative confirmed; 2508.03463 and
  2601.04870 are SPH of white-dwarf binaries and intermediate-mass black holes, but
  "including spin" may hold for one of the two only; the six single-star papers may
  include one that is not about kicks or spin. [Refuted if a number or attribution differs.]
- P8 (l. 273, full NR). 0710.0879, 0711.1165, 1004.1353 are three-or-more black-hole NR
  evolutions; 2505.01495 is a 25-black-hole cluster. Of the "stellar tidal disruption in
  full GR" papers at least one is GR hydrodynamics on a fixed background or with
  approximate self-gravity rather than full GR. [Refuted if all three solve the full
  Einstein equations with the star.]
- P9 (l. 273, [TO VERIFY]). The novelty statement stands as written for the Hills geometry
  (Track F's search of 2026-11-15), with the precision that full-NR binary + heavier hole
  on a bound orbit exists (2406.11985, q = 4 and 9, not separated). An update of the
  citation queries of 2406.11985 and 2505.03934 finds nothing new since 2026-11-15.
  [Refuted if a full-NR tidal separation by a heavier hole is found.]
- P10 (l. 274). 1812.01930, 1908.09752, 2006.11172 are about PBH-binary formation and
  disruption by third bodies / the merger rate; 1805.09034 treats dark-matter dresses of
  PBH binaries. [Refuted if one of them does not treat third-body perturbations or dresses.]
- P11 (l. 275). Covered by errata row 1.5 and Track F's run A (F-hills-20261115-045435-f62d553);
  not repeated. The Peters formula is not on arXiv (1964); a paper in the store quotes it.

## Entry 2, 2026-11-19 07:55: prediction for run N (update of the novelty queries)

The four INSPIRE queries of Track F that matter most for line 273 were repeated through
`harness/bin/nrpic-fetch-arxiv --inspire-query` at 2026-11-19 15:32-15:33 UTC (citations of
2406.11985 = recid 2799952 and of 2505.03934 = recid 2919080; title queries k02 "Hills
mechanism / tidal separation" and k01 "three black holes"). The run compares them record by
record with Track F's raw answers of 2026-11-15 (`scratch/F-hills/tmp/inspire/<label>/response.json`).

Prediction: totals unchanged or larger by at most one or two; any record only in the new answer
is not a full-NR calculation of a binary separated by a heavier black hole. Refuted if a new
record is such a calculation (then line 273 becomes CORRECTED), or if a record of 2026-11-15
disappeared (then the comparison is not like for like and I say so).

## Entry 3, 2026-11-19 08:05: outcome of run N; prediction for run X (number check)

Outcome of run N (`kb-20261119-153345-ed7ee04`): all four totals unchanged (citations of
2406.11985: 9; of 2505.03934: 8; k02: 22; k01: 19), and record for record the same sets: no
record only in the new answers, none dropped. Prediction P9 (second half) holds. The novelty
statement of line 273 stands as of 2026-11-19 for these four queries; the other queries of
Track F were not repeated.

Source checks done so far (outcomes of P1-P8 and P10 go to entry 4 with the tally).

Prediction for run X (`scripts/check_numbers.py`, numbers transcribed from the sources):
- X1. Yu and Tremaine (astro-ph/0309084 `ms.tex:516-526`) report Hills' rms ejection speed as
  v' = 130 to 160 km/s in v_ej = v' (M/m*)^(1/6) (a_b/0.1 au · Msun/m*)^(-1/2). Written as
  v_ej = k v_b q^(1/6) with v_b = sqrt(G m_b/a_b), m_b = 2 m*, q = M/m_b, the prefactor k lies
  in [0.7, 1.5]. Refuted if k is outside [0.5, 2] (then "v_ej ~ v_b q^(1/6)" hides a large
  constant and must say so).
- X2. The same formula reproduces their quoted 5e3 and 0.9e3 km/s (M = 3.5e6 Msun, m* = 1 Msun,
  a_b = 0.01 and 0.3 au; `ms.tex:549-555`) to within the 130-160 band, i.e. ratio 0.8-1.3.
- X3. 2404.16270: r_t/r_g = (a_0/r_gb) q^(-2/3) with M = 1e6, m_b = 1 Msun, a_0 = 0.01 au gives
  101.3 (their `article.tex:172`) within 0.1 per cent, and r_t/(4 r_g) gives their
  beta_max = 25.3 (`article.tex:212`) within 0.3 per cent.
- X4. Peters as quoted in 1805.09593 (`revised_version.tex:202-204`): for equal masses
  (5/256) m^3/(m1 m2 m) = 5/64 exactly; their second line, 6.0e3 Gyr for m = 60 Msun and
  a = 1 au, is reproduced within 2 per cent; the brief's "about 6×10^3 GM/c^3" at a_b = 30 r_gb,
  q = 10 is 6328 (Track F's number).
Constants: GM_sun = 1.3271244e20 m^3 s^-2 (IAU 2015 B3 nominal), au = 1.495978707e11 m
(IAU 2012 B2), c exact, Julian year [BACKGROUND].
