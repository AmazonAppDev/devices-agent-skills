# KPI Measurement

Use this reference before making performance changes. Establish a baseline, choose the right KPI, and re-run the same measurement after each fix.

Primary source: https://developer.amazon.com/docs/vega/0.21/measure-app-kpis.html

## Required Baseline

Before optimizing, record:
- App surface: native React Native for Vega, Vega WebView, or mixed.
- Build variant. Prefer release for publish-readiness measurements.
- Device type and whether it is a physical device or virtual device.
- App name from the default interactive component in `manifest.toml`.
- Scenario: cool start, warm start, UI interaction, video playback, foreground memory, or background memory.
- KPI command and output.

## Official KPI Targets

| KPI | Scenario | Target |
|-----|----------|--------|
| TTFF | Cool start app launch | less than 1.5 s |
| TTFF | Warm start app launch | less than 0.5 s |
| TTFD | Cool start app launch | less than 8.0 s |
| TTFD | Warm start app launch | less than 1.5 s |
| Foreground Memory | App active | less than 400 MiB |
| Background Memory | App backgrounded | less than 150 MiB |
| Video Fluidity | Video playback | greater than 99% |
| TTFVF | Video playback startup | less than 2500 ms |
| UI Fluidity | UI interaction | 99% or higher |

## Commands

Default cool-start latency:

```bash
vega exec perf kpi-visualizer --app-name=<interactive-component-id>
```

Set an explicit iteration count:

```bash
vega exec perf kpi-visualizer --app-name=<interactive-component-id> --iterations <count>
```

UI fluidity:

```bash
vega exec perf kpi-visualizer --app-name=<interactive-component-id> --kpi ui-fluidity --test-scenario <scenario.py>
```

Video fluidity:

```bash
vega exec perf kpi-visualizer --app-name=<interactive-component-id> --kpi video-fluidity --test-scenario <scenario.py>
```

Foreground memory:

```bash
vega exec perf kpi-visualizer --app-name=<interactive-component-id> --kpi foreground-memory --test-scenario <scenario.py>
```

Supported scenarios include:
- `cool-start-latency`
- `warm-start-latency`
- `ui-fluidity`
- `foreground-memory`
- `background-memory`
- `video-fluidity`

## Iterations and Aggregation

Official Vega KPI Visualizer guidance says:
- The visualizer performs three iterations for selected KPIs by default.
- The visualizer window shows the P90 (90th percentile) value calculated from three test iterations.
- The CLI supports `--iterations <number>` to set how many times to run the test.
- Certification mode uses 30 iterations with 90th percentile aggregation.

Use the default 3 iterations for quick local investigation. Use more iterations when results are noisy, when validating a risky optimization, or when preparing release/certification evidence. Keep the iteration count, device, build variant, scenario, and app state the same when comparing before/after results.

## Fully Drawn Marker

TTFD requires the app to report when it is ready for user interaction.

Use `@amazon-devices/kepler-performance-api` and `useReportFullyDrawn()` when the app has completed the work required for user interaction.

Important rules:
- Report after the first render only when required async work is complete.
- Report again for warm launch when the app returns from background to foreground and is ready.
- If TTFD shows `-1`, check whether the app failed to call the Report Fully Drawn API.
- Do not report too early just to improve the metric; the marker must match real readiness.

## Micro KPIs

Use micro KPIs to explain TTFD:
- JavaScript bundle load time.
- Network calls time.
- Other app-defined startup stages.

When TTFD is high, split startup work into measured phases before optimizing.

## Measurement Quality

Good measurement:
- Uses repeatable app state.
- Records the iteration count.
- Uses a scenario that matches real user behavior.
- Uses the same command before and after the fix.
- Captures launch, foreground, background, and playback where relevant.
- Notes unavailable data and why it is missing.

Avoid:
- Comparing debug builds to release builds.
- Comparing different devices or scenarios.
- Optimizing without a baseline.
- Treating one run as conclusive when results are noisy.
