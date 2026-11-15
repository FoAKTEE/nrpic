# Vendored figure libraries (brief section 13.4)

| File | Use | Source |
|---|---|---|
| `czstyle.py` | data figures (`/zoom-figure-style`): `from czstyle import *`, `use_style()`, `save(fig, stem)` | section 9 of the skill zoom-figure-style, extracted with the skill's own regex |
| `cyclic_zoom.mplstyle` | the same rcParams as a style sheet (`plt.style.use(...)`) | `czstyle.write_mplstyle()` |
| `paperfig.py` | schematics (`/sleep-paper-figure-style`): `import paperfig as pf`, `pf.save(fig, stem)` | `scripts/paperfig.py` of the skill sleep-paper-figure-style |
| `figstyle.py` | the project's earlier module (`python/nrpic/figstyle.py`): identical rcParams and palette, different helpers (`save(fig, path, png=True)`, no overflow check) | this repository |

`SHA256SUMS` lists the four files; `SOURCES.json` says where each came from and records the
source's sha256. Check: `python3 -I harness/style/vendor.py --check` (also run by
`harness/tests/test_style.py`, which renders two data figures and one schematic and fails if
czstyle reports a label cut at the figure edge).

Rules: new figure scripts use `czstyle.py` and `paperfig.py`. Each track copies the files it
uses unchanged into `tracks/<ID>/note/scripts/` (the skill wants the module beside the script,
`/paper-writing` wants the scripts beside the manuscript); `harness/bin/nrpic-stage verify`
compares every copy there with `SHA256SUMS` and fails the stage check on a difference. A change
to a library is a proposal against `harness/style/`; the orchestrator re-vendors on main with
`harness/bin/nrpic-env exec -- python harness/style/vendor.py --write` and the tracks refresh
their copies after the next sync.
