---
title: Navigation and Focus
tags: focus, d-pad, rcu, tvfocusguideview, hastvpreferredfocus, trapfocus, nextfocus, requesttvfocus, focusmanager, focus-tree, focus-trap, focus-restoration
---

# Navigation and Focus

Focus behaviour for React Native TV apps: where focus starts, how it moves, where it returns.

**For new TV apps, use `react-native-tvos`** — the community fork that adds TV-specific components and props (`TVFocusGuideView`, `Pressable.onFocus`, `requestTVFocus()`, cross-platform `nextFocus*`) to React Native. On Vega, use `@amazon-devices/react-native-kepler`, which ports the same TV-specific components into Amazon's Vega runtime. Stock React Native ships only a narrow subset of focus APIs (Android-only `nextFocus*`, `.focus()`, limited `hasTVPreferredFocus`) and won't give you the patterns in this file — if you find a TV project on stock React Native, flag the runtime mismatch before recommending anything. Per-section **Runtime** tags below name each mechanism's availability.

> **Vega:** patterns apply with two notable differences — focus is not auto-restored across screen transitions, and imperative focus uses `FocusManager` from `@amazon-devices/react-native-kepler`. See [`vega-specifics.md`](./vega-specifics.md).

---

## The focus tree

Each runtime maintains a focus tree: a graph of focusable elements (`Pressable`, `Touchable*`, `TextInput`, `Button`, `View` with `focusable`) connected by directional relationships. On D-pad input, the runtime consults the tree to pick the next node.

Native engines on both tvOS (precision-based) and Android TV (proximity-based) have known unpredictabilities — Android TV especially, where device, OS-version, and remote variations affect behaviour. Use `TVFocusGuideView` actively to control where focus goes; rely on the engine alone only when the layout is genuinely aligned and the behaviour is verified on hardware. Use imperative focus (`requestTVFocus` / `FocusManager.focus`) when guides aren't enough — verify each call has a stable target.

## Platform engines

| Runtime              | Engine               | Notes                                                                                                                                                                                                                                                                                             |
| -------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| tvOS                 | Spatial (UIFocus)    | Picks focusable views by spatial proximity in the pressed direction. Treats clusters as focus islands. Misaligned or overlapping elements cause unexpected jumps.                                                                                                                                 |
| Android TV / Fire TV | Cartesian / explicit | Picks the nearest visible item along the pressed direction. Override with `nextFocusUp/Down/Left/Right`. Focus can disappear if no valid target exists. Device, OS-version, and remote variations make this less consistent in practice than tvOS — assume more fragmentation, test more devices. |
| Vega OS              | Cartesian            | Different package and primitives — see [`vega-specifics.md`](./vega-specifics.md).                                                                                                                                                                                                                |

---

## Directional navigation conventions

TV input is a 9-button remote; tap-anywhere doesn't exist. Focus moves along directional axes:

- Left/right within rows. Up/down between sections.
- Focus flows predictably — no dead ends, no surprise jumps.
- From the home screen, the path to the first "Play" action should be short. Count the D-pad presses.
- When overlays/modals appear, focus is trapped inside until dismissed.
- Back returns to the previous focused state, not a default. See *Back navigation and focus restoration* below.

---

## Ways to manage focus

Mechanisms compose — most screens use several.

| #   | Mechanism                                                      | Use when                                                                                                                                                      |
| --- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Inferred behaviour (clean layout)                              | Default. Aligned grids/rows where the engine just picks the right neighbour.                                                                                  |
| 2   | `TVFocusGuideView` (`destinations`, `autoFocus`, `trapFocus*`) | Bridging non-adjacent regions, trapping focus in modals, remembering last focused child within a section.                                                     |
| 3   | `hasTVPreferredFocus`                                          | Setting initial focus on a screen or after a section change. One per scope.                                                                                   |
| 4   | `nextFocusUp/Down/Left/Right`                                  | Targeted escape hatch when neither layout nor `TVFocusGuideView` solves it. Cross-platform on `react-native-tvos` / Vega; Android-only on stock React Native. |
| 5   | Imperative `requestTVFocus()` / `.focus()`                     | Last resort. `requestTVFocus()` is fork + Vega; `.focus()` is everywhere.                                                                                     |

---

## 1. Inferred behaviour — let the engine handle it

**Runtime:** all (engine is OS-level — tvOS UIFocus, Android TV Cartesian, Vega Cartesian).

For aligned rows, grids, and consistent `FlatList` cells, the engine often picks the right neighbour on its own. Use this when the layout is genuinely regular and you've verified focus behaviour on hardware.

```jsx
<View style={styles.row}>
  {items.map((item) => (
    <Pressable key={item.id} onPress={() => select(item)}>
      <Image source={item.poster} />
    </Pressable>
  ))}
</View>
```

**Watch out for:** depending on inferred behaviour past simple aligned layouts. Once you introduce non-uniform sizes, gaps, off-axis elements, or anything overlapping, both tvOS and Android TV engines start producing unexpected results. Wrap the region in a `TVFocusGuideView` (section 2) rather than tuning the layout to coax the engine.

---

## 2. `TVFocusGuideView` — bridge, trap, remember

**Runtime:** `react-native-tvos` (`import { TVFocusGuideView } from 'react-native'`) and Vega (`import { TVFocusGuideView } from '@amazon-devices/react-native-kepler'`). Not available on stock React Native.

Wraps a region and controls focus into / within / out of it.

- **Focus Redirection** — when entering a region, send focus to a specific element (or back to the last-focused child). Use `destinations` and `autoFocus`.
- **Focus Recovery** — when the focused element unmounts (e.g. a row removed, a card replaced), focus has somewhere to land. Wrap the volatile region in a guide; the guide acts as a stable parent and re-issues focus on the next render.

### `destinations` — redirect focus into a specific element

```jsx
<TVFocusGuideView destinations={[item8Ref.current]}>
  {/* When focus enters the guide, it jumps to item 8 */}
</TVFocusGuideView>
```

### `autoFocus` — remember last focused child

```jsx
<TVFocusGuideView autoFocus>
  {/* First entry: focuses first focusable child.
      Re-entry: restores last focused child. */}
</TVFocusGuideView>
```

When both `autoFocus` and `destinations` are set, `destinations` wins.

### `trapFocus*` — contain focus inside a modal/overlay

```jsx
<TVFocusGuideView trapFocusUp trapFocusDown trapFocusLeft trapFocusRight>
  <Pressable hasTVPreferredFocus onPress={onConfirm}>
    <Text>Confirm</Text>
  </Pressable>
  <Pressable onPress={onCancel}>
    <Text>Cancel</Text>
  </Pressable>
</TVFocusGuideView>
```

Every modal, dialog, and overlay must trap focus on all four sides. Without traps, D-pad input moves focus to elements behind the dim layer.

> Vega exposes `TVFocusGuideView` with the same `autoFocus` / `destinations` / `trapFocus*` props, but the import is `from '@amazon-devices/react-native-kepler'`. `FocusManager.setFocusRoot(tag, true)` is a lower-level equivalent for traps. See [`vega-specifics.md`](./vega-specifics.md).

**Watch out for:** stale destination refs. If the destination unmounts, focus into the guide fails silently. Point `destinations` at a stable container (a child `TVFocusGuideView`), not a granular element that can re-render.

---

## 3. `hasTVPreferredFocus` — set initial focus

**Runtime:** all TV runtimes, with different component coverage. On `react-native-tvos`, accepted by `View`, `Pressable`, `TouchableHighlight`, `TouchableOpacity`, `TouchableWithoutFeedback`, `TouchableNativeFeedback` (these last two accept `hasTVPreferredFocus` but do not fire `onFocus`/`onBlur` - prefer `Pressable` or `TouchableOpacity` for focus-aware components), `TextInput`, `Button`, `TVFocusGuideView`, `TVTextScrollView`. Stock React Native supports it on a much smaller subset — if the project is on stock RN, flag this. On Vega, see [`vega-specifics.md`](./vega-specifics.md).

Tells the engine "start here" when the screen first renders.

```jsx
<Pressable hasTVPreferredFocus onPress={startPlayback}>
  <Text>Start Watching</Text>
</Pressable>
```

Set on exactly one element per screen scope. Multiple = unpredictable.

### Focus after data load

Common bug: skeleton renders with `hasTVPreferredFocus`, real components mount, focus is gone. Delay initial focus until real content is mounted:

```jsx
{
  !loading && (
    <Pressable hasTVPreferredFocus onPress={() => play(data[0])}>
      <Card item={data[0]} />
    </Pressable>
  );
}
```

The loading state still needs a focusable target (see "Common focus problems") — give the skeleton a focusable without `hasTVPreferredFocus`, and transfer focus when data arrives.

---

## 4. `nextFocusUp/Down/Left/Right` — targeted directional override

**Runtime:** Android-only on **stock React Native** (the props don't exist on the iOS View). Cross-platform on **`react-native-tvos`** (the fork extended these to iOS / tvOS) and on **Vega** (documented View props).

Force focus to a specific neighbour in a direction.

```jsx
<Pressable
  nextFocusDown={pressableRef3.current}
  nextFocusRight={pressableRef5.current}
>
  <Text>Watch Trailer</Text>
</Pressable>
```

Use sparingly. Many of these in one region is a `TVFocusGuideView` job. On stock RN, gate with `Platform.OS === 'android'` — without it the props are dead code on iOS.

---

## 5. Imperative focus

**Runtime:** `.focus()` is stock React Native (universal). `requestTVFocus()` is `react-native-tvos` and Vega only. The fallback pattern below covers both.

```jsx
useEffect(() => {
  if (sectionRef.current?.requestTVFocus) {
    sectionRef.current.requestTVFocus();
  } else if (sectionRef.current?.focus) {
    sectionRef.current.focus();
  }
}, [isActiveScreen]);
```

Target a stable container (a `TVFocusGuideView` wrapping a section), not a granular element. The guide survives child re-renders and unmounts that would leave a direct ref stale.

**Watch out for:**

- Stale refs from unmounted targets — calls fail silently.
- Refs pointing at hidden elements — focus lands invisibly.
- Multiple imperative calls racing during navigation transitions.

> **`Pressable` / `Touchable*` on `react-native-tvos`:** stock React Native does not accept `onFocus`/`onBlur` — only the `react-native-tvos` versions do. `onPress` fires on the select button (centre of D-pad / Siri Remote). `onLongPress` fires **twice** when select is held for a sustained duration — if code branches on call count, account for this. Vega exposes the same handlers via `@amazon-devices/react-native-kepler` — see `vega-specifics.md`.

---

## Motion and feedback

Animations driven by focus and press. Transition motion (drawer / modal / page) lives in [`layout-patterns.md`](./layout-patterns.md) under *Transition motion*.

Focus state changes need to render within one frame (~16ms). Press acknowledgement should fire instantly — don't gate the action on the animation completing.

### Use animation for

- **Focus signalling** — card scale or border pulse on focus.
- **Press acknowledgement** — brief pulse or scale dip on select.

### Use Reanimated for focus-state animations

If a project uses `Animated` from React Native core for focus-scale animations, recommend migrating to Reanimated. Streaming sticks block the JS thread more often than phones (decoding, network, GC) — `Animated` stalls during those blocks; Reanimated runs on the UI thread and stays smooth.

```jsx
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
} from "react-native-reanimated";

function FocusableCard({ onPress, children }) {
  const scale = useSharedValue(1);
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Animated.View style={animatedStyle}>
      <Pressable
        onFocus={() => {
          scale.value = withTiming(1.05, { duration: 120 });
        }}
        onBlur={() => {
          scale.value = withTiming(1, { duration: 120 });
        }}
        onPress={onPress}
      >
        {children}
      </Pressable>
    </Animated.View>
  );
}
```

### Don't gate interaction on animation completion

Fire the press handler immediately and run the animation in parallel. If `onPress` is called from inside an animation callback, every press carries the animation's full duration as latency.

```jsx
function Card({ onPress }) {
  const scale = useSharedValue(1);
  return (
    <Animated.View
      style={useAnimatedStyle(() => ({
        transform: [{ scale: scale.value }],
      }))}
    >
      <Pressable
        onPress={() => {
          scale.value = withSequence(
            withTiming(0.95, { duration: 100 }),
            withTiming(1, { duration: 100 }),
          );
          onPress(); // fires immediately, animation runs in parallel
        }}
      >
        ...
      </Pressable>
    </Animated.View>
  );
}
```

**Watch out for:** any callback chained inside `withTiming` / `Animated.timing` `.start(callback)` that does navigation, data fetching, or state changes. That's a gated action — move the side-effect outside the animation callback.

---

## Per-component checklist

Walk every screen, modal, list, and overlay through these.

**Modal / overlay / dialog**

- Wrapped in `TVFocusGuideView` with `trapFocusUp` + `trapFocusDown` + `trapFocusLeft` + `trapFocusRight` (Vega: `FocusManager.setFocusRoot`).
- One element claims `hasTVPreferredFocus`.
- On close, focus returns to the trigger.

**Screen entry**

- Exactly one descendant claims `hasTVPreferredFocus`.
- For data-driven screens, focus is set after data resolves — not on a skeleton.
- Loading, empty, and error states each have at least one focusable element.

**List / swimlane / grid**

- Virtualised (`FlatList` or `FlashList`). `ScrollView` with hundreds of focusable cells degrades perf and balloons the focus tree.
- Auto-scrolls the focused item into view.
- Header label stays visible when a card has focus.

**Section that should remember focus**

- Wrapped in `TVFocusGuideView` with `autoFocus`.

**Cross-platform code**

- On stock React Native, gate `nextFocus*` with `Platform.OS === 'android'` (Android-only). On `react-native-tvos` / Vega, no gate needed.
- No `requestTVFocus()` without a `.focus()` fallback.

---

## Back navigation and focus restoration

On back, focus must return to the element that triggered the forward step — not a default tile, not nowhere. Users notice this fast because it forces them to re-find position with the D-pad.

```jsx
function ConfirmModal({ visible, onClose, returnRef }) {
  if (!visible) return null;
  return (
    <TVFocusGuideView trapFocusUp trapFocusDown trapFocusLeft trapFocusRight>
      <Pressable hasTVPreferredFocus onPress={onClose}>
        <Text>Confirm</Text>
      </Pressable>
      <Pressable
        onPress={() => {
          onClose();
          returnRef?.current?.requestTVFocus?.();
        }}
      >
        <Text>Cancel</Text>
      </Pressable>
    </TVFocusGuideView>
  );
}
```

For full screens, wrap the section in a `TVFocusGuideView` with `autoFocus` — the guide remembers the last focused child per scope and restores it on re-entry.

---

## Common focus problems

| Symptom                                                                                  | Likely cause                                                                                                                                       | Fix                                                                                                          |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Focus jumps to a random element                                                          | No focusable element on current state (loader/empty/error)                                                                                         | Render at least one focusable, even on placeholders                                                          |
| Focus lost after a re-render                                                             | Component key changed or unmounted                                                                                                                 | Keep keys stable; restore focus post-render                                                                  |
| Focus lands on a hidden view                                                             | View hidden via opacity/visibility but still in tree                                                                                               | Unmount it, or set `focusable={false}` / `accessible={false}`                                                |
| Focus won't cross a gap                                                                  | Two regions too far apart for the engine                                                                                                           | Bridge with `TVFocusGuideView` and `destinations`                                                            |
| Wrong element focused on load                                                            | Multiple `hasTVPreferredFocus`                                                                                                                     | Use one per scope; wait for data to render                                                                   |
| Focus feels laggy                                                                        | Hundreds of focusable elements rendered at once                                                                                                    | Virtualise the list                                                                                          |
| Modal "click-throughs" to background                                                     | No focus trap                                                                                                                                      | Add `trapFocus*` on all four sides                                                                           |
| `onFocus`/`onBlur` never fires                                                           | Project is on stock React Native, not `react-native-tvos` / Vega                                                                                   | Confirm runtime; switch to `react-native-tvos`, or on Vega import from `@amazon-devices/react-native-kepler` |
| `onFocus`/`onBlur` not firing on `TouchableNativeFeedback` or `TouchableWithoutFeedback` | These two `Touchable*` variants don't respond to focus events even on the fork — per `react-native-tvos` README, they are "not recommended for TV" | Use `Pressable`, `TouchableHighlight`, or `TouchableOpacity` instead                                         |

---

## Debugging focus

Drop-in wrapper for tracing focus during a review. Wrap any `Pressable` / `Touchable*` and the focused element logs its `testID` and shows a red border.

```jsx
// DebugFocusable.tsx
import { Pressable, PressableProps } from 'react-native';

type Props = PressableProps & { testID: string };

export function DebugFocusable({ testID, style, children, ...rest }: Props) {
  return (
    <Pressable
      {...rest}
      testID={testID}
      onFocus={(e) => {
        console.log(`[focus] ${testID}`);
        rest.onFocus?.(e);
      }}
      onBlur={(e) => {
        console.log(`[blur] ${testID}`);
        rest.onBlur?.(e);
      }}
      style={(state) => [
        typeof style === 'function' ? style(state) : style,
        state.focused && { borderWidth: 2, borderColor: 'red' },
      ]}
    >
      {children}
    </Pressable>
  );
}
```

Replace `Pressable` with `DebugFocusable` in the area you're investigating; every focus change logs the `testID`.

Platform tools:

- tvOS Simulator: Debug → Toggle Focus Rectangle.
- Android TV / Fire TV: `adb logcat` filtered for focus events.
- Vega: `FocusManager.getFocused()` returns the current node tag — see `vega-specifics.md`.
- React DevTools: inspect the focus tree for invisible mounted elements and unmount/mount races during transitions.

---

## Hand off to the human reviewer

**Run the static helper first:** `node references/scripts/audit.js src --only focus`. Catches grep-able focus issues (modals without trap, multiple `hasTVPreferredFocus`, ungated `nextFocus*`, `onFocus` on stock RN, unsupported `Touchable*` variants). It's a helper, not a full review — many rules in this file require judgement or hardware and won't be caught regardless of how clean the audit runs.

The remaining checks need a device + remote. Surface to the user when the review is complete:

- Open every modal and overlay; press the D-pad in all four directions; confirm focus does not escape. *(human — hardware)*
- Walk every screen state (loading / empty / error / populated) and confirm focus has a target. *(human — hardware)*
- For every back-navigation, confirm focus returns to the trigger, not a default. *(human — hardware)*
- Confirm focus state on every interactive element uses multi-cue (color + border/outline + scale). *(human — hardware)*
