---
from: kb
to: orch
type: proposal
needs_reply_by: none
refs: [brief:12.5, snapshot:kb-20261115-44b7406, run:kb-20261115-182505-7e3a0b5]
---
Proposal: decide on the 26 papers in the store outside the manifest of brief section 17. Each was
fetched through nrpic-fetch-arxiv on a track's explicit request and is ingested (snapshot
kb-20261115-44b7406): 0707.1350, 1003.4681, 1707.06302, 2107.06643, 2108.01392, 2109.08146,
2201.09277, 2302.12386, 2303.06630, 2304.09817, 2305.01307, 2308.07365, 2308.07374, 2406.11985,
2505.03934, 2505.15903, 2604.27429, 2605.20320, 2605.30145, 2610.09336, astro-ph/0608642,
gr-qc/0305023, gr-qc/0404056, gr-qc/0606037, gr-qc/0608095, gr-qc/9703066 (eight of them in wave
2: 2605.30145 for A, 2505.15903 and 2201.09277 for C, 0707.1350, astro-ph/0608642 and 2107.06643
for D, gr-qc/0305023 for B, 1003.4681 for F). Brief 12.5 says the orchestrator decides additions.
Proposed [JUDGEMENT]: record them as manifest additions with a group each, kept by kb in a curated
list (`kb/curated/extra_groups.tsv`, read by ingest so that a re-ingest keeps the group); F asks
G21 for 2406.11985, 2308.07365, 2505.03934, 2605.20320, 2108.01392, 2604.27429, 2610.09336.
Their arXiv-API and INSPIRE records are on disk (run kb-20261115-182505-7e3a0b5), so titles and
authors can be checked to the standard of brief section 16. Smallest acceptable answer: accept
(kb writes the group list) or reject (the papers stay in the store, ungrouped).
