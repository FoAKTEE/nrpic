-- Migration 6 (stages K4-K5, embeddings): provenance of every vector and the model registry.
-- embeddings.model is '<model name>@<revision7>' (kbtool/embed_model.py); a new model or
-- revision adds a new set of rows and keeps the old one (brief 12.6).
ALTER TABLE embeddings ADD COLUMN text_sha256 TEXT;   -- sha256 of the exact string embedded (recipe applied)
ALTER TABLE embeddings ADD COLUMN n_tokens INTEGER;   -- word pieces before truncation
ALTER TABLE embeddings ADD COLUMN truncated INTEGER;  -- 1 when n_tokens exceeds the model's max_seq_length
ALTER TABLE embeddings ADD COLUMN at TEXT;
CREATE INDEX embeddings_model_kind ON embeddings(model, owner_kind);
CREATE TABLE embed_models(
  model TEXT PRIMARY KEY,                             -- value of embeddings.model
  name TEXT NOT NULL, revision TEXT NOT NULL,         -- full revision hash of the model repository
  dim INTEGER NOT NULL, pooling TEXT, normalized INTEGER, max_seq_length INTEGER, query_prefix TEXT,
  weights_sha256 TEXT, license TEXT, source TEXT,
  recipe_json TEXT,                                   -- the strings embedded per owner kind (kbtool/embed_index.py)
  runtime_json TEXT,                                  -- library versions and threads of the last run
  created_at TEXT);
