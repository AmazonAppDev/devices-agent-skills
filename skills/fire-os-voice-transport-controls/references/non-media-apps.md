# Voice transport controls for apps that aren't video players

The pattern below uses the platform `android.media.session.MediaSession` (API 21+), so it needs no extra
dependency. `androidx.media.session.MediaSessionCompat` works the same way.

## The code

```kotlin
class BoardActivity : ComponentActivity() {
    private lateinit var session: MediaSession

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        session = MediaSession(applicationContext, "Class board").apply {
            setCallback(object : MediaSession.Callback() {
                override fun onPause() = board.pause()         // "Alexa, pause": never a toggle
                override fun onPlay() = board.resume()         // "Alexa, resume" / "Alexa, play"
                override fun onStop() = board.pause()          // "Alexa, stop": a wall screen pauses
                override fun onSkipToNext() = board.next()     // "Alexa, next"
                override fun onSkipToPrevious() = board.previous()
            })
            isActive = true
        }
        publish()
    }

    /** Call after every change of what the screen can do. */
    private fun publish() {
        val actions = PlaybackState.ACTION_PLAY or PlaybackState.ACTION_PAUSE or
            PlaybackState.ACTION_PLAY_PAUSE or PlaybackState.ACTION_STOP or
            (if (board.slideCount > 1) PlaybackState.ACTION_SKIP_TO_NEXT or PlaybackState.ACTION_SKIP_TO_PREVIOUS else 0L)
        val state = if (board.paused) PlaybackState.STATE_PAUSED else PlaybackState.STATE_PLAYING
        session.setPlaybackState(
            PlaybackState.Builder()
                .setActions(actions)
                .setState(state, PlaybackState.PLAYBACK_POSITION_UNKNOWN, if (board.paused) 0f else 1f)
                .build(),
        )
    }

    override fun onStart() { super.onStart(); session.isActive = true }
    override fun onStop() { session.isActive = false; super.onStop() }
    override fun onDestroy() { session.release(); super.onDestroy() }
}
```

And in `AndroidManifest.xml`:

```xml
<uses-permission android:name="com.amazon.permission.media.session.voicecommandcontrol" />
```

## What to advertise

Fire OS reads the session's `PlaybackState`. List the actions the screen can perform **right now**:

| The screen | State | Actions |
|---|---|---|
| Nothing to control (a loading or setup screen) | `STATE_NONE` | none |
| A timer running | `STATE_PLAYING` | play, pause, play/pause, stop |
| A timer paused, with slides to page | `STATE_PAUSED` | play, pause, play/pause, stop, next, previous |
| Slides rotating, nothing to pause | `STATE_PLAYING` (the slideshow is what's playing) | next, previous |
| Something seekable | `STATE_PLAYING`/`STATE_PAUSED` | add fast forward, rewind |

- Use speed `1f` while playing and `0f` otherwise. Position can be `PLAYBACK_POSITION_UNKNOWN` unless the app
  supports "Alexa, fast forward 30 seconds", which arrives as `onSeekTo(absolutePosition)` and needs a real position.
- A stale state is how "Alexa, next" ends up offered on a screen with one slide. Update the state on every change;
  it's cheap.

## Voice vs keys

| Input | Means | Callback / key | Do |
|---|---|---|---|
| "Alexa, pause" | *be paused* | `onPause()` | pause; if already paused, do nothing |
| "Alexa, resume" | *be playing* | `onPlay()` | resume; if already playing, do nothing |
| Remote Play/Pause key | *the other state* | `KEYCODE_MEDIA_PLAY_PAUSE` | toggle |

If the voice callbacks reuse a toggle, the second "Alexa, pause" in a noisy gym resumes the class. Keep a
"set state" function for voice and a "toggle" for the key.

## Remote keys

Handle them in `Activity.dispatchKeyEvent`, on `ACTION_DOWN` with `repeatCount == 0`. When you consume a press,
also consume its repeats and its `ACTION_UP`, so a held key fires once and the release doesn't leak into the UI.

| Key | Code | Notes |
|---|---|---|
| Play/Pause | `KEYCODE_MEDIA_PLAY_PAUSE` | toggle |
| Fast-forward / Rewind | `KEYCODE_MEDIA_FAST_FORWARD` / `KEYCODE_MEDIA_REWIND` | the Fire TV remote has no Next/Previous keys; screens without a timeline can use these to page |
| Menu | `KEYCODE_MENU` | a status or help panel |
| Left / Right | `KEYCODE_DPAD_LEFT` / `KEYCODE_DPAD_RIGHT` | only on screens with nothing focusable |
| Select | `KEYCODE_DPAD_CENTER`, `KEYCODE_ENTER` | only on screens with nothing focusable |
| Back, Home | | never consume |

Handle Play/Pause in `dispatchKeyEvent` rather than counting on the system to route it: a media key the activity
doesn't consume goes to the "media button session", which is the app that last played audio. On a screen that never
plays sound, that may be some other app.

The microphone button always goes to Alexa; apps can't intercept it.

## Fire OS pauses the app in front on Home

When the user presses Home, Fire OS's key policy (in the system server) sends `onPause()` to the session of the
app in front, about 150 ms **before** the activity's own `onPause`. Lifecycle callbacks can't filter it out.
For a video that's right. For a screen whose state is shared, such as a class timer shown on every TV in a gym,
one person leaving the app on one TV would pause the class everywhere.

Tell it apart by the caller, which is available inside a callback on API 28+ (Fire OS 7 and later):

```kotlin
override fun onPause() {
    val caller = if (Build.VERSION.SDK_INT >= 28) session.currentControllerInfo else null
    if (caller?.uid == Process.SYSTEM_UID) return // Fire OS on Home, not a person
    board.pause()
}
```

Alexa's voice service and the Fire TV mobile app are ordinary apps with their own uids. A debug adb hook calls from
the app's own process. Log `caller.packageName` and `caller.uid` with every command so the next surprise is easy
to spot.

## Gotchas

- **Debug logs vanish.** Fire OS drops `Log.d` lines. Log received commands at `Log.i` so
  `adb logcat -s <tag>` shows them.
- **Context.** Create the session with `applicationContext` and release it in `onDestroy`. A leaked active session
  keeps taking commands after the activity is gone.
- **Lint.** Overriding `dispatchKeyEvent` in a `ComponentActivity` raises a `RestrictedApi` lint error, because
  androidx marks its own override as restricted. `Activity.dispatchKeyEvent` is public API, so
  `@SuppressLint("RestrictedApi")` on the override is the usual fix.
- **Which session wins.** `adb shell dumpsys media_session` lists the sessions, their state and whether they are
  active. Look for yours there first when nothing reaches it.
