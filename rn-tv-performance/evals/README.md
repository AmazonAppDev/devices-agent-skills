# RN TV Performance Evals

Use these evals to measure whether `rn-tv-performance` improves performance investigations compared with a baseline run without the skill.

## Files

| File | Purpose |
|------|---------|
| [TRIGGER_PROMPTS.md](TRIGGER_PROMPTS.md) | Trigger and non-trigger prompts for description quality |
| [TASK_SCENARIOS.md](TASK_SCENARIOS.md) | Realistic performance diagnosis and fix scenarios |
| [SCORING_RUBRIC.md](SCORING_RUBRIC.md) | Quantitative and qualitative scoring criteria |
| [RUNBOOK.md](RUNBOOK.md) | Step-by-step instructions for running and comparing evals |

## Success Targets

- Trigger precision: at least 9/10 trigger prompts should use the skill.
- Non-trigger specificity: at least 8/10 non-trigger prompts should avoid the skill.
- Task pass rate: at least 80% of task scenarios score 4 or 5.
- Safety: zero outputs should recommend optimizations without measurement or mix WebView and native RN guidance incorrectly.

## Required Behaviors

High-quality outputs should:
- Detect app surface first: generic React Native TV, React Native for Vega, Vega WebView, mixed, or unknown.
- Choose a KPI and establish a baseline before recommending fixes.
- Use official Vega tools and targets: KPI Visualizer, Activity Monitor, Recording View, Chrome DevTools, Perfetto, overdraw, and report fully drawn APIs.
- Apply platform-specific fixes for native RN or WebView.
- Re-measure the same scenario after changes.
