# Scoring Rubric

Score each task scenario from 1 to 5. A score of 4 or 5 is a pass.

## Overall Score

| Score | Meaning |
|-------|---------|
| 5 | Excellent: measured, platform-aware, source-aligned, actionable, and verified |
| 4 | Good: mostly correct with minor omissions |
| 3 | Partial: useful generic advice but misses one important Vega requirement |
| 2 | Poor: generic performance advice with little platform-specific measurement |
| 1 | Harmful: recommends changes without measurement or applies wrong platform guidance |

## Criteria

### 1. App Surface Detection

- 5: Identifies native RN for Vega, WebView, mixed, or unknown before fixing.
- 3: Mentions app type but does not adapt the plan.
- 1: Applies WebView or RN-only guidance blindly.

### 2. Measurement Discipline

- 5: Establishes baseline KPI, command/tool, target, and repeatable scenario before fixes.
- 3: Mentions measurement but lacks target or repeatability.
- 1: Optimizes without measuring.

### 3. Official Tool Usage

- 5: Uses appropriate Vega tools: KPI Visualizer, Activity Monitor, Recording View, Chrome DevTools, Perfetto, or overdraw.
- 3: Uses some tools but misses the best one.
- 1: Uses only generic profiling advice.

### 4. Fix Quality

- 5: Gives concrete, platform-specific fixes tied to evidence.
- 3: Gives plausible but broad advice.
- 1: Gives unsafe, speculative, or unrelated fixes.

### 5. Verification

- 5: Re-runs the same KPI/scenario and compares before/after values.
- 3: Includes basic testing without KPI comparison.
- 1: No verification.

## Automatic Failure Conditions

Set overall score to 1 if the output:
- Recommends optimizations without any baseline measurement.
- Reports TTFD success without explaining `useReportFullyDrawn()` or real readiness.
- Mixes WebView APIs and native RN APIs incorrectly.
- Ignores UI fluidity targets for jank/D-pad performance.
- Treats debug-build profiling as final publish-readiness evidence.

## Aggregate Metrics

Track:
- Trigger precision.
- Non-trigger specificity.
- Task pass rate.
- Average score.
- Automatic failures.
- Most common missing behavior.
