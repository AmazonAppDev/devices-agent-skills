# Vega TV Accessibility Evals

Use these evals to measure whether `vega-tv-accessibility` improves agent behavior compared with a baseline run without the skill.

These evals follow the skill-creator loop:
1. Run each prompt without the skill.
2. Run the same prompt with the skill available.
3. Score both outputs with [SCORING_RUBRIC.md](SCORING_RUBRIC.md).
4. Compare pass rate, correctness, harmful guidance, time, and token usage.
5. Update the skill when failures show unclear instructions or missing guidance.

## Files

| File | Purpose |
|------|---------|
| [TRIGGER_PROMPTS.md](TRIGGER_PROMPTS.md) | 20 trigger/non-trigger prompts for description optimization |
| [TASK_SCENARIOS.md](TASK_SCENARIOS.md) | Realistic accessibility audit and fix prompts |
| [SCORING_RUBRIC.md](SCORING_RUBRIC.md) | Quantitative and qualitative scoring criteria |
| [RUNBOOK.md](RUNBOOK.md) | Step-by-step instructions for running and comparing evals |

## Success Targets

- Trigger precision: at least 9/10 trigger prompts should use the skill.
- Trigger specificity: at least 8/10 non-trigger prompts should avoid the skill.
- Task pass rate: at least 80% of task scenarios score 4 or 5 overall.
- Safety: zero outputs should apply WebView-only guidance to native Vega RN without checking app type, or native-only guidance to WebView content.
- Source quality: outputs should cite or reflect official Vega, React Native, WCAG, or WAI-ARIA guidance.

## Required Behaviors

An output should:
- Detect app type first: WebView, native Vega RN, mixed, or unknown.
- Use the correct reference path for the detected surface.
- Separate WebView guidance from native Vega RN guidance.
- Prioritize VoiceView, D-pad/remote navigation, focus, captions, magnifier, labels, roles, state, contrast, and validation.
- Include concrete fix steps and verification steps.

## Failure Signals

Treat these as high-priority failures:
- Skips app-type detection.
- Recommends ARIA-only fixes for native RN components without checking supported props.
- Recommends legacy React Native props when React Native for Vega guidance says to prefer newer `role` or `aria-*` props.
- Ignores VoiceView, D-pad, Back, Select, or magnifier validation.
- Gives generic web accessibility advice with no TV or Vega-specific behavior.
