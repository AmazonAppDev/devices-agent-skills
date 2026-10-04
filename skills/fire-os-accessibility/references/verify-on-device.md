# Proving it on the device

Accessibility and audio behaviour on Fire TV has to be checked on a real device. Return values lie (the text-to-speech engine reports success and stays silent), JVM tests run a different regex engine and none of the platform audio stack, and listening once is neither repeatable nor possible for every tester. Make the app **log what it decides and when**, then read the device's own logs and dumps.

*Measured* notes refer to a Fire TV Stick HD, Fire OS 7.7.1.5 (Android 9, API 28).

## Connect

On the device, once: Settings → My Fire TV → Developer Options → **ADB Debugging** on. The IP address is under Settings → My Fire TV → About → Network. The first `adb connect <ip>:5555` shows an authorisation prompt on the TV that must be accepted with the remote. The address can change between sessions on DHCP; look it up again rather than hard-coding it.

## Log one line per decision

Give the app one log tag and log every decision with its timestamp: which text-to-speech engine was selected and why, each voice starting and ending, each duck and its target level, each focus loss and gain, each line dropped and the reason. Then a whole run can be read back with:

```sh
adb logcat -s YourTag:V
```

The default log buffer can drop lines during a long run; raise it for the session with `adb logcat -G 4M` (resets on reboot).

## What the system will tell you

| Question | Command | What to look for |
| --- | --- | --- |
| Which engines exist, which is default | Log `TextToSpeech.getEngines()` and each engine's voice count from the app; `adb shell settings get secure tts_default_synth` for the user's default (empty if never changed) | Engine package names and voice counts |
| Did VoiceView speak, and when | `adb logcat` | `VoiceViewEventProvider` … `Is speaking? true` / `false` (*measured*, Fire OS 7) |
| Who holds audio focus | `adb shell dumpsys audio` | The focus stack; `MediaFocusControl` lines in logcat show each `requestAudioFocus` |
| Mix period per output thread | `adb shell dumpsys media.audio_flinger` | Per thread: sample rate, HAL frame count, normal frame count, fast mixer or not. Mix period = normal frames ÷ sample rate |
| Is VoiceView on, and its service name | `adb shell settings get secure enabled_accessibility_services` | `com.amazon.logan/com.amazon.logan.LoganAccessibilityService` (*measured*, Fire OS 7) |
| What the accessibility tree exposes | `adb shell uiautomator dump` then `adb pull /sdcard/window_dump.xml` | `text` and `content-desc` of each node |
| Which accessibility events fire | `adb shell uiautomator events` | Event type and text as focus moves |
| What is in the foreground | `adb shell dumpsys activity activities \| grep mResumedActivity` | Check before driving the device — it may be someone's TV |

`adb shell input keyevent <code>` drives the same key path as the remote: 85 Play/Pause, 89 Rewind, 90 Fast Forward, 19–22 D-pad, 23 Select, 4 Back, 82 Menu.

## What you cannot capture

- `adb shell screenrecord` on Android 9 records **video only**; its source declares a single `video/avc` track (`frameworks/av`, `cmds/screenrecord/screenrecord.cpp`).
- `scrcpy` forwards audio only on **Android 11+**.
- *Measured:* `screenrecord` also left the **video area blank** when the video played on a `SurfaceView`; moving playback to a `TextureView` made it visible but recorded at about 4 fps at 1080p.

So there is no software route that records a Fire OS 7 device's picture and sound together. To show or check what a viewer hears, film the TV with a camera, or use an HDMI capture device (whether HDCP blocks it on your content is untested here), and line the recording up against the app's own log. For **level** checks without a capture, a debug-only output meter using `Visualizer` on session 0 works ([audio-ducking.md](audio-ducking.md#loudness)).

## Traps that only show on the device

- **Regex.** Android's `java.util.regex` is ICU-based and stricter than the desktop JVM's. *Measured:* `\{[^}]*}` (a bare closing brace) compiles on the JVM and in Robolectric, and throws `PatternSyntaxException` on the device. Escape braces (`\{[^}]*\}`), and run anything that parses text at least once on a device or emulator.
- **Raw resources opened by file descriptor.** Media3's `RawResourceDataSource` calls `Resources.openRawResourceFd`, which fails for a **compressed** APK entry ("This file can not be opened as a file descriptor; it is probably compressed"). Extensions not on `aapt`'s default no-compress list, such as `.srt`, are compressed. Add them in Gradle: `androidResources { noCompress += "srt" }`. A subtitle sidecar on the same `MediaItem` that fails to open can take down playback of the whole item.
- **Compose for TV dependencies.** `androidx.tv:tv-foundation` 1.0.0 is effectively empty (its lazy lists moved into `compose-foundation` 1.7) yet forces `compileSdk` 35, AGP 8.6+ and a Kotlin 2.1 standard library onto the build. If the code only uses `androidx.tv.material3`, depend on `tv-material` alone.
- **`minSdk` vs `compileSdk`.** `minSdk` decides whether the device installs the APK; raising `compileSdk` does not raise the device floor.

## Test with VoiceView on — and on a fresh device

- Turn VoiceView on (Back + Menu, held for two seconds), repeat the main flows, and read the `VoiceViewEventProvider` lines alongside your own log.
- Test text-to-speech on a device where VoiceView has **never** been enabled; it behaves differently from one where it has ([text-to-speech.md](text-to-speech.md#the-silent-default-engine)).
- Leave the device as you found it: VoiceView setting restored, your app closed.
