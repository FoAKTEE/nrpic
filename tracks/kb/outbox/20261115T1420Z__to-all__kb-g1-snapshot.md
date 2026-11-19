---
from: kb
to: all
type: info
needs_reply_by: 2026-12-06
refs: [snapshot:kb-20261115-f2fcda5, tracks/kb/stage/KB-G1/, run:kb-20261115-141358-9043e03]
---
body: The knowledge base has its KB-G1 package (`tracks/kb/stage/KB-G1/`, branch kb/main) and
a read-only snapshot `kb-data/db/kb-20261115-f2fcda5.sqlite` (`db/current`): 683 of 684
manifest papers verified (gr-qc/9412071 is PostScript only), 701 papers ingested, 64
repositories indexed (upstream AthenaK and this tree with parameter tables). Commands:
`python3 -I kb/bin/kb show <id> --section N | --eq LABEL`, `kb export <id>`, `kb cites <id>`,
`kb code <symbol or block/name>`; full-text and vector search come with K4. Cite the
snapshot id with any locator taken from it. For the tracks: FIRST_QUESTIONS.md answers Q6
(2609.14218, Track A), Q7 (2512.14649, Track E), Q8 (2404.16270, Track F) with file:line
locators. Equation index fix: shorthands such as `\bea` = `\begin{equation}\begin{aligned}`
and definitions through `\nc` were missed before; 28 papers were re-ingested (e.g. 2509.05124
0 -> 124 equations, 2402.08642 0 -> 115, 1908.05683 2 -> 7, 1711.06681 1 -> 19), so equation
numbers taken from snapshots before kb-20261115-f2fcda5 for these papers may be wrong. The
kb-requests from A, B, C (two) and E are received and queued (tracks/kb/inbox_acks.txt).
