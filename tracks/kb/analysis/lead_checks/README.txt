Checkers of the kb lead session of 2026-11-15 (journal tracks/kb/JOURNAL.md, checks L1-L11).
Own code, independent of kbtool; they read kb-data as text or bytes and are run with python3 -I
from outside the store. Copied from scratch/kb/lead/ where they were run.
  store_scan.py      L2   manifest ids against the store bytes and the download records
  eqcount.py         L5   numbered display lines of a single-file LaTeX source
  bibcount.py        L6   bibliography entries (.bbl \bibitem, .bib keys cited)
  alias_scan.py      L10  papers defining an alias of a definition command (\nc)
  eqcount_alias.py   L10  eqcount after substituting shorthands defined through such aliases
  composite_scan.py  L11  shorthands for several environments (use count flawed: see journal)
  composite_uses.py  L11  corrected use count over all files; joins database counts
  lgrep.py                line-numbered regex search used to find locators
  l10_table.tsv, l11_table.tsv, l11_before.txt   inputs of kb/scripts/fig_lead_equations.py
                                                 (run kb-20261115-141630-b2e57be)
