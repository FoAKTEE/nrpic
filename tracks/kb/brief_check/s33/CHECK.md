# Check of brief lines 164-185 (section 3.3, late universe)

Owner kb, work package s33, 2026-11-19. Brief: `einstein_vlasov_pic_cosmology_agent_brief.en.md`
(version 2), section 3.3 "Late universe: structure formation, backreaction, light-cone
observables". Every statement of these lines with a label, and every specific claim about a
cited paper (also where it carries no label), is checked at the TeX source in the
knowledge-base store; nothing here rests on an abstract page alone.

Locators: `<key>/<version>/src/<file>:<line>` are lines of the TeX sources under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/` (gr-qc/0702082 as `gr-qc_0702082`); the version
checked is the newest in the store. `meta:arxiv-api/<id>` and `meta:inspire/<id>` are the
metadata files `kb-data/meta/arxiv-api/<id>.json` and `kb-data/meta/inspire/<id>.json` written
by `harness/bin/nrpic-fetch-arxiv`. All 53 cited papers were already in the store; nothing was
fetched. Nothing here repeats a row of `coord/BRIEF_ERRATA.md` (none of its rows is on lines
164-185); row 12 is the same finding as row s31.2 of package s31_32 (brief line 149), made
here for line 168.

Label column: the brief's label for the statement; "(unl.)" marks a specific claim about a
paper that carries no label. Statements that are the brief author's [JUDGEMENT] are listed at
the end and not given a verdict.

Verdicts: CONFIRMED (the source says it, at the locator), CONFIRMED (precision) (right, but the
source qualifies it in a way a reader should know; what in the note), CORRECTED (the source
says something else or the statement omits what reverses its reading; what is right in the
note), NOT FOUND (what was searched). Totals: 53 rows; 38 CONFIRMED, 13 CONFIRMED (precision),
2 CORRECTED, 0 NOT FOUND.

## Line 166: what full-NR fluid simulations found

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 166 | "In 2016 three groups independently produced the first full-NR cosmological simulations without symmetry (arXiv:1511.01105, arXiv:1511.05124, arXiv:1611.05447)" | (unl.) | CONFIRMED (precision) | `1511.01105/v3/src/cgraphprl_shorter.tex:37, 59`; `1511.05124/v3/src/dustQ.tex:55, 110`; `1611.05447/v2/src/inca_2016a.tex:148-151`; `meta:inspire/1511.01105`, `/1511.05124`, `/1611.05447` | The two "first" papers are 1511.01105 (BSSN, synchronous gauge: "the first numerical cosmological study that is fully relativistic, non-linear and without symmetry", L37) and 1511.05124 (dust, "no continuous symmetries", L110): posted November 2015, published back to back in Phys. Rev. Lett. 116, 251301 and 251302 (2016). 1611.05447 was posted in November 2016 and published in Phys. Rev. D 95, 064028 (2017); it is a feasibility study that builds on the other two ("Simulations free of these symmetries have only emerged within the last year", "Our approach is similar to", L148-151), not an independent first. |
| 2 | 166 | "Simulations evolved from CMB initial conditions to today" (arXiv:1807.01711) | [VERIFIED] | CONFIRMED | `1807.01711/v2/src/INCAPRD2019.tex:106, 221, 426` | "Simulations are initiated at z=1100 and evolve to z=0" (L221); initial conditions "drawn from the CMB" (L150, L588). Pressureless fluid in a matter-dominated (Einstein-de Sitter) model, not particles (L144, L608). |
| 3 | 166 | "give a global backreaction energy density of about 10⁻⁸ of the matter energy density (arXiv:1807.01711)" | [VERIFIED] | CONFIRMED (precision) | `1807.01711/v2/src/INCAPRD2019.tex:106` (abstract); `:524, :644` (body); `:458`; `:610, :630`; `:878-880` | The 10⁻⁸ is the abstract's (L106, "Although our results are preliminary"). The body gives, globally at z = 0, Omega_R ≈ 10⁻⁸ for the curvature and Omega_Q + Omega_L ≈ 10⁻⁹ for the backreaction terms (L524, L644; Omega_Q + Omega_L is "the energy density associated with the backreaction terms", L458): the backreaction proper is an order of magnitude below the abstract's number, which matches the curvature parameter. Both "in our chosen gauge" (L610, L630: the result depends on the averaging hypersurface); scales below 100-150 Mpc are not converged, so curvature and backreaction are underestimated (L878-880). |
| 4 | 166 | "Averaged on hypersurfaces of a Newtonian-like gauge, backreaction is negligible on small scales as well" (arXiv:2408.03049) | [VERIFIED] | CONFIRMED | `2408.03049/v1/src/main.tex:30, 38, 235, 485, 539` | "only negligible cosmic backreaction on these hypersurfaces even on very small scales" (L38); Omega_Q at most of order 10⁻⁹ for spheres of radius 20 h⁻¹ Mpc (L485). The hypersurfaces are those of the Einstein Toolkit run, in Newtonian gauge initially and while the perturbations stay linear (L235). The authors add that this does not show backreaction is negligible in the real universe (L543) and that their EdS results are upper bounds relative to LambdaCDM (L533). |
| 5 | 166 | "in sub-volumes of radius about 200 Mpc the curvature parameter can fluctuate by about 10%" (arXiv:2408.03049) | [VERIFIED] | CONFIRMED (precision) | `2408.03049/v1/src/main.tex:38, 485, 216` | "up to 10%" in Omega_R for spheres of r_D ~ 200 Mpc (L38, L485): the extreme over 1000 spheres, not a typical value ("about 10%"). Model: linearly perturbed Einstein-de Sitter fluid, h = 0.45 (L216). |
| 6 | 166 | "fluid flowing in and out changes the density by up to about 5% between z=1 and 0" (arXiv:2408.03049) | [VERIFIED] | CONFIRMED | `2408.03049/v1/src/main.tex:38, 496` | "up to a 5% change in the density between redshift z=1 and z=0 of a single sphere of radius ~200 Mpc (and larger for smaller spheres)" (L38, abstract); the body attributes the change to the flux term C_q (L496) and shows it in figures, without restating the number. |

## Line 168: from fluid to particles

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 7 | 168 | "The fluid description fails once multi-stream regions appear, and multi-stream regions are a generic feature of structure formation (introduction of arXiv:1908.05683)" | [VERIFIED] | CONFIRMED | `1908.05683/v2/src/main.tex:150-151` | "such fluid descriptions break down as soon as multistream regions emerge, which of course are generic features of structure formation". |
| 8 | 168 | "East et al. compared full Einstein–Vlasov solutions with Newtonian N-body particle by particle" | [VERIFIED] | CONFIRMED (precision) | `1908.05683/v2/src/main.tex:164-167, 292-296, 326-333, 429-433, 468-472`; `2409.01939/v2/src/LRCosmo.tex:1068` | The comparison is along the worldlines of a set of tracers: fiducial observers comoving with the matter and freely falling test particles (tracked in Newtonian runs through the tetrahedral cells of the dark-matter particles, L292-296), with consistent initial conditions from the Newtonian-relativistic dictionary (L164-167). Not every N-body particle is compared. |
| 9 | 168 | "the Living Review summarizes this body of work as follows: as long as the Newtonian potential stays in the weak-field range, the two differ at the sub-percent level (arXiv:2409.01939)" | [VERIFIED] | CONFIRMED (precision) | `2409.01939/v2/src/LRCosmo.tex:1038, 1068, 1106`; `meta:inspire/2409.01939` | "the Einstein-Vlasov formalism agrees with the Poisson-Vlasov formalism up to sub-percent level, as long as the Newtonian potential does not exceed the weak-field approximation abs(Psi_N) ≤ 0.1" (L1068); the same for the earlier fluid comparison (L1038). Published as Living Rev. Rel. 28 (2025) 5 (INSPIRE record; "this Living Review", L1106). The review adds that for non-linear collapse the Newtonian overdensities collapse faster (L1068), as 1908.05683 says (L176-178). |
| 10 | 168 | "Giblin et al. ran N-body + BSSN in harmonic and Newtonian gauges" (arXiv:1810.05203) | [VERIFIED] | CONFIRMED | `1810.05203/v1/src/grnbody.tex:182, 266` | BSSNOK formulation (L182); "an N-body system in harmonic and Newtonian gauges, and a perfect fluid in comoving-synchronous gauge" (L266). |
| 11 | 168 | "and reported very poor N-body convergence in comoving synchronous gauge" (arXiv:1810.05203) | [VERIFIED] | CONFIRMED | `1810.05203/v1/src/grnbody.tex:287-294, 134-140` | "In comoving synchronous gauge, we find poor convergence of simulations when using an N-body system" (particles do not move; deposition errors accumulate secularly; "unacceptably large" error), so a pressureless fluid is used there (L287-294). The paper's headline result is a different one: linear theory describes the metric in Newtonian and harmonic gauges but "is entirely unable [to] describe the synchronous gauge metric" (L134-140). |
| 12 | 168 | "Other particle-type implementations: arXiv:1611.03437, ..." | (unl.) | CORRECTED | `1611.03437/v3/src/Main_v3.tex:41, 68, 330` | 1611.03437 is a 3+1 scheme for a perfect fluid, eliminated through the constraints (L41, L68); it says itself that shell crossing of cold dark matter "can only be captured through an N-body description" (L330). It is the fluid precursor of the group's N-body code 1904.07841, not a particle implementation. Same finding as package s31_32, CHECK #30 (brief line 149). |
| 13 | 168 | "Other particle-type implementations: ... arXiv:1904.07841 ..." | (unl.) | CONFIRMED | `1904.07841/v2/src/Main.tex:26, 179, 214` | N free-falling particles with geodesic equations, energy-momentum projected to the mesh (L179, L214). |
| 14 | 168 | "Other particle-type implementations: ... arXiv:2307.15194" | (unl.) | CONFIRMED (precision) | `2307.15194/v1/src/aipsamp.tex:74, 280, 700-712, 741` | General-relativistic smoothed particle hydrodynamics (phantom) coupled to the Einstein Toolkit: a Lagrangian particle discretisation of a fluid, which "allows for simulation of gas as well as collisionless matter" (L741) and is evolved past shell crossing (L700-712). Particle-type, but not an Einstein-Vlasov N-body code in the sense of rows 13 and 1908.05683. |

## Lines 170-174: light-cone observables

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 15 | 170 | "A general-relativistic ray-tracing framework for NR spacetimes is given in arXiv:2209.06775" | (unl.) | CONFIRMED | `2209.06775/v2/src/paper.tex:51, 65, 239-241` | "a new ray-tracing tool to calculate cosmological distances in the context of fully nonlinear general relativity" (L65), applied to Einstein Toolkit simulations through `mescaline` (L239-241). |
| 16 | 170 | "Three results from 2026" | [VERIFIED] | CONFIRMED | `meta:arxiv-api/2603.24838`, `/2606.05479`, `/2606.18437` | Submitted 2026-03-25, 2026-06-03, 2026-06-16 (v1 each). |
| 17 | 172 | "20 synthetic observers, ℓ<100, 0.05<z<3" (arXiv:2603.24838) | [VERIFIED] | CONFIRMED | `2603.24838/v1/src/main.tex:40-41, 151` | 20 observers in each of three simulations (L151). |
| 18 | 172 | "the prediction of linear perturbation theory deviates from the nonlinear convergence by about 3%–30% on average" | [VERIFIED] | CONFIRMED | `2603.24838/v1/src/main.tex:41, 459` | "On average across our observers, linear perturbation theory predicts the nonlinear convergence to within 3--30% across all redshifts and angular scales" (L41); the residual remains "when considering all known general-relativistic corrections" and depends on angular scale, smaller scales being better matched (L459, L42). |
| 19 | 172 | "and most of the differences lie below cosmic variance" | [VERIFIED] | CONFIRMED | `2603.24838/v1/src/main.tex:43, 331` | "the differences are mostly below the level of cosmic variance" (L43). |
| 20 | 173 | "1 of 20 observers infers dark-energy parameters close to DESI's within 2σ (arXiv:2606.05479)" | [VERIFIED] | CONFIRMED (precision) | `2606.05479/v1/src/main.tex:50, 187-192, 250-251, 299` | Observer #18 is the only one to measure both a non-LambdaCDM w0 and w_a at 2 sigma; its w0 = -0.866 ± 0.039, w_a = -0.37 (+0.20/-0.17) lie in DESI's quadrant and agree with DESI within 1 sigma (L187-190); the 1/20 holds at all three resolutions (L192, L299). Most observers infer the opposite quadrant (w0 < -1, w_a > 0), attributed to their sitting in underdense regions; #18 sits in an overdensity (L250-251). |
| 21 | 174 | "at z≲0.2 the difference between the full-NR and the FLRW treatment is smaller than the statistical error of current data (arXiv:2606.18437)" | [VERIFIED] | CONFIRMED (precision) | `2606.18437/v1/src/main.tex:38, 307, 336-340` | Abstract as quoted (L38). In the body the systematic offset in the growth rate is < 1 per cent at z ≤ 0.2 against a statistical error of 3.1-4.1 per cent (L307, L338), the latter a Fisher forecast "for an ideal all-sky survey" (L336); the offset grows to 7.5 per cent at z = 0.3 and 38.9 per cent at z = 0.4 (L340). |
| 22 | 176 | "anisotropy of the Hubble flow and the local H₀ (arXiv:1807.01714, ...)" | (unl.) | CONFIRMED | `1807.01714/v2/src/HubLetter.tex:163, 249` | Local against global expansion rate; local H differs from the global value by < 1 per cent (L249). |
| 23 | 176 | "... arXiv:2103.11918 ..." | (unl.) | CONFIRMED | `2103.11918/v3/src/draft.tex:61, 91` | Luminosity distance and anisotropic sky-sampling at low redshift. |
| 24 | 176 | "... arXiv:2111.14423 ..." | (unl.) | CONFIRMED | `2111.14423/v1/src/CosmographyQuiet.tex:55, 66-68` | Predicted anisotropies of the nearby Hubble flow (dipole in distance, quadrupole in redshift drift). |
| 25 | 176 | "... arXiv:2402.09659 ..." | (unl.) | CONFIRMED | `2402.09659/v1/src/main.tex:25, 37` | Anisotropic sky-sampling and H0 from synthetic Pantheon-like catalogues. |
| 26 | 176 | "... arXiv:2507.01095" | (unl.) | CONFIRMED | `2507.01095/v3/src/main.tex:43, 58` | Prediction of the dipole in nearby luminosity distances. |
| 27 | 176 | "measurement of spatial curvature (arXiv:2010.07274)" | (unl.) | CONFIRMED | `2010.07274/v3/src/main.tex:34, 76-77` | |
| 28 | 176 | "redshift drift (arXiv:2404.06242)" | (unl.) | CONFIRMED | `2404.06242/v2/src/main.tex:60, 80` | First redshift-drift computation in fully relativistic (Einstein Toolkit) simulations (L80). |
| 29 | 176 | "void statistics (arXiv:2403.15134)" | (unl.) | CONFIRMED | `2403.15134/v2/src/void_statistics.tex:94, 130-132` | |

## Line 178: what the weak-field route already covers

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 30 | 178 | "gevolution solves all six metric degrees of freedom in Poisson gauge" (arXiv:1604.06065) | [VERIFIED] | CONFIRMED | `1604.06065/v2/src/compendium_arxiv.tex:55-56, 139-154` | Weak-field expansion; gauge conditions kept beyond linear level (L150); h_ij carries the two tensor degrees of freedom (L154). |
| 31 | 178 | "and pushes particles with canonical momenta, which holds for relativistic particles too" | [VERIFIED] | CONFIRMED | `1604.06065/v2/src/compendium_arxiv.tex:56-57, 408` | "geodesic equation which we write in terms of a canonical momentum such that it remains valid also for relativistic particles". |
| 32 | 178 | "It now has a GPU version (arXiv:2607.17929)" | [VERIFIED] | CONFIRMED | `2607.17929/v1/src/gevolution2.tex:65, 82, 110` | gevolution 2.0: MPI, OpenMP and CUDA offload (L82, L110). |
| 33 | 178 | "rotation and B modes of weak lensing (arXiv:2603.24179)" | (unl.) | CONFIRMED | `2603.24179/v2/src/paper_framedragging.tex:185-187, 1056` | Second-order perturbation theory of rotation and shear B-modes, supported by gevolution simulations (1920³ particles, L1056). |
| 34 | 178 | "number counts (arXiv:2106.01347)" | (unl.) | CONFIRMED | `2106.01347/v3/src/numbercounts.tex:138-139, 274` | |
| 35 | 178 | "redshift drift (arXiv:2505.04731)" | (unl.) | CONFIRMED | `2505.04731/v2/src/main.tex:49, 82` | |

## Line 180: the theoretical dispute

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 36 | 180 | "The Green–Wald framework argues that the effective stress–energy of small-scale inhomogeneity is traceless, like radiation and unlike dark energy (arXiv:1011.4920, arXiv:1407.8084)" | [BACKGROUND] | CONFIRMED (precision) | `1011.4920/v2/src/inhomogeneities-paper.tex:38-46, 320-328`; `1407.8084/v2/src/main.tex:440-466` | Proved, not only argued, within their framework: if the matter satisfies the weak energy condition (and the framework's assumptions on the one-parameter family of metrics), the effective stress-energy is traceless with positive energy density, "corresponding to the presence of gravitational radiation", and "cannot mimic the effects of dark energy" (1011.4920 L38-46); for an FLRW background it is a P = rho/3 fluid (1407.8084 L463-465). The label can be [VERIFIED]. |
| 37 | 180 | "Buchert et al. dispute its range of validity (arXiv:1505.07800)" | (unl.) | CONFIRMED | `1505.07800/v2/src/main.tex:106-110` | Among the five points: the proof of the trace-free property "is unphysical and the theorem about it fails to be a mathematically general statement"; the scheme "does not involve averaging". |
| 38 | 180 | "The backreaction term defined by spatial averaging depends on the choice of foliation, that is, of gauge (arXiv:2310.19451, arXiv:2409.00024)" | [VERIFIED] | CONFIRMED | `2310.19451/v2/src/Verweg2023_ClassQuantGrav_Averaging_GaugeProblem_preprint.tex:41, 180-186, 271`; `2409.00024/v1/src/main.tex:45, 47, 811` | "standard scalar averaging is foliation-dependent, and thus gauge-dependent" (2310.19451 L271); "the acclaimed kinematical backreaction term ... is foliation-gauge dependent" (2409.00024 L811). Both propose a gauge-invariant averaging. |
| 39 | 180 | "Reviews: arXiv:1112.5335, arXiv:1109.2314, arXiv:1612.08222, arXiv:2509.01320" | (unl.) | CONFIRMED | `1112.5335/v2/src/ar_arxiv_v2.tex:175`; `1109.2314/v1/src/Section_1_v3.tex:92`; `1612.08222/v3/src/kbmk-arxiv3.tex:50, 104`; `2509.01320/v2/src/notes_cosmo_beyond_FLRW.tex:111, 125` | 1612.08222 adds a survey of 50 researchers of the field (L50); 2509.01320 are Les Houches lecture notes (SciPost Phys. Lect. Notes, L125). |

## Line 182: timescape and DESI

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 40 | 182 | "timescape is one concrete realization of the Buchert averaging scheme (arXiv:gr-qc/0702082, arXiv:0909.0749)" | (unl.) | CONFIRMED | `gr-qc_0702082/v4/src/clocks.tex:128, 278`; `0909.0749/v2/src/observe.tex:104-105`; `2412.15143/v1/src/letter_P5+.tex:204` | "based on an exact solution to a Buchert average of the Einstein equations with backreaction" (0909.0749 L104-105). |
| 41 | 182 | "The Pantheon+ analysis reports a Bayesian preference for timescape: ln B>5 for the full sample, and still ln B>1 when restricted to z>0.075 (arXiv:2412.15143, arXiv:2311.01438)" | [VERIFIED] | CONFIRMED (precision) | `2412.15143/v1/src/letter_P5+.tex:189, 232, 301`; `2311.01438/v2/src/article_p4+.tex:643, 665, 689, 691` | Both numbers are from 2412.15143 (L189, L301). The earlier analysis 2311.01438 reports weaker evidence: ln B = 2.93 for the full sample at z_min = 0 (L643), ln B close to 0 for the full P+1690 sample beyond z_min = 0.075 and about 1 for the subsamples (L665, L689), overall ln B = 1.02 ± 0.04 for P+580 (L691). Citing both for the numbers mixes two analyses. |
| 42 | 182 | "When the DES supernova team combined supernovae with BAO angular scales, the two data sets were mutually inconsistent under timescape, and the AIC judged it worse than flat ΛCDM (arXiv:2406.05048)" | [VERIFIED] | CONFIRMED (precision) | `2406.05048/v2/src/main.tex:901-907, 946, 963, 977` | BAO: transverse angular BAO from SDSS, D_M(z_*)/D_M(z) (L903); "in tension in the Timescape model, and this model is therefore disfavoured relative to Flat-LambdaCDM by the AIC statistic" (L907), half Delta AIC = +6.3 (L946); "strong tension" by the Suspiciousness (L977). With DES-SN5YR alone timescape is weakly preferred (half Delta AIC = -1.7, L946, L963). The timescape fits use a cut z_min = 0.033 and no peculiar-velocity corrections (L901). |
| 43 | 182 | "The hint of evolving dark energy in DESI DR2 (arXiv:2503.14738)" | (unl.) | CONFIRMED | `2503.14738/v3/src/main.tex:275, 868` | 3.1 sigma for DESI BAO + CMB; 2.8-4.2 sigma with supernovae, depending on the sample. |
| 44 | 182 | "an estimate with three toy models, concluding that the magnitude is similar but probably insufficient to explain the whole deviation (arXiv:2601.20633)" | [VERIFIED] | CONFIRMED | `2601.20633/v1/src/PRL_main_V2.tex:180, 197, 306` | Clumps and voids (Dyer-Roeder), backreaction, large-scale curvature (L197); "might not be enough to explain the entirety ... but is found to be of a similar order of magnitude" (L180, L306). |

## Line 184: local voids and large-scale anomalies

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 45 | 184 | "A local void as an explanation of the H₀ tension: arXiv:1304.2884, ..." | (unl.) | CONFIRMED (precision) | `1304.2884/v5/src/Keenan_2013_astroph.tex:9, 19, 347` | An observational paper: evidence for a ~300 Mpc underdensity from the K-band luminosity density; such an underdensity "could resolve the apparent tension" (L19). Not itself a model of the tension. |
| 46 | 184 | "... arXiv:2009.11292, ..." | (unl.) | CONFIRMED (precision) | `2009.11292/v2/src/paper.tex:140, 166` | The KBC void explains the tension only in a MOND cosmology with 11 eV sterile neutrinos; in LambdaCDM the void itself is a 6.04 sigma tension (L166). |
| 47 | 184 | "... arXiv:2602.03928" | (unl.) | CONFIRMED | `2602.03928/v2/src/Nature_void_review_MNRAS_style.tex:175, 199` | A Perspective on the local void model for the Hubble and BAO tensions. |
| 48 | 184 | "a test with DESI DR2 BAO of the redshift offset required by local-void models gives a result compatible with zero (arXiv:2606.02712)" | [VERIFIED] | CORRECTED | `2606.02712/v3/src/z0m_MNRAS_style.tex:205, 283, 559, 798` | Incomplete in a way that reverses the reading. The data are BBN + CMB + DESI DR2 BAO + cosmic chronometers (L205). z_0 = -0.4 (+0.8/-0.9) per cent for z > 0.5 and -0.1 ± 0.7 per cent for z > 0.29: compatible with zero, but the void value 0.84 per cent is also compatible ("the posterior inference on z_0 is consistent with 0.84%", L559; Delta chi² < 2, L205). The authors conclude that a void large enough to solve the Hubble tension "cannot be ruled out" (L205, L798); only the Bayesian evidence disfavours the extra parameter (L798). |
| 49 | 184 | "Tests of the cosmological principle and anomalies: arXiv:2207.05765, ..." | (unl.) | CONFIRMED | `2207.05765/v4/src/observations.tex:98, 107` | Review of observational tests of the cosmological principle. |
| 50 | 184 | "... arXiv:2009.14826, ..." | (unl.) | CONFIRMED | `2009.14826/v2/src/manuscript.tex:7, 16` | Quasar dipole from CatWISE2020. |
| 51 | 184 | "... arXiv:2206.05624, ..." | (unl.) | CONFIRMED | `2206.05624/v2/src/manuscript.tex:6, 33-34` | Joint radio-galaxy and quasar dipole. |
| 52 | 184 | "... arXiv:2302.02028, ..." | (unl.) | CONFIRMED | `2302.02028/v1/src/CF4-submit.tex:154, 165` | Bulk flow from CosmicFlows-4. |
| 53 | 184 | "... arXiv:2510.05340" | (unl.) | CONFIRMED | `2510.05340/v3/src/review.tex:194, 293-295` | A review of large-scale peculiar velocities (bulk flows). |

## Statements labelled [JUDGEMENT] (no verdict)

- Line 178: "For most relativistic effects in the late universe this route is both fast and
  sufficient. Any increment from NRPIC in the late universe can only come from places where
  the weak-field expansion fails or where independent verification is needed." Consistent with
  rows 4, 9 and 21 (negligible backreaction on Newtonian-gauge hypersurfaces; sub-percent
  agreement in the weak field; FLRW modelling adequate at z ≲ 0.2), but it remains a
  judgement and is not written into a paper as fact.

## Searches

The regex searches are in `specs/l166.txt` ... `specs/l184.txt`, run with
`scripts/locate.py`; outputs in `scratch/kb/tmp/s33/loc_*.txt`. Metadata dumps:
`scripts/meta_dump.py`, outputs `scratch/kb/tmp/s33/meta{1,2,3,4}.txt`. Locators that came
from reading a passage rather than a regex hit were read with `sed -n` on the same files.
