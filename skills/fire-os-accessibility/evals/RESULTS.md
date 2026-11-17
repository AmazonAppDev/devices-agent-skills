# Results

Run 2026-09-29. Answering model: Claude Sonnet 5, fresh context, no file or web access except (for "with skill") the skill's `SKILL.md` and `references/`. Graded against the assertions in [TASK_SCENARIOS.md](TASK_SCENARIOS.md).

## Task scenarios

| Scenario | Without skill | With skill |
| --- | --- | --- |
| S1 Silent text-to-speech | 1/4 | 4/4 |
| S2 Voice search from the remote | 2/3 | 3/3 |
| S3 Menu long-press shortcut | 1/2 | 2/2 |
| S4 Two voices at once | 1/4 | 4/4 |
| S5 A 10 ms duck | 2/3 | 3/3 |
| S6 Narration too loud | 3/3 | 3/3 |
| S7 Measuring the film's loudness | 3/3 | 3/3 |
| S8 Where the accessibility controls go | 2/3 | 3/3 |
| S9 VoiceView for a movie grid | 0/3 | 3/3 |
| S10 Recording a demo with sound | 2/3 | 3/3 |
| S11 Regex crash only on the device | 3/3 | 3/3 |
| **Assertions passed** | **20/34 (59%)** | **34/34 (100%)** |
| **Scenarios fully passed** | **3/11** | **11/11** |

## What the baseline got wrong

Beyond missed assertions, the answer without the skill gave advice that fails on a Fire TV:

- **S2:** recommended `SpeechRecognizer` with `RECORD_AUDIO` for in-app voice. Fire OS has no Google Play Services to back it.
- **S1:** checked `isLanguageAvailable` and suggested `ACTION_INSTALL_TTS_DATA`, but never said to select the engine by its voice count or to implement the deprecated `onError` overload, the only error signal on this path.
- **S3:** said a Menu long press opens the system quick settings. Amazon documents it as VoiceView's Review Mode.
- **S4:** suggested the app itself request `AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK`, rather than holding focus to be told when VoiceView speaks.
- **S5:** said volume steps "may click". The mixer ramps every change across a buffer, so they don't.
- **S8:** suggested remembering the audio description choice globally across sessions, the pattern behind users' "audio description stuck on" reports.
- **S9:** named no Amazon extras (`usageHint.remote`, `orientationText`, `describedBy`), only generic Android collection info.

Where the baseline was already right (S6, S7, S11), the skill added the source-level reasons (AOSP mixer code, the API-level table) and the measured figures.

## Trigger prompts

A fresh agent (Claude Sonnet 5) was given only the `name` and `description` of the three skills in this repository and asked which it would load for each prompt in [TRIGGER_PROMPTS.md](TRIGGER_PROMPTS.md). This simulates the choice from descriptions; it is not a run through any particular host's skill router.

| | Result |
| --- | --- |
| Should trigger: loaded `fire-os-accessibility` | 10/10 |
| Should not trigger: did not load it | 10/10 |

The same run picked `rn-tv-ui-best-practices` for the React Native focus and swimlane prompts and `vega-multi-tv-migration` for the Vega migration prompt, so the new description does not take prompts that belong to the existing skills.
