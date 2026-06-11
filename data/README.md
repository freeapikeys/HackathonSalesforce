# North Star Data Index

This folder is the human and agent entry point for demo data.

The actual committed hospital demo data still lives in two places because the
existing validators expect both:

- root JSON files such as `../master_data.json`, `../complaints.json`, and
  `../warehouse_inventory.json`;
- mirrored copies under `../synthetic_data/` for teammates and agents that look
  for a dedicated synthetic data folder.

Do not move the root JSON files unless `scripts/validate-hospital-demo-data.mjs`
is updated at the same time. That validator proves root and `synthetic_data/`
copies are identical, synthetic, and safe for the hospital demo.

Use `hospital-demo-data-manifest.json` as the quick index for what each data
file contains.

Validation:

```bash
npm run check:demo-data
npm run check:fixture-language
```
