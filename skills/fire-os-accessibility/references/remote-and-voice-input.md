# Remote buttons and voice input

Fire TV remotes send ordinary Android `KeyEvent`s and never `MotionEvent`s. Source: Amazon, [Remote Control Input (Fire TV)](https://developer.amazon.com/docs/fire-tv/remote-input.html).

## What an app can and can't receive

| Button | `KeyEvent` | Can the app handle it? |
| --- | --- | --- |
| Home | none | **No.** System event, cannot be intercepted |
| Microphone (voice search, Voice Remote only) | none | **No.** Invokes the system voice search, cannot be intercepted |
| Back | `KEYCODE_BACK` | Yes |
| Menu | `KEYCODE_MENU` | Yes, but see VoiceView below |
| Select | `KEYCODE_DPAD_CENTER` | Yes |
| D-pad | `KEYCODE_DPAD_UP/DOWN/LEFT/RIGHT` | Yes |
| Play/Pause | `KEYCODE_MEDIA_PLAY_PAUSE` | Yes, but see VoiceView below |
| Rewind / Fast Forward | `KEYCODE_MEDIA_REWIND` / `KEYCODE_MEDIA_FAST_FORWARD` | Yes |

Amazon notes that Play/Pause, Rewind and Fast Forward **may not be present on every remote**, so every action must also be reachable with the D-pad and Select.

## With VoiceView on

VoiceView takes some of these buttons for itself (Amazon's VoiceView documentation; details in [voiceview.md](voiceview.md#buttons-voiceview-owns)):

- **Menu**: a single press makes VoiceView read the screen's hints and static content, and a long press toggles Review Mode. The app still receives double presses.
- **Back + Menu**, held: toggles VoiceView itself.
- **Play/Pause** while VoiceView is speaking: silences VoiceView. The press reaches the app only when VoiceView is quiet.
- **Rewind / Fast Forward** while VoiceView reads static content: move through what it is reading.

Design so that no feature depends on a single Menu press, a long press, or a chord. Two practical consequences:

- If you bind Rewind and Fast Forward **one key at a time** (as a media controller does by default), a chord of the two can fire both actions. Act only on the first key-down of a press, and ignore repeats from a held key (`event.repeatCount > 0`).
- Put everything an accessibility user needs on focusable, labelled controls reachable by D-pad, so nothing requires a special button.

## Voice input

A blind user asking a question out loud seems natural, but on Fire TV a third-party app cannot get the user's voice:

1. The remote's **microphone button goes to Alexa** and cannot be intercepted (table above).
2. Fire OS has **no Google Play Services**, so the platform `SpeechRecognizer` has no recognition service behind it. Code written against it compiles and then fails at runtime.
3. `AudioRecord` with `RECORD_AUDIO` granted *appeared to succeed and returned silent buffers* on the test device (Fire TV Stick HD, Fire OS 7). That looks like a bug in your own code; it isn't.

So don't plan voice commands for a Fire TV app. Bind the interaction to a remote button (or a focusable on-screen control), and speak the result. For a blind user that is often faster anyway: no wake word and no recognition delay.

