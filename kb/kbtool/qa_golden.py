"""K9: the golden questions of the retrieval regression (brief 12.9: at least 30 questions
with known answer locations, hit rate within the top 10).

Each question is our own wording, written on 2026-11-15 before any retrieval result was
seen. The answer location comes from a statement a person read at the source: the brief's
own example (q01), the answers to the first questions of KB-G1
(`tracks/kb/stage/KB-G1/FIRST_QUESTIONS.md`, "FQn"), and claims of the K8 layer that the
audit P2 marked checked (`claim <id>`; ids of the seed run kb-20261115-154020-7b80ccc).
A hit at paper level: a returned chunk of `paper`; at locator level: a returned chunk whose
source range (file and lines through build/tex/<id_>/sourcemap.json) overlaps one of `lines`
of `file`, widened by SLACK lines.

Bias [JUDGEMENT]: questions written by someone who knows the answer share words with it,
so a BM25 hit rate on this set is an upper estimate for questions a track would ask.
The set is also kept as data here (not as kb/golden/questions.yaml, which is outside this
package); `golden_yaml()` writes it in that form.
"""

SLACK = 5

QUESTIONS = [
    ("q01", "brief 12.9 example", "Which paper writes the Einstein equations as a first-order system in a form "
     "analogous to electrodynamics?", "2111.05282", "paper.tex", [(87, 88), (130, 140)]),
    # 2611.12831 (FQ1-FQ5 of KB-G1)
    ("q02", "FQ1 L637-663", "What order of shape function is used when particles are deposited onto the grid?",
     "2611.12831", "main.tex", [(625, 670)]),
    ("q03", "FQ1 L680-686", "Is the deposited source smoothed by a binomial filter after deposition?",
     "2611.12831", "main.tex", [(680, 686)]),
    ("q04", "FQ2 L888-917", "How is the dust ball of the Oppenheimer-Snyder test sampled with particles?",
     "2611.12831", "main.tex", [(888, 917)]),
    ("q05", "FQ3 L371-397", "Which lapse and shift gauge conditions are used, and how does the shift damping "
     "follow the tracked black holes?", "2611.12831", "main.tex", [(371, 397)]),
    ("q06", "FQ4 L1393", "Which future directions are listed in the conclusions of the particle-in-cell "
     "numerical relativity paper?", "2611.12831", "main.tex", [(1390, 1399)]),
    ("q07", "FQ5 L1398", "On which supercomputers were the Einstein-Vlasov particle-in-cell simulations run?",
     "2611.12831", "main.tex", [(1395, 1399)]),
    ("q08", "claim 508", "At what times do the two clumps inside the common envelope form apparent horizons?",
     "2611.12831", "main.tex", [(1340, 1340)]),
    ("q09", "claim 577", "How does the implicit midpoint pusher average positions and momenta between "
     "time levels?", "2611.12831", "main.tex", [(445, 456)]),
    ("q10", "claim 560", "Do the constraint violations seeded by particle noise scale as the inverse square "
     "root of the particle number?", "2611.12831", "main.tex", [(1129, 1129), (1509, 1511)]),
    # 2609.14218 (FQ6, claims 11, 31)
    ("q11", "FQ6 L398-469", "Which modified slicing condition is used for primordial black hole formation in "
     "a matter-dominated universe with a background scale factor?", "2609.14218", "MDPBH.tex", [(398, 469)]),
    ("q12", "claim 31", "What are the eigenvalues of the deformation tensor for the ellipsoidal peak with "
     "ellipticity e and prolateness p?", "2609.14218", "MDPBH.tex", [(907, 908)]),
    # 2512.14649 (FQ7), 2404.16270 (FQ8)
    ("q13", "FQ7 L503-506", "Which window function in wavenumber is used to coarse-grain the stochastic "
     "inflation noise in the numerical relativity simulation?", "2512.14649", "PRD_v2.tex", [(503, 506)]),
    ("q14", "FQ8 L194", "Below which pericentre distance do general-relativistic effects become significant "
     "for tidal separation of binaries by a massive black hole?", "2404.16270", "article.tex", [(194, 194)]),
    # other papers, from checked claims of the K8 seed
    ("q15", "claim 51", "Is the hoop conjecture ratio 2M over the circumferential radius used to diagnose "
     "black hole formation in dust collapse with different gauges?", "2610.23218", "main.tex", [(352, 360)]),
    ("q16", "claim 55", "Which paper uses the Zel'dovich approximation to estimate primordial black hole "
     "formation in the matter-dominated era?", "1609.01588", "apj_nonsphericalpbh.tex", [(381, 383)]),
    ("q17", "claim 91", "Does a trapped surface form near the centre at the time of collapse for a generic "
     "quadratic density profile?", "2507.18312", "Main.tex", [(234, 238)]),
    ("q18", "claim 164", "How large is the gravitational-wave power emitted around the time of black hole "
     "formation in the collapse simulations?", "1901.04498", "main.tex", [(284, 284)]),
    ("q19", "claim 178", "What is the gravitational-wave energy spectrum per logarithmic frequency in terms "
     "of the Fourier transform of the quadrupole moment?", "2403.15126", "pII_GW_Vir_C2_Arx.tex", [(903, 903)]),
    ("q20", "claim 196", "How many particles and which softening are chosen for the N-body runs of "
     "nonspherical collapse, and how converged are they?", "2605.04487", "main_v3.tex", [(2365, 2365)]),
    ("q21", "claim 198", "How do the fully numerical gravitational-wave spectra compare with the "
     "Zel'dovich-based estimate near the peak?", "2605.04487", "main_v3.tex", [(2512, 2512)]),
    ("q22", "claim 212", "What is the traceless part of the space-space Einstein equation in the weak-field "
     "expansion of the relativistic N-body code?", "1604.06065", "compendium_arxiv.tex", [(294, 298)]),
    ("q23", "claim 223", "Which open-source multigrid code solves the constraint equations for initial data "
     "with fundamental fields and inhomogeneous cosmologies?", "2501.13046", "main.tex", [(62, 103)]),
    ("q24", "claim 279", "What is the relaxation time of self-interacting dark matter in terms of density, "
     "velocity dispersion and cross section?", "astro-ph/0110561", "SIDMGT_Xiv2.tex", [(310, 321)]),
    ("q25", "claim 342", "For which black hole can the capture condition of dark matter orbits be derived "
     "analytically?", "1305.2619", "SFWpaper.tex", [(377, 377)]),
    ("q26", "claim 345", "Does black hole spin increase the dark matter density spike close to the hole?",
     "1707.06302", "kerrdm.tex", [(83, 95)]),
    ("q27", "claim 371", "Which simulations model a matter-dominated background with an oscillating massive "
     "scalar field and the perturbation with a massless field?", "2109.04896", "PBH_formation.tex", [(89, 89)]),
    ("q28", "claim 386", "What coupling strength k do traditional black holes like Kerr have in the cosmological "
     "coupling hypothesis?", "2302.07878", "paper_couple_rev.tex", [(132, 132)]),
    ("q29", "claim 405", "What do the Gaia black hole binaries imply for cosmologically coupled black hole "
     "mass growth with k equal to three?", "2305.01307", "andrae-elbadry-2023.tex", [(48, 50), (184, 184)]),
    ("q30", "claim 429", "Which simulation shows an exchange followed by a merger after a strong "
     "binary-single black hole scattering?", "2505.03934", "apssamp.tex", [(464, 480)]),
    ("q31", "claim 436", "Which three black hole simulations start from the Pythagorean Burrau configuration "
     "of the three-body problem?", "2108.01392", "main.tex", [(185, 185), (269, 277), (400, 400)]),
    ("q32", "claim 438", "Which study simulates head-on collisions of several black holes initially at rest "
     "with the BSSN formulation?", "2610.09336", "Liu_article_V2.tex", [(129, 129)]),
]


def questions():
    return [dict(id=i, source=s, question=q, paper=p, file=f, lines=[list(x) for x in L])
            for i, s, q, p, f, L in QUESTIONS]


def golden_yaml():
    """The set in the layout of brief 12.2 (`kb/golden/questions.yaml`)."""
    out = ["# Golden questions of the retrieval regression (brief 12.9); written by kbtool/qa_golden.py",
           "version: 1", "questions:"]
    for q in questions():
        out += [f"  - id: {q['id']}", f"    from: \"{q['source']}\"", f"    question: \"{q['question']}\"",
                f"    paper: \"{q['paper']}\"", f"    file: {q['file']}", f"    lines: {q['lines']}"]
    return "\n".join(out) + "\n"


def parse_source(src):
    """'main.tex:L12-34' -> ('main.tex', 12, 34); 'a.tex:L5-b.tex:L9' -> ('a.tex', 5, 10**9)
    (the chunk runs to the end of a.tex); else (None, None, None)."""
    import re
    m = re.match(r"^(.+?):L(\d+)(?:-(?:(.+?):L)?(\d+))?$", src.strip())
    if not m:
        return None, None, None
    f, a = m.group(1), int(m.group(2))
    if m.group(3) and m.group(3) != f:
        return f, a, 10 ** 9
    return f, a, int(m.group(4) or a)


def hit_level(q, hits):
    """(rank of the first hit of the paper or None, rank of the first locator hit or None)."""
    rp = rl = None
    for h in hits:
        if h.get("paper_id") != q["paper"]:
            continue
        rp = rp or h["rank"]
        f, a, b = parse_source(h.get("source") or "")
        if f and a is not None and f.split("/")[-1].lower() == q["file"].split("/")[-1].lower():
            if any(a <= hi + SLACK and b >= lo - SLACK for lo, hi in q["lines"]):
                rl = rl or h["rank"]
    return rp, rl
