# North Star Demo Data

## First Demo Product

The first live story uses fresh-food island beef burger patties because judges
can quickly understand the operational risk: low stock, near-expiry units,
quality complaints, price mismatch, supplier uncertainty, and weekend queue
pressure.

## Product Categories

| Category    | Product                       | Demo purpose                                           |
| ----------- | ----------------------------- | ------------------------------------------------------ |
| Fresh food  | Island beef burger patties    | Primary stockout, expiry, quality, and promotion story |
| Frozen food | Vanilla family ice cream tubs | Frozen stockout and supplier lead-time comparison      |
| Dairy       | Greek yogurt multipacks       | Expiry and cold-chain complaint extension              |
| Beverages   | Sparkling water multipacks    | Overstock and seasonal demand pressure                 |
| Household   | Laundry detergent cartons     | Price mismatch and shelf signage correction            |
| Electronics | Rechargeable power banks      | High-value stockout and supplier delay example         |

## Fixture IDs

| Retail concept        | Fixture ID                          |
| --------------------- | ----------------------------------- |
| Store                 | `STORE-GOODLANDS-FRESHMART`         |
| Supplier              | `SUPPLIER-ISLAND-PROTEINS`          |
| Product               | `PROD-FRESH-BEEF-PATTIES-400G`      |
| Product batch         | `BATCH-FRESH-BEEF-2026-06-07-A`     |
| Promotion             | `PROMO-WEEKEND-GRILL-2026-W23`      |
| Shelf area            | `SHELF-MEAT-CHILLER-A3`             |
| Roster                | `ROSTER-GOODLANDS-2026-06-06-PM`    |
| Restock task          | `TASK-RESTOCK-FRESH-BEEF-001`       |
| Shelf correction task | `TASK-SHELF-PRICE-FRESH-BEEF-001`   |
| Queue task            | `TASK-CHECKOUT-OPEN-LANE-001`       |
| Correlation           | `CORR-NORTH-STAR-WEEKEND-GRILL-001` |

## Stock and Demand

| Location  |  Quantity | Notes                                                |
| --------- | --------: | ---------------------------------------------------- |
| Shelf     |  18 units | Below minimum weekend display level of 36 units      |
| Backroom  |  24 units | Includes 12 near-expiry units requiring rotation     |
| Warehouse |  72 units | Transfer can arrive before 14:00                     |
| Supplier  | 180 units | Replacement batch available, normal delivery delayed |

Sales velocity is 28 units per hour during the promotion window. The forecast
window is 10:00 to 19:00 on Saturday, with the highest pressure expected from
15:00 to 18:00. Current combined store stock gives 1.5 hours of cover before
warehouse transfer.

## Supplier Response Options

| Response ID                               | Meaning                     | Recommended interpretation                                  |
| ----------------------------------------- | --------------------------- | ----------------------------------------------------------- |
| `SUPPLIER_RESPONSE-REPLACEMENT-APPROVED`  | Replacement batch confirmed | Request replacement and keep safe transfer option           |
| `SUPPLIER_RESPONSE-CREDIT-NOTE`           | Credit note offered         | Preserve outcome and continue batch investigation           |
| `SUPPLIER_RESPONSE-DELAYED-DELIVERY`      | Lead time slips past rush   | Prefer warehouse transfer or alternate source               |
| `SUPPLIER_RESPONSE-INSUFFICIENT-EVIDENCE` | Supplier disputes issue     | Keep evidence review open and avoid broad supplier block    |
| `SUPPLIER_RESPONSE-UNRESOLVED-QUALITY`    | Quality issue unresolved    | Require manager approval before reorder or customer message |

Default lead time is 36 hours. Replacement-batch lead time is 18 hours.
Warehouse-transfer lead time is 4 hours.

## Complaint Examples

| Complaint type    | Example                                                       |
| ----------------- | ------------------------------------------------------------- |
| Smell             | "Opened pack had a sour smell before the use-by date."        |
| Damaged packaging | "Film seal was loose and liquid leaked in the bag."           |
| Price mismatch    | "Shelf said promo price, but checkout charged regular price." |
| Refund            | "Customer returned two packs from the same batch."            |
| Availability      | "Promotion display empty before the lunch rush."              |

## Expiry and Waste

The batch expires on 2026-06-08. Twelve backroom units and six shelf units are
near expiry. Safe near-expiry units should be rotated forward or marked down
before 17:00. Any unit connected to unresolved quality evidence should be
quarantined instead of discounted.

## Queue and Staffing

Baseline staffing has three checkout lanes open and one aisle colleague assigned
to promotion replenishment. The queue-risk window is 16:30 to 18:30. The store
operations recommendation is to open one extra cashier lane from 16:15, move one
aisle colleague to checkout if queue depth exceeds eight customers, and keep the
fresh-food lead assigned to rotation and quarantine tasks.

## Expected Outcome Metrics

| Metric           | Target                                                             |
| ---------------- | ------------------------------------------------------------------ |
| Stockout avoided | At least 50 units protected through transfer or replacement        |
| Waste reduced    | At least 18 near-expiry units rotated, marked down, or quarantined |
| Complaint risk   | Affected batch isolated and supplier case opened                   |
| Queue readiness  | Extra cashier lane opened before 16:30                             |
| Staff execution  | Critical tasks acknowledged within 10 minutes                      |
| Supplier SLA     | Supplier response captured with lead time and resolution state     |
