# Aarav Data Review: 2026-06-09

## Summary

The uploaded data is a useful starter set, but it is not demo-ready yet. It has
the right direction: three stores, six suppliers, thirty products, twenty-two
events, and twelve recommendation cases. The main weakness is that it is still
too shallow for the North Star agent workflow and is not wired into the existing
event fixture validation path.

## Strengths

- Includes three Mauritius supermarket stores and six synthetic suppliers.
- Includes thirty products across several categories, so it avoids a
  burger-only demo.
- Includes twenty-two retail events, which is close to the roadmap target.
- Includes twelve recommendation cases, matching the target count.
- Covers useful issue types: waste, quality complaints, expiry, price mismatch,
  missing items, supplier delay, and temperature deviation.

## Weaknesses To Fix

- Product categories are only six, while the assignment asks for eight:
  fresh food, frozen food, bakery, dairy, beverages, household, pharmacy shelf,
  and electronics.
- Sales data has only fourteen store-day rows for one store. The assignment
  asks for daily summaries across three stores, thirty products, and fourteen
  days.
- There are no product batches, inventory positions, warehouse inventory,
  promotions, complaint clusters, refund records, supplier responses, roster
  records, queue pressure records, task templates, or channel recipient aliases.
- Event IDs such as `EVT-001` are readable, but they do not match the existing
  event-envelope validator expectation that source event IDs are UUIDs.
- `EVT-012` intentionally or accidentally has no `type`; if it is meant to be a
  malformed event, it should live in a clearly named malformed fixture with an
  expected rejection result.
- `hfscontenthash` values such as `hash-001` are placeholders, not real
  `sha256:` hashes, so they will not pass the existing content-hash contract.
- Root-level JSON files are easy to inspect, but they are not yet integrated
  into `integration/events/fixtures/` or the Salesforce/LWC seed path.

## Recommended Next Step

Keep these files as drafts, then normalize them into the repo's existing
fixtures:

- move validated event envelopes under `integration/events/fixtures/retail/`;
- add one data inventory file that names stores, products, batches, suppliers,
  evidence IDs, role aliases, and expected recommendation cases;
- create a smaller coherent demo slice first: one stockout plus complaint case,
  one supplier response, one approval, one Slack alert, one WhatsApp alert, and
  one outcome.

This will be much more useful for the team than generating a large dataset that
the app cannot consume yet.
