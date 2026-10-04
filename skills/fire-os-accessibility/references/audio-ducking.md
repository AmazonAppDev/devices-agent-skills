# Audio focus, ducking and loudness

For an app that speaks over its own content — audio description over a film, a spoken subtitle over music — the content has to dip under the voice, quickly and by the right amount. Fire OS 7 is Android 9's audio stack, and several of its behaviours surprise. Source citations are to AOSP `frameworks/av` for Android 9 (read from the LineageOS `lineage-16.0` mirror). *Measured* means observed on a Fire TV Stick HD, Fire OS 7.7.1.5.

## Audio focus

Amazon's [Managing Audio Focus (Fire TV)](https://developer.amazon.com/docs/fire-tv/managing-audio-focus.html) adds rules on top of Android's:

- Hold focus for exactly as long as you play, with the `MediaSession` active; abandon it as soon as playback ends.
- Handle focus callbacks the way Android's pre-8.0 audio focus guidance describes.
- On any focus loss, stop handling media events until focus returns. A permanent loss means release everything.
- Don't request focus again without abandoning the previous request.
- When asked to duck, go to about **30–40%** of the original level.

A self-voicing app can also use focus to hear VoiceView coming: see [voiceview.md](voiceview.md#apps-that-speak-for-themselves).

## How fast a volume change takes effect

`AudioTrack.setVolume()` (and ExoPlayer's `setVolume`, which calls it) does not reach the mixer immediately. It writes the gain into the track's shared control block and returns (`media/libaudioclient/AudioTrack.cpp`, `setVolume`). AudioFlinger's mixer thread reads it **once per mix buffer** (`services/audioflinger/Threads.cpp`, `prepareTracks_l`) and ramps linearly from the old gain to the new one across that buffer.

So:

- **A volume change is heard as a ramp one mix period long**, starting at the next buffer. You cannot make it shorter.
- Writing volume faster than the mix period does nothing: every value but the last is overwritten before it is read.
- Because every change is ramped, no single step clicks, however large.

The mix period depends on the output thread, i.e. the route. *Measured* with `adb shell dumpsys media.audio_flinger`:

| Output thread | Mix period |
| --- | --- |
| `AudioOut_D` | 16 ms |
| `AudioOut_15` (fast mixer) | 20 ms |
| `AudioOut_4D` | 32 ms |

Over Bluetooth A2DP, the app's media and speech tracks both landed on the 32 ms thread. Broadcast audio-description guidance asks for the content to duck within about 15 ms, so the first consonant isn't masked (Netflix's Audio Description Style Guide: an attack of 2–15 ms). **No Fire OS 7 route measured meets that**; command a short attack (≈10 ms) and accept that the platform's own ramp is what is heard. Check your route's period with `dumpsys` rather than assuming one.

For finer control, apply gain to the samples yourself inside the player's render chain — in Media3, an `AudioProcessor` added through a custom `DefaultAudioSink` — instead of calling `setVolume`. Two Media3 notes if you do:

- In Media3 **before 1.11.0**, `AudioProcessor.flush()` takes no arguments and gives the processor no way to learn where a **seek** landed. If the processor tracks playback position, reset it from the player's `onPositionDiscontinuity` (`DISCONTINUITY_REASON_SEEK`). 1.11.0 adds `flush(StreamMetadata)` with `positionOffsetUs`.
- `DefaultAudioSink` buffers a lot of PCM (hundreds of ms), so gain applied in the processor reaches the speaker that much later than the decision. Measure the lag, and schedule the duck ahead by that much.

## Narration playback

**Mono voices play about 3 dB louder than a mono measurement says.** On Android 9 the mixer does not remix a mono track onto a stereo output; it copies the sample to both channels at full level, with no pan law (`media/libaudioprocessing/AudioMixer.cpp`, the `MONO_HACK` comment in `prepareForDownmix`; `AudioMixerOps.h`, `MIXTYPE_MONOEXPAND`). A loudness meter (ITU-R BS.1770) sums power across channels, so a signal duplicated to both measures `10·log10(2) ≈ 3.01` LU hotter than the same signal measured as mono.

*Measured:* the same pink noise, played once as a mono file and once already duplicated into two channels, came out within 0.18 dB of each other at the device output — no pan law. A duck computed from the voice's mono loudness left the voice 15.1 LU above the ducked content where 12.5 was intended.

Fix: add `10·log10(2)` to a mono voice's measured loudness before using it in any level decision. Keep it a setting: a device or route that does apply a pan law would need `0`.

**Use a static track for short, pre-rendered lines.** An `AudioTrack` in `MODE_STATIC` holds the whole clip, so there is no feed to starve. But note: `AudioTrack.getUnderrunCount()` **always returns 0 for a static track** — the static proxy has no underrun counter (`include/private/media/AudioTrackShared.h`, `StaticAudioTrackClientProxy::getUnderrunCount`). A zero there proves nothing.

Detect the end of a line by watching `AudioTrack.getPlaybackHeadPosition()` reach the frame count, not by a timer set from the file's length.

## Loudness

How far to duck depends on how loud the content is at that moment: the rule is to keep the voice a constant loudness above the content, not to cut a fixed number of decibels. On API 28 **the platform gives no way to read the content's loudness**:

| Candidate | Why it doesn't work on API 28 |
| --- | --- |
| `LoudnessEnhancer` | An effect, not a meter. It changes gain; it reports nothing |
| `MediaFormat.KEY_AAC_DRC_OUTPUT_LOUDNESS` | Added in API 30. AAC only, and `-1` when the stream has no MPEG-D DRC metadata |
| `LoudnessCodecController` | Added in API 35 |
| `Visualizer` | Needs `RECORD_AUDIO` just to observe your own output; 8-bit samples (~48 dB of range); returns zeros on Widevine L1 secure paths and HDMI passthrough, where the app never sees decoded samples |
| AC-3/E-AC-3 `dialnorm` | In the bitstream, but Media3's `Ac3Util.parseAc3SyncframeInfo` skips it without storing it |

What works: measure it yourself, on the decoded PCM, in the render chain (the same Media3 `AudioProcessor` that applies the duck). Implement ITU-R BS.1770-4 — K-weighting, gated integrated loudness, short-term (3 s) loudness — and validate it against the EBU Tech 3341 test signals and against `ffmpeg -af ebur128` on real content before trusting it. The standard's filter coefficients are given for 48 kHz: re-derive them for any other sample rate (text-to-speech engines render at 16 or 24 kHz).

This only works where the app sees decoded samples. For DRM-protected content on a secure path, or passthrough audio, there is no measurement route on this platform.

**For debugging only**, `Visualizer` attached to session 0 (the output mix) is a useful check that a duck arrives as commanded: *measured*, the output level it reported tracked commanded gain changes at 0.997 dB per dB (residual 0.64 dB RMS). It averages power over the interleaved channels, so it cannot see the mono duplication described above — which is exactly what makes it useful for testing for it. It needs `RECORD_AUDIO`, so keep it out of release builds.

## Checklist

- [ ] Audio focus held and abandoned exactly around playback; losses handled per Amazon's rules.
- [ ] Duck timing designed around the route's mix period, measured with `dumpsys media.audio_flinger`.
- [ ] Mono voice loudness corrected by +3.01 LU before it feeds a level decision.
- [ ] No reliance on `getUnderrunCount()` for static tracks.
- [ ] Duck depth derived from measured content loudness, where the app can see the samples.
