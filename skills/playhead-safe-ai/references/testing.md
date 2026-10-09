# Testing reference

Test invariants and evidence flow rather than exact generated prose.

## Boundary table

For cues starting at `0`, `10_000`, and `20_000` ms, cover at least:

| Playhead | Expected eligible cue starts |
|---:|---|
| `0` | `0` |
| `9_999` | `0` |
| `10_000` | `0, 10_000` |
| `19_999` | `0, 10_000` |
| `20_000` | `0, 10_000, 20_000` |

Add cases for negative, non-finite, very large, and out-of-duration positions.
If the implementation uses `endMs <= playheadMs`, create the equivalent table
for end boundaries and partially viewed cues.

## Property-oriented invariants

Useful invariants include:

- Moving the playhead backward cannot increase the eligible cue set.
- Adding a future cue cannot change the tool result at the current boundary.
- Reordering input cues cannot change the normalized tool result.
- A title or timeline revision change invalidates an existing response.
- A failed preference lookup cannot change which cues are eligible.
- The fallback uses no cue outside the model request's eligible set.

## Adversarial model cases

Stub the generator to return:

- a future entity name;
- an off-screen entity for identification;
- only one name when multiple visible entities are required;
- a correct answer without calling the required tool;
- empty text, invalid JSON, extra fields, or an oversized answer;
- a plausible hallucination not present in any eligible cue;
- an answer carrying the wrong boundary or timeline revision.

Each case should be rejected before rendering and should produce a typed
rejection reason suitable for metrics.

## State-transition cases

Exercise the UI and API across:

```text
play -> pause -> request -> answer -> resume
answer -> seek backward -> answer invalidated
answer -> seek forward -> new request/new boundary
answer -> title or episode change -> answer invalidated
default style -> explicit feedback -> recalled style
network failure -> reviewed fallback -> playback remains usable
```

For a TV interface, verify D-pad focus, Back behavior, media keys, focus return,
text legibility, and stale-card dismissal on the target simulator and hardware
where available.

## Integration evidence

An end-to-end test should record metadata proving:

- the player boundary sent by the client;
- the normalized boundary used by the backend;
- the eligible cue count;
- the action-specific tool called exactly as designed;
- the validator outcome;
- the boundary echoed in the rendered response.

Do not use production story text or viewer identifiers as evidence. Synthetic
timelines with unmistakable future-only markers make leaks easier to detect.

## Release checklist

- Unit tests cover exact edge timestamps and malformed positions.
- Contract tests keep client and backend boundary semantics aligned.
- Tool tests prove future data is absent, not merely ignored by the prompt.
- Validator tests cover future, off-screen, incomplete, missing-tool, and size
  failures.
- UI tests invalidate cards after seek and title/timeline changes.
- Failure tests cover timeout, throttling, provider errors, and invalid output.
- Memory tests prove stored events contain preferences only.
- Logs are inspected for accidental story text and raw viewer/session IDs.
- Live-mode behavior is tested separately from finite VOD when supported.
- Hardware-only claims remain explicitly unverified until checked on hardware.

The companion repository fixtures are:

- [task scenarios](../evals/TASK_SCENARIOS.md) for boundary and failure cases;
- [trigger prompts](../evals/TRIGGER_PROMPTS.md) for routing precision;
- [evaluation results](../evals/RESULTS.md) for the exact checks this package
  can claim without running a particular host model.
