# Architecture reference

Use this reference when selecting contracts and enforcement points for a
playhead-bounded media assistant.

## Trust boundaries

Treat these as separate trust domains:

```text
media player -> application boundary selector -> agent tool -> model
                                                    |
viewer UI <- deterministic validator <- structured response
```

- **Media player:** authority for the current position and title/session state.
- **Boundary selector:** authority for which timeline records are eligible.
- **Agent tool:** the only model-facing source of media facts for the request.
- **Model:** untrusted natural-language transformer; it may omit, invent, or
  repeat information.
- **Validator:** authority for whether generated text may reach the surface.
- **UI:** invalidates stale answers whenever the underlying boundary changes.

## Minimal contracts

Use integers for time at contract boundaries to avoid floating-point edge
differences. Milliseconds are usually sufficient.

```ts
type MediaMode = 'vod' | 'live';
type ContextAction = 'catch_up' | 'identify_visible';

interface TimelineCue {
  id: string;
  startMs: number;
  endMs?: number;
  text: string;
  visibleEntityIds: readonly string[];
}

interface ContextRequest {
  mediaId: string;
  mode: MediaMode;
  action: ContextAction;
  playheadMs: number;
  timelineRevision: string;
}

interface ContextResponse {
  answer: string;
  boundaryMs: number;
  timelineRevision: string;
  confidence: 'high' | 'medium' | 'fallback';
  sourceCueCount: number;
}
```

Do not trust a client-provided cue list merely because every timestamp is below
the playhead. Prefer selecting from a server-owned or signed timeline when the
feature protects licensed or sensitive content.

## Selection rules

Choose and document one rule per action:

- **Catch-up:** cues with `startMs <= playheadMs`, or the stricter
  `endMs <= playheadMs` when partially viewed cues must not be summarized.
- **Visible identification:** cues whose visibility interval contains the
  playhead, or the latest cue at/before the playhead when the source only has
  point timestamps.
- **Live:** use the viewer's playhead within the available live window, never
  the wall clock or live edge as a substitute.

Sort deterministically, de-duplicate by cue ID, clamp negative positions, and
reject non-finite or implausibly large values.

## Tool construction

Prefer a request-scoped closure over a general timeline-query tool:

```ts
function createWatchedTimelineTool(
  boundaryMs: number,
  cues: readonly TimelineCue[],
) {
  const eligible = cues
    .filter((cue) => cue.startMs <= boundaryMs)
    .sort((left, right) => left.startMs - right.startMs);

  return async () => ({
    boundaryMs,
    cues: eligible.map(({id, startMs, text}) => ({id, startMs, text})),
  });
}
```

The model should not supply a requested timestamp to the tool. Capturing the
normalized boundary in the closure removes that degree of freedom.

## Response validation

Structured output is useful but not sufficient. Validate both the schema and
domain invariants. Maintain a normalized entity catalog with each entity's
first eligible timestamp or visibility intervals. Reject future or off-screen
entities after generation even when the model reports high confidence.

If the product promises all visible entities, compare the normalized set in the
answer with the expected set. Otherwise, document that the result is partial.

Apply surface limits deterministically. Ask the model for fewer words than the
hard UI limit to leave room for tokenization and punctuation differences.

## Cache keys

Include every value that changes eligibility or phrasing:

```text
mediaId + timelineRevision + action + normalizedBoundaryBucket
        + locale + responseStyleVersion
```

Do not serve an answer across titles, episodes, timeline revisions, or a seek
backward unless the cache key proves the same evidence boundary. Preference
memory may change style but must not contribute media facts.

## Logs and metrics

Log enough metadata to prove the boundary was enforced without copying story
content into observability systems:

- request ID, action, media/timeline revision hash;
- normalized boundary and eligible cue count;
- required/observed tool-call counts;
- validator outcome and rejection reason;
- model/provider latency, token counts, and fallback source;
- preference-memory operation outcome without raw identifiers.

Avoid raw subtitles, cue text, generated answers, names, actor/session IDs, and
model prompts unless a separately reviewed diagnostic mode explicitly requires
them.

## Source map

Use these primary references when adapting the pattern to a concrete platform:

- [Amazon Vega `HTMLMediaElement` API](https://www.developer.amazon.com/docs/vega-api/0.24/classes.HTMLMediaElement.amazon-devices_react-native-w3cmedia)
  documents `currentTime`, `duration`, `paused`, and seeking state for Vega SDK
  0.24.
- [WebVTT](https://www.w3.org/TR/webvtt1/) defines timestamped text tracks and
  cue timing; it does not make the cue content trustworthy by itself.
- [Strands custom tools](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/)
  documents typed Python/TypeScript tool definitions. The tool host still owns
  authorization and data filtering.
- [Strands tool security](https://strandsagents.com/docs/user-guide/sdk/tools/)
  warns that tools execute with the permissions of the host process.
- [AgentCore Memory types](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-types.html)
  distinguishes short-term events from extracted long-term records; choose
  explicitly which mode a media product is allowed to use.
- [AgentCore `CreateEvent`](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/short-term-create-event.html)
  documents immutable events, actor/session scope, payload types, and extraction
  configuration.
- [OWASP LLM output handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)
  treats model output as untrusted input to downstream systems, supporting the
  independent validator boundary used here.

When a platform version changes, re-check the linked source and label measured
device behavior separately from normative API behavior.

## Failure behavior

Timeouts, throttling, model refusal, invalid JSON, missing tool use, validation
failure, and preference-memory failure are normal paths. Define their behavior
before integrating the model.

A reviewed fallback should be generated from the same eligible cue set. If no
safe fallback exists, show a neutral unavailable state. Preference-memory
failure should degrade personalization, not the temporal safety boundary.
