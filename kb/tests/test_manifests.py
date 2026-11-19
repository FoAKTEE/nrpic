"""T1: the manifests in kb/manifests are the brief's section 17, row for row."""
import json
import os

import pytest

from kbtool import brief, paths

BRIEF = paths.default_brief()
pytestmark = pytest.mark.skipif(BRIEF is None, reason="brief not found")


def test_committed_manifests_equal_fresh_extraction():
    arxiv, github, prov = brief.extract_manifests(BRIEF)
    for name, rows in (("arxiv.tsv", arxiv), ("github.tsv", github)):
        have = open(os.path.join(paths.kb_manifest_dir(), name)).read()
        assert have == "".join("\t".join(r) + "\n" for r in rows)
    src = json.load(open(os.path.join(paths.kb_manifest_dir(), "SOURCE.json")))
    assert src["brief_sha256"] == prov["brief_sha256"]
    assert src["arxiv"]["rows"] == len(arxiv) and src["github"]["rows"] == len(github)


def test_locator_rule_points_at_the_row():
    lines, _ = brief.read_brief(BRIEF)
    arxiv, github, prov = brief.extract_manifests(BRIEF)
    a0 = prov["arxiv"]["first_line"]
    for i, (aid, grp, pri) in enumerate(arxiv):
        assert lines[a0 - 1 + i].split("\t") == [aid, grp, pri]
    g0 = prov["github"]["first_line"]
    for i, row in enumerate(github):
        assert lines[g0 - 1 + i].split("\t")[0] == row[0]


def test_rows_are_valid_and_unique():
    arxiv = brief.load_arxiv_manifest(os.path.join(paths.kb_manifest_dir(), "arxiv.tsv"))
    ids = [r["id"] for r in arxiv]
    assert len(ids) == len(set(ids))
    assert all(brief.valid_arxiv_id(i) for i in ids)
    assert {r["priority"] for r in arxiv} <= {1, 2, 3}
    gh = brief.load_github_manifest(os.path.join(paths.kb_manifest_dir(), "github.tsv"))
    assert len({r["repo"].lower() for r in gh}) == len(gh)
    assert {r["role"] for r in gh} <= brief.ROLES


def test_extraction_rejects_malformed_rows(tmp_path):
    p = tmp_path / "b.md"
    p.write_text("## 17. M\n\n**arXiv manifest.** x\n\n```tsv\n2611.12831\tG01\t3\nnot-an-id\tG01\t9\n```\n\n"
                 "**GitHub repository manifest.** y\n\n```tsv\na/b\tcore\tall\td\n```\n")
    with pytest.raises(brief.BriefFormatError) as e:
        brief.extract_manifests(str(p))
    assert "bad arXiv id" in str(e.value) and "bad priority" in str(e.value)


def test_schema_is_the_brief_block():
    sql, prov = brief.extract_schema(BRIEF)
    body = [l for l in open(paths.schema_path()).read().splitlines() if not l.startswith("-- Schema of") and
            not l.startswith("-- (brief sha256")]
    assert "\n".join(body).strip() == sql.strip()
