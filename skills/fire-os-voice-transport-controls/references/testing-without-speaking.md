# Testing voice transport controls without speaking

A spoken "Alexa, pause" needs a person and a microphone. Everything after speech recognition can be tested from a
script: Fire OS's voice service ends up calling `MediaController.TransportControls` on the app's session, and so
can a test.

**Why not `adb shell media dispatch pause`?** On Fire OS 7 it goes to the "media button session", which is the
app that last played audio. A screen that never plays sound gets nothing ("Media button session is null").
`adb shell media monitor` fails with a missing-permission error. Use the layers below instead.

## Layers

| Layer | Proves | Runs on |
|---|---|---|
| Unit tests | the state → actions mapping and key → command mapping, including held keys | JVM |
| On-device test | the session receives each transport control through the system service, and the PlaybackState Fire OS reads is right | a Fire TV, `connectedDebugAndroidTest` |
| adb hook | the real app reacts to each command, in a debug build | a Fire TV, from a shell or CI |
| End to end with screenshots | what the screen shows after each command or key | a Fire TV |

Keep the mapping (what to advertise, which key means what) in pure functions so the JVM tests can cover it:
`PlaybackState` and `KeyEvent` constants are compile-time constants, so the tests need no Android runtime.

## On-device test

```kotlin
@RunWith(AndroidJUnit4::class)
class TransportControlsTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext
    private val received = LinkedBlockingQueue<String>()
    private lateinit var session: MediaSession

    @Before fun setUp() = instrumentation.runOnMainSync {
        session = MediaSession(context, "test").apply {
            setCallback(object : MediaSession.Callback() {
                override fun onPause() { received += "pause" }
                override fun onSkipToNext() { received += "next" }
            })
            isActive = true
        }
    }

    @After fun tearDown() = instrumentation.runOnMainSync { session.release() }

    @Test fun voiceCommandsReachTheSession() {
        val transport = MediaController(context, session.sessionToken).transportControls
        transport.pause()
        assertEquals("pause", received.poll(5, TimeUnit.SECONDS))
        transport.skipToNext()
        assertEquals("next", received.poll(5, TimeUnit.SECONDS))
    }
}
```

`setPlaybackState` reaches the session service asynchronously. When you assert on
`MediaController.playbackState`, poll for up to a few seconds instead of reading it once.

## The adb hook

A debug-only receiver that turns a broadcast into the same `TransportControls` call:

```kotlin
// In the class that owns the session; register only when BuildConfig.DEBUG.
private val testHook = object : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val transport = session.controller.transportControls
        when (intent.getStringExtra("cmd")) {
            "play" -> transport.play()
            "pause" -> transport.pause()
            "stop" -> transport.stop()
            "next" -> transport.skipToNext()
            "previous" -> transport.skipToPrevious()
        }
    }
}

// adb's broadcasts come from the shell user, so the receiver has to be exported.
val filter = IntentFilter("${context.packageName}.debug.VOICE")
if (Build.VERSION.SDK_INT >= 33) context.registerReceiver(testHook, filter, Context.RECEIVER_EXPORTED)
else context.registerReceiver(testHook, filter)
```

```bash
adb shell am broadcast -a com.example.app.debug.VOICE -p com.example.app --es cmd pause
```

Never register it in release builds: any app could then pause the screen.

## End to end with screenshots

```bash
adb shell input keyevent KEYCODE_WAKEUP
adb shell am start -W -n com.example.app/.MainActivity
adb shell am broadcast -a com.example.app.debug.VOICE -p com.example.app --es cmd pause
sleep 1; adb exec-out screencap -p > 01-pause.png
adb shell input keyevent KEYCODE_MEDIA_PLAY_PAUSE      # the remote's Play/Pause, through dispatchKeyEvent
sleep 1; adb exec-out screencap -p > 02-key-toggle.png
adb logcat -d -s <your-log-tag>:I                       # the commands the session delivered
```

`input keyevent` sends keys to the focused window, so it exercises `dispatchKeyEvent` exactly as the remote does.
On Git Bash for Windows, set `MSYS_NO_PATHCONV=1` so the paths in these commands aren't rewritten.

## Test cases worth having

- Each advertised action arrives as its callback; an action that isn't advertised is absent from the PlaybackState.
- "pause" sent twice leaves the screen paused (catches a voice callback wired to a toggle).
- After `onStop`, the session is inactive; after `onStart`, active again.
- With an activity in front, `input keyevent KEYCODE_HOME` delivers `onPause()` from uid 1000 (Fire OS only): assert the
  app ignores it if its state is shared. Put an activity in front first; Fire OS only pauses the app on screen.
- A held D-pad key pages once; a key the screen declines still moves focus.
