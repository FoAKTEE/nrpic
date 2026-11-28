# g3/scope_review: independent review of Track D's G3 scope before its runs

Helper package of D-bh-dress (batch 34). Reviews `scope/SCOPE_G3.md` against decision 0045 item 2 and
the G2 reservations (`stage/G2/GATE_REVIEW.md` section 5). The scope text is changed by the lead, not here.

Contents
- `SCOPE_REVIEW.md`: findings ranked (blocking / should change / note), evidence with run ids, proposed
  wording, verdict line.
- `JOURNAL.md`: predictions before every calculation and their outcomes.
- `tools/make_decks.py`: writes the G-8, G-12, G-16 decks as the scope describes them (into `decks/`).
- `tools/g2_analogs.py`: the G3 criteria of Claim G applied to G2's registered outputs (one factor coarser).
- `tools/dress_model.py`: exact LTB profile, the lead and the proper-time map of Claim D.
- `tools/figstyle.py`: copy of `python/nrpic/figstyle.py`.

How to rerun (from the worktree root; run ids in JOURNAL.md)
- `python3 tracks/D-bh-dress/g3/scope_review/tools/make_decks.py` then, per deck,
  `/data/haiyangw/nrpic/.work/build_cpu_v08/src/athena -i <deck> -m` inside an empty output directory.
- `harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/D-bh-dress/g3/scope_review
  --purpose ... -- python3 tracks/D-bh-dress/g3/scope_review/tools/<script>.py '$NRPIC_RUN_DIR'`

Requests: see the end of SCOPE_REVIEW.md.
