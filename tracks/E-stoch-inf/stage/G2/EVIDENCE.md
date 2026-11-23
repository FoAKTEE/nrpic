# EVIDENCE of E-stoch-inf at G2 (lead of batch 10a, 2026-11-22)

Criteria: `spec/scope/SCOPE.md` 4c (fixed before production). Predictions: `g2prod/JOURNAL.md`
entries 1 and 3; outcomes entry 2. Release card build core-v0.6 throughout.

| Item | Runs | Result | Status |
|---|---|---|---|
| Timing T | E-20261121-202929-43dcc9c; analysis E-20261123-015014-b4ecd4e | 1.374 / 2.522 / 4.300 s per step at 256/320/384^3; peak 19589 / 36393 / 61077 MiB | prediction held on time; memory band at 384^3 missed low |
| SR 256^3 on the release (G1 reservation 2) | P256v6 E-20261121-202935-31520bc; same analysis | records identical digit for digit to E-20261115-172618-f948386; A2 1.2078e-4 | held |
| USR seed A, s = +-1 | E-20261121-211214-0377aab, E-20261121-214629-da64fb7; analysis E-20261123-014858-8e72d4c | identical per mode to the scouting pair; U-A2' 1.089e-4; U-A0..U-A3 pass | PASS |
| USR seed B (U-S) | E-20261122-033244-564627b, E-20261122-071038-d9f933b; analysis E-20261123-021730-a421438 | U-A2' 1.087e-4; one-point rms 0.89411 (lattice 0.89366); skewness 0.004, -0.001 | PASS |
| Resolution U-R | E-20261122-023427-0ac3f0b, E-20261122-110042-ffcb4b3; analysis E-20261123-020751-0baf597 | factor 2.10; shell power 1.2e-4 / 4.6e-3; even/odd 1.1e-4 | PASS (predicted band of the factor missed) |
| Halving U-A4'(a), (b) | E-20261122-113320-9bbb52b, E-20261122-152116-0542096 | H 3.992-4.042 (9 dumps); M 10 of 11 within, 3.925 at cN 6.52 | FAIL (one dump of M) |
| Records U-A4'(c) | the nine proper chains | H' <= 3.0e-12, M <= 0.025 | PASS |
| Control U-A4'(d) | E-20261122-190341-0419be6 | odd part of H 1.19e5 times the proper one | PASS |
| Window U-W | E-20261121-154733-0d1fbda, rerun E-20261121-203008-f104a3e | shift <= 1.9e-4 to k_max/2 | met |
| SCOPE 4c judge | E-20261123-024359-5dc3213 (figures fig_g2_*.png), check E-20261123-024806-3c0e139 | common-mode floor of the odd part scales as s^2 (ratio 4.16) | finding |
| Restart of the deck | E-20261121-202941-da16544 | byte-exact | held |
