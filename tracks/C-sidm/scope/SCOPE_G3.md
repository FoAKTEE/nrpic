# Track C, gate G3: scope of the science runs (written 2026-11-28, before any production run)

Owner C-sidm. Written in batch 35 by the lead, after gate G2 was signed (coord/GATES.md,
2026-11-27, pass with reservations) and under decision 0048 item 1: the monoenergetic family and
the King family with b = 0.1 are the first step of G3; no production run of G3 on b = 0.1 models
starts before the bracket of that family is located at a million particles on two meshes with the
horizon finder of core-v0.8 and at least three seeds for the members next to the threshold; this
scope is reviewed independently before production; eighty card-hours toward G3. Only the members of
step 1a (section 2) are queued with this text; nothing of sections 4 to 7 runs before the review.
Labels as in the brief: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 1. The question and what G3 must deliver

The track's second measurement (SCOPE.md:58-59): the collapsed mass fraction f_BH = M_BH/M of a
self-interacting thermal core as a function of the central Knudsen number, converged in particle
number and collision step, for models on both sides of the collisionless threshold. The science
family is the truncated Maxwell-Boltzmann core of arXiv:2108.11967 with b = 0.1 (`tmb01`,
`models/model_set.py`), labelled by the central redshift Z(0). Its first maximum of the binding
energy lies at Z(0) = 0.54041, the fluid onset with the adiabatic index of a Juttner gas at
0.53306 (stable side, by 0.0074) and the onset with gamma = 1 + p/u at 0.63482 (models README,
runs C-20261115-165315-7b473b8 and C-sidm-20261115-120722-38ab057) [VERIFIED by those runs]. For a
core-halo family the collisionless onset can lie beyond the first maximum of the binding energy
(arXiv:2105.05556, cited in the note) [BACKGROUND], so the threshold of this family is measured,
not assumed.

Knudsen number (collide/SPEC.md:41-48): Kn_c = lambda_c/H_c with lambda_c = 1/(rho_0c sigma_m)
and H_c = (v1_c^2/(4 pi rho_0c))^(1/2); sigma_m = K/Kn_c with K = 142.6 for the b = 0.1 model at
the binding-energy maximum (verifier run C-20261115-170630-1037f6a) [VERIFIED by that run].

## 2. First step (decision 0048): the two brackets

### 2a. Thermal core b = 0.1

Models of the `tmb01` grid at N = 1e6, sampled with the stratified sampler of the equilibria
package and kicked inward by one percent of each particle's speed (threshold_scan/make_scan.py
`kick`, as every G2 bracket member): Z(0) = 0.52 (stable side), 0.5404 (unkicked control),
0.56 and 0.60 (past the maximum, below the gamma = 1 + p/u onset). Mesh A is the G2 mesh M/8 of
`longruns/inputs/A8N_*` (root 64^3 over +-512 M, cells of M/4 inside |x|_inf < 7.9 M, M/8 inside
3.9 M; the b = 0.1 core has H_c = 0.96 M, R = 20.4 M, SCOPE.md section 3.2). Mesh B is the G2 mesh
M/16 (level 8 inside 1.95 M) and, for the members next to the threshold only, mesh C = M/4 (no
level 7) for an order. Release core-v0.8 card build; cfl_number 0.25 as in G2 (below the bound 0.47 of the 1+log lapse; no dt_gauge, so the decks differ from G2's only in the model and the finder);
tlim 600 M; history every 0.25 M; restart every 10 M.

| Step | Members | Seeds | Mesh | Entries | Card-hours (each) |
|---|---|---|---|---|---|
| 1a | ctrl 0.5404; kicked 0.52, 0.56, 0.60 | 1 | A | 4 | 2.7 |
| 1b | the two kicked members next to the threshold found in 1a | 2, 3 | A | 4 | 2.7 |
| 1c | the same two members | 1 | B | 2 | 4.0 (unstable), 6.4 (stable) |
| 1c' | the unstable member of the two | 1 | C | 1 | 0.7 |

If 1a leaves 0.60 stable, the next members are 0.6348 and the gamma-onset side is scouted before
1b (the review decides; card-hours from the reserve). Costs are the G2 manifests at the same mesh
and N: 2.63, 2.62, 2.71 card-hours for 600 M on M/8 (C-20261126-020831-fabf2d7,
-130519-1a79a66, C-20261124-221122-928c9eb), 3.97 and 6.38 on M/16 (C-20261126-043714-8ea1c35,
-121449-1d37e77) [VERIFIED from the manifests]; b = 0.1 costs are [TO VERIFY] by 1a.

### 2b. Monoenergetic family (verification family, SCOPE.md section 3.1)

Members y_c = 0.70 (stable side) and 0.66 (unstable side) of the binding-energy maximum
y_c = 0.67961 (run C-sidm-20261115-115344-eb8b752), kicked inward, N = 1e6, seed 1, on meshes A
and B, tlim 400 M (the first paper's unstable models form a horizon before 200 M, SCOPE.md:96-100).
Deck generator from `python/nrpic/st_cluster.py` tables [TO VERIFY: not yet written]. Four entries,
about 12 card-hours. One seed per member: this family enters G3 as a cross-check of the method,
not as a science family (stage/G0 decision 1); the three seeds of decision 0048 apply to b = 0.1.

## 3. What a collapse is from now on

Every G3 deck carries the finder of core-v0.8 (`scratch/core/exe/core_nrpic_v08/READY`;
`coord/INTERFACES/finder_stop.md`):

```
<fastflow>
num_horizons        = 1         # 0 when absent: no finder (z4c/z4c.cpp:286)
find_every          = 32        # every 1 M at dt = M/32
mass_tol_0          = 1.0e-5
flow_iterations_0   = 400
polish_iterations_0 = 100
flow                = shear      # one key for all horizons (z4c/fastflow.cpp:68)
initial_radius_0    = 1.0
diagnostics         = true       # <basename>.horizon_status_0.txt
```

A run has collapsed when the status file reports a found surface (polished, mass rule 1e-5) and
the next four searches are found as well (H1). The lapse marker alpha_min = 0.3 stays in the
history as a second reading; a run that crosses the marker without a found horizon within 50 M is
"undecided", never "collapsed". Horizon masses are quoted with the residual of the mass rule, the
irreducible mass M_irr = (A/16 pi)^(1/2), and only from searches whose status is found.

## 4. Second step: collapsed mass fraction against the Knudsen number

Models: U, the first kicked member on the unstable side of the bracket of 2a, and S, the last on
its stable side (both seed 1, mesh A, N = 1e6). Knudsen numbers Kn_c = infinity (collisions off:
the first step's runs), 10, 1, 0.3 (sigma_m = K/Kn_c). Collision settings of the G2 series
(coll_energy = particle, collision cells of M/4, the D2 f-leg showed the rate independent of the
cell between M/8 and M/2: C-20261124-130442-0819c88).

Statistic: f_BH(Kn) = M_irr(t_H + 100 M)/M_ADM and f_form(Kn) = M_irr(t_H)/M_ADM, with t_H the
time of the first found horizon of H1 and M_ADM the mass of the initial table. For S the
statistic is the fate (found horizon or not by 600 M) and t_H.

Estimator and error: the value of the seed-1 member on mesh A; its error
sigma_f = (sigma_seed^2 + sum over legs Delta_leg^2)^(1/2), with sigma_seed the standard deviation
of f_BH over the three seeds of U at Kn = infinity (1b) and Delta_leg the difference of each
convergence leg of section 6. One seed per collisional member is a limitation of the budget,
stated as such [JUDGEMENT].

Reference: at Kn = infinity the collisionless member of the same model and seed; the first paper
finds M_AH/M = 1.0000 and 1.0001 at the end of its two unstable monoenergetic runs
(SCOPE.md:96-100, 2611.12831 tab_outcomes.tex:120-121) [VERIFIED by the G0 reading], so the
collisionless reference is expected near 1. At the fluid end the reference is stability only:
the Juttner onset 0.53306 lies on the stable side of the maximum, so a fluid at Z(0) = 0.52 is
stable and one at 0.56 unstable [VERIFIED, models README].

## 5. Criteria, with numbers fixed now, and what refutes each

| Id | Criterion | Refuted by, and then |
|---|---|---|
| F1 | b = 0.1 bracket located: members Z_lo < Z_hi of the grid with Z_hi - Z_lo <= 0.04, Z_lo stable (no found horizon, alpha_min > 0.3 to 600 M, 20 M block means of alpha_c - alpha_c(0) within +-0.03 with an interior maximum after the kick) and Z_hi collapsed (H1 before 600 M), in all three seeds on mesh A and in seed 1 on mesh B | any seed or mesh with the other fate: the bracket is not located; no production on b = 0.1; the review decides between a member in between, more particles or a wider bracket |
| F2 | the unkicked control at 0.5404 holds 600 M at N = 1e6 on mesh A (block means within +-0.03, no found horizon) | a collapse: finite-N decay at b = 0.1 even at 1e6; members are then read against the control's contraction as in G2 and this is a failure on record |
| F3 | reading, not a pass item: whether 0.5404 lies inside the bracket | either outcome is a result; prediction in JOURNAL before 1a |
| F4 | monoenergetic members 0.70 and 0.66 keep opposite fates on meshes A and B | equal fates: recorded failure; the family is dropped from the paper's verification table, the b = 0.1 step stands on its own |
| H1 | every collapse is a found horizon: five consecutive found searches, polished, mass rule 1e-5; M_irr non-decreasing within 1e-3 relative afterwards | a marker crossing without a found horizon within 50 M (undecided), or M_irr falling by more than 1e-3: finder or excision defect, reported to core, the run is not used |
| K1 | f_BH(Kn = infinity) >= 0.95 for U on mesh A, all three seeds | below 0.95: mass lost by excision or escaping envelope; the scan waits for its cause |
| K2 | each convergence leg of section 6 changes f_BH of U at Kn = 1 by at most 0.03 (absolute) | a leg above 0.03: its difference enters sigma_f; above 0.10: f_BH(Kn) is not claimed |
| K3 | a dependence on Kn is claimed only if \|f_BH(0.3) - f_BH(infinity)\| > 3 sigma_f | otherwise the result is "f_BH independent of Kn within sigma_f" (a null result, reported as such) |
| K4 | the fate of S at each Kn is read only from H1; t_H quoted with its seed and mesh envelope, no order from two meshes | - |
| B1 | whole-system budget, section 7 | as section 7 |
| C1 | collision count per member and window (0, t_H]: counted/expected with \|z\| <= 3 | \|z\| > 3 in more than one member: the rate in curved spacetime is investigated before more collisional runs |

## 6. Convergence legs that can fail

All at Kn = 1 on model U, seed 1, against the mesh-A member (one run each):

- particle number: N = 3e5 (cost about 1 card-hour);
- collision step: coll_pmax halved (the collision sub-steps double);
- slicing: harmonic lapse (`lapse_oplog = 0`, `lapse_harmonic = 1`) instead of 1+log, with
  cfl_number 0.25 below its bound 0.55 (coord/INTERFACES/step_limit.md); this leg can fail: the
  collapse time and the slice of the horizon change with the slicing, and f_BH must not;
- domain: outer faces at +-1024 M (root 128^3, same cells inside);
- mesh: three meshes C, A, B at Kn = infinity (steps 1b, 1c, 1c'); f_BH of U on the three
  either converges (|f_A - f_B| < |f_C - f_A|) or each difference is at most 0.03; collapse
  times are quoted as envelopes, no order is claimed from two meshes.

The shift-damping leg of G2 is not repeated (it could hardly fail, GATE_REVIEW section 4 C2).

## 7. Whole-system budget with the collisionless drift (B1)

Per collisional run, up to t_H: (a) rest mass sum m conserved to 1e-12 relative up to the first
excision (`*.cons.hst`); (b) the pairwise collision energy budget below 1e-14 of sum m H (G2:
2.8e-16 to 3.2e-16, C-20261124-130442-0819c88); (c) the drift of the total energy of the system,
the ADM mass at the outer extraction radius of the z4c history [TO VERIFY that the decks write
it; otherwise the particle sum sum m W / psi of the initial-data constraint, as in the G0 checks],
minus the same drift of its collisionless twin (same model, seed, mesh), lies within three times
the standard deviation of that drift over the three seeds of 1b. Refuted: collisions change the
system's energy beyond the collisionless drift; the scan stops and core is asked.

## 8. Card budget (80 card-hours toward G3, decision 0048)

| Item | Card-hours |
|---|---|
| heat reruns q0092, q0093 (decision 0048) | 0.6 |
| 1a (4 entries) | 10.8 |
| 1b (4) | 10.8 |
| 1c, 1c' (3) | 11.1 |
| 2b monoenergetic (4) | 12.0 |
| step 1 total | 44.7 |
| 4: U and S at Kn 10, 1, 0.3 on mesh A (6; collisional N = 1e6 cost [TO VERIFY], 3.5 assumed) | 21.0 |
| 6: legs N, collision step, slicing, domain (4) | 11.7 |
| step 2 total | 32.7 |
| reserve | 2.0 |
| sum | 80.0 |

Step 2 is re-costed from the measured cost of step 1 before it is queued; if it does not fit,
the order of dropping is: Kn = 10 of S, then the domain leg; the slicing leg and the particle
number leg stay.

## 9. Optional, only from the reserve or a later allotment

A second seed of the N = 1e4 control N4c and N6c continued to about 900 M (the verifier's test
of a logarithmic law, VERIFIER.md section 3); a second seed per collisional member.

## 10. Order of runs and stops

1. Batch 35: 1a (four entries, priority 2), predictions in JOURNAL before they are queued.
2. After 1a is read: 1b, 1c, 1c' (priority 2), predictions first; F2 decided.
3. 2b monoenergetic, as cards allow.
4. Independent review of this scope (decision 0048 item 1), with F1 and F2 known.
5. Step 2 (sections 4, 6, 7) only after the review and F1 passed.

## 11. What G3 claims, and what it does not

It claims the collisionless bracket of the b = 0.1 family at N = 1e6 with seeds and meshes, and
f_BH(Kn) for one model on each side with the errors of section 4. It does not claim real-core
Knudsen numbers (twelve to twenty orders below, note Sec. I), a located threshold inside the
bracket, or convergence of a collapse time in the mesh.
