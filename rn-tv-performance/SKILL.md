---
name: rn-tv-performance
description: Audit, measure, and optimize performance for React Native TV applications, with Vega-specific guidance for React Native for Vega and Vega WebView apps. Use when investigating app launch latency, UI fluidity, video fluidity, memory, CPU usage, overdraw, jank, slow lists, re-renders, WebView performance, Web Workers, WebGL, profiling, Vega KPI Visualizer results, TTFF, TTFD, or TTFVF.
---

# RN TV Performance

## Overview

Measure before optimizing. Help agents diagnose and improve React Native TV app performance across native TV surfaces, with Vega-specific guidance for React Native for Vega, Vega WebView, official Vega KPIs, and Vega Studio profiling tools.

Always identify the app surface first because generic React Native TV, React Native for Vega, and Vega WebView apps use different APIs, tools, and performance tactics.

## When to Apply

Use this skill when user mentions:
- React Native TV app performance, slow startup, launch latency, responsiveness, or release-readiness
- UI jank, poor fluidity, slow D-pad navigation, frame drops, or unresponsive screens
- Video startup, Time-to-First Video Frame, buffering, dropped frames, or video fluidity
- High CPU usage, memory growth, crashes, background memory, or profiling
- React Native re-renders, FlatList, FlashList, memoization, concurrent rendering, or image/list performance
- Vega app performance, React Native for Vega, Vega WebView, TTFF, TTFD, TTFVF, or report fully drawn
- Vega KPI Visualizer, Activity Monitor, Recording View, Perfetto, Chrome DevTools, overdraw, or flamegraphs

## Phase Priority Guide

| Priority | Phase | Impact | When to Use |
|----------|-------|--------|-------------|
| 1 | App Surface Detection | CRITICAL | Before recommending platform-specific fixes |
| 2 | Baseline Measurement | CRITICAL | Before optimizing launch, fluidity, memory, or video |
| 3 | Tool Selection | HIGH | Choose KPI Visualizer, Activity Monitor, CDT, Perfetto, or overdraw |
| 4 | Root Cause Analysis | HIGH | Map symptoms to CPU, memory, rendering, network, list, video, or WebView causes |
| 5 | Targeted Fix | HIGH | Apply the smallest source-aligned fix and re-measure |

## Quick Decision Tree

```
What is slow?
+-- Launch or resume?
|   +-- Measure platform launch metrics; for Vega, measure TTFF/TTFD and verify reportFullyDrawn/useReportFullyDrawn
+-- UI interaction, scrolling, D-pad, or animation?
|   +-- Measure ui-fluidity; inspect re-renders, overdraw, render thread, and JS thread
+-- Video startup or playback?
|   +-- Measure video-fluidity and TTFVF; check hardware decode and media setup
+-- Memory or crash?
|   +-- Measure foreground/background memory; inspect Activity Monitor recordings
+-- Native React Native TV screen?
|   +-- Use RN TV guidance for memoization, lists, images, render work, and navigation responsiveness
+-- WebView page or HTML app?
|   +-- Use WebView guidance for network, JS, cache, Web Workers, WebGL, video
+-- Vega app?
|   +-- Use Vega KPI and profiling guidance for official metrics and tooling
+-- Unknown?
    +-- Inspect manifest.toml, package.json, app entry points, WebView usage, and rendered flows
```

## Quick Reference

### Detect App Surface

```bash
# Generic React Native TV indicators
rg "react-native|react-native-tvos|@react-native|FlatList|FlashList|TVEventHandler|hasTVPreferredFocus"

# Vega package marker
find . -name manifest.toml -maxdepth 5

# WebView indicators
rg "@amazon-devices/webview|<WebView|webview.html|ReactNativeWebView|postMessage"

# React Native for Vega indicators
rg "@amazon-devices/react-native-kepler|react-native-vega|build:app|vega project|FlatList|FlashList"
```

### Vega Measurement Commands

```bash
# Check host and target readiness
vega exec perf doctor

# Default cool-start TTFF and TTFD
vega exec perf kpi-visualizer --app-name=<interactive-component-id>

# Explicit iteration count
vega exec perf kpi-visualizer --app-name=<interactive-component-id> --iterations <count>

# UI fluidity with a test scenario
vega exec perf kpi-visualizer --app-name=<interactive-component-id> --kpi ui-fluidity --test-scenario <scenario.py>

# Activity Monitor with CPU profiling
vega exec perf activity-monitor --record-cpu-profiling --app-name=<interactive-component-id> --sourcemap-file-path=<source-map>
```

### Vega KPI Targets

- Cool start TTFF: less than 1.5 s
- Warm start TTFF: less than 0.5 s
- Cool start TTFD: less than 8.0 s
- Warm start TTFD: less than 1.5 s
- Foreground memory: less than 400 MiB
- Background memory: less than 150 MiB
- Video fluidity: greater than 99%
- Time-to-First Video Frame: less than 2500 ms
- UI fluidity: target 99% or higher
- Iterations: default 3; certification mode uses 30 with 90th percentile aggregation

### Vega-Specific Path

Use the Vega-specific references when the app is React Native for Vega, uses Vega WebView, exposes `manifest.toml`, or needs official Vega KPI evidence. For non-Vega React Native TV apps, use the RN TV reference and the project's available platform profilers, then adapt the same measure-before-fix workflow.

## References

| File | Impact | Description |
|------|--------|-------------|
| [REACT_NATIVE_TV_PERFORMANCE.md](references/REACT_NATIVE_TV_PERFORMANCE.md) | CRITICAL | React Native TV optimization for renders, lists, images, concurrent rendering, and TV navigation responsiveness |
| [KPI_MEASUREMENT.md](references/KPI_MEASUREMENT.md) | CRITICAL | Vega-specific KPI Visualizer metrics, targets, commands, and report fully drawn APIs |
| [WEBVIEW_PERFORMANCE.md](references/WEBVIEW_PERFORMANCE.md) | CRITICAL | Vega WebView launch, network, rendering, cache, Web Worker, WebGL, and video guidance |
| [PROFILING_AND_RENDERING.md](references/PROFILING_AND_RENDERING.md) | HIGH | Vega Activity Monitor, Recording View, CPU profiler, Chrome DevTools, Perfetto, overdraw |

### Templates

Use [PERFORMANCE_CHECKLIST.md](assets/templates/PERFORMANCE_CHECKLIST.md) to track measurement, fixes, and verification.

### Evals

Use [evals/README.md](evals/README.md) to test trigger quality, task quality, and with-skill vs without-skill behavior.

## Problem -> Skill Mapping

| Problem | Start With |
|---------|------------|
| Slow React Native TV screen or interaction | REACT_NATIVE_TV_PERFORMANCE.md |
| Slow Vega launch or resume | KPI_MEASUREMENT.md |
| Vega TTFD is missing or `-1` | KPI_MEASUREMENT.md |
| UI jank or D-pad lag | PROFILING_AND_RENDERING.md, then platform reference |
| Slow FlatList/rails | REACT_NATIVE_TV_PERFORMANCE.md |
| Too many React renders | REACT_NATIVE_TV_PERFORMANCE.md |
| Slow WebView load | WEBVIEW_PERFORMANCE.md |
| Heavy WebView JavaScript | WEBVIEW_PERFORMANCE.md |
| High CPU or memory | PROFILING_AND_RENDERING.md |
| Rendering overdraw | PROFILING_AND_RENDERING.md |
| Video startup/playback issues | KPI_MEASUREMENT.md, then WEBVIEW_PERFORMANCE.md if WebView video |

## Workflow

1. Detect app surface: generic React Native TV, React Native for Vega, Vega WebView, mixed, or unknown.
2. Identify the symptom and target KPI: launch, UI fluidity, video fluidity, memory, CPU, or rendering.
3. Run the appropriate measurement tool on a release build when possible. For Vega, use KPI Visualizer, Activity Monitor, Recording View, and related Vega tools.
4. Inspect evidence: profiler output, KPI Visualizer output, Activity Monitor recording, flamegraph, Perfetto trace, Chrome DevTools profile, overdraw colors, or re-render logs.
5. Apply targeted fixes from the correct reference path.
6. Re-run the same measurement and compare before/after values.
7. Report symptom, baseline, root cause, fix, after-measurement, remaining risk, and official source used.

## Guardrails

- Do not optimize before establishing a baseline measurement.
- Do not compare debug-build numbers against release-build numbers.
- Do not compare before/after results from different devices, app states, scenarios, or iteration counts.
- Do not treat Vega TTFD as valid unless the app reports fully drawn when it is actually ready for user interaction.
- Do not apply WebView fixes to native React Native surfaces, or native-only fixes to WebView content, without checking app surface first.

## Official Sources

- App Performance Best Practices: https://developer.amazon.com/docs/vega/0.21/best_practices.html
- Measure App KPIs: https://developer.amazon.com/docs/vega/0.21/measure-app-kpis.html
- Performance Best Practices for Web Apps: https://developer.amazon.com/docs/vega/0.21/webview-app-performance-best-practices.html
- Improve App Performance with Concurrent Rendering: https://developer.amazon.com/docs/vega/0.21/concurrent-rendering.html
- Optimizing Flatlist Configuration: https://developer.amazon.com/docs/react-native-vega/0.72/optimizing-flatlist-configuration.html
- Monitor CPU Usage: https://developer.amazon.com/docs/vega/0.21/monitor-cpu-usage.html
- Use Chrome DevTools for App Profiling: https://developer.amazon.com/docs/vega/0.21/chrome-devtools.html
- Identify UI Rendering Issues: https://developer.amazon.com/docs/vega/0.21/ui-rendering.html
- Detect Overdraw: https://developer.amazon.com/docs/vega/0.21/detect-overdraw.html

## Attribution

Based on official React Native performance patterns plus official Vega, React Native for Vega, Vega WebView, and Vega Studio performance documentation.
