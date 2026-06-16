# Logia Demo Operator Guide

This guide is for the hackathon team on demo day. It explains what to show,
what each command means, and what is live versus mocked.

## One-Sentence Pitch

Logia turns messy business signals into evidence, a multi-agent action plan,
manager approval, safe execution, and measurable outcomes across hospital,
airport, hotel, and banking profiles.

## What Is Live

- Meta WhatsApp Cloud API receives customer-facing messages through MuleSoft.
- MuleSoft maps inbound WhatsApp messages into safe Logia intake.
- Salesforce and Agentforce are the system of record for evidence,
  recommendations, approvals, actions, and outcomes.
- Slack is the internal staff and manager cockpit.
- Slack messages, approval buttons, and slash-command replies are available when
  the Slack app points to the verified CloudHub Request URL.
- `/logia` slash commands are the reliable live Slack demo path.
- The MuleSoft reference runtime supports manager/staff intake through
  `@Logia` mentions, DMs, and the `Send to Logia` message shortcut. Do not demo
  those live until the CloudHub Events route is re-enabled and smoke-tested.
- Slack Lists can mirror safe task fields when the paid workspace, bot scopes,
  list ID, and list column IDs are configured.
- Supplier email has a Gmail API adapter in the MuleSoft reference runtime. It
  sends live only after manager approval and only when Gmail OAuth credentials
  are configured outside Git.

## What Is Mocked Or Protected

- Vendor or supplier email is protected. If Gmail credentials are missing or
  Gmail fails, Logia keeps the supplier email in a protected queue and says so.
  Do not claim live supplier email unless the Gmail send proof is visible.
- Slack Lists are a mirror, not the source of truth. Salesforce remains the
  official task, approval, and audit surface.
- WhatsApp customer replies are short receipt acknowledgements today. The deep
  reasoning happens in Salesforce, Agentforce, and the command center.
- Clinical, legal, and final financial decisions are never automated. Logia can
  recommend and route, but protected actions need approval.

## Slack Commands

Use these inside Slack as real slash commands, not as normal chat messages.

```text
/logia queue
/logia status <case-id-or-approval-id>
/logia demo hospital
/logia demo airport
/logia demo hotel
/logia demo bank
/logia order <item> qty <amount> due <days> supplier <email>
```

### `/logia queue`

Shows a safe internal operations queue summary. It should be used by managers
to ask: what is active, what needs approval, and what is being tracked?

It does not expose raw customer messages or private phone numbers.

### `/logia status <case-id-or-approval-id>`

Checks a specific case or approval. Use this after a Slack alert or button click
to show that Slack is not the database; it is asking Salesforce for safe status.

### `/logia demo hospital|airport|hotel|bank`

Shows how the same universal Logia operating model maps to different business
profiles. This is the fast way to prove that Logia is not only a hospital tool.

These commands are intentionally visible in-channel so judges can see the
profile mapping.

### `/logia order <item> qty <amount> due <days> supplier <email>`

Creates a manager-facing stock-order draft. Use it when the manager already
knows the needed item, quantity, deadline, and supplier contact.

Example:

```text
/logia order gloves qty 500 due 3 days supplier supplier@example.com
```

Expected result:

- Logia captures the request as an inventory and supply signal.
- Logia drafts a supplier email.
- Logia marks the action as protected.
- Slack shows `Approve`, `Reject`, and `Modify`.
- No supplier email or order is sent before approval.
- If Gmail API credentials exist, approval sends the supplier email.
- If Gmail API credentials are missing, approval records a protected queued
  fallback instead of pretending the email was sent.
- Salesforce remains the source of truth for the final approval and audit
  record.

### Plain-English Slack Intake

Use `/logia` when you want reliable live demo control. For a more natural
business UX, the reference runtime also supports:

```text
@Logia order 500 gloves by Friday from supplier@example.com
```

or DM Logia:

```text
Need 500 gloves in 3 days
```

If item, quantity, due date, or supplier email is missing, Logia asks for the
missing details through the order form/modal path. It should not guess supplier
email, quantity, or deadline. This path must be re-enabled in live CloudHub
before using it on demo day.

Slack message shortcut:

```text
Send to Logia
```

Use it on an existing Slack message such as "pharmacy says gloves are low." It
prefills the order form with the selected message so the manager can complete
the protected action safely.

## Demo Roles

Use these simple roles in the demo:

- Owner: sees summary and outcomes.
- Operations Manager: approves protected actions.
- Worker A: service/customer/front-desk work.
- Worker B: inventory, facilities, and resource work.
- Finance Reviewer: billing, refund, payment, and claim review.
- Supplier: external recipient for approved supplier emails.
- Customer Alias: external complainant with no raw personal data shown.

## Slack Lists Task Mirror

Salesforce remains the task source of truth. Slack Lists are a paid-plan mirror
for safe fields only:

- case;
- profile;
- module;
- priority;
- status;
- owner role;
- due time;
- approval ID;
- action ID;
- evidence count;
- outcome.

If Slack Lists fail because of plan, scope, or column setup, the demo still
works through Slack messages and Salesforce.

## If `/logia queue` Does Not Reply

1. Make sure you typed it as a Slack slash command. If the literal text
   `/logia queue` appears as a normal channel message, Slack did not invoke the
   command.
2. Open Slack app settings and check **Slash Commands**.
3. Confirm the `/logia` command exists.
4. Confirm the Request URL is:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

5. Reinstall the Slack app after changing scopes, slash commands, or
   interactivity.
6. Invite the bot to the channel:

```text
/invite @Logia
```

If Slack still does not reply, test the CloudHub URL from a terminal with a
form post. A successful response proves MuleSoft is alive and the issue is Slack
app configuration.

## Realistic WhatsApp Intake

A customer will not usually say a perfect structured complaint. They may say:

```text
I waited one hour and no one told me what is happening.
```

Logia should treat this as a `Signal`, create `Evidence`, and ask a short
follow-up if the service area is missing:

```text
Which department or counter are you waiting at?
```

If the message has enough context, Logia should map it into:

- `Customer`: patient, guest, passenger, or client alias;
- `Location`: reception, gate, branch, room, or service desk;
- `Resource`: queue, room, stock item, gate, belt, account, or case;
- `Risk`: service delay, capacity pressure, stock risk, partner delay, billing
  exposure, or compliance risk;
- `Recommendation`: one evidence-backed plan;
- `Approval`: manager decision before protected action;
- `Action`: internal alert, task, restock request, partner follow-up, billing
  review, or customer update;
- `Outcome`: wait reduced, stockout avoided, task acknowledged, dispute routed,
  or customer updated.

## Demo Day Flow

### 1. Start With The Universal Story

Say: Logia is not a chatbot. It is an operations system that expands one messy
issue into the affected business functions, asks for missing evidence, blocks
unsafe actions, and tracks outcomes.

### 2. Show Agentforce Chat

Use a realistic vague prompt:

```text
I waited one hour and nobody told me what is happening.
```

Expected behavior: Logia should ask one short follow-up or explain that it will
map the issue into evidence, capacity, communication, approval, and outcome.

### 3. Show WhatsApp Intake

Send one customer-style WhatsApp complaint:

```text
I waited one hour at outpatient reception and the pharmacy says the item is not
available.
```

Explain that WhatsApp is the external front door. It creates the signal. The
deep operational work is visible in Salesforce and Slack.

### 4. Show Salesforce Command Center

Open the command center and show:

- original signal and safe customer alias;
- evidence timeline;
- affected primitives;
- ten-agent handoff trace;
- recommendation;
- approval requirement;
- proposed actions;
- outcome metrics.

### 5. Show Slack Internal Cockpit

Use:

```text
/logia queue
```

Then show the internal alert card. Explain that Slack is where managers and
staff see the work, discuss it, and approve or reject actions.

For a manager-created stock order, run:

```text
/logia order gloves qty 500 due 3 days supplier supplier@example.com
```

Explain: the manager can express the operational need in plain language. Logia
turns it into a protected supplier email draft and approval card, but it does
not send anything before approval.

### 6. Show Approval

Click `Approve` on the Slack card if live interactivity is working. If not, use
the Salesforce command-center approval fallback and say that Salesforce is the
official approval surface.

Protected actions must not execute before approval.

### 7. Show Execution And Outcome

After approval, show the action results:

- Slack internal alert sent;
- WhatsApp receipt or approved customer acknowledgement;
- vendor email sent through Gmail if configured, otherwise protected queued
  fallback;
- service task created or queued;
- outcome metric recorded.

## Four-Business Presentation

Use hospital as the main live story because it has the richest demo data. Then
use the profile commands to show the same system in other sectors:

```text
/logia demo airport
/logia demo hotel
/logia demo bank
```

Explain the mappings:

| Hospital                 | Airport                | Hotel                | Banking                    |
| ------------------------ | ---------------------- | -------------------- | -------------------------- |
| patient complaint        | passenger complaint    | guest complaint      | client complaint           |
| room readiness           | gate readiness         | room readiness       | case readiness             |
| pharmacy stock           | equipment stock        | linen or food stock  | card/document availability |
| lab or insurer delay     | airline/vendor delay   | laundry/vendor delay | KYC or processor delay     |
| billing duplicate charge | fee or baggage dispute | guest overcharge     | payment dispute            |

## Problems Logia Solves

- Customer complaint and trust.
- Queue, capacity, and availability pressure.
- Inventory and stock risk.
- Staff task coordination.
- Partner or vendor delay.
- Billing, refund, claim, or payment review.
- Risk, compliance, and approval routing.
- Internal and external communication.
- Outcome tracking and learning.

## Inventory And Auto-Order Demo

Use this phrase:

```text
The pharmacy counter says the item is unavailable and the queue is not moving.
```

Expected business flow:

1. Logia detects stock risk and queue pressure.
2. Resource and Capacity estimates stock cover and service pressure.
3. Partner and Vendor checks supplier or transfer options.
4. Financial Impact estimates cost or service risk.
5. Risk and Approval blocks supplier order/email until manager approval.
6. Slack posts an approval card.
7. Slack List can mirror the task as `Pending Approval`.
8. Manager approves.
9. MuleSoft sends the supplier email through Gmail if configured, or keeps it
   in a protected queue if not.
10. Logia records `stockout avoided`, `supplier request sent or queued`, and
    `manager approved`.

Manager-initiated stock request:

```text
/logia order surgical gloves qty 500 due 3 days supplier supplier@example.com
```

This is different from a customer complaint. It starts from an internal manager,
not WhatsApp. The same rules still apply: supplier email is protected, approval
is required, and outcome is recorded.

## Exact Demo Script

1. In Agentforce Studio, type:

```text
I waited one hour and nobody told me what is happening.
```

2. In WhatsApp, send:

```text
I waited one hour at outpatient reception and the pharmacy says the item is not
available.
```

3. In Slack, run:

```text
/logia queue
```

4. In Slack, run:

```text
/logia demo airport
/logia demo hotel
/logia demo bank
```

5. In Salesforce, open the command center and show the evidence, recommendation,
   approval, actions, and outcomes.

6. Approve the protected action in Slack or Salesforce.

7. Show that Logia recorded the outcome instead of only sending a message.

## What To Say If Something Fails

- If WhatsApp receives but does not generate a deep answer: "WhatsApp is the
  intake channel. The governed reasoning and approval trace are shown in
  Salesforce and Slack."
- If Slack buttons fail: "Slack interactivity is the manager cockpit, and
  Salesforce remains the fallback approval surface."
- If Slack Lists fail: "Lists are a paid Slack mirror. Salesforce remains the
  source of truth."
- If vendor email is asked about: "Supplier email is protected. Gmail can send
  it after approval when credentials are configured; otherwise Logia records a
  protected queued fallback."
