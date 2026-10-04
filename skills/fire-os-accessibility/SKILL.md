---
name: fire-os-accessibility
description: Accessibility and speech-audio guidance for native Fire OS apps on Fire TV (Kotlin/Java, AndroidX Media3/ExoPlayer, Compose for TV, Android TV views). Use when building, reviewing or debugging a Fire TV app that works with VoiceView (Amazon's screen reader) or speaks for itself — text-to-speech (TextToSpeech, IVONA, Pico) that is silent or sounds wrong, VoiceView talking over the app, audio focus and ducking under narration, audio description, spoken subtitles, caption and audio-description controls (EN 301 549 clause 7), com.amazon.accessibility extras (usage hints, orientation text, described-by), remote buttons VoiceView reserves, voice input or the microphone on Fire TV, and proving audio behaviour on a real Fire TV device with adb, logcat and dumpsys. Not for Vega OS or React Native apps.
---

# Fire OS Accessibility and Speech Audio

This skill helps an agent build or review a **native Fire OS app** (the Android-based Fire TV platform) that has to work with VoiceView, Fire TV's screen reader, or that speaks on its own: audio description, spoken subtitles, UI narration, a talking menu. The references hold the non-obvious platform behaviour. Pick the one that matches the task rather than reading them all.

Most of what goes wrong here is **silent**. The text-to-speech engine reports success and produces no sound. VoiceView speaks over an app that hid every view from it. A volume change lands later than it was asked for. JVM tests pass and the device does something else. So the rule that runs through every reference: **prove behaviour on a real Fire TV device**, from logs, not from return values or from listening once.

## Check before applying

1. **Is this Fire OS?** An Android project (Gradle, `AndroidManifest.xml`) that targets Fire TV: `android.software.leanback` in `<uses-feature>` or the `LEANBACK_LAUNCHER` category. If the project has a `manifest.toml` or depends on `@amazon-devices/*` packages, it is **Vega OS** — this skill does not apply; use Amazon's Vega documentation. If it is React Native, use `rn-tv-ui-best-practices` for focus and layout; the text-to-speech and audio references here still apply to any native module underneath.
2. **Which Fire OS version and API level?** `minSdk` and the devices you ship to decide which APIs exist. Measurements in these references were taken on a **Fire TV Stick HD running Fire OS 7 (Android 9, API 28)**, and are marked as such. Re-verify device-specific numbers on each device you support.
3. **Does the app speak for itself, or rely on VoiceView?** Most apps should expose a good accessibility tree and let VoiceView do the talking ([voiceview.md](references/voiceview.md)). An app that speaks on its own (audio description, spoken subtitles) also needs [text-to-speech.md](references/text-to-speech.md) and [audio-ducking.md](references/audio-ducking.md).

## The eight things an agent gets wrong without this skill

1. **Trusting `TextToSpeech` status.** On Fire TV the default engine can return `SUCCESS` from `onInit` and `synthesizeToFile` and produce no audio, if no voice has been provisioned on that device. Select an engine by **voice count**, not status → [text-to-speech.md](references/text-to-speech.md).
2. **Assuming hidden views keep VoiceView quiet.** Marking every node unimportant for accessibility stops focus announcements, but VoiceView can still speak on its own, for example when playback starts or the screen changes → [voiceview.md](references/voiceview.md).
3. **Binding keys VoiceView owns.** Menu (long press, and Back + Menu) and Play/Pause while VoiceView is speaking belong to VoiceView. Rewind and Fast Forward control its reading → [voiceview.md](references/voiceview.md).
4. **Planning voice input.** The remote's microphone goes to Alexa and cannot be intercepted, and there is no Google `SpeechRecognizer` → [remote-and-voice-input.md](references/remote-and-voice-input.md).
5. **Treating `setVolume` as instant.** Volume changes take effect once per mixer buffer, and the buffer depends on the output route → [audio-ducking.md](references/audio-ducking.md).
6. **Measuring a mono voice as mono.** On the tested device a mono track is copied to both stereo channels at full level, so it plays about 3 dB louder than a mono loudness measurement says → [audio-ducking.md](references/audio-ducking.md).
7. **Burying caption and audio-description controls in settings.** EN 301 549 clause 7.3 puts them at the same level as the main media controls → [media-accessibility-controls.md](references/media-accessibility-controls.md).
8. **Believing JVM tests and `screenrecord`.** Android's regex engine, resource packaging and audio mixer differ from the desktop JVM, and `screenrecord` on Android 9 records no audio → [verify-on-device.md](references/verify-on-device.md).

## References

| Topic | File |
| --- | --- |
| VoiceView: Amazon's accessibility extras, reserved buttons, coexisting with a self-voicing app | [voiceview.md](references/voiceview.md) |
| Text-to-speech engines on Fire TV: selection, silent failures, durations | [text-to-speech.md](references/text-to-speech.md) |
| Audio focus, ducking under narration, loudness, mono voices | [audio-ducking.md](references/audio-ducking.md) |
| Remote buttons available to apps, and why there is no voice input | [remote-and-voice-input.md](references/remote-and-voice-input.md) |
| Captions, audio description and spoken subtitles: what a player must offer and where | [media-accessibility-controls.md](references/media-accessibility-controls.md) |
| Proving it on the device: adb, logcat, dumpsys, uiautomator; build traps that only show on Android | [verify-on-device.md](references/verify-on-device.md) |

## Decision tree

```
VoiceView
├─ Screen reads badly or not at all          → voiceview.md (Content descriptions, extras)
├─ Which remote buttons can I bind?          → voiceview.md + remote-and-voice-input.md
├─ VoiceView talks over my app's own speech  → voiceview.md (Self-voicing apps) + audio-ducking.md (Audio focus)
└─ Test with VoiceView on                    → verify-on-device.md

Speech the app produces
├─ No sound, no error                        → text-to-speech.md
├─ Voice sounds robotic on some devices      → text-to-speech.md (Provisioning)
├─ Timing depends on the engine              → text-to-speech.md (Durations)
└─ Playing rendered speech                   → audio-ducking.md (Narration playback)

Mixing speech over content
├─ Lowering the film under a voice           → audio-ducking.md
├─ How loud is the content?                  → audio-ducking.md (Loudness)
└─ Voice too loud or too quiet vs. measured  → audio-ducking.md (Mono voices)

Player features
├─ Captions, audio description, spoken subs  → media-accessibility-controls.md
└─ Voice commands / microphone               → remote-and-voice-input.md

Anything claimed to work                     → verify-on-device.md
```

## What to hand to a human

An agent can read logs and dumps, but some checks need a person at the TV: whether speech is intelligible over a loud scene, whether VoiceView's reading order makes sense, and the actual timing between two voices (which needs an audio capture — see verify-on-device.md). Flag these for human verification rather than claiming them.
