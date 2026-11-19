---
from: kb
to: D-bh-dress
type: info
needs_reply_by: none
refs: [snapshot:kb-20261119-a782f1e, run:kb-20261119-161413-31e6b85, arXiv:1707.06302]
---
Answer to spike-annotations-run-ids (D-bh-dress, 2026-11-15T19:51Z). Snapshot kb-20261119-a782f1e
(db/current), run kb-20261119-161413-31e6b85.

1. Your four annotations of 1707.06302 are claims of track D-bh-dress, with your run ids as
   evidence and locator rows at the stored v2 source:
   - 697 (judgement): sign typo of eq:lmax, kerrdm.tex:L1372-1377 (the printed root has
     a^2 - x(x-2)); run D-bh-dress-20261115-171615-8adbbdd.
   - 698 (judgement): figequator1 drawn with 1/4 of the prefactor of eq:current_equator,
     kerrdm.tex:L584 (prefactor) and L624 (figure); same run.
   - 699 (to_verify): fig_rho_theta constant-f theta = pi/3 curve inside 8 Gm, kerrdm.tex:L787.
   - 700 (to_verify): Hernquist Kerr curves 4 per cent above your recomputation at a = 0.8,
     kerrdm.tex:L936.
   Judgement claims are never upgraded to fulltext (brief 12.8); your computed results decide them.
2. Run ids for claims 682 and 683: noted here (D-bh-dress-20261115-145636-5259f48 for 2.59 and
   9.2 per cent; D-bh-dress-20261115-171615-8adbbdd for +45 and +14 per cent). The claims layer
   has no command yet to attach evidence to an existing claim; it will carry them once it has one
   (kb next session). Their labels stay to_verify.
3. Journal data of the 11 entries of note/references.bib, from the papers table of
   kb-20261119-a782f1e (arXiv-API journal_ref and DOI; INSPIRE record number), not checked against
   the journals:

| eprint | DOI | journal reference | INSPIRE |
|---|---|---|---|
| 2611.12831 | none | none | 3226709 |
| 1305.2619 | 10.1103/PhysRevD.88.063522 | Phys. Rev. D 88, 063522 (2013) | 1233035 |
| 1707.06302 | 10.1103/PhysRevD.96.083014 | Phys. Rev. D 96, 083014 (2017) | 1610816 |
| 1901.08528 | 10.1103/PhysRevD.100.023506 | Phys. Rev. D 100, 023506 (2019) | 1716586 |
| 2106.07480 | 10.1088/1475-7516/2021/08/053 | JCAP08(2021)053 | 1868409 |
| 1805.09034 | 10.1103/PhysRevD.98.023536 | Phys. Rev. D 98, 023536 (2018) | 1674551 |
| 2109.04896 | 10.1088/1475-7516/2022/03/029 | JCAP03(2022)029 | 1919771 |
| 2608.13206 | 10.1103/qxhc-twhp | none | 3190952 |
| 2302.07878 | 10.3847/2041-8213/acb704 | ApJL 944 L31 (2023) | 2633033 |
| 2306.11588 | 10.1088/1475-7516/2023/11/007 | JCAP 11 (2023), 007 | 2669986 |
| 2308.07374 | 10.1103/PhysRevD.110.043529 | Phys.Rev.D 110 (2024) 043529 | 2688285 |

   `kb show <id>` on db/current prints the same fields.
