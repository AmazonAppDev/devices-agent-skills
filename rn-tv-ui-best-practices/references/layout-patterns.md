---
title: Layout Patterns and Common Components
tags: drawer, tabs, modal, overlay, card, swimlane, carousel, hero, button, safe-zone, overscan, flatlist, flashlist, legendlist, 16:9, 21:9
---

# Layout Patterns and Common Components

Screen structure, navigation placement, card/row sizing, list virtualisation, and overscan handling for TV. Patterns are library-agnostic; `@react-navigation/*` shown as the common choice.

> **Vega:** install `@amazon-devices/shopify__flash-list` instead of `@shopify/flash-list`. Layout primitives otherwise identical. See [`vega-specifics.md`](./vega-specifics.md).

---

## Three properties of a working TV layout

1. **Orientation** — where am I.
2. **Context** — what can I do here.
3. **Momentum** — where can I go next.

Loss of any of these = the user hits back. Most layout bugs trace to one of these breaking.

---

## Spacing and density

Starting points calibrated for 10ft viewing distance. Adapt per brand; verify on hardware.

| Concern                      | Starting point            |
| ---------------------------- | ------------------------- |
| Safe zone                    | 5–10% margin on all sides |
| Card focus scale             | 3–5% larger               |
| Vertical rhythm between rows | 1.5× card height          |
| Drawer items                 | 5–7 max                   |
| Tab count                    | 3–5 max                   |
| Drawer/modal animation       | <200ms                    |
| Modal fade in                | ~150ms                    |
| Page transition              | <300ms                    |
| Focus state change           | <16ms (one frame)         |

---

## Transition motion

Drawer / modal / page transitions and ambient screen motion. Focus-driven and press-driven animation lives in [`navigation-and-focus.md`](./navigation-and-focus.md) under *Motion and feedback*.

TV input pipelines add 50–100ms of latency between remote press and the event reaching the app. The pipeline adds its own latency on top of dev-machine measurements — keep transitions short.

### Use transitions for

- **Continuity** — detail panel sliding in from the right ("same thing, deeper") rather than replacing the screen abruptly.
- **Hierarchy signalling** — drawer slide-in distinguishes "global navigation" from in-screen focus movement.

### Don't animate

- **Decorative motion** that doesn't communicate change (looping decorations, idle shimmer on always-visible elements).
- **More than two concurrent animations** in the same region.
- **Transition fades over 300ms** — flag and trim.

### Static audit for motion timings

Anything over 200ms on a transition is a candidate for trimming. Run from the project root:

```bash
rg -n "duration:\s*[2-9][0-9]{2,}|duration:\s*[0-9]{4,}" --type tsx --type ts
```

Matches `duration: 200` and up, plus any 4+ digit duration. Doesn't catch animations declared via `Animated.spring` defaults or `withSpring` — those need a hardware feel-test.

---

## Navigation patterns

TV navigation operates on two layers:

- **Global navigation** moves between top-level sections (Home, Search, Settings). Drawer is the typical pattern.
- **Local navigation** moves within a section (Popular, New, Favorites). Tabs are the typical pattern.

Most apps combine both. Don't use tabs as primary navigation for an app with many sections — they cramp.

### Drawer (global navigation)

Left-edge menu for app-wide sections. Acts as the user's reliable reference point — they can always return to the main menu regardless of how deep they are.

```jsx
import { createDrawerNavigator } from "@react-navigation/drawer";
import { NavigationContainer } from "@react-navigation/native";

const Drawer = createDrawerNavigator();

export function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator
        screenOptions={{
          drawerType: "permanent", // TV doesn't have gestures; keep it visible
          drawerStyle: { width: 240 }, // wide enough to read at 10ft
          headerShown: false,
        }}
      >
        <Drawer.Screen name="Home" component={HomeScreen} />
        <Drawer.Screen name="Movies" component={MoviesScreen} />
        <Drawer.Screen name="TV Shows" component={TVShowsScreen} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}
```

Rules:

- 5–7 items max.
- Open/close transition under 200ms.
- Focus trapped inside while open.
- On close, focus returns to the trigger (see `navigation-and-focus.md`).

### Tabs (within-section navigation)

For switching views within a section (Popular / New / Favorites). For switching between top-level sections, use a drawer.

```jsx
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

const Tab = createBottomTabNavigator();

export function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          tabBarStyle: { height: 80 }, // larger hit target for TV
          tabBarLabelStyle: { fontSize: 22 }, // readable at 10ft
          headerShown: false,
        }}
      >
        <Tab.Screen name="Home" component={HomeScreen} />
        <Tab.Screen name="Movies" component={MoviesScreen} />
        <Tab.Screen name="TV Shows" component={TVShowsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
```

Rules:

- 3–5 tabs max.
- Current tab visually distinct (bold + underline + colour).
- Left/right switches; down enters content rows below.

### Modal / overlay

Confirmations, playback controls, detail flyouts.

```jsx
<Modal visible={open} transparent animationType="fade">
  <TVFocusGuideView trapFocusUp trapFocusDown trapFocusLeft trapFocusRight>
    <View style={styles.modalContent}>
      <Text style={styles.title}>Remove this item?</Text>
      <Pressable hasTVPreferredFocus onPress={confirm}>
        <Text>Confirm</Text>
      </Pressable>
      <Pressable onPress={cancel}>
        <Text>Cancel</Text>
      </Pressable>
    </View>
  </TVFocusGuideView>
</Modal>
```

Rules:

- Trap focus on all four sides (Vega: `FocusManager.setFocusRoot(tag, true)` — see `vega-specifics.md`).
- Restore focus to the trigger on close.
- Transition ~150ms.
- Don't stack modals.

---

## Common components

### Cards

Discrete content units (movie, show, playlist, profile). Entry points, not summaries — they say "select me to see more." Foundation of a content-focused TV interface.

```jsx
<Pressable
  onPress={() => openDetails(id)}
  style={({ focused }) => [
    styles.card,
    focused && {
      borderWidth: 2,
      borderColor: "#00D4FF",
      transform: [{ scale: 1.05 }], // 3–5% is the comfortable range
    },
  ]}
>
  <Image source={poster} style={styles.poster} />
  <Text numberOfLines={2} ellipsizeMode="tail" style={styles.title}>
    {title}
  </Text>
</Pressable>
```

Rules:

- Multi-cue focus state (border + scale + colour). Colour alone fails for color-deficient users and on washed-out displays.
- Title max 2 lines + `ellipsizeMode="tail"`.
- One secondary detail max (runtime or rating, not both).
- No metadata that only makes sense after selection.

### Rows / carousels / swimlanes

Horizontal rows of cards. Left/right moves within a row (within a category); up/down moves between rows (between categories). Signature pattern of content-heavy TV apps.

```jsx
// FlatList — for short rows. The tuning props below are FlatList-only;
// drop them when migrating to FlashList. On FlashList v1 use estimatedItemSize + getItemType;
// on FlashList v2+ drop estimatedItemSize too (deprecated) — see "Tuning notes" below.
import { FlatList } from "react-native";
import { useCallback } from "react";

function Row({ title, data, onSelect }) {
  const renderItem = useCallback(
    ({ item }) => <Card item={item} onPress={() => onSelect(item)} />,
    [onSelect]
  );

  return (
    <View>
      <Text style={styles.rowHeader}>{title}</Text>
      <FlatList
        data={data}
        horizontal
        keyExtractor={(item) => item.id}
        showsHorizontalScrollIndicator={false}
        removeClippedSubviews
        initialNumToRender={6}
        maxToRenderPerBatch={6}
        windowSize={5}
        renderItem={renderItem}
      />
    </View>
  );
}
```

```jsx
// FlashList v1 — for long, image-heavy rows. No key on Card, no useState inside Card.
// Drop FlatList tuning props (windowSize, initialNumToRender, etc.) — they don't apply.
// On FlashList v2+, drop estimatedItemSize too (deprecated). See "Tuning notes" below.
import { FlashList } from "@shopify/flash-list";
import { useCallback } from "react";

function Row({ title, data, onSelect }) {
  const renderItem = useCallback(
    ({ item }) => <Card item={item} onPress={() => onSelect(item)} />,
    [onSelect]
  );

  return (
    <View>
      <Text style={styles.rowHeader}>{title}</Text>
      <FlashList
        data={data}
        horizontal
        showsHorizontalScrollIndicator={false}
        estimatedItemSize={220}
        renderItem={renderItem}
      />
    </View>
  );
}
```

Rules:

- Always virtualise. A swimlane with hundreds of cards in a `ScrollView` degrades perf and balloons the focus tree.
- Auto-scroll focused card into view, smoothly (animate the scroll, don't snap). `FlatList` defaults with focusable children work for most cases; for tighter control, call `scrollToIndex` with `animated: true` on focus.
- Peek the next card: size and position cards so a sliver of the next off-screen item is always visible. Signals "more content here" and reduces dead-ends at the row edge.
- Header label stays visible when a card has focus.
- Vertical spacing between rows: ~1.5× card height.

### Picking a list library — present these as options

Three libraries the agent should know about. Surface them as a choice; don't pick silently. For Vega-specific package names and runtime constraints, see [`vega-specifics.md`](./vega-specifics.md).

| Library                  | Package                   | When to recommend                                                                                                                                                                                                                                                                                                     |
| ------------------------ | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FlatList`               | `react-native` (built-in) | Short / static lists (~20–100 items). The agent will see this all over existing TV codebases — it's what most apps reach for first. Tunable via `getItemLayout` for fixed-height rows.                                                                                                                                |
| `FlashList` (Shopify)    | `@shopify/flash-list`     | Recommended for >100 items, image-heavy swimlanes, or anything scrolling more than a screen or two. Recycles cells instead of creating new ones; lower memory and smoother scroll on streaming sticks. Drop-in for `FlatList` (same `data` / `renderItem` API).                                                       |
| `LegendList` (LegendApp) | `@legendapp/list`         | Newer, drop-in replacement for both `FlatList` and `FlashList`. Vendor claims faster than `FlashList` in most scenarios — no public TV-specific benchmark. Pure TypeScript, no native deps. Adds `maintainScrollAtEnd`, `maintainVisibleContentPosition`, bidirectional infinite scroll, native dynamic-size support. |

For long catalogues, image-heavy rows, or anything scrolling beyond a screen or two, default to `FlashList` or `LegendList` over `FlatList`.

#### Tuning notes

The three APIs are not fully interchangeable for tuning props.

**`FlatList` tuning props that do not transfer to `FlashList`:** `windowSize`, `getItemLayout`, `initialNumToRender`, `maxToRenderPerBatch`, `updateCellsBatchingPeriod`. `removeClippedSubviews` is a `FlatList` perf prop too; drop it when migrating to be safe.

For fixed-height items, `getItemLayout` lets `FlatList` skip measurement and improves scroll perf:

```jsx
const ITEM_HEIGHT = 200;

<FlatList
  data={data}
  renderItem={renderItem}
  getItemLayout={(_, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>;
```

**`FlashList`** — drop the props above. **Check the installed major version before recommending props:**

- **v1**: `estimatedItemSize` is part of the optimisation guidance; set it to a realistic average item height.
- **v2+**: `estimatedItemSize`, `estimatedListSize`, and `estimatedFirstItemOffset` are deprecated and ignored — do not flag them as missing. See <https://shopify.github.io/flash-list/docs/v2-changes/>.
- `getItemType` — when cell components differ structurally between rows; helps recycling pick the right pool. Example:

  ```jsx
  <FlashList
    data={items}
    renderItem={({ item }) => {
      if (item.type === "header") return <Header {...item} />;
      if (item.type === "card") return <Card {...item} />;
      return <Spacer {...item} />;
    }}
    getItemType={(item) => item.type}
  />
  ```

- Don't put a `key` prop on item components or their children. Recycling reuses cells; a stable key fights recycling. For `.map()` calls inside an item, use FlashList's `useMappingHelper` hook to generate keys that play well with recycling.
- Avoid `useState` inside recycled items — state can carry over from the previous item the cell rendered. The official replacement is `useRecyclingState` (accepts a deps array and an optional reset callback). `useLayoutState` is also available for state that should reset on recycle.
- Define `renderItem` outside the component (or with `useCallback`); inline functions cause re-renders.

**`LegendList`** — drop both sets of tuning props and configure with:

- `recycleItems={true}` to enable recycling (off by default). Same caveat as `FlashList`: if recycling is on, don't keep local state inside item components.
- `maintainVisibleContentPosition` for lists where data can change beneath the user (e.g. live updates, prepended items).
- `maintainScrollAtEnd` for chat-style lists; pair with `alignItemsAtEnd` to align content to the bottom when the list is shorter than the viewport.
- Native dynamic-size handling — no `estimatedItemSize` equivalent needed.
- `getItemType` is not yet supported in `LegendList` (per its README roadmap); use `FlashList` if mixed cell shapes need recycling pools.
- Imports from `@legendapp/list/react-native`.

### Hero header

Large visual at the top of a screen. Anchors the screen, sets the tone, gives focus a clear starting point, and creates breathing room before the denser rows below.

```jsx
function Hero({ feature }) {
  return (
    <View style={styles.hero}>
      <Image source={feature.backdrop} style={StyleSheet.absoluteFill} />
      <LinearGradient
        colors={["transparent", "rgba(0,0,0,0.85)"]}
        style={StyleSheet.absoluteFill}
      />
      <View style={styles.heroContent}>
        <Text style={styles.heroTitle}>{feature.title}</Text>
        <Text numberOfLines={2} style={styles.heroSummary}>
          {feature.summary}
        </Text>
        <Pressable hasTVPreferredFocus onPress={() => play(feature)}>
          <Text style={styles.heroCta}>Play</Text>
        </Pressable>
      </View>
    </View>
  );
}
```

Rules:

- One feature, one primary CTA (`Play`, `Resume`, `More info`).
- Gradient or blur overlay so the title remains readable across any backdrop.
- `hasTVPreferredFocus` on the CTA, not on a decorative element.

### Buttons

Buttons appear less often on TV than on mobile or web — most actions happen via card focus. When they do appear, prioritise clarity over visual style.

```jsx
<Pressable
  onPress={onPress}
  style={({ focused }) => [
    styles.button,
    focused && {
      backgroundColor: "#FFF",
      borderColor: "#00D4FF",
      transform: [{ scale: 1.04 }],
    },
  ]}
>
  <Text style={styles.buttonLabel}>{label}</Text>
</Pressable>
```

Rules:

- Short verb labels (`Play`, `Retry`, `Cancel`).
- Group related actions with consistent spacing (e.g. Play next to More Info).
- Primary action visually heavier than secondary (size + colour).

### Overlays (playback controls, pause menus)

Distinct from modals: overlays are tied to the content beneath them (e.g. video controls over a playing stream), not separate surfaces.

- Fade in quickly on user input; fade out after a short inactivity period.
- Dim the content beneath, but don't hide it — the user should still feel connected to what's playing.
- Predictable focus order within the overlay (left-to-right through controls).
- Don't persist overlays: they exist for the moment of interaction, not as standing UI.

### Details / info panels

Extended descriptions, cast lists, related recommendations. Slide in or overlay smoothly to maintain continuity, rather than replacing the entire screen.

- Back button must return the user to where they started, not a default state.
- Don't lose scroll position or focus on the row that triggered the panel.
- Use a full-screen view only when the content genuinely requires it (rare).

---

## Layout and safe zones

### Overscan

Many TVs crop the outer 5–10% of the layout. Critical content (text, logos, buttons, focus indicators) must sit inside the safe zone. Background images and hero backdrops can extend to the screen edge; UI on top of them cannot.

```jsx
import { StyleSheet, View } from "react-native";

const SAFE_ZONE_INSET = "5%";

export function SafeZone({ children, style }) {
  return <View style={[styles.zone, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  zone: {
    flex: 1,
    paddingTop: SAFE_ZONE_INSET,
    paddingBottom: SAFE_ZONE_INSET,
    paddingLeft: SAFE_ZONE_INSET,
    paddingRight: SAFE_ZONE_INSET,
  },
});
```

**Watch out for:** `position: 'absolute'` with `top: 0` / `left: 0` / `right: 0` / `bottom: 0` on interactive content. Full-bleed positioning of buttons or text guarantees overscan crop on TVs that apply it. Backgrounds are fine; UI is not.

### Multiple screen sizes

TVs range 32"–85"+, with 720p / 1080p / 4K, and 16:9 (rarely 21:9).

- Use relative units (`%`, `flex`, `Dimensions.get('window')`-derived values), not fixed pixel widths.
- Anchor regions via flex layout, not absolute coordinates.
- Don't position CTAs near corners — overscan crops them.
- Hard-coded `width: 1920` / `height: 1080` breaks on every non-1080p screen.

### Aspect ratios

Design for 16:9; verify the layout does not clip or push CTAs off-screen at 21:9. Background compositions stay balanced when cropped.

---

## Hand off to the human reviewer

**Run the static helper first:** `node references/scripts/audit.js src --only layout`. Catches grep-able layout issues (`ScrollView` with `.map`, `FlashList` with FlatList-only tuning props, inline `renderItem`, hard-coded TV resolutions). It's a helper, not a full review — most layout problems require hardware and viewing distance to surface.

The remaining checks need a real device, the platform remote, and viewing distance:

- UI fits within the 5% safe zone; focus state remains visible at the screen edges. *(human — hardware)*
- No clipping at 16:9 or 21:9; CTAs stay on-screen at both ratios. *(human — hardware)*
- Overlays render correctly on HD and 4K. *(human — hardware)*
- Drawer / modal / page transitions measured under 200ms. `Animated.spring` defaults need a feel-test; the static duration grep doesn't catch them. *(human — hardware)*
- At 8–10ft with the platform remote: can the user find and play content? Anything sluggish, unclear, or surprising? *(human — couch test)*
- Lights on and lights off. Contrast and focus cues that work in one fail in the other. *(human — couch test)*
