"""Arithmetic behind the verdicts of items 1 and 2 (numbers copied from the source lines named
in verdicts/*.tsv; nothing is read from the claims). python3 -I arith_checks.py --out DIR"""
import argparse
import json
import math
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r = {}
    # 2108.11967 Table 1, b = 0.1 block (main.tex L490-497) and next block L516: C = M/R
    rows = {"0.1": (2.72074e-2, 6.82000, 3.98936e-3), "0.3": (3.29993e-2, 2.89200, 1.41053e-2),
            "0.6": (3.47240e-2, 1.63800, 2.11990e-2), "1.1": (3.29600e-2, 9.64001e-1, 3.41909e-2),
            "1.5": (3.02662e-2, 7.25001e-1, 4.17464e-2), "0.05(next block)": (3.87808e-2, 9.67200, 4.00960e-4)}
    r["2108.11967_C_eq_M_over_R"] = {k: {"M/R": m / R, "printed_C": c, "ratio_printed_to_M/R": c / (m / R)}
                                     for k, (m, R, c) in rows.items()}
    p0 = {"0.1": 1.42585e-6, "0.3": 7.40805e-5, "0.6": 9.86165e-4, "1.1": 1.09378e-3, "1.5": 4.12090e-2,
          "1.9": 1.21454e-1, "2.3": 3.09617e-1, "2.7": 7.19304e-1}
    lo, hi = math.log10(p0["0.6"]), math.log10(p0["1.5"])
    r["2108.11967_p0_interp_w1.1"] = 10 ** (lo + (hi - lo) * (1.1 - 0.6) / (1.5 - 0.6))
    # conduction constant b (1101.3097 L410-412, astro-ph/0110561 L394)
    r["b"] = {"25 sqrt(pi)/32": 25 * math.sqrt(math.pi) / 32, "25 sqrt(pi)/(32 sqrt 6)": 25 * math.sqrt(math.pi) / (32 * math.sqrt(6)),
              "25 pi/(32 sqrt 6)": 25 * math.pi / (32 * math.sqrt(6)), "25 pi/32": 25 * math.pi / 32}
    # 2512.13673 eq. r = 16 pi mu^2 / (Mpl^2 N*^2), N* = 60 (main.tex L135)
    r["r_crit"] = {str(mu): 16 * math.pi * mu ** 2 / 60 ** 2 for mu in (0.020, 0.025)}
    r["log10_5.6e-6"] = math.log10(5.6e-6)
    # horizon mass: M_H = c^3 t/G = 2.03e5 M_sun (t/1 s), t = 0.738 s (T/MeV)^-2 (g/10.75)^-1/2 (2002.12778 L278-290)
    r["M_H_Msun"] = {"T=100MeV": 2.03e5 * 0.738 / 100 ** 2, "T=1MeV": 2.03e5 * 0.738}
    # FFT prefactor of 2502.06783 L880 / 2610.32592 L489-490: (dk/2pi)^3 (dk/2pi)^(-3/2) (2pi)^(3/2) vs (dk/sqrt(2pi))^(3/2)
    dk = 2 * math.pi / 1.0
    first = (dk / (2 * math.pi)) ** 3 * (dk / (2 * math.pi)) ** -1.5 * (2 * math.pi) ** 1.5
    second = (dk / math.sqrt(2 * math.pi)) ** 1.5
    r["fft_prefactor_L1"] = {"first_line": first, "dk^1.5": dk ** 1.5, "second_line": second,
                             "first/second": first / second, "(2pi)^0.75": (2 * math.pi) ** 0.75}
    # 2406.11985 (claim 425): plunge bound 4 q^(2/3); a_b = d/M over the binary mass (massratio_table.tex L13-21)
    r["claim425"] = {"4q^(2/3) q=4": 4 * 4 ** (2 / 3), "4q^(2/3) q=9": 4 * 9 ** (2 / 3),
                     "a_b q8 = 1.97912096/(0.09997350+0.09996202)": 1.97912096 / (0.09997350 + 0.09996202),
                     "a_b q18 = 0.98956048/(0.04997869+0.04997149)": 0.98956048 / (0.04997869 + 0.04997149),
                     "q q8 = 0.79961960/0.19993552": 0.79961960 / (0.09997350 + 0.09996202),
                     "q q18 = 0.90002248/0.09995018": 0.90002248 / (0.04997869 + 0.04997149)}
    with open(os.path.join(a.out, "arith_checks.json"), "w") as f:
        json.dump(r, f, indent=1)
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
