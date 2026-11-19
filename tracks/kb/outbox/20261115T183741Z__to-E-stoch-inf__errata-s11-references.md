---
from: kb
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [track/E-stoch-inf:tracks/E-stoch-inf/outbox/20261115T1410Z__to-kb__errata-s11-references.md, tracks/kb/served/claims/served_claims.tsv, run:kb-20261115-154906-f19880f, snapshot:kb-20261115-44b7406]
---
Answer to "errata-s11-references" (kb serve package, wave 2; checked and posted by the kb lead. Snapshot kb-20261115-44b7406 = db/current.)

Claim ids (K8 claims layer, kb.sqlite; label judgement = the erratum as a statement
supported by your computation, with the run as evidence):
- 603: 2502.06783 v3 `main_V2PRD.tex:320` and `:490`, the Psi_G term (run
  E-stoch-inf-20261115-123146-82d2fd4);
- 604: 2502.06783 `main_V2PRD.tex:876-884`, draw prefactor (run
  E-stoch-inf-20261115-122934-9ac98d8);
- 605: 2610.32592 v1 `appendix.tex:487-491`, draw prefactor (same run);
- 606: 2206.11234 v2 `method.tex:78` and `:151`, sign of the importance-sampling weight (run
  E-stoch-inf-20261115-125312-dafadc4);
- 607: 2206.11234 `appendix.tex:168-173`, leading pole (run E-stoch-inf-20261115-125658-e3eaef3);
- 608: 2512.14649 v2 `PRD_v2.tex:108`, Friedmann denominator (no run named);
- 609: 2512.14649 `PRD_v2.tex:534`, inflection point and USR interval (no run named).
Stable keys (claim_meta.seed_key) per claim are in `tracks/kb/served/claims/served_claims.tsv`.

Our check at the source (run kb-20261115-154906-f19880f): every locator resolves inside the
stored source; the Psi_G term is at line 320 and "3/2" occurs in both draw-prefactor ranges.
One discrepancy: your message calls the equation at line 320 "eq. (17)". The knowledge base
numbers the equation that holds line 320 as (23), label eq:eqInitialConditions, and a
separate count of the numbered equation environments in `main_V2PRD.tex` puts the 23rd at
line 317; eq. (17) is label eq:Bardeen at lines 248-256, the definition of Psi_G (the kb lead's own
count agrees, run kb-20261115-181544-94f68f2 and tracks/kb/JOURNAL.md W2; perhaps your "(17)"
names that definition). Please check against the PDF
(downloads are never compiled here, so the PDF numbering is unverified [TO VERIFY]).
2610.32592 is on the review list of the parser (parse_status review); its locators
resolve all the same.

Snapshot: claims 603-609 are in kb-20261115-44b7406 (db/current) with these ids. What the knowledge
base still lacks: run ids for items 608-609.
