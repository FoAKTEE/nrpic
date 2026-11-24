# Reproduction of arXiv:2512.14649 and arXiv:2401.08530: state on 2026-11-24 11:10 PST

Decisions 0028, 0029, 0031, 0032. Owner Track E, packages `tracks/E-stoch-inf/repro/`.

The working note exists: `tracks/E-stoch-inf/repro/note/manuscript/main.pdf` on branch
`track/E-stoch-inf` (23 pages, REVTeX; written with the paper-writing skill; guide and
notation one level above; ledger of 113 rows, each with the fresh verifier's verdict).
The verdict per figure and statement of both papers is Table IV of the note and the
table in `tracks/E-stoch-inf/repro/note/README.md`.

Done: map and audit of the set-up (`scope`), the one-patch Langevin part (`langevin`), the
equations of both papers checked and mapped to the source (`equations`), level 2 of the
stochastic backreaction on branch `core/noise-level2` (written on Opus, reviewed on Fable:
results unchanged), fifteen card runs, the figures (`figs`), the note (`note`), a fresh
verifier (`verify`), a correction pass.

Pending: five card runs that were cut by their segment limit after preemptions and are
being continued (`continue`): the slow-roll run with dumps, the sign-flip control, the two
256-cell convergence runs, the slow-roll level-2 ablation to its end. The note marks
their rows. The update pass is prepared as `harness/workflows/batch-R3.json` (figures,
note, verifier, final correction; core closes the open steps of the level-2 review); it
starts when the sequencer of `continue` has ended (`scratch/E-stoch-inf/repro_continue_seq/`).

Open points the note states: the one-point spread of the fields is three to four times
narrower in our runs than in the published figures while the published spectra agree with
ours (cause open; a judgement from reading the figures); the level reached with a flipped
noise sign is a hundred times below the printed one; the skewness of the one-patch lapse
differs by about seven per cent between two implementations.
