# Event Contract

## Purpose

Every source enters the platform through one versioned event envelope. The
contract preserves the original source identity and makes retries, replay,
late arrival, ordering, and contradictory assertions observable before data is
mapped into Data 360 or Salesforce.

The envelope follows CloudEvents 1.0 JSON conventions and adds lowercase HFS
extension attributes.

## Envelope

Required CloudEvents fields:

- `specversion`: currently `1.0`;
- `id`: unique occurrence identifier;
- `source`: stable URI identifying the source boundary;
- `type`: versioned event type;
- `subject`: stable business-record subject;
- `time`: when the source says the event occurred;
- `datacontenttype`: `application/json`;
- `dataschema`: URI of the event schema;
- `data`: the preserved normalized source payload.

Required HFS extensions:

- `hfstenantid`: isolation boundary;
- `hfsschemaversion`: envelope contract version;
- `hfscorrelationid`: end-to-end trace identifier;
- `hfsidempotencykey`: stable source retry key;
- `hfssourcerecordid`: original source record identifier;
- `hfssourcesequence`: source ordering hint;
- `hfsobservedat`: when this platform received the event;
- `hfscontenthash`: SHA-256 of canonical `data`.

`hfscausationid` is optional and links derived events to their immediate cause.
Event types use the repository-owned `io.github.freeapikeys.hfs.*` namespace.
When a source has no native sequence, its MuleSoft System API assigns a
monotonic sequence for that source boundary.

## Deterministic Intake Results

| Result                          | Meaning                                                                          |
| ------------------------------- | -------------------------------------------------------------------------------- |
| `ACCEPTED`                      | Valid, new, ordered event                                                        |
| `DUPLICATE`                     | Same idempotency scope and content hash                                          |
| `REJECTED_SCHEMA`               | Envelope or payload violates JSON Schema                                         |
| `REJECTED_HASH`                 | Payload does not match the declared content hash                                 |
| `REJECTED_IDEMPOTENCY_CONFLICT` | Same idempotency key was reused for different content                            |
| `ACCEPTED_LATE`                 | Valid event arrived outside the configured lateness window                       |
| `ACCEPTED_OUT_OF_ORDER`         | Valid event sequence is behind the source watermark                              |
| `CONFLICT_REVIEW`               | A valid assertion contradicts an existing assertion for the same effective point |

Late and out-of-order events are preserved rather than silently discarded.
Conflicts coexist as claims and are routed for resolution; no history is
overwritten.

The executable fixture validator and MuleSoft reference runtime use the same
stateful classifier. Idempotency is scoped by tenant, source, and idempotency
key, and exact replay compares the canonical `data` hash rather than
transport-level fields such as event occurrence ID or observation time.

Schema/hash failures and accepted events whose source-store retries are
exhausted enter an immutable `QUARANTINED` intake attempt. An authorized replay
submits a complete corrected envelope to `POST /v1/events/replays`, links the
new attempt to the original, and applies a separate replay idempotency key.
Permanent idempotency and state conflicts cannot be replayed.

## Synthetic Case

Fixtures model an industry-neutral organization with people, departments,
resources, partners, agreements, work, evidence, and outcomes. The scenario then
replays a duplicate, sends malformed input, delivers a late event, introduces a
contradictory assertion, and sends an out-of-order event.

The North Star private hospital demo should add hospital operations fixtures
using the same envelope and intake rules. Candidate event types:

- `io.github.freeapikeys.hfs.hospital.patient-complaint-cluster-detected.v1`;
- `io.github.freeapikeys.hfs.hospital.bed-capacity-pressure-detected.v1`;
- `io.github.freeapikeys.hfs.hospital.discharge-room-blocked.v1`;
- `io.github.freeapikeys.hfs.hospital.pharmacy-stock-risk-detected.v1`;
- `io.github.freeapikeys.hfs.hospital.lab-vendor-response-delayed.v1`;
- `io.github.freeapikeys.hfs.hospital.billing-approval-stalled.v1`;
- `io.github.freeapikeys.hfs.hospital.staff-queue-risk-detected.v1`;
- `io.github.freeapikeys.hfs.hospital.clinical-decision-request-refused.v1`;
- `io.github.freeapikeys.hfs.hospital.action-outcome-captured.v1`.

Hospital event payloads must name department, location, typed resource, partner
where relevant, source metric, evidence summary, and approval/action context
where relevant. They must not contain real patient data, medical records,
diagnoses, treatments, phone numbers, emails, or credentials.

Run:

```bash
npm run check:events
npm run check:mulesoft
```

Contract basis:

- [CloudEvents specification](https://github.com/cloudevents/spec)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
