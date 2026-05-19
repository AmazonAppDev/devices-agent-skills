# Eval Runbook

Use this runbook to compare baseline agent behavior with behavior after installing or enabling `rn-tv-performance`.

## Preparation

1. Use the same model and environment for baseline and skill-enabled runs.
2. Use the same prompt text in both runs.
3. Record whether the skill was available, explicitly invoked, or automatically selected.
4. Capture response text, timing, and token usage if the runner exposes those metrics.

## Trigger Eval

1. Run each prompt in [TRIGGER_PROMPTS.md](TRIGGER_PROMPTS.md).
2. Mark expected trigger prompts as pass when the agent uses or clearly follows the skill.
3. Mark expected non-trigger prompts as pass when the agent avoids the skill and uses a more relevant workflow.
4. Calculate:
   - Trigger precision: trigger passes / 10
   - Non-trigger specificity: non-trigger passes / 10

## Task Eval

1. Run each prompt in [TASK_SCENARIOS.md](TASK_SCENARIOS.md) without the skill.
2. Run the same prompt with the skill available.
3. Score both outputs with [SCORING_RUBRIC.md](SCORING_RUBRIC.md).
4. Mark scenarios scoring 4 or 5 as pass.
5. Compare:
   - Overall score delta
   - Pass/fail delta
   - Automatic failures
   - Missing guidance patterns

## Review Template

Use this template for each scenario:

```markdown
Prompt ID:
Skill available: yes/no
Skill selected: yes/no/unknown
Overall score:
App surface detection:
Measurement discipline:
Official tool usage:
Fix quality:
Verification:
Automatic failure: yes/no
Key strengths:
Key gaps:
Recommended skill change:
```

## Iteration Rules

Update the skill when:
- Two or more scenarios miss the same required behavior.
- Any scenario recommends optimization before measurement.
- Any scenario mixes WebView and native React Native TV guidance incorrectly.
- Trigger precision is below 9/10.
- Non-trigger specificity is below 8/10.
- Task pass rate is below 80%.

Update the description when:
- Trigger prompts are missed despite good skill content.
- Non-trigger prompts activate because the description is too broad.

Update references or checklist when:
- The agent uses the skill but still misses official Vega KPI targets, iteration count, release-build guidance, or validation steps.
