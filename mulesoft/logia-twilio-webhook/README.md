# Logia Channel Webhook Mule App

This Mule app is the public channel door for the hackathon demo. It supports
Twilio Sandbox and Meta WhatsApp Cloud API webhook shapes, plus Slack
interactivity and slash-command acknowledgements.

Twilio flow:

1. Twilio Sandbox posts `application/x-www-form-urlencoded` data to the public
   CloudHub webhook URL: `https://<cloudhub-host>/twilio/whatsapp/inbound`.
2. Mule maps the message into a safe Logia intake payload.
3. Mule calls the Salesforce Apex REST endpoint
   `/services/apexrest/logia/v1/twilio/whatsapp`.
4. Salesforce creates `Signal`/event, customer alias, evidence, work item,
   recommendation, and pending approval records.
5. Twilio receives a short TwiML acknowledgement.

Meta flow:

1. Meta verifies the webhook with `GET` against the configured public CloudHub
   callback URL.
2. Meta posts WhatsApp Cloud API JSON to `POST` against the same callback URL.
3. Mule maps the Meta message into the same safe Logia intake payload.
4. Mule calls the same Salesforce Apex REST endpoint used by the Twilio path.
5. Meta receives a JSON acknowledgement.

CloudHub 2 ingress behavior can differ by deployment target. This app accepts
both the friendly public paths and the rewritten internal root path `/`. That
keeps Twilio and Meta working whether the deployment target preserves the path
or rewrites it before reaching the Mule listener.

Text messages are forwarded as safe intake payloads and Salesforce performs the
deeper complaint categorisation, evidence creation, recommendation, and approval
setup. Voice notes, images, and PDFs are mapped as media evidence hints with
media count, media type, media kind, and a media reference. The app does not
claim transcription/extraction until a trusted service supplies it.

If Twilio receives the inbound message but the WhatsApp user sees no reply,
check Twilio's latest outbound-reply status. Error `63038` is a Twilio account
daily-limit/account-restriction failure; the webhook can be healthy while
Twilio blocks delivery.

No secrets belong in this folder. Override these properties at runtime:

- `salesforce.host`
- `salesforce.accessToken`
- `logia.tenant`
- `logia.purpose`
- `meta.webhookVerifyToken`
- `meta.whatsappPhoneNumberId`
- secure `meta.whatsappAccessToken`
- secure `slack.signingSecret`
- secure `slack.botToken`, optional
- `slack.channelId`, optional

For the hackathon, Meta Cloud API is preferred when the app, test recipient,
phone number ID, access token, and webhook are ready. Keep Twilio Sandbox as a
backup path.

Package locally:

```bash
mvn -f mulesoft/logia-twilio-webhook/pom.xml clean package
```

Deploy the packaged app with Anypoint CLI or Anypoint Runtime Manager. Use
Anypoint secure properties for the Salesforce access token.

For CloudHub 2 shared spaces, point WhatsApp providers to the active public
endpoint. The current deployed endpoint is:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

Despite the inherited `twilio` path name, the Mule listener behind this route is
provider-neutral: Twilio form posts return TwiML, and Meta JSON posts return a
JSON acknowledgement. CloudHub 2 currently routes this endpoint reliably with
`pathRewrite: "/"`; the friendly `/meta/whatsapp/inbound` listener remains in
the Mule app for future routing targets, but it is not the active public demo
endpoint.

For Meta, set the WhatsApp webhook callback URL to the active endpoint above and
use this verify token value from Anypoint runtime properties:

```text
logia-meta-verify
```

Meta verification is healthy when a GET with `hub.mode=subscribe`, the matching
`hub.verify_token`, and a `hub.challenge` returns HTTP `200` with the raw
challenge body.

Inbound webhook acknowledgements are not visible inside the WhatsApp chat. To
send a visible customer acknowledgement, configure these CloudHub runtime
properties outside Git:

- `meta.whatsappPhoneNumberId`
- secure `meta.whatsappAccessToken`

When both are valid, Meta inbound messages receive this neutral acknowledgement
after Salesforce intake succeeds:

```text
Thanks. Logia received this. A manager will review it.
```

Current deployed demo URL:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

## Slack Interactivity

Use the same free CloudHub app for Slack. No paid Slack plan, Slack Lists,
ngrok, or tunnel is needed after this Mule app is deployed.

In the Slack app, set **Interactivity & Shortcuts** to this Request URL:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/slack/interactions
```

For the `/logia` slash command, set the command Request URL to:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/slack/commands
```

The endpoints return fast ephemeral Slack acknowledgements. This prevents
Slack timeouts and keeps the live demo free. The Salesforce command center
remains the system of record for approval state, action execution, and outcome
tracking until the CloudHub flow is extended to write signed approval decisions
back to Salesforce.
