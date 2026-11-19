-- Schema of the knowledge base: brief section 12.2, lines 1277-1347, extracted by kbtool.brief.extract_schema
-- (brief sha256 9492261e307ba118225eac6b1b41b9b8e98d718e9c609c686899a75b2aa48449). Changes after this point go into migrations/.
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE schema_version(version INTEGER NOT NULL, applied_at TEXT NOT NULL);

-- ---------- papers ----------
CREATE TABLE papers(
  paper_id TEXT PRIMARY KEY,              -- arXiv id: '2611.12831' or 'gr-qc/9804040'
  title TEXT NOT NULL, authors_json TEXT, abstract TEXT, primary_class TEXT,
  grp TEXT, priority INTEGER,             -- group code (G01...) and priority (3/2/1) from the manifest of this brief
  version TEXT, submitted TEXT, updated TEXT, doi TEXT, inspire_recid INTEGER, journal_ref TEXT, license TEXT,
  source_kind TEXT CHECK(source_kind IN ('tex','pdf','none')),
  main_tex TEXT, parse_status TEXT, parse_score REAL, sha256 TEXT, ingested_at TEXT,
  brief_title TEXT, brief_authors TEXT, title_matches_brief INTEGER);   -- cross-check against the brief
CREATE TABLE sections(
  section_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, parent_id INTEGER,
  level INTEGER, number TEXT, title TEXT, label TEXT, char_start INTEGER, char_end INTEGER);
CREATE TABLE chunks(
  chunk_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, section_id INTEGER REFERENCES sections,
  kind TEXT CHECK(kind IN ('abstract','body','caption','footnote','appendix','comment')),
  text TEXT NOT NULL, tex TEXT, n_tokens INTEGER, char_start INTEGER, char_end INTEGER);
CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='chunk_id', tokenize='porter unicode61');
CREATE TABLE equations(
  eq_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, section_id INTEGER REFERENCES sections,
  env TEXT, label TEXT, number TEXT, tex_raw TEXT NOT NULL, tex_norm TEXT, symbols_json TEXT, context TEXT, tags_json TEXT);
CREATE VIRTUAL TABLE equations_fts USING fts5(tex_norm, context, content='equations', content_rowid='eq_id');
CREATE TABLE figures(
  fig_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, label TEXT, number TEXT, caption TEXT, files_json TEXT);

-- ---------- bibliography and citation graph ----------
CREATE TABLE bib_entries(
  bib_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, cite_key TEXT, raw TEXT,
  target_arxiv TEXT, target_doi TEXT, target_recid INTEGER, resolved_by TEXT, confidence REAL);
CREATE TABLE citations(
  cit_id INTEGER PRIMARY KEY, citing TEXT NOT NULL REFERENCES papers, cited_arxiv TEXT, cited_doi TEXT,
  bib_id INTEGER REFERENCES bib_entries, chunk_id INTEGER REFERENCES chunks, context TEXT, in_corpus INTEGER);
CREATE INDEX citations_cited ON citations(cited_arxiv);

-- ---------- code ----------
CREATE TABLE repos(
  repo_id TEXT PRIMARY KEY,               -- 'owner/name'
  url TEXT, commit_sha TEXT, commit_date TEXT, default_branch TEXT, license_spdx TEXT, role TEXT,
  paper_ids_json TEXT, branches_json TEXT, ingested_at TEXT);
CREATE TABLE code_files(
  file_id INTEGER PRIMARY KEY, repo_id TEXT NOT NULL REFERENCES repos, path TEXT, lang TEXT, loc INTEGER, sha256 TEXT);
CREATE TABLE symbols(
  sym_id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES code_files, name TEXT, qualname TEXT,
  kind TEXT, signature TEXT, line_start INTEGER, line_end INTEGER, doc TEXT);
CREATE TABLE code_chunks(
  cc_id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES code_files, sym_id INTEGER REFERENCES symbols,
  text TEXT NOT NULL, line_start INTEGER, line_end INTEGER);
CREATE VIRTUAL TABLE code_fts USING fts5(text, content='code_chunks', content_rowid='cc_id', tokenize='unicode61');
CREATE TABLE params(                       -- runtime parameters read by a code (e.g. AthenaK input blocks)
  param_id INTEGER PRIMARY KEY, repo_id TEXT NOT NULL REFERENCES repos, block TEXT, name TEXT, type TEXT,
  default_value TEXT, file_id INTEGER REFERENCES code_files, line INTEGER);

-- ---------- links, claims, embeddings, provenance ----------
CREATE TABLE impl_links(                   -- "symbol S implements equation E of paper P"
  link_id INTEGER PRIMARY KEY, paper_id TEXT, eq_id INTEGER, repo_id TEXT, sym_id INTEGER, relation TEXT,
  status TEXT CHECK(status IN ('claimed','verified','refuted')), evidence TEXT, by_owner TEXT, at TEXT);
CREATE TABLE claims(
  claim_id INTEGER PRIMARY KEY, text TEXT NOT NULL,
  kind TEXT CHECK(kind IN ('result','method','limitation','open_question','number','definition')),
  paper_id TEXT, locator TEXT, chunk_id INTEGER, quote_start INTEGER, quote_end INTEGER,
  label TEXT CHECK(label IN ('fulltext','abstract','title_only','background','judgement','to_verify','refuted')),
  origin TEXT, track_tags TEXT, verified_by TEXT, verified_at TEXT, supersedes INTEGER);
CREATE TABLE embeddings(                   -- float32 blobs are the source of truth; ANN indexes are rebuilt from them
  owner_kind TEXT CHECK(owner_kind IN ('chunk','equation','code_chunk','claim')),
  owner_id INTEGER, model TEXT, dim INTEGER, vec BLOB, PRIMARY KEY(owner_kind, owner_id, model));
CREATE TABLE ingest_log(
  log_id INTEGER PRIMARY KEY, at TEXT, step TEXT, target TEXT, status TEXT, message TEXT, tool_version TEXT);
