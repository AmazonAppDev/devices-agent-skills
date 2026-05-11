# Typography and Color for TV Displays

TV-specific typography and color guidelines. What works on phones fails on TV due to distance, panel tech, ambient light, and OS rendering.

## Gotchas

- TV text must be **50-80% larger** than mobile equivalents. A 16px body on mobile = 24px on TV. Anything smaller is unreadable from the couch.
- Avoid pure `#FFFFFF` on pure `#000000` for entire screens — causes eye fatigue and HDR glow. Use near-white (#E5E5E7) and near-black (#1a1a1a).
- Focus contrast must use **multi-cue**: color + border/outline + mild scale. Color alone fails for color-deficient users and washed-out displays.

## Typography

### Critical Values (Guidelines)

These are recommended starting points based on visual acuity research for living room environments. Adapt to your app's brand and user testing results.

```
Typography (minimum TV sizes):
  Body: 24px | Caption: 20px | Button: 22px
  Heading: 32px | Title: 48px | Display: 64px

Contrast:
  Normal text: >= 4.5:1
  Core UI (menus, buttons, captions): >= 7:1
  Focus border: #00D4FF (11.3:1 vs black)
```

### Recommended Font Sizes

TV text should be 50-80% larger than mobile equivalents. These are guidelines based on visual acuity research for living room environments — use as starting points and adjust based on your app's design and user testing:

| Text Style | Mobile | TV | Use Case |
|---|---|---|---|
| Body | 16px | 24px | Descriptions, paragraphs |
| Caption | 12px | 20px | Metadata, labels, tags |
| Button | 14px | 22px | Interactive elements, CTAs |
| Heading | 20px | 32px | Section titles, category names |
| Title | 28px | 48px | Page titles, hero text |
| Display | 36px | 64px | Large promotional text |

```js
const tvTypography = StyleSheet.create({
  body: { fontSize: 24, lineHeight: 32, fontWeight: '400' },
  button: { fontSize: 22, lineHeight: 28, fontWeight: '600' },
  caption: { fontSize: 20, lineHeight: 26, fontWeight: '400' },
  heading: { fontSize: 32, lineHeight: 40, fontWeight: '600' },
  title: { fontSize: 48, lineHeight: 56, fontWeight: '700' },
});
```

**Verify before ship:** every text style on screen lands at >= 20px (captions) and >= 24px (body). Anything smaller is a regression — a single 16px label slipping through is the kind of thing only catches at couch distance, so audit explicitly rather than relying on a quick scan.

### Platform Typefaces

Use the platform's optimized system font:
- **tvOS**: San Francisco (SF Pro Display / SF Pro Text)
- **Android TV / Fire TV**: Roboto
- **Fallbacks / multi-script**: Inter, Noto Sans

### Line and Character Spacing

Line height values are **multipliers** of font size (e.g., 1.4x means line-height = 1.4 × fontSize).

| Context | Line Height | Letter Spacing | Use |
|---|---|---|---|
| Content (paragraphs) | 1.4x | +0.4px | Long-form reading |
| Navigation (menus) | 1.2x | +0.5px | Menu items, scanning |
| Display (large text) | 1.15x | -0.4px to -0.8px | Hero text, titles |

Negative tracking for large titles: huge sizes amplify default spacing, so tighten slightly to avoid airy gaps.

### Text Rendering Rules

- Sentence case over ALL CAPS for body/captions (caps reduce word shape recognition).
- Tile titles: max 2 lines + `ellipsizeMode="tail"`.
- Avoid ultra-light/ultra-thin weights — shimmer on LCDs, bloom on OLEDs.
- For long localized titles: gentle marquee on focus only, never by default.

### Text Over Images

Text can vanish against complex backgrounds. Use:

```js
const readableOnImage = {
  color: '#FFF',
  textShadowColor: 'rgba(0,0,0,0.35)',
  textShadowOffset: { width: 0, height: 1 },
  textShadowRadius: 2,
};
```

For subtitles/over-video UI: combine shadow + thin stroke outline at low opacity. Don't crank shadow blur.

## Color and Contrast

### Contrast Ratios

- Normal text: >= 4.5:1
- Core UI (menus, buttons, captions over images): >= 7:1
- Avoid pure #FFFFFF on #000000 for entire screens (eye fatigue, HDR glow).
- Use near-white and near-black for base UI; reserve extremes for short-lived highlights.
- Focus indicators must use **multi-cue**: color + border/outline + mild scale.

**Verify before ship:** spot-check every text-on-background pair against these ratios (4.5:1 normal, 7:1 core UI). Don't trust the design comp — TV gamma and ambient glare push borderline pairs below threshold once the app actually renders on hardware.

### HDR Considerations

- Keep UI whites around 80-90% luminance; avoid hard #FFFFFF for persistent text.
- Cap highlight intensity (focus glow, selection chips) to prevent blooming against HDR content.
- Test both SDR and HDR modes; ship a palette that doesn't collapse in either.

### Ambient Light Adaptation

| Environment | Background | Primary Text | Secondary Text | Accent | Min Contrast |
|---|---|---|---|---|---|
| Bright room | #000000 | #FFFFFF | #E5E5E7 | #007AFF | 7:1 |
| Dim room | #1a1a1a | #E5E5E7 | #B3B3B3 | #5AC8FA | 4.5:1 |
| Dark room | #2a2a2a | #D1D1D6 | #8E8E93 | #64D2FF | 3:1 |

### Color Palette with Contrast Ratios

| Purpose | Value | vs Black | vs #1a1a1a | Use Case |
|---|---|---|---|---|
| Primary text | #FFFFFF | 21:1 | 17.8:1 | Body, headings, critical info |
| Secondary text | #E5E5E7 | 18.5:1 | 15.7:1 | Labels, metadata |
| Tertiary text | #A1A1AA | 8.6:1 | 7.3:1 | Timestamps, auxiliary |
| Disabled text | #6B7280 | 4.2:1 | 3.6:1 | Inactive (use sparingly) |
| Primary accent | #007AFF | 8.2:1 | 7.0:1 | Links, CTAs, selected states |
| Focus border | #00D4FF | 11.3:1 | 9.6:1 | Focus indicators |
| Success | #34C759 | 9.8:1 | 8.3:1 | Confirmations |
| Warning | #FF9500 | 7.1:1 | 6.0:1 | Warnings |
| Danger | #FF3B30 | 5.9:1 | 5.0:1 | Errors, destructive actions |
