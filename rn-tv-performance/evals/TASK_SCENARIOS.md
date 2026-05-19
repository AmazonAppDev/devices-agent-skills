# Task Scenarios

Run each scenario with and without `rn-tv-performance`. Score both outputs using [SCORING_RUBRIC.md](SCORING_RUBRIC.md).

## Scenario 1: Launch KPI Baseline

Prompt:

```text
Our React Native TV app takes a long time to launch. Tell me how to establish a baseline before changing code, and explain what extra official KPI path to use if the app targets Vega.
```

Expected behavior:
- Starts with app surface and platform detection.
- Establishes repeatable launch measurements before fixes.
- Mentions cool and warm start where the platform exposes those metrics.
- For Vega, uses KPI Visualizer, TTFF/TTFD targets, `useReportFullyDrawn()`, and real readiness.
- Avoids premature code optimization.

## Scenario 2: Missing TTFD

Prompt:

```text
KPI Visualizer reports TTFD as -1 for our Vega app. What is likely wrong and how should we fix and verify it?
```

Expected behavior:
- Identifies missing Report Fully Drawn marker.
- Recommends `@amazon-devices/kepler-performance-api` and `useReportFullyDrawn()`.
- Explains cool and warm launch readiness.
- Re-runs the same KPI command after the fix.

## Scenario 3: Slow Native Rails

Prompt:

```text
A React Native TV home page has large horizontal content rails. D-pad movement stutters and memory grows while scrolling. Suggest a performance investigation and fix plan.
```

Expected behavior:
- Treats this as native React Native TV.
- Measures UI responsiveness/fluidity and memory using the best available platform tools.
- Checks re-renders, list configuration, image sizes, and render functions.
- Covers FlatList/FlashList tradeoffs.
- Adds Vega KPI Visualizer guidance if the target is Vega.
- Re-measures same scenario.

## Scenario 4: WebView Startup

Prompt:

```text
A Vega WebView app shows a blank screen for several seconds before the home page appears. It loads several scripts and API calls at startup. What should we do?
```

Expected behavior:
- Treats this as WebView.
- Uses native SplashScreen and TTFD marker guidance.
- Optimizes requests, compression, caching, redirects, async/defer scripts, code splitting, and noncritical data.
- Measures with KPI Visualizer and Chrome DevTools.

## Scenario 5: Web Workers

Prompt:

```text
Our Vega WebView app uses many Web Workers to preload images when users move quickly through a carousel. The UI freezes. Diagnose this.
```

Expected behavior:
- Explains worker floods and main-thread response overhead.
- Uses worker count guidance based on `navigator.hardwareConcurrency`.
- Recommends batching, transferable objects, pooling, termination, and caching.
- Measures UI fluidity before/after.

## Scenario 6: WebGL and Video

Prompt:

```text
A Vega WebView app uses WebGL animations over video playback and video fluidity is below 99%. What should we inspect?
```

Expected behavior:
- Measures video fluidity and TTFVF.
- Checks hardware-supported codecs and video element usage.
- Avoids canvas video for WebGL.
- Reduces draw calls, texture sizes, shaders, and GPU contention.
- Re-tests playback scenario.

## Scenario 7: CPU Hot Functions

Prompt:

```text
Activity Monitor shows CPU spikes during app launch. How should I use Vega tooling to find and prioritize fixes?
```

Expected behavior:
- Uses Activity Monitor, launch mode recording, Recording View, hot functions, flamegraphs, call tree.
- Mentions release variant for hot functions.
- Uses source maps where needed.
- Prioritizes high self/total CPU time in app code.

## Scenario 8: Overdraw

Prompt:

```text
Our Vega app has jank on a dense detail screen with layered backgrounds and translucent overlays. How can we detect and fix overdraw?
```

Expected behavior:
- Uses `SHOW_OVERDRAWN=true`.
- Explains color meanings.
- Recommends removing unnecessary backgrounds, flattening view hierarchy, and reducing transparency.
- Re-runs UI fluidity or rendering validation.
