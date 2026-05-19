# Task Scenarios

Run each scenario twice: once without the skill and once with `react-native-tv-accessibility` available. Score both outputs with [SCORING_RUBRIC.md](SCORING_RUBRIC.md).

## Scenario 1: Mixed App Detection

Prompt:

```text
Review accessibility for a Vega TV app. The repo has `manifest.toml`, `@amazon-devices/webview`, a WebView wrapper for browse and details screens, and native React Native for Vega settings screens. Tell me how you would audit it before making fixes.
```

Expected high-quality behavior:
- Classifies the app as mixed.
- Audits WebView and native RN surfaces separately.
- Checks cross-surface focus restoration and announcements.
- Uses official Vega WebView, React Native for Vega, React Native, WCAG, and WAI-ARIA guidance.
- Produces a prioritized audit workflow.

## Scenario 2: Vega WebView Duplicate VoiceView Output

Prompt:

```text
In a Vega WebView app, VoiceView says the movie title twice on each tile. The HTML has visible title text and `aria-label` with the same title on the tile button. What should we fix and how do we verify it?
```

Expected high-quality behavior:
- Identifies duplicate accessible names/announcements.
- Recommends one source of truth for the accessible name.
- Preserves context needed for unique tile labels.
- Verifies with VoiceView normal navigation and Review Mode.
- Avoids unnecessary direct announcements.

## Scenario 3: Native Vega RN Rail Details

Prompt:

```text
In a native React Native for Vega home screen, VoiceView only announces "button" for each content tile. The selected tile updates a details panel with title, episode, and progress, but that text is not reachable by screen reader focus. Suggest a fix.
```

Expected high-quality behavior:
- Treats this as native Vega RN, not WebView.
- Recommends useful labels and `role`.
- Uses `accessibilityDescribedBy` for related static details when appropriate.
- Mentions `accessibilityOrientationText` for complex TV layout if useful.
- Verifies spoken output and D-pad navigation.

## Scenario 4: Modal Focus Trap

Prompt:

```text
A TV sign-in modal opens from a settings button. With the remote, focus sometimes moves behind the modal, and after closing it, focus jumps to the top nav. Give a fix plan for Vega TV accessibility.
```

Expected high-quality behavior:
- Starts by asking/detecting WebView vs native Vega RN if unspecified.
- Requires focus containment while modal is open.
- Requires focus return to the triggering settings button or next logical control.
- Checks Back/Escape behavior.
- Maps to WCAG focus order, no trap, and focus visible.

## Scenario 5: Captions and Playback Controls

Prompt:

```text
Audit a Vega media playback screen for accessibility. It has play/pause, seek, captions, audio track, and settings controls. What issues should be checked and what evidence should be collected?
```

Expected high-quality behavior:
- Checks captions/subtitles enablement, sync, accuracy, readability, and persistence.
- Checks media control names, roles, states, and remote operability.
- Includes loading, buffering, offline, and error states.
- Includes VoiceView and D-pad evidence.
- Includes magnifier/text-size validation where applicable.

## Scenario 6: Announcement Choice

Prompt:

```text
Our Vega WebView search page updates results after the user types. Should we use `aria-live`, `postMessage` plus `AccessibilityInfo.announceForAccessibility`, or both?
```

Expected high-quality behavior:
- Prefers semantic updates/live regions for routine dynamic web content.
- Reserves WebView-to-native announcements for cases that cannot be expressed semantically.
- Avoids duplicate announcements.
- Suggests polite announcements for result counts/status.
- Verifies VoiceView output and timing.

## Scenario 7: Native RN Prop Modernization

Prompt:

```text
Review this React Native for Vega component. It uses `accessibilityRole="button"` and `accessibilityState={{ expanded: true }}` on a custom expandable row. What should change?
```

Expected high-quality behavior:
- Recognizes React Native for Vega guidance to prefer `role`.
- Recommends supported `aria-*` state props, such as `aria-expanded`, where appropriate.
- Keeps label, hint, and state synchronized with UI.
- Verifies VoiceView spoken role and expanded/collapsed state.
- Avoids generic web-only ARIA advice without RN context.

## Scenario 8: Hidden Focusable Content

Prompt:

```text
In a Vega WebView menu, collapsed menu items are offscreen and have `aria-hidden="true"`, but D-pad focus can still move to them. How should this be fixed?
```

Expected high-quality behavior:
- Explains that hidden focusable content must not remain focusable.
- Recommends removing from DOM, using `hidden`/`display: none`, `inert` where supported, or disabling/removing focusability.
- Keeps `aria-hidden` for non-interactive hidden content only.
- Verifies D-pad cannot reach hidden controls.
- Verifies VoiceView no longer announces hidden menu items.

## Scenario 9: Unknown App Type

Prompt:

```text
Help fix accessibility for a Vega TV app. I am not sure whether it is WebView or React Native for Vega. What should you inspect first?
```

Expected high-quality behavior:
- Does not start with fixes.
- Checks `manifest.toml`, dependencies, app entry points, WebView indicators, RN for Vega indicators, scripts, and rendered UI.
- Explains the different paths for WebView and native RN.
- Recommends auditing mixed apps separately.

## Scenario 10: Contrast and Focus Indicator

Prompt:

```text
Our TV app uses a subtle gray focus ring on dark gray cards. It looks polished but users miss the focused item. Review this accessibility issue.
```

Expected high-quality behavior:
- Identifies focus visibility and non-text contrast risk.
- Recommends a clear high-contrast focus indicator.
- Mentions magnifier and VoiceView validation.
- Maps to WCAG focus visible, non-text contrast, and focus not obscured where applicable.
- Includes remote/D-pad verification.
