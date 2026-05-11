---
name: rn-tv-ui-best-practices
description: React Native TV UI best practices for tvOS, Android TV, Fire TV, and Vega OS (including react-native-tvos). Use whenever building, reviewing, or debugging a TV / set-top box / streaming (OTT) app. Covers focus management (TVFocusGuideView, hasTVPreferredFocus, trapFocus, requestTVFocus, useTVEventHandler, focus loss/jumping); D-pad / RCU / spatial navigation; swimlanes, hero banners, drawers, tabs, modals, overscan/safe zones; TV typography, contrast, HDR; remote-driven text or voice input.
---

# React Native TV UI Best Practices

Build polished React Native TV apps across tvOS, Android TV, Fire TV, Vega OS.

## When to Apply

Use when user is:
- Building or reviewing TV UI components
- Debugging focus/navigation issues
- Designing layouts for TV (10-foot experience)
- Choosing typography or color for TV displays
- Implementing keyboard/text input on TV

## When NOT to Apply

- Mobile-only React Native apps (no TV target)
- Web apps not targeting TV platforms
- General React Native performance issues unrelated to TV UX

## Quick Decision Tree

```
Starting a new TV app or doing a broad design review?
└─ Read in order: references/ten-foot-experience.md → references/layout-patterns.md → references/typography-and-color.md

Focus / navigation issue?
├─ Not sure which approach to use → references/navigation-and-focus.md (Focus Management Hierarchy)
├─ Focus doesn't start where expected → references/navigation-and-focus.md (hasTVPreferredFocus)
├─ Focus jumps unexpectedly → references/navigation-and-focus.md (Debugging Focus Issues + Common Focus Problems)
├─ Focus disappears (loader/empty/error state) → references/navigation-and-focus.md (Gotchas)
├─ Need modal/overlay focus trap → references/navigation-and-focus.md (Focus Traps)
├─ Back button not restoring focus → references/navigation-and-focus.md (Back Navigation and Focus Restoration)
├─ Need to move focus programmatically → references/navigation-and-focus.md (Imperative Focus)
└─ Cross-platform differences (tvOS vs Android TV vs Vega) → references/navigation-and-focus.md (Platform Focus Engines)

Building screens/components?
├─ Drawer / tabs / modals → references/layout-patterns.md (Navigation Patterns)
├─ Cards / rows / swimlanes / hero banners → references/layout-patterns.md (Common Components)
├─ Buttons / overlays / details panels → references/layout-patterns.md (Common Components)
└─ Safe zones / overscan / multi-aspect-ratio → references/layout-patterns.md (Layout and Safe Zones)

Visual design?
├─ Font sizes / line height / letter spacing → references/typography-and-color.md (Typography)
├─ Color / contrast / accessibility → references/typography-and-color.md (Color and Contrast)
├─ HDR / bright vs dim vs dark room → references/typography-and-color.md (HDR Considerations + Ambient Light Adaptation)
├─ Text over images or video → references/typography-and-color.md (Text Over Images)
└─ Animation / motion / feedback timing → references/ten-foot-experience.md (Feedback, Motion, and Rhythm)

Text input / search / auth?
├─ Reduce typing burden → references/keyboard-handling.md (Input Minimization)
├─ System keyboard + RCU events → references/keyboard-handling.md (Built-In System Keyboard)
├─ Custom keyboard UI → references/keyboard-handling.md (Custom Keyboard)
├─ Voice input → references/keyboard-handling.md (Voice Input)
└─ Phone-as-input / QR auth → references/keyboard-handling.md (Mobile Companion Apps)

Pre-ship review / sanity check?
├─ Focus traps & back navigation → references/navigation-and-focus.md (Verify before ship)
├─ Safe zones & aspect ratios → references/layout-patterns.md (Verify before ship)
├─ Typography sizes & contrast → references/typography-and-color.md (Verify before ship)
├─ Animation timing & input latency → references/ten-foot-experience.md (Verify before ship)
└─ Couch test (real device, real distance, real remote) → references/ten-foot-experience.md (Couch Sanity Checks)
```

## References

| File | When to Load |
|------|--------------|
| [ten-foot-experience.md](references/ten-foot-experience.md) | UX design decisions, remote interaction patterns, animation/motion |
| [layout-patterns.md](references/layout-patterns.md) | Building screens, navigation structure, component patterns, safe zones |
| [typography-and-color.md](references/typography-and-color.md) | Setting font sizes, choosing colors, ensuring readability at distance |
| [navigation-and-focus.md](references/navigation-and-focus.md) | Focus bugs, TVFocusGuideView, focus traps, back navigation, platform differences |
| [keyboard-handling.md](references/keyboard-handling.md) | Search screens, login forms, any text input UI |
