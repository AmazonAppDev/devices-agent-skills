# Text-to-speech on Fire TV

Android's `TextToSpeech` API works on Fire OS, but the engines behind it behave differently from a phone's, and the difference fails silently. Everything marked *measured* below was observed on a Fire TV Stick HD (AFTSSS), Fire OS 7.7.1.5, Android 9 / API 28, ~900 MB RAM. Other Fire TV models may ship different engines; run the checks below on each one.

## What is installed

*Measured:* two engines, both declaring `android.intent.action.TTS_SERVICE`:

| Engine | Package | Notes |
| --- | --- | --- |
| IVONA | `com.ivona.tts.oem` | The platform **default**. Voices are fetched on demand; the APK itself contains no voice data |
| SVOX Pico | `com.svox.pico` | Ships its voice data in the system image (`/system/tts/lang_pico`). Works from first boot. 16 kHz, noticeably robotic |

## The silent default engine

On a device where no IVONA voice has been provisioned:

| Call | Returns | Reality |
| --- | --- | --- |
| `TextToSpeech(context, listener)` (two-argument form) | binds the default engine, IVONA | — |
| `onInit` | `SUCCESS` | the engine has **0 voices** |
| `synthesizeToFile(...)` | `SUCCESS` | **no audio is produced** |
| `UtteranceProgressListener.onError(utteranceId, errorCode)` | not called | — |
| `UtteranceProgressListener.onError(utteranceId)` (deprecated) | called, no error code | the only signal |

An app that checks return values and doesn't implement the deprecated overload sees nothing wrong, and produces silence.

**Provisioning.** *Measured:* the only trigger found for IVONA to fetch a voice was **enabling VoiceView**. It then downloaded one voice matching the device locale (`kajal`, en-IN, on the test device), 24 kHz, and the voice **stayed after VoiceView was switched off again**. So two identical devices can give the same app different voices, depending on whether anyone ever turned the screen reader on.

## Selecting an engine

```kotlin
// Engines the device offers. On targetSdk 30+ this needs the <queries> entry below.
val engines = context.packageManager.queryIntentServices(
    Intent(TextToSpeech.Engine.INTENT_ACTION_TTS_SERVICE), 0
).map { it.serviceInfo.packageName }

// Bind each candidate explicitly with the three-argument constructor, then qualify it
// by what it can actually speak, not by the status passed to onInit.
val tts = TextToSpeech(context, { status -> /* don't trust this alone */ }, enginePackage)
// After onInit has been called:
val usable = tts.voices.orEmpty().any { it.locale.language == wanted.language }
```

- Never use the two-argument constructor; name the engine.
- Treat an engine with **zero voices** (or none for the language you need) as unavailable, whatever `onInit` said.
- Prefer IVONA when it reports a usable voice; fall back to Pico; if neither qualifies, say so in the log and in the UI rather than scheduling audio that doesn't exist.
- Implement **both** `onError` overloads in your `UtteranceProgressListener`.

**Package visibility.** If the app targets API 30 or higher, add this to the manifest or `queryIntentServices` sees no engines on Android 11+ devices ([Android docs](https://developer.android.com/training/package-visibility/use-cases#connect-to-a-text-to-speech-engine)):

```xml
<queries>
    <intent>
        <action android:name="android.intent.action.TTS_SERVICE" />
    </intent>
</queries>
```

## Durations differ between engines

*Measured:* the same sentence rendered as **3,730 ms** on IVONA and **4,648 ms** on Pico — 918 ms, about 25%. If the app decides whether a line fits a gap (audio description between lines of dialogue, a subtitle before the next one), measure the duration **with the engine and voice that will actually play it**, from the rendered file, and never reuse a duration measured on another engine or at another speaking rate.

## Rendering ahead of time

For speech whose text is known in advance (audio description, spoken subtitles), render to files once, measure them, and play the files. This:

- removes engine start-up and synthesis latency from the moment the line must start;
- gives an exact, measured duration per line;
- lets the app cache renders across launches, keyed by text, engine, voice and speaking rate, so only the first launch pays the synthesis time.

Speech that can't be known in advance (announcing the button that just got focus) has to be synthesised live; keep it short.

Play the rendered files with `AudioTrack` or a media player using `AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY` and `CONTENT_TYPE_SPEECH`. The narration-playback section of [audio-ducking.md](audio-ducking.md#narration-playback) covers what that route does to the voice's level.

## Checklist

- [ ] Engine chosen by voice count, three-argument constructor, both `onError` overloads.
- [ ] `<queries>` entry present if `targetSdk >= 30`.
- [ ] The app tells the user when no usable voice exists, instead of going silent.
- [ ] Every timing decision uses a duration measured from the engine that plays it.
- [ ] Tested on a device where VoiceView has **never** been enabled (factory-fresh, or a second device), not only on the developer's own.
