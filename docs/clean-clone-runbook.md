# Clean-Clone Completion Runbook

## Purpose

This runbook proves that a repository ref can reproduce the current North Star
hospital MVP without manual Salesforce record edits:

`hospital operations surge -> global primitives and evidence -> model-routed
Agentforce recommendation -> clinical-refusal guardrail -> manager approval ->
approved Salesforce task action records plus Slack and WhatsApp-style MuleSoft
channel actions -> hospital outcomes and evaluations -> refreshed North Star
command center`

The verifier creates a temporary clone, installs locked dependencies, runs all
repository checks, deploys Salesforce metadata with the four Apex test suites,
runs the connected demo, validates its governed failure paths, and writes a
sanitized JSON evidence artifact.

## Prerequisites

The operator needs:

- access to the private Git repository;
- Git, Node.js 20 or newer, npm, Python 3.12 or newer, Salesforce CLI v2, and
  a Unix-style shell for `scripts/verify-clean-clone.sh`;
- an authenticated Salesforce development org;
- permission to deploy metadata and assign the demo permission sets.

Authenticate once if the target alias is not already connected:

```bash
sf org login web --alias hfs-dev
sf org display --target-org hfs-dev
```

Expected result: Salesforce CLI reports the org as connected. Do not add its
credentials, username, URL, or local auth state to the repository.

On Windows, run the shell script from Git Bash or WSL. Local npm checks and
demo commands are Windows-aware, but the clean-clone wrapper itself is a Bash
script.

## Completion Command

From any clone of this repository:

```bash
./scripts/verify-clean-clone.sh \
  --target-org hfs-dev \
  --ref main \
  --output artifacts/clean-clone-result.json
```

For a pull-request branch, push the branch and replace `main` with its remote
branch name. The default repository is the current clone's `origin` URL.

The equivalent npm command is:

```bash
npm run verify:clean-clone -- \
  --target-org hfs-dev \
  --ref main
```

## Expected Checkpoints

| Stage               | Command or behavior                                          | Expected result                                                                                                          |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| Authenticate        | `sf org display --target-org hfs-dev --json`                 | Connected org; no auth data enters the artifact                                                                          |
| Clone               | `git clone --single-branch --branch main ...`                | Temporary clone resolves to one full commit SHA                                                                          |
| Bootstrap           | `./scripts/bootstrap-runtime.sh`                             | Locked Python and npm dependencies install                                                                               |
| Repository checks   | `npm run check`                                              | Contracts, ontology, events, MuleSoft, models, Agentforce, metadata, formatting, lint, harness tests, and LWC tests pass |
| Salesforce deploy   | `sf project deploy start ... --test-level RunSpecifiedTests` | Metadata succeeds; all Apex test classes run with zero failures                                                          |
| Connected demo      | `npm run demo:run -- --target-org hfs-dev ...`               | Every connected step passes, including clinical refusal plus Slack and WhatsApp-style mock delivery                      |
| Evidence validation | `scripts/verify_clean_clone_result.py`                       | Required success, refusal, approval, channel, and outcome invariants pass                                                |

The final terminal line contains `Clean-clone verification passed`. The JSON
artifact has:

```json
{
  "schemaVersion": "1.0.0",
  "status": "passed",
  "source": {
    "ref": "main",
    "commit": "<full-git-sha>"
  },
  "deployment": {
    "status": "Succeeded",
    "testFailures": 0
  },
  "demo": {
    "status": "passed"
  }
}
```

The artifact records no access token, refresh token, username, org URL,
command log, machine-local path, real patient data, or medical record.

## Required Invariants

Evidence validation fails unless all of these are true:

- the restricted model route returns `NO_QUALIFIED_DEPLOYMENT` and
  `FAILED_CLOSED`;
- Agentforce refuses inaccessible evidence with `INACCESSIBLE_EVIDENCE`;
- Agentforce cites evidence, preserves the model invocation ID, covers
  complaint, resource, capacity, partner, billing, stock, staffing, approval,
  and post-outcome context, and does not execute the external action;
- Salesforce rejects action logging before approval with `INVALID_STATE`;
- MuleSoft rejects an unregistered approval with `403 PERMISSION_DENIED`;
- MuleSoft accepts approved channel write-backs with `202 QUEUED`;
- approved Slack delivery is recorded as `SENT` or honest `MOCK_SENT`;
- approved WhatsApp-style delivery is recorded as `SENT` or honest `MOCK_SENT`;
- five task action records and two channel actions are `EXECUTED` in the final
  Salesforce context;
- the five task actions include required owner role aliases, escalation role
  aliases, deterministic priority ranks, approval requirement, service windows,
  and missed-task escalation windows that occur before service-window loss;
- direct Apex final context includes the customer alias, department/location,
  resources, partner, process, hospital evidence types, approved actions,
  delivery outcomes, business outcomes, and metric keys;
- outcomes are `SUCCESS`, work item is `COMPLETED`, and evaluations exist;
- final Salesforce counts include at least nine events, seven evidence records,
  seven actions, eight outcomes, eight evaluations, one recommendation,
  and one work item.

## Recovery

| Failure stage               | What to inspect                                   | Recovery                                                                                                      |
| --------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `prerequisites`             | Missing executable or unsupported runtime version | Install the required tool/version, then rerun the same command                                                |
| `salesforce-authentication` | Expired or absent target-org alias                | Run `sf org login web --alias <alias>`, then rerun                                                            |
| `clone`                     | Git access, branch spelling, or unpushed branch   | Confirm `gh auth status`, push the branch, and rerun with the exact remote ref                                |
| `bootstrap`                 | npm or pip network/package error                  | Restore registry access and rerun; dependencies are locked by `package-lock.json` and `requirements-dev.txt`  |
| `repository-checks`         | First failing validator or unit test              | Run `npm run check` in the working clone, fix the deterministic failure, push, and rerun                      |
| `salesforce-deployment`     | Metadata or Apex test failure                     | Rerun the deploy command from `docs/salesforce-development.md`; fix metadata or tests before running the demo |
| `connected-demo`            | `failedStage` plus the demo's failed step/error   | Run `npm run demo:reset -- --target-org <alias>`, then rerun the verifier                                     |
| `evidence-validation`       | Missing or changed invariant in the artifact      | Compare the connected report with the Required Invariants; do not bypass the validator                        |

Add `--keep-workdir` to preserve the temporary clone after a failure:

```bash
./scripts/verify-clean-clone.sh \
  --target-org hfs-dev \
  --ref main \
  --keep-workdir
```

The failure artifact identifies the failed stage. Temporary working directories
and raw CLI results remain outside Git.

The accepted first-slice release result is summarized in
[First Vertical Slice Completion Evidence](verification/first-vertical-slice-completion.md).
