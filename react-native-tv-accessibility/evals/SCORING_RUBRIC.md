# Scoring Rubric

Score each task scenario from 1 to 5. A score of 4 or 5 is a pass.

## Overall Score

| Score | Meaning |
|-------|---------|
| 5 | Excellent: correct, source-aligned, app-type-aware, actionable, and includes validation |
| 4 | Good: mostly correct with minor omissions |
| 3 | Partial: useful generic advice but misses one important Vega/TV requirement |
| 2 | Poor: misses app type or gives mostly generic/mobile/web advice |
| 1 | Harmful: likely to cause incorrect accessibility behavior or applies the wrong platform guidance |

## Criteria

### 1. App Type Detection

Score 1-5:
- 5: Explicitly detects WebView, native Vega RN, mixed, or unknown before fixing.
- 3: Mentions app type but does not use it to guide recommendations.
- 1: Applies one platform's guidance without checking.

### 2. Correct Platform Guidance

Score 1-5:
- 5: Uses the right path for Vega WebView, native React Native for Vega, or both.
- 3: Gives mostly correct guidance but mixes APIs or terms.
- 1: Recommends WebView-only ARIA for native RN or RN-only props for WebView.

### 3. Official Source Alignment

Score 1-5:
- 5: Reflects official Vega WebView, React Native for Vega, React Native, WCAG 2.2, and WAI-ARIA guidance where relevant.
- 3: Uses general accessibility knowledge but lacks platform specificity.
- 1: Conflicts with official guidance.

### 4. TV Interaction Coverage

Score 1-5:
- 5: Covers VoiceView, D-pad/remote, Select, Back, focus visibility, focus order, and no trap zones.
- 3: Covers some focus or screen reader behavior but misses TV remote specifics.
- 1: Treats the app like a mouse/touch web app only.

### 5. Fix Quality

Score 1-5:
- 5: Provides concrete, implementable fixes with clear priorities.
- 3: Gives plausible but high-level recommendations.
- 1: Gives vague or unsafe fixes.

### 6. Validation Quality

Score 1-5:
- 5: Includes verification with VoiceView, remote/D-pad, magnifier/text size, captions/media where relevant, and regression checks.
- 3: Includes only basic manual testing.
- 1: Does not include verification.

## Automatic Failure Conditions

Set overall score to 1 if the output:
- Skips app-type detection and applies the wrong platform guidance.
- Suggests hiding focusable interactive content with `aria-hidden="true"` alone.
- Recommends direct `announceForAccessibility()` for routine updates without considering semantic roles, labels, or live regions.
- Ignores VoiceView and D-pad/remote behavior for a TV accessibility task.
- Claims WCAG conformance without validation or scope.

## Quantitative Metrics

Record these for each run:
- Prompt ID.
- Skill available: yes/no.
- Overall score.
- Criteria scores.
- Pass/fail.
- Time to first answer if available.
- Total runtime if available.
- Token usage if available.
- Notes on missing or harmful guidance.

## Aggregate Review

After running all scenarios, calculate:
- Trigger precision and non-trigger specificity.
- Task pass rate.
- Average overall score.
- Number of automatic failures.
- Most common missing behavior.
- Whether the skill needs description changes, content changes, or new examples.
