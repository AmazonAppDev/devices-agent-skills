---
name: fire-os-voice-transport-controls
description: Add and test Alexa voice transport controls ("Alexa, pause", "Alexa, resume", "Alexa, stop", "Alexa, next", "Alexa, previous", "Alexa, fast forward", "Alexa, rewind") and the remote's transport keys in native Fire OS apps (Kotlin/Java), including apps that are not video players, such as timers, slideshows, dashboards, signage and games. Covers the Fire OS voice permission, MediaSession and PlaybackState actions, voice-versus-key semantics, session lifecycle, and testing voice commands from adb or instrumented tests without speaking. Use when asked to make a Fire TV app respond to Alexa playback commands, wire up Play/Pause or Next on the Fire TV remote, or find out why "Alexa, pause" does nothing.
---

# Fire OS Voice Transport Controls

Fire TV hands Alexa's transport commands, spoken into the remote or to a paired Echo, to the **MediaSession of the
app on screen** ([Amazon's guide](https://developer.amazon.com/docs/fire-tv/mediasession-api-integration.html)).
Video players get most of this from their player library. Every other kind of app (a class timer, a slideshow, a
dashboard, a menu board, a game) has to build it, and the mistakes are quiet: no crash, no log, Alexa just doesn't
do anything. This skill helps an agent add the controls correctly and, just as important, **test them without
anyone speaking to the TV**.

## Check before applying

1. **Native Fire OS app?** There's an `AndroidManifest.xml` and Kotlin/Java sources. A Vega OS app
   (`@amazon-devices/react-native-kepler` in `package.json`) uses a different API, so this skill doesn't apply.
2. **Does a player already own a session?** If the app plays video or audio through Media3/ExoPlayer with a
   `androidx.media3.session.MediaSession`, the player already maps play, pause and seek. Usually only the permission
   (step 1 below) and the tests are missing. Read [non-media-apps.md](references/non-media-apps.md) only for the
   commands the player doesn't cover, such as next/previous on a non-playlist screen.
3. **Run the audit:** `bash references/scripts/audit.sh <project-dir>`. It has no dependencies and exits 1 on
   findings. It only catches what's visible statically (permission, session, actions, active flag, toggle-on-pause);
   read each finding in context.

## Workflow

1. **Permission.** Add
   `<uses-permission android:name="com.amazon.permission.media.session.voicecommandcontrol" />` to the app's manifest.
   Without it Fire OS doesn't deliver voice transport commands. Other Android devices ignore it.
2. **One session, created on the main thread,** with a callback for each command the screen supports, then
   `isActive = true`. A screen with no audio still qualifies.
3. **Advertise only what the screen can do now.** Set a `PlaybackState` whose actions list the supported commands,
   and update it whenever that changes. If nothing can be controlled, use `STATE_NONE` with no actions, which is
   better than offering a command the screen ignores. See the table in
   [non-media-apps.md](references/non-media-apps.md#what-to-advertise).
4. **Voice is not a toggle.** `onPause()` must pause and `onPlay()` must resume. Only the remote's Play/Pause
   *key* toggles. If `onPause` calls a toggle, a second "Alexa, pause" resumes the class.
5. **Lifecycle.** Set `isActive = false` in `onStop` and back to `true` in `onStart`, so "Alexa, pause" said while
   another app is in front never reaches this one. Call `release()` in `onDestroy`. Fire OS also sends
   `onPause()` from the system when Home is pressed; ignore it if the screen's state is shared (see the reference).
6. **Remote keys.** Handle transport keys in `Activity.dispatchKeyEvent`. Take the D-pad and select keys only on
   screens with nothing focusable (signage, timers); a menu needs them for focus. Never take Back or Home.
7. **Test without speaking.** Add the debug-only adb hook and the tests in
   [testing-without-speaking.md](references/testing-without-speaking.md). `adb shell media dispatch` is not
   enough: on Fire OS 7 it never reaches a session that hasn't played audio.

**Shortcut:** if adding a dependency is fine, the Apache-2.0 library
[firetv-voice-controls](https://github.com/tapaderuza/firetv-voice-controls) packages steps 1–7 (permission merge,
`Controls` → `PlaybackState`, `RemoteKeys`, the adb hook and `scripts/alexa.sh`), verified on a Fire TV Stick.

## References

| Topic | File |
|---|---|
| The pattern for apps that aren't video players: code, what to advertise, voice vs keys, lifecycle, gotchas | [non-media-apps.md](references/non-media-apps.md) |
| Unit tests, on-device tests with a MediaController, the adb hook, end-to-end with screenshots | [testing-without-speaking.md](references/testing-without-speaking.md) |
| Static checks | [scripts/audit.sh](references/scripts/audit.sh) |

## Decision tree

```
"Alexa, pause" does nothing
├─ Permission missing from the merged manifest   → Workflow 1 (audit.sh finds it)
├─ Session never set active / released too early  → Workflow 2, 5
├─ Action missing from the PlaybackState          → non-media-apps.md#what-to-advertise
├─ Works once, then the second "pause" resumes    → Workflow 4
├─ The class pauses when someone presses Home     → non-media-apps.md#fire-os-pauses-the-app-in-front-on-home
└─ Another app's session wins                     → Workflow 5; check `adb shell dumpsys media_session`

Adding controls to a new screen
├─ Plays media with Media3/ExoPlayer              → Check before applying, step 2
├─ Timer / slideshow / dashboard / game           → non-media-apps.md
└─ Remote keys (Play/Pause, FF/RW, D-pad, Menu)   → non-media-apps.md#remote-keys

Proving it works
├─ No microphone / CI                             → testing-without-speaking.md#the-adb-hook
├─ Instrumented test on a Fire TV                 → testing-without-speaking.md#on-device-test
└─ Screenshots for a PR or a store listing        → testing-without-speaking.md#end-to-end-with-screenshots
```

## What needs a human

The adb hook and the on-device tests drive the session through a `MediaController`, which goes through the system
media session service just as Fire OS's voice service does. They don't cover speech recognition. Before a
release, have someone say "Alexa, pause" and "Alexa, next" to the TV once, and flag that step for the user
instead of claiming it was done.
