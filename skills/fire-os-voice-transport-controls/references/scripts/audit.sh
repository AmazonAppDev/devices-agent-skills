#!/usr/bin/env bash
# Static checks for Alexa voice transport controls in a native Fire OS project.
# Usage: bash audit.sh [project-dir]. No dependencies. Exits 1 if anything needs attention.
# It only sees what grep can see: read each finding in context before changing code.
set -uo pipefail

root="${1:-.}"
findings=0
pass() { printf '  ok    %s\n' "$1"; }
flag() { printf '  FIX   %s\n' "$1"; findings=$((findings + 1)); }
info() { printf '  note  %s\n' "$1"; }

sources() { grep -rlE --include='*.kt' --include='*.java' "$1" "$root" 2>/dev/null | grep -v '/build/'; }
manifests=$(find "$root" -name AndroidManifest.xml -not -path '*/build/*' 2>/dev/null)
gradle_files=$(find "$root" \( -name '*.gradle' -o -name '*.gradle.kts' -o -name '*.toml' \) -not -path '*/build/*' 2>/dev/null)

echo "Fire OS voice transport controls: $root"

if [ -z "$manifests" ]; then
  echo "  no AndroidManifest.xml found: not a native Android/Fire OS project, so this check doesn't apply."
  exit 0
fi

uses_library=false
if [ -n "$gradle_files" ] && grep -qs 'firetv-voice-controls' $gradle_files; then uses_library=true; fi

# 1. Permission
if grep -qs 'com.amazon.permission.media.session.voicecommandcontrol' $manifests; then
  pass "voice permission in the manifest"
elif $uses_library; then
  pass "voice permission (merged from the firetv-voice-controls library)"
else
  flag "no manifest requests com.amazon.permission.media.session.voicecommandcontrol: Fire OS won't deliver Alexa transport commands"
fi

# 2. A session
media3=$(sources 'androidx\.media3\.session\.MediaSession')
platform=$(sources '(android\.media\.session\.MediaSession|MediaSessionCompat)\b')
if $uses_library; then
  pass "session provided by firetv-voice-controls (VoiceControls)"
elif [ -n "$media3" ]; then
  pass "Media3 MediaSession (the player maps play/pause/seek; check next/previous separately)"
elif [ -n "$platform" ]; then
  pass "MediaSession in: $(echo "$platform" | xargs -n1 basename | sort -u | tr '\n' ' ')"
else
  flag "no MediaSession, MediaSessionCompat or Media3 session: nothing can receive \"Alexa, pause\""
fi

# 3-4. Platform/compat sessions must be activated and must advertise actions
if [ -n "$platform" ] && ! $uses_library; then
  if grep -qsE 'isActive\s*=\s*true|setActive\(\s*true\s*\)' $platform; then
    pass "session is set active"
  else
    flag "session never set active (isActive = true / setActive(true))"
  fi
  if grep -qsE 'setActions\(' $platform; then
    pass "PlaybackState lists actions"
  else
    flag "no PlaybackState.Builder().setActions(...): Alexa is offered nothing"
  fi
  if grep -qsE 'setActive\(\s*false\s*\)|isActive\s*=\s*false' $platform; then
    pass "session is deactivated somewhere (onStop?)"
  else
    info "session is never deactivated: consider isActive = false in onStop so another app's \"Alexa, pause\" can't reach it"
  fi
fi

# 5. Voice callbacks wired to a toggle
toggles=$(grep -nsE -A3 'fun onPause\(\)|void onPause\(\)' $platform $media3 2>/dev/null | grep -iE 'toggle' | head -3)
if [ -n "$toggles" ]; then
  flag "onPause() appears to call a toggle: a second \"Alexa, pause\" would resume. Lines:"
  echo "$toggles" | sed 's/^/          /'
fi

# 6. Remote keys and the debug hook (informational)
if [ -n "$(sources 'KEYCODE_MEDIA_PLAY_PAUSE')" ] || $uses_library; then
  pass "the remote's Play/Pause key is handled"
else
  info "KEYCODE_MEDIA_PLAY_PAUSE isn't handled in code: an unhandled media key goes to the app that last played audio, which may not be this one"
fi
if [ -n "$(sources 'transportControls')" ] || $uses_library; then
  pass "something drives transportControls (a test or an adb hook)"
else
  info "no test or adb hook drives transportControls: see testing-without-speaking.md"
fi

echo
if [ "$findings" -eq 0 ]; then echo "No findings."; else echo "$findings finding(s)."; fi
[ "$findings" -eq 0 ]
