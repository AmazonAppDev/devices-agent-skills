# Profiling and Rendering

Use this reference to choose Vega Studio and platform tools for CPU, memory, rendering, and jank investigations.

Primary sources:
- Monitor CPU Usage: https://developer.amazon.com/docs/vega/0.21/monitor-cpu-usage.html
- Chrome DevTools for App Profiling: https://developer.amazon.com/docs/vega/0.21/chrome-devtools.html
- Identify UI Rendering Issues: https://developer.amazon.com/docs/vega/0.21/ui-rendering.html
- Detect Overdraw: https://developer.amazon.com/docs/vega/0.21/detect-overdraw.html

## Tool Selection

Use:
- **Vega App KPI Visualizer** for TTFF, TTFD, UI fluidity, video fluidity, and memory KPIs.
- **Activity Monitor** for real-time CPU and memory graphs on connected devices.
- **Recording View** for timelines, traces, hot functions, flamegraphs, and call trees.
- **CPU Profiler on App Launch** for launch bottlenecks.
- **Chrome DevTools** for React Native for Vega debug profiling and WebView web profiling.
- **Perfetto traces** for render thread and system-level jank analysis.
- **Overdraw detection** for unnecessary GPU work from repeated pixel rendering.

## Activity Monitor

Use Activity Monitor to observe:
- CPU utilization over time.
- Memory usage over time.
- App crashes and restart gaps.
- Correlation between user actions and spikes.

Important:
- Vega Virtual Device does not support Vega Studio Performance Tools.
- Release variant is required for some profiling data such as hot functions.
- CPU utilization of 400% means full usage across four cores.

## Recording View

Use Recording View to inspect:
- Timeline windows.
- Lifecycle traces: launch, foreground, background, crash.
- Thread states.
- Hot functions.
- Flamegraphs.
- Call tree sorted by total or self CPU time.

Prioritize:
- Wide flamegraph nodes.
- High self CPU time in app code.
- Hot functions that align with KPI drops.
- JS thread, UI thread, or render thread contention.

## CLI CPU Profiling

Use CPU profiling with Activity Monitor when you need hot functions and source mapping.

```bash
vega exec perf activity-monitor \
  --record-cpu-profiling \
  --app-name=<interactive-component-id> \
  --sourcemap-file-path=<JS Source Map File Path in kepler-build directory>
```

Generated output can include:
- CPU and memory utilization.
- Process state.
- Hot functions summary.
- Trace event file for Chrome DevTools.

## UI Rendering Jank

Jank means stuttering or lag in UI rendering and input response.

To investigate:
1. Run a UI fluidity test in KPI Visualizer.
2. Locate drops in the fluidity graph.
3. Open the CPU profile graph and flamegraph near the drop.
4. Inspect Perfetto traces.
5. Examine `Toolkit/Render thread` for long or recurring events.

Common causes:
- Frame size mismatch with display resolution.
- Frame overdraw.
- Heavy render thread work.
- Heavy JavaScript work during interactions.
- Expensive layout or image decode during navigation.

## Overdraw Detection

Overdraw means rendering the same pixel multiple times in one frame.

Enable overdraw detection by configuring launch options with:

```text
SHOW_OVERDRAWN=true
```

Color guide:
- True color: no overdraw.
- Blue: overdrawn 1 time.
- Green: overdrawn 2 times.
- Pink: overdrawn 3 times.
- Red: overdrawn 4 or more times.

Fixes:
- Remove unnecessary backgrounds.
- Flatten the view hierarchy.
- Reduce transparency.
- Avoid stacked full-screen overlays when not needed.

## Chrome DevTools

Use Chrome DevTools:
- In Debug builds for React Native for Vega profiling.
- For WebView web content profiling with Performance and Network tabs.
- With source maps where available.

Do not treat debug performance as publish-ready. Use release builds and Vega performance tools for final validation.

## Custom Tracing

React Native Systrace can add custom trace markers for suspected expensive code paths.

Use sparingly:
- Traces can add overhead.
- Over-instrumentation can create false positives.
- Add markers only around code paths being investigated.

## Report Format

For each performance finding, include:
- Symptom.
- KPI and baseline.
- Tool used.
- Evidence file or observation.
- Suspected root cause.
- Code or asset fix.
- After-measurement.
- Remaining risk.
