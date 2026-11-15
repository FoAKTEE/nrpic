"""K8: defects of sources that the tracks reported to kb, entered one by one.

The two kb-requests with errata (E-stoch-inf `20261115T1410Z__to-kb__errata-s11-references`,
C-sidm `20261115T1320Z__to-kb__index-locators-typos`) write several defects per sentence
with locators in an irregular order ("method.tex 78 and 151", "`:493` (p(0) = ...)"), so
they are transcribed here instead of parsed: one claim per defect, in our own wording, with
the locators and the run ids the track gave. They are the tracks' computed findings, so the
label is judgement (brief 12.8: supported or overturned by computed results, never
upgraded to fulltext); the knowledge base checks that each locator resolves and that the
numbers quoted from the paper are at the cited lines.

Each entry: (origin line in the request, paper id, [(file, first, last)], text, runs).
The file '' is the paper's main file.
"""
from .claims_parse import ClaimSeed, Locator

E_PATH = "tracks/E-stoch-inf/outbox/20261115T1410Z__to-kb__errata-s11-references.md"
C_PATH = "tracks/C-sidm/outbox/20261115T1320Z__to-kb__index-locators-typos.md"

E_ITEMS = [
    (12, "2502.06783", [("main_V2PRD.tex", 320, 320), ("main_V2PRD.tex", 490, 490)],
     "Erratum, eq. (17): the term -sqrt(2 eps1) H Mpl Psi_G vanishes in the geodesic gauge (line 490); "
     "the initial data need -sqrt(2 eps1) Mpl H Psi_B instead (derivation tracks/E-stoch-inf/spec/SPEC.md 5.3).",
     "E-stoch-inf-20261115-123146-82d2fd4"),
    (15, "2502.06783", [("main_V2PRD.tex", 876, 884)],
     "Erratum: the printed prefactor dk^(3/2) of the noise draws gives (2 pi)^3 too much power; "
     "the right normalisation is L^(-3/2).",
     "E-stoch-inf-20261115-122934-9ac98d8"),
    (15, "2610.32592", [("", 487, 491)],
     "Erratum, appendix: the printed draw prefactor (dk/sqrt(2 pi))^(3/2) gives (2 pi)^(3/2) too much "
     "power; the right normalisation is L^(-3/2).",
     "E-stoch-inf-20261115-122934-9ac98d8"),
    (18, "2206.11234", [("method.tex", 78, 78), ("method.tex", 151, 151)],
     "Erratum: the sign of the importance-sampling weight is wrong.",
     "E-stoch-inf-20261115-125312-dafadc4"),
    (19, "2206.11234", [("appendix.tex", 168, 173)],
     "Erratum: v0/4 is not the leading pole in general.",
     "E-stoch-inf-20261115-125658-e3eaef3"),
    (21, "2512.14649", [("PRD_v2.tex", 108, 108)],
     "Erratum: the Friedmann denominator lacks the factor 3 Mpl^2.", ""),
    (21, "2512.14649", [("PRD_v2.tex", 534, 534)],
     "Erratum: the 'very shallow maximum' is an exact stationary inflection point at -sqrt2 v, and the USR "
     "interval given in the text is one e-fold later than in the paper's Fig. 1.", ""),
]

C_ITEMS = [
    (10, "2108.11967", [("main.tex", 491, 491)],
     "Typo in Table 1: C = 1.41053e-2 at w0 = 0.3 is not M/R = 1.141e-2.", "C-sidm-20261115-120722-38ab057"),
    (10, "2108.11967", [("main.tex", 493, 493)],
     "Typo in Table 1: p(0) = 1.09378e-3 at w0 = 1.1 is off by ten (about 1.09e-2 by the neighbouring rows).",
     "C-sidm-20261115-120722-38ab057"),
    (11, "2108.11967", [("main.tex", 516, 516)],
     "Typo in Table 1: C = 4.0e-4 where M/R = 4.0e-3.", "C-sidm-20261115-120722-38ab057"),
    (12, "2108.11967", [("main.tex", 197, 197)],
     "The printed e^{2 Phi} is not consistent with the tabulated numbers.", "C-sidm-20261115-120722-38ab057"),
    (14, "gr-qc/0601112", [("ssevnum7.tex", 694, 694)],
     "Z_c is printed as 1/sqrt(alpha(0)) - 1; the tables are reproduced only with 1/alpha(0) - 1.",
     "C-sidm-20261115-121626-e99907d"),
    (15, "gr-qc/0601112", [("ssevnum7.tex", 811, 812)],
     "Table 3 prints Z_c = 0.045 and 0.052 between 0.42 and 0.77; read as 0.45 and 0.52.", ""),
    (17, "1101.3097", [("sidm1.tex", 410, 412)],
     "The conduction constant b = 25 sqrt(pi)/32 here; the footnote's value matches neither this nor "
     "25 pi/(32 sqrt 6) of astro-ph/0110561 SIDMGT_Xiv2.tex:394.", ""),
    (18, "2601.17117", [("SIDM_MS.tex", 233, 233)],
     "The conduction constant b = 25 sqrt(pi)/32 (as 1101.3097), not 25 pi/(32 sqrt 6) as in astro-ph/0110561.",
     ""),
    (18, "astro-ph/0110561", [("SIDMGT_Xiv2.tex", 394, 394)],
     "The conduction constant b = 25 pi/(32 sqrt 6), not 25 sqrt(pi)/32 as in 1101.3097 and 2601.17117.", ""),
]


def seeds(refs):
    """ClaimSeeds of the errata. refs = {track: git ref}."""
    out = []
    for track, path, items in (("E-stoch-inf", E_PATH, E_ITEMS), ("C-sidm", C_PATH, C_ITEMS)):
        for line, pid, locs, text, runs in items:
            L = [Locator(pid, "", f, a, b, f"{f}:{a}" + (f"-{b}" if b != a else ""), 0) for f, a, b in locs]
            out.append(ClaimSeed(text=text, label="JUDGEMENT", locators=L, paper_id=pid, origin_path=path,
                                 origin_ref=refs.get(track, f"track/{track}"), origin_line=line, track=track,
                                 section="kb-request (errata)", kind="limitation",
                                 evidence=("run " + runs) if runs else "", extra={"erratum": True}))
    return out


SPECS = (("E-stoch-inf", "track/E-stoch-inf", E_PATH), ("C-sidm", "track/C-sidm", C_PATH))
