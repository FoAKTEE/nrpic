-- Migration 3 (stages K2-K3, papers): locators and provenance the schema of brief 12.2 lacks.
-- All character offsets refer to build/tex/<id_>/flat.tex of the paper, whose sha256 is
-- papers.flat_sha256; build/tex/<id_>/sourcemap.json maps an offset to file, line and column.
ALTER TABLE papers ADD COLUMN flat_sha256 TEXT;
ALTER TABLE papers ADD COLUMN title_source TEXT;           -- 'tex' (from \title) until the metadata stage
ALTER TABLE papers ADD COLUMN parse_json TEXT;             -- quality components, converter, counts, notes
ALTER TABLE papers ADD COLUMN tool_version TEXT;
ALTER TABLE equations ADD COLUMN char_start INTEGER;
ALTER TABLE equations ADD COLUMN char_end INTEGER;
ALTER TABLE figures ADD COLUMN kind TEXT;                  -- 'figure' or 'table'
ALTER TABLE figures ADD COLUMN section_id INTEGER;
ALTER TABLE figures ADD COLUMN char_start INTEGER;
ALTER TABLE figures ADD COLUMN char_end INTEGER;
ALTER TABLE bib_entries ADD COLUMN source TEXT;            -- 'bbl', 'bib' or 'thebibliography'
ALTER TABLE bib_entries ADD COLUMN title TEXT;             -- title found in the entry, if any
ALTER TABLE bib_entries ADD COLUMN eprint TEXT;            -- the eprint field as written
ALTER TABLE citations ADD COLUMN cite_key TEXT;
ALTER TABLE citations ADD COLUMN char_start INTEGER;       -- offset of the \cite command
CREATE INDEX sections_paper ON sections(paper_id);
CREATE INDEX chunks_paper ON chunks(paper_id);
CREATE INDEX equations_paper_label ON equations(paper_id, label);
CREATE INDEX figures_paper ON figures(paper_id);
CREATE INDEX bib_entries_paper ON bib_entries(paper_id, cite_key);
CREATE INDEX citations_citing ON citations(citing);
