# VERIFIER report: gate KB-G1 of the knowledge base

Verifier: helper of kb, wave 2b, 2026-11-19 (Opus). Fresh reader: I did not read `REVIEW.md`,
`../REVIEW-wave2.md`, `VERIFY_RESULTS.*` or `STAGE_REPORT.md` of this package, and I read the
answers in `FIRST_QUESTIONS.md` only after writing my own answers from the sources (journal
entry 14:05 UTC and the section Q below). My code (`verifier/`) is my own and does not import
`kb/kbtool`; it opens the snapshot `kb-data/db/current -> kb-20261115-a848a06.sqlite`
(sha256 `a848a06b...`) read-only and reads the raw sources as data.

Runs (hand-written manifests, because `nrpic-run submit` refused the shared worktree while other
kb helpers had uncommitted code in `kb/kbtool/`; the manifests say so):

| Run id | What | Output |
|---|---|---|
| `kb-20261119-142015-7620bd4` | tests P, C, K, Q (`verifier/run_all.py`), 5.6 s, 1 core | `scratch/kb/kb-20261119-142015-7620bd4/` |
| `kb-20261119-142303-f38a48c` | follow-up of P: every TeX paper with no bibliography entry | `scratch/kb/kb-20261119-142303-f38a48c/` |
| `kb-20261119-142448-3ea268d` | follow-up of C: locator strings against locator rows, all claims | `scratch/kb/kb-20261119-142448-3ea268d/` |

Figures (looked at): `fig_papers.png`, `fig_summary.png` (first run), `fig_zero_bib.png` (second).

## Verdicts

| Test | Items | CONFIRMED | NOT CONFIRMED | WRONG |
|---|---|---|---|---|
| P: twenty papers, equations / sections / bibliography against the TeX source | 20 | 18 | 0 | 2 |
| C: ten statements of the claims layer at their locators | 10 | 10 | 0 | 0 |
| K: ten rows of the parameter index against this repository's source | 10 | 10 | 0 | 0 |
| Q: the nine first questions answered again from the sources | 9 | 9 | 0 | 0 |

Per-item verdicts with the numbers: `verifier/verdicts.tsv`. Predictions (JOURNAL.md): P "at
least 18 of 20, no lost content" — held for the count, refuted on "no lost content" (two
papers lost their bibliography); C, K and Q held.

## Defects found (most important first)

1. **Bibliographies lost for unusual reference-list formats; eleven papers with parse status
   `ok` have no bibliography entry at all** [VERIFIED, run `kb-20261119-142303-f38a48c`,
   `zero_bib.tsv`]. 20 of 707 TeX papers have zero rows in `bib_entries`. My parser finds a
   reference list in 14 of them: `\bibitem` inside a REVTeX-3 `references` environment
   (0710.5073, 1109.2484, 1302.5308, 1304.7791, gr-qc/0107076, gr-qc/9402041, hep-ph/0011159,
   astro-ph/0003278), AASTeX `\reference` items (1201.4794: 46), a macro standing for
   `\bibitem` (gr-qc/0304002 `\bi`, gr-qc/9703066 `\bib`), `\harvarditem` in the `.bbl`
   (2507.01095: 103), plain-TeX `\ref` paragraphs (gr-qc/9906015, astro-ph/9510056). Eleven of
   them carry `parse_status = ok`, so the quality score does not flag the loss; those eleven
   alone have 502 reference items whose entries and citation edges are missing. The other six
   (all `review`) have no list my parser recognizes.
2. **The parameter index of this repository is stale** [VERIFIED, run
   `kb-20261119-142015-7620bd4`, `params.json` "stale"]. It was built at commit `a1c2237`
   (2026-11-15 03:54 PST). On today's `main` (`27b2ced`), 101 (block, name) pairs read by
   `pin->Get*` calls in 12 files are absent from the index: the scalar field
   (`scalar_field.cpp` 13, `scalar_field_noise.cpp` 21), collisions (`nrpic_collide.cpp` 12),
   punctures and Bowen-York (`nrpic_puncture_setup.hpp` 11, `nrpic_bowen_york.hpp` 7),
   `nrpic_geodesic.cpp` 8, `scalar_field_tests.cpp` 9, `rng_test.cpp` 6, `nrpic_kick.cpp` 5,
   `nrpic_newton.cpp` 5, `nrpic_cf.cpp` 3, `utils/rng.hpp` 1. A track that looks up an option
   of release core-v0.3 in the index will not find it. What the index does hold is exact (K).
3. **gr-qc/9906015 (plain TeX) is a shell** [VERIFIED, `papers.tsv`]: the 71 displays are
   there, but no equation numbers (the source has 58 live `\eqno`), no sections and no
   bibliography (21 `\ref` items). The knowledge base itself flags it `review` (score 0.51).
4. **One claim lost one of its two locators** [VERIFIED, run `kb-20261119-142448-3ea268d`]:
   claim 25 names `L1084; L1101-1103` in `claims.locator`, but `claim_locators` holds only
   L1101-1103 (the part with e = 0.2 is at L1084). Of the 649 claims with a locator string,
   this is the only one whose string and rows disagree.
5. Minor locator offsets, the content being right: claim 254 points at the stability bound
   (L840-842) while the collapse it states is at L853-855; `FIRST_QUESTIONS.md` Q8 cites L792
   for a sentence whose number sits on L793; Q9 cites `particles_tasks.cpp:30-45` at
   `a1c2237`, where it is right, but on `main` the deposit task is now at line 47.

## Test P: twenty papers

Sample: 10 random priority-3 papers and 10 random others among the 707 TeX papers, seed
20261119 (`verifier/check_papers.py`). My counter (`verifier/texcount.py`) finds the main
file, flattens `\input`-like commands, strips comments, `\iffalse` blocks and `comment`
environments, expands macros that stand for `\begin{equation}` and the like, and counts.

- Main file: my choice equals the knowledge base's for 20 of 20.
- Equations. The knowledge base stores one record per numbered row of a multi-row
  environment (align, eqnarray) and one record per environment otherwise; my environment
  count is therefore lower (grey crosses in `fig_papers.png`). Numbered equations (rows that
  carry a number, including `\tag` and subequations): equal in 20 of 20. Counter steps
  (distinct numbers): equal in 20 of 20. Records under the rule above: equal in 19 of 20;
  2006.16182 has one more because a trailing `\nonumber` row of one eqnarray is kept as its
  own record (definitional, not an error).
- Sections, levels 1 to 3: counts equal in 20 of 20; titles agree position by position
  except three in 2003.08014 that are macros (the knowledge base expanded them, my parser did
  not). For gr-qc/9906015 both are zero because neither parser reads plain-TeX headings.
- Bibliography: equal to my count from the same source kind (`.bbl` `\bibitem`, inline
  `thebibliography`, or cited keys present in the `.bib`) in 18 of 20. 1201.4794 (46 AASTeX
  items, knowledge base 0, parse status `ok`) and gr-qc/9906015 (21 plain-TeX items, 0) are
  WRONG; see defect 1.

| Paper | prio | records KB/mine | numbered KB/mine | sections KB = mine | bib KB/mine (source) | Verdict |
|---|---|---|---|---|---|---|
| 1011.4920 | 3 | 161/161 | 160/160 | 5/3/0 | 37/37 (bbl) | CONFIRMED |
| 1901.04498 | 3 | 0/0 | 0/0 | 1/0/0 | 26/26 (bbl) | CONFIRMED |
| 2003.08014 | 3 | 37/37 | 37/37 | 10/8/0 | 104/104 (bbl) | CONFIRMED |
| 2203.13852 | 3 | 145/145 | 137/137 | 7/7/3 | 124/124 (thebib.) | CONFIRMED |
| 2402.02178 | 3 | 18/18 | 18/18 | 5/10/0 | 101/101 (bbl) | CONFIRMED |
| 2405.10692 | 3 | 17/17 | 17/17 | 6/9/0 | 155/155 (bbl) | CONFIRMED |
| 2507.18312 | 3 | 144/144 | 144/144 | 12/6/0 | 48/48 (bib) | CONFIRMED |
| 2601.17117 | 3 | 42/42 | 42/42 | 6/7/0 | 134/134 (bib) | CONFIRMED |
| 2607.17929 | 3 | 19/19 | 19/19 | 7/9/0 | 28/28 (bib) | CONFIRMED |
| gr-qc/9906015 | 3 | 71/71 | 0/0 (58 `\eqno`) | 0/0/0 (plain TeX) | 0/21 (plain `\ref`) | WRONG (flagged `review`) |
| 1101.3097 | 1 | 23/23 | 23/23 | 7/8/4 | 94/94 (bbl) | CONFIRMED |
| 1201.4794 | 2 | 29/29 | 29/29 | 8/2/0 | 0/46 (AASTeX) | WRONG |
| 1203.6478 | 1 | 27/27 | 23/23 | 8/6/0 | 37/37 (thebib.) | CONFIRMED |
| 1707.06938 | 2 | 30/30 | 30/30 | 10/7/0 | 59/59 (bbl) | CONFIRMED |
| 2003.10455 | 1 | 89/89 | 89/89 | 11/13/0 | 157/157 (bbl) | CONFIRMED |
| 2006.16182 | 2 | 92/91 | 91/91 | 6/15/33 | 1030/1030 (bbl) | CONFIRMED |
| 2409.16053 | 2 | 30/30 | 30/30 | 6/11/0 | 86/86 (bbl) | CONFIRMED |
| 2504.05937 | 1 | 104/104 | 104/104 | 8/7/0 | 75/75 (bbl) | CONFIRMED |
| astro-ph/9709072 | 2 | 12/12 | 12/12 | 0/0/0 | 19/19 (thebib.) | CONFIRMED |
| astro-ph/9906391 | 1 | 16/16 | 16/16 | 2/0/0 | 14/14 (thebib.) | CONFIRMED |

## Test C: ten claims at their locators

Sample: 10 of the 533 claims with label `fulltext` whose locators all resolve, seed 20261119
(`verifier/check_claims.py`; the source lines are in `claims_excerpts.txt` of the run
directory, not committed). I read each passage and judged whether it supports the claim as
worded.

| Claim | Paper, locator | Verdict | Note |
|---|---|---|---|
| 25 | 2609.14218 L1101-1103 (+L1084) | CONFIRMED | thresholds supported; L1084 missing from `claim_locators` (defect 4) |
| 58 | 1609.01588 L503 | CONFIRMED | axis ratio at the turnaround of the first axis |
| 63 | 1609.01588 L637-693 | CONFIRMED | Doroshkevich distribution and its normalization |
| 254 | gr-qc/0601112 L840-842 | CONFIRMED | bound at the locator, collapse statement at L853-855 |
| 296 | 1101.3097 L722-728 | CONFIRMED | Knudsen number as the inverse dimensionless cross section |
| 319 | astro-ph/0110561 L309-323 | CONFIRMED | hard-sphere coefficient a = sqrt(16/pi) |
| 435 | 1004.1353 L58-67 | CONFIRMED | three equal-mass holes; four equal-mass at L1309; authors match |
| 541 | 2611.12831 L686 | CONFIRMED | higher-degree kernels gave no advantage |
| 585 | 2611.12831 L678 | CONFIRMED | lapse excision after the push, before deposit |
| 640 | 1004.1353 L185-194, L1238-1261 | CONFIRMED | non-converging error; junk differences an order of magnitude |

## Test K: ten rows of the parameter index

Sample: 10 of the 1115 rows of `params` with `repo_id = 'local/nrpic'`, seed 20261119
(`verifier/check_params.py`). For each row the file at the indexed commit `a1c2237` was read
with `git show`; a call `->Get*`/`->GetOrAdd*` with that block, name, type and default must sit
on the recorded line. Non-literal blocks and names (`{block}`, `{budget_key[a]}`) are compared
as expressions.

| Row | block / name | type | default | file:line | Verdict |
|---|---|---|---|---|---|
| 5871 | {pzoom->block_name} / p_zoom | Real | (FLT_MIN) | cyclic_zoom/zoom_data.cpp:59 | CONFIRMED |
| 5932 | {block} / gamma_thermal | Real | 5.0/3.0 | eos/primitive_solver_hyd.hpp:97 | CONFIRMED |
| 5941 | {block} / c2perrs | Integer | 1000 | eos/primitive_solver_hyd.hpp:141 | CONFIRMED |
| 6272 | problem / smoothtr | Real | 0.0 | pgen/fluids/disk-magnetosphere.cpp:274 | CONFIRMED |
| 6349 | mhd / const_accel_val | Real | none (GetReal) | pgen/fluids/rt.cpp:91 | CONFIRMED |
| 6391 | problem / id | String | "flrw" | pgen/nrpic/nrpic_cosmo.cpp:87 | CONFIRMED |
| 6570 | problem / erad | Real | none (GetReal) | pgen/tests/rad_linear_wave.cpp:156 | CONFIRMED |
| 6737 | {block} / cpower_rel | Real | 1. | srcterms/srcterms.cpp:65 | CONFIRMED |
| 6814 | z4c / {budget_key[a]} | Real | 0.0 | z4c/driftcontrol/driftcontrol.cpp:168 | CONFIRMED |
| 6886 | z4c / damp_ch_chipow | Real | -0.25 | z4c/z4c.cpp:137 | CONFIRMED |

All ten calls sit on the same line on today's `main`. Recall at the indexed commit on every
file under `athenak/src/particles/` and `athenak/src/pgen/nrpic/` that reads parameters: 83 of
83 calls (61 literal, 22 non-literal) have a row on their line, with no extra row and no type or
default mismatch. Staleness against `main`: defect 2.

## Test Q: the first questions answered again

I answered each question from the sources before reading `FIRST_QUESTIONS.md` (sources:
`kb-data/raw/arxiv/<id>/<v>/src/<file>` lines, and AthenaK at upstream `c5a0d7f` and this
repository). Then I compared, and checked mechanically (`verifier/check_answers.py`): every
labelled equation number of the four papers against my own numbering (2611.12831: 86 of 86
equal; 2609.14218: 45 of 45; 2512.14649: 33 of 33; 2404.16270: 21 of 21), the nine equation
numbers cited in the answers (9 of 9), 73 cited paper locators (73 of 73 contain the cited
item) and 18 cited code locators (18 of 18).

| Q | My answer, own wording, with locators | Comparison with `FIRST_QUESTIONS.md` | Verdict |
|---|---|---|---|
| 1 | First-order (linear B-spline, cloud-in-cell) shape by default, `2611.12831v1` L641-648; binomial 1/4-1/2-1/4 filter per direction applied to the ten sources after deposition, L680-686; number of passes not stated | same; adds the AMR deposition (L738-762, Eqs. 91-92, numbers verified) and c_H (L688-696) | CONFIRMED |
| 2 | Time-symmetric, conformally flat slices with K_ij = 0 and zero shift; Hamiltonian constraint satisfied by construction per model: OS interior conformal factor L903, prolate spheroid via a Poisson solve and the matching ADM density L967, ST clusters from the static equilibrium L1100-1117, Plummer L1261-1275; particles at rest or isotropic so S_i = 0 in the continuum; sampling noise gives constraint violations ~N^(-1/2), L1129, L1509-1511 | same; its open point (Sec. 4 clump momenta) I confirm: no "constraint" in L1313-1362 | CONFIRMED |
| 3 | Only symbols for kappa_1, kappa_2, mu_S, eta, eta_0, kappa_{1,0}, c_H (L238-397, L688-696); stated values: mu_L = 2/alpha (1+log, L380), factor 3/4 in the B-driver (L384), alpha_exc = 0.1 (L1117) and 0.05 in Sec. 4 (L1338) | same; adds refinement thresholds 0.2/0.02 (L722-725) and upstream defaults (`z4c.cpp:131-148`, checked) | CONFIRMED |
| 4 | No availability statement; future work L1393 (higher-order methods, extremal black holes, cosmic censorship, instability and collapse); no "cosmolog", no "tidal"; matter collisionless, "collisional" only as context (L1008, L1323) | same; adds resampling under AMR (L763) and FLRW only inside OS (L867, L877) | CONFIRMED |
| 5 | No timings, node or GPU hours, throughput or scaling; only CPU/GPU portability (L674), the machines (L1398) and run sizes (L1017, L1338) | same | CONFIRMED |
| 6 | `2609.14218v1`: growing-mode gradient-expansion data on a K = -3H slice from Psi = exp(zeta/2), E and J from the constraints, H_i = 5k = 50/L (L509-549); modified 1+log slicing with an H_k term and C = 5 (L452-461), Gamma driver damped with 3H (L463-469), scaled coordinates eta = 10 (L476-487); threshold by apparent-horizon formation, analytic hoop/Zel'dovich criterion (L900-916); particles at e = 0.2: horizon for mu >= 0.05, none for mu <= 0.045 (L1101-1103), threshold ~0.045 if accepted (L1145) | same, with equation numbers (3.4)-(3.10), (2.20), (2.22) consistent with my numbering of all 45 labels | CONFIRMED |
| 7 | `2512.14649v2`: quadratic (eps_1 = 0.01, eps_2 = -0.02, H_0 = 1e-5 M_Pl) and Higgs-inflection (Lambda = 1.86e-6, v = 0.198 M_Pl, phi_0 = -1.2 M_Pl), Table at L400-426; N = 256, sigma = 1, M_Pl = 100 (L519), s = 5 (L506), k_max = N k_sigma/4 (L512), geodesic slicing, no damping, no AMR, periodic (L483); acceptance: R spectrum vs Mukhanov-Sasaki (L522-536), constraints at second order in the noise (L538-541), convergence (App. at L733), backreaction ablation below one part in 10^4 (L520) | same | CONFIRMED |
| 8 | `2404.16270v1`: r_p below ~100 r_g (L194), effects of 1 % or more in Fig. 2 (L204); prograde below 0.1 % except beta >= 9 (L788-790); retrograde: separation from beta ~ 2 vs 2.5 and up to 30 % more separations (L795-796); HRNA vs 1PN agree to beta = 5, up to 10 % apart for 5 <= beta <= 10 (L792-793), 1PN insufficient below ~20 r_g (L477) | same (its "L792" sentence ends on L793) | CONFIRMED |
| 9 | Cell-centred Z4c (cell-centred boundary buffers and `CellCenterX`; paper L674); `Tmunu` holds E, S_i, S_ij (ten components, `z4c/tmunu.hpp`); upstream: `MHD_SetTmunu` after `MHD_CopyU` in the run list, and `Z4c_CalcRHS` waits for it at every stage (`z4c_tasks.cpp:48-58`, `dyn_grmhd.cpp:198-200`); here the NRPIC particles deposit once per step in `after_timeintegrator` (`particles_tasks.cpp:47` on `main`) | same; its local line range 30-45 is right at `a1c2237` | CONFIRMED |

## Not checked

- The 64 repositories other than AthenaK in the code index, the symbols and code chunks, the
  embeddings and the retrieval ranking (KB-G2 material).
- Title and author agreement with arXiv/INSPIRE metadata, and the citation-edge resolution.
- Claims with labels other than `fulltext`; the 31 claims with status `checked`.
- The inventory report and the download checks of KB-G1 (not part of this package's task).

## Requests

To kb (lead):
1. Parse reference lists in REVTeX-3 `references` environments, AASTeX `\reference` items,
   macros standing for `\bibitem`, and `\harvarditem` entries; lower the quality score (or set
   `review`) when a paper with `\cite` commands ends with zero bibliography entries. The list
   of the 20 papers is in `zero_bib.tsv` of run `kb-20261119-142303-f38a48c`.
2. Re-index `local/nrpic` at the current `main` (core-v0.3 options are missing; defect 2) and
   record the commit in the reports that cite the index.
3. Restore the second locator (L1084) of claim 25.
4. Give helpers a way to register runs while another helper's shared code is uncommitted in the
   shared worktree (or have helpers commit `kb/kbtool` work before others run).
