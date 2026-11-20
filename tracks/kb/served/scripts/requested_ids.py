"""The arXiv identifiers named in the kb-requests of wave 1 (read from the request files).

Each entry: request key -> list of (arXiv id, what the requester wants: 'index' = already
read by the track, index it; 'fetch' = fetch and index; 'check' = check locators into it).
The ids are copied from the request files named in REQUEST_FILES (git branch:path).
"""

REQUEST_FILES = {
    "A": "track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T1320Z__to-kb__ingest-s1-references.md",
    "B": "track/B-emd-gw:tracks/B-emd-gw/outbox/20261115T1340Z__to-kb__track-b-sources.md",
    "C1": "track/C-sidm:tracks/C-sidm/outbox/20261115T1320Z__to-kb__index-locators-typos.md",
    "C2": "track/C-sidm:tracks/C-sidm/outbox/20261115T1320Z__to-kb__literature-fetch.md",
    "D": "track/D-bh-dress:tracks/D-bh-dress/outbox/20261115T1510Z__to-kb__dress-and-coupling-sources.md",
    "E": "track/E-stoch-inf:tracks/E-stoch-inf/outbox/20261115T1410Z__to-kb__errata-s11-references.md",
    "F1": "track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-kb__index-hills-sources.md",
    "F2": "track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-kb__locators-wanted.md",
    "core": "core/nrpic:tracks/core/outbox/20261115T1510Z__to-kb__paper-metadata-and-philox.md",
}

IDS = {
    # A: twelve key references of S1 (refs line) + five to ingest
    "A": [(i, "index") for i in (
        "2609.14218", "2610.23218", "1609.01588", "1707.03595", "2211.13950", "2507.18312",
        "2508.10070", "2109.04896", "2306.11810", "2605.04487", "1611.07906", "1901.04498")]
         + [(i, "fetch") for i in ("1708.09143", "2608.13206", "2403.15126", "2605.30145",
                                   "1810.03490")],
    # B: eleven read + 2003.08014; fetch list of item 2
    "B": [(i, "index") for i in (
        "2403.15126", "2605.04487", "2111.09163", "1604.06065", "1704.04307", "2608.13206",
        "2610.23218", "2207.03125", "2501.13046", "1505.04756", "2010.12584", "2003.08014")]
         + [(i, "fetch") for i in ("2212.00425", "2312.12499", "1704.03500", "2012.14016",
                                   "2610.08045", "1708.09143")],
    "C1": [(i, "index") for i in ("2108.11967", "gr-qc/0601112", "2009.08163", "2601.17117",
                                  "astro-ph/0110561", "1101.3097")],
    "C2": [(i, "index") for i in ("2601.17117", "2506.17641", "2108.11967", "2602.17487",
                                  "gr-qc/9804040", "gr-qc/0107076", "1409.5176")],
    "D": [(i, "index") for i in ("1305.2619", "1707.06302", "1901.08528", "1805.09034")],
    "E": [(i, "index") for i in ("2512.14649", "2401.08530", "2502.06783", "2610.32592",
                                 "2606.14853", "1308.4754", "2206.11234", "2405.10692")],
    "F1": [(i, "index") for i in ("2406.11985", "2308.07365", "2505.03934", "2605.20320",
                                  "2108.01392", "2604.27429", "2610.09336", "2404.16270",
                                  "2402.02178")]
          + [(i, "check") for i in ("0911.1136", "1201.4794", "1804.02911", "0710.0879",
                                    "1004.1353")],
    "F2": [(i, "index") for i in ("0912.2920",)],
    "core": [(i, "index") for i in ("2611.12831",)],
}
