# Task scenarios

Each scenario is a prompt an agent receives with no other context, plus the assertions a good answer must meet. Run each prompt twice, once with the skill loaded and once without, and score each assertion pass/fail. A scenario passes when all its assertions pass.

## S1. Silent text-to-speech

> My Fire TV app uses Android's TextToSpeech. `onInit` returns SUCCESS and `synthesizeToFile` returns SUCCESS, but on a customer's brand-new Fire TV Stick nothing is spoken and no error is reported. What is going on and how do I fix it?

- A1. Says the default engine on Fire TV can have no voice installed while still reporting success.
- A2. Recommends choosing the engine by checking its voices (not by `onInit` status), binding it by package name with the three-argument constructor.
- A3. Mentions the deprecated `onError(String)` overload as the only error signal on this path.
- A4. Names a fallback engine (Pico) and/or that enabling VoiceView once provisions the default engine's voice.

## S2. Voice search from the remote

> I want users of my Fire TV app to press the microphone button on the remote and ask a question that my app answers. How do I capture the microphone button and the audio?

- A1. Says the microphone button cannot be intercepted by the app (it goes to the system voice search / Alexa).
- A2. Says `SpeechRecognizer` is unavailable because Fire OS has no Google Play Services.
- A3. Proposes a non-voice alternative (a remote button or on-screen control).

## S3. A Menu long-press shortcut

> In my Fire TV video player I want a long press on the Menu button to open the subtitle and audio description settings. Any problems with that?

- A1. Says Menu long press is VoiceView's Review Mode (and/or a single Menu press is taken by VoiceView).
- A2. Recommends putting the controls on screen, reachable with the D-pad, next to the playback controls.

## S4. Two voices at once

> Our Fire TV app narrates its own UI with TextToSpeech. We hid all our views from accessibility so VoiceView wouldn't talk, but VoiceView users still sometimes hear VoiceView and our narration at the same time. How do we coordinate with VoiceView?

- A1. Says hiding views does not guarantee VoiceView stays silent.
- A2. Proposes using audio focus to detect VoiceView speaking (hold `AUDIOFOCUS_GAIN`, receive a transient/can-duck loss).
- A3. Mentions `setWillPauseWhenDucked(true)` (or equivalent) so the app is told instead of being ducked silently.
- A4. Notes a limitation: no public VoiceView-speaking API, or the app cannot tell VoiceView from other focus holders.

## S5. A 10 ms duck

> When our audio description starts, we fade the movie down with ExoPlayer's `setVolume`, calling it every 2 ms to get a smooth 10 ms fade on Fire TV (Fire OS 7). Will the listener actually hear a 10 ms fade?

- A1. Says the mixer applies volume once per mix buffer, so the fade takes at least one mix period.
- A2. Says writes faster than the mix period are overwritten / have no effect.
- A3. Gives a realistic range (≈16–32 ms depending on route) or says to measure with `dumpsys media.audio_flinger`.

## S6. Narration too loud

> Our audio description narration is a mono file normalised to -27 LUFS. We compute how much to duck the film from that number, but on Fire TV the narration sounds about 3 dB too prominent over the film. Why?

- A1. Explains the mono track is copied to both stereo channels at full level (no pan law).
- A2. Quantifies it as about +3 dB (10·log10 2) in BS.1770 terms.
- A3. Recommends adding that offset to the mono measurement (kept configurable).

## S7. Measuring the film's loudness

> On a Fire TV Stick (API 28), how can my app find out how loud the movie currently playing is, so I can set the duck depth under audio description?

- A1. Says API 28 has no platform loudness readback (e.g. `KEY_AAC_DRC_OUTPUT_LOUDNESS` is API 30; `LoudnessEnhancer` reports nothing).
- A2. Recommends measuring BS.1770 loudness on the decoded PCM in the player's render chain (e.g. a Media3 `AudioProcessor`).
- A3. Notes it can't be done on DRM secure paths or passthrough, or that `Visualizer` is unsuitable (permission, 8-bit, blind under DRM).

## S8. Where the accessibility controls go

> We are building a Fire TV video player for the EU market. Where in the UI should the caption and audio description controls go?

- A1. Cites EN 301 549 clause 7.3 (or equivalent): at the same level as the primary playback controls.
- A2. Says they should be reachable with the D-pad without special buttons, labelled with their state.
- A3. Mentions keeping audio description per title / off by default, or reversible where it was turned on.

## S9. VoiceView for a movie grid

> Our Fire TV app has a grid of movie posters. With VoiceView on, users get lost. What Fire-specific accessibility metadata should we add?

- A1. Names `com.amazon.accessibility.usageHint.remote`, set on the grid container rather than each item.
- A2. Names `com.amazon.accessibility.orientationText` and/or `com.amazon.accessibility.describedBy`, with their purpose.
- A3. Says these go in `AccessibilityNodeInfo` extras (e.g. in `onInitializeAccessibilityNodeInfo`).

## S10. Recording a demo with sound

> I need to record a video of my Fire TV app (Fire TV Stick, Fire OS 7) with its audio for a demo. What's the easiest way?

- A1. Says `adb screenrecord` on Android 9 records no audio.
- A2. Says `scrcpy` audio needs Android 11+.
- A3. Recommends a camera or HDMI capture instead.

## S11. Regex crash only on the device

> Our subtitle parser strips `{\an8}` tags with the Kotlin regex `\{[^}]*}`. All our JVM and Robolectric tests pass, but on the Fire TV Stick the app throws PatternSyntaxException when loading subtitles. Why?

- A1. Explains Android's regex engine (ICU) rejects the unescaped closing brace that the desktop JVM accepts.
- A2. Gives the fix `\{[^}]*\}`.
- A3. Recommends running text-parsing code on a device or emulator, since Robolectric uses the JVM engine.
