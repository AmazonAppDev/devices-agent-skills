# The 10-Foot Experience

Design principles for TV interfaces viewed from across the room with a remote control.

## Designing for Distance

- Bold shapes and simple icons only — fine detail disappears at 10 feet.
- Generous spacing so every element stands out. Dense layouts fail on TV.
- Strong contrast and visual hierarchy over decorative elements.
- Interface must be readable at a glance; important info immediately obvious.

## Remote Interaction Model

Most remotes provide: directional arrows, select, back, play/pause. Design for these constraints:

- **Select** = confirm/activate. **Back** = return to previous screen.
- Every button press produces an immediate visual response (highlight, scale change, or pulse).
- Map actions to predictable buttons consistently across all screens.
- If pressing left opens the drawer from one screen, it must do the same from all screens.

## Directional Navigation Principles

- Left/right for movement **within** rows. Up/down for movement **between** sections.
- Focus should flow predictably — no dead ends, no surprising jumps.
- From home screen to first "Play" action: always a clear, logical path.
- When overlays/modals appear, trap focus inside until dismissed.

## Shared Screen Considerations

TVs are shared among family/roommates. This changes UI decisions:

- Avoid displaying sensitive/personal info unless necessary.
- Make profile/account switching clearly accessible.
- Confirm voice input text before submitting (everyone in the room can see it).
- Overlays/menus: visible long enough to serve purpose, then dismiss. Don't compete with content.

## Feedback, Motion, and Rhythm

TVs have inherent input delay. Immediate visual acknowledgment is critical.

- Every button press acknowledged instantly through a visual cue.
- Animation serves direction or focus changes — never pure decoration.
- If an animation delays interaction or feels sluggish, it's too long.
- Smooth execution matters more than elaborate effects.

**Verify before ship:** animations stay under 200ms (drawers, modals, focus transitions) and there's no perceptible input delay between a remote press and a visible response. If you can press a button and count "one" before anything happens, it's already too slow — TV input pipelines add their own latency on top of whatever you measure on a dev machine.

## Couch Sanity Checks

The mechanical checks (typography sizes, contrast, safe zones, focus behavior, animation timing) are covered in their respective reference files as `**Verify before ship:**` notes. But mechanical pass alone isn't enough — TV apps surface issues only when used the way real users use them.

**Verify before ship: do a real couch test.** Sit at actual viewing distance (8-10 feet), use the actual remote control for the platform, and run through the primary flows. Don't substitute a desk monitor with a keyboard — input cadence, text legibility, and focus visibility all behave differently with a remote in hand and the screen across the room. Two qualitative questions only this test can answer:

- Can you find and play content easily? (Discovery test — does the layout guide you toward the goal?)
- Is anything awkward? Simplify until navigation feels invisible.
