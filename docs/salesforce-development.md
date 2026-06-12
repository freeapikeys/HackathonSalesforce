# Salesforce Development

## Prerequisites

- Node.js 20 or newer
- Salesforce CLI v2
- A Salesforce development org, or a Dev Hub for scratch-org workflows

Install dependencies and run checks that do not require an authenticated org:

```bash
./scripts/bootstrap-runtime.sh
npm run check
```

`npm run check` validates the Salesforce DX structure and semantic contract,
checks formatting and JavaScript, and runs Lightning Web Component tests. The
test command succeeds when no LWC tests exist yet and becomes enforcing as
components are added.

## Authenticate

For a persistent development org:

```bash
sf org login web --alias hfs-dev --set-default
```

For a scratch org, authenticate a Dev Hub and create the org:

```bash
sf org login web --alias hfs-dev-hub --set-default-dev-hub
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias hfs-scratch \
  --duration-days 7 \
  --set-default
```

No credentials, access tokens, org identifiers, or local Salesforce state
belong in Git.

## Metadata Workflow

Preview and deploy the current package:

```bash
sf project deploy preview --source-dir force-app
sf project deploy start --source-dir force-app
```

For the core metadata used by both HFS and North Star, assign the integration
permission set to the connected integration identity and run the rollback smoke
test:

```bash
sf org assign permset \
  --name HFS_Integration_User \
  --target-org hfs-dev
sf apex run \
  --file scripts/apex/verify_core_metadata.apex \
  --target-org hfs-dev
```

Retrieve metadata intentionally by type or name. Do not retrieve an entire org
into the repository.

```bash
sf project retrieve start --manifest manifest/package.xml
```

Before opening a pull request, run:

```bash
npm run check
sf apex run test \
  --tests HFS_ServiceContractTest \
  --result-format human \
  --wait 10
./scripts/sync-beads.sh
git diff --check
```

Skip `./scripts/sync-beads.sh` only when Beads is not installed and no Beads
state changed.

## North Star Demo Workflow

When the North Star seed and harness are implemented, use the same org alias and
run:

```bash
npm run demo:reset -- --target-org hfs-dev
npm run demo:seed -- --target-org hfs-dev
npm run demo:run -- --target-org hfs-dev
```

The expected demo should create private hospital operations context, manager
approval, MuleSoft mock write-back, Slack and WhatsApp-style alert records,
clinical-decision refusal, outcome, and evaluation without manual Salesforce
record edits.

For the final rehearsal, the human setup work is:

- authenticate the org alias with `sf org login web --alias hfs-dev --set-default`;
- confirm it with `sf org display --target-org hfs-dev`;
- deploy metadata and assign `HFS_Integration_User`; the harness assigns
  `HFS_Approver` and `HFS_Integration_User` to the connected user before seed
  and run;
- keep Slack and WhatsApp credentials outside Git. `SLACK_WEBHOOK_URL` enables a
  real Slack webhook, and `SLACK_SIGNING_SECRET` enables live Slack approval
  buttons when a public interactivity URL is configured. Official Meta
  WhatsApp Cloud API credentials enable WhatsApp delivery for the hackathon;
  Twilio Sandbox is legacy backup only. Missing credentials are acceptable only
  when the presenter calls out the honest `MOCK_SENT` fallback.
