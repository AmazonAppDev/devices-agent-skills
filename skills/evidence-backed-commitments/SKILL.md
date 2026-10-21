---
name: evidence-backed-commitments
description: Build assistants that turn spoken promises into verifiable "physical state contracts" and never mark a task done without evidence — for Alexa+ MCP servers, Bee wearable data, Ring camera evidence and Fire TV experiences. Use when designing commitment/reminder/todo features, MCP tools that act on the physical world, human-in-the-loop incident or report flows, Ring WHEP/webhook evidence pipelines, Bee SSE ingestion, or Fire TV "do it before you watch" gates.
---

# Evidence-Backed Commitments

This skill helps an agent design and review assistant features where **a reminder being sent is not
the task being done**. It packages the rules, state machines and a zero-dependency commitment compiler
extracted from DONE/IRL (an Alexa+ MCP / Bee / Ring / Fire TV project). Use it when the user is building:

- reminders, todos or "promise tracking" from speech (Bee, Alexa+, transcripts);
- MCP tools whose effects touch the physical world (cameras, deliveries, doors, reports);
- verification flows that must stay honest about uncertainty (camera "not seen", spoken "I did it");
- a Fire TV / living-room experience gated on a real-world action.

## Core rules (apply to every design)

1. **Separate the claim from the proof.** A courier saying "delivered", a model returning
   `completed=true`, a reminder firing, or a user saying "I already called her" are *leads*. Only
   evidence that satisfies the contract's verifier policy may move a contract to `VERIFIED`.
   See [verification-policy.md](references/verification-policy.md).
2. **"Not seen" is uncertain, never "absent".** A camera that cannot see drinks in someone's hands
   yields `NOT_VISIBLE / NEEDS_USER_CHECK`, not "you forgot". Removal of a parcel is
   `REMOVAL_UNDER_REVIEW`, not "theft".
3. **Consequential external actions need an authenticated human approval record** bound to the exact
   payload and destination. A boolean argument such as `human_confirmed=true` sent by a model is not
   approval. See [mcp-tool-design.md](references/mcp-tool-design.md).
4. **Label every source truthfully**: `LIVE_VERIFIED`, `SIMULATED_VERIFIED`, `NOT_CONNECTED`, `BLOCKED`.
   Never let a replay or simulator look live.
5. **Deadlines escalate early, once, and go quiet when stale**: silent prep at T-60, an actionable
   alert at T-25 only if the person is not demonstrably engaged, no "starts in 25 minutes" at T+10.
6. **Owner confirmation is allowed but labelled** `USER_CONFIRMED`, distinct from `SENSOR_VERIFIED`.

## Workflow

1. Model each promise as a contract using the lifecycle in
   [state-machine.md](references/state-machine.md) (copy the enums; keep transitions append-only).
2. Compile utterances deterministically first: `python scripts/compile_commitments.py "I'll call Mom
   tonight" --now 2026-10-20T08:15:00+05:30`. It returns typed candidates (type, counterparty,
   deadline or trigger, verification modality, recurrence, disclosed assumptions) and refuses
   negations, hedges (flags them for confirmation) and prompt-injection text. Use an LLM only to
   *propose* fields, then validate them against the schema and policy.
3. Choose the verification modality per contract and write down what evidence may and may not
   satisfy it before writing code.
4. For device integrations, read [device-realities.md](references/device-realities.md): Ring live
   sessions are 30/60 s, Playground tokens last ~30 min, Bee stream event shapes, Fire TV in-app gates.
5. Check a contract record with `python scripts/check_contract.py contract.json` — it fails if a
   `VERIFIED` contract lacks policy-matching evidence or if a terminal state was regressed.

## What to flag for humans

Anything that would file an official report, contact third parties, identify a person, or lock
another app is out of scope for automation — the agent must surface it for explicit human decision.

## References

| Topic | File |
| --- | --- |
| Lifecycles: contract, parcel custody, incident | [state-machine.md](references/state-machine.md) |
| What counts as proof, per contract type | [verification-policy.md](references/verification-policy.md) |
| MCP tool design for physical-world actions | [mcp-tool-design.md](references/mcp-tool-design.md) |
| Ring / Bee / Fire TV / Alexa+ constraints | [device-realities.md](references/device-realities.md) |
