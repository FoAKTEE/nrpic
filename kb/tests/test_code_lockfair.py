"""The writer lock is not starved by a writer that releases and re-takes it in a loop (seen
on 2026-11-15: the code ingest waited minutes while the paper ingest took the lock paper
after paper; kbtool.lock now waits in the kernel)."""
import fcntl
import multiprocessing as mp
import os
import time

from kbtool import lock, paths


def _churn(path, seconds, ready):
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o664)
    t0 = time.monotonic()
    fcntl.flock(fd, fcntl.LOCK_EX)
    ready.set()
    while time.monotonic() - t0 < seconds:
        time.sleep(0.05)                       # hold
        fcntl.flock(fd, fcntl.LOCK_UN)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)   # re-take at once, as a polling writer would
        except BlockingIOError:
            fcntl.flock(fd, fcntl.LOCK_EX)
    os.close(fd)


def test_waiter_gets_lock_from_a_churning_holder(tmp_path):
    lay = paths.Layout(home=str(tmp_path), data=str(tmp_path / "data"), lock=str(tmp_path / "w.lock"))
    ctx = mp.get_context("fork")
    ready = ctx.Event()
    p = ctx.Process(target=_churn, args=(lay.lock, 6.0, ready))
    p.start()
    try:
        assert ready.wait(5)
        t0 = time.monotonic()
        with lock.writer_lock(lay, timeout=5.0, what="fair"):
            waited = time.monotonic() - t0
        assert waited < 2.0
    finally:
        p.join(10)
