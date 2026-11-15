"""Published numbers the equilibria are checked against, each with its locator.

Locators are file:line in the untrusted, uncommitted sources fetched by
harness/bin/nrpic-fetch-arxiv under kb-data/raw/arxiv/ (read-only data).
"""

GKLPRSW = "kb-data/raw/arxiv/2009.08163/v1/src/paper.tex"
AR = "kb-data/raw/arxiv/gr-qc_0601112/v1/src/ssevnum7.tex"

# 2009.08163, Table "First binding energy maximizer and zero" (tab:bindengmax).
# y = ln E0 - mu at the centre; E_b = (N - M)/N.
BINDING_TABLE = [
    dict(name="king", kind="king", k=0.0, l=0.0, L0=0.0, y_max="0.334", y_zero="0.784",
         locator=f"{GKLPRSW}:953"),
    dict(name="poly_k0.5", kind="poly", k=0.5, l=0.0, L0=0.0, y_max="0.298", y_zero="0.693",
         locator=f"{GKLPRSW}:954"),
    dict(name="poly_k0.5_L0.001", kind="poly", k=0.5, l=0.0, L0=0.001, y_max="0.267",
         y_zero="0.583", locator=f"{GKLPRSW}:955"),
    dict(name="poly_k0.5_l0.1_L0.001", kind="poly", k=0.5, l=0.1, L0=0.001, y_max="0.265",
         y_zero="0.588", locator=f"{GKLPRSW}:956"),
]

# 2009.08163: King runs either side of y_max (stable 0.314, 0.324; unstable 0.344, 0.354).
KING_RUNS = dict(y0=[0.314, 0.324, 0.344, 0.354], locator=f"{GKLPRSW}:1146")

# gr-qc/0601112: f = (E0 - E)^k_+ (L - L0)^l_+ (line 633), L0 = 0.1 in all cases
# (lines 760-761). Rows (Z_c, E_b, stable for A<1, stable for A>1). Z_c is the redshift
# from the centre to infinity, 1/alpha(0) - 1 (line 694 prints 1/sqrt(alpha(0)) - 1; the
# tables are reproduced only with the standard definition, see JOURNAL.md, Test 1).
AR_L0 = dict(value=0.1, locator=f"{AR}:760-761")
AR_TABLES = {
    1: dict(k=0.0, l=0.0, locator=f"{AR}:762-779", rows=[
        ("0.24", "0.036", True, True), ("0.30", "0.039", True, True),
        ("0.39", "0.041", True, True), ("0.43", "0.041", True, False),
        ("0.47", "0.040", True, False), ("0.52", "0.038", True, False),
        ("0.65", "0.027", True, False), ("0.82", "0.004", True, False),
        ("0.95", "-0.024", False, False), ("1.1", "-0.070", False, False)]),
    2: dict(k=0.0, l=0.5, locator=f"{AR}:781-798", rows=[
        ("0.21", "0.032", True, True), ("0.34", "0.040", True, True),
        ("0.39", "0.040", True, True), ("0.42", "0.041", True, False),
        ("0.46", "0.040", True, False), ("0.56", "0.036", True, False),
        ("0.65", "0.029", True, False), ("0.82", "0.008", True, False),
        ("0.95", "-0.015", False, False), ("1.20", "-0.078", False, False)]),
    # Case 3 (k = 1, l = 1/2, lines 802-819) is not reproduced: (E0 - E)^1 carries the
    # factor E0, whose value depends on the normalisation of alpha (lines 670-674).
    4: dict(k=0.0, l=1.5, locator=f"{AR}:821-837", rows=[
        ("0.21", "0.032", True, True), ("0.34", "0.039", True, True),
        ("0.41", "0.040", True, True), ("0.44", "0.040", True, True),
        ("0.52", "0.038", True, False), ("0.69", "0.025", True, False),
        ("0.80", "0.014", True, False), ("0.92", "-0.004", False, False),
        ("1.1", "-0.045", False, False)]),
}


def half_unit(s):
    """Half a unit in the last printed digit of the string s."""
    d = s.split(".")[1] if "." in s else ""
    return 0.5 * 10.0 ** (-len(d))
