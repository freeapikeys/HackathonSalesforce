# UI Design Principles For The Command Center

Date: 2026-06-15

Purpose: ground the command-center polish work in current dashboard and UI
design sources without copying paid templates, private examples, or full video
transcripts.

## Source Capture

YouTube transcript extraction was attempted with `yt-dlp` for:

- How to Design a Dashboard with SHADCN UI?
  <https://www.youtube.com/watch?v=cuTXgWk0atk>
- EVERYTHING you need to know to build a Dashboard UI
  <https://www.youtube.com/watch?v=B7k5rOgmOGY>

Both `yt-dlp` attempts were blocked by YouTube sign-in or bot checks. A
temporary local `youtube-transcript-api` venv succeeded for the videos listed
below. Full transcripts were not stored in the repository; only implementation
takeaways are recorded.

YouTube transcripts reviewed:

- How to Design a Dashboard with SHADCN UI?
  <https://www.youtube.com/watch?v=cuTXgWk0atk>
- EVERYTHING you need to know to build a Dashboard UI
  <https://www.youtube.com/watch?v=B7k5rOgmOGY>
- NN/g, Data Visualizations for Dashboards:
  <https://www.youtube.com/watch?v=6arCpof4XIM>
- Jan Marshal, You're Using Shadcn/ui the WRONG Way:
  <https://www.youtube.com/watch?v=jHzdo1Bm9Lk>

Transcript-derived takeaways:

- Dashboard UI fails when information is messy, not merely when it is visually
  plain. The screen needs a strong hierarchy before decoration.
- shadcn-style components are useful as composable building blocks: cards,
  dense metrics, charts, tables/logs, and side or command navigation.
- The dashboard metaphor matters: users should be able to glance, identify the
  unacceptable deviation, and act. Do not turn the first screen into deep
  analysis.
- Avoid generic shadcn sameness. Keep the primitives, but make the visual
  language specific to this product: enterprise command center, evidence loop,
  approval boundary, and outcome feedback.

## Open Sources Used

- shadcn/ui dashboard example: <https://ui.shadcn.com/examples/dashboard>
- shadcn/ui blocks: <https://ui.shadcn.com/blocks>
- NN/g dashboard cognition and preattentive processing:
  <https://www.nngroup.com/articles/dashboards-preattentive/>
- NN/g chart-type guidance:
  <https://www.nngroup.com/articles/choosing-chart-types/>
- Smashing Magazine dashboard research, decluttering, and data visualization:
  <https://www.smashingmagazine.com/2021/11/dashboard-design-research-decluttering-data-viz/>
- UX Pilot 2026 dashboard design principles:
  <https://uxpilot.ai/blogs/dashboard-design-principles>

## Principles Applied

1. Treat the screen as an operational dashboard, not a generic portal. The
   first view should answer what changed, what is predicted, who owns the next
   action, and which actions are approval-gated.
2. Use length and 2D position for quantitative comparison. Keep prediction
   visuals linear and readable; avoid decorative gauges, pie charts, or 3D
   effects.
3. Follow shadcn-style composition without adding React dependencies:
   restrained cards, section headers, neutral theme, dense but clear metric
   blocks, charts, tables/logs, and command surfaces.
4. Reduce clutter through hierarchy, whitespace, and monochrome contrast. Use
   black and white as the base; use muted grays for secondary hierarchy rather
   than introducing a broad color palette.
5. Make interactivity honest. Terrain switching, approval buttons, retry,
   correction request, and live/mock states must do real work or dispatch a
   governed event. Do not add fake controls.
6. Keep the loop visible. Evidence, intelligence, approval, action, and outcome
   should be recognizable as one chain, because that is the product's core
   claim.
7. Color is a secondary cue. Labels, position, borders, copy, and shape must
   carry meaning for accessibility and color-blind users.

## Implementation Notes

- The LWC keeps Salesforce Lightning primitives and repository-owned CSS.
- No external shadcn package is added; the styling borrows composition
  principles only.
- No downloaded videos, transcripts, or screenshots are committed.
