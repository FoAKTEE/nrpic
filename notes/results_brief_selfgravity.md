# Results brief for the section "Self-gravitating matter" (facts for the writer)

Status 2026-11-13 13:50. Source of every number: `docs/TESTLOG.md` (entry titles given
in brackets). Numbers are for the figures and the appendix table; the prose uses only
the numbers the writing guide allows. Parts marked NOT YET are not to be written.

All runs: at most 10^4 macroparticles, one graphics card, minutes to a few hours each.

## A. Dust collapse (subsection "Dust collapse") -- final

Setup: homogeneous dust ball at rest, areal radius R_0 = 5 M, total mass M, on a
lattice (9328 particles); adaptive mesh; published deposition rule; one plain filter
pass; lapse excision; corrected horizon finder. Figure: fig_dust (four panels: lapse
against the bound; central density against the cycloid; horizon mass; constraint norm).

Facts, in the order of the argument:
1. The central lapse equals the analytic lapse bound until the coordinate wave from the
   surface arrives, and the central density follows the cycloid. [Dust collapse, R_0 =
   5 M ...]
2. A horizon forms; all particles are removed at the lapse threshold shortly after.
3. Lattice masses. The published rule gives each lattice site the local density times
   the cell volume. The number of lattice sites inside a sphere differs from the
   sphere's volume in cells; at this particle number the particles are 1.2 percent
   heavier than the initial metric assumes. The horizon then comes out 1.1 percent
   heavier than the total mass, and the Misner-Sharp mass of the slice shows a shell of
   excess mass moving outward from the surface at the speed of light. Rescaling the
   masses of the outermost lattice layer (interior unchanged) makes the horizon mass
   equal to the total mass to 3 parts in 10^4 at formation and to 0.13 percent at the
   end of the run. [Dust collapse: the published lattice rule ...; ... corrected
   initial data, cloud at the finest level]
4. Horizon finder. A black hole of known mass (vacuum puncture) was used to check the
   mass measure. The finder of the host code read 2.3 percent low at cells of M/8 and
   5.9 percent low at M/16, while the Misner-Sharp mass of the same slices was right
   to 0.15 percent and 0.001 percent. Cause and change as in the method section. After
   the change finder and slice agree to 3 parts in 10^4. Figure: fig_horizon_check.
   [Horizon mass calibration: results; Further checks of the corrected finder;
   Corrected finder on GPU]
5. Coarser clouds (level cap following the local particle density; Sec. deposition).
   Corrected and extended since the first draft; this replaces the earlier item.
   (a) Lattice sample. The cap removes the jump of the constraint violation at the
   first refinement. The central density reading, which with the published rule drops
   to a third of the cycloid value while the refined central cells are nearly empty,
   instead reads up to 14 percent above the cycloid (49 percent with at most one level
   of coarsening). The particles themselves are the same in all three runs (radii of
   the innermost particles equal to one part in a thousand): the excess is the regular
   lattice beating against a cloud lattice of nearly equal spacing at the centre of
   symmetry. This was confirmed by depositing the stored particles of the uncapped run
   with clouds on the lattice level, which reproduces the readings. Near the forming
   black hole the constraint norm is 2.5 times larger and the horizon mass ends 0.65
   percent above M (unlimited cap) or 1.1 percent below (one level), against 0.13
   percent below with the published rule.
   (b) Random sample of the same ball (same particle number). With the published rule
   and the full refinement depth the curvature-based refinement follows the sampling
   noise and the block count grows past what one card holds before the horizon forms,
   with one plain pass and with four passes plus compensation. With capped clouds the
   same runs pass through horizon formation and on to 41 and 43 M (where the jobs
   reached their time limit), and the horizon mass stays within 0.15 percent of M.
   (c) Random sample, both rules at equal settings (one refinement level fewer, four
   passes plus compensation): horizon mass at the end 0.27 percent below M (published)
   and 0.54 percent below (capped); constraint norm after formation three times higher
   with capped clouds.
   What to conclude in the text: coarser clouds raise the constraint violation around
   a forming black hole and shift its mass by a few tenths of a percent also without a
   lattice; on a lattice the shift is larger and comes with the beat; on a random
   sample capped clouds are what keeps the refinement bounded at the deepest level.
   The published rule is the more accurate one where it can be afforded, and is used
   for every collapse result in the paper. The first prediction (that the disturbance
   was the lattice beat alone) was refuted by run (c).
   Table: the outcomes table needs these rows (being added).
   [Correction: central density with the level cap ...; Is the disturbance ... a
   lattice effect?; Monte Carlo dust ball: published rule runs away ...; Monte Carlo
   dust ball: published rule against capped clouds at equal settings]

## B. Relativistic clusters (subsection "Relativistic clusters") -- final except where marked

Setup: monoenergetic equilibrium sequence labelled by y_c (the original's five models);
10^4 equal-mass particles, stratified sampling, net momentum removed; four filter
passes with compensation; cells of M/2 (two least compact models, static mesh) or M/4
with adaptive refinement (three compact models).

1. Filter (figure fig_filter). With plain filter passes the stable model y_c = 0.819
   expands by 15 percent in radius (central density down by a third) and returns after
   about 230 M; three samples give the same excursion to a tenth of its size, so it is
   not sampling noise. The excursion of the central lapse is 0.004, 0.018, 0.027 for
   zero, two, four passes. With the compensation pass it is 0.006 for two and for four
   passes, and the proper-volume integral of the energy density changes by 1e-4 instead
   of 3e-3. Without any filter the run does not expand but the constraint norm is ten
   times larger and the lapse wanders. [Stable cluster controls: results; Compensated
   filter on the stable cluster: result; addenda]
2. The stable models hold (figures fig_clusters NOT YET MADE, fig_oscillation). y_c =
   0.900 and 0.819 with the original's one-percent inward kick keep all particles for
   300 M; mass-shell radii within a few percent. [Least compact cluster model ...;
   Stable model with the one-percent inward kick, compensated]
3. Core oscillation (figure fig_oscillation). The central lapse of y_c = 0.819
   oscillates with a period of about 72 M, close to the radial period of a particle in
   the core. Its swing grows until about t = 500 M and then stays at two to three
   percent of the lapse to 1200 M. It is the same for three samples, for a Monte Carlo
   sample, for 10^3 particles, for half the time step, for three values of the
   constraint damping, with relaxation of the Hamiltonian constraint, and with half the
   cell size over the cluster (first maximum equal to three percent, growth rate equal
   or slightly larger; the prediction that a discretization error would shrink both by
   four was refuted). The original's
   figure for its perturbed near-critical model shows the same growth, saturation and
   decay of an oscillation at the core period. What sets the small offset from which it
   starts is not determined. [Growing oscillation ... (all entries); Stable cluster to
   1200 M; Stable cluster with Monte Carlo sampling; Reconfiguration test, first
   attempt (second half)]
4. Particle number. With 10^3 particles the stable model behaves as with 10^4 for
   200 M and then drifts; with 10^2 it does not hold (central lapse from 0.81 to 0.58
   in 500 M, kinetic energy doubling). [Growing oscillation against particle number;
   addendum N = 10^2; Monte Carlo sampling]
5. The sequence (figure fig_clusters, being made: for each of the five models the radii
   enclosing 10 to 90 percent of the rest mass and the central lapse against time, as
   in the original). With the original's one-percent inward kick:
   y_c = 0.900 and 0.819 hold. y_c = 0.605 collapses: horizon first found at t = 191 M;
   y_c = 0.500 collapses: horizon at t = 104 M. In both the horizon mass grows as the
   cluster falls in and ends at the total mass (to 0.3 percent and 1e-4), and all but
   a few particles are removed. The original finds its horizons at 109 M and 73 M and
   calls these times dependent on particle number and noise; here both are later, and
   in y_c = 0.605 a core oscillation of growing size precedes the collapse. y_c = 0.283
   (negative binding energy) disperses: lapse to 0.98, half-mass radius from 1.7 M to
   48 M, as in the original. [Compact model y_c = 0.500 ...; Compact model y_c = 0.605
   (two entries); Unbound model y_c = 0.283]
6. Migration (figure fig_migration; Table tab:outcomes_clusters). The unperturbed
   model past the binding-energy maximum (y_c = 0.5 without kick) expands, recontracts
   deeply and then oscillates with decreasing swing about a more extended state, to the
   end of the run at 2500 M, as in the original's migration test. Lapse extrema here
   (value at t/M): 0.552 at 0; 0.913 at 228; 0.541 at 437 (after a first dip of 0.591
   at 400); 0.894 at 631; 0.753 at 783; then between 0.79 and 0.85; 0.816 at the end.
   Original (read from its figure): 0.56; 0.905 (plateau 200 to 320); 0.55 near 490;
   0.90 at 670; 0.765 at 830 to 880; then 0.78 to 0.865; about 0.83 to 0.84 near 2000.
   Agreement: the sequence of states and the values of the first two maxima and minima
   (to 0.01 to 0.02). Differences: every extremum after the first maximum comes earlier
   here (by 50 M at the first minimum, by 130 M at the fifth maximum; full cycles of 250
   to 290 M against 290 to 310 M) and the later swings are smaller; cause not
   determined. Half-mass radius 2.3 M at the start, 12 M at the first expansion, 5 to
   7 M after 900 M; the radius enclosing 90 percent grows from 3.5 M to 19 to 26 M.
   Four of 10^4 particles leave the domain; none is removed by excision. With plain
   filter passes the expansion starts 20 to 30 M earlier than with compensation; three
   samples agree. [Migration of the unperturbed y_c = 0.5 model, complete to 2500 M;
   Unperturbed y_c = 0.5: plain against compensated filter]
7. Near-critical model y_c = 0.756 with a ten-percent density perturbation (the
   original's "reconfiguration" test). The original states the size of the perturbation
   and neither its sign nor how the initial metric is obtained. Here: homologous
   compression (density up by ten percent), with the conformal factor solving the
   Hamiltonian constraint for the compressed matter (the data set is 0.3 percent
   lighter than the unperturbed cluster). Result: the cluster contracts and collapses;
   horizon first found at t = 147 M; all particles removed; the horizon mass at the end
   equals the mass of the initial data to 1e-4. The same particles on the unperturbed
   metric (inconsistent data) give the same contraction, so the outcome does not hinge
   on the initial metric. The original's run oscillates and keeps all particles. The
   run with the density reduced by ten percent (homologous expansion, same
   construction, 600 M): all particles kept; the central lapse first rises to 0.82 and
   falls to 0.73 over 250 M, then oscillates between about 0.72 and 0.83 with extrema
   60 to 100 M apart; the 90 percent mass radius ranges from 6 to 9 M. This shares the
   original's qualitative outcome (large oscillation, no collapse, extended outer part)
   but not its curve (there: about 0.74 to 0.75 from the start, period near 50 M; here
   about 0.77). Neither sign reproduces the original's lapse curve; the definition of
   the perturbation is one candidate cause, not determined.
   Unperturbed model (no kick, no density change, static cells of M/4, 800 M): within
   0.01 of equilibrium to 150 M; then an oscillation at a period of 45 to 59 M whose
   half-swing grows to 0.036 at t = 415 M and is smaller afterwards (0.011 to 0.025);
   lapse between 0.696 and 0.772; the mean falls slowly (0.01 to 0.02 below equilibrium
   from 200 M, 0.03 to 0.04 below at 800 M, still falling); all particles kept; 90
   percent radius 5.6 to 7.3 M. The original's perturbed run (read from its figure and
   text): oscillation growing from the start, extrema 0.696 and 0.777 at 250 to 275 M,
   spacing 50 to 55 M, decayed by 600 M, lapse then falling slowly to 0.735 at 800 M
   and 0.70 at 2000 M. So the unperturbed model here shows the period, the largest
   swing, the decay and the slow fall of the original's perturbed model, about 150 M
   later. Inference (not a result): the original's perturbation started this
   oscillation at a larger amplitude without changing the mean structure; a homologous
   ten-percent change does something else. What the perturbation was cannot be decided
   from the text. [Unperturbed near-critical model y_c = 0.756 to 800 M]
   [Reconfiguration test, first attempt; Consistent initial data for perturbed
   clusters; Reconfiguration rerun ...; addendum 12:05]

## C. Prolate collapse (subsection "Prolate collapse") -- facts final; the Monte Carlo dust control (item 6) NOT YET

Setup: cold homogeneous prolate spheroid, eccentricity 0.9, polar semi-axis b = 10 M,
total mass M, particles at rest; 10^4 equal-mass particles drawn at random with
reflection and half-turn symmetry (Appendix on sampling); adaptive mesh with finest
cells of M/16; four filter passes with compensation; published deposition rule; lapse
excision at 0.05. The original: 2e6 particles, finest cells M/64. Figure: fig_prolate
(made; caption draft and numbers in notes/drafts/figure_captions_3.md: particle
positions in the x-z plane at four times; largest Kretschmann scalar and where it
lies, smallest lapse and particles remaining, horizon mass against time).

Facts, in the order of the argument:
1. Why the test: no symmetry reduces it; the collapse passes through a caustic (matter
   focused onto the axis) before any horizon exists; the literature on it
   (Shapiro:1991zza no horizon found; Yoo:2016kzu; East:2019bwu horizon after the
   caustic; Wu:2026nrpic horizon after the caustic).
2. The spheroid contracts to a spindle. At 10^4 particles the spindle is a chain of
   separate condensations along the axis (figure, third panel). The largest
   Kretschmann scalar lies on the axis, first near the two ends of the spindle, and
   moves inward in steps as it jumps from one condensation to the next (|z| of 5.0 M
   at t = 20 M, 3.9 M at 24.25 M, 2.8 M at 24.5 M, 0.7 M at 26.25 to 28 M, then 1.8 M
   at 28.25 M, 0.7 M at 32 M); largest value at 27.75 M. The two maxima are mirror
   images by the symmetry of the sample. The original describes two maxima near the
   ends, within the matter, and shows them at 22.25 M; its narrow spindle is at
   27.75 M. Do not quote values of the Kretschmann scalar as physical: they depend on
   the cell size (the original says the same), and jump when finer levels appear.
3. The curvature stays finite and the run continues through the caustic stage; an
   apparent horizon is first found at t = 32.0 M (searches every M/4). The original
   shows the configuration after horizon detection at 32 M. All particles are then
   removed at the lapse threshold (from 33.8 M; none left at 45 M; removed rest mass
   equal to the rest mass of the data).
4. Horizon mass (documented difference). First found 0.929 M; largest 0.967 M at
   33.75 M; then falling steadily to 0.949 M at 45 M, not levelling off. The original
   states no horizon mass for this test (its 1e-3 agreement is for the dust collapse);
   this is a limitation found here, not a difference from a published number. The Misner-Sharp mass of the last
   slice agrees with the finder at the horizon (0.92 with an angular spread of 0.03)
   and gives the total mass 0.999 M at large radius: five to eight percent of the mass
   lie outside the black hole, between 5 and 50 M, when every particle has been
   removed. That is field content; this diagnostic does not separate gravitational
   radiation from constraint violation.
5. The norm of the Hamiltonian constraint peaks at the time of the largest curvature
   and is about three times larger there than in the dust collapse on a lattice.
6. A spherical control (randomly sampled dust ball, same filter, published rule,
   finest cells M/13) ends 0.27 percent below M: a random sample of 10^4 particles
   does not by itself cost percent-level horizon mass. The prolate deficit belongs to
   the prolate collapse and its caustic stage; how it splits between particle number
   and cell size there is not determined. With finest cells of M/32 the mesh outgrew one graphics card
   (the refinement asks for more blocks than fit) so that run does not exist.
7. Random sampling and refinement: with a random sample, one plain filter pass and the
   published rule the curvature-based refinement follows the sampling noise and the
   block count grows without bound (seen in the dust ball); four passes with
   compensation keep the prolate run at 1352 blocks at most.
[Prolate collapse, complete to 45 M; Prolate collapse: where the five percent are;
Prolate collapse, attempt with compensated filter; Monte Carlo dust ball with the
published rule: refinement runs away]
## D. Collapse and merger inside a cluster (subsection "Two overdensities in a cluster") -- formation stage final; inspiral and merger NOT YET

Setup: a monoenergetic envelope (0.76 of the total mass) with two Gaussian
overdensities (0.12 each, width 0.7 M) at +-3 M on a circular orbit; 6000 envelope
particles and 2000 in each overdensity (the original: 3e6 and 1e6 each). Envelope
radius: the self-consistent value (Appendix on sampling; the stated radius does not fit
the stated speed). Meshes: finest cells M/64 or M/128 in a region that follows each
overdensity (the original: M/64 at the start, refinement down to M/256). Four filter
passes with compensation. The region of finest cells around each tracker has a radius
of 0.3 M up to t = 13 M and 0.2 M afterwards on the M/64 mesh (0.15 M, then 0.125 M on
the M/128 mesh); the figure caption notes need not mention this, the setups table does.

Facts so far (formation stage), in the order of the argument:
1. Collapse time. The overdensities collapse from the inside out. With cells of M/128,
   in a run in which no particle is removed, the first trapped surface (Misner-Sharp
   mass about the tracker) exists at t = 8.66 M with a mass of 0.05 M. The original's
   first apparent horizons are at 8.475 and 8.525 M. (In the production runs the
   lapse rule starts to remove particles at 8.1 to 9.2 M, before the finder can see
   the horizons.)
2. Black-hole masses after formation. Apparent horizons (finder; production runs as
   stitched for the figure): first found at t = 10.31 and 10.38 M with 0.0932 and
   0.0946 M with cells of M/64; at 9.52 and 9.61 M with 0.0782 and 0.0801 M with cells
   of M/128, where they are 0.0855 and 0.0856 M at t = 10 M. Misner-Sharp at t = 10.0 M (M/64): 0.085 M.
   The original gives 0.0880 and 0.0877 M at t = 10 M. Later: 0.128 M each at
   t = 12.9 M (M/64).
3. What had to change for black holes this small (a tenth of the total mass):
   (a) Horizon finder. Its flow step is a fixed constant sized for a black hole of
   unit mass; for these the first step overshoots to a negative radius and no horizon
   is reported although one exists (shown by the Misner-Sharp mass). A constant twenty
   times smaller finds them; finder and Misner-Sharp masses then agree to one percent.
   (b) Removal of particles. With the published rule alone (lapse below 0.05) the
   runs fail three to five M after the black holes form, on both meshes: on these
   meshes the lapse at cell centres next to the puncture stays at or above the
   threshold, matter inside the horizon is removed only in the few cells nearest the
   puncture, and a non-finite value appears within two cells of one puncture in the
   spacetime update. Removing in addition every particle inside 0.8 of the smallest
   coordinate radius of a found horizon cures this (tested on the M/64 mesh: the run
   passes the step at which two runs without the rule failed). Which quantity of the
   lingering matter turns non-finite was not isolated. Whether the published rule
   alone suffices at the original's cell size cannot be tested on one card.
3c. Individual spins. The finder gives dimensionless spins of 0.007 to 0.03 for the two
   black holes; the original quotes spins of order 1e-5. With 2000 particles per
   overdensity the accreted angular momentum does not average out.
4. Inspiral, merger, common horizon, remnant growth: NOT YET (runs in progress). Do
   not state an outcome.
[Cluster with two overdensities: collapse on time ...; Correction: the black holes of
the two overdensities do form ...; Finder test ...; Second finder test ...; Where the
failure starts: at a puncture; Intervention: removing matter inside the horizon cures
the failure; M/128 chain failed at the same step ...]

## Statements the section must not make
- No horizon mass from before the finder was corrected.
- No claim that the level cap helps near black holes.
- No claim that the central density stays on the cycloid with the level cap.
- No cause for: the remaining sensitivity of the horizon mass to coarser clouds on a
  random sample; the initial
  offset of the cluster oscillation; the later collapse of the compact models compared
  with the original.
