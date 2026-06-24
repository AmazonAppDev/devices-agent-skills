---
title: Vega OS — pointers and gotchas
tags: vega, kepler, fire-tv, react-native-kepler, focusmanager, navigable, usetveventhandler, manifest.toml, inputd, synchronous-focus, flash-list, amazon-devices
---

# Vega OS — pointers and gotchas

Vega's narrow set of divergences from `react-native-tvos`: package paths, deprecated components, observe-only event handler, focus restoration, and platform-only features. The agent should defer to the live Vega docs for API specifics — this file captures only the non-obvious gotchas.

> **Coverage:** this file currently reflects **Vega SDK 0.22 / React Native for Vega 0.72**. Vega's API surface evolves between SDK versions. For the most up-to-date information — and to give the agent live Vega-specific tooling and metadata — install the official Amazon Devices Builder Tools MCP server: `npx -y @amazon-devices/amazon-devices-buildertools-mcp@latest init-context`. See <https://developer.amazon.com/docs/vega/0.22/mcp-server.html>.

## Canonical references

- Vega SDK 0.22 overview (entry point): <https://developer.amazon.com/docs/vega/0.22/vega-overview.html>
- Builder Tools MCP setup: <https://developer.amazon.com/docs/vega/0.22/mcp-server.html>

For specific API pages (Focus Manager, TVFocusGuideView, useTVEventHandler, Navigable, userInputManager, FlashList, Best Practices, etc.), navigate from the overview rather than relying on deep-linked URLs in this file — Amazon's URL namespaces have shifted across SDK versions and would go stale here. With the Builder Tools MCP installed, the agent has direct access to live docs without needing manual URL lookup.

## Relationship to `react-native-tvos`

Vega's React Native runtime is **based on `react-native-tvos`**. TV-specific components are ported into the `@amazon-devices/react-native-kepler` namespace so that one namespace supports both multimodal and TV platforms. `TVFocusGuideView` is a direct port. Most focus patterns and most prop APIs are the same; the differences captured below are narrow.

## Detection signals

A project is on Vega when:

- `package.json` lists `@amazon-devices/react-native-kepler`.
- A monorepo Vega package depends on `@vega-tv/react-native-module-resolver-preset`.
- A `manifest.toml` exists at the project root.

If none of these are present, this file does not apply — go back to `navigation-and-focus.md`.

## Non-obvious gotchas

These are the items the live docs won't surface to the agent automatically — pin them in the agent's mental model when reviewing or building Vega code.

- **Different package.** Focus and event APIs come from `@amazon-devices/react-native-kepler`, not `react-native`. An import from `react-native` for `TVFocusGuideView`, `useTVEventHandler`, or `TVEventHandler` is wrong on Vega.
- **`useTVEventHandler` is observe-only.** Listeners read events but cannot suppress default focus movement. Code that assumes a handler can intercept and cancel D-pad navigation (a pattern that works on `react-native-tvos`) is wrong on Vega.
- **Manifest entry required for remote events.** `manifest.toml` must include `[[wants.service]] id = "com.amazon.inputd.service"`. Without it, `useTVEventHandler` registers but no events fire — silently.
- **Manifest entry required for the virtual keyboard.** `manifest.toml` must also include `[[wants.service]] id = "com.amazon.inputmethod.service"` for the system keyboard to surface when a `TextInput` gains focus on Vega Virtual Device or hardware. Without it, `<TextInput>` accepts focus but no keyboard appears — silently.
- **`FocusManager.focus(ref.current)` typechecks but fails.** The `tag` parameter is a numeric tag from `findNodeHandle(ref.current)`, not the ref itself.
- **`FocusManager.focus` inside `useEffect` on initial mount can fire before the native view exists.** Documented Vega quirk; workaround is `setTimeout(..., 0)`. Not a bug to "fix" by removing the effect.
- **Back button has no long-press.** Vega emits one event for back regardless of hold duration. Code that counts repeats on back is broken.
- **Two imperative focus APIs exist.** Both `ref.current.requestTVFocus()` and `FocusManager.focus(findNodeHandle(ref.current))` are documented on Vega. `requestTVFocus()` is the simpler form (ported from `react-native-tvos`); `FocusManager` is preferable when the same flow also needs `setNextFocus` / `setFocusRoot` / `getFocused` — it shares the same imperative API surface.
- **`nextFocusUp/Down/Left/Right` work on Vega.** The Android-only caveat from `react-native-tvos` does not apply (Vega is not Android). They follow Cartesian semantics.
- **`nextFocus*` self-pointing blocks the direction.** Setting `nextFocusUp={ownNodeHandle}` (or any direction) blocks D-pad presses in that direction; setting it to `undefined` restores default Cartesian behaviour. Useful for damming focus at a specific edge without wrapping the region in a `TVFocusGuideView`.

## Default focus styling — what's free vs what needs work

Vega gives built-in focus visuals to only two components:

- `<Button>` — appearance changes on focus.
- `<TouchableOpacity>` — opacity changes to `0.2` on focus by default. Configure with `activeOpacity`.

`<Pressable>`, `<TouchableHighlight>`, `<TouchableWithoutFeedback>`, and `<View focusable>` get **no built-in focus visuals**. Wire focus state manually via `onFocus`/`onBlur` and conditional styles. Don't rely on platform defaults to make focus visible on these.

## Initial focus: two paths

Vega supports two distinct mechanisms; they don't overlap:

- **`hasTVPreferredFocus`** sets focus during the component's initial mount only. It does not re-run on later state changes. Use for static screens where the first focusable is known at render time.
- **`useEffect` or `useFocusEffect` + `FocusManager.focus()`** sets focus dynamically — after data loads, on screen return, or in response to state changes. Use for anything beyond initial mount.

`hasTVPreferredFocus` works on Vega — it just only fires on initial mount and won't re-target focus after a render. For dynamic focus changes, reach for `FocusManager.focus(findNodeHandle(...))`.

## Focus restoration is not built into Vega

The Vega platform does not auto-restore focus across screen transitions. Neither `@amazon-devices/react-navigation__stack` nor `@amazon-devices/react-navigation__native-stack` does this for you. If a screen review shows "back navigation drops focus on a default tile," this is almost always the missing piece — not a per-screen bug.

Implementation pattern for multi-screen apps using React Navigation:

```jsx
import { useFocusEffect } from "@react-navigation/native";
import { FocusManager } from "@amazon-devices/react-native-kepler";
import { findNodeHandle, Pressable } from "react-native";
import { useRef, useCallback } from "react";

function HomeScreen() {
  // 1. Track the most recently focused element on this screen.
  const lastFocusedRef = useRef(null);

  // 2. On screen re-entry, restore focus to that element.
  useFocusEffect(
    useCallback(() => {
      const tag = findNodeHandle(lastFocusedRef.current);
      if (tag != null) {
        // 3. setTimeout(..., 0) sidesteps the documented Vega quirk where
        //    FocusManager calls inside useEffect / useFocusEffect can fire
        //    before the native view exists.
        setTimeout(() => FocusManager.focus(tag), 0);
      }
    }, []),
  );

  return (
    <Pressable
      onFocus={(e) => {
        // Track whichever element is currently focused so we can restore to it.
        lastFocusedRef.current = e.currentTarget;
      }}
    >
      {/* ... */}
    </Pressable>
  );
}
```

For apps with multiple screens, a single `Map<routeName, ref>` (or a small context) keeps the most-recently-focused element per route so each screen's `useFocusEffect` can restore from the right entry.

## Cartesian edge-overlap gotcha

Vega's default focus engine considers more than alignment — it evaluates edge overlap and weighted distance. Two surprising cases the docs call out:

- A small "side item" overlapping the bottom edge of the focused row can intercept Down-press focus instead of the obvious next row, depending on whether the side item overlaps horizontally or vertically with the next-row item.
- A full-width row between two narrower rows can be **skipped** by Down navigation if its height is below a threshold (the docs show ~104px skipped vs ~105px caught).

Fixes when this matters:

- `FocusManager.setNextFocus(fromTag, toTag, direction)` — define a custom focus path declaratively.
- `nextFocusUp/Down/Left/Right` props with refs converted via `findNodeHandle`.
- `TVFocusGuideView destinations={[ref.current]}` to force entry focus into a container.

Don't try to fix this with layout tweaks alone; the heuristic is sensitive enough that small layout changes can flip the behaviour.

## List edge focus — focus rolls to the next row by default

In Vega's `ScrollView` / `FlatList`, when focus reaches the rightmost (or leftmost) element of a horizontal row and the user presses past it, focus jumps to a row above or below — **it does not trap at the row's edge** by default.

If an app wants "trap focus at the row end" semantics for swimlanes, implement it explicitly via `nextFocusRight` returning the same node handle (effectively blocking the press) or wrap the row in a `TVFocusGuideView` with `trapFocusRight` / `trapFocusLeft`.

## Synchronous focus events

Vega-only opt-in. When set on a component, `onFocus` and `onBlur` callbacks execute **synchronously on the UI thread** — the UI thread blocks until the JS callback returns. Default is async.

> **Prop name has appeared as both `enableSynchronousFocusEventsVega` and `enableSynchronousFocusEventsKepler` in Amazon's docs** (Focus Management page vs View component page). Verify the current name against the installed Vega runtime's TypeScript types or the React Native for Vega release notes before using it. Both spellings have been seen in the wild.

When to use:

- Focus gets reset to the first child inside a `TVFocusGuideView` during rapid key presses.
- An item's `zIndex` change on focus causes the focus to be lost (the item is removed and reinserted, dropping focus).
- A specific UI requirement strictly requires all `onFocus` / `onBlur` side effects to complete before focus moves to another item.

Constraints (these are not optional):

- **Do not call programmatic focus methods inside the synchronous `onFocus`/`onBlur`.** That means no `requestTVFocus()`, no `FocusManager.focus()`/`.blur()`, no `ref.focus()`/`ref.blur()`.
- Don't change the prop value after initial render.
- Don't mix synchronous and non-synchronous components under the same parent — keep groupings consistent.

Side effects to plan for:

- Long animations may be skipped on rapid key presses (reduce duration or drop the animation).
- Unnecessary re-renders cause perceptible lag — the app needs to be optimised before enabling this.
- In-progress animations may drop frames during focus events.

Keep usage minimal. This is not a general "better focus" toggle; it's a targeted fix for a specific class of focus-loss bugs.

## `TVFocusGuideView` on Vega

`TVFocusGuideView` exists on Vega — same role as on `react-native-tvos`, but with a different import path and a smaller documented prop surface. Confirmed against <https://developer.amazon.com/docs/vega-api/0.22/tvfocusguideview.html> (SDK 0.22, open beta).

Documented props: `autoFocus`, `destinations`, `trapFocusUp`, `trapFocusDown`, `trapFocusLeft`, `trapFocusRight`. Documented method: `setDestinations(refs)` to update destinations dynamically.

- **Import is from `@amazon-devices/react-native-kepler`,** not from `react-native`: `import { TVFocusGuideView } from '@amazon-devices/react-native-kepler';`
- **`hasTVPreferredFocus` works on Vega in general** — it's accepted on `Pressable`, `Touchable*`, `View`, `TextInput`, `Button`, etc. — but is **not documented as a prop on Vega's `TVFocusGuideView`**. Don't put it on the focus-guide itself; place `hasTVPreferredFocus` on a focusable child, or use `destinations` / `autoFocus` to control entry focus.
- **`destinations` takes precedence over `autoFocus`** when both are set. Same as `react-native-tvos`.
- **`setDestinations` silently fails if the target component isn't mounted yet.** Two workarounds documented: prefer the `destinations` prop, or wrap the call in `setTimeout`.
- **TypeScript strict mode reports a children-prop error** on Vega's `TVFocusGuideView`. Suppress with `{/* @ts-expect-error */}` immediately above the JSX. This is a known doc'd issue, not a bug to fix in product code.

## List rendering and `Image` on Vega

General `FlashList` / `FlatList` / `LegendList` rules (props that don't transfer, no `key` on items, no `useState` in recycled cells, nested-list memoisation, inline `renderItem`) live in [`layout-patterns.md`](./layout-patterns.md) — they apply on every runtime, not just Vega.

Vega-only deltas:

- **Package name:** install `@amazon-devices/shopify__flash-list` (e.g. `"~2.0.0"`), not the public `@shopify/flash-list`. System-deployed and autolinked at runtime — version is pinned to the React Native for Vega version it's built against, so uplevel the library when you uplevel the runtime. `LegendList` (`@legendapp/list`) has no Vega-specific validation; treat it as a candidate the team can evaluate, not a default.
- **`Image` caches natively on Vega.** Don't add `react-native-fast-image` or `expo-image` — the built-in `Image` performs equivalently. Provide multiple resolutions / cropped thumbnails for list cells to save decode CPU.
- **Native `SplashScreen` API** with `usePreventHideSplashScreen()` and `useHideSplashScreenCallback()` hooks. Don't roll a JS-side splash.
- **Overdraw debug flag.** Launch with `?SHOW_OVERDRAWN=true` to colour-code overdrawn regions (blue 1×, green 2×, pink 3×, red 4+×). Use this when a screen feels janky on hardware.

## Hand off to the human reviewer

Agent confirms statically; the user verifies the rest on a Vega device:

- All `useTVEventHandler` consumers have `com.amazon.inputd.service` in `manifest.toml`. _(agent)_
- All `<TextInput>` consumers have `com.amazon.inputmethod.service` in `manifest.toml`. _(agent)_
- All imperative focus calls use `FocusManager.focus(findNodeHandle(...))`, not bare refs. _(agent)_
- No new `Navigable` or `UserInputManager` usage; existing ones tracked for migration. _(agent)_
- No flow assumes the event listener suppresses default focus movement. _(human)_
- No long-press behaviour depends on the back button repeating. _(human)_
