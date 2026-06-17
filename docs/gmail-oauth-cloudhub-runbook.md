# Gmail OAuth And CloudHub Runbook

This runbook explains how to connect a Gmail sender for the Logia supplier
email demo without committing secrets. The current hackathon path uses one
manager/demo Gmail account as the sender and one supplier email as the demo
recipient.

## Product Shape

The best plug-and-play design is:

1. Salesforce/Logia settings page shows **Connect Gmail**.
2. The manager signs in with Gmail.
3. Salesforce stores connection ownership and policy state.
4. Anypoint/CloudHub stores the provider token as a secure property or named
   credential equivalent.
5. Slack only shows business actions: **Approve**, **Reject**, and **Modify**.
6. If the manager changes, disable the old connection and connect the new
   Gmail account.

Do not ask managers to paste OAuth tokens into Slack.

## Manual OAuth Setup

Create the Google OAuth client:

1. Open Google Cloud Console.
2. Enable **Gmail API**.
3. Configure the OAuth consent screen.
4. Add the manager/demo Gmail as a test user.
5. Create an OAuth client.
6. Add this redirect URI:

```text
https://developers.google.com/oauthplayground
```

Use the narrow scope:

```text
https://www.googleapis.com/auth/gmail.send
```

In Google OAuth Playground, use your own OAuth credentials, authorize the
`gmail.send` scope, and exchange the authorization code for tokens. Save only
the refresh token. Do not commit the client secret or refresh token.

## Local Windows Environment

Each teammate can use their own sender Gmail by setting these user environment
variables:

```powershell
[Environment]::SetEnvironmentVariable("GMAIL_CLIENT_ID", "<google-client-id>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_CLIENT_SECRET", "<google-client-secret>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_REFRESH_TOKEN", "<google-refresh-token>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_SENDER_EMAIL", "<manager-demo@gmail.com>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_SUPPLIER_EMAIL", "<supplier-demo@gmail.com>", "User")
```

The sender email must match the Gmail account that authorized the refresh
token. If a new manager owns the mailbox, reconnect Gmail and replace the
refresh token.

## CloudHub Secure Properties

Use the helper script from the repository root:

```powershell
.\scripts\configure-cloudhub-logia-secrets.ps1 `
  -SupplierEmail "supplier@example.com" `
  -TargetOrg hfs-dev
```

The script refreshes the Salesforce token from `hfs-dev`, reads Meta, Slack,
and Gmail values from the Windows user environment, and applies the complete
CloudHub property set in one Anypoint CLI call.

This matters because `anypoint-cli-v4 runtime-mgr application modify` can
replace the CloudHub property set. Do not update only one secret unless you
also preserve the existing required properties.

The required CloudHub values are:

| Type   | Key                          |
| ------ | ---------------------------- |
| normal | `logia.tenant`               |
| normal | `logia.purpose`              |
| normal | `northstar.tenant`           |
| normal | `northstar.purpose`          |
| normal | `salesforce.host`            |
| normal | `meta.webhookVerifyToken`    |
| normal | `meta.whatsappPhoneNumberId` |
| normal | `slack.channelId`            |
| secure | `salesforce.accessToken`     |
| secure | `meta.whatsappAccessToken`   |
| secure | `slack.signingSecret`        |
| secure | `slack.botToken`             |
| secure | `gmail.clientId`             |
| secure | `gmail.clientSecret`         |
| secure | `gmail.refreshToken`         |
| secure | `gmail.senderEmail`          |
| secure | `gmail.supplierEmail`        |

## Smoke Tests

After CloudHub returns to `RUNNING`, test the live route:

```powershell
$uri = "https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound"
Invoke-WebRequest -Method Post -Uri $uri `
  -Body @{ command = "/logia"; text = "queue"; user_name = "ops-manager" } `
  -ContentType "application/x-www-form-urlencoded"
```

Expected result: HTTP `200` with the Logia queue summary.

Meta webhook verification smoke test:

```powershell
Invoke-WebRequest -Method Get `
  -Uri "$uri?hub.mode=subscribe&hub.verify_token=north-star-meta-verify&hub.challenge=logia-smoke"
```

Expected result: HTTP `200` with body `logia-smoke`.

## Current CloudHub Behavior

The Python MuleSoft reference runtime and deployed CloudHub channel app can send
Gmail after approval when these credentials are present. The Slack approval
route refreshes the Gmail access token, sends the supplier email through Gmail
API, and returns a `gmail-api` provider message id when delivery succeeds.

Claim live Gmail delivery only when the approval response shows provider
`gmail-api` with a message id. If Gmail credentials are missing or Gmail fails,
the supplier email stays in the protected queue and Logia reports the fallback.
