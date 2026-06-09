# Aarav Data Review: 2026-06-09

## Summary

The new fake data is a major improvement over the first upload. It now includes
the main North Star evidence families: batches, inventory, warehouse stock,
promotions, complaints, complaint clusters, supplier responses, queue pressure,
task templates, channel aliases, expected recommendation cases, and validated
retail event fixtures.

It is much closer to demo-ready. The validated event fixtures are good, and the
draft JSON files now parse after cleanup on this branch. Remaining issues are
coverage and canonical-location decisions, not basic file validity.

## Strengths

- Adds the missing operational surfaces: batches, inventory positions,
  warehouse inventory, promotions, complaints, clusters, supplier responses,
  queue pressure, task templates, and channel aliases.
- Adds 14 validated retail event-envelope fixtures from stockout through
  outcome capture.
- Adds `docs/north-star-demo-data.md`, `docs/north-star-demo-narrative.md`, and
  `docs/north-star-agentforce-topics.md`, which helps the team keep one story.
- Includes 60 product batches, 90 inventory positions, 30 warehouse inventory
  records, 84 queue-pressure records, 20 task templates, 12 channel aliases, 12
  recommendation cases, 10 supplier responses, and 8 promotions.
- Includes 50 complaint records, meeting the lower end of the assignment target.
- The existing event contract now passes with 28 deterministic fixtures,
  including malformed, late, out-of-order, duplicate, idempotency-conflict, and
  invalid-hash cases.
- All root draft JSON and `synthetic_data/` JSON files parse successfully after
  typo cleanup.

## Weaknesses To Fix

- The product catalog still has 6 categories, while the assignment asks for 8.
  Missing categories are pharmacy shelf and electronics as separate categories.
- Sales data is still too thin: 14 store-day rows for one store, with 42 product
  sales entries. The assignment target is 3 stores x 30 products x 14 days.
- The root JSON files and `synthetic_data/` files duplicate each other. That is
  okay temporarily, but one canonical location should be chosen before the demo.
- Some draft source event IDs and hashes in `event_stream.json` are still not
  contract-valid. Treat `integration/events/fixtures/events/15-28*.json` as the
  real validated event fixtures.

## Recommendation

Keep the validated event fixtures and demo docs. Next, either remove the
duplicated root data files or document that `synthetic_data/` is the canonical
draft-data folder.

After that, expand sales coverage and categories only if the app actually
consumes those records. For the hackathon, clean parseable data matters more
than large volume, so this is now in a much healthier place.
