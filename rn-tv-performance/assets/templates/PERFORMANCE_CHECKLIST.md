# Performance Checklist

Use this checklist during React Native TV performance investigations. Use Vega-specific KPI and profiling checks when the app targets Vega.

## Scope

- [ ] Identified app surface: generic React Native TV, React Native for Vega, Vega WebView, mixed, or unknown.
- [ ] Identified symptom: launch, UI fluidity, video, CPU, memory, rendering, network, list, or WebGL.
- [ ] Identified target device and build variant.
- [ ] Confirmed measurements are from a repeatable scenario.
- [ ] Recorded KPI iteration count, using default 3 iterations for quick checks or 30 iterations for certification-mode evidence.

## KPI Baseline

- [ ] Recorded cool start TTFF.
- [ ] Recorded warm start TTFF if relevant.
- [ ] Recorded cool start TTFD and verified report fully drawn marker.
- [ ] Recorded warm start TTFD if relevant.
- [ ] Recorded UI fluidity for navigation or scrolling.
- [ ] Recorded video fluidity and TTFVF for playback.
- [ ] Recorded foreground memory.
- [ ] Recorded background memory.
- [ ] Compared P90 values from the same iteration count before and after the fix.

## Native React Native TV

- [ ] Checked unnecessary re-renders with React DevTools or why-did-you-render in development.
- [ ] Memoized expensive stable children where evidence supports it.
- [ ] Stabilized callbacks, objects, arrays, and render functions passed to list items.
- [ ] Tuned FlatList props: `initialNumToRender`, `maxToRenderPerBatch`, `windowSize`, `getItemLayout`, and `keyExtractor`.
- [ ] Considered FlashList when list performance remains poor.
- [ ] Used thumbnail/cropped images in lists and rails.
- [ ] Applied concurrent rendering for heavy non-urgent updates.

## Vega WebView

- [ ] Used native SplashScreen API where applicable.
- [ ] Implemented TTFD marker only after real readiness.
- [ ] Minimized startup JavaScript and render-blocking scripts.
- [ ] Optimized network requests, redirects, cache headers, and server response time.
- [ ] Deferred noncritical data and code.
- [ ] Avoided forced reflows and heavy scroll handlers.
- [ ] Used Web Workers only for suitable heavy work and bounded worker count.
- [ ] Optimized WebGL draw calls, texture sizes, shaders, object reuse, and blocking calls.
- [ ] Used hardware-supported video codecs and avoided multiple simultaneous video elements.

## Profiling and Rendering

- [ ] Used KPI Visualizer for the target KPI.
- [ ] Used Activity Monitor or Recording View for CPU/memory spikes.
- [ ] Inspected flamegraphs or call trees for hot functions.
- [ ] Inspected Perfetto traces for render thread jank.
- [ ] Checked overdraw with `SHOW_OVERDRAWN=true` where rendering cost is suspected.
- [ ] Used Chrome DevTools for debug/web profiling where appropriate.

## Verification

- [ ] Re-ran the same KPI command and scenario after fixes.
- [ ] Compared before/after numbers.
- [ ] Confirmed no regression in adjacent flows.
- [ ] Confirmed UI remains responsive with D-pad navigation.
- [ ] Documented source, fix, measurement, and remaining risk.
