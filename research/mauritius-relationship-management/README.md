# Mauritius Relationship Management Research

This archive preserves the evidence used to define the product roadmap.

- `findings.md`: detailed findings and product implications.
- `source-register.json`: structured source inventory.
- `claims.jsonl`: claim-to-source map with locators and confidence.
- `download-manifest.json`: local archive status, file sizes, and SHA-256 hashes.
- `methodology.md`: research approach and limitations.
- `architecture-implications.md`: direct mapping from evidence to system design.
- `_downloads/`: ignored local copies fetched by the research script.

Run:

```bash
python3 scripts/fetch_research_sources.py
```

Downloaded files are kept local unless redistribution permission is confirmed.
The source register and findings remain committed so the research is
reproducible without committing copyrighted documents.
