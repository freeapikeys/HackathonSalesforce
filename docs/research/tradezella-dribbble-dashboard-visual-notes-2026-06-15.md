# TradeZella And Dribbble Dashboard Visual Notes

Date: 2026-06-15

Purpose: adapt the command center toward a TradeZella-like analytics dashboard
without copying a proprietary screen. The implementation should preserve the
closed-loop intelligence product model and Salesforce/LWC constraints.

## Sources

- TradeZella homepage: <https://www.tradezella.com/>
- TradeZella trading journal page:
  <https://www.tradezella.com/trading-journal>
- Dribbble trading journal search:
  <https://dribbble.com/search/trading-journal>
- Dribbble dark SaaS dashboard search:
  <https://dribbble.com/search/dark-saas-dashboard>
- Dribbble dark analytics dashboard search:
  <https://dribbble.com/search/analytics-dashboard-dark>
- Dribbble trading platform dashboard search:
  <https://dribbble.com/search/trading-platform-dashboard>

## Design Translation

- TradeZella pattern: trading journal dashboard, synced records, analytics
  reports, filters, AI coaching, replay/backtesting, P&L-style curves,
  calendar/log views, and strategy tracking.
- Command-center translation: relationship-intelligence journal, synced
  evidence, prediction reports, terrain filters, Agentforce recommendations,
  replayable evidence timeline, approval/action log, and outcome tracking.
- Visual direction: dark app shell, persistent left rail, dense card grid,
  compact chart panels, status chips, muted dividers, green positive accents,
  red risk/denial accents, and high-contrast operational text.
- Constraint: keep the current LWC data contract and interactions. Do not add
  fake trading controls, broker language, or speculative financial labels.

## Concrete UI Decisions

1. Add a dark sidebar/rail to make the screen feel like an analytics product
   rather than a single Salesforce card.
2. Move the main canvas to dark charcoal and make panels/cards the primary
   information units.
3. Keep the terrain switcher as the equivalent of TradeZella account/report
   switching.
4. Treat KPI cards like trade analytics widgets: large number, small status
   chip, confidence, and progress bar.
5. Treat daily brief, agent threads, shared chats, evidence timeline, approval,
   actions, and outcome as the journal/review loop.
