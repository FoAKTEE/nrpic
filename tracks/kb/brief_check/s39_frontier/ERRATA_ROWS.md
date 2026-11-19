# Rows for `coord/BRIEF_ERRATA.md` from work package s39_frontier (brief lines 239-256)

Owner kb (helper of the brief check, wave 3a), 2026-11-19. Format of `coord/BRIEF_ERRATA.md`
on main (sections 1, 2 and 4, same columns). Row numbers `s39.n` are provisional; the
orchestrator numbers them when it merges. None of these statements is already in
`coord/BRIEF_ERRATA.md` (no row there cites lines 239-256). Paper locators
`<id>/<v>/src/<file>:<line>` are lines of the TeX sources under `kb-data/raw/arxiv/`;
`meta:<id>` is `kb-data/meta/arxiv-api/<id>.json`. The full check (44 rows: 37 confirmed, 16
of them with a precision, 7 corrected) is `tracks/kb/brief_check/s39_frontier/CHECK.md`
(branch `kb/brief-check`), whose row numbers are given as "CHECK #". The table of lines
239-256 carries no evidence label; its second column is checked as unlabelled claims about
papers, its third column as [JUDGEMENT] whose factual premises are checked.

## 1. Statements of the brief that are wrong or incomplete

| # | Brief line | What the brief says | What is right | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| s39.1 | 243 (§3.9) | "semi-relativistic gravitational waves by the same authors arXiv:2605.04487", relation "Direct competition" | Not the same authors: Escrivà, Harada, Kohri, Terada, Yoo (Terada added). "Semi-relativistic" is the N-body model: collisionless particles in an Einstein-de Sitter background with Newtonian self-gravity and semirelativistic kinematics; the waves come from the numerical quadrupole. Not full NR: it competes with Track B's signal estimate, not with full-relativity particle runs; the direct competitor of the row is 2609.14218 | `2605.04487/v2/src/main_v3.tex:144-148, 171, 189, 209-214`; CHECK #4, #37 | kb (s39_frontier) |
| s39.2 | 244 (§3.9) | 2610.23218: "The gauge scheme can be borrowed directly" | There is no finished scheme: "The best-performing simulations reach close proximity to a black hole; however, further work on the gauge choice is required for this to be stable". What transfers: a softplus lapse that switches from synchronous to puncture-like slicing, and the finding that the best Gamma-driver damping is resolution-dependent, so a spatially varying damping is needed (not yet identified). The matter is a dust fluid (Einstein Toolkit, HRSC), whose shell-focusing failure particles avoid | `2610.23218/v1/src/main.tex:41, 89, 113, 294, 447, 449`; CHECK #7 | kb (s39_frontier) |
| s39.3 | 252 (§3.9) | "Relativistic Hills mechanism: ... arXiv:2610.13294" | 2610.13294 is a population model of Hills EMRIs in which the binary-MBH encounter is a semi-analytic three-body treatment in Newtonian dynamics; relativity enters only in the later EMRI inspiral (semi-relativistic fluxes, FEW trajectories). A Hills-channel rate and eccentricity study, not a relativistic treatment of the separation | `2610.13294/v1/src/main.tex:107, 295, 313, 317-324`; CHECK #29 | kb (s39_frontier) |
| s39.4 | 255 (§3.9) | "Relativistic SIDM collapse: arXiv:2601.17117, arXiv:2506.17641" | 2506.17641 computes no relativistic collapse: it applies the onset criterion of earlier work (one-dimensional central dispersion about 0.3c) to a gravothermal model and follows the seed by dark Bondi and baryonic accretion. Only 2601.17117 (spherical Misner-Sharp fluid with GR) is a relativistic collapse calculation | `2506.17641/v3/src/sidmacc.tex:53, 74, 133, 147-155`; `2601.17117/v2/src/SIDM_MS.tex:60-68`; CHECK #35, #36 | kb (s39_frontier) |

## 2. Statements that are right but imprecise, or carry a wrong label

| # | Brief line | What the brief says | What is right | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| s39.5 | 239 (§3.9) | heading "Developments in 2025–2026 and active groups" | Three of the 32 ids are from 2024: 2401.08530 (2024-01-16), 2402.02178 (2024-02-03), 2404.16270 (2024-04-25) | meta:2401.08530, meta:2402.02178, meta:2404.16270 (field `published`); CHECK #1 | kb (s39_frontier) |
| s39.6 | 243 (§3.9) | 2609.14218: "Black-hole formation in a matter-dominated era, full-NR particles" | 3+1 NR with two matter models: a dust fluid for most of the paper, and in the last section "the attempt to perform a particle-in-cell (PIC) simulation in full numerical relativity": particles on a regular lattice with per-particle masses, deposited with a cell-sized top-hat support; with particles the runs do not crash and the threshold is about an order of magnitude below the analytic estimate | `2609.14218/v1/src/MDPBH.tex:168-177, 242, 1006-1072, 1197`; CHECK #3 | kb (s39_frontier) |
| s39.7 | 246, 247, 250 (§3.9) | "Macpherson et al.", "Adamek et al.", "Launay, Rigopoulos, Shellard" as author attributions | Group labels, not author lists: 2603.24838 is by Macpherson alone, 2606.18437 by Nguyen, Blake, Macpherson; 2603.24179 by Magi, Lepori, Adamek; 2610.32592 is Launay's PhD thesis (single author), built from papers with Rigopoulos and Shellard | `2603.24838/v1/src/main.tex:30`; `2606.18437/v1/src/main.tex:26-28`; `2603.24179/v2/src/paper_framedragging.tex:167-169`; `2610.32592/v1/src/preword.tex:18, 67-92, 107`; CHECK #12, #14, #22 | kb (s39_frontier) |
| s39.8 | 247 (§3.9) | 2603.24179 under "Weak-field relativistic N-body" | Mainly second-order perturbation theory of weak lensing (Sachs-basis rotation, frame dragging), validated against a relativistic N-body simulation: a user of gevolution, not a code paper. 2508.20606 runs in gevolution's weak-field Poisson-gauge expansion | `2603.24179/v2/src/paper_framedragging.tex:189, 212, 1053-1056`; `2508.20606/v2/src/main.tex:247`; CHECK #15 | kb (s39_frontier) |
| s39.9 | 249 (§3.9) | 2607.06441 under "NR of initial conditions for inflation" | Spherically symmetric throughout, BSSN in spherical polar coordinates with a reference metric, asymptotically flat boundaries instead of periodic ones | `2607.06441/v1/src/main.tex:69, 120, 205, 362`; CHECK #20 | kb (s39_frontier) |
| s39.10 | 251 (§3.9) | 2506.11795 under "Lattice inflation and super-horizon freezing" | 2506.11795 works in the decoupling limit with an FLRW metric, the class of simulation that 2606.14853 finds does not freeze superhorizon modes; it is a lattice-USR reference (nonperturbative delta-N), not a study of freezing | `2506.11795/v2/src/main.tex:165, 244`; `2606.14853/v2/src/Manuscript.tex:122, 151-153`; CHECK #24, #26 | kb (s39_frontier) |
| s39.11 | 252 (§3.9) | 2404.16270, 2402.02178 under "Relativistic Hills mechanism" | Relativistic approximations, not full GR: the hybrid relativistic-Newtonian approximation (exact Schwarzschild acceleration, Newtonian binary self-gravity) against Newtonian and 1PN runs (2404.16270); a binary evolved in a frame freely falling past a Kerr SMBH, where the paper calls full NR intractable (2402.02178) | `2404.16270/v1/src/article.tex:123, 148-154`; `2402.02178/v1/src/main.tex:225-229, 293, 523`; CHECK #27, #28 | kb (s39_frontier) |
| s39.12 | 253 (§3.9) | 2511.20567 under "Full-GR ... extremal black holes" | Spherically symmetric Einstein-Maxwell-Vlasov (charged collisionless particles); beyond a critical point the threshold solution is an extremal black hole. Not 3D | `2511.20567/v2/src/main.tex:62-72, 117`; CHECK #31 | kb (s39_frontier) |

## 4. Statements superseded by a decision (not errors of fact)

| # | Brief line | What the brief says | What holds now | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| s39.13 | 246 (§3.9) | Macpherson et al.: "Benchmark and potential collaborators for S6" | Benchmark only: no session contacts anybody outside (decision 0017 item 3) | `coord/DECISIONS/0017-delegation.md` item 3; CHECK #38 | kb (s39_frontier) |
| s39.14 | 247, 248 (§3.9) | gevolution: "Comparison code in the weak-field regime"; GRTresna among the "Foundation of M1" | Neither code is run here (decision 0010): gevolution's published results are compared with (as row 4.5 already says for sheet B); GRTresna's formalism (CTTK) may be used, the initial-data solve lives in AthenaK (decision 0010 consequence 4) | `coord/DECISIONS/0010-one-code-base.md`; CHECK #39, #40 | kb (s39_frontier) |

No item of lines 239-256 was labelled [TO VERIFY], so section 3 has no rows from this
package. The frontier search (FRONTIER.md) adds no correction to the brief; it adds papers.
