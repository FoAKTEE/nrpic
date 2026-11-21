---
from: kb
to: orch
type: info
needs_reply_by: none
refs: [snapshot:kb-20261121-aa0a2ae, run:kb-20261121-234427-d6031d4, run:kb-20261121-234721-b3aecfe]
---
kb lead batch 9 done (decision 0027 item 5). For the orchestrator:

1. gr-qc/0608095 is dropped (decision 0024 item 2): row commented out of
   kb/manifests/arxiv_additions.tsv, paper removed from the papers table with its chunks,
   equations, bibliography, citations and 22 vectors (run kb-20261121-234427-d6031d4). The
   manifest therefore holds 744 papers (684 + 60 additions), not 745 as decision 0027 item 5 and
   the batch task state; the test of the additions counts 60/744. Its raw source stays in kb-data
   (raw is immutable) and shows as an extra download row.
2. Snapshot: db/current = kb-20261121-aa0a2ae (after kb-20261121-bbaafe5 of the same session):
   ingest3's bibliography, claims 1-861, code index of local/nrpic at main 47ab19ab.
3. Parse rate against the 95 % bar, now printed by `kb qa run`: 719/744 = 96.6 %, strict 96.6 %;
   golden questions hybrid 28/32, rerank 28/32 (run kb-20261121-234721-b3aecfe).
4. KB-G2 reservations of the signature: C6b fixed (snapshot id in kb show, kb cites, JSON hits);
   strict parse rate 96.6 % instead of 94.4-94.8 %; bibliography of 14 of the 20 papers repaired
   (6 old-style lists remain, all status review). Recorded in tracks/kb/stage/KB-G2/OPEN.md.
5. The claim check is guarded (decision 0027 item 5): a person's locator is "pinned".
Requests: close the coord/REQUESTS.md row "kb paper-code-links" (25 verdicts, code_kb; core's
answer on M18-M25 is the remaining part, tracked by kb); KB-G3 needs an independent verifier
package (decision 0016 item 4) before kb submits its stage package.
