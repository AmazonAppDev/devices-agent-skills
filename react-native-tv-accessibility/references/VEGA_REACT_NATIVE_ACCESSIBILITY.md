# Vega React Native Accessibility

Use this guide when the app is a native React Native for Vega app, not primarily a WebView-rendered app.

Primary sources:
- React Native for Vega accessibility: https://developer.amazon.com/docs/react-native-vega/0.72/accessibility.html
- React Native accessibility: https://reactnative.dev/docs/accessibility.html
- Vega app manifest: https://developer.amazon.com/docs/vega/0.22/app-manifest.html
- Vega Yarn workspaces: https://developer.amazon.com/docs/vega/0.22/yarn-workspaces.html

## Detection

Check for:
- `manifest.toml` at the Vega package root
- React Native for Vega app entry points and components
- `@amazon-devices/react-native-kepler`
- `build:app`, `vega project`, or Yarn workspace scripts for React Native for Vega apps
- `packages/application`, `packages/*`, or Vega workspace layout
- Native RN surfaces without `WebView` as the main content renderer

If the app also embeds `WebView`, audit the native shell and WebView content separately.

## Core Model

React Native for Vega accessibility generally follows React Native accessibility guidance, with Vega-specific behavior and newer recommendations.

Key points:
- VoiceView follows input focus on TV, so focus behavior directly affects screen reader behavior.
- Touchable or D-pad-navigable elements are accessible by default in many cases, but do not rely on `accessible` alone for focusability.
- In React Native for Vega, prefer `role` over legacy `accessibilityRole`.
- Prefer Vega-supported `aria-*` props where the React Native for Vega docs recommend them.
- Use direct screen reader announcements sparingly; prefer roles, labels, descriptions, and live regions.

## Labels, Roles, Hints, and State

For each actionable component:
- Provide a clear accessible name with visible text, `aria-label`, or React Native label APIs as appropriate.
- Use `role` for purpose, such as button, link, image, text, checkbox, or progressbar.
- Use `accessibilityHint` only when the result of the action is not clear from the label.
- Expose state with `aria-checked`, `aria-disabled`, `aria-expanded`, `aria-selected`, or related props where supported.
- Use range value props such as `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, and `aria-valuetext` for progress or sliders.

Avoid:
- Names that duplicate visible text unnecessarily.
- Multiple controls with identical spoken names.
- Forcing announcements for normal focus movement.
- Grouping child text into a parent `accessible={true}` element when the child text must be independently reachable.

## Vega-Specific Guidance

Use these when applicable:
- `accessibilityOrientationText`: describe screen layout or navigation model the first time a user encounters a screen or container.
- `accessibilityDescribedBy`: reference static text or details that describe the focused component, especially when screen reader focus follows TV input focus.
- `aria-live`: communicate dynamic updates without moving focus.
- `AccessibilityInfo.announceForAccessibility()`: reserve for cases where semantic roles, labels, or live regions cannot communicate the update.

When a screen opens:
- Focus the most useful initial element.
- Provide orientation text for complex layouts.
- Ensure static details related to focused tiles are associated with the tile.

When a dialog closes:
- Return focus to the triggering element or the next logical control.

## Focus and D-pad Navigation

Validate:
- Up, Down, Left, Right, Select, and Back all behave predictably.
- The visually focused item and spoken item match.
- Every actionable item is reachable.
- Focus does not land on hidden or disabled content.
- Lists, grids, and carousels have predictable edge behavior.
- Screen transitions restore or move focus intentionally.

Fix issues by correcting component structure and focus behavior before adding extra announcements.

## Media and TV Patterns

For playback:
- Media controls must have names, roles, states, and remote actions.
- Play/pause, captions, audio tracks, seek, scrub, and settings controls need clear state.
- Captions/subtitles must be discoverable and operable with the remote.
- Loading, buffering, errors, and restricted content states need spoken and visual feedback.

For rows, rails, and tiles:
- Tile labels should include enough context to be unique.
- Use descriptions for metadata that matters to selection, such as title, episode, progress, price, or availability.
- Avoid reading all metadata on every focus if it creates excessive speech.

## Verification

Test with:
- VoiceView enabled.
- Standard TV remote/D-pad.
- Magnifier and text-size settings when available.
- Captions/subtitles enabled and disabled.
- Screen transitions, modal flows, search, playback, settings, and error states.

Report native Vega RN findings with:
- Component/file
- Focus path
- Spoken output
- Expected output
- API or prop to change
- WCAG or platform reference
