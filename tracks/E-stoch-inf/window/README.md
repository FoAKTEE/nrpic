# window: sensitivity of the USR spectrum to the window function (E-stoch-inf, test L9)

Second G2 criterion of Track E, "sensitivity to window-function parameters"
(`coord/CHARTER.md` 9.8; test L9 of `../codebase/DESIGN_REVIEW.md` 8.1). Status: inputs and
predictions written (`JOURNAL.md` entries 0, 1); reference, card job and analysis follow.

## Contents

| Path | What |
|---|---|
| `inputs/usr_256.athinput` | copy of `../usr/inputs/usr_256.athinput` (USR production set-up); the list overrides mesh, nmax2, mode file, s, sigma and the mode scale |
| `inputs/sr_base.athinput` | copy of `../ladder/inputs/sr_base.athinput` (slow-roll contrast) |
| `inputs/card_window.list` | the card job: 10 USR runs at 128^3 (5 windows, +-1) and 6 slow-roll runs at 64^3 |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `JOURNAL.md` | predictions and outcomes |

## Requests

None yet.
