# Check of brief lines 267-278 (section 3.11, Hills mechanism, tidal separation and strong-field three-body dynamics)

Owner kb, work package s311, 2026-11-19. Brief: `einstein_vlasov_pic_cosmology_agent_brief.en.md`
(version 2), section 3.11: the classic picture (line 269), restricted and full three-body work
(line 270), gravitational-wave channels (line 271), how far the relativistic treatment has gone
(line 272), related full numerical relativity and the novelty statement (line 273), the
cosmological connection (line 274) and the scale estimate (line 275). Lines 267, 276-278 hold a
heading, a blank line, a rule and the next heading: no statement. Every labelled statement of
lines 269-275, and every specific claim about a cited paper (also inside a [JUDGEMENT] item or
without a label), is checked at the TeX source in the knowledge-base store. Not checked: the
[JUDGEMENT] of line 274 that the two-peak case of S1 meeting a heavier third black hole is "the
early-universe version of the Hills process" (no literature claim).

Locators: `<key>/<version>/src/<file>:<line>` are lines of the TeX sources under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/` (astro-ph/0309084 as `astro-ph_0309084`, and so on);
the version is the newest in the store. `meta:arxiv-api/<id>` and `meta:inspire/<id>` are the
metadata files under `kb-data/meta/` written by `harness/bin/nrpic-fetch-arxiv`;
`meta:inspire/query/<sha16>` is a query answer of 2026-11-19. `<branch>:<path>:<lines>` is a file
of this repository on a branch (Track F's novelty package is on `track/F-hills`). Run ids:
`kb-...` are runs of this package (manifests in `tracks/kb/runs/`), `F-hills-...` are Track F's
(manifests on `track/F-hills` under `tracks/F-hills/runs/`). All 52 cited papers were already in
the store; nothing was fetched. Four INSPIRE queries were repeated (run
`kb-20261119-153345-ed7ee04`); numbers printed in the sources were recomputed in run
`kb-20261119-153659-4688c5b` (`scripts/check_numbers.py`, figure `fig_numbers.png`).

Not repeated here as a correction: line 275 is row 1.5 of `coord/BRIEF_ERRATA.md` (main) from
Track F's re-derivation (runs F-hills-20261115-045435-f62d553 and the lead's -144954-b5b0bce,
-145915-71abf93); rows 61-66 cite it.

Label column: the brief's label for the statement; "(unl.)" marks a specific claim about a
paper that carries no label. Line 269 is [BACKGROUND]; lines 270 and 271 are "[titles VERIFIED]";
line 272 is "[VERIFIED: abstracts or search snippets]"; the citations of line 273 carry no label
and its last sentence is [TO VERIFY]; line 274 is [JUDGEMENT]; line 275 is "[JUDGEMENT;
derivation to be checked]".

Verdicts: CONFIRMED (the source says it, at the locator), CONFIRMED (precision) (right, but the
source qualifies it in a way a reader should know; what in the note), CORRECTED (the source says
something else; what is right in the note), NOT FOUND (what was searched). Totals: 66 rows; 45
CONFIRMED, 18 CONFIRMED (precision), 3 CORRECTED, 0 NOT FOUND.

## Line 269: the classic picture [BACKGROUND]

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 269 | "Hills (1988, no arXiv version)" | [BACKGROUND] | CONFIRMED | `astro-ph_0309084/v1/src/ms.tex:1112`, `1201.4794/v1/src/ms.tex:1058` | Hills, J. G. 1988, Nature 331, 687; it predates arXiv. Not in the store and not read: the statements of rows 2-4 are checked at the papers that report Hills' results (0911.1136 calls its framework the one "in which Hills predicted the existence of HVSs", `0911.1136/v1/src/prp.tex:118-119`). |
| 2 | 269 | "a binary of mass m_b and separation a_b that passes a black hole of mass M on a near-parabolic orbit is pulled apart inside the tidal radius r_t ≈ a_b (M/m_b)^(1/3)" | [BACKGROUND] | CONFIRMED (precision) | `0911.1136/v1/src/prp.tex:86-88, 40, 46-47, 1081`, `astro-ph_0309084/v1/src/ms.tex:151-153, 500-515, 529-540`, `2404.16270/v1/src/article.tex:168-176, 180-182` | r_t = a (M/m)^(1/3) with m the binary mass. Separation inside r_t is likely, not certain: in Hills' runs exchange (one ejected, one bound) occurs in nearly 80 per cent of encounters at R'_min ≈ 0.3 and 50 per cent at R'_min ≈ 1 (R'_min = pericentre in units of a_b (M/m*)^(1/3), m* the mass of one of two equal members, i.e. of 2^(1/3) r_t); about 20 per cent of deeply penetrating (planar, circular) binaries survive; r_t is "only an order-of-magnitude estimate" and the outcome depends on the binary's phase and orientation. Hills' binaries came in on unbound orbits with v_inf, the results being independent of v_inf while it is small, which is the near-parabolic limit. |
| 3 | 269 | "one member is ejected with speed v_ej ~ v_b (M/m_b)^(1/6) ..., where v_b is the orbital speed of the binary" | [BACKGROUND] | CONFIRMED | `0911.1136/v1/src/prp.tex:89-90, 106-116`, `astro-ph_0309084/v1/src/ms.tex:516-526`; run `kb-20261119-153659-4688c5b` | v_0 = (G m/a)^(1/2), velocity at infinity v_0 (M/m)^(1/6) (at infinity from the black hole, before the Galactic potential). Hills' numbers as reported by Yu and Tremaine (v' = 130-160 km/s) give v_ej = k v_b q^(1/6) with k = 1.10 to 1.35 (run X1), and reproduce their 5e3 and 0.9e3 km/s (ratios 1.01-1.26, run X2). |
| 4 | 269 | "and the other is captured on a bound orbit of high eccentricity" | [BACKGROUND] | CONFIRMED (precision) | `0911.1136/v1/src/prp.tex:106-107, 40, 828`, `astro-ph_0309084/v1/src/ms.tex:674-677, 1030-1031`, `1201.4794/v1/src/ms.tex:43, 349` | Right. Which member is ejected is a coin toss for a disrupted equal-energy split: each body has a 50 per cent chance, also for unequal masses on a parabolic orbit (contrary to earlier claims). Ejection plus capture needs the binary's own orbit to be nearly parabolic, abs(1 - e) ≲ (m/M)^(1/3). |
| 5 | 269 | "Hypervelocity stars and S-stars at the Galactic centre: arXiv:astro-ph/0309084" | [BACKGROUND] | CONFIRMED | `astro-ph_0309084/v1/src/ms.tex:59, 70, 681-686` | Yu and Tremaine 2003: three ejection channels, among them Hills' tidal breakup; the bound companions as young S-stars. |
| 6 | 269 | same, arXiv:astro-ph/0501177 | [BACKGROUND] | CONFIRMED | `astro-ph_0501177/v1/src/wbrown.tex:5, 32, 57` | Brown et al. 2005: first unbound hypervelocity star, "as predicted by Hills". |
| 7 | 269 | same, arXiv:astro-ph/0608159 | [BACKGROUND] | CONFIRMED | `astro-ph_0608159/v1/src/ms.tex:38, 71` | Bromley et al. 2006: ejection-velocity spectrum from binary disruption. |
| 8 | 269 | same, arXiv:1105.1432 | [BACKGROUND] | CONFIRMED | `1105.1432/v1/src/HVS.tex:40, 62-69` | Zhang, Lu, Yu: spatial and velocity distributions of HVSs from three-body experiments (tidal breakup and binary-black-hole channels). |
| 9 | 269 | same, arXiv:1210.1901 | [BACKGROUND] | CONFIRMED | `1210.1901/v2/src/msGCSstar.tex:60, 74` | Zhang, Lu, Yu: S-stars and HVSs as products of the same tidal breakups. |
| 10 | 269 | same, arXiv:2002.10547 | [BACKGROUND] | CONFIRMED | `2002.10547/v2/src/hills.tex:42, 75` | Generozov and Madigan: the Hills mechanism and the S-stars. |

## Line 270: restricted and full three-body work ["titles VERIFIED"]

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 11 | 270 | "Restricted three-body problem and parameter scans: arXiv:0911.1136" | [titles VERIFIED] | CONFIRMED | `0911.1136/v1/src/prp.tex:19, 32-33, 135, 149` | Sari, Kobayashi, Rossi: restricted parabolic three-body problem, valid for (M/m)^(1/3) ≫ 1 (`:137-139`). |
| 12 | 270 | same, arXiv:1201.4794 | [titles VERIFIED] | CONFIRMED | `1201.4794/v1/src/ms.tex:17, 39, 111` | Kobayashi et al.: ejection and capture in restricted three-body encounters, non-parabolic orbits. |
| 13 | 270 | same, arXiv:1307.1134 | [titles VERIFIED] | CONFIRMED (precision) | `1307.1134/v3/src/msv3.tex:33, 51, 143` | Rossi, Kobayashi, Sari: an application (velocity distribution of HVSs after leaving the Galaxy, analytic plus Monte Carlo) built on the restricted method, not a new scan of the encounter. |
| 14 | 270 | same, arXiv:1804.02911 | [titles VERIFIED] | CONFIRMED | `1804.02911/v1/src/mnras.tex:24, 63, 135-137` | Brown et al.: parabolic and radial restricted approximations, inclined and eccentric binaries, fits of disruption probability and energy gain. |
| 15 | 270 | "Full three-body, stellar collisions and double tidal disruptions: arXiv:0909.1959" | [titles VERIFIED] | CONFIRMED (precision) | `0909.1959/v2/src/ms.tex:19, 41` | Antonini et al.: post-Newtonian N-body code, binaries on bound highly elliptical orbits followed for several revolutions (Kozai cycles, collisions and mergers), not single parabolic passages. |
| 16 | 270 | same, arXiv:astro-ph/0609440 | [titles VERIFIED] | CONFIRMED | `astro-ph_0609440/v2/src/Paper.tex:26, 45, 105` | Ginsburg and Loeb: direct N-body (Aarseth), collisions of the binary members. |
| 17 | 270 | same, arXiv:2409.09597 | [titles VERIFIED] | CONFIRMED (precision) | `2409.09597/v2/src/sample631.tex:24, 40, 75` | Yu and Lai: break-up, double disruptions and collisions, but with "restricted 3-body scattering experiments" (`:75`), so by method it belongs to the first group. |
| 18 | 270 | same, arXiv:1504.02787 | [titles VERIFIED] | CONFIRMED | `1504.02787/v2/src/tidal.tex:42, 53, 146` | Mandel and Levin: double tidal disruptions; three-body integrations (REBOUND), parabolic centre of mass. |
| 19 | 270 | same, arXiv:1703.05796 | [titles VERIFIED] | CONFIRMED (precision) | `1703.05796/v1/src/tidal_disruptions_paper.tex:72, 101, 134-136` | Bradnick, Mandel, Levin: in the empty loss cone most binaries (≳ 75 per cent) merge before they reach tidal separation, then the merger product is disrupted; near-periapsis REBOUND integrations with relaxation kicks in between. |
| 20 | 270 | "Repeating partial tidal disruptions: arXiv:2203.08162" | [titles VERIFIED] | CONFIRMED | `2203.08162/v1/src/main.tex:30, 44, 64` | Cufari, Coughlin, Nixon: Hills capture onto a 114-day orbit (ASASSN-14ko), analytic plus three-body integrations. |

## Line 271: gravitational-wave source channels ["titles VERIFIED"]

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 21 | 271 | "The captured member becomes an EMRI: arXiv:astro-ph/0507133" | [titles VERIFIED] | CONFIRMED | `astro-ph_0507133/v2/src/main.tex:20, 42-45` | Miller et al. 2005: tidal separation of compact binaries gives EMRIs with nearly zero eccentricity in the LISA band. |
| 22 | 271 | same, arXiv:2610.13294 | [titles VERIFIED] | CONFIRMED | `2610.13294/v1/src/main.tex:57, 106` | "Hills EMRIs": a black-hole binary tidally separated by a massive black hole. |
| 23 | 271 | "Compact binaries and massive black holes: arXiv:1501.07856" | [titles VERIFIED] | CONFIRMED | `1501.07856/v1/src/Busting_Up_Binaries.tex:66, 83-90` | Addison, Laguna, Larson: about 13 million encounters; bound member e ≈ 0.97; survivors harden. |
| 24 | 271 | same, arXiv:1801.05780 | [titles VERIFIED] | CONFIRMED | `1801.05780/v3/src/ms.tex:23, 49-54` | Chen and Han: binary EMRIs from tidal capture of a black-hole binary. |
| 25 | 271 | same, arXiv:1805.09593 | [titles VERIFIED] | CONFIRMED | `1805.09593/v3/src/revised_version.tex:71, 94` | Fernández and Kobayashi: mergers of binaries that survive a tidal encounter. |
| 26 | 271 | same, arXiv:1903.02685 | [titles VERIFIED] | CONFIRMED (precision) | `1903.02685/v2/src/gw_merger.tex:62, 80` | Zhang, Shao, Zhu: binaries bound in the nucleus (relaxation, binary-single encounters, Kozai-Lidov, close encounters with the MBH); a population model, not a passage. |
| 27 | 271 | same, arXiv:1203.2938 | [titles VERIFIED] | CONFIRMED (precision) | `1203.2938/v2/src/ms_apj.tex:20, 49-52` | Antonini and Perets: secular Kozai evolution of compact binaries bound to the SMBH (a hierarchical triple), not tidal separation. |
| 28 | 271 | same, arXiv:1706.09896 | [titles VERIFIED] | CONFIRMED (precision) | `1706.09896/v2/src/BHBinaries_v5.tex:36, 48, 71` | Hoang et al.: eccentric Kozai-Lidov mergers, secular (quadrupole and octupole) Monte Carlo; also a bound triple. |
| 29 | 271 | "Tests of general relativity with 'binary EMRIs': arXiv:1801.07060" | [titles VERIFIED] | CONFIRMED | `1801.07060/v5/src/mn_revision.tex:29, 63-64` | Han and Chen: merger of the inner binary seen as a glitch in the EMRI signal. |
| 30 | 271 | "Waveform effects for binaries near a massive black hole: arXiv:1703.10543" | [titles VERIFIED] | CONFIRMED | `1703.10543/v4/src/mn.tex:17, 47` | Chen, Li, Cao: Doppler and gravitational redshift for binaries merging within 10 Schwarzschild radii of a SMBH. |
| 31 | 271 | same, arXiv:2105.02230 | [titles VERIFIED] | CONFIRMED | `2105.02230/v2/src/ms.tex:68, 83` | Liu and Lai: frame dragging by the SMBH modulates the binary's orbital axis. |
| 32 | 271 | same, arXiv:1604.02148 | [titles VERIFIED] | CONFIRMED (precision) | `1604.02148/v2/src/main.tex:20, 26, 326, 344` | Meiron, Kocsis, Loeb: triple companions of merging binaries in general (stellar, intermediate and supermassive perturbers); the SMBH is one case. |
| 33 | 271 | same, arXiv:2310.00042 | [titles VERIFIED] | CONFIRMED (precision) | `2310.00042/v3/src/main.tex:38, 296, 437, 537` | Xuan et al.: millihertz bursts from wide eccentric stellar-mass binaries of several formation channels; one channel is binaries driven to high eccentricity by the SMBH (eccentric Kozai-Lidov). A burst signal, not a waveform effect of the SMBH's field. |
| 34 | 271 | same, arXiv:0704.2612 | [titles VERIFIED] | CORRECTED | `0704.2612/v2/src/ms.tex:59, 105, 158` | Not a binary. Yunes et al. treat extreme-mass-ratio bursts: one stellar-mass compact object on a nearly radial orbit about a massive black hole, with relativistic (geodesic) corrections to the burst waveform. It belongs to EMRI or burst waveforms, not to binaries near a massive black hole. |

## Line 272: how far the relativistic treatment has gone ["VERIFIED: abstracts or search snippets"]

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 35 | 272 | "(i) The exact relativistic acceleration of a Schwarzschild black hole combined with Newtonian self-gravity of the binary, compared with Newtonian and 1PN results (arXiv:2404.16270)" | [VERIFIED: abstracts] | CONFIRMED | `2404.16270/v1/src/article.tex:103, 123, 148`, `2404.16270/v1/src/appendix.tex:114-117` | Manzaneda, Navarrete, Tejeda: the Hybrid Relativistic-Newtonian Approximation of Tejeda et al. 2017 against Newtonian and 1PN N-body. |
| 36 | 272 | "the paper estimates that relativistic effects start to matter when the pericentre distance is below about 100 gravitational radii" | [VERIFIED: abstracts] | CONFIRMED (precision) | `2404.16270/v1/src/article.tex:194, 204, 123` | A rule of thumb quoted "in broad terms" from Tejeda et al. 2017, not the paper's own estimate; "relevant" means "order 1 percent or higher" (caption of Fig. 2). The paper's own results: in retrograde encounters up to 30 per cent more separations and an earlier onset (beta = 2 against 2.5). |
| 37 | 272 | "(ii) Dynamics and waveform of a binary black hole flying close to a Kerr black hole on a parabolic orbit (arXiv:2402.02178)" | [VERIFIED: abstracts] | CONFIRMED | `2402.02178/v1/src/main.tex:92, 112, 343-348` | Zhang and Chen: parabolic outer orbit of arbitrary inclination, tidal treatment in a frame freely falling with the binary. |
| 38 | 272 | "the paper says the dynamical range of such systems is too large for a direct full-NR solution and stresses the need for new numerical tools" | [VERIFIED: abstracts] | CONFIRMED | `2402.02178/v1/src/main.tex:222-226, 123` | "the outer orbit is typically 10^4 times bigger than the size of the inner binary ... intractable to solve the problem by full numerical relativity"; "highlight the necessity of building new numerical tools". |
| 39 | 272 | "(iii) Perturbative treatment: arXiv:1203.6185" | [VERIFIED: abstracts] | CONFIRMED | `1203.6185/v1/src/bbbhPRD.tex:8, 41, 144, 190-193`; `meta:inspire/1203.6185` | A binary black hole in the potential of a third, "instead of simulating the three-BH problem with a fully relativistic treatment". The journal record (J. Phys. Conf. Ser. 330, 012016) carries a second title, "From binary black hole simulation to triple black hole simulation", with Bai first; 2402.02178 cites it under that title (`2402.02178/v1/src/biblio.bib:22-34`). |
| 40 | 272 | "(iv) Members with internal structure: SPH simulations of white-dwarf binaries tidally disrupted by intermediate-mass black holes, including spin (arXiv:2508.03463, ...)" | [VERIFIED: abstracts] | CONFIRMED (precision) | `2508.03463/v2/src/Binary.tex:19, 41, 168, 270-283` | Non-spinning black hole: Schwarzschild geodesics with Newtonian hydrodynamics and self-gravity. Spin enters only in the companion paper (row 41). Neither evolves the spacetime. |
| 41 | 272 | same, arXiv:2601.04870 | [VERIFIED: abstracts] | CONFIRMED | `2601.04870/v2/src/Binary_kerr_Final.tex:26, 52, 411` | Kerr geodesics plus Newtonian hydrodynamics and self-gravity; spin of the black hole and inclination of the binary. |
| 42 | 272 | "relativistic kicks and spin effects in the tidal disruption of single stars (arXiv:1502.02039, ...)" | [VERIFIED: abstracts] | CONFIRMED | `1502.02039/v2/src/paper.tex:10, 44, 102` | Gafton et al.: kicks of partially disrupted stars in a generalized potential that reproduces Schwarzschild. |
| 43 | 272 | same, arXiv:1305.4634 | [VERIFIED: abstracts] | CONFIRMED (precision) | `1305.4634/v2/src/ms.tex:67, 69, 82, 86` | Manukian et al.: kicks of solitary stars from partial disruptions in Newtonian hydrodynamics (the word "relativ" does not occur in the source); the Newtonian baseline that 1502.02039 extends. |
| 44 | 272 | same, arXiv:1411.5022 | [VERIFIED: abstracts] | CORRECTED | `1411.5022/v2/src/shs.tex:33, 40-43, 51` | Not a single-star disruption. Guillochon and Loeb: stars bound to the secondary of a massive-black-hole binary are ejected at up to about 1e5 km/s ("semi-relativistic hypervelocity stars"), the Hills mechanism with a massive black hole as the second body. It belongs with the hypervelocity-star papers of line 269. |
| 45 | 272 | same, arXiv:1701.00303 | [VERIFIED: abstracts] | CONFIRMED | `1701.00303/v2/src/article.tex:75-76, 95` | Tejeda et al.: relativistic hydrodynamics of a test fluid in Kerr with Newtonian self-gravity; spin effects on the debris. |
| 46 | 272 | same, arXiv:1903.09147 | [VERIFIED: abstracts] | CONFIRMED | `1903.09147/v2/src/paper.tex:38, 62` | Gafton and Rosswog: spin and impact parameter. |
| 47 | 272 | same, arXiv:1207.6401 | [VERIFIED: abstracts] | CONFIRMED (precision) | `1207.6401/v2/src/Aug16.tex:12, 31-32, 154` | Kesden: spin dependence of the fallback rate with the debris on Kerr geodesics; no hydrodynamics. |

## Line 273: related full numerical relativity and the novelty statement

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 48 | 273 | "Evolutions of three or more black holes: arXiv:0710.0879" | (unl.) | CONFIRMED | `0710.0879/v2/src/first.tex:28, 53-54` | Campanelli, Lousto, Zlochower: first long-term evolutions of three equal-mass black holes. |
| 49 | 273 | same, arXiv:0711.1165 | (unl.) | CONFIRMED | `0711.1165/v2/src/second.tex:28, 53-56` | Lousto and Zlochower: third hole approaching a binary; prompt merger, elliptic binary, or disruption into three free holes (equal masses). |
| 50 | 273 | same, arXiv:1004.1353 | (unl.) | CONFIRMED | `1004.1353/v2/src/Punc_N.tex:58, 177, 210` | Galaviz, Bruegmann, Cao: three and four equal-mass holes with solved initial data. |
| 51 | 273 | "a cluster of 25 black holes: arXiv:2505.01495" | (unl.) | CONFIRMED | `2505.01495/v2/src/apssamp.tex:76, 107-109` | Bamber et al.: 25 equal-mass nonspinning holes, R/M ≈ 10, full GR. |
| 52 | 273 | "Stellar tidal disruption in full GR: arXiv:1201.4389" | (unl.) | CONFIRMED | `1201.4389/v1/src/paper.tex:19, 190-191, 1583-1584` | Haas et al.: white dwarfs and spinning intermediate-mass holes; Einstein equations (BSSNOK, moving punctures) with hydrodynamics. |
| 53 | 273 | same, arXiv:1502.05740 | (unl.) | CONFIRMED | `1502.05740/v2/src/ms.tex:36, 51, 167` | Evans, Laguna, Eracleous: solar-type stars and intermediate-mass holes, Maya code (Einstein equations, fourth order). |
| 54 | 273 | same, arXiv:1408.1695 | (unl.) | CONFIRMED (precision) | `1408.1695/v2/src/main.tex:31, 99, 120-125, 208-213` | East: full GR with hydrodynamics, but mostly head-on collisions of stars with black holes at mass ratios 1.25e5 to 1e6, made affordable by subtracting the truncation error of the black-hole background; the subject is the gravitational waves of the collision. |
| 55 | 273 | "A Hills-type full-NR calculation of 'binary + massive black hole' was not found" | [TO VERIFY] | CONFIRMED (precision) | `track/F-hills:tracks/F-hills/novelty/NOVELTY.md:9-29, 35-65, 137-146`; `2406.11985/v1/src/TBH3.tex:582-597`; `2406.11985/v1/src/massratio_table.tex:3, 21, 28, 30`; `2505.03934/v2/src/apssamp.tex:110, 464-465`; `meta:inspire/query/9016c78742b1a3b7`, `/query/152b0ae13c79f8c7`, `/query/83ada7349ec463b7`, `/query/d1c89deb2a285952`; run `kb-20261119-153345-ed7ee04` | Not found by Track F's search of 2026-11-15, and the four key queries repeated on 2026-11-19 return the same records (citations of 2406.11985: 9; of 2505.03934: 8; Hills/tidal-separation titles: 22; three-black-hole titles: 19). Precision: full-NR evolutions of a binary with a heavier third hole do exist, 2406.11985 with masses 8:1:1 and 18:1:1 (q = 4 and 9; binary separation d = 1.98 and 0.99 M, third hole at D = 12.9 and 12.0 M on a bound quasi-circular orbit), but the binary is not separated; a binary is broken up in full NR by an equal-mass third hole (0711.1165) and, with exchange and ejection, by a single hole lighter than the binary (2505.03934, all holes equal). The statement holds for a heavier perturber on a near-parabolic orbit with pericentre near r_t. |
| 56 | 273 | "nor a version whose members are self-gravitating collisionless clumps" | [TO VERIFY] | CONFIRMED | `track/F-hills:tracks/F-hills/novelty/NOVELTY.md:28-29, 110-115, 127-133` | No full-GR calculation of any matter binary (fluid or collisionless) passing a black hole was found: the relativistic matter-binary work uses geodesics or a fixed metric with Newtonian self-gravity (rows 40-41); the NRPIC source paper has no third body. |

## Line 274: the cosmological connection [JUDGEMENT], claims about the cited papers

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 57 | 274 | "The formation of primordial-black-hole binaries and their history of perturbation by third bodies determine the merger rate (arXiv:1812.01930, ...)" | [JUDGEMENT] | CONFIRMED | `1812.01930/v3/src/PBHmergers.tex:48, 65` | Raidal et al.: N-body simulations; most initial binaries are disrupted by the surrounding PBHs when PBHs are all of the dark matter, so the tidally perturbed two-body estimate overestimates the rate. |
| 58 | 274 | same, arXiv:1908.09752 | [JUDGEMENT] | CONFIRMED | `1908.09752/v3/src/PBBH3.tex:42, 54, 64-66` | Vaskonen and Veermäe: lower bound on the rate from the maximal fraction of perturbed binaries. |
| 59 | 274 | same, arXiv:2006.11172 | [JUDGEMENT] | CONFIRMED | `2006.11172/v2/src/paperv3.tex:225-233` | Jedamzik: three-body interactions with a by-passing PBH in early clusters, by full numerical integration, lower the predicted rates by orders of magnitude. |
| 60 | 274 | "for primordial-black-hole binaries with dark-matter dresses see arXiv:1805.09034" | [JUDGEMENT] | CONFIRMED | `1805.09034/v3/src/main.tex:27, 41` | Kavanagh, Gaggero, Bertone: merger of dressed PBH binaries and its (small) effect on the merger rate. |

## Line 275: scale estimate [JUDGEMENT; derivation to be checked] (re-derived by Track F; correction already in errata row 1.5)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 61 | 275 | "r_t/r_g = (a_b/r_gb)·q^(−2/3), with q = M/m_b and r_gb = G m_b/c²" | [JUDGEMENT] | CONFIRMED | `track/F-hills:tracks/F-hills/novelty/scope/SCOPE.md:75`; run `F-hills-20261115-045435-f62d553`; `2404.16270/v1/src/article.tex:168-176`; run `kb-20261119-153659-4688c5b` | Follows from r_t = a_b q^(1/3) (Track F, difference 4e-15). Independently: the formula gives 2404.16270's own r_t = 101.3 r_g (M = 1e6 Msun, m_b = 1 Msun, a_0 = 0.01 au) to 1e-4 (run X3). |
| 62 | 275 | "A parabolic orbit in Schwarzschild with pericentre below 4 r_g plunges into the black hole" | [JUDGEMENT] | CONFIRMED | `2404.16270/v1/src/article.tex:204, 209-210`; `track/F-hills:tracks/F-hills/novelty/scope/SCOPE.md:76-80`; run `F-hills-20261115-045435-f62d553` | The marginally bound circular orbit, 4 r_g ("limit of direct capture"); Track F's root r_mb = 4.000000 M. |
| 63 | 275 | "so separation before the plunge requires a_b/r_gb ≳ 4 q^(2/3): about 19 for q=10, about 86 for q=100, about 400 for q=1000" | [JUDGEMENT] | CONFIRMED | `track/F-hills:tracks/F-hills/novelty/scope/SCOPE.md:76-85`; run `F-hills-20261115-045435-f62d553`; `2404.16270/v1/src/article.tex:209-212`; run `kb-20261119-153659-4688c5b`; `main:coord/BRIEF_ERRATA.md:31` | 18.57, 86.18, 400.0 (Track F). The same bound written as beta_max = r_t/(4 r_g) reproduces 2404.16270's beta_max = 25.3 to 0.1 per cent (run X3). Order-of-magnitude criterion (no exact prefactor in r_t). |
| 64 | 275 | "For compact binaries, full NR can reach q≈10–30 and a_b≈20–60 r_gb: the separation happens at a few r_g, and every pair of the three bodies is in the strong field" | [JUDGEMENT] | CORRECTED (errata 1.5, not repeated) | `main:coord/BRIEF_ERRATA.md:31`; `track/F-hills:tracks/F-hills/novelty/scope/SCOPE.md:86-90` | Already corrected: part of the box lies below the plunge bound (separation needs a_b ≥ 29.5 r_gb at q = 20 and 38.6 at q = 30), and the bound holds for the centre of mass only. |
| 65 | 275 | "The gravitational-wave merger time of an equal-mass binary is, by the Peters formula, (5/64)(a_b/r_gb)⁴ G m_b/c³; for a_b=30 r_gb and q=10 this is about 6×10³ GM/c³" | [JUDGEMENT] | CONFIRMED | `1805.09593/v3/src/revised_version.tex:128, 202-205`; run `kb-20261119-153659-4688c5b`; `track/F-hills:tracks/F-hills/novelty/scope/SCOPE.md:91-92`; run `F-hills-20261115-045435-f62d553` | Peters (1964, not on arXiv) as quoted by 1805.09593: (5/256) c^5 a^4/(G^3 m1 m2 m), which is exactly 5/64 for equal masses; the transcription reproduces their 6.0e3 Gyr (m = 60 Msun, a = 1 au) to 0.9 per cent (run X4). 6328 GM/c^3 at a_b = 30, q = 10 (Track F; run X4). |
| 66 | 275 | "far longer than the few hundred GM/c³ of one passage, so the binary survives until the encounter" | [JUDGEMENT] | CONFIRMED (precision) | `track/F-hills:tracks/F-hills/novelty/scope/SCOPE.md:93-97`; run `F-hills-20261115-045435-f62d553` | Schwarzschild parabolic coordinate time in and out from r0 = 3, 4, 5 r_t to r_p = 6 r_g: 163, 223, 285 GM/c^3 (q = 10, a_b = 30); Peters time / passage = 28. Holds for starts within about 5 r_t; the binary turns about twice during the passage (period 103 GM/c^3). |
