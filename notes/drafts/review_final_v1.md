# Referee report on the last-written parts of the NRPIC manuscript (final pass, v1)

Date: 2026-11-14. Scope: introduction.tex (paragraphs at lines 11 and 13, outline at 15);
self_gravity.tex:120-150 (subsection "Collapse and merger inside a cluster", Figs. 16 and 17);
conclusions.tex; abstract (title.tex:9); appendix_sampling.tex:77 (last sentence);
method.tex:195-197 (pointers). Built PDF: paper/main.pdf of 10:16 (newer than every source;
last source edit 10:14), 35 pages; Fig. 16 = fig:overdensities (p. 23), Fig. 17 =
fig:overdensities_radius (p. 24), Table I = tab:setups (p. 27), Table VII =
tab:outcomes_migration (p. 32), Table VIII = tab:outcomes_stated_radius (p. 33).

Sources: notes/results_brief_selfgravity.md ("brief", items cited as D1 ... D14, C4 ...);
docs/TESTLOG.md ("TL", entry time); Tables I, II, VII, VIII; the two figure PNGs;
refs/arxiv_2611.12831/src/main.tex ("orig.", line); paper/data/overdensities.npz and
problems/kerr/results/kerr_summary.json for spot checks.

The stated-radius run (Table VIII, brief D14) is still running; differences between its 78 M and
86 M numbers are not reported. Every prose statement about it was checked against the state so far.

Counts: FA 19, FB 12, FC 8, FD 10 (+ conclusions assessment), FE 6.

---------------------------------------------------------------------------------------------

## A. Facts

### FA1. Prolate deficit attributed to particle number (introduction.tex:13)
- Sentence: "Its apparent-horizon mass stays a few percent below ... with a spherical control."
- Wrong: "a measurement limitation at this particle number" names a cause. The spherical control
  shows the opposite: a random sample of 10^4 loses only a few tenths of a percent, so random
  sampling alone does not explain the deficit. How the deficit splits between particle number
  and cell size is not determined. "stated with a spherical control" is also unclear.
- Source: self_gravity.tex:56; brief C4 ("a limitation found here"), C6.
- Rewrite: "Its apparent-horizon mass stays a few percent below the total mass. A spherical control
  with a random sample loses far less, so the deficit belongs to the prolate collapse itself."

### FA2. "The pair transfers" angular momentum (self_gravity.tex:137) -- suspect (2) confirmed
- Sentence: "Across the inspiral, the pair transfers ... to the surrounding envelope."
- Wrong: only the envelope's L_z was measured (from -0.003 at t = 0 to +0.032 at 57 M; M/128
  +0.038). The orbital angular momentum of the pair was not, so a transfer is not shown. Ref. measured
  both sides (orig. 1358); we did not. No table row or figure holds the envelope L_z.
- Source: brief "Not established", fourth item ("the text may say that the envelope gains angular
  momentum about the orbital axis, not that the pair transfers it"); brief D10; TL 02:35.
- Rewrite: "During the inspiral, the envelope gains positive angular momentum $L_z$ about the orbital
  axis, as in Ref.~\cite{Wu:2026nrpic}." Add a Table VII row: envelope L_z about the origin at t = 0
  and at the first common horizon (-0.003, +0.032; M/128 +0.038).

### FA3. Spins of A and B attributed to discrete momenta (self_gravity.tex:128) -- suspect (1) confirmed
- Sentence: "Discrete particle momenta at this sample size ... near-zero spins in Ref."
- Wrong: the cause was never tested. The brief argues that a cold clump with one bulk velocity
  has no spin about its own center, whatever the sample. No table or figure gives these spins.
- Source: brief D3c ("The text states the spins and gives no cause"); D5 (0.06, 0.05 before the
  merger); overdensities.npz (A, B: 0.022, 0.023 at first detection).
- Rewrite: "The finder gives black hole A and black hole B small dimensionless spins, well above
  the near-zero spins in Ref.~\cite{Wu:2026nrpic} (Table~\ref{tab:outcomes_migration})." Add a
  Table VII row: chi of A, B after formation; at the last search before the common horizon
  (0.007-0.03; 0.06, 0.05 | of order 1e-5).

### FA4. "Every self-gravitating test in kind" (conclusions.tex:3)
- Sentence: "That implementation reproduces ... recovers every self-gravitating test in kind."
- Overstated. In the near-critical test, the compressed model collapses where Ref. oscillates.
  The expanded model oscillates about another lapse with another rhythm, and which perturbation
  Ref. applied cannot be decided. The abstract's own list leaves this test out. Neither envelope
  radius reproduces the published merger outcome.
- Source: self_gravity.tex:111, 141; brief B7; title.tex:9.
- Rewrite (two sentences): "That implementation reproduces the single-particle geodesic
  benchmarks to all published digits. It recovers dust collapse, prolate collapse, the cluster
  sequence, migration, and the merger inside a cluster in kind."

### FA5. Fig. 17 caption misdescribes its markers (self_gravity.tex:146) -- suspect (5) confirmed
- Sentence: "With the stated radius ... Open symbols mark merger time and remnant mass in Ref."
- Wrong: the open circles mark Ref.'s masses of A and B at 10 M and 60 M and of the common
  apparent horizon at 64.16 M and 100 M. Ref.'s merger time is the tick at the top of each panel.
  The caption also omits:
  - the line styles: orange solid is the stated radius, blue dashed the self-consistent radius
    ("labeled" says nothing);
  - the dotted line at the total mass.
  The caption runs to eight typeset lines (FE1).
- Source: fig_overdensities_radius.png; scripts/fig_overdensities_radius.py:22, 54-55.
- Rewrite (45 words, about five to six lines): "The black holes widen their orbit at nearly fixed
  mass with the stated envelope radius (orange, solid) and merge with the speed-matched radius
  (blue, dashed). Top: separation. Middle: apparent-horizon masses. Bottom: envelope rest mass
  outside the black holes. Circles, ticks: masses, merger time of Ref.~\cite{Wu:2026nrpic}."

### FA6. "Post-merger outcome" used for a run without merger; mechanism in the conclusions
- Locations:
  - title.tex:9: "The outcome after merger ... orbital speed conflict."
  - introduction.tex:13: "The post-merger outcome ... stated orbital speed."
  - conclusions.tex:7: "In a relativistic cluster ... fix the post-merger outcome." and "Through
    envelope gravity and accretion, ... a wide black hole orbit."
- Wrong:
  - With the stated radius no merger happens. The radius decides whether the pair merges, not
    only the state after a merger.
  - "Through envelope gravity and accretion" names a mechanism nobody tested. The two-body
    estimate gives a different picture: with the stated radius only 0.0016 M of envelope lies
    inside the orbit, so the companion sets the circular speed (0.103 against the stated 0.1332).
    That estimate supports the outward motion "as a two-body estimate, no more".
  - In the abstract, "where" and "conflict" are vague.
- Source: Table VIII (no common horizon; never searched); TL 09:24, 09:33; brief D14.
- Rewrites:
  - Abstract: "The published envelope radius and orbital speed disagree. With the radius that fits
    the speed, the remnant swallows the envelope; with the stated radius, the black holes settle
    on a wide orbit."
  - Introduction: "The outcome depends on the envelope radius, and the published radius disagrees
    with the published orbital speed."
  - Conclusions: "Initial data for black holes forming inside a cluster need an orbital speed that
    is circular in the chosen envelope. The two published values give a remnant that swallows the
    envelope or a widening orbit, and the published run lies between them."

### FA7. "Exceeds the remnant mass of Ref. by about half" (self_gravity.tex:139) -- suspect (4) confirmed
- Sentence: "Its final apparent-horizon mass ... by about half (Table~VII)."
- Wrong: 1.0255/0.6474 = 1.58, so the excess is about three fifths, not half. "Reaches the total
  mass" also clashes with "lies above M by a few percent" four sentences later.
- Source: Table VII row "Common horizon M_AH/M, chi at t = 70, 80, 90, 100M" (1.0255 against
  0.6474); brief D7, D13.
- Rewrite: "Its final apparent-horizon mass $M_{\rm AH}$ therefore slightly exceeds the total mass
  $M$, more than one and a half times the remnant mass of Ref.~\cite{Wu:2026nrpic} (Table)."

### FA8. Mechanism for the spin drop; non-conservation of S not stated (self_gravity.tex:139)
- Sentence: "As low-angular-momentum envelope matter falls in, ... published final spin (Fig.; Table)."
- Problems:
  - The clause names a mechanism, but the horizon S itself halves (0.0600 at 57 M to 0.0296 at
    80 M) and then rises to 0.0890 at 100 M. Infall of low-angular-momentum matter does not
    describe that.
  - The brief explains the lower final chi by arithmetic, mainly the larger final mass:
    0.49 = (0.6474/1.0255)^2 x 0.0890/0.0718.
  - The text never says that S is not conserved, whereas Ref. finds J conserved to 2 percent
    (orig. 1360). This is a documented difference that goes unstated.
- Source: brief D10; Table VII rows "S of the common horizon ..." and "Common horizon M_AH/M, chi".
- Rewrite (two sentences): "The dimensionless spin $S/M_{\rm AH}^2$ ends near half the published
  final value, mainly because the final mass is larger (Fig.; Table)." / "The horizon spin $S$
  first halves and then recovers, while $S_z$ plus $L_z$ of the surviving macroparticles stays
  nearly constant (Table)." The second replaces the current sentence "Across post-merger
  accretion, ...".

### FA9. "Form at nearly the same time and mass" (self_gravity.tex:141) -- suspect (3) confirmed as ambiguous
- Sentence: "With the larger envelope radius ... form at nearly the same time and mass (Fig.; Table)."
- True of A against B. Read against the self-consistent run it is wrong: there the black holes
  form at 10.50 and 10.56 M with 0.0976 and 0.0992 M, here at 9.06 to 9.19 M with 0.0877 to
  0.0907 M. That is about 1.4 M earlier and a tenth lighter. Line 128 calls a shift of the same
  size between meshes "earlier at M/128".
- Source: Table VIII row 1 against Table VII row 1.
- Rewrite: "With the larger envelope radius stated in Ref.~\cite{Wu:2026nrpic} ($M/64$), black hole A
  and black hole B form somewhat earlier and lighter than in the speed-matched envelope (Fig.;
  Tables~\ref{tab:outcomes_migration} and \ref{tab:outcomes_stated_radius})."

### FA10. "Initial masses close to the published values" (self_gravity.tex:128)
- Sentence: "Those apparent horizons appear somewhat later ... close to the published values (Fig.; Table)."
- The cited table contradicts the claim as printed. It gives 0.0976 and 0.0992 at 10.50 and
  10.56 M, against Ref.'s 0.0880 and 0.0877 at t = 10 M: 11 to 13 percent apart, at different
  times. Ref.'s column for the formation masses reads "--". The claim holds at equal times, but
  no table shows it:
  - M/128 gives 0.0855 and 0.0856 at 10.02 M, a few percent below Ref.;
  - M/128 at 10.48 M (0.0964) matches M/64 at 10.5 M (0.0976).
- Source: Table VII rows 1-2; brief D2; overdensities.npz (m128_ahA/B).
- Rewrite: "At $t = 10M$ the $M/128$ masses $M_{\rm AH}$ lie a few percent below the published values
  (Fig.~\ref{fig:overdensities}; Table~\ref{tab:outcomes_migration})." Add the M/128 masses at
  10 M to Table VII.

### FA11. "Begins removing core particles shortly before" (self_gravity.tex:128)
- Sentence: "Lapse excision begins removing core particles ... black hole B (Table~VII)."
- Understated. When the finder first detects the horizons (10.5 M), only 789 and 769 of the
  2000 macroparticles of each overdensity remain. Lapse excision has removed about three fifths
  of each overdensity, not its core.
- Source: overdensities.npz m64_snap_n at 10.5 M; Table VII row "Macroparticles removed ...:
  before the first apparent horizon 2448 (0.163)"; Fig. 16 bottom right.
- Rewrite: "By the first detection of the apparent horizons of black hole A and black hole B, lapse
  excision has removed more than half of each overdensity (Fig.~\ref{fig:overdensities}, bottom
  right; Table~\ref{tab:outcomes_migration})."

### FA12. "Two evolutions" are three runs (self_gravity.tex:124)
- Sentence: "Two evolutions are therefore reported: ... and one at $M/64$ with the stated radius."
- Wrong count: M/64 and M/128 with the self-consistent radius, plus M/64 with the stated radius,
  make three runs. The sentence is also a lab-report sentence (5.3).
- Rewrite: "Two envelopes are therefore evolved: the speed-matched one at finest cells $M/64$ and
  $M/128$, and the stated one at $M/64$."

### FA13. "Drifts slightly out of the orbital plane"; the stated-radius drift is unmentioned (self_gravity.tex:137)
- Sentence: "At $M/64$ the binary midpoint drifts slightly ... stays near the plane (Table~VII)."
- The drift is 0.59 M, about a tenth of the initial separation and some forty finest cells, so
  "slightly" understates it. The stated-radius run (same M/64 mesh) drifts to 1.34 M by 86 M
  (Table VIII row 5). The text never reports that drift, yet line 150 lists the M/64 drift as
  open.
- Source: Table VII last row; Table VIII row 5; brief D11, D14; TL 23:10.
- Rewrite (two sentences): "At $M/64$ the midpoint of the pair drifts out of the orbital plane by
  about a tenth of the initial separation and then levels off, and further with the stated radius
  (Tables~\ref{tab:outcomes_migration} and \ref{tab:outcomes_stated_radius})." / "At $M/128$ it stays
  near the plane."

### FA14. "Circular speed in this envelope ... no common apparent horizon found" (self_gravity.tex:141)
- Sentence: "The stated speed exceeds the circular speed ... found to the end of the run."
- Problems:
  - "Found" implies that searches ran. The finder never searched, because the trackers never
    came within 0.24 M.
  - In this sparse envelope the companion sets the circular speed, so "in this envelope" points
    the reader the wrong way.
  - The sentence holds for the state so far. The separation is 9.24 M at 86 M and falls by about
    0.01 M per M, while a common-horizon search needs 0.24 M. So it also holds at 100 M if
    nothing changes.
- Source: Table VIII rows 3-4 ("none ..., never searched"); TL 09:33.
- Rewrite (two sentences): "The stated speed exceeds the circular speed of the pair, which the
  companion sets in this sparse envelope." / "The pair moves out to a wide orbit, and its trackers
  stay too far apart for a common-horizon search
  (Table~\ref{tab:outcomes_stated_radius})."

### FA15. Why the second removal rule is needed (self_gravity.tex:126)
- Sentence: "With lapse excision alone on these meshes, ... removal rule of Sec.~\ref{sec:numerical_methods}."
- Incomplete: "requiring" hides the reason. Without the rule the evolution fails three to five M
  after the black holes form. Method.tex:195 does not say so either.
- Source: brief D3b; TL 18:30.
- Rewrite (two sentences): "With lapse excision alone, matter lingers inside these black holes
  and the evolution fails soon after they form." / "The removal rule inside a found apparent
  horizon (Sec.~\ref{sec:numerical_methods}) cures this."

### FA16. Prolate open question presupposes a purely numerical deficit (conclusions.tex:9) -- suspect (6)
- Sentence: "How does the apparent-horizon mass deficit ... across the axial caustic stage?"
- The wording follows brief C6 and self_gravity.tex:56, but it presupposes that the whole deficit
  is numerical error. The same section (line 56) and brief C4 state that M_MS - M_AH also
  contains radiated gravitational-wave energy, which the slice diagnostic cannot separate.
- Rewrite: "How much of the apparent-horizon mass missing after prolate collapse is radiated, and
  how much shrinks with more macroparticles or finer cells?"

### FA17. One tetrad gauge for all benchmarks (title.tex:9)
- Sentence: "Single-particle geodesic benchmarks match all published digits ... pusher is fixed."
- Misleading. The digits are confirmed (see Checked), but different gauges reproduce the two
  published runs: the symmetric gauge on the analytic Kerr-Schild metric, the (x, y, z) Cholesky
  gauge on the mesh (test_particles.tex:30). "Is fixed" in the singular suggests one gauge.
- Rewrite: "Single-particle geodesic benchmarks match all published digits once the unstated
  tetrad gauge of each published Boris-pusher run is identified."

### FA18. "Separated true causes from guesses" (conclusions.tex:11)
- Sentence: "Predictions written before dedicated control runs ... several initial explanations failed."
- Overstated. Many causes remain not determined (self_gravity.tex:100, 102, 139, 150;
  conclusions p. 4). Assembly reports refutations (assembly.tex: seven explanations refuted).
- Rewrite: "Predictions written before dedicated control runs refuted several initial explanations
  and confirmed others."

### FA19. "About a tenth of the total mass" per overdensity (self_gravity.tex:122)
- Sentence: "Each collapsing overdensity holds about a tenth of the total mass $M$."
- Each overdensity holds 0.12 M (Table I), which is closer to an eighth. The black holes
  themselves start near a tenth, so the sentence mixes the two.
- Rewrite: "Each collapsing overdensity holds about an eighth of the total mass $M$."

---------------------------------------------------------------------------------------------

## B. Consistency

### FB1. One name for the radius, one for the cluster
- Variants in use:
  - "self-consistent radius/envelope": self_gravity.tex:124, 128, 146; the figure label
    (scripts/fig_overdensities_radius.py:54); appendix_sampling.tex:77 ("self-consistent host
    radius").
  - "speed-matched radius": introduction.tex:13; conclusions.tex:7.
  - "host radius / host cluster / host-envelope radius / host-radius evolutions":
    introduction.tex:11; appendix_sampling.tex:77; conclusions.tex:7; self_gravity.tex:150.
- Recommendation: "speed-matched radius", and "envelope" for the cluster.
  - In numerical relativity, "self-consistent initial data" means data that solve the
    constraints. Conclusions p. 4 asks about exactly such data, so the current term invites a
    misreading.
  - "host" already means AthenaK ("host code") in the same paragraphs (introduction.tex:11,
    conclusions.tex:7).
  - Fig. 17 is being regenerated anyway, so the label in the script can change at no cost.
- Define the term once at self_gravity.tex:124: "the speed-matched radius, at which the stated
  speed is circular".

### FB2. Constraint violation of the initial data: presupposed, never stated, and contradicted elsewhere
- conclusions.tex:9: "Would initial data that solve the constraints ... above the total mass?"
  presupposes that the present data do not solve them.
- No section says so. method.tex:218-221 and appendix_sampling.tex:3 state that the superposed
  potentials "solve H = 0".
- The numbers show a sizable violation. Table VII row "||H|| at t = 0; ..." gives 5.82 at t = 0.
  That is larger than the second peak during the envelope infall (5.36 at 77 M; brief D12) and
  three times the largest value of the lattice dust collapse with finest-level clouds (1.9;
  Table IV).
- self_gravity.tex:139 says only that ||H|| "peaks during initial collapse and rapid envelope
  infall". The infall peak is not in Table VII.
- Fix, in three parts:
  - Subsection, replacing the current ||H|| sentence: "The superposed initial slice already
    carries a sizable Hamiltonian-constraint norm $\|\Ham\|$, which peaks during the initial
    collapse, rises again during the envelope infall, and then decays
    (Table~\ref{tab:outcomes_migration})." Add the second maximum to the row.
  - Method and appendix: limit "solve H = 0" to the continuum conformal sources. Which part the
    sampled macroparticles break is not determined in the sources.
  - Conclusions: "Does the constraint violation of the superposed initial slice cause the
    post-merger apparent-horizon mass excess above the total mass?"

### FB3. The M/128 run is missing from the setup tables
- self_gravity.tex:124 names finest cells M/64 and M/128 and cites Tables I and II. Both list
  only the M/64 configuration:
  - Table I row "Two overdensities: ...", "adaptive, 1/64-1/2";
  - Table II row "Two overdensities", "1/64: 0.2 about each puncture".
- The M/128 run differs: domain +-256 M, finest region 0.15 then 0.125 M, and it stopped at
  61.57 M. Brief D (setup) says "the setups table does" give the regions.
- Add it as a control run in parentheses, as the Table I caption provides: L = 256 M, 1/128,
  end 61.6 M, and in Table II "1/128: 0.15, then 0.125 about each puncture".

### FB4. Every "Table" and "Fig." pointer in the new subsection

Pointers whose table holds the quantity:

| Line | Claim | Table and row |
|---|---|---|
| 124 | initial slice | I "Two overdensities: ..." |
| 124 | finest-level clouds, 4+c, refinement following both overdensities | I (columns n_f, Deposition); II "Two overdensities" |
| 137 | A, B grow while separation shrinks | VII "M_AH/M of A, B at t = 20M; 40M; ..."; "Coordinate separation ..." |
| 137 | less than one turn; first found earlier | VII "... turns ... 0.42"; "First common apparent horizon ..." |
| 137 | preset separation | II footnote d ("closer than 0.24M") |
| 139 | zero escaping | VII "Macroparticles removed ... left the domain 0" |
| 139 | final M_AH and Ref. | VII "Common horizon M_AH/M, chi at t = 70, ..., 100M" |
| 139 | spin below the published final value | VII same row |
| 139 | S_z + L_z | VII "S of the common horizon ...; S_z plus L_z ..." |
| 141 | formation of A, B | VIII row 1 |
| 141 | envelope stays outside | VIII last row (0.980) |

Pointers whose table holds only part, or none, of the quantity:

| Line | Claim | What is missing |
|---|---|---|
| 128 | lapse excision begins before detection | VII has the count removed before the first apparent horizon, not the start time (9.11 M) |
| 128 | "earlier at M/128" | no row (VII is M/64 only) |
| 128 | published formation masses | VII Ref. column reads "--" (FA10) |
| 128 | each black hole accretes the rest of its overdensity early | no row (only Fig. 16 bottom right; empty by 27.5 M, brief D8) |
| 137 | M/128 stays near the plane | no row |
| 139 | "contracting envelope" | no row |
| 139 | ||H|| peak during envelope infall | no row (5.36 at 77 M) |
| 139 | outward step of M_MS | no row |

Claims that have no pointer at all:

| Line | Claim | What to do |
|---|---|---|
| 128 | individual spins | add a row (FA3) |
| 137 | envelope L_z | add a row (FA2) |
| 139 | "The envelope contracts as a whole from the start" | add a row: half-mass radius 8.48, 8.08, 6.56, 4.12 M at 0, 20, 40, 60 M; M/128 4.22 M at 60 M (brief D9) |
| 141 | "hardly grow" | point to VIII row 2 |
| 141 | wide orbit, no common horizon | point to VIII rows 3-4 |

- Figure pointer at 128: "(Fig. 16, top row)" for "collapse from the inside out". The snapshots
  at 0, 12, 50 and 100 M cannot show inside-out collapse. Drop the phrase or cite its source
  (brief D1).
- Table VII caption: "(finest cells M/64; ...)" reads as if it applied to the whole table,
  migration rows included (static M/4). Move it into the block heading.
- Table VII row "at the outermost 2m/R = 1": the text writes M_MS, the table m.

### FB5. Run time in the introduction (introduction.tex:7, outside the revised paragraphs)
- Sentence: "... where a run takes minutes to a few hours on one graphics card, ..."
- The new runs take longer:
  - M/64: thirteen 25-minute segments, about five and a half hours;
  - M/128: about six hours to 61.6 M;
  - stated-radius run: fourteen or more segments so far.
- The conclusions' "minutes to hours" fits. Write "minutes to several hours" in the introduction
  as well.
- Source: runs/jeans/n1e4_v19/chain, n1e4_v11 and n1e4_v18/chain, n1e4_v20/chain (segment counts
  and ATHENA_WALL).

### FB6. Appendix evidence on the published radius is missing from the subsection
- appendix_sampling.tex:77 says the cluster in the published figure fits the smaller radius.
- self_gravity.tex:141 says which data Ref. evolved "cannot be decided" and places the published
  outcome between the two runs. A reader cannot weigh one against the other.
- Add before line 141's last sentence: "The cluster in the published figure fits the
  speed-matched radius, while the published remnant mass lies between the two outcomes."

### FB7. "Documented differences in timing" (title.tex:9)
- The documented differences go beyond timing:
  - post-horizon central lapses and smaller late migration swings (self_gravity.tex:100, 102);
  - the prolate horizon-mass deficit (self_gravity.tex:56).
- Rewrite: "... are reproduced in kind, with documented differences."

### FB8. A rule announced in the introduction is missing from the conclusions
- introduction.tex:11 lists "two more settings" for small black holes; method.tex:195 and 197
  and self_gravity.tex:126 support them. The conclusions do not state them.
- Add: "Black holes resolved by a few cells need particle removal inside the found apparent
  horizon. The lapse at the nearest cell centers stays above the excision threshold and leaves
  matter inside."

### FB9. The key open point of the merger subsection is missing from the outlook
- self_gravity.tex:150 lists the envelope contraction as not determined. Brief D9 says it sets
  the remnant mass. Conclusions p. 4 does not ask about it.
- Add: "What makes the envelope around the forming pair contract from the start, which sets how
  much of it the remnant swallows?"

### FB10. "All published digits" against the printed digits (Table III, generated)
- Three entries print as 9.05e-8, 2.05e-6 and 1.25e-7, against the published 9.0, 2.0 and 1.3.
- Full precision confirms the claim: 9.0463e-8, 2.0457e-6, 1.2543e-7 (kerr_summary.json). A
  reader who rounds the printed values half-up gets 9.1 and 2.1.
- Print four digits for these three entries.

### FB11. Fig. 16 caption against the figure (self_gravity.tex:133)
- "black hole A and black hole B (red, blue)": in the top row, red and blue are the macroparticles
  of overdensities A and B, labeled at t = 0.
- "Small circles" (recorded positions) and "Open circles ... mark Ref." use the same marker.
- Rewrite: "Top: orbital-plane macroparticles of the envelope (gray) and of overdensities A and B
  (red, blue), with apparent horizons (black circles)." Draw the recorded positions as filled dots.

### FB12. Introduction results list against the sections
- Each item of introduction.tex:13 has its section.
- Two items need the fixes above: the prolate sentence (FA1) and the post-merger sentence (FA6).
- "Spiral inward" fits the subsection, although the pair completes less than half an orbit
  (Table VII, 0.42 turns); see FD7.

---------------------------------------------------------------------------------------------

## C. Rules (SKILL.md, WRITING_GUIDE.md, NOTATION.md)

### FC1. Symbol collisions (3.6)
- chi = S/M_AH^2 (Table VII caption and rows; Table VIII) against the Z4c variable chi:
  NOTATION; Table II footnote a ("floor 1e-5 on chi"); Table IV caption ("chi >= 1/16").
- S and S_z for horizon spin (self_gravity.tex:137, 139) against the momentum density S_i
  (NOTATION). "S_z" reads as a component of S_i.
- d for the separation (Fig. 16) against d_orb, the orbital radius, which is half the separation
  (appendix_sampling.tex:73-77).
- Suggestion: chi_AH, J (as in Ref.) and d_AB. Add all three to NOTATION.md.

### FC2. Negations other than "not determined" (5.1)
Each line below gives the location, the current wording, and a positive rewrite:
- self_gravity.tex:126, "overshoots such small surfaces and finds no apparent horizon": drop
  "and finds no apparent horizon".
- self_gravity.tex:141, "with no common apparent horizon found ...": use the FA14 rewrite.
- self_gravity.tex:137, "Two cell spacings give a direction of change without an order of
  convergence.": "Two cell spacings give the direction of change only."
- introduction.tex:13, "without merging within the run": "on a wide orbit to the end of the run".

### FC3. Mesh spacings in prose (4.1)
- M/64 and M/128 appear in self_gravity.tex:124, 128, 137, 139, 141, 150 and in both captions.
  The guide's "Allowed numbers" sends mesh spacings to tables. Earlier sections set the same
  precedent with M/16 and M/32 (self_gravity.tex:58).
- These spacings label figure curves. Either add "the finest cell spacings that label figure
  curves" to the guide's allowed list, or write "the coarser and the finer mesh".

### FC4. Lab-report and implementation sentences (5.3, 5.5)
- self_gravity.tex:124 "Two evolutions are therefore reported": see FA12.
- self_gravity.tex:137 "... with earlier slices unsearched": see FD4.
- method.tex:195 "This rule waits for a successful search of the current run". "Current run" means
  the restart segment, a project record. Rewrite: "This rule acts once a search has found the
  apparent horizon and ignores a surface more than four times the starting radius of the search."
- method.tex:197 "Searches there ...": "there" has no antecedent, and m is undefined. Write
  "Searches in Sec.~\ref{sec:overdensities}".

### FC5. Terms undefined at first use for plasma-PIC and stellar-dynamics readers (1.2)
- "puncture trackers" (137): the initial data contain no punctures.
- "common apparent horizon" (137).
- "trapped surfaces" (128).
- "unexcised" (128).
- "inspiral survival" and "host-radius" (150).
- "slice-mass geodesics" (introduction.tex:13).
- FD gives rewrites for each.

### FC6. Expert dictionary: "apparent horizon" where the finder is meant (WRITING_GUIDE Sec. 6)
- Fig. 16: caption "common-horizon spin" and panel label "spin of common horizon".
- Tables VII and VIII: rows "Common horizon ...".
- Write "common apparent horizon".

### FC7. Hardware and wall time (5.5): a decision for the authors
- The phrases:
  - "one graphics card" (abstract; introduction.tex:7; conclusions.tex:3, 11);
  - "evolved in minutes to hours" (conclusions.tex:3).
- They state the paper's cost claim, but 5.5 excludes GPUs and wall times of runs.
- Add an explicit exception to WRITING_GUIDE "Standing statements", or state the cost as a ratio.

### FC8. Checker results in scope
Command run: `check_manuscript.py --main main.tex --forbid '<guide list>'`, without --compile.
- 5.1 candidates in scope: self_gravity.tex:139, 141, 150. All are "not determined" or "cannot be
  decided" statements, which are allowed.
- 5.7 candidates: title.tex:9 and introduction.tex:11. Both concern AthenaK's defect, which is
  allowed.
- 9.1 candidate: self_gravity.tex:146, estimated at ~5.7 lines. It is confirmed and worse when
  rendered (FE1).
- No 4.3, 3.4, 1.3, 5.5, 5.6 or 5.8 hits in scope.
- The only 4.1 hit (a percent sign) is tab_outcomes.tex:159 in the new Table VII block ("conserved
  to 2\%", Ref. column). It is an appendix table and acceptable.

---------------------------------------------------------------------------------------------

## D. Clarity (sentences a first-year student from a neighbouring field would not follow)

- FD1, self_gravity.tex:124. "The envelope radius and orbital speed stated in Ref. belong to
  different cluster sizes."
  - Rewrite, which also replaces the next sentence: "The orbital speed stated in
    Ref.~\cite{Wu:2026nrpic} is circular only in an envelope less than half the stated radius
    (Appendix~\ref{app:sampling})."
- FD2, self_gravity.tex:128. "An unexcised $M/128$ check shows trapped surfaces ... formation
  time in Ref."
  - Rewrite: "In an $M/128$ run that keeps every macroparticle, spheres with $2M_{\rm MS}=R$
    appear about each overdensity near the published formation time."
- FD3, self_gravity.tex:137. "The finder searches for a common apparent horizon only once the two
  puncture trackers come within a preset separation."
  - Rewrite: "The finder looks for a common apparent horizon, one surface enclosing both black
    holes, once the points tracking them come within a preset separation
    (Table~\ref{tab:setups_numerics})."
- FD4, self_gravity.tex:137. "On both meshes that first search already finds ... with earlier
  slices unsearched."
  - Rewrite: "On both meshes the first search already finds one, so the recorded time is an upper
    bound on when the common apparent horizon forms."
- FD5, self_gravity.tex:139. "At the end of the run, $M_{\rm AH}$ lies above $M$ ... carries an
  outward step at large radius."
  - Rewrite: "At the end of the run, $M_{\rm AH}$ exceeds $M$ by a few percent and equals
    $M_{\rm MS}$ at the apparent horizon (Table~\ref{tab:outcomes_migration})." / "Farther out,
    $M_{\rm MS}$ varies by a few percent and crosses a step that moved outward during the envelope
    infall."
- FD6, self_gravity.tex:150. "The two host-radius evolutions further show that the envelope
  governs inspiral survival and the post-merger remnant state."
  - Rewrite: "The two envelope radii further show that the envelope decides whether the pair
    merges within the run and how much mass the remnant gains."
- FD7, self_gravity.tex:137. "The line between black hole A and black hole B turns by less than
  one turn before ... (Table)."
  - Rewrite: "The pair completes less than half an orbit before a common apparent horizon is first
    found, earlier than in Ref.~\cite{Wu:2026nrpic} (Table~\ref{tab:outcomes_migration})."
- FD8, introduction.tex:11. "For self-gravitating tests, Ref. leaves open ... the host radius
  inconsistent with its stated orbital speed, and small black hole finder settings, listed where
  each arises."
  - Problem: a radius is not "left open", and "small black hole finder settings" is ambiguous.
  - Rewrite: "For self-gravitating tests, Ref.~\cite{Wu:2026nrpic} leaves open the filter pass
    count, the near-critical perturbation, and finder settings for small black holes, and its
    envelope radius disagrees with its orbital speed."
- FD9, introduction.tex:13. "Tracers around evolving black holes match slice-mass geodesics and
  conserve axial angular momentum (Sec.)."
  - Rewrite: "Tracers around evolving black holes follow geodesics of the mass measured on the
    slice and conserve angular momentum about the symmetry axis
    (Sec.~\ref{sec:evolving_black_hole})."
  - Related, introduction.tex:11: "They bound refinement on full-depth random samples, while ..."
    repeats the sentence two before it (2.4). Rewrite: "The published finest-level rule stays the
    choice wherever refinement remains bounded (Sec.~\ref{sec:deposition})."
- FD10, title.tex:9. "Two overdensities collapse to black holes that spiral inward and merge in
  kind inside a cluster." This is suspect (9): "merge in kind" does not parse.
  - Rewrite: "Inside a cluster, two overdensities collapse to black holes that spiral inward and
    merge, as in the published run."

Conclusions assessment:
- Rules stated as rule plus reason:
  - Filter compensation, finest-level clouds, and lattice masses: yes.
  - Tetrad gauge: rule plus reason, but in jargon. Plain version: "A pusher that rotates momenta
    in a local frame must state which frame it uses, because its step error depends on how that
    frame turns along the orbit."
  - Lattice reason (conclusions.tex:5), "... and otherwise shifts ...". Rewrite: "Unrescaled, the
    lattice-site count inside a sphere differs from its volume in cells and shifts the mass of the
    black hole formed in collapse."
  - Mass check (conclusions.tex:7): the reason is an anecdote, not the why. Rewrite: "Apparent-
    horizon masses need an independent check from the slice mass, because a finder can return a
    converged surface with a wrong mass." The finder as distributed gave 0.9771 at both stopping
    tolerances (Table III).
  - Merger rule: see FA6.
- Rules without support in a section: none. The only unsupported part is the mechanism clause of
  the merger rule (FA6). One supported rule is missing (FB8).
- Paragraph 4 reads as open questions, with four problems:
  - The first sentence is a hybrid. Start with "What initiates ...?".
  - The second sentence joins two unrelated questions. Split it.
  - The third presupposes an unstated fact (FB2).
  - The fourth presupposes a numerical deficit (FA16).
  - The envelope-contraction question is missing (FB9).
- Paragraph 5: see FA18.

---------------------------------------------------------------------------------------------

## E. Layout (pages 20-25, 27, 32, 33 rendered at 80 dpi; captions at 160 dpi)

- FE1. Fig. 17 caption runs to eight lines in one column (p. 24); the limit is six. The FA5
  rewrite (45 words) brings it to about five to six lines.
- FE2. Fig. 16 caption runs to six lines at full width (p. 23); the limit is five. Shorten the
  bottom-left clause, for example drop "interpolated between recorded positions (small circles)"
  and use filled dots (FB11).
- FE3. Both figures land two pages after their first citation:
  - Fig. 16 is first cited on p. 21 and printed at the top of p. 23, above the Sec. VI heading.
  - Fig. 17 is first cited on p. 22 and printed on p. 24, inside Sec. VI beside the hypergraph
    text.
  - The tops of p. 22 hold Figs. 14 and 15. Moving the fig:overdensities float to just after the
    subsection's first paragraph, and fig:overdensities_radius to before line 141, should pull
    both forward one page.
- FE4. Fig. 16 drawing (PNG inspected at full size):
  - The bottom-right legend sits on the gray envelope curve, which runs through "M/64" and
    "M/128".
  - The open circles at t = 100 M (Ref.'s final mass and spin) are half clipped by the right frame
    in the bottom-middle and bottom-right panels.
  - The "original" ticks touch their labels (bottom left at 64 M; bottom middle at 8.5 M).
- FE5. Tables:
  - Table I (p. 27): nothing is cut off. All ten columns, every row up to "Two overdensities,
    stated radius", and footnotes a-g are visible within the page.
  - Table VII (p. 32) fits.
  - Table VIII (p. 33) fits, but sits inside Appendix B between Eqs. (B8) and (B12), as known
    from the earlier review (E2).
- FE6. No overfull lines in scope. The only one in main.log is method.tex:125, outside scope and
  known. No widows or orphans on pp. 20-25.

---------------------------------------------------------------------------------------------

## Checked and found correct

- Suspect (7), "to all published digits" (conclusions, abstract): correct. Table III against
  orig. Kerr section (four pusher/metric pairs). The borderline printed values were checked at
  full precision in kerr_summary.json; see FB10 for the display only.
- Suspect (8), introduction tracer sentence: correct in substance. Evidence:
  - test_particles.tex:70-78: the plunge matches the M_MS geodesic; the circular tracers' M_eff
    agrees with M_MS; the head-on axial angular momentum is conserved closely;
  - Table III: L_z change 1e-4 to 4e-4; L_x 1e-3.
  Wording only (FD9).
- Suspect (3): true for A against B (Table VIII row 1); only the comparison with the other run is
  wrong (FA9).
- References: every \ref and \cite resolves. main.log of the 10:16 build has no undefined
  references or citations; the sec:*, tab:*, fig:* and app:* labels used in scope exist.
- Stated-radius prose against the present state (86 M): every statement holds, and none becomes
  false by 100 M if the present trend continues (separation 9.24 M at 86 M, falling about 0.01 M
  per M). The statements checked:
  - black holes form at 9.1 to 9.2 M near 0.09 M;
  - "hardly grow": 0.137 M at 20 M, 0.148 M at 85.7 M;
  - "order of magnitude less dense": twelve times (D14);
  - the stated speed is above circular: 0.1332 against 0.103 (TL 09:33);
  - outward to a wide orbit: 6 M to 9.3 M; the caption's "widen" is a net statement;
  - no common horizon;
  - "nearly the whole envelope" outside: 0.980.
- The text gives no number for the stated-radius turn (a quarter of a turn), so nothing there can
  go stale.
- Other prose facts in the merger subsection:
  - "merge earlier": the first search is an upper bound, and 57.0 < 64.16;
  - "several million" (orig. 1338);
  - "less than half as large" (13.3 against 30 M);
  - "somewhat later" (10.5 and 9.5 M against 8.5 M);
  - first search on both meshes (brief D6; TL 02:35);
  - trends with M/128: time toward Ref., mass further below, chi crossing above;
  - the envelope contracts on both meshes;
  - the remnant accretes all but 15 macroparticles, none escape;
  - the excess of a few percent (2.5);
  - S_z + L_z within 0.087-0.099;
  - Ref.'s outcome lies between the two runs (TL 09:24).
- method.tex:195 pointer: consistent with Table I footnote f and brief D3b.
- appendix_sampling.tex:77, last sentence: consistent with the subsection, except "host" (FB1).
- Introduction outline (line 15) matches the section structure, and each results-list item has
  its section.
- Rules:
  - no sentence in scope above 35 words (longest 31, counted by script);
  - no gerund openings;
  - at most one dash pair per paragraph;
  - no \eqref;
  - no bare "hole";
  - no hype;
  - no file, run, machine or code-version names in scope;
  - abstract free of mathematical symbols.
- Table I: nothing cut off on p. 27.

## Could not check

- The 100 M state of the stated-radius run, which is still running. All of its statements were
  checked against the 78-86 M state only.
- Why ||H|| = 5.82 at t = 0: the sources leave open whether particle sampling on the superposed
  metric or the momentum constraint of time-symmetric data with moving overdensities causes it.
- Envelope L_z, half-mass radii and the slice-mass profile: taken from brief D9, D10, D13 and
  TL 02:35, not recomputed from snapshots.
- The M/128 curves of Fig. 16: spot-checked only (masses at 9.5-11 M from overdensities.npz).
- Ref.'s figures (jeans_ah_mass_spin, particle snapshots): not rendered; I used the numbers in
  its text.
- Run wall times (FB5): estimated from segment counts and configured wall limits in the chain
  directories, not from scheduler accounting.
- Compilation: I did not compile. I used main.pdf and main.log of 10:16, which postdate every
  source file.
