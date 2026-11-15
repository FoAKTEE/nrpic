# 0015 Knowledge base: metadata, PDF mode, embedding model

Status: PROVISIONAL · 2026-11-15

- Metadata of the manifest entries may be fetched from the arXiv API and from INSPIRE
  through `harness/bin/nrpic-fetch-arxiv` only (one lock per service, three seconds
  between requests, a generic client name, nothing about the user or the project in a
  request).
- The same command gets a PDF mode for entries without a TeX source, a size limit and a
  content check.
- One open embedding model may be downloaded once into the environment of `wt/kb`; no
  paper text leaves the machine.
- The weekly check of upstream AthenaK is run by the knowledge-base session of each wave.
