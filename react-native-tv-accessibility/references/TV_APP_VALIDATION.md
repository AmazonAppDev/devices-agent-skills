# TV App Accessibility Validation

Use this guide after fixing issues in Vega WebView, native Vega RN, or mixed TV apps.

Primary sources:
- Vega WebView accessibility test cases: https://developer.amazon.com/docs/vega/0.22/webview-accessibility-guide.html
- React Native for Vega accessibility: https://developer.amazon.com/docs/react-native-vega/0.72/accessibility.html
- WCAG 2.2: https://w3.org/TR/2024/REC-WCAG22-20241212

## Validation Setup

Before testing:
- Identify app type: WebView, native Vega RN, or mixed.
- Identify critical flows: launch, navigation, search, details, playback, captions, settings, sign-in, errors, dialogs, and exit.
- Enable VoiceView where available.
- Prepare a TV remote/D-pad and keyboard if supported.
- Enable magnifier and larger text settings if available.
- Capture expected spoken output for key controls and screens.

## VoiceView

Verify:
- VoiceView can be enabled and disabled.
- Focused controls are spoken with name, role, state, hint, and useful context.
- New screens announce enough orientation for the user to understand where they are.
- Static text needed to understand a control is reachable or associated with the control.
- Dynamic updates are announced through live regions or appropriate app APIs.
- Duplicate announcements are removed.
- Review Mode can reach important text and controls.

## Remote and Keyboard Navigation

Verify with D-pad, Select, Back, and supported keyboard input:
- All actionable items are reachable.
- Focus order matches visual and task order.
- Focus is always visible.
- Focus never lands on hidden, disabled, or offscreen content.
- There are no trap zones.
- Dialogs trap focus while open and return focus when closed.
- Carousels, rows, grids, and menus handle edges predictably.
- Back exits overlays or screens without losing focus context.

## Magnifier and Text Size

Verify:
- Magnifier follows the focused item.
- Text can increase without clipping critical content.
- Controls remain visible and operable after zoom or text-size changes.
- Layout remains readable and scrollable.
- User settings persist if the app supports persistence.

## Captions and Media

Verify:
- Captions/subtitles can be enabled and disabled with the remote.
- Caption settings persist when required.
- Captions are accurate, synchronized, and readable.
- Media controls expose clear names and states.
- Loading, buffering, restrictions, offline errors, and playback failures are announced or visibly communicated.

## Regression Checks

After each fix:
- Re-test the exact failed path.
- Re-test neighboring controls and screens.
- Confirm no duplicate announcements were introduced.
- Confirm visual focus still matches spoken focus.
- Confirm the change works with VoiceView off and on.
- Map the result to the finding's WCAG/platform reference.

## Evidence to Collect

For each validated fix, record:
- Device/emulator and app build.
- App surface tested: WebView, native Vega RN, or mixed.
- Assistive technology setting, such as VoiceView on/off.
- Remote/keyboard path.
- Actual spoken output before and after.
- Screenshot or short screen recording if useful.
- Remaining risk or untested condition.
