# Keyboard Handling

Input patterns for React Native TV apps. D-pad typing is the slowest interaction on TV — minimize it first, then optimize what remains.

## Input Minimization (Priority #1)

Before building keyboard UI, reduce the need for typing:

- Pre-filled options and smart defaults (past searches, popular searches).
- Voice input via system dictation or `react-native-voice`.
- Real-time validation to minimize corrections.
- Maintain input history so users don't retype.
- QR code authentication (TV shows QR, phone scans to authenticate).
- Mobile companion apps for complex input (auth, casting, search).

## Built-In System Keyboard

Trigger by rendering a standard `TextInput`. Keyboard appears automatically on focus.

### Platform Differences

- **Android TV (Gboard)**: Grid-based, arrow-navigated. Pops up center/bottom, covers UI beneath.
- **Apple tvOS**: Row-based, Siri Remote swipe-friendly. Also supports iOS Remote app and dictation.

### Keyboard Types

Use the appropriate type to minimize friction:

- `default`: Full autocomplete & autocorrect
- `email-address`: @, ., .com shortcuts; autocorrect off
- `numeric`: Numbers only
- `number-pad`: Digits only (PINs, codes)
- `decimal-pad`: Numeric with decimal point
- `phone-pad`: Digits + #, +
- `url`: Includes /, ., .com shortcuts
- Password: Use `secureTextEntry` prop (not a keyboardType)

**iOS-only types:** `ascii-capable`, `ascii-capable-number-pad`, `name-phone-pad`, `numbers-and-punctuation`, `twitter`, `web-search`

**Android-only:** `visible-password`

### Enhancing with RCU Events

Map remote buttons to keyboard actions using `useTVEventHandler`:

```jsx
import { useTVEventHandler } from 'react-native';

const SearchScreen = () => {
  const inputRef = useRef(null);
  const inputValueRef = useRef('');

  const handleSearch = () => {
    // Call search API with inputValueRef.current
  };

  useTVEventHandler((evt) => {
    if (evt.eventType === 'play') {
      handleSearch(); // "play" button = submit search
    }
  });

  return (
    <View>
      <TextInput
        ref={inputRef}
        placeholder="Search TV shows..."
        onChangeText={(text) => { inputValueRef.current = text; }}
        onSubmitEditing={handleSearch}
      />
    </View>
  );
};
```

`onSubmitEditing` fires when the text input's submit button is pressed, which is the most common trigger. Depending on your UI, you may also want `onBlur` (submit when focus leaves the field) or to listen for events from surrounding `Pressable` / `Touchable` components (e.g., a dedicated "Search" button next to the input). Pick whichever matches how users actually complete the action in your flow.

## Custom Keyboard

When the system keyboard covers important UI or you need more control:

### Implementation Pattern

```jsx
const [showKeyboard, setShowKeyboard] = useState(false);

return (
  <KeyboardAvoidingView behavior="position" style={{ flex: 1 }}>
    <View style={{ flex: 1 }}>
      <TextInput
        onFocus={() => setShowKeyboard(true)}
        showSoftInputOnFocus={false}  // Suppress default keyboard
      />
    </View>
    {showKeyboard && <CustomKeyboard onKeyPress={handleKeyPress} />}
  </KeyboardAvoidingView>
);
```

### Custom Keyboard Considerations

- Set `showSoftInputOnFocus={false}` to suppress the default keyboard.
- Each key button needs two states: **focused** and **selected** (user skips over buttons to reach target letter).
- Wire each button's output to the TextInput value.
- Focus management within the keyboard grid follows standard TV navigation rules.

### Tradeoff

Custom keyboards give full UI control but users must learn your specific layout. The system keyboard is familiar even if less pretty. Only build custom when the system keyboard genuinely blocks critical UI (like YouTube's search with results visible below).

## Voice Input

- **With system keyboard**: Already handles dictation. Just wait for system to fill the TextInput.
- **With custom keyboard**: Need native code. Use `react-native-voice` library.
- Remember: adding voice requires microphone + speech recognition permissions.

## Mobile Companion Apps

Companion apps (YouTube, Netflix, Spotify pattern) offload input to the phone:
- Authentication via QR code (TV shows code, phone scans, backend binds devices via shared token).
- Search input typed on phone keyboard, sent to TV over local network.
- Media casting from phone to TV (no TV-side login needed).

## Key Rules

1. Prioritize input minimization — every keystroke saved is UX gained.
2. Use appropriate keyboard types (don't show full keyboard for a PIN).
3. Maintain input history.
4. Enable voice input where possible.
5. Consider companion app flows for complex authentication.
