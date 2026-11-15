---
from: kb
to: core
type: request
needs_reply_by: 2026-11-29
refs: [arXiv:2611.12831, kb/curated/paper_code_links.tsv, run:kb-20261115-135323-534eb86]
---
body: `kb/curated/paper_code_links.tsv` holds 25 links from statements of the method of
arXiv:2611.12831 (line ranges and equation labels of the stored v1 source) to functions of
this repository at main, derived from your interface documents (tracks/core/interfaces at
core/nrpic c37eeca). All 25 pass `kb link check` (rechecked by the kb lead) and are `claimed`.
Please name, for each link, the test or run that upgrades it to verified; kb then records
`kb link add ... --status verified --evidence <run id>`. Also: `<z4c> nco` is set in
problems/jeans/jeans.athinput line 127 and read by no code of this tree (parameter index,
run kb-20261115-135545-d405f64). Smallest acceptable answer: a list link_key -> test or run
id, and whether nco is dead.
