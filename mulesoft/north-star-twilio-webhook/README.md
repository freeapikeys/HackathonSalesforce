# North Star Twilio Webhook Mule App

This Mule app is the public WhatsApp intake door for the hackathon demo.

Flow:

1. Twilio Sandbox posts `application/x-www-form-urlencoded` data to the public
   CloudHub webhook URL: `https://<cloudhub-host>/twilio/whatsapp/inbound`.
2. Mule maps the message into a safe North Star intake payload.
3. Mule calls the Salesforce Apex REST endpoint
   `/services/apexrest/northstar/v1/twilio/whatsapp`.
4. Salesforce creates `Signal`/event, customer alias, evidence, work item,
   recommendation, and pending approval records.
5. Twilio receives a short TwiML acknowledgement.

No secrets belong in this folder. Override these properties at runtime:

- `salesforce.host`
- `salesforce.accessToken`
- `northstar.tenant`
- `northstar.purpose`

For the hackathon, use Twilio Sandbox. Meta Cloud API verification is out of
scope.

Package locally:

```bash
mvn -f mulesoft/north-star-twilio-webhook/pom.xml clean package
```

Deploy the packaged app with Anypoint CLI or Anypoint Runtime Manager. Use
Anypoint secure properties for the Salesforce access token.

For CloudHub 2 shared spaces, point Twilio Sandbox "When a message comes in" to
`https://<cloudhub-host>/twilio/whatsapp/inbound`. The app listener accepts a
wildcard POST path so CloudHub endpoint rewriting does not block the intake.

Current deployed demo URL:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```
