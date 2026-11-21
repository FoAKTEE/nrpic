#!/usr/bin/env python3
"""Thread placement for a threaded processor run on a shared machine: picks the N
physical cores that are least busy right now, on as few NUMA nodes as possible, and
prints them as an OMP_PLACES list (one place per core, both hardware threads of it).

    OMP_PLACES=$(scripts/omp_places.py 16) OMP_PROC_BIND=true OMP_NUM_THREADS=16 athena ...
    scripts/omp_places.py 16 --verbose        # also says which cores and how busy they are

Why: OMP_PLACES=cores with OMP_PROC_BIND=spread or close binds every job of every
session to the same cores (0, 4, 9, ... or 0 to N-1), so two such jobs share cores while
others stand idle; without any binding the threads migrate and lose their memory
locality. A list of idle cores on one NUMA node avoids both. The arrays of AthenaK are
zero-filled by one thread (Kokkos), so their pages start on the NUMA node of the first
place; with all places on that node no thread reads remote memory.

Method: two readings of /proc/stat, --interval seconds apart; a core is as busy as the
sum of its hardware threads. The node with the most idle capacity among its N least busy
cores is taken; if a node has fewer than N cores, the least busy cores of the machine.
Standard library only; reads /proc and /sys, changes nothing.
"""
import argparse
import glob
import os
import re
import sys
import time


def cpu_times():
    out = {}
    with open("/proc/stat") as f:
        for ln in f:
            m = re.match(r"cpu(\d+)\s+(.*)", ln)
            if m:
                v = [int(x) for x in m.group(2).split()]
                idle = v[3] + (v[4] if len(v) > 4 else 0)
                out[int(m.group(1))] = (sum(v[:8]), idle)
    return out


def topology():
    """{(node, package, core id): [logical cpus]}"""
    node_of = {}
    for nd in glob.glob("/sys/devices/system/node/node[0-9]*"):
        n = int(re.search(r"node(\d+)$", nd).group(1))
        for c in glob.glob(os.path.join(nd, "cpu[0-9]*")):
            node_of[int(re.search(r"cpu(\d+)$", c).group(1))] = n
    cores = {}
    for c in glob.glob("/sys/devices/system/cpu/cpu[0-9]*"):
        cpu = int(re.search(r"cpu(\d+)$", c).group(1))
        try:
            with open(os.path.join(c, "topology", "core_id")) as f:
                core = int(f.read())
            with open(os.path.join(c, "topology", "physical_package_id")) as f:
                pkg = int(f.read())
        except OSError:
            continue
        cores.setdefault((node_of.get(cpu, pkg), pkg, core), []).append(cpu)
    return {k: sorted(v) for k, v in cores.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("n", type=int, help="number of threads (one core each)")
    ap.add_argument("--interval", type=float, default=0.5)
    ap.add_argument("--node", type=int, default=-1, help="take the cores from this NUMA node")
    ap.add_argument("--one-thread-per-core", action="store_true",
                    help="places of one hardware thread instead of both threads of a core")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    cores = topology()
    allowed = os.sched_getaffinity(0)
    cores = {k: [c for c in v if c in allowed] for k, v in cores.items()}
    cores = {k: v for k, v in cores.items() if v}
    if a.n < 1 or a.n > len(cores):
        sys.exit("omp_places: %d threads asked, %d cores available" % (a.n, len(cores)))
    t0 = cpu_times()
    time.sleep(a.interval)
    t1 = cpu_times()
    busy = {}
    for key, cpus in cores.items():
        b = 0.0
        for c in cpus:
            tot = t1[c][0] - t0[c][0]
            b += (1.0 - (t1[c][1] - t0[c][1])/tot) if tot > 0 else 0.0
        busy[key] = b                         # 0 (idle) to number of hardware threads
    nodes = sorted({k[0] for k in cores})
    best = None
    for nd in ([a.node] if a.node >= 0 else nodes):
        mine = sorted((busy[k], k) for k in cores if k[0] == nd)
        if len(mine) >= a.n:
            cost = sum(b for b, _ in mine[:a.n])
            if best is None or cost < best[0]:
                best = (cost, [k for _, k in mine[:a.n]])
    if best is None:
        mine = sorted((busy[k], k) for k in cores)
        best = (sum(b for b, _ in mine[:a.n]), [k for _, k in mine[:a.n]])
    chosen = sorted(best[1])
    places = []
    for k in chosen:
        cpus = cores[k][:1] if a.one_thread_per_core else cores[k]
        places.append("{" + ",".join(str(c) for c in cpus) + "}")
    if a.verbose:
        sys.stderr.write("omp_places: node(s) %s, mean load of the chosen cores %.2f "
                         "(of 2), of all cores %.2f\n" % (
                             sorted({k[0] for k in chosen}), best[0]/a.n,
                             sum(busy.values())/len(busy)))
    print(",".join(places))


if __name__ == "__main__":
    main()
