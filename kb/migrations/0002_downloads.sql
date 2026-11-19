-- Migration 2: the K1 inventory (kb verify-downloads) in the database.
-- Why a table of its own: papers.title is NOT NULL and the titles come from the arXiv/INSPIRE
-- metadata (a later stage), so K1 cannot create papers rows without inventing titles.
-- One row per arXiv id that is in the manifest or in the store; rewritten by every
-- verify-downloads inside one transaction.
CREATE TABLE downloads(
  paper_id TEXT PRIMARY KEY,               -- arXiv id as in the manifest ('2611.12831', 'gr-qc/9804040')
  in_manifest INTEGER NOT NULL, grp TEXT, priority INTEGER,
  status TEXT NOT NULL CHECK(status IN ('ok','problem','incomplete','failed','missing')),
  version TEXT, version_source TEXT, versions_present_json TEXT,
  path TEXT,                               -- source.bin relative to the data root
  sha256 TEXT, bytes INTEGER,
  sniffed_kind TEXT,                       -- from the content: gzip-tar, gzip-tex, pdf, html, ...
  source_kind TEXT CHECK(source_kind IN ('tex','pdf','none')),
  n_files INTEGER, src_bytes INTEGER,
  problems_json TEXT, notes_json TEXT, fetched_utc TEXT, checked_at TEXT NOT NULL, tool_version TEXT);
CREATE INDEX downloads_status ON downloads(status, priority);
CREATE TABLE repo_downloads(
  repo_id TEXT PRIMARY KEY,                -- 'owner/name' as in the manifest
  role TEXT, owners TEXT,
  status TEXT NOT NULL CHECK(status IN ('ok','problem','incomplete','missing')),
  commit_sha TEXT, head_ref TEXT, license_spdx_guess TEXT,
  problems_json TEXT, notes_json TEXT, checked_at TEXT NOT NULL, tool_version TEXT);
