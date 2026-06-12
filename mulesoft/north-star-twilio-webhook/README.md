# North Star WhatsApp Webhook Mule App

This Mule app is the public WhatsApp intake door for the hackathon demo. It
supports both Twilio Sandbox and Meta WhatsApp Cloud API webhook shapes.

Twilio flow:

1. Twilio Sandbox posts `application/x-www-form-urlencoded` data to the public
   CloudHub webhook URL: `https://<cloudhub-host>/twilio/whatsapp/inbound`.
2. Mule maps the message into a safe North Star intake payload.
3. Mule calls the Salesforce Apex REST endpoint
   `/services/apexrest/northstar/v1/twilio/whatsapp`.
4. Salesforce creates `Signal`/event, customer alias, evidence, work item,
   recommendation, and pending approval records.
5. Twilio receives a short TwiML acknowledgement.

Meta flow:

1. Meta verifies the webhook with `GET
https://<cloudhub-host>/meta/whatsapp/inbound`.
2. Meta posts WhatsApp Cloud API JSON to `POST
https://<cloudhub-host>/meta/whatsapp/inbound`.
3. Mule maps the Meta message into the same safe North Star intake payload.
4. Mule calls the same Salesforce Apex REST endpoint used by the Twilio path.
5. Meta receives a JSON acknowledgement.

Text messages are mapped into safe complaint summaries. Voice notes, images,
and PDFs are mapped as media evidence hints with media count, media type, media
kind, and a media URL hash. The app does not store raw media URLs or claim
transcription/extraction until a trusted service supplies it.

If Twilio receives the inbound message but the WhatsApp user sees no reply,
check Twilio's latest outbound-reply status. Error `63038` is a Twilio account
daily-limit/account-restriction failure; the webhook can be healthy while
Twilio blocks delivery.

No secrets belong in this folder. Override these properties at runtime:

- `salesforce.host`
- `salesforce.accessToken`
- `northstar.tenant`
- `northstar.purpose`
- `meta.webhookVerifyToken`

For the hackathon, Meta Cloud API is preferred when the app, test recipient,
phone number ID, access token, and webhook are ready. Keep Twilio Sandbox as a
backup path.

Package locally:

```bash
mvn -f mulesoft/north-star-twilio-webhook/pom.xml clean package
```

Deploy the packaged app with Anypoint CLI or Anypoint Runtime Manager. Use
Anypoint secure properties for the Salesforce access token.

For CloudHub 2 shared spaces, point Twilio Sandbox "When a message comes in" to
`https://<cloudhub-host>/twilio/whatsapp/inbound`.

For Meta, set the WhatsApp webhook callback URL to:

```text
https://<cloudhub-host>/meta/whatsapp/inbound
```

Use the same verify token value that is configured as
`meta.webhookVerifyToken` in Anypoint.

Current deployed demo URL:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```
