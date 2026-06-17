---
title: Typography and Color
tags: typography, font-size, line-height, letter-spacing, contrast, color, palette, hdr, ambient-light, multi-cue-focus, amazon-ember
---

# Typography and Color

Font sizes, line height, contrast ratios, and palette choices calibrated for 10ft TV viewing. Mobile defaults fail on TV — this file is the source of "what numbers to use."

---

## Sizes

TV text needs to be 50–80% larger than its mobile equivalent. Starting points; adapt per brand and verify on hardware.

| Style   | Mobile | TV  | Use                      |
| ------- | ------ | --- | ------------------------ |
| Caption | 12     | 20  | Metadata, labels, tags   |
| Body    | 16     | 24  | Descriptions, paragraphs |
| Button  | 14     | 22  | Interactive CTAs         |
| Heading | 20     | 32  | Section titles           |
| Title   | 28     | 48  | Page titles, hero text   |
| Display | 36     | 64  | Large promotional text   |

If font sizes are scattered ad-hoc through stylesheets, recommend a token set:

```ts
// styles/tvTypography.ts
import { StyleSheet } from "react-native";

export const tvTypography = StyleSheet.create({
  caption: { fontSize: 20, lineHeight: 26, fontWeight: "400" },
  body: { fontSize: 24, lineHeight: 32, fontWeight: "400" },
  button: { fontSize: 22, lineHeight: 28, fontWeight: "600" },
  heading: { fontSize: 32, lineHeight: 40, fontWeight: "600" },
  title: { fontSize: 48, lineHeight: 56, fontWeight: "700" },
  display: { fontSize: 64, lineHeight: 72, fontWeight: "700" },
});
```

**Watch out for:** any `fontSize` below 20 on a screen the user reads. `fontSize: 16` looks fine on a desk monitor at 60cm and unreadable at 10ft.

---

## Line height and letter spacing

Line height is a _multiplier_ of font size.

| Context                | Line height | Letter spacing | Notes                                        |
| ---------------------- | ----------- | -------------- | -------------------------------------------- |
| Paragraphs / long-form | 1.4×        | +0.4           | Reading                                      |
| Menus / nav items      | 1.2×        | +0.5           | Scanning                                     |
| Display titles (40+)   | 1.15×       | -0.4 to -0.8   | Tighten; large sizes amplify default spacing |

Negative tracking on display sizes prevents airy gaps. Don't apply below ~40px.

---

## Platform typefaces

Use the platform system font unless the brand requires otherwise.

| Platform                | System font                                  |
| ----------------------- | -------------------------------------------- |
| tvOS                    | San Francisco (SF Pro Display / SF Pro Text) |
| Android TV              | Roboto                                       |
| Fire TV / Vega          | Amazon Ember                                 |
| Cross-platform fallback | Inter, Noto Sans                             |

Avoid `fontWeight: '100'` or `'200'`. They shimmer on LCDs and bloom on OLEDs.

---

## Text rendering rules

- Tile titles: `numberOfLines={2}` + `ellipsizeMode="tail"`. Without these, titles overflow into siblings.
- Sentence case for body / captions. ALL CAPS reduces word-shape recognition.
- Long localised titles: marquee on focus only, never by default.

### Text over images / video

Plain text vanishes against complex backgrounds. Use shadow + a dark gradient or blur underlay:

```ts
const readableOnImage = {
  color: "#FFF",
  textShadowColor: "rgba(0,0,0,0.35)",
  textShadowOffset: { width: 0, height: 1 },
  textShadowRadius: 2,
};
```

For subtitles or persistent text over video, combine shadow with a low-opacity stroke. Cap `textShadowRadius` at ~3 — beyond that, text turns smeary.

---

## Color and contrast

### Contrast ratios

| UI role                                        | Minimum ratio                                           |
| ---------------------------------------------- | ------------------------------------------------------- |
| Normal text                                    | 4.5:1                                                   |
| Core UI (menus, buttons, captions over images) | 7:1                                                     |
| Focus indicator                                | as high as possible (e.g. `#00D4FF` is 11.3:1 vs black) |

Pure `#FFFFFF` on `#000000` is 21:1 but causes eye fatigue on sustained reading and HDR bloom. Use near-white (`#E5E5E7`) and near-black (`#1a1a1a`) as base; reserve extremes for short-lived highlights.

### Recommended palette (with computed ratios)

| Purpose        | Value     | vs `#000` | vs `#1a1a1a` |
| -------------- | --------- | --------- | ------------ |
| Primary text   | `#FFFFFF` | 21:1      | 17.8:1       |
| Secondary text | `#E5E5E7` | 18.5:1    | 15.7:1       |
| Tertiary text  | `#A1A1AA` | 8.6:1     | 7.3:1        |
| Disabled text  | `#6B7280` | 4.2:1     | 3.6:1        |
| Primary accent | `#007AFF` | 8.2:1     | 7.0:1        |
| Focus border   | `#00D4FF` | 11.3:1    | 9.6:1        |
| Success        | `#34C759` | 9.8:1     | 8.3:1        |
| Warning        | `#FF9500` | 7.1:1     | 6.0:1        |
| Danger         | `#FF3B30` | 5.9:1     | 5.0:1        |

### Multi-cue focus state

Every focus indicator combines colour + border/outline + scale. Colour alone fails for color-deficient users and on washed-out displays.

```jsx
<Pressable
  style={({ focused }) => ({
    backgroundColor: focused ? '#FFF' : '#222',
    borderWidth: focused ? 2 : 0,
    borderColor: '#00D4FF',
    transform: [{ scale: focused ? 1.04 : 1 }],
  })}
>
```

**Watch out for:** focused-state styles changing only `backgroundColor` or only colour. Without a border or scale change, low-contrast TVs and color-deficient users can't tell what's selected.

---

## HDR considerations

- Cap UI whites at 80–90% luminance. Pure `#FFFFFF` for persistent text causes HDR glow.
- Cap focus-glow / selection-chip intensity to prevent blooming against HDR content.
- Test SDR and HDR. Ship a palette that holds in both.

If hardware testing isn't available, render screens over HDR backdrop content and confirm UI doesn't disappear into highlights.

---

## Ambient light

Three environments and starting palettes:

| Environment | Background | Primary text | Secondary text | Accent    | Min contrast |
| ----------- | ---------- | ------------ | -------------- | --------- | ------------ |
| Bright room | `#000000`  | `#FFFFFF`    | `#E5E5E7`      | `#007AFF` | 7:1          |
| Dim room    | `#1a1a1a`  | `#E5E5E7`    | `#B3B3B3`      | `#5AC8FA` | 4.5:1        |
| Dark room   | `#2a2a2a`  | `#D1D1D6`    | `#8E8E93`      | `#64D2FF` | 3:1          |

For apps with manual "night mode" or system-driven theming, these three rows are starting points for the three modes.

---

## Hand off to the human reviewer

**Run the static helper first:** `node references/scripts/audit.js src --only typography`. Catches grep-able typography issues (small font sizes, ultra-thin weights, white-on-black, ALL CAPS, missing `numberOfLines`, large `textShadowRadius`, implausible `lineHeight`, negative tracking on small fonts, WCAG contrast below 4.5:1 for same-object pairs). It's a helper, not a full review — debug overlays, button labels, and test fixtures can legitimately violate the rules; inherited / cross-component contrast pairs need hardware spot-checks.

The remaining checks need hardware, distance, and human eyes. Surface to the user when the review is complete:

- Spot-check inherited / cross-component text-on-background pairs on hardware. The audit only catches pairs in the same style object; styles applied through composition need an eyes-on review. TV gamma and ambient glare also push borderline pairs below threshold. _(human — hardware)_
- Toggle HDR on a supporting TV; confirm whites don't bloom and focus indicators remain visible. _(human — hardware)_
- View screens at 10ft with lights on **and** lights off. Contrast that works in one condition fails in the other. Leaning forward = type or contrast is wrong. _(human — couch test)_
