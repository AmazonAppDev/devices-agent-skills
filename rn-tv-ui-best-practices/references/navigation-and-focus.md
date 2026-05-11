# Navigation and Focus

Focus management for React Native TV apps. The most common source of TV UX bugs.

## The Focus Tree Mental Model

Each platform builds a **focus tree**: an internal map of all focusable elements. Every `Pressable`, `Touchable`, or `TextInput` becomes a node, connected to its neighbors by directional relationships. When a key event comes in, the focus engine consults this tree to determine which node to highlight next.

React Native TV mirrors this concept with a unified set of focus APIs so you can build predictable flows without diving into native code. Understanding this tree structure helps debug — if focus jumps unexpectedly, the tree's structure (element positions, visibility, mount status) is what's broken.

## Platform Focus Engines

Each platform handles focus differently. Understand these differences before writing focus code.

### tvOS (Inferred Focus Engine)

Apple's engine is spatial and physics-based:
- Searches for focusable views in the pressed direction based on spatial proximity.
- Treats clusters of related items as "focus islands."
- Expects clean grid/alignment — misaligned or overlapping elements cause unexpected jumps.
- Supports diagonal movement and inertia-based swipes from Siri Remote.

### Android TV (Explicit Directional Model)

More flexible, more manual:
- Focus moves to nearest visible item along pressed direction (Cartesian).
- Override with `nextFocusUp`, `nextFocusDown`, `nextFocusLeft`, `nextFocusRight`.
- Tolerates less regular layouts, but focus can disappear entirely if no valid target exists.

**Note:** `nextFocus*` props are Android-only, ignored on tvOS. Don't use in cross-platform codebases.

### Vega OS

Cartesian focus management like Android TV.

## Focus Management Hierarchy

Apply in this order. Each level is a fallback when the previous doesn't work:

### 1. Inferred Behavior (Default — Always Try First)

Design your UI so the focus engine handles everything automatically:

- Align and space elements logically so directional presses resolve to intended neighbor.
- Avoid dead zones (gaps in focusable elements cause unpredictable jumps).
- Group related UI into containers ("focus islands").
- On tvOS: account for diagonal/inertia. On Android TV: strict up/down/left/right.

```jsx
<View style={styles.row}>
  {items.map((item) => (
    <Pressable key={item.id}
      onPress={() => select(item)}
      onFocus={() => setFocusedItem(item.id)}
    >
      <Image source={item.poster} />
    </Pressable>
  ))}
</View>
```

**If focus behaves strangely, adjust the layout first — don't add more code.**

### 2. TVFocusGuideView (Complex Layouts)

Bridges areas that don't naturally connect. Groups focusable elements so the system remembers last focused child and redirects focus intelligently.

```jsx
<TVFocusGuideView destinations={[refSidebar, refGrid]}>
  <View style={{ flexDirection: 'row' }}>
    <Sidebar ref={refSidebar} />
    <ContentGrid ref={refGrid} />
  </View>
</TVFocusGuideView>
```

- If you need many guides, your layout probably needs simplifying.
- Keep destination refs up to date — stale refs cause focus loss.

### 3. hasTVPreferredFocus (Initial Focus)

Tells the engine "start here" when a screen first loads.

```jsx
<Pressable hasTVPreferredFocus onPress={startPlayback}>
  <Text>Start Watching</Text>
</Pressable>
```

- Never set on multiple elements in the same view (unpredictable results).
- Delay focus until data-dependent UI has rendered.

### 4. Focus Traps (Modals/Overlays)

Use `trapFocus*` props on `TVFocusGuideView` to contain focus inside temporary surfaces:

```jsx
<TVFocusGuideView trapFocusUp trapFocusDown trapFocusLeft trapFocusRight>
  <View>
    <Pressable hasTVPreferredFocus onPress={onConfirm}>
      <Text>Confirm</Text>
    </Pressable>
  </View>
</TVFocusGuideView>
```

**Platform note:** `trapFocus*` is built into the framework on `react-native-tvos` (tvOS and Android TV). Other platforms — notably web-based TVs like Tizen and webOS — don't expose this natively. On those, use a spatial navigation library (e.g., `@noriginmedia/norigin-spatial-navigation`) with equivalent concepts like `isFocusBoundary` and `saveLastFocusedChild`. Consider wrapping both in a shared `FocusBoundary` abstraction so the same patterns hold across your codebase.

**Verify before ship:** every modal and overlay traps focus inside itself. Open each one, mash the D-pad in all four directions, and confirm focus never escapes to elements behind the dim layer.

### 5. Imperative Focus (Last Resort Only)

Use `requestTVFocus()` (preferred on react-native-tvos) or `.focus()`:

```js
useEffect(() => {
  if (lastFocusedRef.current?.requestTVFocus) {
    lastFocusedRef.current.requestTVFocus();
  } else if (lastFocusedRef.current?.focus) {
    lastFocusedRef.current.focus();
  }
}, [isActiveScreen]);
```

**Risks:**
- If referenced element is unmounted or ref is stale, focus call fails silently.
- Overuse signals your layout/navigation is too brittle.
- Prefer focusing a stable container (TVFocusGuideView wrapping a section) over a granular element.

**If you must use imperative focus, target a stable container.** Focusing a `TVFocusGuideView` wrapping a section is safer than focusing a granular element — the guide acts as a predictable anchor and survives child re-renders or unmounts that would otherwise leave a direct ref stale.

## Back Navigation and Focus Restoration

### Focus Restoration

- `TVFocusGuideView` manages last-focused element internally per scope.
- When user returns to a section, the same element is automatically refocused.
- For complex layouts, nest multiple guides — each remembers focus for its region.
- Use `hasTVPreferredFocus` once within a guide for first-time default focus; the guide handles subsequent restores.

### Overlays/Modals

When an overlay closes, focus must return to the element that opened it:

```jsx
function ConfirmModal({ visible, onClose, returnRef }) {
  return visible ? (
    <TVFocusGuideView trapFocusUp trapFocusDown>
      <Pressable hasTVPreferredFocus onPress={onClose}>
        Confirm
      </Pressable>
      <Pressable onPress={() => { onClose(); returnRef?.current?.focus(); }}>
        Cancel
      </Pressable>
    </TVFocusGuideView>
  ) : null;
}
```

### Back Button Consistency

Each back press should move back one layer and restore previous focus state. Same behavior everywhere — modals, drawers, screens.

**Verify before ship:** for every navigation transition, press back and confirm focus lands on the element that triggered the forward step — not a default tile, not nowhere. This is the bug users notice fastest because it forces them to re-find their place with the D-pad.

## Debugging Focus Issues

### Visualize Focus

- **tvOS**: Simulator → Debug > Toggle Focus Rectangle.
- **Android TV**: `adb logcat` and filter for focus changes.
- **Instrument directly**: Add visible borders on focus for debugging.

```jsx
<Pressable
  testID="playButton"
  style={({ focused }) => ({
    borderWidth: focused ? 2 : 0,
    borderColor: focused ? 'red' : 'transparent',
  })}
>
  <Text>Play</Text>
</Pressable>
```

### Add Logs

```jsx
<Pressable
  testID="playButton"
  onFocus={() => console.log('Focused: playButton')}
  onBlur={() => console.log('Blurred: playButton')}
>
  <Text>Play</Text>
</Pressable>
```

Log `testID` or `accessibilityLabel` for each component to pinpoint where focus actually landed.

### React DevTools

- Inspect which components are actually focusable.
- Identify invisible/off-screen elements still receiving focus.
- Profile re-renders after D-pad key press to catch timing issues (component mounting/unmounting during focus transition).

## Gotchas

- The **focus management hierarchy** is: (1) clean layouts with inferred behavior, (2) TVFocusGuideView, (3) hasTVPreferredFocus, (4) trapFocus props, (5) requestTVFocus() as last resort. If you're reaching for imperative focus, your layout probably needs fixing.
- `nextFocusUp`/`nextFocusDown`/etc. are **Android-only** and ignored on tvOS. Don't use them in cross-platform codebases.
- Hidden views can still **receive focus** if they remain in the tree. When hiding elements, unmount them entirely or disable focus explicitly.
- Always have **at least one focusable element** on screen — including loaders, empty states, and error states. Without one, focus jumps to arbitrary locations or vanishes entirely. Verify by walking every screen state (loading, empty, error, populated) and confirming focus has somewhere to land.
- On tvOS, **misaligned or overlapping elements** cause unexpected focus jumps. The focus engine expects clean grid alignment.
- `hasTVPreferredFocus` on **multiple elements** in the same view produces unpredictable results. Use it once per screen.

## Common Focus Problems

| Problem | Cause | Fix |
|---------|-------|-----|
| Focus jumps to random element | No focusable element on current screen (loader/empty state) | Always render a focusable placeholder |
| Focus lost after re-render | Component key changed or unmounted | Keep keys stable; restore focus post-render |
| Focus lands on hidden content | Hidden view still in tree | Unmount hidden elements or disable focus |
| Focus won't cross a gap | Two areas too far apart for engine | Use TVFocusGuideView to bridge |
| Wrong element focused on load | Multiple `hasTVPreferredFocus` | Use only one; wait for UI to render |
| Focus feels laggy | Too many focusable elements | Reduce count; virtualize lists |

## Building Predictable Navigation

- **Keep movement consistent**: If "right" moves to next card on one screen, same everywhere.
- **Let the layout lead**: Clear alignment helps the engine make right decisions.
- **Plan focus transitions**: Define where focus starts, how "back" behaves, what regains focus on return.
- **Simplify the hierarchy**: Shallow navigation works best. Too many layers = lost users.

**Verify before ship:**

- Every interactive element shows a visible focus state using multi-cue (color + border/outline + mild scale) — color alone fails on washed-out displays and for color-deficient users.
- No dead ends: from any focused element, the user can always navigate back. Walk every screen and confirm "back" produces a sensible destination, not a stuck state.
