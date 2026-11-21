# Second-agent review of the CHECK.md rows of the brief check (sample of 30)

Reviewer: kb helper of package claims_brief (wave 3, 2026-11-21), who wrote none of the eleven
brief-check packages. Written before any label was changed from these packages.

**Sample.** 30 rows of the 620 CHECK.md rows on `kb/brief-check` at 476a1763, drawn by
`scripts/plan_outcomes.py` in run kb-20261121-232142-3378910 (file `sample.tsv` there):
random seed 20261121, stratified by package, 3 rows from each of the eight larger packages
and 2 from novelty, s7_s8 and s39_frontier, drawn from the rows with a TeX locator, rows
joined to a brief seed first (s39_frontier has no joined row, so its two come from the rest).

**What I did per row.** Read the row (quotation, verdict, locator, note) and every TeX
locator it gives, in `kb-data/raw/arxiv/<id>/<v>/src/<file>` (at most twelve lines per
locator, by a reader outside the store, `scratch/kb/claims_brief/review/show_locs.py`), and
for the two CORRECTED rows of section 3 also the brief line itself (lines 148 and 235). I
judged whether the passages say what the row says and whether the verdict follows. I did not
redo the packages' searches (a "closest work" or "not found" claim stays theirs), and I did
not check metadata locators (`meta:`, `iq:`).

**Result: 30 agree, 0 disagree** (threshold: more than 3 disagreements would have stopped
every upgrade). Prediction P3 (at most 3 disagree) held. Two rows carry a remark.

| # | Row | Brief line | Verdict | Locators read | Review | Reason |
|---|---|---|---|---|---|---|
| 1 | novelty #31 | 1749 | CONFIRMED (precision) | 1505.02959 L46-64; 2403.03470 L143 | agree | the 2015 paper tests Isaacson's averaged radiation-fluid behaviour numerically; 2403.03470 L143 calls its proof of the Burnett conjecture the first without symmetry assumptions. Remark: "closest numerical work" is the package's search, not checked here |
| 2 | novelty #9 | 410 | CONFIRMED | 2303.07980 L357; 2006.16182 L1046-1048 | agree | L357 gives 5.25/10.75 before annihilation; the after-annihilation share 0.409 follows from the N_eff definition at L1046 with N_eff = 3.045 (my arithmetic: 0.2271 x 3.045 = 0.692, 0.692/1.692 = 0.409) |
| 3 | s310 #37 | 261 | CONFIRMED | 2405.10692 L149, L166, L186-188 | agree | title and abstract: a C++ package for stochastic lattice simulation with stochastic delta-N |
| 4 | s310 #46 | 261 | CONFIRMED (precision) | 2302.00655 L53, L79, L247 | agree | L79 presents the method in "this Letter and its companion paper"; L247 releases the tool under a separate citation |
| 5 | s310 #12 | 259 | CONFIRMED | 0808.1786 L47, L76-78 (and L79-80) | agree | abstract: stochastic and field-theoretic approaches give exactly the same fluctuations of light fields, at leading slow-roll order (L79-80) |
| 6 | s311 #22 | 271 | CONFIRMED | 2610.13294 L57, L106 | agree | title "Hills EMRIs"; L106: a black-hole binary tidally separated by a massive black hole |
| 7 | s311 #5 | 269 | CONFIRMED | astro-ph/0309084 L59, L70, L681-686 | agree | ejection of hypervelocity stars by Hills' mechanism (L70); S-stars as components of disrupted binaries (L684-686) |
| 8 | s311 #1 | 269 | CONFIRMED | astro-ph/0309084 L1112; 1201.4794 L1058 | agree | both bibliographies cite Hills 1988, Nature 331, 687; 1988 predates arXiv |
| 9 | s31_32 #12 | 145 | CONFIRMED | 2607.17929 L65, L82 | agree | gevolution 2.0, GPU-accelerated |
| 10 | s31_32 #11 | 145 | CONFIRMED | 1308.6524 L95; 1604.06065 L55; 1509.01699 L55 | agree | weak-field formalism (1308.6524), the code with six metric degrees of freedom (1604.06065, 1509.01699) |
| 11 | s31_32 #25 | 148 | CORRECTED | 2003.08014 L285, L298, L307, L317-321, L326-330 | agree | brief line 148 lists the comparison in the row "Full NR + dust fluid"; L285 compares four codes of different rungs (gevolution, GRAMSES, Einstein Toolkit, CosmoGRaPH) |
| 12 | s33 #37 | 180 | CONFIRMED | 1505.07800 L106-110 | agree | point (ii) at L109: the trace-free proof "unphysical" |
| 13 | s33 #17 | 172 | CONFIRMED | 2603.24838 L40-41, L151 | agree | l < 100, 0.05 < z < 3 (L41); 20 observers in each of three simulations (L151) |
| 14 | s33 #38 | 180 | CONFIRMED | 2310.19451 L41, L180-186, L271; 2409.00024 L45, L47, L811 | agree | both: averaging is foliation dependent, hence gauge dependent (L271; L811) |
| 15 | s34_36 #45 | 220 | CONFIRMED (precision) | 2312.12499 L113, L209, L216, L235 | agree | enhancement up to the inverse light-crossing time of the largest halos (L113), none on linear scales (L216), caution above that frequency (L235) |
| 16 | s34_36 #44 | 220 | CONFIRMED | 2312.12499 L111, L139, L157-159 | agree | hybrid N-body and lattice simulation with decay of the matter into radiation (L111, L159) |
| 17 | s34_36 #65 | 222 | CONFIRMED | 2505.21885 L65, L100, L253, L442, L513 | agree | "up to two orders of magnitude" (L65), linear regime (L65, L253) |
| 18 | s35 #16 | 201 | CONFIRMED (precision) | 2608.13206 L457-471, L480-483, L495, L505 | agree | the Zel'dovich-Novikov law is a two-parameter late-time fit (L463-466); F from 2.958 to 3.613 (L495) |
| 19 | s35 #24 | 205 | CONFIRMED | 2211.13950 L157-166; 1810.03490 L133; 2609.14218 L213 | agree | asphericity, angular momentum, inhomogeneity (L165-166; L133), velocity dispersion (L161-162; L213) |
| 20 | s35 #41 | 213 | CONFIRMED | 2306.11810 L79, L96, L267 | agree | spin falls as the hole accretes non-rotating background matter (L96) |
| 21 | s37_38 #22 | 230 | CONFIRMED (precision) | 1907.10743 L85, L103, L116-124; 2506.21779 L124; 1706.09501 L109, L2438-2439 | agree | conjecture stated at L117-118, measure-valued fields at L121; the "if and only if" form at 2506.21779 L124 |
| 22 | s37_38 #50 | 235 | CORRECTED | 2611.12831 L42-44, L1313, L1338, L1352, L1360, L1385-1390 | agree | brief line 235: "Full NR with a particle-dark-matter environment was not found [TO VERIFY]"; the target paper evolves two overdensities in a common collisionless (particle) envelope through black-hole formation, inspiral, merger and accretion (L42-44, L1385-1390) |
| 23 | s37_38 #16 | 229 | CONFIRMED | gr-qc/0512031 L147-153, L191, L197-199, L929, L954, L315-317 | agree | past dynamics differs considerably from the perfect fluid (L197-199); heteroclinic network (L149, L929) |
| 24 | s39_frontier #22 | 250 | CONFIRMED (precision) | 2610.32592 L18, L67-92, L107 | agree | a thesis by Launay alone (L18, L107) collecting papers with Rigopoulos and Shellard (L67-78) |
| 25 | s39_frontier #11 | 245 | CONFIRMED | 2609.03051 L173, L282, L592 | agree | neighbouring peaks need not map one to one onto black holes (L173); Hawking-energy compactness (L282), threshold near 0.56 (L592) |
| 26 | s5_s6 #2 | 410 | CONFIRMED | 2002.12778 L276-291 | agree | t = 0.738 s at 1 MeV (L278-280) and M = gamma c^3 t/G = 2.03e5 gamma (t/1 s) M_sun (L288-291) give 1.5e5 M_sun. Remark: L287 prints R_H^{-3} where the volume needs R_H^3 (a typo of that paper, [TO VERIFY]; not a section-5 row, left to the lead) |
| 27 | s5_s6 #4 | 410 | CONFIRMED | astro-ph/0306304 L31, L140-148 | agree | anisotropic stress ("anisotropic inertia") of free-streaming neutrinos once out of equilibrium (L142-145) |
| 28 | s5_s6 #50 | 512 | CONFIRMED (precision) | 2111.05282 L980-997, L1003-1022, L1924 | agree | matter equation with the exchange term Q_a (L980-988); the sum is flux-conservative without sources (L1006-1014) |
| 29 | s7_s8 #22 | 583 | CORRECTED | 2607.09326 L96, L141, L307, L309-311, L317; 2606.16879 L43, L56-61; 2306.17774 L49 | agree | stability of Einstein-de Sitter asymptotics proven for Einstein-Euler with polytropic index n > 3 (L141), Gowdy numerics agree (2606.16879 L43, L59), massless Vlasov FLRW stable (2306.17774 L49); massive Vlasov stays open. Remark: the content is right; the class "CORRECTED" is strong for an item left [TO VERIFY], and coord/BRIEF_ERRATA.md files it as an imprecision (row 2.101), so this package does not refute the seed (claim 790 annotated, status partial) |
| 30 | s7_s8 #21 | 583 | CONFIRMED (precision) | 1709.00267 L363, L381, L390-394 | agree | the Milne model is vacuum (L381); first 3+1 Einstein-Vlasov stability with Lambda = 0 (L393); earlier results needed Lambda > 0 or massless particles (L392) |

**Consequence.** 0 of 30 disagree, so the outcomes of all eleven packages are imported as the
rules of step 2 give them (JOURNAL, "Rules of step 2"): verified where every row on a seed
supports it with a TeX locator in the database, refuted where an errata row of section 1 or 3
corrects it, annotated otherwise. The sample covers each package with 2 or 3 rows; a package
with a systematic defect in one row type could still pass with 2 rows, so the import rests
on 30 rows, not on a check of each package's 33 to 74 rows [JUDGEMENT].
