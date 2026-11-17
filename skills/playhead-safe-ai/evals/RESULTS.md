# Evaluation results

This package deliberately separates deterministic repository checks from host
model evaluation. It does not claim that a particular model router will select
the skill perfectly, or that documentation alone proves a production app is
spoiler-safe.

## Reproducible repository check

Run from the repository root:

```bash
node skills/playhead-safe-ai/evals/check.mjs
```

The check covers 26 structural and executable reference invariants:

- required frontmatter and trigger boundary;
- authoritative clock and deterministic post-model validation guidance;
- primary memory source citation;
- request-scoped tool and future-data architecture guidance;
- backward-seek and future-entity test guidance;
- 12 task scenarios and 20 routing prompts;
- README registration;
- all local reference links used by the eval package;
- exact-boundary inclusion and future-cue exclusion;
- deterministic sorting and cue-ID de-duplication;
- rejection of non-finite boundaries;
- missing-tool, stale-boundary, stale-revision, empty, oversized, and
  ineligible-entity response rejection;
- preference isolation and viewer-playhead behavior for live media.

The expected output is:

```text
playhead-safe-ai checks passed: 26
```

## Host-model evaluation protocol

To compare routing or answer quality in a specific host, provide a fresh
context containing only the skill names/descriptions for the trigger test, or
the skill plus its linked references for task scenarios. Score each scenario
against the required assertion in `TASK_SCENARIOS.md`. Record the host, model,
date, prompt set, and failures. Do not report a model score without those
details.

The trigger set contains 10 positive and 10 negative prompts. The task set
contains 12 boundary, adversarial, state-transition, memory, live-media, and
failure scenarios. These fixtures are designed to make a future maintainer's
evaluation reproducible without using private programme data.

## What this contribution can claim

- The skill has a dependency-free structural and executable reference check.
- The guidance names explicit pre-model and post-model enforcement points.
- The evaluation fixtures cover exact boundary edges, stale state, future-only
  entities, missing tool calls, malformed output, memory failure, and live mode.
- The cited platform behavior is tied to primary documentation and marked as
  version-sensitive where appropriate.

It cannot claim that a simulator proves hardware-only behavior, that the
timeline source contains no bad future facts, or that all host models will
follow the routing description identically.
