"""Test Q of the KB-G1 verifier: mechanical checks of the locators and numbers cited in
FIRST_QUESTIONS.md (the answers themselves were formed first by reading the sources; see
VERIFIER.md). Usage: python3 check_answers.py <outdir>

(1) Equation numbers: for the four papers of the first questions, my own numbering of every
    labelled display equation (texcount.label_numbers) against the knowledge base's.
(2) Locators: each cited line range must contain the stated token (regular expression).
(3) Code locators: each cited file:line of AthenaK must contain the stated token.
Writes <outdir>/answers.json. No paper text is written (only line numbers and verdicts).
"""
import json
import os
import re
import sqlite3
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texcount  # noqa: E402

ROOT = "/data/haiyangw/nrpic/kb-data"
DB = os.path.join(ROOT, "db", "current")
GIT = "/data/haiyangw/nrpic/wt/kb"
UP = os.path.join(ROOT, "raw", "github", "IAS-Astrophysics__athenak")
LOCAL_SHA = "a1c223753952674ee38819dc45043591dddc3022"

PAPERS = {"2611.12831": ("v1", "main.tex"), "2609.14218": ("v1", "MDPBH.tex"),
          "2512.14649": ("v2", "PRD_v2.tex"), "2404.16270": ("v1", "article.tex")}

# (question, paper, first line, last line, regex that must occur in the range)
LOCATORS = [
    (1, "2611.12831", 641, 641, r"unless otherwise stated"),
    (1, "2611.12831", 625, 637, r"B-splines"),
    (1, "2611.12831", 637, 663, r"first-order-shape"),
    (1, "2611.12831", 664, 670, r"sqrt\{\\gamma\}_\{ijk\}"),
    (1, "2611.12831", 738, 762, r"weight-unity"),
    (1, "2611.12831", 738, 762, r"tmunu-source-cell"),
    (1, "2611.12831", 680, 686, r"binomial filter"),
    (1, "2611.12831", 686, 686, r"smoothed particle hydrodynamics"),
    (1, "2611.12831", 688, 696, r"c_H"),
    (2, "2611.12831", 903, 903, r"Hamiltonian constraint"),
    (2, "2611.12831", 905, 917, r"Monte Carlo"),
    (2, "2611.12831", 965, 967, r"Poisson"),
    (2, "2611.12831", 1119, 1129, r"stratified"),
    (2, "2611.12831", 1129, 1129, r"N\^\{-1/2\}"),
    (2, "2611.12831", 1261, 1275, r"plummer-hamiltonian"),
    (2, "2611.12831", 1336, 1336, r"0\.133215"),
    (2, "2611.12831", 1442, 1442, r"(?i)lattice"),
    (2, "2611.12831", 1476, 1476, r"-1/2"),
    (2, "2611.12831", 1509, 1509, r"N\^\{-1/2\}"),
    (3, "2611.12831", 238, 248, r"kappa_1"),
    (3, "2611.12831", 380, 380, r"\\mu_L=2/\\alpha"),
    (3, "2611.12831", 384, 384, r"\\frac\{3\}\{4\}"),
    (3, "2611.12831", 388, 397, r"kappa_\{1,0\}"),
    (3, "2611.12831", 722, 725, r"0\.02"),
    (3, "2611.12831", 1117, 1117, r"alpha_\{\\rm exc\}=0\.1"),
    (3, "2611.12831", 1338, 1338, r"0\.05"),
    (4, "2611.12831", 1393, 1393, r"(?i)future work"),
    (4, "2611.12831", 763, 763, r"(?i)resampl"),
    (4, "2611.12831", 867, 867, r"FLRW"),
    (4, "2611.12831", 877, 877, r"FLRW"),
    (4, "2611.12831", 1323, 1323, r"collisional dynamics"),
    (4, "2611.12831", 1008, 1008, r"collisional"),
    (5, "2611.12831", 674, 674, r"GPUs"),
    (5, "2611.12831", 1398, 1398, r"Vista"),
    (5, "2611.12831", 1338, 1338, r"5\\times ?10\^6|5\\times10\^\{6\}"),
    (5, "2611.12831", 1338, 1338, r"256\^3"),
    (5, "2611.12831", 1017, 1017, r"2\\times10\^6"),
    (6, "2609.14218", 492, 549, r"K&=&-3H"),
    (6, "2609.14218", 549, 549, r"H_i=5k=50/L"),
    (6, "2609.14218", 837, 841, r"\\ln\\Psi"),
    (6, "2609.14218", 1063, 1075, r"m_p=\\frac\{E"),
    (6, "2609.14218", 452, 461, r"C\$ as \$5"),
    (6, "2609.14218", 463, 469, r"3H B\^i"),
    (6, "2609.14218", 473, 487, r"\\eta\$ is set to \$10"),
    (6, "2609.14218", 848, 910, r"hoop conjecture"),
    (6, "2609.14218", 828, 830, r"threshold"),
    (6, "2609.14218", 1084, 1102, r"\\mu\\geq0\.05"),
    (6, "2609.14218", 1095, 1095, r"N=80"),
    (6, "2609.14218", 1145, 1145, r"0\.045|0\.05"),
    (6, "2609.14218", 1203, 1205, r"Hamiltonian constraint"),
    (7, "2512.14649", 480, 483, r"geodesic slicing"),
    (7, "2512.14649", 519, 519, r"N=256"),
    (7, "2512.14649", 503, 506, r"s=5\.0"),
    (7, "2512.14649", 512, 512, r"N k_\{\\sigma\}\^\\circledast/4"),
    (7, "2512.14649", 405, 420, r"1\.86\\times 10\^\{-6\}"),
    (7, "2512.14649", 405, 420, r"H_0 = 10\^\{-5\}"),
    (7, "2512.14649", 528, 528, r"varepsilon_2 \\sim 6"),
    (7, "2512.14649", 534, 534, r"2\.8 \\times  10\^\{-2\}"),
    (7, "2512.14649", 538, 541, r"10\^\{-10\}"),
    (7, "2512.14649", 520, 520, r"textpertenthousand"),
    (8, "2404.16270", 194, 194, r"100\\,\\rg"),
    (8, "2404.16270", 204, 204, r"1 percent"),
    (8, "2404.16270", 194, 194, r"0\.01\$? ?au"),
    (8, "2404.16270", 211, 211, r"25\.3"),
    (8, "2404.16270", 317, 317, r"10\^\{-6\}|10\^-6|1\.013"),
    (8, "2404.16270", 348, 348, r"400"),
    (8, "2404.16270", 782, 782, r"0\.1|400|10"),
    (8, "2404.16270", 788, 788, r"0\.1\\%"),
    (8, "2404.16270", 790, 790, r"2,000"),
    (8, "2404.16270", 792, 793, r"\\beta = 5"),   # sentence starts at L792, number on L793
    (8, "2404.16270", 477, 477, r"20\\,\\rg"),
    (8, "2404.16270", 795, 796, r"2\.5"),
    (8, "2404.16270", 475, 475, r"retrograde"),
]

# (question, where, path, first line, last line, regex)
CODE = [
    (3, "upstream", "src/z4c/z4c.cpp", 131, 148, r'"damp_kappa1",\s*0\.0'),
    (3, "upstream", "src/z4c/z4c.cpp", 131, 148, r'"lapse_oplog",\s*2\.0'),
    (3, "upstream", "src/z4c/z4c.cpp", 131, 148, r'"shift_eta",\s*2\.0'),
    (3, "upstream", "src/z4c/z4c.cpp", 131, 148, r'"shift_Gamma",\s*1\.0'),
    (3, "local", "athenak/src/z4c/z4c.cpp", 131, 157, r'"damp_ch"'),
    (3, "local", "athenak/src/z4c/z4c.cpp", 131, 157, r'"damp_kappa1_over_alpha"'),
    (9, "upstream", "src/z4c/z4c.cpp", 81, 88, r"ncells1|nx1 \+ 2\*\(indcs\.ng\)|2\*\(indcs\.ng\)"),
    (9, "upstream", "src/z4c/z4c.cpp", 199, 199, r"cell-centered"),
    (9, "upstream", "src/z4c/z4c_calcrhs.cpp", 663, 664, r"CellCenterX"),
    (9, "upstream", "src/z4c/z4c_Sbc.cpp", 81, 83, r"CellCenterX"),
    (9, "upstream", "src/z4c/tmunu.hpp", 28, 43, r"S_dd"),
    (9, "upstream", "src/z4c/tmunu.cpp", 26, 32, r"realloc|u_tmunu"),
    (9, "upstream", "src/z4c/z4c_calcrhs.cpp", 129, 131, r"tmunu"),
    (9, "upstream", "src/dyn_grmhd/dyn_grmhd.cpp", 198, 200, r"MHD_SetTmunu"),
    (9, "upstream", "src/dyn_grmhd/dyn_grmhd.cpp", 415, 415, r"SetTmunu"),
    (9, "upstream", "src/z4c/z4c_tasks.cpp", 48, 58, r"MHD_SetTmunu"),
    (9, "upstream", "src/tasklist/numerical_relativity.hpp", 126, 128, r"QueueTask"),
    (9, "local", "athenak/src/particles/particles_tasks.cpp", 30, 45, r"NrpicDeposit"),
]

# labels cited with an equation number in FIRST_QUESTIONS.md
CITED_EQ = [("2611.12831", "eq:first-order-shape", "76"), ("2611.12831", "eq:weight-unity", "91"),
            ("2611.12831", "eq:tmunu-source-cell", "92"), ("2611.12831", "eq:z4-einstein", "17"),
            ("2611.12831", "eq:z4c-lapse", "30"), ("2611.12831", "eq:z4c-shift", "31"),
            ("2611.12831", "eq:plummer-hamiltonian", "128"), ("2512.14649", "eq:ourWindow", "33"),
            ("2404.16270", "e1.0", "1")]


def src_lines(pid):
    ver, fn = PAPERS[pid]
    p = os.path.join(ROOT, "raw", "arxiv", pid, ver, "src", fn)
    with open(p, "rb") as f:
        return f.read().decode("utf-8", "replace").split("\n")


def code_lines(where, path):
    if where == "upstream":
        with open(os.path.join(UP, path), "rb") as f:
            return f.read().decode("utf-8", "replace").split("\n")
    r = subprocess.run(["git", "-C", GIT, "show", f"{LOCAL_SHA}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace").split("\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    res = {"equations": {}, "cited_eq": [], "locators": [], "code": []}
    for pid, (ver, fn) in PAPERS.items():
        src = os.path.join(ROOT, "raw", "arxiv", pid, ver, "src")
        style, mine = texcount.label_numbers(os.path.join(src, fn), src)
        kb = dict(c.execute("select label, number from equations where paper_id=? and label is not null",
                            (pid,)).fetchall())
        common = sorted(set(mine) & set(kb))
        diff = [(l, kb[l], mine[l]) for l in common if (kb[l] or "") != (mine[l] or "")]
        res["equations"][pid] = {"style": style, "my_labels": len(mine), "kb_labels": len(kb),
                                 "common": len(common), "differ": diff,
                                 "only_mine": sorted(set(mine) - set(kb)),
                                 "only_kb": sorted(set(kb) - set(mine))}
        print(f"{pid}: style {style}; labels mine {len(mine)}, kb {len(kb)}, common {len(common)}, "
              f"numbers differ {len(diff)} {diff[:5]}; only mine {sorted(set(mine) - set(kb))[:5]}; "
              f"only kb {sorted(set(kb) - set(mine))[:5]}")
        for (p2, lab, cited) in CITED_EQ:
            if p2 == pid:
                ok = mine.get(lab) == cited and kb.get(lab) == cited
                res["cited_eq"].append({"paper": pid, "label": lab, "cited": cited, "mine": mine.get(lab),
                                        "kb": kb.get(lab), "ok": ok})
    for (q, pid, a, b, rx) in LOCATORS:
        L = src_lines(pid)
        txt = "\n".join(L[a - 1:b])
        ok = re.search(rx, txt) is not None
        hit = None
        if not ok:   # where does the token occur?
            hit = [i + 1 for i, l in enumerate(L) if re.search(rx, l)][:5]
        res["locators"].append({"q": q, "paper": pid, "lines": [a, b], "regex": rx, "ok": ok,
                                "found_at": hit})
    for (q, where, path, a, b, rx) in CODE:
        L = code_lines(where, path)
        ok = re.search(rx, "\n".join(L[a - 1:b])) is not None
        hit = None if ok else [i + 1 for i, l in enumerate(L) if re.search(rx, l)][:5]
        res["code"].append({"q": q, "where": where, "path": path, "lines": [a, b], "regex": rx,
                            "ok": ok, "found_at": hit})
    with open(os.path.join(out, "answers.json"), "w") as f:
        json.dump(res, f, indent=1)
    for e in res["cited_eq"]:
        print(f"cited eq {e['paper']} {e['label']}: cited {e['cited']} mine {e['mine']} kb {e['kb']} "
              f"{'ok' if e['ok'] else 'MISMATCH'}")
    nl = sum(1 for x in res["locators"] if x["ok"])
    print(f"paper locators: {nl}/{len(res['locators'])} contain the cited token")
    for x in res["locators"]:
        if not x["ok"]:
            print(f"   Q{x['q']} {x['paper']} L{x['lines'][0]}-{x['lines'][1]} /{x['regex']}/ not found; "
                  f"occurs at {x['found_at']}")
    nc = sum(1 for x in res["code"] if x["ok"])
    print(f"code locators: {nc}/{len(res['code'])} contain the cited token")
    for x in res["code"]:
        if not x["ok"]:
            print(f"   Q{x['q']} {x['where']}:{x['path']}:{x['lines'][0]}-{x['lines'][1]} /{x['regex']}/ "
                  f"not found; occurs at {x['found_at']}")


if __name__ == "__main__":
    main()
