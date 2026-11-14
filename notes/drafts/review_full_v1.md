# Referee report on the NRPIC reconstruction draft (full manuscript, v1)

Scope: `paper/main.tex` and `paper/sections/*.tex` as built into `paper/main.pdf` (13 Nov 2026,
30 pages), tables in `paper/sections/tables/`, figures in `paper/figures/`. Not reviewed (as
instructed): the subsection on the cluster with two overdensities, the conclusions, the
placeholder abstract. Statements about the original were checked in
`refs/arxiv_2611.12831/src/main.tex` (cited below as "orig. line N"); its figures were rendered
from `refs/.../Figures/*.pdf` where a reading from them is claimed.

Authority used: run files and `paper/data/runs.json`, `paper/data/ledger.txt`, the tables;
then `docs/TESTLOG.md` (later and "Correction" entries override); then the briefs. Where a
claim rests on an analysis record outside these (e.g. `docs/results_geodesic.md`,
`docs/results_cluster_test.md`), that record is named.

Counts: A 30, B 34, C 22, D 10, E 8.

---------------------------------------------------------------------------------------------

## A. Factual errors, overstatements, statements contradicted by later corrections

Ranked by severity (A1 most serious).

### A1. Coarser clouds: the introduction's conclusion is contradicted by the latest controls
- **introduction.tex:11**, "Coarser particle clouds---a tempting change on sparse refined
  meshes---raise constraint violations and drive black hole mass drift, so clouds belong on
  the finest local level (Sec. V)."
- Wrong on two counts. (i) On a random sample at the full refinement depth the published
  (finest-level) rule cannot reach black-hole formation at all: the block count passes the
  limit at t = 8.8 M (1884 > 1800, n_f = 1) and t = 10.2 M (2024 > 2000, n_f = 4+c), while
  capped clouds carry both runs through formation with M_AH within 0.15 percent of M after the
  matter is removed (Table III rows "Largest MeshBlock count", "M_AH/M at t = 20M, 40M";
  TESTLOG "Monte Carlo dust ball: published rule runs away with either filter (14:50)", item (3)
  of "... at equal settings (15:50)"). (ii) "drive black hole mass drift" is not specific to
  coarse clouds without a lattice: at equal settings (finest h/4, 4+c) the published rule goes
  1.0019 -> 0.9973 (-0.46 percent after formation) and capped clouds 0.9990 -> 0.9946
  (-0.44 percent); the two differ by an offset of 0.27 percent and by a 3x higher ||H|| after
  formation (`os/mc_nocap4`, `os/mc_adapt4`; Table III). A drift that distinguishes the rules
  exists only on the lattice (-0.13 vs +0.65 / -1.1 percent).
- Replace with the conclusion the log itself draws (15:50, "Conclusions that these support"
  (1)-(3)): coarser clouds raise the constraint violation around a forming black hole and
  shift M_AH by a few tenths of a percent (more on a lattice, where it comes with the beat),
  but on random samples at full depth they are what keeps refinement bounded; the published
  rule is used wherever refinement stays bounded. The method section (method.tex:139) and
  Sec. V A (self_gravity.tex:41) already say this; the introduction must match.

### A2. Horizon-finder check: three statements contradict Table II and Fig. 9
- **self_gravity.tex:30**, "Across three cell spacings on that puncture, AthenaK's distributed
  finder reported masses well below M, with a larger deficit at finer resolution". Table II:
  0.9353, 0.9771, 0.9406 at dx = M/4, M/8, M/16 (deficits 6.5, 2.3, 5.9 percent): not
  monotonic, and largest at the coarsest mesh. Same paragraph: "The deficit is largest on the
  finest mesh" is false against M (it holds only relative to the slice mass: 3.1, 2.4, 5.9
  percent).
- **self_gravity.tex:30**, "That check showed that the evolved spacetime carried the mass M to
  the accuracy plotted and that the deficit belonged to the finder." At dx = M/4 the slice
  Misner-Sharp mass is 0.9656 (Table II; `runs.json` slice_masses `puncture/hcal/dx4`; TESTLOG
  10:00 correction to "Horizon mass calibration: results"): the spacetime itself is 3.4 percent
  light there, about half of the M/4 deficit. Restrict the sentence to M/8 and M/16 (slice
  1.0016 and 1.0000).
- **assembly.tex:18**, "Independent evaluations of the slice Misner--Sharp mass M_MS confirmed
  that the evolved black hole spacetime carried the mass M to the accuracy shown in Fig. 9"
  (same error) and "... brought the apparent-horizon mass into agreement with M_MS across the
  plotted resolutions." The corrected finder was evaluated only at M/8 (1.0013, and the live
  run 1.0003) and M/16 (0.99974); Fig. 9 has no diamond at M/4 (TESTLOG "Further checks of the
  corrected finder"). Note: `notes/claims_brief.md` ("worse on finer meshes") carries the same
  error; the table overrides it.

### A3. The list of documented differences from Ref. in the introduction is incomplete
- **introduction.tex:11**, "Documented differences from Ref. appear in the collapse times of
  unstable clusters and in the collapse of one perturbed near-critical model (Sec. V C)."
- Sec. V C documents more: (i) migration: every extremum after the first maximum earlier
  (cycles 250-290 M against 290-310 M) and later swings smaller (0.795-0.853 against
  0.78-0.865) (self_gravity.tex:102; TESTLOG "Migration ... complete to 2500 M (13:45)");
  (ii) central lapse after horizon formation 0.02-0.05 against about 0.2 (self_gravity.tex:100;
  TESTLOG 12:10 corrections, last item); (iii) y_c = 0.605: growing core oscillation before
  collapse where the published lapse falls smoothly (self_gravity.tex:100); (iv) the original's
  perturbed near-critical curve is matched by the unperturbed model here about 150 M later
  (TESTLOG 13:50). The prolate horizon-mass deficit is a limitation, not a difference, and is
  correctly labelled in Sec. V B.

### A4. What Ref. reports for the near-critical model is misdescribed
- **self_gravity.tex:111**, "Near the binding-energy maximum, Ref. applies a ten-percent density
  perturbation to y_c = 0.756 and observes bounded oscillations with every macroparticle
  retained."
- The original's stated outcome is a reconfiguration into a persistent core-halo structure
  (orig. lines 1213, 1219, 1228): r_99 grows from about 7 M to excursions near 18 M and settles
  near 15 M at 2000 M, inner quantiles contract, and a Plummer-like fit gives a_fit = 6.52 M,
  p = 4.17 (orig. 1304-1308); alpha_c goes from 0.75 to 0.70 at 2000 M (orig. 1221). Its N is
  10^6 (orig. 1217). State this, and limit "That evolution ... resembles the published curve of
  the perturbed model in Ref. most closely" to the central-lapse curve: no run here measures
  r_99 or runs past 800 M, so the core-halo outcome is not compared.

### A5. Interpolation against Cartesian time-stepping: "down to the finest steps tested" is false
- **test_particles.tex:41**, "Direct differences between mesh and analytic-Cartesian final
  states at equal Delta t confirm that spatial interpolation shifts the position far less than
  Cartesian time-stepping down to the finest steps tested."
- `docs/results_geodesic.md` (lines 378-384, 415-416): interpolation alone moves the final
  position by 5e-5 to 2.3e-3; at the published step (0.01 M) that is one to two orders below
  the time-step error (1.73e-2 analytic Cartesian), but "the two contributions become
  comparable only at dt ~ 0.001 M (at dt = 0.00125 M: lattice 8.9e-5, Cartesian analytic
  2.7e-4, difference 3.4e-4)". At the finest step the interpolation effect exceeds the
  Cartesian error. Replace "down to the finest steps tested" by "at the published step size;
  the two become comparable near Delta t = 0.001 M".
- Same paragraph, "Spatial interpolation sets the (E, L_z, Q) errors on the mesh, which exceed
  analytic Cartesian values at the published step size and flatten onto an interpolation floor
  as Delta t shrinks" is supported by `results_geodesic.md` (Q: 40x, E: 3.5x; E floor 8.8e-7)
  but not by Fig. 4, which shows no analytic-Cartesian invariant curve and no Delta t sweep of
  the invariants (see B6).

### A6. "Two algorithmic changes" undercounts what the paper itself says is required at N = 1e4
- **introduction.tex:11**, "Self-gravitating evolutions at ten thousand macroparticles require
  two algorithmic changes (Sec. V)."
- The manuscript elsewhere requires more: (i) on random samples refinement runs away under the
  published rule at full depth (self_gravity.tex:41, 58; Table I footnote d), handled by capped
  clouds, by one level fewer (prolate, TESTLOG 12:49), or by the compensated filter for the
  early noise-driven part; (ii) for black holes of 0.1 M the method section adds a second
  removal rule and a finder flow constant reduced twentyfold (method.tex:195; TESTLOG 17:40,
  18:30, 18:40). Either count these or scope the sentence ("two changes to the published
  algorithm for dust collapse and cluster equilibria").

### A7. "Once one unstated choice is identified": the paper finds more gaps in the published text
- **introduction.tex:11**, "The published description suffices to rebuild the method and
  reproduce the single-particle errors of Ref. once one unstated choice is identified".
- As the answer to the paper's first question this omits gaps the paper documents: the sign and
  form of the near-critical density perturbation (self_gravity.tex:111; orig. 1217 states only
  "a density perturbation of 10%"); the host-cluster radius inconsistent with the quoted orbital
  speed (appendix_sampling.tex:77; `notes/2026-11-13.md`, "Cluster with two overdensities":
  13.3 M fits 0.133215, the stated 30 M gives 0.103); the number of filter passes per test (not
  stated anywhere in orig., see A8); the finder flow constant for small black holes. If the
  sentence is meant only for single-particle benchmarks, say so and list the other gaps
  (`notes/claims_brief.md` A1 lists two of them).

### A8. A filter choice is attributed to Ref. that its text does not state
- **method.tex:151**, "Spherical dust collapse on a lattice retains one plain binomial pass
  [Wu:2026nrpic]."
- The original defines one pass of the binomial filter (orig. 680-686) and never states how
  many passes any test uses (no other occurrence of "pass"/"filter" in its text).
  `notes/method_brief.md:251` itself says "one or two passes". Write that the pass count is
  not given in Ref. and one pass was chosen here (and add it to the unstated choices, A7).

### A9. Prolate refinement: bounded only after a level was removed, not by the filter
- **self_gravity.tex:58**, "Four binomial passes with compensation (Sec. III C) keep the block
  count bounded throughout the prolate collapse."
- With the same filter and finest cells M/32 (`prolate/e09_v7`) the refinement asked for 2584
  blocks at t = 16.3 M; the compensated filter removed only the early, noise-driven refinement,
  and the late refinement "belongs to the collapse itself" (TESTLOG "Prolate collapse, attempt
  with compensated filter (12:49)"). The production run `prolate/e09_v8` has one level fewer
  (finest M/16, at most 1352 blocks). Same paragraph: "drives unbounded block growth" ->
  "growth past the block limit (1884 > 1800 at 8.8 M; 2024 > 2000 at 10.2 M)"; no run shows
  unboundedness. The paragraph also duplicates self_gravity.tex:41.

### A10. Direction of the lattice surface-count offset is overgeneralized
- **introduction.tex:11** "discrete site counts inside a sphere exceed its continuum volume at
  low particle number"; **self_gravity.tex:28** "At N <~ 1e4, however, more lattice sites lie
  inside the sphere than its volume in cells"; **appendix_sampling.tex:33** "so summed m_p^pub
  exceeds M_0 on small lattices".
- TESTLOG "Dust collapse: the published lattice rule at 10^4 particles carries 1.2 percent too
  much mass (07:05)": the offset is "between -0.7 and +2.5 percent for n_lat = 14 to 27"; it is
  +1.18 percent for this lattice (9328 sites for a volume of 9203 cells). Say "differ", and give
  the sign for n_lat = 26.

### A11. "Every diagnostic run ... preceded by a written statement ... under every mechanism"
- **assembly.tex:18**, "Each diagnostic run meant to explain an anomaly was preceded by a
  written statement of the outcome expected under every proposed mechanism."
- Counter-examples in TESTLOG: "Reruns with working finder ... (18:05)": "No prediction is
  attached: this is a measurement of where the failure starts" (run `jeans/diag_v14`);
  "Reconfiguration test, first attempt (10:12)" and "Consistent initial data (10:35)": "No
  prediction is made for the outcome"; prediction 4 (06:22): "no prediction for the lapse".
  Many predictions state the expected outcome of one reading with the alternative only implied.
  Say "most", or "each control run designed to test a stated explanation".

### A12. Halved cell size does not "leave the oscillation unchanged"
- **self_gravity.tex:89**, "... and halving the cell size over the cluster likewise leaves the
  oscillation unchanged."
- TESTLOG "Stable cluster at half the cell size: the oscillation does not shrink (12:58)": first
  maximum equal to 3 percent, but the half-swing grows at 1.70e-5 per M against 1.34e-5 (+27
  percent), last minimum -0.0158 against -0.0108, mean ends 0.0073 below equilibrium against
  0.0039. What was refuted is the predicted fourfold drop. Replace by "does not shrink it; the
  swing grows at the same rate or slightly faster". No table row or figure shows this run (B12).

### A13. Unperturbed stable cluster "as at N >= 1e6 in Ref."
- **self_gravity.tex:69**, "An unperturbed cluster on the stable branch (y_c = 0.819) was
  expected to stay near equilibrium with minor oscillations, as at N >= 10^6 in Ref."
- The original shows y_c = 0.819 only with the inward kick (orig. 1138, Fig. st_dynamics; "only
  small-amplitude oscillations"); its unperturbed y_c = 0.819 runs (Appendix B of orig., 1-8e6
  Monte Carlo) show constraint norms only and state that they "do not assert convergence of the
  late-time lapse or shell oscillations" (orig. 1466). Table V row "Rise of alpha_c ... within
  130M" likewise sets the unperturbed runs here against "approx 0.01 (read from figure)", which
  is the kicked run of the original. Say "as for the kicked model in Ref.".

### A14. "10^6 or more macroparticles" in Ref.
- **self_gravity.tex:3**, "Whereas Ref. evolves self-gravitating benchmarks with 10^6 or more
  macroparticles on large machines".
- The OS fiducial run has N = 998,592 (orig. 917); its OS convergence runs include N = 125,000
  (orig. table, cases A1, D1) and its prolate convergence starts at 5e5 (orig. 975). Use
  "about 10^6 to 5 x 10^6 in its main runs".

### A15. Particle-removal paragraph contradicts itself and omits Ref.'s horizon-based excision
- **method.tex:195**, "Lapse excision ... removes particles with alpha < alpha_exc, clearing black
  hole interiors through this lapse criterion alone." The next sentence says the opposite on
  coarse meshes ("lapse excision alone leaves matter inside the black hole"). Make the first a
  statement about Ref.'s default.
- The original also implements apparent-horizon-based excision and "find[s] no significant
  difference" for its benchmarks (orig. 678). The second rule here is presented as new and the
  list of unimplemented options (method.tex:227) is silent on it; say that Ref. offers it and
  that here it becomes necessary at 3-10 cells per horizon radius.
- "ignores surfaces several times larger than the starting radius": the rule's factor is four
  (TESTLOG "M/128 chain failed at the same step ... (18:40)").
- "used only for black holes of a tenth of the total mass (Sec. V)" points to a subsection that
  does not exist yet (B2).

### A16. Finder flow constant "reduced in proportion (by a factor of twenty for m = 0.1 M)"
- **method.tex:195**. Proportional reduction would be tenfold. Production used 0.05 (20x) for
  each individual horizon and 0.2 (5x) for the common horizon, with 2000 flow iterations and
  mass tolerance 1e-7 instead of 400 and 1e-5 (`runs/jeans/n1e4_v14/chain/config.sh`
  EXTRA_ARGS; TESTLOG "Second finder test (17:40)": "The constant 0.05 is the safer one").
  State the values, not a proportionality.

### A17. "Before dynamic refinement" / "the first refinement" in the dust subsection
- **self_gravity.tex:19**, "Before dynamic refinement, the central density E_c(tau_c) likewise
  follows the cycloid closely". In `os/nocap_sc` the central blocks refine to h/2 at t = 0.64 M
  (MeshBlocks 288 -> 344, `runs/os/nocap_sc/os.nrpic.hst` column 23) and to h/4 at t = 7.29 M
  (-> 400). E_c follows the cycloid until the refinement to h/4 (TESTLOG 13:35: "0.27 to 0.52
  after the centre is refined to h/4 (t = 7.3 M)").
- **self_gravity.tex:39**, "an unlimited cap removes the ||H|| jump at the first refinement":
  it is the refinement to h/4 (Table III row "within 1M after the refinement to Delta x = h/4").

### A18. "This published rule ... is used for every result in the paper"
- **method.tex:121** "This published rule ... is used for every result in the paper"; **method.tex:139**
  "Every collapse result in Sec. V uses the published rule"; **self_gravity.tex:41** "... is
  used for every collapse result in the paper."
- Sec. V A and Table III report level-capped collapse runs (`os/adapt_sc`, `adapt_mc1/2`,
  `mc_adapt2/3/4`); the only full-depth random-sample black holes are capped. Say "every
  production result; the level-capped runs are controls".

### A19. "Each stage of the cycle ... conserves deposited weight across refinement boundaries"
- **method.tex:3**. The mesh filter is not conservative across levels (method.tex:151;
  test_particles.tex:52; `docs/results_cluster_test.md` section 2(c): up to 7.3e-3 after the
  filter for the plunging family), and excision is irreversible, so "each stage preserves
  orbital time-reversal symmetry" is also too strong. Restrict both to the pusher and the
  unfiltered deposition.

### A20. Finite-difference order and ghost cells
- **method.tex:167**, "sixth order on refined meshes and fourth order on uniform meshes": every
  Z4c run uses nghost = 4 (sixth order) and none evolves Z4c on a uniform mesh
  (`problems/*/*.athinput`); the fourth-order clause describes no run here.
- **method.tex:97**, "The stencil needs at least two ghost cells ..., and the runs here use more."
  The Kerr/Schwarzschild mesh tests and the test-particle clusters use nghost = 2
  (`problems/kerr/geodesic_mesh.athinput`, `problems/cluster_test/cluster_mesh.athinput`).

### A21. Original's collapse-time caveat strengthened
- **self_gravity.tex:100**, "Reference notes that these collapse times depend on N and sampling
  noise." Orig. 1138: "The collapse time should be treated as a proof of principle, as it could
  depend on the number of particles sampled and therefore the initial numerical noise." Keep
  the "could".

### A22. Mis-citation of analytic stability theory as numerical studies
- **introduction.tex:3**, "Early numerical studies with spherical codes mapped equilibrium
  sequences, radial stability, and black hole formation in relativistic clusters
  [1968ApJ...154..251I, 1980ApJ...238.1101I, ST85a, ST85b]". Ipser & Thorne (1968, "Stability
  theory for radial perturbations") and Ipser (1980, "A binding-energy criterion") are analytic
  (bibliography entries [10], [11] in the PDF; orig. 1006 cites them as stability theory). Cite
  them for stability theory and ST85 for the spherical particle codes.

### A23. Kicked stable cluster: "within a narrow band"
- **self_gravity.tex:78**, "... and hold successive rest-mass radii within a narrow band around
  equilibrium, as in Ref." For y_c = 0.819 the 10 percent radius swings between 2.5 and 3.5 M
  against 3.13 M at the end (TESTLOG "Stable model with the one-percent inward kick (06:47)"),
  i.e. -20/+12 percent; only y_c = 0.900 stays within 4 percent (TESTLOG 08:43). Same
  sentence's Table V reference for the mean Lorentz factor: Table V has no such row (B11).

### A24. Test-particle invariants "without secular drift" and "third order"
- **test_particles.tex:43**, "Single-particle (E, L_z, Q) errors stay bounded without secular
  drift, independently of N." `docs/results_cluster_test.md` 2(a): L_z and Q errors "grow slowly
  in the first orbit and then level off"; in Fig. 6 the 99th-percentile mesh curves rise by a
  factor of a few over 1000 M. "decrease at third order with h": measured 2.96 (E) and 2.54
  (L_z) (same file, lines 156-160). Say "about third order in E, 2.5 in L_z".

### A25. Core period "at" the radial period
- **self_gravity.tex:87**, "alpha_c oscillates at the radial period of a particle in the core".
  Table V: 75 M against 66 M. Say "close to".

### A26. Kick definition attributed to Ref.
- **appendix_sampling.tex:66**, "an inward velocity kick of fractional amplitude delta_v scales
  the radial momentum component as in Ref., shifting u-hat to u-hat - delta_v r-hat". The
  implementation adds a coherent inward component; it does not scale u_r. The original states
  only "a coherent inward radial velocity perturbation ... with perturbation amplitude <~ 1% of
  the unperturbed equilibrium local velocity" (orig. 1138); its form is not given, so "as in
  Ref." should become "consistent with Ref.'s description".

### A27. Role description of the agents
- **assembly.tex:16**, "A single language model in the solver-development role produced the
  component design, the symbolic derivations, and the solver source." TESTLOG "Consistent
  initial data for perturbed clusters (10:35)": "Two slips in the derivation I had handed over
  were corrected by the agent who implemented it"; "Second finder test (17:40)": "Change to the
  source normalization (my code)". These entries suggest derivations and source changes also
  came from the logging (verification) agent. I could not verify the role split; please check
  against the session records before submission. See also B29 (assembly vs acknowledgments).

### A28. Dust: published-mass run "kept ... alpha_c and E_c" shown nowhere
- **self_gravity.tex:28**, "Runs with published masses kept the interior density exact---so
  alpha_c and E_c still matched the analytic collapse---yet left an apparent-horizon mass M_AH
  visibly above M (Fig. 8, orange curve)." True per TESTLOG 07:05 and 07:32 (lapse histories
  agree to a few 1e-3), but the orange run appears only in the bottom panels of Fig. 8; cite the
  log or add a table row (Table III has M_AH only).

### A29. Prolate: "a few percent" and "several times"
- **self_gravity.tex:56**, "The remaining few percent of M after lapse excision reside in
  gravitational fields outside the black hole" -> "five to eight percent" (TESTLOG "Prolate
  collapse: where the five percent are (14:12)"; Table IV: 0.920 +- 0.027 at the horizon, 0.999
  at large radius). "several times above its lattice dust peak" -> "about three times" (6.31
  against 1.90, Table IV; TESTLOG 14:25 correction).

### A30. Migration run: "a damped oscillation ... to the end of the run"
- **self_gravity.tex:102** is supported; but note for the comparison that the finest level of
  the static migration mesh covers |x| < 7.9 M, so after t = 100 M most matter sits on cells of
  M/2 to 1 M (TESTLOG 06:47 addendum), whereas Ref. refines adaptively to M/16 (orig. 1166).
  The log lists the mesh as one of the untested candidate causes of the shorter cycle (13:45,
  last item). Not an error; a reader comparing timings needs this sentence.

---------------------------------------------------------------------------------------------

## B. Internal consistency

### References, outline, dangling pointers
- **B1. introduction.tex:13 (outline).** Sec. V is described as "spherical dust collapse and the
  sequence of relativistic clusters"; it also contains the prolate collapse (Sec. V B), the
  migration and near-critical runs, and (pending) the two-overdensity cluster. "the appendix
  records the scenario parameters": there are two appendices; Appendix B (initial data and
  sampling) is not mentioned.
- **B2. method.tex:195**, "(Sec. V)" for black holes of a tenth of the total mass: no such
  subsection exists in this draft; the rule is never exercised in the text that exists.
- **B3. appendix_sampling.tex:77**, "the rebuild adopts this self-consistent host radius in the
  parameter table": Table I has no row for the two-overdensity cluster.
- **B4. appendix_sampling.tex:29**, "with n_lat in the parameter table": Table I gives h = 0.30M
  and N = 9328, not n_lat (= 26, `runs.json` os/nocap_sc).
- **B5. appendix_sampling.tex:38**, "E_0 = alpha_s in Eq. (43)": Eq. (43) (cluster_sequence)
  contains y_c and E_b only; E = alpha W = alpha_s is in the sentence before it. Line 46,
  "interior profiles matched at rbar_s from Eq. (B4)": Eq. (B4) is the dust-ball equation; only
  its first line (isotropic surface radius) applies.
- **B6. test_particles.tex:41** cites Fig. 4 for the invariant-error floor and the
  interpolation/time-step split; Fig. 4 shows invariants only for spherical analytic and Hermite
  input at Delta t = 0.01 M. **test_particles.tex:32** cites Fig. 5 for third-order convergence
  "for both a = 0.9M and a -> 0"; Fig. 5 is a -> 0 only (a = 0.9 is in Table II).
- **B7. assembly.tex:20**, "The data-availability statement at the end of the paper": it is
  printed on p. 22, before both appendices and the bibliography.

### Captions against figures (PNGs and rendered PDFs inspected)
- **B8. Fig. 2 (fig:deposition) caption**, "Right: ... numbers give leaf-cell weights omega_Cp":
  the right panel has no numbers (they are in the left and middle panels). The middle-panel case
  ell_p = ell is the capped branch (under the published rule this particle would have
  ell_p = ell+1); the caption should say so.
- **B9. Fig. 4 (fig:passage) caption**, "Solid, dashed, and dotted curves mark analytic spherical
  Kerr--Schild, analytic Cartesian, and mesh-reconstructed metrics": dashed curves appear only in
  the top-right panel.
- **B10. Fig. 5 (fig:convergence) caption**, "errors versus h on the mesh": the axis is
  "Delta x/M (mesh)" (NOTATION.md: h only in the reconstruction formulas).
- **B11. Fig. 10 (fig:prolate) caption**, "Dashed: first apparent horizon": in the bottom panels
  red dashed curves are the outermost particle (left) and the surviving fraction (middle); the
  black curve "horizon" in the |z| panel and the "outermost particle" curve are not described.
- **B12. Fig. 12 (fig:clusters) caption**, "from least compact (left) to unbound (right)": the
  rightmost model is the most compact; order by compactness and mark the unbound one.
- **B13. Fig. 6 (fig:tpcluster) caption** shows E and L_z; the text (test_particles.tex:43)
  claims Q as well.
- **B14. Fig. 1 (fig:cycle)** has a "Reconstruction" stage and no "save metric" stage; the text
  (method.tex:5) lists six stages that include saving and exclude reconstruction.
- **B15. Fig. 16 (fig:hypergraph)** and assembly.tex:5 name the deposition component
  "level-capped deposition"; every production result uses the published single-level rule
  (A18). Name it "single-level deposition (with optional level cap)".

### Text citing figures/tables for quantities they do not contain
- **B16. self_gravity.tex:69**: "expanded by a visible fraction of its radius ... (Fig. 11, left
  panel, solid curves)" -- Fig. 11 shows the central lapse only; "central density dropped ...
  (Table V)" -- Table V has no central density. The numbers (radius +15 percent, density -35
  percent) are in TESTLOG "Stable cluster controls: results" and `notes/2026-11-13.md`.
- **B17. self_gravity.tex:78**: "mean Lorentz factor ... (Table V)" -- not in Table V.
- **B18. self_gravity.tex:87**: "outer shells barely move (Fig. 13, top panel; Table V)" -- neither
  shows shells. "A run at N = 10^3 ... (Fig. 13, bottom left)" -- those are kicked runs
  (`st/yc0819_n1e3_v4`, `st/yc0819_v4`) offered as evidence about the unperturbed oscillation;
  say so.
- **B19. self_gravity.tex:89**: halved-cell run and its numbers are in no table or figure (add a
  Table V row: first maximum +0.0036 against +0.0037, half-swing slope 1.70e-5 against 1.34e-5,
  minimum at 276 M -0.0158 against -0.0108).
- **B20. test_particles.tex:70**: "R(tau) and azimuth accumulate a small advance" -- Fig. 7 shows R
  only.

### Tables
- **B21. tab_setups.tex:24 (Near-critical row).** Main entry "L/M = 512, static, 1/4" matches no
  run: the static runs (`st/yc0756_unpert`, `st/reconf_yc0756_v4`) have L = 1024; the two
  adaptive runs (`st/reconf_yc0756_hc`, `_hc_m`) have L = 512 (`runs.json`). Also the
  parenthesis convention ("single runs of a family") is violated for the dust random-sample row
  (three finest-level runs, `mc_nocap2/3/4`, under "(finest level)").
- **B22. tab_setups.tex footnotes** appear in the order d, c, b, a in the printed table.
- **B23. tab_outcomes.tex:97**, Ref. column "approx 0.01 (read from figure)" compares the
  unperturbed runs with Ref.'s kicked run (see A13); label it.
- **B24. Table II/III naming.** Table III caption defines ||H|| "the same measure is used in every
  table"; the text uses "Hamiltonian constraint norm ||H||" from self_gravity.tex:19 on with no
  definition or pointer (see C1).

### Notation (against NOTATION.md) and naming
- **B25. E_0 has two meanings.** Dust: E_0 = rho_0 initial density (self_gravity.tex:7; Fig. 8 axis
  E_c/E_0; Table III). Clusters: E_0 = alpha_s, energy per unit rest mass (appendix_sampling.tex:38,
  58; NOTATION.md). The same cluster energy is called script-E in self_gravity.tex:62.
- **B26. Cycloid parameter.** Text uses varphi and E (self_gravity.tex:7-11); NOTATION.md "the
  cycloid R(eta), tau(eta), rho(eta)". Update NOTATION.md (eta is the shift damping).
- **B27. Overloaded symbols in Sec. III.** s = Hermite offset (method.tex:89) and s = sin^2
  (method.tex:147); c = compensation weight and c_jk, c^t_k triad gradients (method.tex:50, 145);
  F(k) filter response and F(rbar) cumulative mass (appendix_sampling.tex:56); epsilon for the
  Levi-Civita symbol, the refinement indicator varepsilon_i and epsilon_0; L = domain half-width
  (Table I) and total angular momentum (Sec. IV); h = cell spacing in test_particles.tex:32
  ("cell spacing h") against NOTATION.md (Delta x outside the reconstruction formulas).
- **B28. "the published rule" names two different things** in Sec. V A: the lattice mass rule
  (self_gravity.tex:28) and the deposition rule (self_gravity.tex:41). Use "published lattice
  masses" and "finest-level clouds" consistently (the figure legend already does).
- **B29. Roles.** assembly.tex:16 "Separate language models in the verification role" against
  acknowledgments.tex:11 "One language-model family served each of the dedicated ... roles".
- **B30.** alpha_s, I (Kretschmann), varepsilon_i/epsilon_0/delta_0, Lambda_h, delta_rho, delta_v,
  W_c, n_lat are used but absent from NOTATION.md.
- **B31.** Fig. 8 legend "level-capped cloud" against caption "level-capped clouds with unlimited
  (yellow)"; the yellow curve in the top-right panel is the unlimited cap; the one-level run is
  absent there although the text compares its E_c (self_gravity.tex:39).
- **B32.** "bound models (E_b > 0)" (self_gravity.tex:100) includes the two stable models; write
  "bound models past the maximum".
- **B33.** method.tex:139 "using either a fixed or density-adaptive ceiling" -- only the
  density-adaptive cap is used in any reported run; the fixed cap appears only in the
  deposition test (TESTLOG "Deposition on refined meshes").
- **B34.** Sec. V A says "first refinement" where Table III says "refinement to Delta x = h/4"
  (A17).

---------------------------------------------------------------------------------------------

## C. Method completeness (used in results but not defined or specified)

- **C1. ||H||.** Defined only in the Table III caption (square root of the integral of H^2 over the
  proper volume, cells with chi < 1/16 excluded, not divided by volume; TESTLOG 16:10 correction).
  It differs from Ref.'s coordinate-volume-weighted RMS norm (orig. 1497-1502), so cross-paper
  comparisons need the definition in Sec. III. "Constraint norms" (plural, self_gravity.tex:69)
  implies a momentum-constraint norm that is never defined.
- **C2. Z4c and gauge parameters.** Only kappa_1 = 0.02 is given (Table I). Missing: kappa_2 = 0,
  eta = 2, mu_S = 0.75, Kreiss-Oliger coefficient 0.5, CFL 0.25, lapse and shift advection on,
  chi floor 1e-5 (`problems/os/os_amr.athinput` <z4c>; same in all inputs via runs.json
  "spacetime"). The shift equation used (mu_S Gamma-tilde, no alpha^2) differs from Ref.'s written
  alpha^2 mu_S form (orig. 375-376; `athenak/src/z4c/z4c_calcrhs.cpp:647-656`); say so.
- **C3. c_H.** method.tex:174 says c_H "sums a constant and a term proportional to Delta x"; the
  only run uses c_H = 0.05 M and a zero Delta x term (Table I footnote a; runs.json
  `st/osc/ch0p05`).
- **C4. Density-adaptive level cap.** How ell_cap follows "local particle density" is not given:
  target 1 particle per cloud cell measured on the previous deposit, floor level 4 (cloud never
  coarser than the lattice cell h), maximum coarsening 1, 2 or unlimited (`os_amr.athinput`
  deposit_ppc, deposit_min_level, deposit_max_coarsen; `notes/2026-11-13.md` "Decisions").
- **C5. Refinement criterion values.** Thresholds 0.2 / 0.02, epsilon_0 = 0.01, delta_0 = 1e-99
  (same as Ref., orig. 722-725; `athenak/src/z4c/z4c_amr.cpp:41-43, 260`); check every 4 cycles,
  refinement interval 8; num_levels, inner radius and level per scenario (radius_0_rad,
  radius_0_reflevel); MeshBlock limits, which decide the "runaway" results (Table I footnote d
  gives two of them).
- **C6. Horizon finder settings.** Search every 16 cycles, 16 angular points, l_max = 8, mass
  tolerance 1e-5, 400 flow iterations, initial radius 1 M, start time (8 M for dust), flow
  constant 1.0, mean-expansion tolerance 100; for small black holes 0.05/0.2, 2000 iterations,
  1e-7 (A16); order of the Lagrange interpolant whose derivative is used.
- **C7. Removal rules.** alpha_exc per scenario is in Table I only; the value 0.62 for the
  test-particle clusters (Kerr-Schild lapse at r = 1.25 M, `problems/cluster_test/
  cluster_mesh.athinput` header) needs a sentence; horizon-based rule factors 0.8 and 4 (A15);
  outer-boundary treatment of clouds (weight outside the mesh dropped, test_particles.tex:52).
- **C8. Pusher iteration.** Tolerance 1e-7 and at most 50 iterations in production, 2e-14 for the
  Kerr benchmarks (TESTLOG first entry; `os_amr.athinput` <particles>); initial guess.
- **C9. Random-sample dust ball.** The sampler is not described in Sec. III F or Appendix B
  (equal masses, acceptance psi^6/psi(0)^6 as in orig. 909-913?); Table I says only "equal
  masses".
- **C10. Misner-Sharp evaluation.** How R and K_T are computed on coordinate spheres, the shell
  averaging and the "spread over angle" quoted in Table IV, and the centre used.
- **C11. Time step under refinement.** The global step halves whenever a finer level appears
  (runs.json dt_halvings); Table I gives the first step only.
- **C12. Test-particle cluster initial data.** Gaussian widths in position and velocity, the
  factor f_L of the circular angular momentum, and the definition of the "plunging family"
  (`docs/results_cluster_test.md` section 1) are absent.
- **C13. Tracer initial data.** Radii (7.04, 9.03, 11.03 M), inclinations, the plunge and the
  radial-infall start for the puncture runs, and the six head-on tracers are not given.
- **C14. Mass-shell radii.** Fig. 12 uses radii about the origin while diagnostics use the centre
  of mass (TESTLOG 12:10); Figs. 14-15 not stated.
- **C15. Central probe in clusters.** "eight central cells" is stated in Table V; the 1.5 percent
  offset of alpha_c(0) for y_c = 0.283 from the probe averaging (TESTLOG 12:10) should be noted
  where alpha_c is compared with alpha_c,eq.
- **C16. Kretschmann scalar.** Finite-difference order used for D_i K_jk and the Ricci terms (sixth
  order per TESTLOG "Kretschmann scalar").
- **C17. Filter per scenario** is complete in Table I, but the text does not say that the
  test-particle clusters use two plain passes and the vacuum runs none.
- **C18. Lattice alignment.** h equals the level-4 cell (os_amr.athinput header), as NOTATION.md
  requires to be "stated there"; Sec. V A does not state it.
- **C19. Outer boundary.** "Sommerfeld radiative outer boundaries" while the mesh inputs set
  outflow; one sentence that Z4c applies Sommerfeld conditions on outflow faces
  (`athenak/src/z4c/z4c_Sbc.cpp`).
- **C20. Perturbed initial data.** <W(rbar)> in Eq. (B12) averaged "over directions" -- of what
  momentum magnitude (u_eq at the old radius lowered with psi_eq(rbar_p)^2)? The two lowering
  factors in appendix_sampling.tex:71 should be reconciled in one formula.
- **C21. Unimplemented options.** method.tex:227 lists two; also not implemented here:
  BHaHAHA horizon finder, higher-degree shape functions, electromagnetic fields in the pusher;
  horizon-based excision is implemented but in a different role (A15).
- **C22. Seeds.** Which seeds define "sample 1-3" (for reproduction).

---------------------------------------------------------------------------------------------

## D. Clarity for numerical relativity (NR), plasma PIC (PIC) and stellar dynamics (SD) readers

1. **method.tex:75**, "Free motion in polar coordinates has straight-line solutions, yet a finite
   step that evaluates unit-vector rotation at the midpoint and projects at the endpoints makes an
   error that Cartesian axes avoid." The analogy is the key to the tetrad-gauge result but is
   compressed into one sentence; "unit-vector rotation" and "projects at the endpoints" are not
   tied to Eqs. (14)-(16). PIC and SD readers will not see why a frame choice changes a
   second-order error.
2. **method.tex:83**, "while any triad construction that coincides with these two frames along the
   tested orbits remains consistent with the published digits." Unclear which constructions are
   meant and why this matters.
3. **method.tex:121**, "With ell_loc(p) the finest level among leaf blocks owning the eight cell
   centers nearest x_p": centres at which level? Readers from PIC (WarpX) expect a statement in
   terms of the particle's own cell.
4. **method.tex:195** (one paragraph): lapse excision, a second removal rule, the finder's
   ghost-zone defect, the fix, and the flow constant in one block, with the scope pointing to a
   missing subsection. NR readers need the finder defect; PIC/SD readers need the removal logic;
   split.
5. **self_gravity.tex:13-17**, "Under 1+log slicing without shift advection from unit initial
   lapse, local integration inside the homogeneous core gives an analytic lower bound on alpha_c
   ... Until a coordinate slicing wave launched at the surface density jump reaches the origin,
   causal isolation keeps alpha_c on the lapse bound". PIC and SD readers do not know why the lapse
   is a diagnostic or what a "slicing wave" is (a gauge mode).
6. **self_gravity.tex:39**, "That excess arises because the contracting lattice beats against a
   cloud lattice of nearly equal spacing at the center." "Cloud lattice" is undefined; the reader
   needs that capped clouds sit on cells of size about h, the particle spacing.
7. **self_gravity.tex:41**, the random-sample paragraph ("full-depth refinement", "one level
   shallower", "equal settings") together with the Table III row "order of the runs below: capped
   clouds at the full depth with n_f = 1 and 4+c; one level fewer, finest-level and capped clouds
   (4+c)". Four runs plus two failed ones are hard to keep apart; a four-line table in the text
   (rule x depth x filter -> outcome) would fix it.
8. **self_gravity.tex:62**, "populate one Killing energy E = alpha W = alpha_s. Here alpha_s is the
   boundary lapse where particles turn around (W = 1)." SD readers know "isotropic monoenergetic
   (single-energy) cluster"; "boundary lapse" and "turn around" need "the surface, where the
   particles' speed vanishes".
9. **self_gravity.tex:89**, "On the full-range lapse axis of the sequence figure in Ref., a swing of
   this size in y_c = 0.819 sits at the resolution limit of the curve." Meaning: the original's
   figure cannot show a 0.01 swing. Say that.
10. **appendix_sampling.tex:22**, "In multi-component superpositions, each component multiplies
    its isolated particle masses by psi psi_c^{-1} (psi_c = 1 and rest mass m_c W_c^{-1} at bulk
    Lorentz factor W_c) and lowers orthonormal momenta with psi^2." Too dense to rebuild from;
    write the two cases (tabulated envelope, boosted Gaussian) separately.

Also hard (beyond the ten): introduction.tex:5 "the standard way to evolve Einstein's equations
through black hole formation on a fixed grid, advances the spacetime on an adaptive mesh" ("fixed"
means "without excision", which a PIC reader will read as "not adaptive"); self_gravity.tex:56 "That
enclosed geometric mass combines gravitational radiation and constraint violation in one total";
the Fig. 6 caption parenthesis "(yellow edges: the spacetime Boris run under the implicit midpoint
run)".

---------------------------------------------------------------------------------------------

## E. Layout (main.pdf, 30 pages; pages rendered and inspected)

- **E1. Floats drift two to three pages past their first reference** and land in unrelated
  sections: Fig. 6 (test-particle clusters, Sec. IV A) on p. 13 and Fig. 7 (tracers, Sec. IV B,
  referenced p. 10-11) on p. 14, both inside Sec. V A dust text; Fig. 9 (horizon check, referenced
  p. 14) on p. 16 inside Secs. V B/V C; Fig. 13 on p. 20 (referenced p. 17-18); Fig. 16 on p. 22
  after Sec. VI has ended. `main.log` reports "A float is stuck" at self_gravity.tex:20 and :48
  and assembly.tex:6.
- **E2. Appendix tables are scattered and one lands in the bibliography.** Appendix A is two
  sentences (p. 22-23); Table I is on p. 24, Table II p. 25, Tables III-IV p. 26, Table V p. 27,
  Table VI p. 28. Appendix B's text is broken around them (its Eq. B11 sits under Tables III-IV on
  p. 26), the reference list begins under Table V on p. 27, and **Table VI is printed inside the
  reference list on p. 28**.
- **E3. Data availability and acknowledgments** print on p. 22 before the appendices (see B7).
- **E4. Overfull line** at method.tex:125 (Eq. 24, conservation identity, 9.4 pt): the trailing
  comma reaches the column gutter on p. 6.
- **E5. Captions over five lines:** Fig. 2 (6 lines, full width), Fig. 6 (6 lines, full width),
  Fig. 9 (6 lines, one column), Fig. 14 (6 lines, one column); Table I caption 4 lines plus four
  footnotes.
- **E6. Loose lines:** underfull boxes with badness 7012 (introduction.tex:5, first line of the
  NRPIC paragraph) and 10000 (self_gravity.tex:3, first line), visible as wide word spacing on
  pp. 1 and 11.
- **E7. Table I** (p. 24) uses 2 pt column separation; the "Mesh, Delta x/M" and "Deposition"
  cells wrap into three to four lines ("level-capped (<= 1, <= 2, any)").
- **E8.** The title-page date and the "[Funding ...]" placeholder line in the acknowledgments
  (acknowledgments.tex:15-16) still print.

---------------------------------------------------------------------------------------------

## Checked and found correct (for the record; no action)

Kerr benchmark digits (Table II against orig. 825-833; TESTLOG first entry); symmetric gauge
on analytic input and (x,y,z) Cholesky on the lattice; Hermite weights (orig. 588-591);
characteristic equations and tetrad equation of motion (re-derived: Eqs. 14-17 are consistent);
Boris rotation; compensation response F(k); prolate times (32.0 M, orig. 971) and "Ref. states no
apparent-horizon mass for this test" (orig. 969-975; TESTLOG 16:10); cluster horizon times and
masses (Table V against runs.json); alpha_c after collapse ~0.2 in the original (its Fig.
st_dynamics extends about 20 M past the horizons, rendered); migration extrema (orig. figure
rendered); y_c = 0.283 dispersal and ST85 contrast (orig. 1140); near-critical compressed run
(M_AH 0.99698 against 0.99689; 10^4 removed); dust numbers in Table III; tracer and head-on
numbers; run times (longest production run 2.3 h, `st/migration_yc0500_v4`).

## What I could not check

- Values read by eye from the original's figures other than st_dynamics, the reconfiguration
  figure and the migration figure (e.g. the prolate snapshots); I accepted the log's readings.
- The role assignment of the language models (A27, B29): no ground-truth record in the repo.
- `paper/data/ledger.txt` line by line against every table cell (spot-checked about twenty values
  against runs.json; all agreed).
- Claims that rest only on `docs/results_geodesic.md`, `docs/results_tracers.md` and
  `docs/results_cluster_test.md` (precession, block-face agreement to rounding, phase mixing): I
  read the relevant passages but did not recompute from the run files.
- Whether AthenaK's Sommerfeld condition is active with the outflow mesh flags in every run (C19).
