# VoiceView

VoiceView is Fire TV's built-in screen reader. It moves with the input focus and speaks whatever gains focus, reading from the standard Android accessibility tree. Most of an app's VoiceView support is ordinary Android accessibility work. Fire OS adds a few Amazon-specific extras, reserves some remote buttons, and behaves in ways that matter when the app also speaks for itself.

Sources: Amazon, [Implement VoiceView Accessibility Features (Fire TV)](https://developer.amazon.com/docs/fire-tv/implement-voiceview-accessibility-features-fire-os.html) and [How to implement VoiceView on Fire devices](https://developer.amazon.com/apps-and-games/blogs/2025/11/how-to-implement-voiceview-on-fire-devices) (Nov 2025). Behaviour marked *measured* was observed on a Fire TV Stick HD, Fire OS 7.7.1.5 (Android 9, API 28).

## Baseline: the Android accessibility tree

Amazon's checklist starts with the standard framework:

- Make the UI compatible with the Android accessibility framework.
- Give every image, icon button and custom view a **content description** (`android:contentDescription`; `Modifier.semantics { contentDescription = … }` in Compose). An unlabelled icon is read as "Unlabeled button" or "Image".
- Announce changes the user cannot see: `AccessibilityEvent.TYPE_ANNOUNCEMENT` for one-off results, or a container with `android:accessibilityLiveRegion="polite"` for regions where new content appears.

## Amazon's accessibility extras

Fire OS reads extra keys from `AccessibilityNodeInfo.getExtras()`. Set them in `onInitializeAccessibilityNodeInfo` (on a `View`, or through an `AccessibilityDelegate`):

| Key | What VoiceView does with it | Put it on |
| --- | --- | --- |
| `com.amazon.accessibility.usageHint.remote` | Reads a navigation hint when focus **enters** the container, not on every move inside it | The container of a list or grid, never each item |
| `com.amazon.accessibility.orientationText` | Reads a description of the screen's layout the first time the container is seen, and again when the user presses Menu | The container of a screen region |
| `com.amazon.accessibility.describedBy` | Reads extra, non-focusable detail after the user **pauses** on the focused item | The focusable item whose details are shown elsewhere on screen |

`usageHint.touch` is the Fire tablet counterpart of `usageHint.remote`. The Amazon blog also lists `com.amazon.accessibility.hint`.

```kotlin
override fun onInitializeAccessibilityNodeInfo(host: View, info: AccessibilityNodeInfo) {
    super.onInitializeAccessibilityNodeInfo(host, info)
    info.extras.putString(
        "com.amazon.accessibility.usageHint.remote",
        "Press left or right to find a movie, up or down to change rows."
    )
}
```

Compose's semantics API does not expose `AccessibilityNodeInfo` extras directly. Amazon's blog notes this for Compose and React; check it for the current approach before promising these extras in a Compose UI.

## Buttons VoiceView owns

From Amazon's VoiceView documentation:

| Button | With VoiceView on |
| --- | --- |
| **Back + Menu**, held together for two seconds | Turns VoiceView on or off |
| **Menu**, long press | Enters or leaves **Review Mode** (linear exploration of the whole screen) |
| **Menu**, single press | VoiceView reads usage hints, orientation text, described-by text, then other static content. The app still receives **double** presses |
| **Play/Pause** while VoiceView is speaking | Silences VoiceView. A second press then pauses the media |
| **Rewind / Fast Forward** while VoiceView reads static content | Move through what it is reading |

So an app should not depend on a single Menu press, a Menu long press, or the Back + Menu chord. Handle Play/Pause normally: when VoiceView is quiet the press reaches the app.

Fire TV's other accessibility shortcuts (for example the screen magnifier and text banner) are also chords of Back, Menu, Rewind and Fast Forward. Check Fire TV's current accessibility help before binding any **chord** or long press, and prefer single short presses for app features.

## Apps that speak for themselves

An app that produces its own speech — audio description, spoken subtitles, a narrated menu — has two voices to keep apart: its own and VoiceView's.

**Hiding the tree is not enough.** A common approach is to hide the app's own views from accessibility (`importantForAccessibility="noHideDescendants"`, or `Modifier.semantics { invisibleToUser() }` in Compose) and narrate focus changes itself. *Measured:* with every node hidden, VoiceView stayed silent while focus moved, but still spoke on its own — about 2 s after playback started, and on a full-screen visual change — and did so while a `uiautomator dump` showed no readable text anywhere in the app. What it said could not be recovered from any log. Design for VoiceView speaking at moments you do not control.

**Knowing when VoiceView is speaking.** There is no public "VoiceView is speaking" API. What works is **audio focus**:

1. Hold `AUDIOFOCUS_GAIN` while your app is playing, requested with `AudioFocusRequest.Builder(AUDIOFOCUS_GAIN).setWillPauseWhenDucked(true)` (API 26+).
2. *Measured:* VoiceView requests `AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK` before it speaks. Because of `setWillPauseWhenDucked(true)`, the framework delivers `AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK` to your listener instead of lowering your volume silently (AOSP 9, `services/core/java/com/android/server/audio/FocusRequester.java`). The loss arrived 2–24 ms after VoiceView's request, 3 of 3 times.
3. On that loss, stop your own speech, start nothing new, and resume when `AUDIOFOCUS_GAIN` comes back.

Limits of this approach: the app learns about VoiceView only after VoiceView has asked, and it cannot tell VoiceView apart from any other app taking transient focus. Keep the rest of Amazon's audio focus rules too ([audio-ducking.md](audio-ducking.md#audio-focus)).

**Finding VoiceView's service for tests.** No installed package is named for VoiceView. With VoiceView switched on by hand, `adb shell settings get secure enabled_accessibility_services` shows `com.amazon.logan/com.amazon.logan.LoganAccessibilityService` (*measured*, Fire OS 7). The system log carries a `VoiceViewEventProvider` line, "Posting VoiceView speaking event. Is speaking? true/false", which is useful when reading a test run ([verify-on-device.md](verify-on-device.md)). Whether an app can subscribe to that event is not established.

**Users' own workaround** when VoiceView and audio description talk over each other is to turn VoiceView off for the film (for example, [r/Blind](https://www.reddit.com/r/Blind/comments/revt97/three_audio_tracks_on_amazon_fire_tv_while/)). That costs them the ability to operate the TV, so treat a self-voicing app's coexistence with VoiceView as a design requirement, not an edge case.
