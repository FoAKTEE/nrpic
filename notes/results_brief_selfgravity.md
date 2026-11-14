# Results brief for the section "Self-gravitating matter" (facts for the writer)

Status 2026-11-13 13:50; part D completed 2026-11-14. Source of every number: `docs/TESTLOG.md` (entry titles given
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
## D. Collapse and merger inside a cluster (subsection "Two overdensities in a cluster") -- final for the M/64 run (complete to 100 M); the M/128 comparison stopped at 61.57 M

Setup: a monoenergetic envelope (0.76 of the total mass) with two Gaussian
overdensities (0.12 each, width 0.7 M) at +-3 M on a circular orbit; 6000 envelope
particles and 2000 in each overdensity (the original: 3e6 and 1e6 each). Envelope
radius: the self-consistent value, areal radius 13.3 M (Appendix on sampling; the
stated radius of 30 M does not fit the stated speed). Meshes: finest cells M/64 or M/128
in a region that follows each overdensity (the original: M/64 at the start, refinement
down to M/256). Four filter passes with compensation. Figure and tables use the M/64 run
`jeans/n1e4_v19`: one run from t = 0 to 100 M on a domain of +-80 M (root cells 2 M,
eight levels), finest region of radius 0.2 M around each tracker throughout, removal
below a lapse of 0.05 and inside 0.8 of the smallest radius of a found horizon, finder
flow constants 0.05 (A, B) and 0.2 (common horizon). The M/128 comparison
(`n1e4_v11` to 6.31 M, then `n1e4_v18`) has a domain of +-256 M and a finest region of
0.15 M, then 0.125 M. The figure caption notes need not mention the regions, the setups
table does.

Facts so far (formation stage), in the order of the argument:
1. Collapse time. The overdensities collapse from the inside out. With cells of M/128,
   in a run in which no particle is removed, the first trapped surface (Misner-Sharp
   mass about the tracker) exists at t = 8.66 M with a mass of 0.05 M. The original's
   first apparent horizons are at 8.475 and 8.525 M. (In the production runs the
   lapse rule starts to remove particles at 8.1 to 9.2 M, before the finder can see
   the horizons.)
2. Black-hole masses after formation. Apparent horizons (finder): first found at
   t = 10.50 M (A) and 10.56 M (B) with 0.0976 and 0.0992 M with cells of M/64 (`n1e4_v19`,
   the figure's run; the earlier M/64 run on +-256 M: 10.38 and 10.31 M, 0.0946 and
   0.0932 M); at 9.61 and 9.52 M with 0.0801 and 0.0782 M with cells of M/128, where
   they are 0.0855 and 0.0856 M at t = 10 M. Misner-Sharp at t = 10.0 M (M/64, `n1e4_v7`):
   0.085 M. The original gives 0.0880 and 0.0877 M at t = 10 M. Later (M/64, `n1e4_v19`):
   0.1448 and 0.1442 M at 20 M.
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
[Cluster with two overdensities: collapse on time ...; Correction: the black holes of
the two overdensities do form ...; Finder test ...; Second finder test ...; Where the
failure starts: at a puncture; Intervention: removing matter inside the horizon cures
the failure; M/128 chain failed at the same step ...]

Inspiral, merger and remnant (M/64 run `jeans/n1e4_v19`, complete to 100 M). Sources:
`runs/jeans/n1e4_v19/jeans.horizon_summary_{0,1,2}.txt` (A, B, common horizon; columns
time, mass, S), `jeans.nrpic.hst` (np, sum_m, n_excised, m_excised, n_escaped,
m_escaped), `jeans.z4c.user.hst` (H-norm2; norms below are its square root), tracker
positions from the restart-dump headers and `jeans.co_{0,1}.txt` with `co_archive/`;
all printed by `paper/scripts/make_data_overdensities.py` (summary) and tabulated by
`paper/scripts/make_tables.py` (Table tab:outcomes_migration, last block). Figure:
fig_overdensities (made, complete to 100 M). [Two overdensities: run complete at 100 M]

Established:
4. Inspiral. Coordinate separation of the trackers: 6.05 M at the first individual
   horizon (10.5 M), 5.36 M at 30 M, 4.11 M at 40 M, 1.99 M at 50 M, 0.65 M at 55 M,
   0.24 M at 57.0 M. The line from A to B turns by 0.42 of a turn (153 degrees) between
   10.5 and 57.0 M (172 degrees from t = 0): the black holes merge before completing one
   orbit. The trackers coincide from 59.69 M (the code then follows one point; the
   figure's separation ends there).
5. Individual black holes before the merger: A 0.1890 M (last search before the common
   horizon, 56.88 M), B 0.1862 M (56.94 M); 0.1887 and 0.1862 M at 57.0 M; their spins
   S/M^2 0.06 and 0.05. Both are still found inside the common horizon until 58.56 M (A)
   and 58.44 M (B); after that their searches converge on the common horizon (rows of A,
   B with the common mass, from 58.63 M on, are left out of figure and table). The
   original: 0.1742 and 0.1761 M at 60 M.
6. Common horizon: first found at t = 57.00 M with M_AH = 0.3746 M, S = 0.0600,
   chi = S/M_AH^2 = 0.427. This is the first search of it: the finder looks for the
   common horizon only while the trackers are closer than fastflow/merger_distance (1.0)
   times the sum of the tracker masses z4c/co_<n>_mass (2 x 0.12), i.e. 0.24 M
   (athenak/src/z4c/fastflow.cpp, PuncAreClose), and the first row of
   horizon_summary_2.txt already has a horizon. So 57.0 M is an upper bound on when a
   common horizon exists on this mesh, not its formation time. At 57.0 M the two
   individual masses add up to 0.3749 M. The spin 0.41 of the 23:30 entry and of a commit
   message is chi at 57.9 M (0.3837 M, S = 0.0600); at the first common horizon chi =
   0.427 (0.43). The original: 64.16 M, 0.3833 M, chi = 0.504.
7. Remnant (common horizon; found in all 688 searches from 57.0 to 99.94 M): M_AH, chi =
   0.4015, 0.368 at 60 M; 0.5194, 0.178 at 70 M; 0.8257, 0.043 at 80 M; 1.0183, 0.079
   at 90 M; 1.0255, 0.085 at 99.94 M. Over the last 10 M: +0.0072 in mass (0.7
   percent), +0.0053 in chi; the mass still rises by 3.5e-4 to 5.6e-4 per M at the end.
   Settled to within about 1 percent in mass, not in chi (6 percent per 10 M). The
   original at 100 M: 0.6474 M, chi = 0.1713.
8. Matter. Particle number and rest mass (of 1.0502 at t = 0): 7552 and 0.887 at 10.5 M;
   5927 and 0.775 at 20 M; 5372 and 0.703 at 57.0 M; 4270 and 0.559 at 70 M; 1875 and
   0.245 at 80 M; 98 and 0.013 at 90 M; 15 and 0.0020 at 100 M. Every removed particle was
   removed by the two removal rules (lapse below 0.05, or inside 0.8 of the smallest
   radius of a found horizon; the history does not separate them); none left through the
   outer boundary (n_escaped = m_escaped = 0 throughout). Removed (rest mass in units of
   M): 2448 particles (0.163) before the first found horizon, from 9.11 M on (lapse rule
   only); 2180 (0.184) from 10.5 to 57.0 M; 5357 (0.701) after 57.0 M, of which 4172
   (0.546) between 70 and 90 M (largest rate 0.042 M per M near 78 M). The last particles of the two
   overdensities are gone by 27.5 M. At 100 M the 15 left are envelope particles 1.3 to
   8.1 M from the remnant, all moving inward.
9. The envelope contracts as a whole from the start, alike on both meshes: radius about
   the origin enclosing half the envelope's rest mass 8.48 M at t = 0, 8.08 M at 20 M,
   6.56 M at 40 M, 4.12 M at 60 M (M/128: 4.22 M); 90 percent radius 11.36 M to 7.35 M
   at 60 M (particle snapshots). After the merger it falls into the remnant (half-mass
   radius 2.80 M at 70 M, 1.81 M at 80 M). That the remnant swallows the whole envelope
   by 90 M is what makes its mass 1.03 M here against 0.65 M in the original, whose
   envelope is mostly still outside at 100 M.
10. Angular momentum. S of the common horizon: 0.0600 at 57 M, 0.0480 at 70 M, 0.0296 at
   80 M, 0.0823 at 90 M, 0.0890 at 100 M; not conserved (the original: J = chi M_AH^2
   conserved to 2 percent). S_z of the horizon plus L_z of the particles left (about the
   midpoint of the trackers, from their stored momenta u_i; snapshots every 0.5 M) stays
   between 0.087 and 0.099 from 57 to 100 M and is 0.0907 at both ends (S_z 0.0600 +
   L_z 0.0307 at 57 M, 0.0872 + 0.0035 at 100 M): the changes of S are matched by the
   matter around the hole. The envelope's L_z about the origin rises from -0.003 at t = 0
   to +0.032 at 57 M during the inspiral (M/128: +0.038 at 57 M). The lower final chi is
   arithmetic: chi_here/chi_orig = 0.49 = (0.6474/1.0255)^2 x (0.0890/0.0718).
11. Out of the orbital plane (M/64 only): midpoint of the trackers at z = +0.24 M at
   20 M, +0.43 M at 30 M, +0.55 M at 40 M, +0.59 M at 50 M and at 57 M; merged tracker
   at +0.59 M at 100 M (the drift stops after about 45 M). M/128: within 0.06 M of the
   plane throughout.
12. Constraint norm ||H||: 5.82 at t = 0 (superposed initial data), largest 12.6 at 8.0 M
   (collapse), 2.88 at 57.0 M, a second maximum of 5.36 at 77 M (envelope falling in),
   0.54 at 100 M.
13. Remnant mass above the total mass. M_AH = 1.0255 at 100 M (area mass
   sqrt(A/16 pi) = 1.0246) is 2.5 percent above the mass M = 1 of the initial data. The
   initial macroparticles give sum m W / psi = 1.00000 with the generator's psi, so the
   data carry M = 1 in the integral. Slice Misner-Sharp mass (analysis/diag/slicemass.py)
   at large radius (36 to 72 M): 0.9999 at t = 0, 1.0008 at 15 M, 0.9964 at 30 M, 1.0002
   at 50 M, 1.0043 at 59.7 M, 1.0202 at 70 M (not flat), 1.0277 at 78.5 M, 1.0289 at
   90 M, 1.0283 at 100 M; at the horizon at 100 M 1.024 +- 0.006 (agrees with the
   finder). At 100 M the profile m(r) outside the hole is not flat: 1.02 at r = 1 to 5 M,
   0.97 to 1.01 at 12 to 28 M, 1.03 at 39 to 66 M; a step of about +0.03 moves outward
   through r = 39 to 66 M between about 55 and 85 M, so it is not a reflection coming in
   from the outer boundary. The deposited energy equals the particles' energy at every
   step (int_E = sum_mW to round-off).

14. The stated envelope radius (`jeans/n1e4_v20`: areal radius 30 M as stated in the
   original, same clumps and speeds, 10^4 particles, otherwise the configuration of
   `n1e4_v19`; test of candidate (b) of the envelope's contraction below). STATE AT 78 M,
   run still in progress to 100 M; numbers marked (78) will be replaced by the 100 M
   values. First apparent horizons at 9.19 M (A, 0.0907 M) and 9.06 M (B, 0.0877 M);
   0.1366 and 0.1367 M at 20 M; 0.1406 and 0.1411 M at 40 M; 0.1440 and 0.1443 M at 60 M;
   0.145 M each at 78 M (78). The black holes hardly grow after 20 M (0.0002 M per M
   against 0.001 M per M in the self-consistent envelope): the envelope is twelve times
   less dense. Rest mass of the particles: 1.029 at t = 0, 0.770 at 20 M (the two
   overdensities are gone), 0.762 at 60 M, 0.758 at 78 M (78): the envelope stays
   outside, 97 percent of it at 78 M (78). No common horizon is found: the trackers never
   come within the 0.24 M at which the finder starts to look. Separation of the black
   holes: 9.2 M at 64 M, 9.3 M at 76 to 78 M, hardly changing; the line between them has
   turned by a quarter of a turn by 78 M (78); the stated speed is above the circular
   speed in this envelope, so the pair moves out from 6 M to a wide orbit. The midpoint
   of the trackers is 1.0 to 1.2 M out of the orbital plane at 64 to 78 M.
   Reading: with the self-consistent radius the whole envelope falls in and the remnant
   is 1.03 M; with the stated radius nothing merges by 78 M (78) and the black holes stay
   at 0.145 M; the original (merger at 64 M, remnant 0.65 M at 100 M, individual masses
   0.174 and 0.176 M at 60 M) lies between the two. Which initial data the original
   evolved cannot be decided from its text.

Comparison of the merger with the original (common horizon first found; both of ours at
the first search, see 6; the M/128 chain stopped at 61.57 M when it reached its limit of
ten job segments, not on an error):

| | t/M | M_AH/M | chi |
|---|---|---|---|
| M/64 (`n1e4_v19`) | 57.00 | 0.3746 | 0.427 |
| M/128 (`n1e4_v18`) | 59.70 | 0.3523 | 0.565 |
| original (M/64 refined to M/256) | 64.16 | 0.3833 | 0.504 |

Observation from two resolutions (no order of convergence): with finer cells the time
moves towards the original's; the mass at first detection does not (the M/128 black
holes are about 0.01 M lighter each throughout the inspiral: 0.1644 and 0.1628 M against
0.1754 and 0.1751 M at 50 M); chi goes from below to above the original's value.
M/128 run (`n1e4_v11` + `n1e4_v18`) at the same times as the M/64 run (separation;
masses of A, B): 5.99 M, 0.0855, 0.0856 M at 10 M; 5.75 M, 0.1368, 0.1375 M at 20 M;
5.15 M, 0.1439, 0.1448 M at 30 M; 4.03 M, 0.1517, 0.1532 M at 40 M; 2.24 M, 0.1644,
0.1628 M at 50 M; 0.72 M, 0.1738, 0.1715 M at 57.0 M; 0.24 M, 0.1779, 0.1753 M at the
first common horizon (59.70 M). It approaches faster than M/64 to 40 M and more slowly
afterwards. The line from A to B turns by 0.61 of a turn between its first horizon and
the common horizon.

Not established (each with its candidate causes; none tested):
- Why the merger comes earlier than in the original (57.0 and 59.7 M against 64.16 M).
  (a) Cell size: the trend of two resolutions points this way; test: a third resolution.
  (b) Our times are first searches, set by the trackers coming within 0.24 M; test:
  repeat the stretch from the dump at 50.89 M with a larger merger_distance, so that
  the search runs before and gives the formation time. (c) Domain and coarse-level
  layout (0.15 M of separation by 28 M, 23:10 entry); test: the run on +-256 M carried
  to the merger. (d) The drift out of the plane on the M/64 mesh (but M/128 does not
  drift and still merges earlier than the original). (e) 2000 particles per overdensity
  and 6000 in the envelope against 10^6 and 3 x 10^6; test: a second sample.
- Why the envelope contracts from t = 0 on both meshes (item 9), which sets the remnant
  mass and spin at 100 M. (a) The envelope is an equilibrium of its own; the clumps add
  mass inside it (Newtonian estimate from the initial macroparticles: the clumps add
  78 percent to the envelope's virial term); test: the envelope alone on the same mesh to
  60 M. (b) Our envelope's areal radius (13.3 M) against the stated 30 M; a larger
  envelope contracts and is accreted more slowly; test: the stated radius (clumps then
  off their circular orbit). (c) Particle number; test: a second sample.
- Whether the 2.5 percent of remnant mass above M is mass of the spacetime or an error
  (item 13), and what the outgoing step of the slice mass is. Candidates: the
  constraint violation of the superposed initial data (||H|| = 5.8 at t = 0; test:
  initial data that solve the Hamiltonian constraint); the removal of most of the
  matter in bursts inside the horizon (0.55 of the rest mass in 70 to 90 M; test: the
  slice-mass profile against the removal history on more dumps); the measures (finder
  and Misner-Sharp agree at the horizon, but the slice measure outside is not flat to
  +-3 percent).
- How the envelope acquires L_z = +0.03 during the inspiral (item 10); test: the
  envelope's L_z against the orbital angular momentum of the black holes over time.
- The drift out of the plane on the M/64 mesh (item 11; open since the 23:10 entry).
What the text may say: the black holes merge inside the cluster before completing an
orbit; the common horizon is found at 57 M (M/64) and 59.7 M (M/128) against 64.16 M,
each at its first search; its mass at detection is within 2.3 percent (M/64) and 8
percent (M/128) of the original's; after the merger the whole envelope falls in, so the
remnant at 100 M is 1.03 M with chi = 0.085 against 0.647 M and 0.171. It must not give
57.0 M as the formation time of the common horizon, nor a cause for the earlier merger,
the contraction of the envelope or the mass excess.

## Statements the section must not make
- No horizon mass from before the finder was corrected.
- No claim that the level cap helps near black holes.
- No claim that the central density stays on the cycloid with the level cap.
- No cause for: the remaining sensitivity of the horizon mass to coarser clouds on a
  random sample; the initial
  offset of the cluster oscillation; the later collapse of the compact models compared
  with the original.
- Two overdensities: no formation time of the common horizon (57.0 M and 59.7 M are
  first searches); no cause for the earlier merger, the contraction of the envelope, the
  remnant mass above M, or the drift out of the plane.
