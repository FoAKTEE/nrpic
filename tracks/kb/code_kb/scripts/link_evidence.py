#!/usr/bin/env python3
"""Evidence of the verdicts on the 25 curated paper-code links (package code_kb, step 3).

Every verdict below rests on locators; this script checks each of them mechanically and
writes the table LINKS.tsv and a JSON record into the output directory:
  - test entry: the heading is at that line of docs/TESTLOG.md or cosmo/TESTLOG.md at the
    commit REF, and the commit named as the entry's origin already contains the heading;
  - record: a run directory of the main checkout's runs/ (untracked, read only) or a
    tracked file contains the given text (an option of the deck or of the command line);
  - reach: a source line at REF contains the given text (the call or the read that puts
    the linked symbol on the test's code path).
Standard library only; run with python3 -I. Nothing is executed or imported from the
paths it reads.

    python3 -I link_evidence.py --out DIR [--home /data/haiyangw/nrpic] [--ref 47ab19ab]
"""
import argparse
import json
import os
import subprocess
import sys

DT, CT = "docs/TESTLOG.md", "cosmo/TESTLOG.md"
P, Z = "athenak/src/particles/", "athenak/src/z4c/"

# entry = (file, line, heading prefix, commit that added it)
E_PUSH = (DT, 6, "## Pusher kernels (standalone build", "495d451c")
E_MESH = (DT, 23, "## Mesh path (CPU, 2026-11-13)", "495d451c")
E_DSMR = (DT, 30, "## Deposition on refined meshes", "495d451c")
E_DUST = (DT, 50, "## Dust collapse, R_0 = 5 M", "495d451c")
E_STAB = (DT, 72, "## Stable cluster y_c = 0.819", "495d451c")
E_CTLQ = (DT, 132, "## Stable cluster controls: what drives", "e38d4e53")
E_PUNC = (DT, 166, "## Test particles around an evolved puncture", "935da4da")
E_CTLR = (DT, 225, "## Stable cluster controls: results", "bfc0daf9")
E_COMP = (DT, 282, "## Compensated filter (source", "884ea6ac")
E_KERR = (DT, 635, "## Test-particle clusters in Schwarzschild and Kerr", "e0e36761")
E_RELX = (DT, 804, "## Growing oscillation: parabolic relaxation", "dc796fed")
E_INTV = (DT, 1971, "## Intervention: removing matter inside the horizon", "e90c46db")
E_CT1 = (CT, 1480, "## T1: conservation on the mesh, and the interpolation", "f219aded")
E_CT1A = (CT, 443, "## T1a: cloud-shape study, outcome", "e2c189a8")

R = "runs/"
KP, KPC = R + "geodesic/kerr_passage/", R + "geodesic/kerr_passage_cpu/"
REC_PUSH = [(KPC + "mid_ks_dt0.01/cmd.sh", "particles/pusher=midpoint"),
            (KPC + "mid_ks_dt0.01/cmd.sh", "particles/tolerance=2.0e-14"),
            (KP + "mid_ks_dt0.01/geodesic.athinput", "pusher         = midpoint")]
REC_MESH = [("problems/tests/mesh_static.athinput", "metric         = mesh"),
            ("problems/tests/mesh_static.athinput", "pusher         = midpoint"),
            ("problems/tests/mesh_static.athinput", "deposit        = true"),
            ("problems/tests/mesh_static.athinput", "dynamic = false"),
            (R + "dev/mesh_static/run.log", "cycle=3000"),
            ("analysis/diag/README.md", "The deposition\nidentity holds to 1.0e-15")]
REC_DSMR = [(R + "dev/dep_smr/cap0/deposit_smr.athinput", "refinement       = static"),
            (R + "dev/dep_smr/cap0/athena.log", "particles/deposit_max_level=0"),
            (R + "dev/dep_smr/cap1/athena.log", "particles/deposit_max_level=1"),
            (R + "dev/dep_smr/gpu_adapt/athena.log", "particles/deposit_adaptive=true")]
REC_DUST = [(R + "os/amr_n26/os_amr.athinput", "refinement          = adaptive"),
            (R + "os/amr_n26/os_amr.athinput", "method          = lohner"),
            (R + "os/amr_n26/os_amr.athinput", "lohner_refine   = 0.2"),
            (R + "os/amr_n26/os_amr.athinput", "deposit        = true"),
            (R + "os/amr_n26/athena.log", "problems/os/os_amr.athinput")]
REC_PUNC = [("problems/puncture/tracers_single.athinput", "metric         = mesh"),
            ("problems/puncture/tracers_single.athinput", "pusher         = midpoint"),
            ("problems/puncture/tracers_single.athinput", "alpha_exc      = 0.05"),
            ("problems/puncture/tracers_single.athinput", "lapse_oplog     = 2.0"),
            ("problems/puncture/tracers_single.athinput", "shift_Gamma     = 0.75"),
            ("docs/results_tracers.md", "Run `runs/puncture/single_v3`: Z4c, 1+log slicing")]
REC_KERR = [(R + "cluster_test/plunge_a0.9_mid/cluster_mesh.athinput", "alpha_exc      = 0.62"),
            (R + "cluster_test/plunge_a0.9_mid/cluster_mesh.athinput", "metric         = mesh"),
            ("docs/results_cluster_test.md", "3339 plunge")]
REC_INTV = [(R + "jeans/diag_v14b/athena.log", "particles/ah_exc_factor=0.8"),
            (R + "jeans/diag_v14b/athena.log", "particles/alpha_exc=0.05")]
REC_CTL = [(R + "st/ctl/s1_nf0/athena.log", "particles/nfilter=0"),
           (R + "st/ctl/s1_nf2/athena.log", "particles/nfilter=2"),
           (R + "st/ctl/s1_nf4/athena.log", "particles/nfilter=4"),
           (R + "st/ctl/s1_nf4c/athena.log", "particles/filter_compensate=true")]
REC_RELX = [(R + "st/osc/ch0p05/athena.log", "z4c/damp_ch=0.05")]
REC_CT1 = [(R + "cosmo/dav_c704_n32_pcsct_c/daverio_field.athinput", "interp         = hermite"),
           (R + "cosmo/dav_c704_n32_pcsct_c/daverio_field.athinput", "metric         = mesh"),
           (R + "cosmo/dav_c704_n32_pcsct_c/daverio_field.athinput", "pgen_name  = nrpic_cosmo")]
REC_CT1A = [(R + "cosmo/east_d0.0025_n64_tsc/athena.log", "particles/deposit_shape=tsc"),
            (R + "cosmo/east_d0.0025_n64_pcs/athena.log", "particles/deposit_shape=pcs")]

# reach = (path at REF, line, text on that line)
S_MID = [("tests/kernel/kernel_test.cpp", 265, "nrpic::PushMidpoint(met, dt, tol, 200, x, u)"),
         (P + "nrpic.cpp", 554, ": nrpic::PushMidpoint(met, dt, tol, maxit, x, u);")]
S_LF = [("tests/kernel/kernel_test.cpp", 91, "nrpic::LorentzFactor(gi, u, uup)"),
        (P + "nrpic.cpp", 856, "nrpic::LorentzFactor(gi, up, uup)")]
S_AVG = [(P + "nrpic_kernels.hpp", 393, "if (!is_static) {"),
         (P + "nrpic_kernels.hpp", 395, "AverageAdm(p, q);")]
S_TOL = [(P + "nrpic.cpp", 90, "GetOrAddReal(\"particles\", \"tolerance\", 1.0e-7)"),
         (P + "nrpic.cpp", 91, "GetOrAddInteger(\"particles\", \"max_iterations\", 50)")]
S_TRI = [("tests/kernel/kernel_test.cpp", 202, "BuildTriad(nrpic::kTriadSymmetric"),
         (P + "nrpic_kernels.hpp", 468, "BuildTriad(triad_kind, p.g, tr);")]
S_BOR = [("tests/kernel/kernel_test.cpp", 266, "nrpic::PushBoris(met, (pusher == 1)"),
         (P + "nrpic.cpp", 553, "it = boris ? nrpic::PushBoris(met, triad, dt, tol, maxit, x, u)")]
S_HER = [(P + "nrpic_mesh.hpp", 99, "HermiteWeights(xi - static_cast<Real>(i0 - ist[d]), w[d], dw[d]);")]
S_GAT = [(P + "nrpic_mesh.hpp", 152, "Gather(m0, x, p);")]
S_DEP = [(P + "nrpic.cpp", 1179, "dep_sum[0] = se; dep_sum[1] = sx; dep_sum[2] = sy; dep_sum[3] = szz;")]
S_SHP = [(P + "nrpic.cpp", 173, "GetOrAddString(\"particles\", \"deposit_shape\", \"cic\")")]
S_TSK = [(P + "particles_tasks.cpp", 37, "AddTask(&Particles::NrpicPush, this, none)"),
         (P + "particles_tasks.cpp", 47, "AddTask(&Particles::NrpicDeposit, this,")]
S_RGD = [("athenak/src/mesh/mesh_refinement.cpp", 189, "pmbp->ppart->NrpicInitializeSources();")]
S_CON = [(P + "nrpic_io.cpp", 645, "conservation of energy and momentum of the deposited matter"),
         (P + "nrpic_io.cpp", 665, "if (pm->multilevel) return;"),
         (P + "nrpic_io.cpp", 289, "dep_sum[0], dep_sum[1], dep_sum[2], dep_sum[3]")]
S_ADM = [(Z + "z4c_tasks.cpp", 101, "ADMConstraints")]
S_RHS = [(Z + "z4c_tasks.cpp", 51, "Task_Run, {Z4c_CopyU}, {MHD_SetTmunu, SF_SetTmunu});")]

V, C, F = "verified", "claimed", "refuted"
LINKS = [
    # key, area, verdict, entries, records, reach, outcome (from the entry), note
    ("M01", "pusher", V, [E_PUSH], REC_PUSH, S_MID,
     "midpoint, analytic spherical KS: E 2.781e-8, L_z 0, Q 1.254e-7 against published 2.8e-8, round-off, 1.3e-7; "
     "pericentre 1.898325 M (exact 1.898327 M); same numbers through AthenaK on CPU", ""),
    ("M02", "pusher", V, [E_PUSH], REC_PUSH, S_LF,
     "invariant E = alpha W - beta.u of the test uses LorentzFactor; E error 2.781e-8 (published 2.8e-8)",
     "the pushers use LorentzFactorEps (nrpic_kernels.hpp:398); LorentzFactor is on the deposit's sum m W"),
    ("M03", "pusher", V, [E_PUSH, E_MESH], REC_PUSH + REC_MESH, S_MID,
     "standalone and AthenaK midpoint rows match the published digits; mesh path: r in [8.0000, 8.0012] M, "
     "E 8.4e-7, L_z 5.1e-6 over 300 M", ""),
    ("M04", "pusher", V, [E_PUNC], REC_PUNC, S_AVG,
     "six tracers in an evolved puncture spacetime, 250 M: L_z to 1.1e-4..3.9e-4; late Killing energy low by "
     "1.6e-4..2.4e-4", "two stored time levels averaged only when the metric is evolved (is_static false)"),
    ("M05", "pusher", V, [E_PUSH], REC_PUSH, S_TOL,
     "AthenaK runs pass tolerance 2.0e-14, max_iterations 200 to NrpicInit; results equal the standalone ones",
     "option-of: the read is tested, the default 1e-7 (the paper's value) is not exercised by this entry"),
    ("M06", "pusher", V, [E_PUSH], REC_PUSH, S_TRI,
     "Boris with symmetric and Cholesky triads, analytic and lattice: symmetric analytic 9.046e-8, 1.136e-8, "
     "7.825e-7 against 9.0e-8, 1.1e-8, 7.8e-7", ""),
    ("M07", "pusher", V, [E_PUSH], REC_PUSH, S_BOR,
     "Boris rows: Cholesky lattice 2.046e-6, 3.788e-6, 5.289e-5 against 2.0e-6, 3.8e-6, 5.3e-5", ""),
    ("M08", "interpolation", V, [E_CT1], REC_CT1, S_HER,
     "Catmull-Rom gradient error computed -6.4, +3.1, +0.6 percent; predicted residual 1.15e-3 against "
     "measured 1.27e-3; momentum residual 2.2e-3 (hermite) against 4.3e-4 (bspline)", ""),
    ("M09", "interpolation", V, [E_MESH], REC_MESH, S_GAT,
     "mesh-sampled Kerr-Schild metric, 96^3, dx = 0.25 M: E 8.4e-7, L_z 5.1e-6, no secular drift", ""),
    ("M10", "deposit", V, [E_MESH], REC_MESH, S_DEP,
     "deposition identity |int E sqrt(gamma) dV / sum m W - 1| at most 1.0e-15 over 3000 cycles", ""),
    ("M11", "deposit", V, [E_MESH, E_CT1A], REC_MESH + REC_CT1A, S_SHP + S_DEP,
     "cic (default): identity 1.0e-15; tsc, pcs: mean relative H constraint 2.0e-4, 6.0e-6, 9.9e-6 "
     "(linear, quadratic, cubic)", ""),
    ("M12", "deposit", V, [E_MESH], REC_MESH, S_DEP,
     "identity 1.0e-15 in a metric with sqrt(gamma) != 1 across each cloud",
     "[JUDGEMENT] the identity holds only if the deposit divides by the receiving cell's sqrt(gamma) that "
     "the integral multiplies by"),
    ("M13", "time step", V, [E_MESH], REC_MESH, S_TSK,
     "order from the source: NrpicSaveMetric before the stages, NrpicPush, NrpicExcise, NrpicCollide, "
     "NrpicDeposit after them (run kb-20261121-232013-52c350a)",
     "the named test has no Z4c (<adm> dynamic = false): it runs the particle half of the order only"),
    ("M14", "excision", V, [E_KERR], REC_KERR, [],
     "removal at the lapse threshold: 3726 and 3345 particles removed against 3727 and 3339 predicted", ""),
    ("M15", "excision", V, [E_INTV], REC_INTV, [],
     "with removal inside 0.8 of the horizon radius the run passes 11.926 M (where v7, v14 failed) and "
     "reaches 13.0 M", ""),
    ("M16", "filter", V, [E_CTLQ, E_CTLR, E_COMP], REC_CTL, [],
     "late constraint norms 0.14, 0.026, 0.011 for 0, 2, 4 passes; single particle: second moment 2.0000 "
     "cells^2 without, 0.0000 with compensation", ""),
    ("M17", "Z4c", V, [E_RELX], REC_RELX, [],
     "relaxation length 0.05: H norm 0.077 against 0.121 at 5 M, 0.0145 against 0.031 at the end",
     "damp_ch_dx is 0 in this run: its part is not exercised"),
    ("M18", "Z4c", C, [E_MESH], REC_MESH, S_ADM,
     "", "the named test has no Z4c (<adm> dynamic = false), so ADMConstraints (a Z4c task) does not run; "
     "candidate: DT 'Stable cluster y_c = 0.819' (docs/TESTLOG.md:72, constraint norms) or a resolution "
     "study of H at t = 0 of constraint-solved data"),
    ("M19", "refinement", C, [], REC_DUST, [],
     "", "no test named; candidate: DT 'Dust collapse, R_0 = 5 M' (docs/TESTLOG.md:50), runs/os/amr_n26 with "
     "problems/os/os_amr.athinput (method = lohner, 0.2, 0.02, 0.01); it records the refinement, not the indicator"),
    ("M20", "refinement", C, [E_DSMR], REC_DSMR, S_RGD,
     "", "the named test uses refinement = static: no regrid, so the call after a regrid "
     "(mesh_refinement.cpp:189) does not run; candidate: DT 'Dust collapse, R_0 = 5 M' (docs/TESTLOG.md:50, "
     "adaptive, 'deposition identity 1e-15 throughout, across all regrids')"),
    ("M21", "refinement", V, [E_DSMR], REC_DSMR, S_DEP,
     "three levels, 10^4 particles crossing level boundaries: integrals equal the particle sums to 16 digits "
     "(GPU), 4e-13 (CPU), for level caps 1 and 0 and the adaptive cap", ""),
    ("M22", "refinement", V, [E_DSMR], REC_DSMR, S_DEP,
     "identity to the printed 16 digits on the GPU and to 4e-13 on the CPU across level boundaries", ""),
    ("M23", "diagnostics", F, [E_DSMR], REC_DSMR, S_CON,
     "", "NrpicWriteConservation computes residuals of nabla_b T^ab = 0 on uniform meshes and returns on "
     "refined ones (nrpic_io.cpp:645, 665); it was added in f219aded (2026-11-14), after the named test. The "
     "identity of the paper is dep_sum of NrpicDepositSources written by NrpicWriteHistory (nrpic_io.cpp:289): "
     "proposed symbol particles::Particles::NrpicWriteHistory"),
    ("M24", "Z4c", C, [], REC_PUNC, [],
     "", "no test entry named ('every isolated-system run'); candidate: DT 'Test particles around an evolved "
     "puncture' (docs/TESTLOG.md:166; lapse_oplog 2.0, shift_Gamma 0.75, shift_eta 2.0), which checks "
     "gauge-invariant quantities only; shift_alpha2Gamma unused"),
    ("M25", "Z4c", C, [E_MESH], REC_MESH + REC_DUST, S_RHS,
     "", "the named test has no Z4c; candidate: DT 'Dust collapse, R_0 = 5 M' (docs/TESTLOG.md:50: central "
     "lapse on the lapse bound to 1e-4, density on the cycloid to 2e-4), runs/os/amr_n26"),
]


def git_show(home, ref, path):
    r = subprocess.run(["git", "-C", home, "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def read(home, path):
    """A file of the main checkout; a link (athena.log -> athena.<stamp>.log) is followed
    only to a file in the same directory."""
    p = os.path.join(home, path)
    if os.path.islink(p):
        q = os.path.realpath(p)
        if os.path.dirname(q) != os.path.realpath(os.path.dirname(p)):
            return None
        p = q
    if not os.path.isfile(p):
        return None
    with open(p, "rb") as f:
        return f.read(16 << 20).decode("utf-8", "replace")


def check(home, ref):
    rows, checks = [], []
    cache = {}

    def at(path, commit=ref):
        k = (commit, path)
        if k not in cache:
            cache[k] = git_show(home, commit, path)
        return cache[k]

    for key, area, verdict, entries, recs, reach, outcome, note in LINKS:
        res = []
        for f, line, head, commit in entries:
            txt = at(f)
            ok = bool(txt) and txt.splitlines()[line - 1].startswith(head)
            res.append(("entry", f"{f}:{line}", ok))
            first = at(f, commit)
            res.append(("entry-commit", f"{commit}:{f}", bool(first) and head in first))
        for path, needle in recs:
            txt = read(home, path) if path.startswith("runs/") else at(path)
            res.append(("record", f"{path} ~ {needle!r}", bool(txt) and needle in txt))
        for path, line, needle in reach:
            txt = at(path)
            ok = bool(txt) and len(txt.splitlines()) >= line and needle in txt.splitlines()[line - 1]
            res.append(("reach", f"{path}:{line}@{ref[:8]}", ok))
        checks.append({"link_key": key, "checks": [{"kind": a, "locator": b, "ok": c} for a, b, c in res]})
        nok = sum(1 for r in res if r[2])
        rows.append({"link_key": key, "area": area, "verdict": verdict,
                     "test_entries": "; ".join(f"{f}:{ln} ({c})" for f, ln, _, c in entries) or "-",
                     "records": "; ".join(sorted({p.split('/')[0] + '/' + '/'.join(p.split('/')[1:3])
                                                  if p.startswith('runs/') else p for p, _ in recs})) or "-",
                     "reach": "; ".join(f"{p}:{ln}" for p, ln, _ in reach) or "-",
                     "outcome": outcome or "-", "note": note or "-",
                     "checks": f"{nok}/{len(res)}"})
    return rows, checks


def nco_scan(home, ref):
    """Every occurrence of the token nco in athenak/src at ref (git grep, word match)."""
    r = subprocess.run(["git", "-C", home, "grep", "-n", "-w", "nco", ref, "--", "athenak/src"],
                       capture_output=True)
    hits = [ln.split(":", 1)[1] for ln in r.stdout.decode().splitlines()]
    reads = [h for h in hits if '"nco"' in h]
    return {"hits": hits, "parameter_reads": reads}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--home", default="/data/haiyangw/nrpic")
    ap.add_argument("--ref", default="47ab19ab7162e5dc8839958c1409b1947c3055c8")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows, checks = check(a.home, a.ref)
    cols = ["link_key", "area", "verdict", "test_entries", "records", "reach", "outcome", "note", "checks"]
    with open(os.path.join(a.out, "LINKS.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(r[c].replace("\t", " ") for c in cols) + "\n")
    nco = nco_scan(a.home, a.ref)
    bad = [(c["link_key"], x["locator"]) for c in checks for x in c["checks"] if not x["ok"]]
    out = {"ref": a.ref, "links": rows, "checks": checks, "failed_checks": bad, "nco": nco,
           "counts": {v: sum(1 for r in rows if r["verdict"] == v) for v in (V, C, F)}}
    with open(os.path.join(a.out, "link_evidence.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"links {len(rows)}; verdicts {out['counts']}; checks {sum(len(c['checks']) for c in checks)}, "
          f"failed {len(bad)}")
    for k, loc in bad:
        print(f"FAILED {k}: {loc}")
    print(f"nco in athenak/src at {a.ref[:8]}: {len(nco['hits'])} lines, parameter reads {len(nco['parameter_reads'])}")
    for h in nco["hits"]:
        print("  " + h)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
