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

Retrieve metadata intentionally by type or name. Do not retrieve an entire org
into the repository.

```bash
sf project retrieve start --manifest manifest/package.xml
```

Before opening a pull request, run:

```bash
npm run check
./scripts/sync-beads.sh
git diff --check
```
