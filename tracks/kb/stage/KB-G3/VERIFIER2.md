# VERIFIER report 2: gate KB-G3 of the knowledge base (kb), 2026-11-25

Verifier: a fresh kb helper session of batch 15 that wrote none of the packages checked
(claims3, lead_b13, lead_b15) and did not read REVIEW-wave3.md, the claims3 LEDGER or either
earlier sample's verdict notes before giving its own verdicts. Of the first verifier's report
it read only the summary table (VERIFIER.md L1-34). Gate criterion (brief 12.10, L1458):
"every statement in the evidence queue that bears on G1 of the six tracks has been
processed". Everything is read from the frozen snapshot `kb-data/db/kb-20261125-2f97258.sqlite`
(sha256 2f97258cf6c1..., the target of db/current; run kb-20261125-041310-20371de), opened
read-only and immutable, and from the raw sources under `kb-data/raw/arxiv/`. Own code in
`verifier2/scripts/`. Predictions and seed 20261126 were committed before the draw
(`verifier2/JOURNAL.md` entry 1, commit d4741a70b). No card time.

Verdict words: SUPPORTED (as worded, at its locators), NOT SUPPORTED, LOCATOR WRONG; for
superseded or withdrawn claims TAKEN OUT RIGHTLY or WRONGLY; for seeds that are questions or
instructions PROCESSED RIGHTLY or not. "Right as worded" (item 2) means every statement of the
text is said by the source at its locators. A cut sentence whose meaning survives counts as
right. A pointer or fragment without a statement, a wrong number or attribution, or a judgement
stored under a support label counts as not right. Borderline cases are flagged, and the rates
are given with them counted both ways.

## Summary

| Item | What was checked | Result | Verdict |
|---|---|---|---|
| 1 | 61 claims written or changed since the first verifier, re-read at their locators | 60/61 right: 28 supported, 25 taken out rightly, 7 processed rightly; 1 not supported (781); 0 locator wrong | CONFIRMED, except 781 |
| 2 | new stratified sample of 40 (seed 20261126) | P checked by a person 12/14 = 85.7 % (CP 95 % 57.2-98.2); M machine-located 10/13 = 76.9 % (46.2-95.0); Q rest of the weak class 12/13 = 92.3 % (64.0-99.8) | rates below; the package states the limit, but quotes a mixed-class rate that is higher than the machine-located rate |
| 3 | the seven criteria of KB-G3 (CHECKLIST C1-C7) | C1-C7 met, with reservations on C1 and C5 | PASS WITH RESERVATIONS |

Runs (all scouting, processors, manifests under `tracks/kb/runs/`):
kb-20261125-041256-d4741a7 (failed: my path error, before any draw);
kb-20261125-041310-20371de (strata, draw, item-1 list, C1 recount, snapshot hash);
kb-20261125-042218-7b7af60 and kb-20261125-042240-6c19d72 (tally and figures; the second after
a layout fix, same numbers); kb-20261125-042327-f947572 (C2: `kb status`, `kb show`, unlocated
counts). Figures, both looked at: `verifier2/figures/fig_item1.png`, `fig_sample.png`.

## 1. Claims written or changed since the first verifier (61)

Verdicts per claim with the lines that decide them: `verifier2/verdicts/item1.tsv`.

| Group | Claims | Result |
|---|---|---|
| New claims 862-881 | 20 | 20 SUPPORTED. 862: L443 of 1305.2619 and D's run D-bh-dress-20261115-145636-5259f48 (2.5897, 0.0922). 863: my grep of 2611.12831 main.tex, the only .tex file, finds 0 hits for "cosmolog" and 0 for "periodic". 867: I compared L588-591 with the Catmull-Rom weights term by term; the judgement label is right. 869: all 13 locators read; my own full-text search finds the same 20 papers as claims3's search. 877: L361-362, and F's run F-hills-20261115-045435-f62d553 gives D/r_t of 4.116 and 5.810 |
| Superseded and withdrawn | 25 | 25 TAKEN OUT RIGHTLY: each old text is a fragment, a pointer, a cut text or an unsupported part, and each successor is right (29->865, 126->866, 482->867, 572->868, 682->862, 81/84/85->876/875, 179/192/213/277->878-881, 424->877, 619-622/625->870-874, 290/314/431/623->siblings) |
| Siblings receiving `--to` | 4 | 289, 313, 430, 624 SUPPORTED. Wording issues: 313 keeps locator debris; 430 is cut at both ends ("lines 110, 246): ..." and a trailing "(") |
| Seeds and named claims | 12 | 803, 790, 805, 452, 714, 804, 809: PROCESSED RIGHTLY. 409, 447, 449, 450: SUPPORTED, but carry a fulltext label on abstract readings (OPEN O4). **781: NOT SUPPORTED as worded** |

Claim 781 (fulltext/checked) reads "so deep refinement slows everything down; whether NRPIC
keeps this is [TO VERIFY]". The answer the lead found is right: 2611.12831 L75 says
"Particles and fields share a common global time step", and L676 agrees. But the first clause
is the brief's inference, the text still carries [TO VERIFY], and the lead's own verify event
says that only the time-step part is supported. This is the defect class of 482 and 572 and
should be superseded by a whole-sentence claim.

Other reservations from item 1:
- 804 (an instruction listing six topics) became fulltext/checked, while 805 (also an
  instruction) stays to_verify. The two are treated inconsistently.
- 877 puts a paper statement and F's run numbers under one fulltext label.
- 864 lists "Jena" among the authors of 2602.06961.
- 741, which I spot-checked under 804: its stored locator L64-67 does not hold "near-extremal".
  The supporting line is Spin_PBH.tex L1206.

## 2. New stratified sample of forty

Population: live claims with the label fulltext, abstract or title_only and status checked,
located or partial (694 claims). From it I removed the claims already re-read: item 1 (29), the
first verifier's verdict files (38) and claims3's sample (26). That leaves 600 claims, so the
sample is new information.

The strata are disjoint. They were defined in JOURNAL entry 1 before the draw:
- **W, the weak class.** Labels set by a pipeline step (auto, kb-claims_tracks, kb-claims_brief,
  12.8 map) on claims that carry no event of a person's reading.
- **M, located by machine.** The part of W whose label was set by auto. It is claims3's WA, and
  has 402 claims.
- **Q, the rest of the weak class.** Claims3's WQ, WB and WM: 127 claims.
- **P, checked by a person.** Status checked and not in W: 71 claims.

Allocation was 14 / 13 / 13. Verdicts: `verifier2/verdicts/sample_verdicts.tsv`. Numbers:
run kb-20261125-042240-6c19d72, `tally.json`.

| Stratum (size) | Right as worded | CP 95 % | Not right | Borderline (counted as in column 2) |
|---|---|---|---|---|
| P checked by a person (71) | 12/14 = 85.7 % | 57.2-98.2 % | 223 a pointer ("Summary and features: lines 62-103"), verified by audit P2; 574 a noun phrase whose predicate "the need for further investigation of" (L1140) was cut, verified by the claims_tracks audit | 102, 391 counted right (cut but readable) |
| M located by machine (402) | 10/13 = 76.9 % | 46.2-95.0 % | 145: gives the mean and median \|v_pec\|/c of 0.4-0.5 (2605.04487 L2400-2402) as a maximum ("up to"); 462: fragment, subject cut; 553: a [JUDGEMENT] stored as fulltext (the algebra is right, I redid it) | 462 counted not right, 521 counted right (table-row format) |
| Q rest of the weak class (127) | 12/13 = 92.3 % | 64.0-99.8 % | 169: "2507.18312 says no for spherical shells" with the question (L240) cut away | 428 counted right: the author order "Ficarra, Ciarfella, Lousto" differs from the paper's (Ciarfella first, TBH.tex L37-47) |

Stratum-weighted estimates:

| Population | Estimate (s.e.) | All borderline cases right | All borderline cases not right |
|---|---|---|---|
| W = M + Q (529 claims) | 80.6 % (9.3 %) | 86.5 % | 72.9 % |
| All 600 claims | 81.2 % (8.2 %) | 86.4 % | 72.7 % |

Pooled with claims3's own sample of the same classes (its verdicts, not mine), and therefore
not independent of claims3:

| Class | Right | Rate (CP 95 %) |
|---|---|---|
| Machine-located (claims3's 22 WA claims plus my 13) | 28/35 | 80.0 % (63.1-91.6 %) |
| Rest of the weak class (claims3's 8 plus my 13) | 20/21 | 95.2 % (76.2-99.9 %) |

Expected number of claims not right as worded among the 529 unread claims of W: about 86,
with a range of 34-179 from the intervals [JUDGEMENT: extrapolation]. The package expects about
70 (21-167) among its 543.

**Does the package state the limit of the machine-located claims honestly?** Mostly yes:
- OPEN.md O7 and EVIDENCE.md give the size of the class, the sample, the interval and an
  extrapolated count. They label the extrapolation a judgement. They say that all errors were
  the seeder's cuts (WA), and they tell readers to read the locator of a located or partial
  claim before citing it.
- Two things are missing. First, the headline 86.5 % is the rate of the mixed class. The rate of
  the machine-located stratum alone is lower: claims3's own WA count is 18/22 = 81.8 %, pooled
  with mine 80.0 %. It is not written down.
- Second, the package and its risk register imply that "checked" means read and right. My P
  stratum has 2 wrong claims in 14. Both had been verified by audits that confirmed that the
  passage supports the claim, not that the text states something. The first verifier found
  17/18 in the same class, so the pooled P rate is 29/32 = 90.6 %.

## 3. Criteria of KB-G3 (CHECKLIST.md C1-C7; brief 12.10, decision 0012)

| # | Criterion | Verdict | My evidence |
|---|---|---|---|
| C1 | Every statement in the evidence queue that bears on G1 has been processed | **MET under the package's reading (SCOPE.md), with reservations** | My own SQL (run ...041310, `queue.json`): A 1/1, D 8/8, F 2/2, core 3/3 to_verify claims carry a processing event, and so do 12 of the 17 brief claims; B, C and E have none. The 5 without an event are exactly 806, 807, 810, 811 and 812, which decision 0035 item 5 (L28) rules do not bear on G1. My label counts per track and status counts equal the EVIDENCE.md table line by line. Reservations: (a) 781 is processed but its text is not right as worded; (b) 12 claims carry the label abstract with no locator and only their seed event (706, 709-712, 715, 773, 774, 794-796, 844; run ...042327, `unlocated.json`); 773 (A's threshold paper 2609.14218) and 774 (NRPIC capabilities) bear on track work and fall outside the package's to_verify reading; (c) "processed" counts a machine-located claim whose locator resolves, which is a [JUDGEMENT] of SCOPE.md: about 1 in 5 of those claims is not right as worded (item 2) |
| C2 | Tracks read read-only; `kb` opens db/current by default | **MET** | `kb show 2611.12831` ends with "[kb snapshot kb-20261125-2f97258]"; db/current resolves to that file; the text views default to db/current (`kb/kbtool/cli.py` L312, `paths.py` L65). Note: `kb status --json` names `kb.sqlite` as "database" next to the snapshot, which a reader may misread |
| C3 | Snapshot at the end of the stage; its id in the package and with every locator | **MET** | sha256 2f97258cf6c15d29... (my hash, run ...041310); EVIDENCE.md L4-6 names it; my recomputed counts (762 papers, 881 claims, statuses, labels per track) all equal the package's |
| C4 | Package documents of decision 0012 | **MET** | STAGE_REPORT, EVIDENCE, OPEN, CHECKLIST, REVIEW, SCOPE, VERIFIER present in `stage/KB-G3/` |
| C5 | Verifier subagent (fresh context) wrote its report; numbers recomputed | **MET with this report** | VERIFIER.md (batch 11) and this VERIFIER2.md; I recomputed the C1 table, the weak-class count (claims3's query today 548; mine 540 = 543 minus the three siblings 289, 430, 624, explained in JOURNAL entry 3) and the snapshot hash. CHECKLIST marked C5 PASS before this report existed |
| C6 | Null results and failed runs on record | **MET** | the manifest of kb-20261124-233445-89478ae has status failed; my own failed run kb-20261125-041256-d4741a7 is on record with its cause (JOURNAL entry 2) |
| C7 | STATUS, JOURNAL, HANDOFF current | **MET (by date)** | all three last changed in dc28b4ee5 (2026-11-24 19:44 PST, lead of batch 15); I did not judge their content |

## What could not be checked

- The tracks' rows behind the withdrawn claims 171, 187 and 549. `git show` at the commits named
  in the withdrawal events returned nothing, and I judged from the stored texts alone.
- The repository half of 596 (`paper/sections/method.tex` L229 at the time).
- The INSPIRE record ids of 809. I read only the status fields.
- Two of the ten locators of 739.
- The brief's line 426 (context of 781), which lies outside the line ranges this session may read.
- Retrieval and parse rate. They are not KB-G3 criteria, and the first verifier covered them.
- The clean-export re-verification (`nrpic-stage verify`), which I did not re-run.
- The weak class beyond the sample. The sample sizes per stratum (13-14) give wide intervals.

## The three weakest points

1. **Machine-located claims are right as worded about 4 times in 5, not 6 in 7.** My sample has
   10/13; pooled with claims3's WA it is 28/35 = 80 % (63-92 %), over 402 unread claims. The
   package's headline 86.5 % mixes this class with better ones. A track that cites a located
   claim without reading it is wrong about once in five.
2. **"Checked" is not a guarantee.** Two of 14 person-checked claims are a pointer and a
   fragment that audits passed, and 781 was verified although its text is not the source's.
   The audits judged whether the passage supports the claim, not whether the claim's text
   states something.
3. **Label hygiene is uneven.** The fulltext label appears on abstract readings (O4, still
   open), on an instruction (804, while 805 stays to_verify), on a judgement (553) and on mixed
   paper-and-run content (877). In addition, 12 claims labelled abstract have no locator at all
   (773 and 774 bear on track work). None of this breaks C1 as scoped, but each weakens what a
   label tells a reader.

## Recommendation

**PASS WITH RESERVATIONS.** The criterion as the package reads it (SCOPE.md) is met: I
recounted the queue independently and found no unprocessed to_verify claim that bears on G1.
The new and changed claims are right (60/61), and the documents, snapshot and records are in
order. Reservations, to be closed in service mode:
- supersede 781, 223, 574, 553, 145, 169 and 462 with whole-sentence, correctly labelled claims;
- write the machine-located stratum's own rate (about 80 %) next to the 86.5 % in OPEN O7 and
  EVIDENCE;
- process or relabel the 12 abstract-labelled claims without a locator, first 773 and 774;
- fix 741's locator (L1206) and 428's author order;
- treat instructions 804 and 805 alike.
