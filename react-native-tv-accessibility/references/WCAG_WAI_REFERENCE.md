# WCAG and WAI Reference

Use this reference to map accessibility findings to shared standards after selecting the correct app surface.

Primary sources:
- WCAG 2.2 Recommendation: https://w3.org/TR/2024/REC-WCAG22-20241212
- WCAG 2.2 Understanding: https://w3.org/WAI/WCAG22/Understanding
- WAI-ARIA Authoring Practices Guide: https://www.w3.org/WAI/ARIA/apg/

## Conformance Target

Default to WCAG 2.2 Level A and AA unless the user or app release criteria specify otherwise.

WCAG 2.2 is organized around four principles:
- **Perceivable**: users can perceive content, alternatives, captions, structure, contrast, and text.
- **Operable**: users can operate controls with keyboard/remote, enough time, no traps, visible focus, and predictable navigation.
- **Understandable**: users can understand content, instructions, errors, labels, and interactions.
- **Robust**: content exposes name, role, value, and state in ways assistive technologies can consume.

## High-Value Success Criteria for TV Apps

Prioritize these for TV/WebView/RN reviews:
- 1.1.1 Non-text Content: images, icons, thumbnails, badges, and controls need text alternatives.
- 1.2.2 Captions (Prerecorded): prerecorded synchronized media needs captions.
- 1.2.4 Captions (Live): live synchronized media needs captions.
- 1.3.1 Info and Relationships: structure and relationships must be programmatically available.
- 1.4.1 Use of Color: do not rely on color alone.
- 1.4.3 Contrast (Minimum): normal text needs 4.5:1; large text needs 3:1.
- 1.4.10 Reflow: content should remain usable when scaled or constrained.
- 1.4.11 Non-text Contrast: focus indicators and UI components need sufficient contrast.
- 2.1.1 Keyboard: remote/keyboard users need equivalent operation.
- 2.1.2 No Keyboard Trap: users must be able to move away from focused controls.
- 2.4.3 Focus Order: focus order must preserve meaning and operability.
- 2.4.7 Focus Visible: keyboard/remote focus must be visible.
- 2.4.11 Focus Not Obscured (Minimum): focused controls should not be hidden by overlays.
- 2.5.8 Target Size (Minimum): pointer targets should meet minimum sizing where applicable.
- 3.2.1 On Focus and 3.2.2 On Input: focus/input should not trigger surprising context changes.
- 3.3.1 Error Identification and 3.3.2 Labels or Instructions: forms and settings need clear errors and instructions.
- 4.1.2 Name, Role, Value: custom controls must expose correct role, name, state, and value.
- 4.1.3 Status Messages: status updates must be announced without moving focus when appropriate.

## WAI-ARIA APG Usage

Use APG patterns for WebView custom widgets and HTML-like app surfaces:
- Dialogs: modal role, title, focus trap, Escape/Back behavior, and focus return.
- Buttons and toggles: name, role, pressed/checked state, Enter/Select activation.
- Tabs: tablist/tab/tabpanel semantics and arrow-key behavior.
- Menus/listboxes: clear ownership, active item, arrow navigation, selection state.
- Carousels: pause/stop controls, accessible names, and predictable navigation.
- Grids: row/column navigation, selected/current state, and cell names.

For native Vega RN, use APG conceptually for roles, names, states, and keyboard patterns, but implement with React Native for Vega-supported props and components.

## Severity Mapping

- **Critical**: blocks a user from completing a flow, such as unreachable controls, missing accessible names on primary actions, no captions for required media, trapped focus, or invisible focus.
- **Serious**: creates major friction, such as wrong role/state, poor contrast, duplicate announcements, confusing focus order, or missing error association.
- **Minor**: improves clarity or consistency, such as overly verbose labels, inconsistent hints, or optional orientation copy.

## Reporting Format

Use this format for findings:

```markdown
Severity: Critical | Serious | Minor
Surface: Vega WebView | Native Vega RN | Mixed
Location: file/component/screen
Issue: What fails
Impact: Which user is affected and how
Reference: WCAG/APG/Vega/RN source
Fix: Concrete code or implementation change
Verification: How to prove the fix works
```
