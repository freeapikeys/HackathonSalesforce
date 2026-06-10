# Agent Instructions

## Required Context

Before starting work:

1. Read `ROADMAP.md`.
2. Read `docs/north-star-mvp.md`.
3. Read `docs/north-star-implementation-plan.md`.
4. If you are doing a teammate task, read the matching file in
   `docs/assignments/`.
5. Read the relevant contract or source files for the surface you are changing.
6. Run `bd prime` and `bd ready` if Beads is installed.
7. If Beads is not installed, use the checklist in `ROADMAP.md` and say which
   checklist item you are advancing.

The roadmap is the visible hackathon checklist. Beads is useful for dependency
tracking, but it is not required to understand the build.

## North Star Context

North Star is the active product. It is a Salesforce, Agentforce, and MuleSoft
operations command center that turns messy business signals into evidence-backed
recommendations, approved actions, role-based alerts, and measurable outcomes.

The product direction is now a global, plug-and-play operating model with one
flagship demo profile: a large private hospital operations command center.

Do not drift back into the old generic chatbot idea. North Star is not a broad
Q&A bot. It is a governed multi-agent operating system with universal business
primitives, business-specific profiles, manager approval, and outcome tracking.

The global primitives are:

- `Signal`
- `Evidence`
- `Entity`
- `Resource`
- `Location`
- `Actor`
- `Customer`
- `Partner`
- `Process`
- `Risk`
- `Policy`
- `Recommendation`
- `Approval`
- `Action`
- `Outcome`
- `Metric`

Business-specific concepts must map into those primitives instead of creating a
separate architecture. For example, hospital beds, hotel rooms, airport gates,
bank accounts, supermarket product batches, and cruise cabins are all typed
`Resource` records.

## Private Hospital Demo Boundary

The hospital demo solves non-clinical operations problems:

- patient and visitor complaints;
- bed, room, queue, staff, pharmacy-stock, and equipment availability;
- discharge cleaning and service-task coordination;
- lab, laundry, food, insurance, payment, and maintenance partner delays;
- billing, refund, claim, and payment-review workflows;
- manager approval, internal alerts, audit trail, and outcome tracking.

North Star must not make diagnosis, treatment, dosage, triage, or clinical
priority decisions. If a user asks for a medical decision, the system must refuse
the action and route the matter to an appropriate clinician or manager.

## North Star Agents

The visible demo should feel like one coordinated product, not many disconnected
chatbots. Agents may be implemented as Agentforce topics, prompt profiles,
deterministic reasoning modules, or action contracts, but their responsibilities
are:

- North Star Orchestrator Topic;
- Evidence and Context Agent;
- Patient Trust Agent;
- Resource and Capacity Agent;
- Operations Execution Agent;
- Partner and Vendor Agent;
- Risk and Approval Agent;
- Financial Impact Agent;
- Communication Agent;
- Outcome Learning Agent.

Optional specialist skills may be added only when they plug into the same
primitives and approval rules, for example Hospital Operations, Inventory and
Capacity, Billing and Insurance, Vendor SLA, Patient Experience, Food Safety, or
Fraud Review.

## Issue Tracking

This project can use [Beads](https://github.com/steveyegge/beads) when
available.

Useful commands:

```bash
bd prime
bd ready
./scripts/team-status.sh
bd show <id>
bd update <id> --claim
bd create "Title" --type task --priority 2
bd dep add <issue> <depends-on>
bd close <id> --reason "Acceptance checks passed"
./scripts/sync-beads.sh
```

Close a bead only after its acceptance checks pass. If you change Beads, run
`./scripts/sync-beads.sh` and commit the updated `.beads/issues.jsonl`.

## Engineering Rules

- Use plain operations language that hospital, hotel, airport, and banking
  judges can understand.
- Preserve source records and evidence.
- Distinguish facts, claims, inferences, recommendations, decisions, actions,
  and outcomes.
- Define every metric, score, formula, time window, confidence value, and
  threshold.
- Do not silently overwrite contradictory evidence. Supersede it explicitly.
- External actions require the configured policy and manager approval.
- Slack, WhatsApp, supplier/vendor, pharmacy stock, billing, refund, insurance,
  room/bed, staff-task, and customer/patient-message write-backs are protected
  external actions unless explicitly scoped as local demo mocks.
- Approval means a business manager role in the MVP, not a Salesforce admin and
  not a developer approving implementation work. A command-center button or
  Salesforce approval/status record is acceptable for the hackathon demo.
- Agents operate with the current user's permissions and purpose restrictions.
- Prefer existing Salesforce, Agentforce, MuleSoft, model-gateway, LWC, and
  harness patterns before adding new architecture.
- Add focused tests for every behavioral change.

## Workflow

1. **Scope:** identify the roadmap checkbox being advanced.
2. **Trace:** identify the source data, evidence, action, owner, and failure
   path.
3. **Assemble:** implement the smallest complete behavior.
4. **Verify:** run the focused checks and record what passed.
5. **Update:** keep docs and checklist status honest.

Use language models for interpretation and recommendations, not for invariants
that must always execute deterministically.

## Documentation

- Update `ROADMAP.md` when a checklist item is truly complete.
- Keep `docs/north-star-mvp.md` as the product brief.
- Keep `docs/north-star-implementation-plan.md` as the practical build plan.
- Record architecture decisions in `docs/decisions/` only when a real contract
  decision changes.
- Never commit secrets, personal memory, downloaded copyrighted source files,
  patient records, medical records, agent transcripts, or machine-local paths.
