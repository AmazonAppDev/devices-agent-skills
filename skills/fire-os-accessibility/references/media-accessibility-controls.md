# Captions, audio description and spoken subtitles

What a video player on Fire TV should offer, and where the controls go. The requirements come from **ETSI EN 301 549 (V3.2.1), clause 7**, the part of the European ICT accessibility standard that covers video players. The European Accessibility Act has applied since 28 June 2025, and streaming devices and services are in its scope, so expect these requirements to matter in the EU. The clause summaries below are paraphrased: read the clause text in the standard before claiming conformance.

## Clause 7, in short

| Clause | Requirement (paraphrased) |
| --- | --- |
| 7.1.1–7.1.2 | Where video with synchronised audio is shown, the player can display the available captions, kept in sync with the audio |
| 7.1.3 | Caption data is preserved through transmission, conversion and recording |
| 7.1.4 | The user can adapt how captions look (size, font, colours, background, opacity) |
| 7.1.5 | Where captions are available, a mode that **speaks** them (spoken subtitles) |
| 7.2.1–7.2.3 | The player can select and play available audio description, kept in sync |
| **7.3** | Controls for captions and audio description are offered **at the same level of interaction as the primary media controls** (play, pause, volume), not buried in a settings tree |

## Where the controls go

Clause 7.3 is the one an agent most often misses. For a TV player that means:

- Caption, audio description and spoken-subtitle toggles sit **in the playback controls**, one D-pad move from Play/Pause — for example a second row directly below the transport bar.
- Each toggle is a focusable, labelled control that says its state: "Audio description, off", not an icon alone.
- Reaching them needs no special button (Menu and chords may belong to VoiceView; see [remote-and-voice-input.md](remote-and-voice-input.md)).

## State: per title, off by default

Users report that once audio description is switched on for Fire TV, it can **stay on for all content**, and forum answers suggest a factory reset to clear it ([Amazon Forum](https://www.amazonforum.com/s/question/0D54P00006zSsxKSAS/audio-description-wont-turn-off)). Whatever the cause, it is a pattern to avoid in your own player:

- Store the audio description choice **per title**, with a global default of off, unless the user sets it globally on purpose.
- Make every setting reversible from the same place it was turned on.

## Spoken subtitles and audio description together

If the player speaks subtitles and plays audio description, and VoiceView may be on as well, the voices will collide unless one component decides who speaks. Fire OS has no platform arbiter for this, so the app must be its own:

- **One voice at a time.** Keep a single owner of "the floor" for everything the app says (descriptions, spoken subtitles, UI narration) and yield it to VoiceView when VoiceView takes audio focus ([voiceview.md](voiceview.md#apps-that-speak-for-themselves)).
- **Book subtitles first.** A spoken subtitle is tied to a line of dialogue and can't move. A description that would still be talking when the next subtitle is due should not start, even if the film is silent right now.
- **Only speak what fits.** Start a description only if its measured duration fits the gap in the dialogue ([text-to-speech.md](text-to-speech.md#durations-differ-between-engines)); drop it otherwise, rather than playing it late or over speech.
- **Say that the voice is synthetic** if descriptions are machine-generated or read by a synthetic voice, once per session, and show the same line on screen.
- **Duck the content under every voice** the app speaks ([audio-ducking.md](audio-ducking.md)).
