# North Star Data Index

This folder is the human and agent entry point for demo data.

The canonical committed hospital demo data lives under `hospital/`.

The older `../synthetic_data/` folder remains as a compatibility mirror for
teammate prompts and agents that still look there. The validator checks that the
canonical files and mirror files stay identical.

The old root JSON files were active hospital fixtures, not obsolete supermarket
fixtures, but they have been moved out of the repository root so the project
does not look like it is still organized around the old prototype.

Do not edit only one copy. Update the canonical `hospital/` file first and keep
the `../synthetic_data/` mirror in sync, then run the validators.

Use `hospital-demo-data-manifest.json` as the quick index for what each data
file contains.

Validation:

```bash
npm run check:demo-data
npm run check:fixture-language
```
