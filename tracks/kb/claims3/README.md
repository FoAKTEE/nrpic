# claims3: brief seeds 803 and 805, `kb claim supersede`, the weak class, fragments

Package of owner kb, wave 3 batch 14 (2026-11-24). It answers decision 0035 item 5 and the open
items O1, O2, O3, O5 (and in part O4) of `tracks/kb/stage/KB-G3/OPEN.md`. It wrote to the
working database `kb-data/db/kb.sqlite` inside the writer lock, in registered runs only. It took
no snapshot: `db/current` still points to kb-20261124-9872d21, so readers of `current` see none of
this until the lead snapshots. Card time used: none.

Status: done. All five items are closed, all predictions in `JOURNAL.md` were written first, and
all write predictions held. What is still open is listed under "Open" below.

## Results

| Item | What was done | Evidence |
|---|---|---|
| 1. Seed 803 (stability of matter-dominated FLRW under Einstein-Vlasov) | Answered by the new claim 869 (fulltext/checked, 13 locators in 9 papers). Future stability is proven in three settings: with Lambda > 0; for the Milne model with massive Vlasov matter (1709.00267 L363, L392-393); and for massless, radiation-like Vlasov matter on decelerating FLRW (2306.17774 L49; 1904.13290 L333). Toward the past, the Big Bang is stable (2402.08544 L152). For the matter-dominated Einstein-de Sitter model the store has fluid results only: dust is linearly unstable, and a polytropic fluid with n > 3 on T^3 is nonlinearly stable (2607.09326 L96, L141; 2606.16879 L43). **No Einstein-Vlasov result for a matter-dominated FLRW with Lambda = 0 is in the store** [VERIFIED for the store; the literature outside it is not claimed]. 803 and the related seed 790 are annotated with a pointer to 869. | runs kb-20261125-023523-40c916a (store search, 20 papers), kb-20261125-023541-5ae96e9, kb-20261125-023915-2822f6f |
| 1. Seed 805 (three derivations to check) | All three were re-derived by the tracks, with symbolic checks and registered runs. The expanding dust ball was checked by A (expball/DERIVATION.md section 8) and by core. The Einstein-Straus bubble was checked by D (four corrections; a and m_p recomputed in D's G1 gate review). The strong-field Hills scale was checked by F (run F-hills-20261115-045435-f62d553, verifier V3), with one correction: part of the brief's parameter box lies below the plunge bound. 805 is annotated with the files, their commits and the run ids, and keeps its to_verify label because it is an instruction, not a statement. | run kb-20261125-023541-5ae96e9; JOURNAL entry 3 |
| 2. `kb claim supersede` | A claim whose text is wrong, or that holds no statement, is closed and points to the claim that replaces it. The replacement is a new claim (`--text`, with its locator rows written at once) or an existing one (`--to`). The old claim gets label refuted and the new status `superseded`; both claims get an event; a `claim_links` row joins them; `kb claim show` prints `superseded_by`. `kb claim withdraw` closes a heading fragment that nothing replaces (status `withdrawn`). A superseding abstract claim is set to status checked (O4), a superseding judgement claim to status located. The first case, 682 -> 862, is now linked. | kb/kbtool/claims_db.py, claims_cli.py; kb/tests/test_claims_supersede.py (6 tests); suite 276 tests, 1 xfail; run kb-20261125-023539-1da3331 |
| 3. Weak class | The query in `scripts/weak_class.py` selects claims labelled fulltext, abstract or title_only whose label was set by a pipeline step and that no person has read against their own wording. It finds 573 claims, in four strata by the step that set the label: WA 426 (automatic locator check), WQ 90 (claims_tracks queue), WB 43 (claims_brief join), WM 14 (the brief's labels mapped to 12.8 labels). I drew 30 with seed 20261125, committed before the draw, and re-read each at its locators. **26/30 = 86.7 per cent are right as worded (Clopper-Pearson 95 per cent: 69.3-96.2 per cent); the stratum-weighted estimate is 86.5 per cent (s.e. 6.1 per cent).** All four errors are in WA: 29 and 572 are fragments, 126 has a part the source does not support, and 482 is a judgement stored as fulltext with a cut text. These four are superseded by claims 865-868. Five right claims had a locator missing part of the support, and their locators are extended. The other right claims are verified, or annotated where they were already checked. | runs kb-20261125-021654-6799dfd (draw), kb-20261125-023540-7407543 (writes), kb-20261125-023841-d9343e6 (rates, figures); `SAMPLE_VERDICTS.tsv` |
| 4. Fragments | All 20 named fragments are closed: 85, 620, 549, and the AUDIT.md list 81, 84, 171, 179, 187, 192, 213, 277, 290, 314, 424, 431, 619, 621, 622, 623, 625. Each was traced to its note row at the origin commit. 13 are superseded by 12 new whole-sentence claims, 870-881, each read at the source (84 and 85 share claim 875). 4 more point to the existing sibling claim that carries the row's statement: 623 -> 624, 290 -> 289, 314 -> 313, 431 -> 430. 3 are withdrawn because their row holds no statement: 171, 187, 549. | run kb-20261125-023542-f420d93 |
| 5. Downloads table | 0707.4654 and 1006.1632 are listed in `kb/manifests/downloads_excluded.tsv`, and `kb verify-downloads` now skips them. The table went from 765 to 763 rows. The 19 files of the two ids are byte-identical before and after, and the only problem row is still the known gr-qc/9412071. | run kb-20261125-023614-440dff2; test in kb/tests/test_inventory.py |

Figures (looked at): `figures/fig_weak_sample.png` (verdicts per stratum; rate with the CP
interval and the stratum-weighted estimate), `figures/fig_actions.png` (writes per run).

## What is here

| File | Content |
|---|---|
| `JOURNAL.md` | predictions (entry 1 before any write or draw; entry 3 before the writes) and outcomes (entries 2-4) |
| `SEED` | seed of the item-3 draw (committed in 6799dfda, before the draw run) |
| `SAMPLE_VERDICTS.tsv` | one row per drawn claim: stratum, verdict (right, right_locator, fragment, part_unsupported, wrong_label), note |
| `LEDGER.tsv` | one row per claim touched or created (72): item, action, label and status before and after, successor, locator rows, evidence, run id |
| `counts.json` | rates, Clopper-Pearson intervals per stratum, weighted estimate, action counts, downloads outcome, run ids |
| `plans/plan_item{1,1b,2,3,4}.json` | the writes, committed before their runs |
| `scripts/weak_class.py` | the query of the weak class and the seeded draw |
| `scripts/apply.py` | applies one plan in one transaction under the writer lock, with a before/after record and a hash of all other claims |
| `scripts/seed803_search.py` | store search for seed 803 |
| `scripts/downloads_item5.py` | item 5: verify-downloads with hashes before and after |
| `scripts/ledger.py` | LEDGER, counts, figures from the runs |
| `scripts/grep_src.py` | read-only search of a stored TeX source (terminal only) |
| `scripts/figstyle.py` | copied unchanged from `python/nrpic/figstyle.py` |
| `figures/` | the two figures (PNG, PDF) |

Code in `kb/`, committed with this package:
- `kbtool/claims_db.py`: `supersede`, `withdraw` and `links`, the `claim_links` table, the statuses superseded and withdrawn, and `refute` refusing a claim that is already superseded or withdrawn.
- `kbtool/claims_cli.py`: the subcommands `kb claim supersede` and `kb claim withdraw`, and links in `show`.
- `kbtool/inventory.py`: reads `manifests/downloads_excluded.tsv`.
- `kbtool/qa_figures.py`: the new statuses in the claims figure.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I tracks/kb/claims3/scripts/weak_class.py count            # the class (read-only)
python3 -I tracks/kb/claims3/scripts/weak_class.py draw --seed 20261125 --n 30 --out DIR
python3 -I tracks/kb/claims3/scripts/apply.py tracks/kb/claims3/plans/plan_item3.json --out DIR --dry-run
python tracks/kb/claims3/scripts/ledger.py --runs W2=... W3=... W1=... W4=... W5=... DRAW=... --out DIR
(cd kb && .venv/bin/python -m pytest -q tests/test_claims_supersede.py tests/test_inventory.py)
```

Do not run the apply plans again for real. The writes are done, and a second run fails by
design: the claims are already superseded. A draw from today's database also gives a different
class, because the 30 sampled claims are now read.

## Open

- The class beyond the sample. The rate implies that about 13 per cent of the 543 unread
  claims in the class are not right as worded: roughly 70 claims, with a CP range of 4-31 per
  cent [JUDGEMENT: extrapolation]. In this sample every error was a cut or a mislabel by the
  seeder in WA. Five of the 30 texts start with a conjunction or a cut ("and", "i.e.",
  "which", "see ...)"). claims_tracks' fragment query (text shorter than 25 characters) misses
  these, so a query for such starts would find candidates for the next pass. Short claims
  outside the named list that look like fragments and were not handled here: 454 ("Title |
  correct [VERIFIED] | L19"), 465, 512, 134, 193, 352.
- The successors 289, 313 and 624 stay machine-located. I checked that they carry the
  statement of their note row, but did not read them against their sources.
- O4 is solved only in part. A superseding abstract claim is now status checked. Older
  abstract-level readings stored as fulltext (448, 753, 765, 409, 447, 449, 450) are unchanged.
- gr-qc/0608095 is in the same position as the two removed ids: it is on disk, has a download
  row, is in no manifest, and its additions row is commented out as off-topic. Decision 0035
  does not name it, so it stays in the table.
- No snapshot was taken. QA_REPORT.md was not regenerated, and QA C9 will now show the
  statuses superseded and withdrawn.

## Requests

- **kb lead**:
  - Take a snapshot and run QA.
  - Send a fresh KB-G3 verifier (decision 0016 item 4) to the processed claims, including
    869, 865-868 and 870-881.
  - Tell the tracks which of their claims were superseded or withdrawn (`LEDGER.tsv`):
    - A: 29 -> 865, 126 -> 866, 81 -> 876, 84 and 85 -> 875.
    - B: 619-622 and 625 -> 870-874, 623 -> 624, 179 -> 878, 192 -> 879, 213 -> 880; 171 and 187 withdrawn.
    - C: 277 -> 881, 290 -> 289, 314 -> 313.
    - F: 424 -> 877, 431 -> 430.
    - core: 482 -> 867 (now a judgement), 572 -> 868; 549 withdrawn.
    - D: claim 373's locator was extended; no other change.
  - Update OPEN.md items O1, O2, O3 and O5 to closed.
- **orch**: decision 0035 item 5 is done. Please decide whether gr-qc/0608095 also leaves the
  downloads table. If so, it needs one line in `kb/manifests/downloads_excluded.tsv`.
