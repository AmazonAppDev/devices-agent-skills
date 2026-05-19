# Accessibility Checklist

Use this checklist during React Native TV and Vega TV accessibility audits.

## App Type

- [ ] Confirmed app surface: Vega WebView, native Vega RN, or mixed.
- [ ] Checked `manifest.toml`.
- [ ] Checked `package.json` dependencies and build scripts.
- [ ] Checked app entry points and rendered screens.
- [ ] Selected the correct reference path before fixing.

## WebView Surface

- [ ] Uses semantic HTML for structure and controls.
- [ ] Custom controls expose role, name, state, and description.
- [ ] Images/icons have meaningful alt text or are correctly hidden.
- [ ] Focus order is logical with remote/D-pad and keyboard.
- [ ] Focus indicator is visible and high contrast.
- [ ] Dialogs trap focus and restore focus.
- [ ] Dynamic content uses `aria-live` or a justified WebView-to-native announcement.
- [ ] Hidden content is not focusable.

## Native Vega RN Surface

- [ ] Focused item and spoken item match.
- [ ] Controls have useful accessible names.
- [ ] Components use `role` and supported `aria-*` props where recommended by React Native for Vega.
- [ ] Hints are present only when labels do not explain the result.
- [ ] State is exposed for toggles, selected items, expanded panels, disabled controls, and progress.
- [ ] `accessibilityOrientationText` is used for complex TV layouts when helpful.
- [ ] `accessibilityDescribedBy` connects focused tiles or controls to important static details.
- [ ] Direct `AccessibilityInfo.announceForAccessibility()` calls are justified and non-duplicative.

## TV Navigation

- [ ] D-pad reaches all actionable items.
- [ ] Select activates focused controls.
- [ ] Back exits overlays/screens predictably.
- [ ] No dead ends or trap zones.
- [ ] Carousels, rows, grids, and menus handle edge navigation.
- [ ] Screen changes intentionally move or restore focus.

## VoiceView

- [ ] VoiceView can be enabled and disabled.
- [ ] Primary flows work with VoiceView enabled.
- [ ] Spoken output includes name, role, state, hint, and context where needed.
- [ ] New screens provide useful orientation.
- [ ] Review Mode reaches important non-actionable text.
- [ ] Duplicate or stale announcements are removed.

## Visual Accessibility

- [ ] Text contrast meets WCAG AA.
- [ ] Focus indicator contrast is sufficient.
- [ ] Status is not communicated by color alone.
- [ ] Text size and magnifier do not break layout.
- [ ] Motion is reduced or disabled when requested.

## Media

- [ ] Captions/subtitles can be enabled and disabled.
- [ ] Captions are accurate, synchronized, readable, and persistent when required.
- [ ] Media controls have labels and states.
- [ ] Loading, buffering, and error states are communicated visibly and accessibly.

## Reporting

- [ ] Each finding includes severity.
- [ ] Each finding identifies WebView, native Vega RN, or mixed surface.
- [ ] Each finding includes file/component/screen.
- [ ] Each finding includes user impact.
- [ ] Each finding cites Vega, React Native, WCAG, or WAI-ARIA guidance.
- [ ] Each fix includes verification steps.
