# Search log of work package "novelty" (2026-11-19)

All requests were generic physics queries: no project, person, repository or user detail.
Times: UTC for INSPIRE (as recorded), PST (UTC-8) for the rest.

## INSPIRE (inspirehep.net literature API)

Made only with `python3 -I harness/bin/nrpic-fetch-arxiv --inspire-query "<query>" --size 25`,
one request at a time (the command holds the machine-wide INSPIRE lock and keeps three seconds
between requests), driven by `scripts/run_queries.py` from the lists `queries_1.txt` to
`queries_4.txt` of this directory. `query_log.tsv` has one line per request: label, UTC time,
total hits, status, the record written (`kb-data/meta/inspire/query/<sha16>.json`, untrusted
data, only parsed as JSON, not committed), and the query. 61 requests:

| Batch | Time (UTC) | Labels | What |
|---|---|---|---|
| pre | 15:33-15:34 | pre_k1, pre_c1, pre_k2 | first trials: a quoted-phrase title query (0 hits); `refersto:arxiv:` (not understood by INSPIRE, matched everything, discarded; later citation queries use `refersto:recid:<record>`); the coupling titles (7 hits) |
| 1 | 15:35-15:38 | s4_c1-c2, s4_k1-k6, s5_k1-k6, s7_k1-k7, b_k1-k7 | first pass over the four items |
| 2 | 15:40-15:42 | s4_c3-c5, s4_k7-k11, s5_c1-c2, s5_k7-k11, s7_k8-k12, b_k8-k14 | citation queries of the closest papers found in batch 1 (records 2633033 = 2302.07878, 2642121 = 2303.07980, 1942269 = 2110.05982, 1369323 = 1505.02959, 2765845 = 2403.03470, 1818072 = 2009.08968, 1674551 = 1805.09034) and narrower topic queries |
| 3 | 15:42-15:43 | b_a1, b_a2, b_k15, s5_k12, s7_k13, s4_k12 | the two authors of 2611.12831 since 2025; remaining gaps |
| 4 | 15:44 | s8_k1 | one limited query for the S8 sentence of line 441 |

Responses are capped at 25 records sorted by date. Five queries had more hits than that and were
read only for their 25 most recent: s5_k1 (47), s5_k6 (31), s5_c2 (34), b_k4 (79), b_k12 (34);
s7_k5 returned exactly 25 of 25. Record numbers for `refersto:recid:` came from the hits of
earlier queries or from `kb-data/meta/inspire/<id>.json`.

## Web (generic search engine), 07:33-07:43 PST

1. primordial black hole formation neutrinos free-streaming numerical relativity kinetic
2. numerical relativity test cosmological coupling of black holes expanding universe horizon mass
3. Burnett conjecture numerical simulation high-frequency gravitational waves massless Vlasov
4. numerical relativity binary black hole merger particle dark matter collisionless environment simulation
5. Burnett conjecture without symmetry high-frequency limit Einstein vacuum null dust proof
6. "cosmological coupling" black holes numerical simulation horizon mass expanding dust Einstein equations
7. black hole in matter dominated universe numerical relativity accretion collisionless particles horizon growth
8. primordial black hole formation threshold neutrinos anisotropic stress free streaming radiation two components
9. numerical relativity backreaction high frequency gravitational waves Green Wald effective stress energy traceless simulation
10. black hole embedded in expanding dust universe numerical relativity simulation mass of black hole does not grow with scale factor
11. "Einstein-Vlasov" binary black hole simulation dark matter halo full general relativity particles
12. dark matter spike around binary black hole general relativistic simulation test particles numerical relativity metric

Web results were used only as leads: every paper named in NOVELTY.md was then read in its TeX
source in the store or, where marked, in its INSPIRE abstract. Leads from the web that the
INSPIRE queries also returned: 2303.07980, 2110.05982, 2403.03470, 2009.08968, 2404.07659,
2402.17530, 2206.12318, 2506.21779, 2210.09254, 2311.18156, 2409.01937, 2507.18934,
2402.13762, 1306.4055, 1903.01490, 2407.14549, 2410.10459, 2306.11588.

## Knowledge base

`kb/bin/kb search --text-only` (BM25 over the read-only snapshot `db/current`,
kb-20261115-a848a06; the vector model is not installed in this worktree): five queries for S5
and line 410 (07:31), four for the four items (07:44). Full-text regular expressions over the
TeX sources of the store with `scripts/locate.py` and the spec files `specs/*.txt`, and with
`rg` over `kb-data/raw/arxiv` for the horizon-mass and neutrino-decoupling numbers of line 410.

## arXiv sources fetched

`python3 -I harness/bin/nrpic-fetch-arxiv`, serially, two calls: 2403.03470, 2009.08968,
2404.07659 (07:39 PST); 2406.11417, 2606.26532, 2607.09285, 2508.13294 (07:42 PST). All
extracted into `kb-data/raw/arxiv/<id>/<v>/src` by the command; read, never executed. Nothing
was written to the knowledge-base database.
