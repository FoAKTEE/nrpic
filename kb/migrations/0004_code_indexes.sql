-- Migration 4 (K6): indexes for the code tables.
-- With PRAGMA foreign_keys = ON, deleting a code_files row checks symbols, code_chunks and
-- params for references; without an index on their file_id every deleted file scans those
-- tables in full (measured: a re-ingest of AthenaK did not finish in 4 min; the first
-- ingest, which deletes nothing, took 6 s). The name indexes serve `kb code`.
CREATE INDEX IF NOT EXISTS code_files_repo ON code_files(repo_id, path);
CREATE INDEX IF NOT EXISTS symbols_file ON symbols(file_id);
CREATE INDEX IF NOT EXISTS symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS symbols_qualname ON symbols(qualname);
CREATE INDEX IF NOT EXISTS code_chunks_file ON code_chunks(file_id);
CREATE INDEX IF NOT EXISTS code_chunks_sym ON code_chunks(sym_id);
CREATE INDEX IF NOT EXISTS params_file ON params(file_id);
CREATE INDEX IF NOT EXISTS params_name ON params(repo_id, name, block);
CREATE INDEX IF NOT EXISTS impl_links_sym ON impl_links(sym_id);
