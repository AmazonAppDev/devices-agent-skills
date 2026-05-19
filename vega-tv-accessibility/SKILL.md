---
name: vega-tv-accessibility
description: Audit and fix accessibility for React Native TV and Vega TV applications, including Vega WebView apps and native React Native for Vega apps. Use when reviewing TV app accessibility, VoiceView, screen reader output, D-pad or remote navigation, focus management, captions, magnifier behavior, React Native accessibility props, Vega WebView accessibility, WCAG, WAI-ARIA, or accessible media app flows.
---

# React Native and Vega TV Accessibility

## Overview

Audit and fix accessibility in TV applications built with React Native, React Native for Vega, or Vega WebView. Always identify the app surface first because WebView apps, native Vega RN apps, and mixed apps use different APIs and validation steps.

## When to Apply

Use this skill when user mentions:
- Accessibility, a11y, WCAG, WAI-ARIA, VoiceView, screen readers, magnifier, captions, or subtitles in a TV app
- Vega WebView app accessibility
- Native React Native for Vega app accessibility
- React Native accessibility props, roles, labels, hints, states, or announcements
- D-pad, remote, Back, Select, keyboard, or focus navigation issues
- TV modals, carousels, media playback controls, settings, search, sign-in, or error flows

## Phase Priority Guide

| Priority | Phase | Impact | When to Use |
|----------|-------|--------|-------------|
| 1 | App Type Detection | CRITICAL | Before applying any accessibility guidance |
| 2 | WebView Audit | CRITICAL | App renders HTML/JS content in Vega WebView |
| 3 | Native Vega RN Audit | CRITICAL | App is built with React Native for Vega components |
| 4 | Shared Standards | HIGH | Mapping findings to WCAG 2.2 and WAI-ARIA |
| 5 | Validation | HIGH | Re-testing with VoiceView, remote, magnifier, captions |

## Quick Decision Tree

```
What kind of Vega TV app is this?
+-- Uses @amazon-devices/webview, WebView, webview.html, or hosted HTML?
|   +-- YES -> Audit WebView surface using Vega WebView + W3C guidance
+-- Uses React Native for Vega components and package/build scripts?
|   +-- YES -> Audit native Vega RN surface using React Native for Vega guidance
+-- Uses both WebView and native RN screens?
|   +-- YES -> Audit each surface separately, then verify cross-surface focus/announcements
+-- Unknown -> Inspect manifest.toml, package.json scripts/dependencies, app entry points, and rendered UI before fixing
```

## Quick Reference

### Critical: Detect App Type First

```bash
# Vega package marker
find . -name manifest.toml -maxdepth 5

# WebView indicators
rg "@amazon-devices/webview|<WebView|webview.html|ReactNativeWebView|postMessage"

# React Native for Vega indicators
rg "@amazon-devices/react-native-kepler|build:app|vega project|react-native-vega|AccessibilityInfo"
```

### Critical: Choose the Correct Guidance

- **Vega WebView**: Use semantic HTML, ARIA, visible focus, logical tab order, focus trapping/restoration, `aria-live`, alt text, and WebView-to-native announcements when needed.
- **Native Vega RN**: Prefer React Native for Vega guidance: `role` over legacy `accessibilityRole`, `aria-*` props where recommended, `accessible`, `accessibilityHint`, `accessibilityOrientationText`, `accessibilityDescribedBy`, and careful `AccessibilityInfo` usage.
- **Both**: Target WCAG 2.2 Level A/AA, verify VoiceView output, remote navigation, magnifier, captions, and no dead-end focus zones.

## References

| File | Impact | Description |
|------|--------|-------------|
| [VEGA_WEBVIEW_ACCESSIBILITY.md](references/VEGA_WEBVIEW_ACCESSIBILITY.md) | CRITICAL | Official Vega WebView accessibility guidance for HTML/JS app surfaces |
| [VEGA_REACT_NATIVE_ACCESSIBILITY.md](references/VEGA_REACT_NATIVE_ACCESSIBILITY.md) | CRITICAL | Official React Native for Vega and React Native accessibility guidance |
| [WCAG_WAI_REFERENCE.md](references/WCAG_WAI_REFERENCE.md) | HIGH | WCAG 2.2 A/AA and WAI-ARIA APG mapping for findings |
| [TV_APP_VALIDATION.md](references/TV_APP_VALIDATION.md) | HIGH | VoiceView, remote, magnifier, captions, focus, and regression validation |

### Templates

Use [ACCESSIBILITY_CHECKLIST.md](assets/templates/ACCESSIBILITY_CHECKLIST.md) as the working checklist during audits and fixes.

### Evals

Use [evals/README.md](evals/README.md) to test trigger quality, task quality, and with-skill vs without-skill behavior.

## Problem -> Skill Mapping

| Problem | Start With |
|---------|------------|
| Unsure whether app is WebView or native Vega RN | App Type Detection |
| HTML content, web assets, or WebView container | VEGA_WEBVIEW_ACCESSIBILITY.md |
| Native RN components or React Native for Vega app | VEGA_REACT_NATIVE_ACCESSIBILITY.md |
| Mixed WebView + native screens | Audit both reference paths |
| Need conformance language or severity | WCAG_WAI_REFERENCE.md |
| Need to prove fixes work on TV | TV_APP_VALIDATION.md, then ACCESSIBILITY_CHECKLIST.md |
| VoiceView reads duplicate or wrong text | Relevant app-type reference, then TV_APP_VALIDATION.md |
| D-pad focus is lost, trapped, or invisible | Relevant app-type reference, then TV_APP_VALIDATION.md |
| Captions, subtitles, media controls, or playback flow | TV_APP_VALIDATION.md |

## Workflow

1. Detect app type from dependencies, `manifest.toml`, app entry points, and rendered UI.
2. Select the WebView, native Vega RN, or mixed-app path.
3. Audit the primary user flows: launch, navigation, search, sign-in, playback, settings, dialogs, errors, and exit.
4. Fix blocking and serious issues first: missing names, non-operable controls, lost focus, invisible focus, incorrect role/state, missing captions, unreadable contrast.
5. Map each issue to WCAG 2.2 A/AA or WAI-ARIA where applicable.
6. Validate with TV remote/D-pad, VoiceView, magnifier, captions/subtitles, and any automated checks available.
7. Report findings with app surface, file/component, issue, user impact, guideline/source, and concrete fix.

## Official Sources

- Vega WebView Accessibility Guide: https://developer.amazon.com/docs/vega/0.22/webview-accessibility-guide.html
- React Native for Vega Accessibility: https://developer.amazon.com/docs/react-native-vega/0.72/accessibility.html
- Vega App Manifest: https://developer.amazon.com/docs/vega/0.22/app-manifest.html
- React Native Accessibility: https://reactnative.dev/docs/accessibility.html
- WCAG 2.2: https://w3.org/TR/2024/REC-WCAG22-20241212
- WAI-ARIA APG: https://www.w3.org/WAI/ARIA/apg/

## Attribution

Based on official Vega WebView, React Native for Vega, React Native, WCAG 2.2, and WAI-ARIA Authoring Practices guidance.
