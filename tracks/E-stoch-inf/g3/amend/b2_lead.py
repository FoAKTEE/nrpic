#!/usr/bin/env python3
"""Lead's own arithmetic for finding B2 of the scope review (batch 19): sensitivity of F(nu) = P(x > nu)
at fixed thresholds nu sigma_lin to a variance error, a skewness and an excess kurtosis (Edgeworth to
first order), and the three-standard-error threshold of the 4d.3 comparison for S seeds and N_ref
reference realisations. Inputs (with their sources): per-seed s.d. of F_+(3) and F_+(4) of a 128^3 box
(5.42e-5, 6.20e-6: review run E-20261125-131002-ceefa2f; power run 4.96e-5, 5.98e-6:
E-20261125-115822-29795d6); reference F_+(3) 1.5e-3 class (ref_inflection_n32.json). Writes b2_lead.json.

    python3 b2_lead.py OUTDIR
"""
import json, os, sys
import numpy as np
from scipy.stats import norm

out = sys.argv[1]
res = {}
for nu, sd_box, Fref in ((3.0, 5.42e-5, 1.5e-3), (4.0, 6.20e-6, 3.6e-5)):
    Q, phi = norm.sf(nu), norm.pdf(nu)
    dlnF_dlnsig = nu * phi / Q                                # F(nu; sigma) = Q(nu sigma_lin / sigma)
    dlnF_dskew = (nu ** 2 - 1) * phi / (6 * Q)                # Edgeworth: + skew/6 He2(nu) phi
    dlnF_dkurt = (nu ** 3 - 3 * nu) * phi / (24 * Q)          # + exkurt/24 He3(nu) phi
    row = dict(Q=Q, dlnF_dlnsigma=dlnF_dlnsig, dlnF_dskew=dlnF_dskew, dlnF_dexkurt=dlnF_dkurt)
    for S, Nref in ((256, 4e6), (128, 4e6), (80, 4e6), (256, 2e5)):
        e_nr = sd_box / Q / np.sqrt(S)
        e_ref = np.sqrt((1 - Fref) / (Nref * Fref))
        thr = 3 * np.hypot(e_nr, e_ref)
        row[f"S{S}_N{Nref:.0e}"] = dict(rel_se_nr=e_nr, rel_se_ref=e_ref, three_se=thr,
                                         sigma_err_seen=thr / dlnF_dlnsig, skew_seen=thr / dlnF_dskew,
                                         exkurt_seen=thr / dlnF_dkurt)
    # seeds at which the NR error is one third of the reference error (4e6)
    e_ref = np.sqrt((1 - Fref) / (4e6 * Fref))
    row["S_where_nr_is_third_of_ref"] = (sd_box / Q / (e_ref / 3)) ** 2
    row["skew_0.0231_moves_F_by"] = 0.0231 * dlnF_dskew
    res[f"nu{nu:g}"] = row
    print(nu, json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in row.items()
                          if not isinstance(v, dict)}), json.dumps({k: round(v, 5) for k, v in row["S256_N4e+06"].items()}))
with open(os.path.join(out, "b2_lead.json"), "w") as f:
    json.dump(res, f, indent=1)
