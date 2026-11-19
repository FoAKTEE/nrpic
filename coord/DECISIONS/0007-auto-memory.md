# 0007 Claude Code auto memory (D7)

Status: ACCEPTED by the user on 2026-11-19 (decision 0017); before that provisional · 2026-11-15

The default of the brief is to switch auto memory off in the project settings. The
project already has a memory directory with the user's standing instructions from earlier
sessions (roles, figures for every test, commit and push, the machine's Slurm rules); it
stays. Track sessions write no memory: all durable knowledge of the program goes into
files under git (`tracks/<ID>/`, `coord/`). Switching the setting itself waits for 0008.
