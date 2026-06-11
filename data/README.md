# North Star Data Index

This folder is the human and agent entry point for demo data.

The committed hospital demo data lives under `hospital/`.

The old root JSON files were active hospital fixtures, not obsolete supermarket
fixtures, but they have been moved out of the repository root so the project
does not look like it is still organized around the old prototype. The duplicate
mirror folder was removed; `hospital/` is now the single source of truth.

Use `hospital-demo-data-manifest.json` as the quick index for what each data
file contains.

Validation:

```bash
npm run check:demo-data
npm run check:fixture-language
```
