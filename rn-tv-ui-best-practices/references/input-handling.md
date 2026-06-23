---
title: Input Handling
tags: remote, d-pad, rcu, select, back, play, pause, voice, mic, textinput, keyboard, keyboardtype, securetextentry, search, login, password, dictation, qr-auth, companion-app, usetveventhandler
---

# Input Handling

Remote button vocabulary, expected app behaviour per button, and patterns for `TextInput` (system keyboard, custom keyboard, voice, QR auth).

> **Vega:** `useTVEventHandler` is observe-only and imports from `@amazon-devices/react-native-kepler`. `manifest.toml` must declare `com.amazon.inputd.service` or no events fire. See [`vega-specifics.md`](./vega-specifics.md).
>
> **Vega:** `manifest.toml` must also include `[[wants.service]] id = "com.amazon.inputmethod.service"` for the system keyboard to appear when a `TextInput` gains focus. Without it, the input accepts focus but no keyboard surfaces — silently. See [`vega-specifics.md`](./vega-specifics.md).

---

## Remote interaction model

Expected behaviours, consistent across every screen:

- Select on a card opens it.
- Back closes whatever is on top — modal, drawer, screen, app.
- Left from the leftmost focusable opens the drawer (if present).
- Every button press produces an immediate visual response.

Use `useTVEventHandler` to map remote buttons to flow actions outside of focus movement (e.g. "play" submits a search, "menu" toggles a settings overlay). Don't use it to override default focus movement on Vega — the handler is observe-only there.

---

## Text input

D-pad typing is the worst interaction in the app. Priority order:

1. Don't ask the user to type if avoidable (input minimisation).
2. Pick the right `keyboardType` to keep the platform keyboard small and predictable.
3. Use the system keyboard unless it blocks critical UI.
4. Add voice input where the platform supports it.
5. Offload complex input to the phone (companion-app, QR auth).

### Pick the right `keyboardType`

Typing-flow reviews almost always find at least one input defaulting to `default` when something more specific applies.

| Use case | `keyboardType` | Notes |
|---|---|---|
| Search | `default` (or `web-search` on iOS) | Full keyboard with autocomplete |
| Email | `email-address` | `@`, `.`, `.com` shortcuts; autocorrect off |
| Phone | `phone-pad` | Digits + `#` and `+` |
| PIN / numeric code | `number-pad` + `secureTextEntry` | Digits only, masked |
| Number (decimal) | `decimal-pad` | Numeric with decimal point |
| URL | `url` | `/`, `.`, `.com` shortcuts |
| Anything sensitive (password, payment) | (whichever fits) + `secureTextEntry` | Shared-room privacy |

iOS-only types (`ascii-capable`, `numbers-and-punctuation`, `web-search`) and Android-only types (`visible-password`) work but should be platform-gated.

```jsx
<TextInput
  placeholder="Password"
  keyboardType="default"
  secureTextEntry
  textContentType="password"
  autoComplete="password"
  onChangeText={setPassword}
/>
```

```jsx
<TextInput
  placeholder="Search shows"
  keyboardType="default"
  value={query}
  onChangeText={setQuery}
  returnKeyType="search"
  onSubmitEditing={() => runSearch(query)}
/>
```

**Watch out for:**
- `<TextInput>` without `keyboardType` — defaults to the slowest keyboard.
- Password-shaped input (placeholder mentions password / PIN / code) without `secureTextEntry` — privacy risk in shared rooms; on some platforms also changes keyboard variant. TVs are shared spaces; everyone in the room sees the screen.
- Search input without `onSubmitEditing` or equivalent submit path — the user has typed with no way to commit.

### System keyboard with RCU events

The system keyboard appears when a `TextInput` gains focus. Use `useTVEventHandler` to map remote buttons to flow actions — e.g. "play" submits the search.

```jsx
// react-native-tvos
import { useTVEventHandler, TextInput, View } from 'react-native';
import { useRef, useState } from 'react';

function SearchScreen({ onSearch }) {
  const queryRef = useRef('');
  const [query, setQuery] = useState('');

  useTVEventHandler((evt) => {
    if (evt.eventType === 'play') {
      onSearch(queryRef.current);
    }
  });

  return (
    <View>
      <TextInput
        placeholder="Search TV shows..."
        keyboardType="default"
        value={query}
        onChangeText={(text) => {
          queryRef.current = text;
          setQuery(text);
        }}
        returnKeyType="search"
        onSubmitEditing={() => onSearch(queryRef.current)}
      />
    </View>
  );
}
```

On Vega, the import is from `@amazon-devices/react-native-kepler` and the handler cannot override default behaviour — usable for side-effects like submitting a search, not for "intercept left to dismiss the keyboard."

#### Platform behaviour

| Platform | Keyboard layout | Notes |
|---|---|---|
| Android TV / Fire TV | Grid (Gboard) | Pops up centre/bottom; can cover UI beneath |
| Apple tvOS | Row-based | Siri Remote swipe-friendly; supports iOS Remote app + dictation |
| Vega | System keyboard | Same general behaviour as Android TV; verify per-device |

### Custom keyboard

Build one only when the system keyboard blocks critical UI (e.g. search screen with results rendered below the keyboard footprint).

```jsx
const [showKeyboard, setShowKeyboard] = useState(false);

return (
  <View style={{ flex: 1 }}>
    <TextInput
      onFocus={() => setShowKeyboard(true)}
      showSoftInputOnFocus={false}      // suppress the default keyboard
    />
    {showKeyboard && <CustomKeyboard onKeyPress={handleKeyPress} />}
  </View>
);
```

If you build one:
- Each key needs `focused` and `selected` states (the user skips keys to reach a target letter).
- Apply standard TV navigation: focus trapped in the keyboard grid, escape on back.
- Use a familiar layout (QWERTY or alphabetic).

Custom keyboards give layout control but force the user to learn a new layout. Bias to the system keyboard unless it measurably breaks the flow.

**Watch out for:** `showSoftInputOnFocus={false}` without a custom keyboard rendered to replace it — leaves the input unusable.

### Voice input

- System keyboard supports dictation on tvOS (Siri Remote) and Android TV (mic on remote). If using the system keyboard, voice is already enabled — wait for the `TextInput` value to fill.
- Custom keyboard + voice requires native code (`react-native-voice` is the common path). Requires microphone and speech-recognition permissions plus matching manifest entries.
- Fire TV / Vega: Alexa flows are more capable than `react-native-voice`. For Fire TV-targeted apps, evaluate Alexa skills / VSK before generic voice input.
- Confirm transcribed text before submitting. The room can hear and see it.

### Companion-app patterns

Phones are better text-input devices. For auth, account creation, casting, or search across long catalogues, offload to the phone.

#### QR-code authentication

Sign-in pattern: TV shows a code, phone scans it, backend binds devices via a shared token.

```jsx
import { useEffect, useState } from 'react';
import { Text, View, ActivityIndicator } from 'react-native';
import QRCode from 'react-native-qrcode-svg';

function QrAuthScreen({ apiClient, onAuthenticated }) {
  const [pairing, setPairing] = useState(null);
  const [error, setError] = useState(null);

  // 1. Ask the backend for a one-time pairing code + URL
  useEffect(() => {
    apiClient.startPairing()
      .then(setPairing)
      .catch(setError);
  }, [apiClient]);

  // 2. Poll for completion
  useEffect(() => {
    if (!pairing) return;
    const id = setInterval(async () => {
      const status = await apiClient.checkPairing(pairing.id);
      if (status.completed) {
        clearInterval(id);
        onAuthenticated(status.token);
      }
    }, 2000);
    return () => clearInterval(id);
  }, [pairing, apiClient, onAuthenticated]);

  if (error) return <Text>Couldn't start pairing. Try again.</Text>;
  if (!pairing) return <ActivityIndicator />;

  return (
    <View>
      <Text>Open this URL on your phone or scan the code:</Text>
      <Text>{pairing.url}</Text>
      <QRCode value={pairing.url} size={400} />
      <Text>Code: {pairing.shortCode}</Text>
    </View>
  );
}
```

Components:
- Pairing endpoint returns a short code, a deep-link URL, and an opaque pairing ID.
- TV polls the backend until the user completes auth on their phone.
- Backend binds the two sessions via the pairing ID and issues a token to the TV.

A 5–6 digit fallback code covers users who can't scan.

#### Casting / search from phone

If the app has a companion mobile app, search input typed on the phone and sent over the local network avoids on-TV typing entirely. Architecture decision rather than a code-level finding, but flag it for any app with a painful search flow.

---

## Hand off to the human reviewer

**Run the static helper first:** `node references/scripts/audit.js src --only input`. Catches grep-able input issues (`TextInput` without `keyboardType`, password-shaped without `secureTextEntry`, search-shaped without submit handler, Vega `useTVEventHandler` imported from the wrong package). It's a helper, not a full review — placeholder-text heuristics miss localised placeholders, and many rules in this file are flow-level decisions the agent can't grep for.

The remaining checks need flow-level / design review:

- Every login flow has a working QR / phone option, or a documented decision not to ship one. *(human — flow review)*
- Voice input, where supported, is visibly available (mic icon, hint) or design has opted out. *(human — design review)*
- Profile / account switching reachable in 1–2 D-pad moves. *(human — flow review)*
- Voice input confirms transcribed text before submitting. *(human — design review)*
