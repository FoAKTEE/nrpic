"""Retrieval at the answer location (kbtool/search_rerank.py; tracks/kb/retrieval, R4).

The defect found in R3 (run kb-20261119-141041-69232a4): an answer of one sentence inside a
long chunk that mixes topics is outranked, by whole-chunk BM25 and by whole-chunk vectors,
by shorter chunks that share more words with the question; and the end of a chunk longer
than the model's input is never read. Synthetic store, HashEmbedder for the model (with an
input limit so that truncation happens as with the real model); no real kb-data.
"""
import sqlite3

import pytest

from kbtool import db as D
from kbtool import embed_index as X
from kbtool import embed_model as E
from kbtool import embed_search as S
from kbtool import paths
from kbtool import search_rerank as R

QUESTION = "On which supercomputer were the simulations performed?"

FILLER = [
    "The deposited density reproduces the analytic benchmark of dust collapse.",
    "The horizon mass agrees with the initial mass to within one part in a thousand.",
    "Relativistic clusters provide a complementary test of kinetic support.",
    "Weakly bound models remain close to equilibrium during the evolution.",
    "Two localized overdensities collapse and form black holes that merge.",
    "The envelope acquires angular momentum during the inspiral of the binary.",
    "Future work should include higher order methods and cosmic censorship.",
    "The authors acknowledge discussions with colleagues and support from a fellowship.",
]


class TruncHash(E.HashEmbedder):
    """HashEmbedder that reads only the first `limit` words of a document (as the real model
    reads only 512 word pieces); the query is never cut."""

    def __init__(self, limit=40, **kw):
        super().__init__(**kw)
        self.limit = limit

    def encode(self, texts, query=False):
        import re
        if not query:
            texts = [" ".join(re.findall(r"\w+", t)[: self.limit]) for t in texts]
        return super().encode(texts, query=query)


@pytest.fixture()
def rstore(tmp_path, monkeypatch):
    data = tmp_path / "kb-data"
    monkeypatch.setenv("KB_DATA_ROOT", str(data))
    monkeypatch.setenv("KB_LOCK", str(tmp_path / "kb-writer.lock"))
    lay = paths.Layout(home=str(tmp_path), data=str(data), lock=str(tmp_path / "kb-writer.lock"))
    D.init_db(lay)
    con = sqlite3.connect(lay.db_work)
    con.execute("INSERT INTO papers(paper_id, title, version, source_kind, parse_status) VALUES "
                "('2611.00001', 'P one', 'v1', 'tex', 'ok'), ('2611.00002', 'P two', 'v1', 'tex', 'ok')")
    con.execute("INSERT INTO sections(section_id, paper_id, level, number, title) VALUES "
                "(1, '2611.00001', 1, '6', 'Conclusions'), (2, '2611.00001', 1, '2', 'Methods'), "
                "(3, '2611.00002', 1, '3', 'Simulations')")
    # chunk 101: the answer is the last of nine sentences, beyond the 40 words the stand-in
    # model reads (as the answer of golden q12 lay beyond 512 word pieces); its other
    # sentences are about other things (as chunk 105400 of 2611.12831 for q06/q07)
    answer = " ".join(FILLER[:7]) + " We thank the referee. The simulations were performed on the Vista supercomputer."
    chunks = [
        (101, "2611.00001", 1, answer),
        # rivals: shorter, about simulations, none names a supercomputer; 104 is the closest by
        # the whole-chunk vector and the second by whole-chunk BM25
        (102, "2611.00001", 2, "The grids of the box are refined twice near the centre."),
        (103, "2611.00002", 3, "Simulations were run for several masses and listed in the table."),
        (104, "2611.00002", 3, "The simulations were performed with a moving mesh at three resolutions."),
        (105, "2611.00001", 2, "The deposition uses a cloud in cell kernel with a binomial filter."),
    ]
    for cid, pid, sid, text in chunks:
        con.execute("INSERT INTO chunks(chunk_id, paper_id, section_id, kind, text, char_start, char_end) "
                    "VALUES (?,?,?,?,?,0,?)", (cid, pid, sid, "body", text, len(text)))
    con.execute("INSERT INTO chunks_fts(chunks_fts) VALUES ('rebuild')")
    emb = TruncHash(limit=40)
    rows = X.chunk_texts(con)
    vecs = emb.encode([t for _, t in rows])
    con.executemany("INSERT INTO embeddings(owner_kind, owner_id, model, dim, vec, text_sha256, n_tokens, "
                    "truncated, at) VALUES ('chunk', ?, ?, ?, ?, ?, 0, 0, 't')",
                    [(i, emb.key, emb.dim, v.tobytes(), X.sha(t)) for (i, t), v in zip(rows, vecs)])
    con.commit()
    con.close()
    return lay, emb


@pytest.mark.parametrize("which", [
    pytest.param("first_stage", marks=pytest.mark.xfail(strict=True, reason="the defect of R3: whole-chunk "
                                                        "BM25 and a truncated whole-chunk vector")),
    "rerank"])
def test_buried_answer_ranks_first(rstore, which):
    """The same assertion on the first stage (embed_search, hybrid; must fail: strict xfail)
    and on the window re-ranking (search_rerank, default variant; must pass)."""
    lay, emb = rstore
    if which == "first_stage":
        hits, _ = S.search(lay, QUESTION, k=1, mode="hybrid", embedder=emb, model=emb.key, db=lay.db_work)
    else:
        hits, info = R.search(lay, QUESTION, k=1, embedder=emb, model=emb.key, db=lay.db_work)
        assert R.DEFAULT == "w2-noexpand" and info["mode"] == "rerank:w2-noexpand"
        assert "supercomputer" in hits[0]["window_snippet"] and info["windows"] > info["pool"]
    assert hits[0]["chunk_id"] == 101


def test_rerank_keeps_the_first_stage_pool(rstore):
    """Without expansion the pool is the first-stage list; a filter on the paper holds."""
    lay, emb = rstore
    hits, info = R.search(lay, QUESTION, k=10, embedder=emb, model=emb.key, db=lay.db_work, paper="2611.00002")
    assert {h["paper_id"] for h in hits} == {"2611.00002"} and info["expanded_papers"] == []


def test_window_spans_cover_every_sentence():
    text = "One sentence here. Two is short! Three ends? $x = y.$ Five follows.\n\nSix after a gap."
    sents = R.sentence_spans(text)
    assert len(sents) == 5 and text[sents[-1][0]:sents[-1][1]] == "Six after a gap."   # "$x = y.$ Five" is one
    wins = R.window_spans(text, win=3, stride=2)
    covered = set()
    for a, b in wins:
        covered |= set(range(a, b))
    assert all(set(range(a, b)) <= covered for a, b in sents)
    assert wins[-1][1] == sents[-1][1]
    long = "x" * 3000
    sl = R.window_spans(long, max_chars=1200, overlap=200)
    assert sl[0] == (0, 1200) and sl[-1][1] == 3000 and all(b - a <= 1200 for a, b in sl)
