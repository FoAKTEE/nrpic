"""Stages K4-K5 end to end on the synthetic store of test_papers_ingest: `kb embed` (migration
0006, incremental updates, re-ingest, orphans, check), `kb search` (BM25, vectors, fusion,
filters, locators, stale vectors), `kb eq` (tags, TeX query, filters). The deterministic
HashEmbedder stands in for the model; one test loads the real model when it is present."""
import json
import os
import sqlite3

import pytest

from test_papers_ingest import build, run
from kbtool import embed_index as X
from kbtool import embed_model as E
from kbtool import embed_search as S
from kbtool import eq_search as Q
from kbtool import eq_tags as T


def _ingest(store, monkeypatch, capsys):
    build(store)
    assert run(store, ["ingest", "arxiv", "--all", "--jobs", "1"], monkeypatch) == 0
    capsys.readouterr()


def _json_out(capsys):
    out = capsys.readouterr().out
    return json.loads(out[out.index("{"):] if not out.lstrip().startswith("[") else out)


def _embed(store, monkeypatch, capsys, *extra):
    rc = run(store, ["embed", "--model", "hash"] + list(extra), monkeypatch)
    out = capsys.readouterr().out
    return rc, json.loads(out[out.index("\n{") + 1:]) if "\n{" in out else json.loads(out)


def test_embed_incremental_and_check(store, monkeypatch, capsys):
    _ingest(store, monkeypatch, capsys)
    rc, st = _embed(store, monkeypatch, capsys)
    assert rc == 0 and st["model"] == "hash64@test"
    con = sqlite3.connect(store.layout.db_work)
    n_chunks = con.execute("SELECT count(*) FROM chunks WHERE kind != 'comment'").fetchone()[0]
    n_eq = con.execute("SELECT count(*) FROM equations").fetchone()[0]
    assert st["kinds"]["chunk"]["written"] == n_chunks and st["kinds"]["equation"]["written"] == n_eq == 2
    # comments are never embedded; every row has its text hash, dimension and blob size
    assert con.execute("SELECT count(*) FROM embeddings e JOIN chunks c ON c.chunk_id = e.owner_id "
                       "WHERE e.owner_kind = 'chunk' AND c.kind = 'comment'").fetchone()[0] == 0
    rows = con.execute("SELECT dim, length(vec), text_sha256, n_tokens, truncated FROM embeddings").fetchall()
    assert all(r[0] == 64 and r[1] == 256 and len(r[2]) == 64 and r[3] > 0 and r[4] == 0 for r in rows)
    m = con.execute("SELECT name, revision, dim, recipe_json FROM embed_models WHERE model='hash64@test'").fetchone()
    assert m[0] == "test/hash" and m[2] == 64 and "chunk-v1" in m[3] and "eq-v1" in m[3]
    assert con.execute("SELECT max(version) FROM schema_version").fetchone()[0] >= 6
    con.close()
    # a second run embeds nothing
    rc, st = _embed(store, monkeypatch, capsys)
    assert st["kinds"]["chunk"]["todo"] == 0 and st["kinds"]["equation"]["todo"] == 0
    assert run(store, ["embed", "--model", "hash", "--check", "--work"], monkeypatch) == 0
    rep = _json_out(capsys)
    assert rep["chunk"]["missing"] == rep["chunk"]["stale"] == rep["chunk"]["orphaned"] == 0
    # change one chunk's text: check reports it stale, embed re-embeds exactly that one
    con = sqlite3.connect(store.layout.db_work)
    cid = con.execute("SELECT chunk_id FROM chunks WHERE kind='body' ORDER BY chunk_id LIMIT 1").fetchone()[0]
    con.execute("UPDATE chunks SET text = text || ' extra words' WHERE chunk_id = ?", (cid,))
    con.commit()
    con.close()
    assert run(store, ["embed", "--model", "hash", "--check", "--work"], monkeypatch) == 1
    assert _json_out(capsys)["chunk"]["stale"] == 1
    rc, st = _embed(store, monkeypatch, capsys)
    assert st["kinds"]["chunk"]["todo"] == 1 and st["kinds"]["chunk"]["written"] == 1
    # re-ingest one paper: its rows get new ids; embed fills them and deletes the orphans
    assert run(store, ["ingest", "arxiv", "--id", "2111.05282", "--jobs", "1"], monkeypatch) == 0
    capsys.readouterr()
    assert run(store, ["embed", "--model", "hash", "--check", "--work"], monkeypatch) == 1
    capsys.readouterr()
    rc, st = _embed(store, monkeypatch, capsys)
    assert st["kinds"]["chunk"]["todo"] > 0
    assert run(store, ["embed", "--model", "hash", "--check", "--work"], monkeypatch) == 0
    capsys.readouterr()
    # a second model key adds a second set and keeps the first
    import kbtool.embed_cli as C
    monkeypatch.setattr(C, "_embedder", lambda name, threads=None: E.HashEmbedder(key="hash64@other"))
    rc, st = _embed(store, monkeypatch, capsys)
    con = sqlite3.connect(store.layout.db_work)
    per = dict(con.execute("SELECT model, count(*) FROM embeddings GROUP BY model"))
    con.close()
    assert set(per) == {"hash64@test", "hash64@other"} and per["hash64@test"] == per["hash64@other"]


def test_search_on_snapshot_without_embeddings(store, monkeypatch, capsys):
    """A database without migration 0006 (an old snapshot) still answers, by text only."""
    _ingest(store, monkeypatch, capsys)
    con = sqlite3.connect(store.layout.db_work)               # undo migration 0006 by hand
    assert X.has_schema(con) is True
    for c in ("text_sha256", "n_tokens", "truncated", "at"):
        con.execute(f"ALTER TABLE embeddings DROP COLUMN {c}")
    con.execute("DROP TABLE embed_models")
    con.commit()
    assert X.has_schema(con) is False
    con.close()
    assert run(store, ["search", "--work", "--model", "hash", "--json", "deposition"], monkeypatch) == 0
    res = _json_out(capsys)
    assert res["info"]["vectors"] == 0 and "no vectors" in res["info"]["note"] and res["hits"]


def test_search_hybrid_filters_locators(store, monkeypatch, capsys):
    _ingest(store, monkeypatch, capsys)
    _embed(store, monkeypatch, capsys)
    args = ["search", "--work", "--model", "hash", "--json"]
    assert run(store, args + ["cloud deposition of order two"], monkeypatch) == 0
    res = _json_out(capsys)
    hits, info = res["hits"], res["info"]
    assert info["model"] == "hash64@test" and info["vectors"] > 0
    top = hits[0]
    assert top["paper_id"] == "2111.05282" and set(top["ranks"]) == {"bm25", "vector"}
    assert top["source"].startswith("method.tex:L") and top["version"] == "v3"
    assert [h["rank"] for h in hits] == list(range(1, len(hits) + 1))
    assert all(hits[i]["rrf"] >= hits[i + 1]["rrf"] for i in range(len(hits) - 1))
    # text only and vector only
    assert run(store, args + ["--text-only", "cloud deposition"], monkeypatch) == 0
    assert all(set(h["ranks"]) == {"bm25"} for h in _json_out(capsys)["hits"])
    assert run(store, args + ["--vector-only", "cloud deposition"], monkeypatch) == 0
    assert all(set(h["ranks"]) == {"vector"} for h in _json_out(capsys)["hits"])
    # structured filters
    assert run(store, args + ["--paper", "gr-qc/9703066", "relativistic particle code"], monkeypatch) == 0
    assert {h["paper_id"] for h in _json_out(capsys)["hits"]} == {"gr-qc/9703066"}
    assert run(store, args + ["--kind", "caption", "cycle of the method"], monkeypatch) == 0
    assert {h["kind"] for h in _json_out(capsys)["hits"]} == {"caption"}
    assert run(store, args + ["--group", "G02", "particle code"], monkeypatch) == 0
    assert {h["group"] for h in _json_out(capsys)["hits"]} == {"G02"}
    # FTS syntax in a query is harmless
    assert run(store, args + ['"deposition" AND (NEAR OR -x*)'], monkeypatch) == 0
    capsys.readouterr()
    # a vector whose chunk text changed after embedding is dropped as stale
    con = sqlite3.connect(store.layout.db_work)
    cid = hits[0]["chunk_id"]
    con.execute("UPDATE chunks SET text = 'replaced' WHERE chunk_id = ?", (cid,))
    con.commit()
    con.close()
    assert run(store, args + ["--vector-only", "cloud deposition of order two"], monkeypatch) in (0, 1)
    res = _json_out(capsys)
    assert res["info"]["stale_dropped"] >= 1 and cid not in [h["chunk_id"] for h in res["hits"]]


def test_eq_tags_and_search(store, monkeypatch, capsys):
    _ingest(store, monkeypatch, capsys)
    assert run(store, ["eq", "--apply-tags"], monkeypatch) == 0
    rep = _json_out(capsys)
    assert rep["equations"] == 2 and rep["per_tag"]["geodesic"] == 1
    con = sqlite3.connect(store.layout.db_work)
    tags = dict(con.execute("SELECT label, tags_json FROM equations"))
    con.close()
    assert json.loads(tags["eq:geo"]) == ["geodesic"] and json.loads(tags["eq:app"]) == []
    _embed(store, monkeypatch, capsys)
    args = ["eq", "--work", "--model", "hash", "--json"]
    assert run(store, args + [r"\dfrac{d u_\mu}{d t}"], monkeypatch) == 0
    res = _json_out(capsys)
    assert res["hits"][0]["label"] == "eq:geo" and res["hits"][0]["number"] == "1"
    assert res["hits"][0]["source"] == "method.tex:L2-4" and res["hits"][0]["tags"] == ["geodesic"]
    assert '"frac"' in res["info"]["fts_query"] and '"dfrac"' not in res["info"]["fts_query"]
    assert run(store, args + ["--tag", "geodesic", "equation"], monkeypatch) == 0
    assert [h["label"] for h in _json_out(capsys)["hits"]] == ["eq:geo"]
    assert run(store, args + ["--tag", "vlasov", "equation"], monkeypatch) == 1
    capsys.readouterr()
    # kb search --kind eq goes to the same index
    assert run(store, ["search", "--work", "--model", "hash", "--json", "--kind", "eq", "geodesic"], monkeypatch) == 0
    assert _json_out(capsys)["hits"][0]["label"] == "eq:geo"


def test_rrf_and_fts_query():
    f = S.rrf({"a": [1, 2, 3], "b": [3, 1]})
    assert f[1][0] == pytest.approx(1 / 61 + 1 / 62) and f[3][0] == pytest.approx(1 / 63 + 1 / 61)
    assert f[2][0] == pytest.approx(1 / 62) and f[1][1] == {"a": 1, "b": 2}
    assert S.fts_query("What is the order of the shape functions?") == '"order" OR "shape" OR "functions"'
    assert S.fts_query("the of a") is None
    # normalized like the stored tex_norm (spaces removed), then cut into FTS5 unicode61 runs
    assert Q.fts_query(r"\partial_t f + \Gamma^\mu") == '"partial" OR "tf" OR "Gamma" OR "mu"'


RULE_CASES = [
    # (tag, label, context, tex, expected)
    ("vlasov", None, "The Vlasov equation for the distribution function reads", r"\partial_t f+v\cdot\nabla f=0", True),
    ("vlasov", None, "The Vlasov equation is solved with particles", r"E=mc^2", False),
    ("geodesic", "eq:geodesic", "", "x", True),
    ("geodesic", None, "Particles follow the geodesic equation", r"\frac{du^\mu}{d\tau}=-\Gamma^\mu{}_{\alpha\beta}u^\alpha u^\beta", True),
    ("hamiltonian_constraint", None, "The Hamiltonian constraint is", r"R+K^2-K_{ij}K^{ij}=16\pi\rho", True),
    ("hamiltonian_constraint", None, "The Hamiltonian of a particle is", r"H=\frac{p^2}{2m}", False),
    ("momentum_constraint", None, "and the momentum constraint", r"D_j(K^{ij}-\gamma^{ij}K)=8\pi S^i", True),
    ("z4c", "eq:z4c-theta", "", "x", True),
    ("z4c", None, "In the Z4c formulation the variable", r"\partial_t\Theta=\alpha H-\kappa_1\Theta", True),
    ("deposition", None, "The cloud-in-cell deposition assigns", r"W(x)=1-|x|", True),
    ("deposition", None, "the energy deposition rate of the jet", r"W=\dot E", False),
    ("compaction_function", None, "The compaction function is defined as", r"\mathcal{C}(r)=2\delta M/R", True),
    ("langevin", None, "The Langevin equation of stochastic inflation", r"\frac{d\phi}{dN}=-\frac{V'}{3H^2}+\frac{H}{2\pi}\xi", True),
    ("langevin", None, "white noise", r"\langle\xi\rangle", False),
    ("tidal_radius", None, "The tidal radius of the binary", r"r_t=a\left(\frac{M}{m}\right)^{1/3}", True),
    ("tidal_radius", None, "The tidal radius is large", r"E=mc^2", False),
    # failure modes of rules version 1 seen in the corpus sample (run kb-20261115-154013-e70f45d)
    ("hamiltonian_constraint", None, "contributions to the Hamiltonian constraint normalised by [EQ] as",
     r"\omega_K\equiv2K^2/3", False),
    ("langevin", None, "when discussing stochastic inflation we fix the Lagrangian as [EQ]",
     r"G_{\mu\nu}+\xi_{,\phi}R\Box\phi=T_{\mu\nu}", False),
    ("tidal_radius", None, "the spread in energy at the tidal radius [EQ]", r"\Delta E=k\frac{GMm}{r_t^2}", False),
    ("tidal_radius", "eq:RT", "the conformal Ricci tensor [EQ]", r"\tilde R_{ij}=-\frac{1}{2}\partial^2\tilde\gamma_{ij}", False),
    ("vlasov", None, "We rewrite the Vlasov equation with the remainders [EQ] where",
     r"\mathcal{R}_1=-\mathcal{P}\partial_{Q}f", False),
    ("momentum_constraint", "eq:matt-energy-momentum-cons", "", r"\partial_tP_a=Q_a", False),
    # label patterns anchored in version 3 (sample of run kb-20261115-154419-f4dfa36)
    ("z4c", "eq:lorentz4", "", r"\Lambda=q(E+V\times B)", False),
    ("z4c", "eq:CCZ4_K", "", "x", True),
    ("tidal_radius", "eq:transportid4", "", r"\partial_v h=0", False),
    ("tidal_radius", "E:rtid", "", "x", True),
]


@pytest.mark.parametrize("tag,label,ctx,tex,expect", RULE_CASES)
def test_tag_rules(tag, label, ctx, tex, expect):
    rules = T.load_rules()
    assert (tag in T.tags_for(rules, label, ctx, tex)) is expect


def test_tag_rules_reject_unknown_field(tmp_path):
    p = tmp_path / "r.yaml"
    p.write_text("version: 1\ntags:\n  x:\n    any:\n      - lable: 'a'\n")
    with pytest.raises(ValueError):
        T.load_rules(str(p))


def test_hash_embedder_and_model_check(tmp_path, monkeypatch):
    h = E.HashEmbedder()
    a = h.encode(["cloud in cell deposition", "cloud in cell deposition", "gauge"])
    assert a.shape == (3, 64) and abs(float((a[0] * a[0]).sum()) - 1) < 1e-6 and (a[0] == a[1]).all()
    monkeypatch.setenv("KB_EMBED_MODELS", str(tmp_path))
    assert E.model_dir().startswith(str(tmp_path)) and E.check_local()[0].startswith("no model")
    d = E.model_dir()
    os.makedirs(d)
    open(os.path.join(d, "f.txt"), "w").write("x")
    json.dump({"files": {"f.txt": {"sha256": "0" * 64}}}, open(os.path.join(d, "download.json"), "w"))
    assert E.check_local() == ["f.txt: sha256 differs"]
    assert E.model_key() == "bge-small-en-v1.5@5c38ec7"


@pytest.mark.skipif(not os.path.exists(os.path.join(E.model_dir(), "download.json")), reason="model not fetched")
def test_real_model_offline():
    emb = E.STEmbedder(threads=2, batch_size=4)
    assert os.environ["HF_HUB_OFFLINE"] == "1"
    v = emb.encode(["first-order cloud-in-cell deposition"], query=True)
    assert v.shape == (1, 384) and abs(float((v[0] ** 2).sum()) - 1) < 1e-5
    assert emb.n_tokens(["a b c"]) == [5]


def test_recipes_are_stable():
    # the recipe strings define the stored hashes: a change must be deliberate (new recipe name)
    assert X._join(X._heading("2.3", "Deposition"), "text") == "2.3 Deposition\ntext"
    assert X._join(X._heading(None, None, "abstract"), "text") == "Abstract\ntext"
    assert X._join(X._heading(None, None), "text") == "text"
