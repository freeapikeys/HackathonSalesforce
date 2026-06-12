# Agentforce Publish Recovery Runbook

This runbook records how we recovered the North Star Agentforce Studio agent
when the live Builder chat was still giving generic Salesforce replies.

Use it when a future teammate, Codex session, or fresh Windows machine gets lost
while trying to make the latest North Star `.agent` source appear in Agentforce
Studio.

## Environment We Fixed

- Machine: Windows with PowerShell.
- Salesforce CLI alias: `hfs-dev`.
- Agentforce agent API name in Salesforce: `North_Star_Hospital_Operations`.
- Agent label in Builder: `North Star Global Operations`.
- Service agent user:
  `north_star_hospital_operations@00dg500000bw0jn1289071216.ext`.
- Local source bundle that must be published:
  `force-app/main/default/aiAuthoringBundles/North_Star_Hospital_Operations`.
- Source file:
  `force-app/main/default/aiAuthoringBundles/North_Star_Hospital_Operations/North_Star_Hospital_Operations.agent`.

Do not paste access tokens, frontdoor URLs, passwords, Twilio secrets, Slack
secrets, or recovery codes into this document or into Git.

## Symptoms

The Agentforce Builder preview was active, but it did not use the deep North
Star script:

- User: `I have a problem`
- Old live response: generic clarification such as "Could you please provide
  more details about the problem you're experiencing?"
- Builder reasoning selected the built-in `Ambiguous Question` path instead of
  the North Star universal operations flow.
- The visible Builder list did not reliably prove that the latest 10-agent
  source was live.

The expected fixed response is:

```text
What happened?
```

For a real mixed issue, the response should include a concise action plan with
primitive trace, facts, hypotheses, missing evidence, agents involved, approval
gate, next actions, and outcome metric.

## Errors We Saw

### Salesforce CLI publish errors

The official publish command sometimes failed from this Windows environment:

```powershell
sf agent publish authoring-bundle --api-name North_Star_Global_Operations_Script --target-org hfs-dev --skip-retrieve --json
```

Failures included:

- `ETIMEDOUT` to `test.api.salesforce.com:443`.
- `read EINVAL`.
- `Error refreshing connection`.
- `Error obtaining API token`.
- `User doesn't have access to agent`.

The timeout to `test.api.salesforce.com` looked scary, but it was not the only
problem. Production Salesforce REST calls worked from the same machine, so the
publish failure was not simply "no internet".

### Authorization errors

Direct API and library attempts exposed the more useful error:

```text
User doesn't have access to agent
```

The connected human user could deploy metadata, but did not initially have all
Agentforce builder permissions required for authoring-bundle compile/publish.

### Wrong local bundle target

We first had a local script bundle named:

```text
North_Star_Global_Operations_Script
```

That bundle had:

```text
developer_name: "North_Star_Global_Operations_Script"
```

Salesforce already had the real live agent as:

```text
North_Star_Hospital_Operations
```

Publishing the wrong developer name tried to create or access the wrong agent,
which caused access and mismatch problems.

### Wrong default agent user

The initial script pointed at the human user. The live service agent is the
Einstein service user:

```text
north_star_hospital_operations@00dg500000bw0jn1289071216.ext
```

Using the human user in the bundle made the source drift from the live Builder
agent.

### Final authoring-bundle metadata quirk

The direct library publish created `BotVersion` v2, but the final
`AiAuthoringBundle` metadata deploy reported:

```text
AuthoringBundleDeploymentError: Required field is missing: bundleType
```

This was a metadata packaging quirk after the bot version already existed. The
practical fix was to activate the created v2 bot version and retrieve the
working Bot and Planner metadata.

## Methods Tried

### Browser Builder edits

We opened Agentforce Builder in the in-app browser. It helped inspect the state,
but it was unreliable for the final fix because the Salesforce Builder UI
rendered duplicated/tiled panels in the browser tool. We did not depend on
manual browser clicks for the recovery.

Result: useful for visual inspection, not reliable enough for the fix.

### Phone hotspot and network retry

We retried while the machine was on a phone hotspot. Some calls still failed.
Direct production Salesforce REST worked, but `test.api.salesforce.com` still
timed out.

Result: did not fix the root problem.

### Temporary access-token alias

We created a temporary CLI alias from an access token to avoid refresh issues.
It reduced one kind of token problem, but did not solve the agent access and
bundle-name mismatch.

Result: not the final fix. Remove temporary aliases after use.

### Node version changes

We tried a direct Node path after CLI publish remained fragile. The issue was
not solved just by switching Node versions.

Result: not the root fix.

### Official CLI publish

The official command is still the preferred clean path when it works:

```powershell
sf agent publish authoring-bundle --api-name North_Star_Hospital_Operations --target-org hfs-dev --skip-retrieve --json
```

In this environment it remained fragile because of the Windows/network/API
token combination.

Result: correct idea, unreliable in this session.

### Direct Salesforce Agentforce library compile and publish

Using the same Salesforce libraries underneath the CLI let us compile and
publish the correct bundle more directly. This produced the v2 bot version.

Result: worked, then we activated v2 with the CLI.

## The Fix That Worked

### 1. Add and deploy Agentforce admin permissions

We added this permission set:

```text
force-app/main/default/permissionsets/North_Star_Agentforce_Admin.permissionset-meta.xml
```

It includes:

- `AIWorkbenchUser`
- `BotManageBots`
- `EinsteinAgentPlatformBuilder`
- `ManageAgentforceServiceAgent`
- `ManagePromptTemplates`
- `ViewRoles`
- `ViewSetup`

Deploy it:

```powershell
sf project deploy start --source-dir force-app/main/default/permissionsets/North_Star_Agentforce_Admin.permissionset-meta.xml --target-org hfs-dev --wait 10 --json
```

Assign it to the connected user:

```powershell
sf org display --target-org hfs-dev --json
sf org assign permset --name North_Star_Agentforce_Admin --target-org hfs-dev --on-behalf-of <salesforce-username-from-org-display> --json
```

If another teammate uses the org, assign the same permission set to that
teammate's Salesforce username.

### 2. Publish the correct source bundle name

The local source must target the live Salesforce agent API name:

```text
North_Star_Hospital_Operations
```

Check the `.agent` file contains:

```text
developer_name: "North_Star_Hospital_Operations"
agent_label: "North Star Global Operations"
default_agent_user: "north_star_hospital_operations@00dg500000bw0jn1289071216.ext"
```

The old `North_Star_Global_Operations_Script` bundle is useful as source
history, but it is not the live publish target.

### 3. Validate the bundle

```powershell
sf agent validate authoring-bundle --api-name North_Star_Hospital_Operations --target-org hfs-dev --json
```

This must pass before publishing.

### 4. Compile and publish with the direct Node fallback

Use this only when the official `sf agent publish authoring-bundle` command is
blocked by the Windows/API-token/network issue.

Run from the repository root:

```powershell
@'
const { Agent } = await import("@salesforce/agents");
const { Org } = await import("@salesforce/core");

const org = await Org.create({ aliasOrUsername: "hfs-dev" });
const agent = await Agent.init({
  org,
  projectPath: process.cwd(),
  aabName: "North_Star_Hospital_Operations"
});

console.log("Compiling North Star authoring bundle...");
await agent.compile();

console.log("Publishing North Star authoring bundle...");
const result = await agent.publish(true);
console.log(JSON.stringify(result, null, 2));
'@ | node --input-type=module
```

If this creates `BotVersion` v2 but ends with the `bundleType` deploy error,
continue to activation. The bot version is the part Builder needs for the live
conversation.

### 5. Activate the new version

```powershell
sf agent activate --api-name North_Star_Hospital_Operations --target-org hfs-dev --json
```

Expected result:

```json
{
  "success": true,
  "version": 2
}
```

### 6. Retrieve the live metadata

```powershell
sf project retrieve start --metadata Bot:North_Star_Hospital_Operations --metadata GenAiPlannerBundle:North_Star_Hospital_Operations --target-org hfs-dev --wait 10 --json
```

This should add or update files such as:

```text
force-app/main/default/bots/North_Star_Hospital_Operations/v2.botVersion-meta.xml
force-app/main/default/genAiPlannerBundles/North_Star_Hospital_Operations/...
force-app/main/default/genAiPlannerBundles/forceGenerated/plannerActions/.../schema.json
```

### 7. Smoke test the live Agentforce preview

Start preview:

```powershell
sf agent preview start --api-name North_Star_Hospital_Operations --target-org hfs-dev --json
```

Send a simple ambiguous issue:

```powershell
sf agent preview send --api-name North_Star_Hospital_Operations --session-id <session-id> --utterance "I have a problem" --target-org hfs-dev --json
```

Expected answer:

```text
What happened?
```

Send a mixed operations issue:

```powershell
sf agent preview send --api-name North_Star_Hospital_Operations --session-id <session-id> --utterance "A patient waited two hours, the room was not ready, pharmacy stock is low, and the bill looks duplicated." --target-org hfs-dev --json
```

Expected answer:

- one concise action plan;
- universal primitive trace;
- facts separated from likely causes;
- missing evidence;
- relevant agents involved from the 10-agent model;
- protected actions held behind manager approval;
- first outcome metric to check.

End preview:

```powershell
sf agent preview end --api-name North_Star_Hospital_Operations --session-id <session-id> --target-org hfs-dev --json
```

### 8. Run checks

```powershell
npm run check:agentforce
npm run check
```

## What Fixed Means

The fix is complete when:

- Agentforce Builder shows active version 2 for `North_Star_Hospital_Operations`.
- Preview says `What happened?` for `I have a problem`.
- A mixed issue returns a North Star action plan with the 10-agent coordination
  visible in the answer.
- `npm run check:agentforce` passes.
- `npm run check` passes before final merge.

## Current Known State

As of the fix recorded here:

- `North_Star_Hospital_Operations` is activated on version 2 in `hfs-dev`.
- The active source contains the universal North Star 10-agent model.
- The hospital remains only the active demo profile.
- Protected actions remain blocked behind manager approval.
- The direct Node fallback is documented because the normal Salesforce CLI
  publish path was unreliable on this Windows machine.

## Important Reminders

- Do not edit the active v1 agent and expect Builder to use the latest source.
  Publish or activate a new version.
- Do not publish a bundle whose `developer_name` does not match the Salesforce
  agent API name.
- Do not use a human user as the `default_agent_user` when the live service
  agent has a generated Einstein service user.
- Do not treat message delivery as the outcome. North Star must record whether
  the business issue improved.
- Do not let Agentforce execute Slack, WhatsApp, vendor, billing, inventory,
  refund, customer-message, partner, or service-task write-backs directly.
