---
name: playhead-safe-ai
description: Build or review playhead-bounded AI features for video and audio, including catch-up recaps, on-screen identification, contextual explanations, and spoiler-safe assistants. Use when model-visible facts must be limited to what a viewer has watched or heard. Do not use for ordinary recommendations, content moderation, or whole-title summaries with no playback boundary.
---

# Playhead-Safe AI

Treat the viewer's playback position as an authorization boundary, not a prompt
hint. The outcome is an assistant that can explain the current experience while
being structurally unable to retrieve future timeline facts.

This skill applies to video-on-demand, live streams, sports replays, podcasts,
and other time-based media. It is platform-neutral; use the host application's
authoritative playback clock and existing media APIs.

## Establish the boundary

Before proposing an architecture or changing code, identify:

1. The authoritative playback clock. Prefer the player's emitted position over
   UI state, wall-clock time, or a client-supplied display label.
2. The media mode: finite on-demand content or live/unknown-duration content.
3. The requested action and its evidence window. A recap may use all eligible
   cues; on-screen identification should usually use only the latest eligible
   cue or a short visibility interval.
4. The timeline source and its trust level. Cues must describe only facts known
   by their own timestamp; a timestamped cue containing future knowledge is
   already unsafe.
5. Boundary semantics. Define whether a cue is eligible by `start <= playhead`,
   `end <= playhead`, or an explicit visibility interval. Keep that rule shared
   by the client, backend, tests, and observability.

For live media, phrase the boundary as "what has aired so far" and do not infer
future schedule or outcome data. Seekable live windows still use the viewer's
actual playhead, not the live edge.

## Use a two-sided safety boundary

Apply independent controls before and after generation:

```text
authoritative playhead
  -> normalize and clamp
  -> select eligible cues
  -> action-specific, request-scoped tool
  -> model generation with a small output contract
  -> deterministic response validation
  -> safe answer or reviewed fallback
```

### Before generation

- Filter future cues in deterministic application code.
- Give the model an action-specific read-only tool rather than the complete
  timeline. Construct the tool per request so it cannot query beyond the
  normalized boundary.
- For identification, return the visible entities and descriptions needed for
  that moment, not raw future scene text or the complete cast.
- Do not include future facts in the system prompt, examples, retrieval index,
  conversation history, cache, or personalization memory.
- Put hard limits on cue count, text size, tool calls, turns, output tokens, and
  latency. Reject or truncate input before invoking the model.

### After generation

Validate independently of the model and prompt. At minimum, reject a response
when:

- the required temporal tool was not called;
- the answer is empty, malformed, or over the surface's word budget;
- it names an entity introduced after the boundary;
- an identification answer names an entity outside the eligible visibility
  set;
- the required visible-entity set is incomplete when the UI promises complete
  identification;
- the response cannot be tied to the boundary used for the request.

On rejection, return a reviewed boundary-specific fallback or a neutral
unavailable state. Never display the unsafe model text alongside a warning.

Read [architecture.md](references/architecture.md) when designing the request
contract, tool surface, memory boundary, caching, or failure behavior. Its
source map links the primary platform and security documentation behind the
pattern.

## Keep personalization separate from media facts

Personalization may remember how to answer, not what happens in the title.
Prefer a small enum such as `shorter`, `more_context`, or `simpler`, stored only
after an explicit viewer choice. Scope and expire it appropriately.

Do not place subtitles, cues, generated answers, character history, programme
facts, or future timeline data in preference memory. A memory or cache hit must
not widen the current request's evidence boundary.

## Design for the viewing surface

- Pause or otherwise make the interaction non-disruptive when appropriate.
- Keep answers readable at the expected viewing distance and enforce a word
  budget in code.
- Make the watched/upcoming boundary legible when it helps the viewer understand
  the safety guarantee.
- Close or invalidate an open answer after seek, title change, episode change,
  timeline revision, or any event that moves the boundary.
- Preserve a useful local or reviewed fallback for network, model, timeout,
  throttling, and malformed-response failures.

For TV-specific layout, focus, and remote behavior, use the repository's
`rn-tv-ui-best-practices` skill separately.

## Review an existing implementation

Trace one fact from timeline ingestion to pixels. Report where future data can
enter through the request, tool, prompt, retrieval layer, history, memory,
cache, logs, fallback, or UI state.

Prioritize findings in this order:

1. The model or tool can access facts beyond the boundary.
2. Generated text reaches the UI without deterministic validation.
3. Seek, title, or timeline changes leave stale answers visible.
4. Memory, caches, or logs retain media facts across incompatible boundaries.
5. Failure paths bypass the same safety contract.
6. The guarantee is correct but not observable or testable.

Avoid claiming "spoiler-free" from prompt wording alone. State the exact
boundary, evidence window, enforcement points, and remaining assumptions.

## Verify the behavior

Read [testing.md](references/testing.md) when implementing tests or producing a
release checklist. Tests should prove invariants at boundary edges and failure
paths, not only match preferred wording.

The repository includes a lightweight, dependency-free content/eval check at
`evals/check.mjs`. Run it with `node skills/playhead-safe-ai/evals/check.mjs`
when editing this skill. The prompt matrix is a routing fixture, not a claim
that every host's model selector behaves identically.

Before calling the feature ready, verify at least:

- a cue exactly on the selected boundary;
- a cue just after it;
- a seek backward after an answer is displayed;
- a seek forward with a new eligible set;
- identification with multiple visible entities;
- malicious or malformed model output containing a future entity;
- missing required tool use;
- timeout, throttling, network failure, and invalid JSON;
- personalization recall without media facts in memory;
- live or unknown-duration behavior when supported.

## Output expectations

When designing or reviewing a feature, provide:

- the authoritative clock and explicit eligibility rule;
- a compact data-flow or threat-boundary diagram;
- the request/tool/response contracts;
- pre-generation and post-generation controls;
- cache, memory, logging, and failure-path decisions;
- tests for the relevant boundary and adversarial cases;
- outstanding checks that require the target device or production media source.

Do not claim that a simulator proves hardware-only behavior, or that deterministic
filtering proves the timeline source itself contains no future knowledge.
