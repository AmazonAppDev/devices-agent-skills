# Trigger and Non-Trigger Prompts

Use these prompts to evaluate whether the skill description activates at the right time.

Expected behavior:
- **Trigger** prompts should use `vega-tv-accessibility`.
- **Non-trigger** prompts should not use `vega-tv-accessibility` unless the user adds accessibility context.

## Trigger Prompts

1. "Review accessibility for our Vega TV app. It has both WebView screens and native React Native for Vega settings pages."
2. "VoiceView reads every movie tile twice in my Vega WebView app. Help me fix it."
3. "Audit this native React Native for Vega playback screen for screen reader and D-pad accessibility."
4. "Our TV app loses focus after closing a modal with the Back button. What should we check?"
5. "Check whether this app should use `aria-live` or `AccessibilityInfo.announceForAccessibility` for loading messages."
6. "Create an accessibility checklist for a Vega media app with captions, magnifier, and remote navigation."
7. "The focused item and spoken item do not match in VoiceView on a React Native for Vega rail."
8. "Fix accessibility labels and roles for a Vega WebView carousel."
9. "Review our TV app for WCAG 2.2 AA issues around contrast, focus visible, and captions."
10. "Determine if this Vega app is WebView or native RN before giving accessibility fixes."

## Non-Trigger Prompts

1. "Migrate our Vega app into a multi-platform React Native monorepo."
2. "Set up Yarn workspaces for an Android TV and Apple TV project."
3. "Debug Metro module resolution for `@amazon-devices/react-native-kepler`."
4. "Add a new GitHub Actions workflow for weekly triage summaries."
5. "Update the README with installation instructions for skills.sh."
6. "Create a package.json for an Expo TV app."
7. "Explain how VMRP maps React Native imports for Vega."
8. "Convert this JavaScript component to TypeScript."
9. "Fix a failing unit test in the media playback reducer."
10. "Create a release note for a new Fire TV app version."

## Description Optimization Notes

If trigger prompts miss the skill, add or clarify terms in the description such as:
- Vega TV accessibility
- VoiceView
- D-pad or remote navigation
- Vega WebView accessibility
- React Native for Vega accessibility
- captions/subtitles
- magnifier

If non-trigger prompts activate the skill too often, narrow the description around accessibility-specific work instead of generic Vega, migration, or monorepo tasks.
