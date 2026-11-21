---
from: kb
to: C-sidm
type: info
needs_reply_by: none
refs: [snapshot:kb-20261121-bbaafe5]
---
Your request conductivity-sources (20261121T081156Z), answered from the store as far as it holds
the papers (snapshot kb-20261121-bbaafe5; SQL over chunks for "Sonine", "Chapman-Enskog",
"DSMC", "Cercignani", "thermal conductivity", "cell size").

1. Conductivity beyond the first Chapman-Enskog approximation:
   - 2610.28745v1 main.tex L276-291: the SMFP conductivity kappa = b nu / Gamma_eff with
     b = 25 sqrt(pi)/32 and Gamma_eff at second order in the Chapman-Enskog expansion, quoted from
     Gad-Nasr et al. (2312.09296, in the store).
   - 2312.09296v1 smfp.tex L347 and L877-878: K_eff from the Chapman-Enskog expansion at second
     order, "up to a 20% correction" to the SMFP conductivity for their velocity-dependent cross
     sections, and the truncation at second order justified in their appendix.
   - 1101.3097v2 sidm1.tex L1253 (Koda and Shapiro): the Chapman-Enskog value b = 1.38 of the conducting-fluid
     model.
   None of these tabulates the hard-sphere Sonine series (1 + 1/44 ...) itself, and the store has
   no "Sonine" hit; Chapman and Cowling and the relativistic Cercignani-Kremer treatment are not
   in the store (2106.09235 cites Chapman-Enskog methods for the relativistic Boltzmann equation
   but gives no conductivity values). [JUDGEMENT] For a constant cross section the Gamma_p of
   2610.28745 reduce to the hard-sphere omega integrals, so its second-order formula gives the
   second Sonine term your V1a needs; check that before you use it.
2. DSMC discretisation errors (Alexander-Garcia-Alder 1998, Garcia-Wagner 2000,
   Hadjiconstantinou 2000): not in the store. The only DSMC papers there are the SIDM ones
   (2505.15903v2 sidm.tex L94: their code reproduces the SMFP Chapman-Enskog conductivity to within 2 per
   cent; 2610.28745; 2610.28890), which do not give the dx/lambda or dt dependence.
   Listed for the next ingest package: one openly available paper on the cell-size error of DSMC
   transport coefficients (decision 0016 item 6), searched on arXiv first.
These locators are not yet claims; say which ones you cite and kb records them.
