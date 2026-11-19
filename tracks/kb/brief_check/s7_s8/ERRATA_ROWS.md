# Rows for `coord/BRIEF_ERRATA.md` from work package s7_s8 (brief lines 554-625)

Owner kb (helper of the brief check, wave 3a), 2026-11-19. Format of `coord/BRIEF_ERRATA.md`
on main (sections 2, 3 and 5, same columns; a last section proposes updates of the open
questions, which are not errata and are for the orchestrator to place). Row numbers `s78.n` are
provisional; the orchestrator numbers them when it merges. None of these statements is already
in `coord/BRIEF_ERRATA.md` (it has no row on lines 554-625; its row 1.4 on the constraints of
arXiv:2512.14649 bears on candidate U11 and is not repeated). Paper locators
`<key>/<v>/src/<file>:<line>` are lines of the TeX sources under `kb-data/raw/arxiv/`;
`meta:inspire/query/<sha16>` are stored INSPIRE answers under `kb-data/meta/inspire/query/`. The
full check (42 statement rows: 19 confirmed, 22 confirmed with a precision, 1 corrected; the
status of the 26 questions and 12 candidates) is `tracks/kb/brief_check/s7_s8/CHECK.md` (branch
`kb/brief-check`), whose row numbers are given as "CHECK #". The tally and every locator of
CHECK.md were checked by a registered run (see `README.md` of the package); the sign statement
of row s78.2 by run kb-20261119-154153-47eb61f.

No statement of these lines was found wrong. Section 1 therefore has no row.

## 2. Statements that are right but imprecise, or carry a wrong label

| # | Brief line | What the brief says | What is right | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| s78.1 | 604 (§8, U1) | "the Newtonian limit is known to have Jeans-type, radial-orbit and two-stream instabilities among others" [BACKGROUND] | Right; can carry [VERIFIED] with locators in the store | `1206.6152/v1/src/vlasov_code.tex:562-567` (Jeans); `1907.08129/v1/src/ms.tex:818` (radial orbit); `1801.03507/v2/src/ms.tex:1336-1346`, `2110.06265/v2/src/cosmo-vlasov.tex:955` (two-stream); CHECK #31 | kb (s7_s8) |
| s78.2 | 604 (§8, U1) | "the gravitomagnetic interaction between co-moving mass currents is repulsive, opposite in sign to electromagnetism" [BACKGROUND] | Right, and can carry [VERIFIED] with a derivation: in linearized GR (harmonic gauge) the h_0x part of the transverse acceleration of a test mass moving with w beside a mass M moving with V is +4 gamma^2 V w M/b^2 (repulsive when V w > 0), the magnetic force between like charges -gamma V w qQ/b^2 (attractive). Two qualifications a reader needs: the net force between co-moving masses stays attractive, -M/(gamma^2 b^2); for counter-streaming matter the h_0x part attracts. The split into parts is gauge dependent | run kb-20261119-154153-47eb61f (symbolic, and finite-difference Christoffel symbols of the full metric agreeing to 1.2e-6; figure `fig_gem_sign.png` in its output directory); CHECK #32 | kb (s7_s8) |
| s78.3 | 558 (§7, Q1) | "Which slicing and shift conditions carry pressureless matter stably through caustics ...? (arXiv:2610.23218, arXiv:2608.13206)" | 2608.13206 is a radiation-era paper (a fluid with pressure); it is cited for its gauge, a cosmologically scaled Gamma-driver allowing a step proportional to the scale factor, and it points to an e-folding lapse for the matter-dominated case. 2610.23218 is a dust fluid (no particles): Gamma-driver failure at shell focusing, a new lapse, black hole approached but not stably reached | `2608.13206/v3/src/PRD.tex:39, 56, 338`; `2610.23218/v1/src/main.tex:41, 51, 447-449`; CHECK #1, #2 | kb (s7_s8) |
| s78.4 | 560 (§7, Q3) | three settings including an "asymptotically FLRW boundary" (arXiv:2508.20606) | 2508.20606 embeds a curved FLRW cap in a flat FLRW exterior inside a periodic box; it is not an evolution with an asymptotically FLRW outer boundary | `2508.20606/v2/src/main.tex:54-58`; CHECK #6 | kb (s7_s8) |
| s78.5 | 583 (§7, Q20) | "Existing results cover the Milne model (arXiv:1709.00267) and cases with symmetry or a cosmological constant" | True of 2017 (the Milne background is a vacuum solution; earlier results needed Lambda > 0, T^3 Gowdy symmetry with Lambda > 0, 2+1 dimensions or massless particles), out of date since 2026: nonlinear stability of Einstein-de Sitter asymptotics for Einstein-Euler with a polytropic equation of state (n > 3) on T^3 (row s78.8) | `1709.00267/v1/src/main.tex:381, 390-394`; `2607.09326/v1/src/main.tex:141, 307`; CHECK #21 | kb (s7_s8) |
| s78.6 | 606 (§8, U3) | "If rotating collisionless collapse has a structure similar to that of arXiv:2402.10190" | 2402.10190 is spherically symmetric charged Vlasov (Einstein-Maxwell-Vlasov) with extremal Reissner-Nordstrom at the threshold; extremal Kerr at the threshold is its authors' conjecture for vacuum. Since then: the extremal threshold found numerically in Einstein-Maxwell-Vlasov, with rotating matter named as a route (arXiv:2511.20567), and gluing to extremal Kerr horizons proved in vacuum (arXiv:2610.35836) | `2402.10190/v1/src/main.tex:166, 192, 237, 405-414`; `meta:arxiv-api/2511.20567`; `meta:arxiv-api/2610.35836`; CHECK #35, part C U3 | kb (s7_s8) |
| s78.7 | 608 (§8, U5) | "If the other branch of solutions pointed out by arXiv:2509.26470 can be evolved" | It has been, in spherical symmetry: 2509.26470 identifies the "type II" data of Uehara et al. 2025 (PBH formation from a type II perturbation, with and without pressure) as strong-branch data | `2509.26470/v2/src/main_PRD.tex:253`; `2509.26470/v2/src/main_PRD.bbl:454-459`; CHECK #37 | kb (s7_s8) |

## 3. Items the brief left [TO VERIFY], now answered

| # | Brief line | What the brief leaves open | Answer | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| s78.8 | 583 (§7, Q20) | "the case of an Einstein–de Sitter-type background is [TO VERIFY]" | Answered for fluids, open for Vlasov. For dust, Einstein-de Sitter is linearly unstable (the growth that forms structure). For Einstein-Euler with a polytropic equation of state of index n > 3 on T^3 there is "an open family of nonlinearly stable solutions" with Einstein-de Sitter asymptotics, "the first nonlinear stability result for a physically realistic matter-dominated cosmological spacetime" (Bernhardt, Fajman, Wyatt 2026); Gowdy-symmetric numerics agree (Fajman, Marshall 2026). Massless Vlasov: the decelerating FLRW family is stable to spherically symmetric perturbations on R^3 (Taylor 2023). Massive Vlasov near Einstein-de Sitter: no result found; Landau damping on expanding backgrounds is proved for repulsive (plasma) Vlasov-Poisson only. For cold matter the question is the instability itself, so it is meaningful only with velocity dispersion | `2607.09326/v1/src/main.tex:141, 307, 309-311, 317`; `2606.16879/v1/src/main_v2.tex:43, 56-61`; `2306.17774/v1/src/masslessVlasovFLRW.tex:49`; `2604.14911/v1/src/Landau-electro.tex:146, 257`; searches `meta:inspire/query/2ad127a6360ac3bf`, `meta:inspire/query/5d79da858c8bc1b1`, `meta:inspire/query/38225ca010ad309d`; CHECK #22, part B Q20 | kb (s7_s8) |

## 5. Defects in sources the brief cites or that answer it (for the knowledge base; not errors of the brief)

| Source and locator | Defect | Evidence | Found by, sent to |
|---|---|---|---|
| arXiv:2607.09326 `main.tex:96` (abstract) against `:141`, `:299-300` | The abstract says every near-flat data set converges "under the Einstein-Euler flow with a polytropic equation of state"; the theorem holds for polytropic index n > 3 only (L141), and the authors conjecture instability for 0 < n < 3 (L300). A reader of the abstract alone would over-read it | read at the source | kb (s7_s8), for the claims layer |

## Proposed updates of the open questions (section 7; not errata, for the orchestrator to place)

Status on 2026-11-19 from CHECK.md part B (26 questions: 0 answered, 16 partly answered, 10
open). Only the questions where work exists that the brief does not name are listed.

| Question (brief line) | Status | What is new | Locator |
|---|---|---|---|
| Q1 (558) | PARTLY ANSWERED | Particles in an early matter era evolve through crossing and form horizons, with "a big caveat" on constraints after crossing (arXiv:2609.14218); prolate collapse through caustics into a black hole in moving-puncture gauge (2611.12831) | `2609.14218/v1/src/MDPBH.tex:177, 1148`; `2611.12831/v1/src/main.tex:975` |
| Q7 (567) | PARTLY ANSWERED | The source paper reports initial and late Hamiltonian and momentum violations scaling as N^-1/2 at fixed mesh, controlled by particles per cell; spurious GWs not quantified | `2611.12831/v1/src/main.tex:1129, 1476, 1509-1511` |
| Q8 (568) | PARTLY ANSWERED | Dust is a singular case of Vlasov matter (2305.04360); a trapped surface forms before any singularity for Vlasov data close to Oppenheimer-Snyder dust (arXiv:2410.06701, proof); linear Vlasov perturbation theory beyond dust (arXiv:2610.25145) | `2305.04360/v1/src/cc_hoop_conj.tex:99-100, 185`; `meta:arxiv-api/2410.06701`; `meta:arxiv-api/2610.25145` |
| Q11 (574) | PARTLY ANSWERED | Threshold for triaxial data with particles an order of magnitude below the analytic estimate (2609.14218); spin only from analytic models | `2609.14218/v1/src/MDPBH.tex:177, 1211-1215` |
| Q12 (575) | PARTLY ANSWERED | Newtonian N-body plus lattice: agreement with the perturbative peak, considerable enhancement at smaller scales; a relativistic treatment called for at high frequency (arXiv:2312.12499; inflaton halos arXiv:2212.00425) | `2312.12499/v2/src/main.tex:109, 209, 251` |
| Q14 (577) | PARTLY ANSWERED | Spherical GR (Misner-Sharp) nonequilibrium collapse gives a seed of about 3e-8 of the halo mass (arXiv:2601.17117) | `2601.17117/v2/src/SIDM_MS.tex:66-70` |
| Q19 (582) | PARTLY ANSWERED | Direct direction proved in U(1) symmetry (1907.10743) and in generalized wave coordinates (Huneau-Luk, arXiv:2403.03470, not in the store); reverse direction without symmetry for finitely many null dusts (arXiv:2402.17530); Vlasov limits only in U(1) symmetry | `1907.10743/v2/src/main.tex:87`; `2506.21779/v1/src/dustvlasov.250626.tex:124, 394`; `2402.17530/v2/src/superposition_final_AOPDES_first_revision_bis.tex:147` |
| Q20 (583) | PARTLY ANSWERED | Row s78.8 | as there |
| Q22 (588) | PARTLY ANSWERED | Shear-free lattice bridging stochastic inflation and delta N (arXiv:2604.00978); USR lattice with nonperturbative zeta (arXiv:2506.11795); the NR comparison is announced in 2512.14649, not done | `2604.00978/v3/src/main.tex:158`; `2506.11795/v2/src/main.tex:87`; `2512.14649/v2/src/PRD_v2.tex:536` |
| Q23 (589) | PARTLY ANSWERED | Done in the Newtonian limit: the fragmenting inflaton condensate followed with N-body particles (arXiv:2011.13333, 2110.15109); the relativistic hand-over not found | `2011.13333/v2/src/inflaton_halos_v2.tex:52, 69`; `2110.15109/v2/src/inflaton_stars.tex:86` |
