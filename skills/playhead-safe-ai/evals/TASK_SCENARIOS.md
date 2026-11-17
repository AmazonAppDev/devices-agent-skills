# Task scenarios

These scenarios are a compact evaluation fixture for an agent using
`playhead-safe-ai`. Each scenario names the invariant that a useful answer must
preserve. They are intentionally model-agnostic: a host can run them against a
fresh context and score the result without supplying the intended answer in the
prompt.

| ID | Scenario | Required assertion |
| --- | --- | --- |
| S1 | A recap is requested at `10.000s` with cues at `10.000s` and `10.001s`. | Apply the documented boundary rule; never include the `10.001s` cue by accident. |
| S2 | A viewer seeks backward after a recap card is visible. | Invalidate the old card or recompute it for the new boundary. |
| S3 | A viewer seeks forward after a recap card is visible. | Do not keep an answer derived from the earlier boundary. |
| S4 | The timeline input is reordered and contains duplicate cue IDs. | Normalize deterministically and de-duplicate before tool output. |
| S5 | `Who’s that?` is requested with two visible entities and five future entities. | Return only the visible set promised by the action. |
| S6 | The model names an entity introduced after the boundary. | Reject the response and show a reviewed fallback/unavailable state. |
| S7 | The model returns a correct-looking answer without calling the required tool. | Reject it; prompt compliance is not evidence access. |
| S8 | The model returns invalid JSON, empty text, and an oversized card in three runs. | Reject each result with a typed reason before rendering. |
| S9 | Preference memory contains `shorter` but no media facts. | Use the preference for phrasing only; eligibility is unchanged. |
| S10 | Preference memory is unavailable or times out. | Degrade personalization while preserving the same spoiler boundary. |
| S11 | The stream has no finite duration and the viewer is behind the live edge. | Use “what has aired so far” at the viewer playhead, not the wall clock. |
| S12 | The title or timeline revision changes while a request is in flight. | Discard a response tied to the old title/revision. |

For an implementation-specific run, attach a synthetic timeline with an
unmistakable future-only marker (for example, `FUTURE_ENTITY`) and record the
boundary, tool result, validator decision, and rendered state. Do not use real
programme text or viewer identifiers as evaluation data.
