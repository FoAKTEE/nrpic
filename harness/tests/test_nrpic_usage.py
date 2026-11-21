#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-usage with recorded event streams and a simulated clock.

    python3 -I harness/tests/test_nrpic_usage.py [--trace FILE]

No call reaches the service: the module is imported, its call_service is replaced by a function that
fails the test if it is ever reached, and every Usage gets a replay of stream-json outputs instead. The
streams are built from the rate_limit_event recorded on 2026-11-19 (seven_day window only) and from the
shape of the readings of 2026-11-20 (five_hour and seven_day); the full recording in
scratch/orch/usage/probe.jsonl is parsed as well when it exists. Every flag and reading is written under
a scratch root scratch/harness/test-usage-<UTC>-<pid>/, never under the live locks/: the test checks
that the live locks/PAUSE is as it was. The root, the service and the clock are parameters of
Usage(...) only; the command line has none.

Covers: parsing (recorded stream, both windows, no event, an error result, junk lines); watch writes
locks/PAUSE at the threshold of the weekly and of the five-hour window, probes faster above --near,
treats six probes without a reading as at the threshold (flag "unknown", exit 3); resume sleeps until
the tripped window's reset (no probe before it), removes the flag when that window is below --near and
the others below --launch-max, holds it (flag rewritten) while another window is above --launch-max,
retries while the tripped window is still high; watch --cycle pauses and resumes twice by itself; the
command line through main(); `show`. --trace writes the simulated week of the cycle test for the figure
(harness/tests/usage_selftest_fig.py).
"""
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.realpath(__file__))
LIVE = os.path.realpath(os.path.join(HERE, "..", ".."))
TOOL = os.path.join(LIVE, "harness", "bin", "nrpic-usage")

# the rate_limit_event recorded on 2026-11-19 07:21 PST (ids zeroed), and the windows' shape of 2026-11-20
RECORDED_EVENT = {"type": "rate_limit_event", "rate_limit_info": {
    "status": "allowed_warning", "resetsAt": 1795125600, "rateLimitType": "seven_day", "utilization": 0.76,
    "overageStatus": "rejected", "overageDisabledReason": "org_level_disabled", "isUsingOverage": False,
    "surpassedThreshold": 0.75, "unifiedWindows": {"seven_day": {
        "utilization": 0.76, "resetsAt": 1795125600, "status": "allowed_warning", "surpassedThreshold": 0.75}},
    "overageEnabled": False}, "uuid": "00000000-0000-0000-0000-000000000000",
    "session_id": "00000000-0000-0000-0000-000000000000"}
FRAME = [{"type": "system", "subtype": "init", "session_id": "0"},
         {"type": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}, "session_id": "0"}]
RESULT = {"type": "result", "subtype": "success", "is_error": False, "result": "ok", "session_id": "0"}


def stream(seven=None, seven_reset=None, five=None, five_reset=None, recorded=False, error=None):
    """A stream-json output as the probe's call prints it."""
    lines = [json.dumps(x) for x in FRAME]
    if recorded:
        lines.append(json.dumps(RECORDED_EVENT))
    elif seven is not None or five is not None:
        uw = {}
        if five is not None:
            uw["five_hour"] = {"utilization": five / 100.0, "resetsAt": five_reset, "status": "allowed"}
        if seven is not None:
            uw["seven_day"] = {"utilization": seven / 100.0, "resetsAt": seven_reset, "status": "allowed"}
        main_w = max(uw, key=lambda k: uw[k]["utilization"])
        lines.append(json.dumps({"type": "rate_limit_event", "rate_limit_info": {
            "status": "allowed", "resetsAt": uw[main_w]["resetsAt"], "rateLimitType": main_w,
            "utilization": uw[main_w]["utilization"], "isUsingOverage": False, "unifiedWindows": uw,
            "overageEnabled": None}}))
    lines.append("not json at all")
    lines.append(json.dumps(dict(RESULT, is_error=bool(error), result=error or "ok")))
    return "\n".join(lines) + "\n"


class Stop(BaseException):
    """Ends a test of a loop that never returns by itself (not an Exception: probe() catches those)."""


class Clock:
    def __init__(self, t0):
        self.t = float(t0)
        self.sleeps = []

    def __call__(self):
        return self.t

    def sleep(self, dt):
        self.sleeps.append(dt)
        self.t += dt


class Replay:
    """The service: each call returns the next scripted reading. An item is a stream text, a callable
    of the time (for scenarios), an Exception to raise (no reading), or Stop."""

    def __init__(self, clock, items):
        self.clock, self.items, self.calls = clock, list(items), []

    def __call__(self, cwd):
        self.calls.append(self.clock())
        if not self.items:
            raise Stop()
        it = self.items.pop(0)
        if callable(it) and not isinstance(it, type):
            it = it(self.clock())
        if isinstance(it, type) and issubclass(it, BaseException):
            raise it()
        if isinstance(it, BaseException):
            raise it
        return 0, it


class Checks:
    def __init__(self, title):
        self.title, self.rows = title, []
        print(f"== {title}")

    def ok(self, cond, what, detail=""):
        self.rows.append((bool(cond), what))
        print(f"  {'PASS' if cond else 'FAIL'}  {what}" + (f"\n        {detail}" if detail and not cond else ""))
        return bool(cond)

    def done(self):
        bad = [w for c, w in self.rows if not c]
        print(f"== {self.title}: {len(self.rows) - len(bad)}/{len(self.rows)} passed")
        return 1 if bad else 0


def load_tool():
    loader = importlib.machinery.SourceFileLoader("nrpic_usage_under_test", TOOL)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def live_home():
    common = subprocess.run(["git", "-C", LIVE, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, check=True,
                            env={"PATH": "/usr/bin:/bin", "HOME": os.path.expanduser("~")}).stdout.strip()
    return os.path.dirname(common)


def flag_state(path):
    try:
        st = os.stat(path)
        return (True, st.st_mtime_ns, open(path).read())
    except FileNotFoundError:
        return (False, None, None)


def main():
    trace_out = sys.argv[sys.argv.index("--trace") + 1] if "--trace" in sys.argv else None
    home = live_home()
    live_flag = os.path.join(home, "locks", "PAUSE")
    live_before = flag_state(live_flag)
    U = load_tool()
    reached = []

    def forbidden(cwd):
        reached.append(cwd)
        raise AssertionError("the test reached the service")
    U.call_service = forbidden
    base = os.path.join(home, "scratch", "harness", f"test-usage-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}")
    os.makedirs(base)
    c = Checks(f"nrpic-usage (scratch roots under {base})")
    n = [0]

    def fresh(t0, items):
        n[0] += 1
        rt = os.path.join(base, f"root{n[0]}")
        os.makedirs(rt)
        clk = Clock(t0)
        rp = Replay(clk, items)
        out = io.StringIO()
        return U.Usage(rt, service=rp, clock=clk, sleep=clk.sleep, out=out), clk, rp, out, rt

    # 1. parsing
    r = U.parse_stream(0, stream(recorded=True), 1795000000)
    c.ok(r["ok"] and r["windows"] == {"seven_day": {"pct": 76.0, "resets_at": 1795125600, "status": "allowed_warning"}}
         and r["overage_enabled"] is False and r["using_overage"] is False,
         "the recorded rate_limit_event of 2026-11-19: weekly 76 per cent, its reset time and status", json.dumps(r))
    r = U.parse_stream(0, stream(seven=51, seven_reset=1795215600, five=3, five_reset=1795229400), 1795212003)
    c.ok(r["ok"] and r["windows"]["seven_day"]["pct"] == 51.0 and r["windows"]["five_hour"]["pct"] == 3.0
         and r["windows"]["five_hour"]["resets_at"] == 1795229400, "both windows of the 2026-11-20 shape", json.dumps(r))
    r = U.parse_stream(1, stream(error="rate limited"), 1)
    c.ok(not r["ok"] and r["error"] == "rate limited" and r["windows"] == {}, "an error result: no reading", json.dumps(r))
    r = U.parse_stream(0, stream(), 1)
    c.ok(not r["ok"] and "no rate_limit_event" in r["error"], "a stream without the event: no reading", json.dumps(r))
    r = U.parse_stream(0, stream(five=50, five_reset=10), 1)
    c.ok(not r["ok"] and r["windows"].get("five_hour", {}).get("pct") == 50.0,
         "a stream with the five-hour window only is not a reading (the weekly one is required)", json.dumps(r))
    raw = os.path.join(home, "scratch", "orch", "usage", "probe.jsonl")
    if os.path.isfile(raw):
        r = U.parse_stream(0, open(raw, errors="replace").read(), 1)
        c.ok(r["ok"] and r["windows"]["seven_day"]["pct"] == 76.0,
             "the full recording scratch/orch/usage/probe.jsonl (hooks, init, assistant, result) parses", json.dumps(r))

    T0 = 1795212000.0
    W_RESET, F_RESET = T0 + 4 * 86400, T0 + 3 * 3600

    # 2. watch: the weekly window reaches the threshold
    u, clk, rp, out, rt = fresh(T0, [stream(seven=80, seven_reset=W_RESET, five=10, five_reset=F_RESET),
                                     stream(seven=92, seven_reset=W_RESET, five=20, five_reset=F_RESET),
                                     stream(seven=95.2, seven_reset=W_RESET, five=30, five_reset=F_RESET)])
    rc = u.watch(95, 240, 90, 75)
    fl = json.load(open(os.path.join(rt, "locks", "PAUSE")))
    c.ok(rc == 0 and fl["window"] == "seven_day" and fl["pct"] == 95.2 and fl["resets_at"] == W_RESET
         and fl["threshold"] == 95 and "PAUSE seven_day usage 95%" in out.getvalue(),
         "watch: weekly 95.2 per cent writes locks/PAUSE (window, pct, reset time) and exits 0", out.getvalue())
    c.ok(clk.sleeps == [240, 75], "watch: --interval below --near, --near-interval above it", str(clk.sleeps))
    log = open(os.path.join(rt, "locks", "usage.log")).read().splitlines()
    c.ok(len(log) == 3 and json.load(open(os.path.join(rt, "locks", "usage.json")))["windows"]["seven_day"]["pct"] == 95.2,
         "watch: every reading appended to usage.log, the last one in usage.json (scratch root)")

    # 3. watch: the five-hour window reaches the threshold while the weekly one is low
    u, clk, rp, out, rt = fresh(T0, [stream(seven=40, seven_reset=W_RESET, five=94.9, five_reset=F_RESET),
                                     stream(seven=41, seven_reset=W_RESET, five=96, five_reset=F_RESET)])
    rc = u.watch(95, 240, 90, 75)
    fl = json.load(open(os.path.join(rt, "locks", "PAUSE")))
    c.ok(rc == 0 and fl["window"] == "five_hour" and fl["resets_at"] == F_RESET and clk.sleeps == [75],
         "watch: five-hour 96 per cent (weekly 41) writes the flag with the five-hour reset time; 94.9 did not",
         json.dumps(fl) + " " + str(clk.sleeps))

    # 4. watch: six probes without a reading are treated as at the threshold (decision 0018)
    u, clk, rp, out, rt = fresh(T0, [stream(seven=50, seven_reset=W_RESET), RuntimeError("timeout"), stream(),
                                     stream(error="overloaded"), OSError("no claude"),
                                     stream(seven=50, seven_reset=W_RESET), RuntimeError("x")] + [stream()] * 5)
    rc = u.watch(95, 240, 90, 75)
    fl = json.load(open(os.path.join(rt, "locks", "PAUSE")))
    c.ok(rc == 3 and fl["window"] == "unknown" and fl["resets_at"] is None and len(rp.calls) == 12
         and "UNKNOWN" in out.getvalue() and clk.sleeps.count(60) == 9,
         "watch: six probes in a row without a reading (a reading in between resets the count): flag 'unknown', exit 3",
         out.getvalue()[-400:] + f" calls={len(rp.calls)}")

    # 5. resume: the five-hour window tripped; weekly at 70 does not hold the flag (--near 60, --launch-max 90)
    u, clk, rp, out, rt = fresh(T0, [stream(seven=70, seven_reset=W_RESET, five=2, five_reset=F_RESET + 5 * 3600)])
    u.write_flag("five_hour", 96.0, F_RESET, 95)
    rc = u.resume(60, 90)
    c.ok(rc == 0 and not os.path.exists(u.flag) and rp.calls and min(rp.calls) >= F_RESET + 90
         and "RESUME five_hour" in out.getvalue(),
         "resume: no probe before the five-hour reset (+90 s), then the flag is removed although weekly is at 70",
         out.getvalue() + f" first probe at reset+{(min(rp.calls) - F_RESET) if rp.calls else None}")
    c.ok(all(s <= 900 for s in clk.sleeps) and abs(sum(clk.sleeps) - (F_RESET + 90 - T0)) < 1,
         "resume: waits in steps of at most 15 minutes, exactly to the reset", str(clk.sleeps[:3]))

    # 6. resume: weekly tripped; after its reset the five-hour window is at 93 (above --launch-max): hold, flag
    # rewritten with the five-hour reset, then removed after that one
    w_reset = T0 + 3600
    f2 = w_reset + 2 * 3600
    u, clk, rp, out, rt = fresh(T0, [stream(seven=1, seven_reset=w_reset + 7 * 86400, five=93, five_reset=f2),
                                     stream(seven=4, seven_reset=w_reset + 7 * 86400, five=1, five_reset=f2 + 5 * 3600)])
    u.write_flag("seven_day", 95.3, w_reset, 95)
    rc = u.resume(60, 90)
    c.ok(rc == 0 and not os.path.exists(u.flag) and "HOLD five_hour" in out.getvalue() and len(rp.calls) == 2
         and rp.calls[0] >= w_reset + 90 and rp.calls[1] >= f2 + 90,
         "resume: a second window above --launch-max holds the pause until its own reset, then the flag goes",
         out.getvalue() + str([c_ - T0 for c_ in rp.calls]))

    # 7. resume: the tripped window is still high just after its reset (late reset): retry after 300 s
    u, clk, rp, out, rt = fresh(T0, [stream(seven=97, seven_reset=T0 + 100), stream(seven=0.5, seven_reset=T0 + 7 * 86400)])
    u.write_flag("seven_day", 95.0, T0 + 10, 95)
    rc = u.resume(60, 90)
    c.ok(rc == 0 and not os.path.exists(u.flag) and len(rp.calls) == 2 and abs(rp.calls[1] - rp.calls[0] - 300) < 1,
         "resume: still above --near after the reset time: probes again five minutes later", str(clk.sleeps))

    # 8. resume waits for a flag to appear; an unknown flag is checked at once and needs every window below
    # --launch-max
    u, clk, rp, out, rt = fresh(T0, [stream(seven=50, seven_reset=W_RESET, five=10, five_reset=F_RESET)])
    u.write_flag("unknown", None, None, 95)
    rc = u.resume(60, 90)
    c.ok(rc == 0 and not os.path.exists(u.flag) and len(rp.calls) == 1, "resume: an 'unknown' flag is lifted by the "
         "first reading with every window below --launch-max", out.getvalue())
    u, clk, rp, out, rt = fresh(T0, [stream(seven=10, seven_reset=W_RESET)])
    rc = u.resume(60, 90, wait_for_flag=False)
    c.ok(rc == 0 and not rp.calls and not os.path.exists(u.flag), "resume (inside --cycle): nothing to do without a flag")

    # 9. watch --cycle over 60 simulated hours: a burst of the five-hour window in hours 20 to 30 (it climbs
    # 22 points an hour within each five-hour window), the weekly window climbing 0.9 points an hour from 60
    # until its reset at hour 48. Expected: five-hour pauses at about hours 24 and 29 (resumed at the resets
    # 25 and 30; weekly then 82.5 and 87, below --launch-max 90), a weekly pause at about hour 39 (resumed at
    # hour 48), all with no outside step.
    trace = []
    week0 = T0

    def scenario(t):
        h = (t - week0) / 3600.0
        if h > 60:
            raise Stop()
        f_reset = week0 + (int(h // 5) + 1) * 5 * 3600
        five = min(99.0, 8.0 + 22.0 * (h % 5)) if 20 <= h < 30 else 5.0
        seven = min(99.0, 60.0 + 0.9 * h) if h < 48 else 3.0 + 0.2 * (h - 48)
        s_reset = week0 + 48 * 3600 if h < 48 else week0 + (48 + 168) * 3600
        trace.append({"t": t, "five": round(five, 3), "seven": round(seven, 3)})
        return stream(seven=seven, seven_reset=s_reset, five=five, five_reset=f_reset)

    u, clk, rp, out, rt = fresh(week0, [scenario] * 5000)
    said = []
    orig_say = u.say

    def say(s):
        said.append((clk.t, s))
        return orig_say(s)
    u.say = say
    try:
        u.watch(95, 240, 88, 60, cycle=True)
        rc = "returned"
    except Stop:
        rc = "stopped"
    ev = [(round((t - week0) / 3600.0, 2), s.split()[0], s.split()[1]) for t, s in said
          if s.split() and s.split()[0] in ("PAUSE", "RESUME", "HOLD")]
    kinds = [e[1] for e in ev]
    wins = [e[2] for e in ev if e[1] == "PAUSE"]
    hours = [e[0] for e in ev]
    c.ok(rc == "stopped" and kinds == ["PAUSE", "RESUME"] * 3 and wins == ["five_hour", "five_hour", "seven_day"]
         and abs(hours[0] - 24.0) < 0.1 and 25.0 < hours[1] < 25.1 and abs(hours[2] - 29.0) < 0.1
         and 30.0 < hours[3] < 30.1 and abs(hours[4] - 38.9) < 0.1 and 48.0 < hours[5] < 48.1
         and not os.path.exists(u.flag),
         "watch --cycle: two five-hour pauses and one weekly pause, each lifted just after its window's reset, "
         "with no outside step", str(ev))
    paused = 0.0
    for k in range(0, len(ev) - 1, 2):
        paused += ev[k + 1][0] - ev[k][0]
    c.ok(abs(paused - (1.0 + 1.0 + 9.1)) < 0.4, f"watch --cycle: {paused:.1f} of 60 hours paused (expected about 11.1)")
    if trace_out:
        json.dump({"t0": week0, "trace": trace, "events": [[t, s] for t, s in said], "threshold": 95, "near": 88,
                   "launch_max": 90}, open(trace_out, "w"), indent=1)

    # 10. the command line through main(), and show
    u, clk, rp, out, rt = fresh(T0, [stream(seven=96, seven_reset=W_RESET)])
    rc = U.main(["watch", "--threshold", "95", "--interval", "180", "--near", "88", "--near-interval", "60"], usage=u)
    c.ok(rc == 0 and os.path.exists(u.flag), "main(['watch', ...]) with the orchestrator's options writes the flag")
    rc = U.main(["show"], usage=u)
    c.ok(rc == 0 and "seven_day 96%" in out.getvalue().splitlines()[-1], "show prints the stored reading",
         out.getvalue()[-200:])
    u2, clk2, rp2, out2, rt2 = fresh(T0, [stream(seven=1, seven_reset=W_RESET)])
    shutil.copyfile(u.flag, u2.flag) if os.path.isdir(u2.locks) else (os.makedirs(u2.locks), shutil.copyfile(u.flag, u2.flag))
    clk2.t = W_RESET + 100
    rc = U.main(["resume", "--near", "60"], usage=u2)
    c.ok(rc == 0 and not os.path.exists(u2.flag), "main(['resume', '--near', '60']) after the reset removes the flag")
    h = subprocess.run(["/usr/bin/python3", "-I", TOOL, "--help"], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": os.path.expanduser("~")})
    c.ok(h.returncode == 0 and "--root" not in h.stdout and "--cycle" in h.stdout and "--launch-max" in h.stdout,
         "the command line has no option for the root (test-only parameter of Usage)", h.stdout[-300:])

    # nothing reached the service, the live flag is untouched
    c.ok(not reached, "no call reached the service (call_service never called)")
    c.ok(flag_state(live_flag) == live_before, f"the live {live_flag} is as before the test "
         f"({'present' if live_before[0] else 'absent'})")
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
