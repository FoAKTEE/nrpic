"""Card cost of one realisation: the track's model (SCOPE.md section 8, cost.json of run
E-20261115-140116-87c1cc5, identical to E-stoch-inf-20261115-123936-b2ec5c7) and the same
step counts with core's measured card throughput (run core-20261115-143907-cea4c86: one
A100, 128^3, MeshBlock 64^3, k_max = 32 dk; Z4c alone, with the field, with the sources).

Extrapolation [JUDGEMENT]: the per-cell cost of Z4c with the field is taken as measured at
128^3 for every N; the extra per-cell cost of the stochastic sources is scaled with the
per-cell operation count of the separable synthesis (d2.json of the same codebase run,
Hermitian count) from (N = 128, MeshBlock 64) to (N, MeshBlock b). At N = 256 the range
spans MeshBlock 128 (lower) to 64 (upper).
"""
import common as C

CODEBASE = "E-20261115-140116-87c1cc5"
CORE = "core-20261115-143907-cea4c86"


def inputs():
    cost = C.load_json(CODEBASE, "cost.json")
    d2 = C.load_json(CODEBASE, "d2.json")
    core = C.load_json(CORE, "summary.json")
    return cost, d2, core


def table():
    cost, d2, core = inputs()
    per_cell = {(r["N"], r["block"]): r["per_cell_hermitian"] for r in d2["ops_table"]}
    t_field = 1.0 / core["field"]["zone_cycles_per_s"]
    t_noise128 = 1.0 / core["noise"]["zone_cycles_per_s"] - t_field
    c_ref = per_cell[(core["n"], core["block"])]
    rows = []
    for r in cost["rows"]:
        if r["theta"] != 0.25 or r["noise_per"] != "stage":
            continue
        N, steps = r["N"], r["steps"]
        blocks = [b for b in (64, 128) if (N, b) in per_cell and b <= N]
        hours = []
        for b in blocks:
            t_cell = t_field + t_noise128 * per_cell[(N, b)] / c_ref
            hours.append(steps * N ** 3 * t_cell / 3600.0)
        rows.append(dict(N=N, case=r["case"], steps=steps, model=r["card_hours"],
                         sec_per_step_model=r["sec_per_step"],
                         measured_lo=min(hours), measured_hi=max(hours),
                         sec_per_step_lo=min(hours) * 3600.0 / steps,
                         sec_per_step_hi=max(hours) * 3600.0 / steps,
                         memory_GB=r["memory_GB"]))
    meta = dict(z4c=core["z4c"]["zone_cycles_per_s"], field=core["field"]["zone_cycles_per_s"],
                noise=core["noise"]["zone_cycles_per_s"], n=core["n"], block=core["block"],
                nmax2=core["nmax2"], modes=core["modes"],
                overhead_measured=core["z4c"]["zone_cycles_per_s"] / core["noise"]["zone_cycles_per_s"] - 1.0,
                overhead_assumed=cost["inputs"]["sf_rhs_overhead"][0],
                z4c_assumed=cost["inputs"]["z4c_gpu_zcps"][0])
    return rows, meta
