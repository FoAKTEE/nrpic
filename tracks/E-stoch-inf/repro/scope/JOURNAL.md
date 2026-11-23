# JOURNAL of package repro/scope (Track E, batch R1, 2026-11-22)

Reproduction of arXiv:2512.14649 (P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`, read whole,
791 lines): map of every figure, table and quantitative statement to our runs (`REPRO_MAP.md`), audit
of the set-up (`SETUP_AUDIT.md`), the missing card runs (`queue.txt`, `CARD_PLAN.md`), the request for
backreaction level 2 (`outbox_draft/`). Predictions are written here before each run.

## Entry 0 (2026-11-22 18:10 PST): processor smoke test of the two decks "as in the paper"

Decks `inputs/sr_paper.athinput` and `inputs/usr_paper.athinput` differ from the decks of the
registered runs P256 / P256v6 (`ladder/inputs/sr_base.athinput`) and U256ap
(`g2prod/inputs/usr_prod.athinput`) only in output options (diff in the deck headers): dump cadence,
`dump_magnitudes = true`, a restart output (SR), `con_signed` (SR). Before any card time, a 32^3
processor run of each (nmax2 = 64, 8 cycles, release processor build core-v0.6).

Prediction S0: both runs end with exit status 0; each writes two NRSFDMP2 dumps (t = 0, t = 0.25 or
0.26) whose variable list holds the 27 names phi, Pi, chi, K, alpha, gt_ij (6), At_ij (6), H, Mx, My,
Mz, E, Hmag, Mmag, MBx, MBy, MBz; Hmag > 0 everywhere; the record `.sf.con.hst` has a line per cycle.
Refuted by: a parse error, a missing variable, a dump layout other than NRSFDMP2, or Hmag <= 0 at a cell.
