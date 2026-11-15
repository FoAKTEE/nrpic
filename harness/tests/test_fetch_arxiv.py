#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-fetch-arxiv against a local server: no request leaves the machine.

    python3 -I harness/tests/test_fetch_arxiv.py [--script PATH]

A scratch repository under <main checkout>/scratch/harness/ holds a copy of the command (and a
linked worktree wt/kb with its own copy), so its kb-data/ and locks/ are the scratch repository's.
The command is pointed at a loopback HTTP server with --test-server (accepted for loopback URLs
only) and a shorter gap (--test-gap, only with --test-server). Covered: e-print archive, HTML error
page refused, gzipped PostScript kept with a hint, unsafe and oversize members, gzip bomb, size
limit, 503 with Retry-After, no refetch of a complete entry, PDF mode (beside the e-print, version
from its record; a truncated PDF refused), arXiv API metadata in one batch (id set checked, DOCTYPE
refused, its own directory), INSPIRE metadata (eprint matched, a cut answer asked again id by id),
INSPIRE query, the gap between two requests to one service also across two processes, the
generic client name and no other identifying header, the caller's environment ignored (proxy,
GIT_DIR), the worktree's copy writing into the main checkout's store, --check, refusals.
"""
import gzip
import http.server
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402

AGENT = "literature-mirror/0.2 (research literature reading tool)"
GAP = 0.4


def targz(files, links=()):
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w:gz") as t:
        for name, data in files:
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
        for name, target in links:
            ti = tarfile.TarInfo(name)
            ti.type = tarfile.SYMTYPE
            ti.linkname = target
            t.addfile(ti)
    return bio.getvalue()


TEX = b"\\documentclass{article}\\begin{document}\\title{T}hello\\end{document}\n"
PDF = b"%PDF-1.4\n1 0 obj\n<< >>\nendobj\ntrailer\n<< >>\n%%EOF\n"
EPRINTS = {
    "2401.00001": (targz([("main.tex", TEX), ("fig.png", b"\x89PNG....")]), "arXiv-2401.00001v3.tar.gz"),
    "2401.00002": (b"<!DOCTYPE html><html><body>Rate limited</body></html>", None),
    "gr-qc/9412071": (gzip.compress(b"%!PS-Adobe-2.0\n%%Title: old paper\nshowpage\n"), "arXiv-gr-qc9412071v2.ps.gz"),
    "2401.00003": (targz([("ok.tex", TEX), ("../evil.tex", b"x"), ("/abs.tex", b"x"), ("big.dat", b"0" * (2 << 20))],
                         links=[("link", "/etc/passwd")]), "arXiv-2401.00003v1.tar.gz"),
    "2401.00004": (gzip.compress(b"\0" * (30 << 20)), "arXiv-2401.00004v1.gz"),
    "2401.00005": (b"x" * (2 << 20), "arXiv-2401.00005v1.gz"),
    "2401.00007": (targz([("main.tex", TEX)]), "arXiv-2401.00007v1.tar.gz"),
}
PDFS = {"gr-qc/9412071v2": PDF, "2401.00006": PDF[:-7]}
API_KNOWN = {"2401.00001": "v3", "gr-qc/9412071": "v2", "2401.00008": "v1"}
INSPIRE_KNOWN = {"2401.00001": 11, "gr-qc/9412071": 12, "2401.00008": 18, "2401.00011": 21}


class Server:
    def __init__(self):
        self.log = []                  # (t, service, path, headers)
        self.flaky = {"2401.00007": 1}
        srv = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def send(self, code, body, ctype="application/octet-stream", extra=None):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                for k, v in (extra or {}).items():
                    self.send_header(k, v)
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass                       # the client stopped reading at its size limit

            def do_GET(self):
                u = urllib.parse.urlsplit(self.path)
                q = urllib.parse.parse_qs(u.query)
                service = "inspire" if u.path.startswith("/api/literature") else "arxiv"
                srv.log.append((time.time(), service, self.path, dict(self.headers)))
                if u.path.startswith("/e-print/"):
                    aid = u.path[len("/e-print/"):]
                    if srv.flaky.get(aid):
                        srv.flaky[aid] -= 1
                        return self.send(503, b"busy", "text/plain", {"Retry-After": "1"})
                    if aid not in EPRINTS:
                        return self.send(404, b"no", "text/plain")
                    body, fn = EPRINTS[aid]
                    return self.send(200, body, extra={"Content-Disposition": f'attachment; filename="{fn}"'}
                                     if fn else None)
                if u.path.startswith("/pdf/"):
                    aid = u.path[len("/pdf/"):]
                    return self.send(200, PDFS[aid], "application/pdf") if aid in PDFS else self.send(404, b"no")
                if u.path == "/api/query":
                    ids = q.get("id_list", [""])[0].split(",")
                    if "2401.00009" in ids:
                        return self.send(200, b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><feed/>',
                                         "application/atom+xml")
                    ents = "".join(
                        f"<entry><id>http://arxiv.org/abs/{a}{API_KNOWN[a]}</id><title>Title of {a}</title>"
                        f"<summary>Abstract of {a}.</summary><author><name>A. Author</name></author>"
                        f"<author><name>B. Author</name></author><published>2024-01-01T00:00:00Z</published>"
                        f'<arxiv:primary_category term="gr-qc"/><category term="gr-qc"/><category term="astro-ph.CO"/>'
                        f"<arxiv:doi>10.1000/x.{a}</arxiv:doi></entry>" for a in ids if a in API_KNOWN)
                    feed = ('<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom" '
                            'xmlns:arxiv="http://arxiv.org/schemas/atom">' + ents + "</feed>").encode()
                    return self.send(200, feed, "application/atom+xml")
                if u.path == "/api/literature":
                    query = q.get("q", [""])[0]
                    ids = [t[len("arxiv:"):] for t in query.split() if t.startswith("arxiv:")]
                    hits = [{"metadata": {"control_number": INSPIRE_KNOWN[a], "arxiv_eprints": [{"value": a}],
                                          "titles": [{"title": f"Title of {a}"}]}} for a in ids if a in INSPIRE_KNOWN]
                    total = len(hits) + (5 if "2401.00008" in ids and len(ids) > 1 else 0)
                    return self.send(200, json.dumps({"hits": {"total": total, "hits": hits}}).encode(),
                                     "application/json")
                return self.send(404, b"no route", "text/plain")

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def count(self, frag):
        return sum(1 for _, _, p, _ in self.log if frag in p)


def make_repo(script):
    home = F.live_home()
    root = os.path.join(home, "scratch", "harness", f"fetch-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}")
    repo = os.path.join(root, "repo")
    os.makedirs(os.path.join(repo, "harness", "bin"))
    shutil.copy2(script, os.path.join(repo, "harness", "bin", "nrpic-fetch-arxiv"))
    open(os.path.join(repo, ".gitignore"), "w").write("wt/\nkb-data/\nlocks/\n")
    g = ["git", "-C", repo]
    F.sh(g + ["init", "-q", "-b", "main"])
    F.sh(g + ["-c", "user.name=t", "-c", "user.email=t@l", "add", "-A"])
    F.sh(g + ["-c", "user.name=t", "-c", "user.email=t@l", "commit", "-q", "-m", "fixture"])
    F.sh(g + ["worktree", "add", "-q", "-b", "kb/main", os.path.join(repo, "wt", "kb"), "main"])
    return root, repo


def main():
    script = os.path.join(F.LIVE, "harness", "bin", "nrpic-fetch-arxiv")
    if "--script" in sys.argv:
        script = os.path.abspath(sys.argv[sys.argv.index("--script") + 1])
    root, repo = make_repo(script)
    srv = Server()
    cmd = os.path.join(repo, "harness", "bin", "nrpic-fetch-arxiv")
    store = os.path.join(repo, "kb-data")
    c = F.Checks(f"nrpic-fetch-arxiv against a loopback server (scratch repo {repo})")
    elsewhere = os.path.join(root, "elsewhere")
    os.makedirs(elsewhere)

    def fetch(*args, env=None, test=True, script_path=cmd, cwd=elsewhere):
        extra = ["--test-server", srv.url, "--test-gap", str(GAP), "--test-max", "file=1048576",
                 "--test-max", "decompressed=10485760", "--test-max", "download=1048576"] if test else []
        return F.sh(["/usr/bin/python3", "-I", script_path] + extra + list(args), cwd=cwd, env=env, check=False,
                    timeout=300)

    def rec(*parts):
        p = os.path.join(store, "meta", *parts)
        return json.load(open(p)) if os.path.isfile(p) else None

    # 1. a good e-print, with a polluted caller environment (dead proxy, GIT_DIR) that must not matter
    polluted = dict(F.H.boot_env(), http_proxy="http://127.0.0.1:9", https_proxy="http://127.0.0.1:9",
                    HTTP_PROXY="http://127.0.0.1:9", GIT_DIR="/nonexistent", PYTHONPATH="/nonexistent")
    r = fetch("2401.00001", env=polluted)
    src = os.path.join(store, "raw", "arxiv", "2401.00001", "v3", "src")
    m = rec("arxiv", "2401.00001.json") or {}
    c.ok(r.returncode == 0 and r.stdout.strip() == src and os.path.isfile(os.path.join(src, "main.tex")),
         "e-print archive extracted under kb-data/raw/arxiv/<id>/<vN>/src; its path printed", r.stdout + r.stderr)
    c.ok(m.get("status") == "ok" and m.get("kind") == "tar" and m.get("tex_source") is True and m.get("version") == "v3",
         "download record ok, kind tar, version from Content-Disposition, TeX found", json.dumps(m)[:400])
    c.ok(r.returncode == 0 and srv.count("/e-print/2401.00001") == 1,
         "the caller's proxy variables and GIT_DIR were ignored (the request reached the loopback server directly)")
    hdrs = [h for _, _, p, h in srv.log if "2401.00001" in p][0]
    c.ok(hdrs.get("User-Agent") == AGENT and not any(k.lower() in ("from", "cookie", "authorization") for k in hdrs),
         f"generic client name ({AGENT}), no From, Cookie or Authorization header", str(hdrs))

    # 2. an HTML error page served with status 200 is not recorded as ok
    r = fetch("2401.00002")
    m = rec("arxiv", "2401.00002.json") or {}
    c.ok(r.returncode == 1 and m.get("status") == "failed" and "content check" in m.get("error", "")
         and not os.path.exists(os.path.join(store, "raw", "arxiv", "2401.00002")),
         "an HTML page with status 200: recorded as failed (content check), nothing stored", json.dumps(m) + r.stderr)

    # 3. gzipped PostScript: stored as before (src/main.tex), content and the hint say what it is
    r = fetch("gr-qc/9412071")
    m = rec("arxiv", "gr-qc_9412071.json") or {}
    c.ok(r.returncode == 0 and m.get("content") == "postscript" and m.get("tex_source") is False
         and "--pdf gr-qc/9412071" in r.stderr and m.get("version") == "v2",
         "gzipped PostScript: ok as served, content postscript, no TeX, a hint to fetch the PDF", json.dumps(m) + r.stderr)

    # 4. unsafe and oversize members
    r = fetch("2401.00003")
    m = rec("arxiv", "2401.00003.json") or {}
    src3 = os.path.join(store, "raw", "arxiv", "2401.00003", "v1", "src")
    outside = [p for p in (os.path.join(store, "raw", "arxiv", "2401.00003", "v1", "evil.tex"), "/abs.tex")
               if os.path.exists(p)]
    c.ok(r.returncode == 0 and set(m.get("skipped_members", [])) >= {"../evil.tex", "/abs.tex", "link"}
         and m.get("oversize_members") == ["big.dat"] and os.path.isfile(os.path.join(src3, "ok.tex"))
         and not outside and not os.path.lexists(os.path.join(src3, "link")),
         "links, parent and absolute paths skipped; a member above the per-file limit skipped and listed",
         json.dumps(m)[:600])

    # 5./6. size limits
    r = fetch("2401.00004")
    m = rec("arxiv", "2401.00004.json") or {}
    c.ok(r.returncode == 1 and "size limit" in m.get("error", ""), "a gzip bomb is refused (inflation limit)", json.dumps(m))
    r = fetch("2401.00005")
    m = rec("arxiv", "2401.00005.json") or {}
    c.ok(r.returncode == 1 and "size limit" in m.get("error", ""), "a download above the size limit is refused", json.dumps(m))

    # 7. 503 with Retry-After, then the e-print
    n0 = srv.count("/e-print/2401.00007")
    r = fetch("2401.00007")
    c.ok(r.returncode == 0 and srv.count("/e-print/2401.00007") - n0 == 2, "503 with Retry-After: retried once, then stored",
         r.stderr)

    # 8. a complete entry is not fetched again
    n0 = len(srv.log)
    r = fetch("2401.00001")
    c.ok(r.returncode == 0 and r.stdout.strip() == src and len(srv.log) == n0, "a complete entry is not fetched again")

    # 9./10. PDF mode
    r = fetch("--pdf", "gr-qc/9412071")
    pdf = os.path.join(store, "raw", "arxiv", "gr-qc_9412071", "v2", "source.pdf")
    m = rec("arxiv-pdf", "gr-qc_9412071.json") or {}
    c.ok(r.returncode == 0 and r.stdout.strip() == pdf and open(pdf, "rb").read() == PDF and m.get("status") == "ok"
         and srv.count("/pdf/gr-qc/9412071v2") == 1 and os.path.isfile(os.path.join(os.path.dirname(pdf), "source.bin")),
         "--pdf: source.pdf beside the e-print of the same version (v2 from its record), record in meta/arxiv-pdf/",
         r.stdout + r.stderr + json.dumps(m))
    r = fetch("--pdf", "2401.00006")
    m = rec("arxiv-pdf", "2401.00006.json") or {}
    c.ok(r.returncode == 1 and "%%EOF" in m.get("error", ""), "a truncated PDF is refused", json.dumps(m))

    # 11./12. arXiv API metadata
    n0 = srv.count("/api/query")
    r = fetch("--meta", "--service", "arxiv", "2401.00001", "gr-qc/9412071", "2401.00010")
    a1, a2, a3 = rec("arxiv-api", "2401.00001.json") or {}, rec("arxiv-api", "gr-qc_9412071.json") or {}, \
        rec("arxiv-api", "2401.00010.json") or {}
    c.ok(srv.count("/api/query") - n0 == 1, "three ids asked of the arXiv API in one request")
    c.ok(r.returncode == 1 and a1.get("status") == "ok" and a1.get("version") == "v3" and a1.get("title") == "Title of 2401.00001"
         and a1.get("authors") == ["A. Author", "B. Author"] and a1.get("categories") == ["gr-qc", "astro-ph.CO"]
         and a2.get("version") == "v2" and a3.get("status") == "not-found",
         "API records: version, title, authors, categories; an id missing from the answer is not-found (exit 1)",
         json.dumps([a1, a3])[:800])
    files = os.listdir(os.path.join(store, "meta", "arxiv"))
    c.ok(os.path.isfile(os.path.join(store, "meta", "arxiv-api", "2401.00001.xml"))
         and os.listdir(os.path.join(store, "meta", "arxiv-api", "batches"))
         and all(f.endswith(".json") and not f.endswith((".api.json", ".inspire.json")) for f in files),
         "the Atom entry and the batch as served are kept in meta/arxiv-api/; meta/arxiv/ holds download records only",
         str(files))
    r = fetch("--meta", "--service", "arxiv", "2401.00009")
    m = rec("arxiv-api", "2401.00009.json") or {}
    c.ok(r.returncode == 1 and "DOCTYPE" in m.get("error", ""), "an API answer with a DOCTYPE or entity is refused before parsing",
         json.dumps(m))

    # 13. INSPIRE
    n0 = srv.count("/api/literature")
    r = fetch("--meta", "--service", "inspire", "--batch", "5", "2401.00001", "gr-qc/9412071", "2401.00012")
    i1, i3 = rec("inspire", "2401.00001.json") or {}, rec("inspire", "2401.00012.json") or {}
    c.ok(r.returncode == 0 and srv.count("/api/literature") - n0 == 1 and i1.get("status") == "ok"
         and i1["record"]["control_number"] == 11 and i3.get("status") == "not-found",
         "INSPIRE: one request for three ids, each matched by its eprint; an id without a record is not-found",
         json.dumps([i1, i3])[:800])
    n0 = srv.count("/api/literature")
    r = fetch("--meta", "--service", "inspire", "2401.00008", "2401.00011")
    c.ok(r.returncode == 0 and srv.count("/api/literature") - n0 == 3 and (rec("inspire", "2401.00008.json") or {}).get(
         "status") == "ok", "an INSPIRE answer cut short (hits.total above the hits) is asked again id by id", r.stderr)
    r = fetch("--inspire-query", "t black hole and date 2020")
    qd = os.path.join(store, "meta", "inspire", "query")
    c.ok(r.returncode == 0 and os.path.isdir(qd) and len(os.listdir(qd)) == 1, "--inspire-query writes meta/inspire/query/<sha16>.json",
         r.stdout + r.stderr)

    # 15. the gap: within one process and across two at once
    pa = subprocess.Popen(["/usr/bin/python3", "-I", cmd, "--test-server", srv.url, "--test-gap", str(GAP), "--pdf",
                           "2401.00006", "--refresh"], cwd=elsewhere, env=F.H.boot_env(), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    pb = subprocess.Popen(["/usr/bin/python3", "-I", cmd, "--test-server", srv.url, "--test-gap", str(GAP), "--meta",
                           "--service", "arxiv", "--refresh", "2401.00001"], cwd=elsewhere, env=F.H.boot_env(),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pa.wait(120)
    pb.wait(120)
    gaps = {}
    for svc in ("arxiv", "inspire"):
        ts = sorted(t for t, s, _, _ in srv.log if s == svc)
        gaps[svc] = min((b - a for a, b in zip(ts, ts[1:])), default=None)
    c.ok(all(g is None or g >= GAP - 0.02 for g in gaps.values()),
         f"every two requests to one service at least the gap apart, two processes included (smallest: "
         f"arxiv {gaps['arxiv']:.2f} s, inspire {gaps['inspire']:.2f} s; gap {GAP} s)")

    # 17. the worktree's copy writes into the main checkout's store
    wcmd = os.path.join(repo, "wt", "kb", "harness", "bin", "nrpic-fetch-arxiv")
    r = fetch("--meta", "--service", "arxiv", "2401.00008", script_path=wcmd, cwd=os.path.join(repo, "wt", "kb"))
    c.ok(r.returncode == 0 and os.path.isfile(os.path.join(store, "meta", "arxiv-api", "2401.00008.json"))
         and not os.path.exists(os.path.join(repo, "wt", "kb", "kb-data")),
         "called as wt/kb/harness/bin/nrpic-fetch-arxiv: writes the main checkout's kb-data/, nothing in the worktree",
         r.stdout + r.stderr)

    # 18. --check, no network
    n0 = len(srv.log)
    r = fetch("--check", "gr-qc/9412071", "2401.00001", test=False)
    c.ok(r.returncode == 0 and "postscript" in r.stdout and "no TeX" in r.stdout and "source.pdf" in r.stdout
         and len(srv.log) == n0, "--check re-runs the content checks on the store without a request", r.stdout + r.stderr)
    sb = os.path.join(store, "raw", "arxiv", "2401.00001", "v3", "source.bin")
    os.chmod(sb, 0o644)
    open(sb, "ab").write(b"x")
    r = fetch("--check", "2401.00001", test=False)
    c.ok(r.returncode == 1 and ("PROBLEMS" in r.stdout or "FAILS" in r.stdout), "--check catches a changed source.bin", r.stdout)

    # 19.-21. refusals and --ids-from
    r = fetch("--test-server", "http://example.org", "2401.00001", test=False)
    c.ok(r.returncode != 0 and "loopback" in (r.stderr + r.stdout), "--test-server accepts a loopback URL only", r.stderr)
    r = fetch("--test-gap", "0", "2401.00001", test=False)
    c.ok(r.returncode != 0 and "only with --test-server" in (r.stderr + r.stdout), "--test-gap only with --test-server", r.stderr)
    r = fetch("not-an-id", test=False)
    c.ok(r.returncode != 0 and "not an arXiv identifier" in (r.stderr + r.stdout), "a malformed identifier is refused", r.stderr)
    lst = os.path.join(elsewhere, "ids.txt")
    open(lst, "w").write("# ids\n2401.00007\narXiv:2401.00001v3  # version and prefix stripped\n")
    n0 = len(srv.log)
    r = fetch("--ids-from", lst)
    c.ok(r.returncode == 0 and len(r.stdout.split()) == 2 and len(srv.log) == n0,
         "--ids-from: comments, arXiv: prefix and version suffix handled (both stored already: no request)", r.stdout)
    c.ok(not any(urllib.parse.urlsplit(p).netloc for _, _, p, _ in srv.log), f"{len(srv.log)} requests, all to the loopback server")
    srv.httpd.shutdown()
    rc = c.done()
    if rc == 0:
        real = os.path.realpath(root)
        if os.path.dirname(real) == os.path.realpath(os.path.join(F.live_home(), "scratch", "harness")) \
                and os.path.basename(real).startswith("fetch-"):
            for dp, dn, fn in os.walk(real):
                for x in dn:
                    os.chmod(os.path.join(dp, x), 0o755)
            shutil.rmtree(real)
    else:
        print(f"kept for inspection: {root}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
