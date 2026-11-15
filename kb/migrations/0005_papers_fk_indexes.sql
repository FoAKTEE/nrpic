-- Migration 5 (stages K2-K3, papers): indexes on the child columns of the foreign keys of the
-- paper tables. Without them SQLite checks each deleted parent row (re-ingesting a paper
-- deletes its sections, chunks, bibliography entries) with a full scan of the child table.
CREATE INDEX IF NOT EXISTS citations_bib ON citations(bib_id);
CREATE INDEX IF NOT EXISTS citations_chunk ON citations(chunk_id);
CREATE INDEX IF NOT EXISTS chunks_section ON chunks(section_id);
CREATE INDEX IF NOT EXISTS equations_section ON equations(section_id);
CREATE INDEX IF NOT EXISTS bib_entries_target ON bib_entries(target_arxiv);
