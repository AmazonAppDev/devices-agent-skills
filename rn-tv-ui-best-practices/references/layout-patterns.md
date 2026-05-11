# Layout Patterns and Common Components

Structural patterns for TV interfaces: navigation, components, safe zones, and spacing.

## Why Structure Matters

Layout patterns reduce cognitive effort. Users focus on content rather than figuring out navigation. Every button press on a remote takes deliberate time, so predictability is a valuable feature.

A well-designed layout provides three things:
1. **Orientation**: Where am I?
2. **Context**: What can I do here?
3. **Momentum**: Where can I go next?

These patterns also create shared vocabulary for teams — designers, developers, and testers can communicate using the same terms (hero, swimlane, drawer, focus trap), turning complex interfaces into manageable, reusable systems.

## Gotchas

- Many TVs still apply **overscan** (5-10% cropped from edges). Keep all interactive elements inside a 5-10% safe zone margin. Only backgrounds/hero images extend to edge.
- Drawer open/close transitions must complete in **under 200ms**. Modal transitions ~150ms. Longer = sluggish.

## Critical Values (Guidelines)

Recommended starting points — adapt to your app's specific needs and user testing.

```
Safe Zone: 5-10% margin on all sides
Card Focus Scale: 3-5% larger
Row Vertical Padding: 1.5x card height
Drawer Items: 5-7 maximum
Tabs: 3-5 maximum
Animation Timing: Drawer < 200ms | Modal ~150ms
```

## Navigation Patterns

### Drawer Navigation (Global)

Left-edge menu for main sections. Acts as the app's structural backbone.

**Behavior:**
- Opens when user presses left from leftmost focusable area (or menu/back shortcut).
- Dims the rest of the screen slightly to signal context shift.
- Focus trapped inside until user exits or selects.
- On close, restore focus to previously active element.

**Rules:**
- 5-7 items maximum.
- Clear labels (icons + text for clarity).
- Open/close transition: under 200ms.

```jsx
<Drawer isOpen={open}>
  <MenuItem label="Home" onPress={() => navigate('home')} />
  <MenuItem label="Movies" onPress={() => navigate('movies')} />
  <MenuItem label="Settings" onPress={() => navigate('settings')} />
</Drawer>
```

### Tab Navigation (Local)

Organizes content within a single section (not between sections). Place beneath hero banner or above first content row.

**Rules:**
- 3-5 tabs maximum.
- Current tab visually obvious (bold, underline, highlight).
- Left/right to switch tabs, down to enter content rows below.
- Tabs as primary navigation only works for apps with limited sections. Complex apps need a drawer.

```jsx
<Tabs>
  <Tab label="Popular" onFocus={() => setCategory('popular')} />
  <Tab label="New" onFocus={() => setCategory('new')} />
  <Tab label="Favorites" onFocus={() => setCategory('favorites')} />
</Tabs>
```

### Modal Navigation

Temporary focused interruptions (confirmations, playback controls, detail views).

**Rules:**
- Trap focus inside. Dim/blur background.
- Restore focus to triggering element on close.
- Transitions ~150ms. Never stack multiple modals.
- Consistent placement: fade or scale from center.

```jsx
<Modal visible={showDetails}>
  <Text>Are you sure you want to remove this item?</Text>
  <Button label="Cancel" onPress={() => setShowDetails(false)} />
  <Button label="Confirm" onPress={handleConfirm} />
</Modal>
```

### Navigation Predictability

- Consistent directional logic across all screens.
- Always provide a visible focus state.
- Never move focus off-screen without scrolling the new element into view.
- Keep focusable element count reasonable — don't force excessive button presses.

## Common Components

### Cards and Content Tiles

Each card = one piece of content. Entry points, not summaries.

- Focus feedback: subtle scaling (3-5%), glow or drop shadow for depth.
- Include: title, thumbnail, one secondary detail (runtime or badge).
- Adequate spacing so focus indicators don't overlap adjacent cards.
- Don't cram too much info — show detail on focus or in a dedicated view.

```jsx
<Card
  image={poster}
  title="The Great Adventure"
  onFocus={() => setHighlight(id)}
  onPress={() => openDetails(id)}
/>
```

### Rows / Carousels / Swimlanes

Horizontal rows of cards — the signature streaming app pattern.

- Render only visible items (FlatList or VirtualizedList).
- Left/right within a row, up/down between rows.
- Auto-scroll when focus reaches row edge.
- Label each row with headers ("Recommended", "New Releases") visible even when card has focus.
- Resist overfilling — fewer distinct categories > overwhelming options.

```jsx
<Row title="Recommended for You">
  {data.map((item) => <Card key={item.id} {...item} />)}
</Row>
```

### Hero Headers

Large visual at top of screen. Anchors attention, provides a starting point for focus.

- Feature a single piece of content (show, event, collection).
- Strong composition — fills space naturally, not cropped.
- Text readable against backgrounds (use gradients or blurs).
- Single primary action: "Play", "Resume", or "More Info".
- Smooth transition to first content row (subtle fades or parallax).

### Buttons and Overlays

- Focused buttons: contrast, outlines, or subtle scaling.
- Group related actions ("Play" + "More Info") with consistent spacing.
- Labels: short verbs ("Play", "Retry", "Cancel").
- Overlays fade in quickly, fade out after inactivity period.
- Predictable focus order within overlays (left to right).
- Dim content beneath overlays but don't hide completely.

### Details and Info Panels

- Slide in or overlay smoothly — maintain continuity, don't replace entire screen.
- Back button always returns to where user started (not a default state).

## Layout and Safe Zones

### Overscan

Many TVs still crop the outer 5-10% of the layout.

- **Essential elements** (text, logos, buttons, nav): inside 5-10% safe zone margin on all sides.
- **Backgrounds and hero images**: can extend to screen edge.
- Use gridlines or invisible bounding boxes during development to visualize safe boundaries.

**Verify before ship:** every interactive or text element sits inside the 5-10% safe zone on all four edges. Easiest check is to overlay a debug rectangle at 5% inset and confirm nothing critical pokes outside it.

### Multiple Screen Sizes

TVs range from 32" to 85"+. Never rely on fixed pixel values.

- Use relative units (percentages, viewport-relative) for spacing and positioning.
- Anchor interface regions to screen edges (top, left, right), not absolute coordinates.
- Keep critical content centered — peripheral areas are less reliable.
- Test on multiple display modes (Standard, Cinema, Game, HDR).

### Aspect Ratios

- Design around 16:9 base grid, adaptable to 21:9 without breaking.
- Don't position titles or CTAs close to corners.
- For backgrounds, choose compositions that stay balanced when cropped.

**Verify before ship:** render the screen at both 16:9 and 21:9 and confirm nothing clips, reflows awkwardly, or pushes a CTA off-screen. Ultrawide displays are a small share of the install base but they expose layout assumptions that look fine at 16:9.

### Spacing

- Align to a grid system (12-column or 8-column).
- Vertical rhythm between rows: 1.5x card height for padding.
- Invisible baselines for text/components keep focus transitions smooth.
- Don't overfill the screen. TV interfaces work best when calm, not dense.

## Layout-Specific Checks

A few layout-specific things that only matter once the structural patterns above are in place:

- Overlays scale correctly on both HD and 4K (test at native and upscaled output).
- Test in real living room conditions: lights on/off, varying distances. TV environments differ enough from a desk monitor that surprises only surface there.
