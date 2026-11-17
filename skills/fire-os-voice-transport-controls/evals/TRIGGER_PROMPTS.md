# Trigger prompts

Prompts the skill should and shouldn't activate on, for checking the `description` field.

## Should trigger

- "Make my Fire TV workout timer pause when I say 'Alexa, pause'."
- "'Alexa, next' doesn't do anything in my Fire TV slideshow app. Why?"
- "Add Play/Pause and fast-forward support for the Fire TV remote to my Kotlin dashboard app."
- "How do I test Alexa voice commands on Fire TV from a CI script?"
- "adb shell media dispatch pause does nothing on my Fire TV Stick."
- "Which permission does a Fire OS app need for Alexa transport controls?"
- "My Fire TV app resumes when the user says 'Alexa, pause' a second time."

## Should not trigger

- "Build an Alexa skill that answers questions about my gym's schedule." (Alexa Skills Kit, not Fire OS)
- "Add focus management to my React Native TV app." (rn-tv-ui-best-practices)
- "Migrate my Vega OS app to Android TV." (vega-multi-tv-migration)
- "Make my Fire TV app work with VoiceView." (accessibility, not transport controls)
- "Play an HLS stream with ExoPlayer on Fire TV." (playback itself, not voice control)
