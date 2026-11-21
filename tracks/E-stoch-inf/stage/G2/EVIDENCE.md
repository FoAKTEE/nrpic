# EVIDENCE of E-stoch-inf at G2 (so far; lead of batch 5, 2026-11-21)

| Item | Evidence | Status |
|---|---|---|
| USR scouting pair at 256^3 (core_scalar-3) | U256 E-20261121-075255-8cf90e7, U256m E-20261121-085221-1f579fe, pair analysis E-20261121-101756-6bffd0c: odd part per mode 1.09e-4 (k <= 32 dk), all modes <= 4.5e-3; U-A0, U-A1, U-A3 pass (usr/README.md) | scouting; release repeat queued |
| USR ladder 64^3/128^3 (k_max/dk = 8) | E-20261120-222621-ba66218, analysis E-20261121-075307-4542ce1, floor E-20261121-080134-a0cc3eb (even halving 3.987-4.001) | scouting |
| Window sensitivity L9 (U-W) | E-20261120-222424-0eb754b, analysis E-20261121-154733-0d1fbda, lead's rerun E-20261121-203008-f104a3e (identical): shift <= 1.9e-4 to k_max/2, <= 9.1e-3 to k_max | criterion U-W met by the scan |
| Strict A4 against resolution (SR) | E-20261121-131000-b23055b, analysis E-20261121-152010-371d5f1, rerun E-20261121-203016-7209255, own code E-20261121-203540-a9b5d10: holds at >= 12.8 cells, fails at <= 10.7 | supports A4' premise |
| Restart of the production deck | E-20261121-202941-da16544: byte-exact | R0 held |
| Criteria fixed before production | spec/scope/SCOPE.md 4c, commit 43dcc9cc (12:28 PST) before the first g2prod submission (12:29 PST) | done |
