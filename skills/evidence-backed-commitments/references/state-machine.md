# Lifecycles

## Contract

```text
DISCOVERED → NEEDS_CONFIRMATION (uncertain speaker/intent) → ACTIVE | REJECTED
DISCOVERED → ACTIVE (clear first-person promise)
ACTIVE ⇄ ENGAGED (authorized engagement signal)
ACTIVE|ENGAGED → EVIDENCE_PENDING (new observation or spoken completion claim)
EVIDENCE_PENDING → VERIFIED (policy-matching evidence) | ACTIVE (insufficient)
ACTIVE|EVIDENCE_PENDING → DISPUTED (contradicting physical evidence)
ACTIVE|ENGAGED → MISSED (deadline passed without proof — not a moral judgement)
MISSED → VERIFIED (valid delayed evidence)
ACTIVE → CANCELLED (owner)          DISPUTED → VERIFIED|CANCELLED (authorized resolution)
VERIFIED, CANCELLED, REJECTED are terminal; never regress them.
```

Enumerations:

```text
CommitmentType   = SCHEDULED_SOCIAL_COMMITMENT | INBOUND_ITEM | PARCEL_CUSTODY | PHYSICAL_ACTION | TRIGGERED_TASK
VerificationMode = RING_SPATIAL_CUSTODY | RING_THRESHOLD_OBJECT_SCAN | BEE_CONVERSATION_AUDIT
                 | FIRE_TV_LIVE_POSE_CAMERA | AUTHORIZED_MANUAL_CONFIRMATION
SourceMode       = LIVE_VERIFIED | SIMULATED_VERIFIED | NOT_CONNECTED | BLOCKED
```

Implementation notes: store corrections as new revisions (append-only); use optimistic concurrency
(`revision`) so two workers cannot verify twice; every state change emits an event carrying one
`trace_id` from utterance to UI.

## Parcel custody (separate from "delivered")

```text
CLAIMED_DELIVERED → DEPOSIT_CHECK → DELIVERY_MISMATCH (courier left with it / ambiguous)
                                  → DEPOSIT_VERIFIED_CUSTODY_ACTIVE (deposit + separation observed)
DEPOSIT_VERIFIED_CUSTODY_ACTIVE → REMOVAL_UNDER_REVIEW (item exits zone)
                                → VERIFIED_SAFE_TRANSFER (owner carries it inward)
REMOVAL_UNDER_REVIEW → AUTHORIZED_TRANSFER (owner says it was family) → VERIFIED_SAFE_TRANSFER
                     → INCIDENT_AWAITING_DECISION
```

A deposit does **not** close custody; a persistent, event-driven watchdog keeps the goal alive
across restarts (it is a durable record that wakes on events, not a 9-to-5 video stream).

## Incident / report

```text
AWAITING_HUMAN_DECISION → EVIDENCE_PREPARED (draft packet, nothing sent)
EVIDENCE_PREPARED → REPORT_APPROVED (authenticated owner approves exact manifest hash + destination)
REPORT_APPROVED → REPORT_DISPATCHED (only via an independently verified, authorized endpoint)
REPORT_DISPATCHED → REPORT_ACKNOWLEDGED (only with a real external receipt)
```

Without a real receiving service the flow ends at an exportable packet; a demo receiver must be
labelled `SIMULATED — NOT SENT`.

## Deadline escalation

For each time-bound contract schedule durable jobs at `due-60m` (silent prep), `due-25m` (engagement
audit → actionable alert only if not engaged) and `due` (→ `MISSED` if no proof). Execute each exactly
once; after a restart, run missed jobs once and mark notifications that would now be misleading as
`STALE_SKIPPED`. Recurring promises roll to the next occurrence after proof or after the deadline.
