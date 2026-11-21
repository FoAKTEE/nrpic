// Kernel timer for the Kokkos tools interface: wall-clock time per named kernel
// (parallel_for, parallel_reduce, parallel_scan), summed over the run, and the time
// outside any kernel. Analysis tool of work package omp; not part of the simulation code.
//
//   g++ -O2 -shared -fPIC -o libkernel_timer.so kernel_timer.cpp
//   KOKKOS_TOOLS_LIBS=/path/libkernel_timer.so KERNEL_TIMER_OUT=kernels.txt athena -i ...
//
// Kernels are entered from the main thread only (no nested dispatch from inside a
// kernel is timed), so no locking is needed. Output: one line per kernel,
// "seconds calls type name", sorted by time, then the total and the run time.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#include <vector>

namespace {
using Clock = std::chrono::steady_clock;
struct Entry { double seconds = 0.0; std::uint64_t calls = 0; char type = '?'; };
std::map<std::string, Entry> table;
std::vector<std::string> names;                 // kernel id -> name
std::vector<Clock::time_point> starts;          // kernel id -> start of the running call
Clock::time_point t_init;
int depth = 0;

void Begin(const char *name, std::uint64_t *kid, char type) {
  std::string key = std::string(1, type) + " " + (name ? name : "(unnamed)");
  *kid = names.size();
  names.push_back(key);
  starts.push_back(Clock::now());
  table[key].type = type;
  ++depth;
}
void End(std::uint64_t kid) {
  const double dt = std::chrono::duration<double>(Clock::now() - starts[kid]).count();
  Entry &e = table[names[kid]];
  // only outermost kernels count toward the sum (nested team loops are part of them)
  if (depth == 1) { e.seconds += dt; }
  e.calls += 1;
  --depth;
  if (depth == 0) { names.clear(); starts.clear(); }
}
} // namespace

extern "C" {
void kokkosp_init_library(const int, const std::uint64_t, const std::uint32_t, void *) {
  t_init = Clock::now();
}
void kokkosp_finalize_library() {
  const double run = std::chrono::duration<double>(Clock::now() - t_init).count();
  const char *out = std::getenv("KERNEL_TIMER_OUT");
  std::FILE *fp = std::fopen(out ? out : "kernel_timer.txt", "w");
  if (fp == nullptr) return;
  std::vector<std::pair<double, std::string>> rows;
  double total = 0.0;
  for (auto &kv : table) {
    rows.push_back({kv.second.seconds, kv.first});
    total += kv.second.seconds;
  }
  std::sort(rows.rbegin(), rows.rend());
  std::fprintf(fp, "# seconds calls type name\n");
  for (auto &r : rows) {
    std::fprintf(fp, "%.6f %llu %s\n", r.first,
                 static_cast<unsigned long long>(table[r.second].calls), r.second.c_str());
  }
  std::fprintf(fp, "# total_in_kernels %.6f\n# run_time %.6f\n", total, run);
  std::fclose(fp);
}
void kokkosp_begin_parallel_for(const char *n, const std::uint32_t, std::uint64_t *k) {
  Begin(n, k, 'F');
}
void kokkosp_end_parallel_for(const std::uint64_t k) { End(k); }
void kokkosp_begin_parallel_reduce(const char *n, const std::uint32_t, std::uint64_t *k) {
  Begin(n, k, 'R');
}
void kokkosp_end_parallel_reduce(const std::uint64_t k) { End(k); }
void kokkosp_begin_parallel_scan(const char *n, const std::uint32_t, std::uint64_t *k) {
  Begin(n, k, 'S');
}
void kokkosp_end_parallel_scan(const std::uint64_t k) { End(k); }
}
