# Vega WebView Accessibility

Use this guide when the app renders web content through Vega WebView, such as `@amazon-devices/webview`, a `WebView` component, `webview.html`, hosted HTML, `window.ReactNativeWebView.postMessage`, or web assets inside a Vega package.

Primary source: https://developer.amazon.com/docs/vega/0.22/webview-accessibility-guide.html

## Detection

Check for:
- `@amazon-devices/webview` in `package.json`
- `WebView` usage in `tsx`, `jsx`, or native app entry points
- `webview.html`, hosted `source={{ uri }}`, bundled HTML, or web build output
- `postMessage` from web content to the Vega WebView container
- `manifest.toml` package/component configuration for the Vega app

If native React Native screens wrap the WebView, audit both native and web surfaces.

## Core Requirements

Vega WebView integrates with Vega OS APIs for HTML5 accessibility, but the app must expose correct semantics and focus behavior.

Prioritize:
- Semantic HTML: use meaningful elements such as `main`, `nav`, `footer`, `button`, `a`, headings, lists, forms, and labels.
- ARIA only when native HTML is insufficient: expose role, name, state, and description for custom widgets.
- Logical focus order: remote/D-pad and keyboard focus should follow the visual and task order.
- Visible focus: every actionable item needs a clear focus indicator.
- Focus trapping and restoration: dialogs and menus trap focus while open and restore focus to the trigger when closed.
- Text alternatives: images and icons need useful alt text or labels; decorative content should not be announced.
- Dynamic updates: use `aria-live` for status and content changes that VoiceView should announce.
- Typography and color: meet WCAG contrast and readability expectations.

## Programmatic Announcements

Prefer semantic markup and live regions before direct announcements.

Use direct announcements only when web content cannot expose the update naturally, such as canvas, diagrams, highly custom navigation, or non-DOM-rendered experiences.

For WebView-to-native announcements:
1. Web content sends a typed message through `window.ReactNativeWebView.postMessage`.
2. The Vega WebView container handles `onMessage`.
3. Native code calls `AccessibilityInfo.announceForAccessibility()` with the announcement text.

Do not use direct announcements for routine focus changes or duplicate content that VoiceView already speaks.

## VoiceView

Verify:
- VoiceView can be enabled and disabled from Accessibility Settings.
- Every actionable item is spoken with the right name, role, state, hint, and description.
- New screens speak meaningful context such as title, orientation, description, and focused item.
- Review Mode can reach static text and controls.
- Duplicate announcements are removed.
- The video player does not trigger continuous reading.

## Focus and Remote Navigation

Test with D-pad, Select, Back, and supported keyboard input:
- All actionable elements are reachable.
- There are no dead ends or trap zones.
- Modal close returns focus to the launching control.
- Carousels and menus can be entered and exited predictably.
- Magnifier follows focus.
- Focus is not moved to hidden, offscreen, or collapsed content.

## Media Requirements

For media apps:
- Captions/subtitles can be enabled and disabled.
- Captions are accurate, synchronized, readable, and persist if the app supports persistence.
- Media controls have labels, states, and remote-operable actions.
- Loading, buffering, errors, and offline states communicate through more than color alone.

## Common Fix Patterns

- Replace clickable `div`/`span` with `button` or `a` where possible.
- Add `aria-label` only when the visible text is missing or insufficient.
- Use `aria-describedby` for helper text, error text, or longer context.
- Use `aria-expanded`, `aria-pressed`, `aria-selected`, and `aria-current` for stateful controls.
- Use `aria-live="polite"` for non-urgent updates; reserve assertive announcements for urgent interruptions.
- Avoid repeated labels such as many identical "Play" or "More" controls; include nearby context.
- Do not hide focusable interactive content with `aria-hidden="true"` alone.

## Troubleshooting

If VoiceView says only "button":
- Add or correct the accessible name.
- Confirm the element has the right role and visible/semantic text.

If VoiceView reads duplicate text:
- Remove redundant `aria-label`, duplicated live-region content, or duplicate announcements.

If VoiceView reads a different element than the visual focus:
- Check focus management, hidden content, stale DOM nodes, and custom focus code.

If navigation gets stuck:
- Inspect focus traps, custom key handlers, carousel edge handling, overlays, and hidden focusable elements.
