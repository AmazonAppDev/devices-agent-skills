# Trigger prompts

Use these routing fixtures with only the skills' names and descriptions visible.
The expected result is whether `playhead-safe-ai` should load.

## Should load

1. Add a spoiler-safe “what did I miss?” card to a Fire TV video player.
2. Summarize only the scenes before the viewer's current playhead.
3. Build a “who is that?” action that must not name future characters.
4. Our media assistant leaks events after a user seeks backward; review the data flow.
5. How should an AI recap tool be scoped to a live stream viewer's position?
6. Validate a model response against the timeline boundary before displaying it.
7. Store recap style preferences without storing subtitles or plot facts.
8. Design cache keys for a time-bounded video explanation service.
9. Test that a future-only entity cannot reach an on-screen identification card.
10. Make an agent invalidate stale context after an episode or timeline revision.

## Should not load

1. Add `TVFocusGuideView` to a React Native Vega modal.
2. Migrate a Vega app to a multi-platform React Native monorepo.
3. Implement VoiceView support in a native Fire OS Kotlin app.
4. Build a generic customer-support chatbot with no media timeline.
5. Recommend movies based on a viewer's genre preferences.
6. Fix a WebVTT parser that does not display captions at all.
7. Optimize an HLS CDN cache with no AI-generated context feature.
8. Add OAuth login to a streaming application.
9. Build an Alexa+ Agent Skill for shopping.
10. Improve color contrast and typography in a TV home screen.

The negative cases are deliberate: the skill is about a temporal evidence
boundary for media AI, not general TV UI, accessibility, recommendations,
caption rendering, or unrelated agents.
