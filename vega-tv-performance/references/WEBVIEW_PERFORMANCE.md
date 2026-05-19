# Vega WebView Performance

Use this reference for Vega apps that render HTML, JavaScript, CSS, media, WebGL, or hosted content inside Vega WebView.

Primary sources:
- WebView performance best practices: https://developer.amazon.com/docs/vega/0.21/webview-app-performance-best-practices.html
- Web Worker best practices: https://developer.amazon.com/docs/vega/0.21/webview-web-workers-best-practices.html
- WebGL best practices: https://developer.amazon.com/docs/vega/0.21/webview-webgl-best-practices.html

## First Checks

Before fixing:
- Confirm WebView usage with `@amazon-devices/webview`, `<WebView>`, `webview.html`, hosted HTML, or `ReactNativeWebView`.
- Measure TTFF, TTFD, UI fluidity, memory, video fluidity, or TTFVF as appropriate.
- Use Vega KPI Visualizer plus Chrome DevTools when possible.
- Separate native wrapper issues from web content issues.

## Launch Performance

Use the native SplashScreen API for immediate visual feedback at launch.

For WebView TTFD:
- Use `useReportFullyDrawn()` after the web app has loaded and is ready for user interaction.
- In WebView, the `onLoad` callback can be a good marker only if the loaded URL represents the actual ready screen.
- Report fully drawn for warm starts when the app returns from background and is ready.
- Do not report fully drawn when the user cannot interact yet.

## Network and Server Response

Optimize startup and navigation by:
- Minimizing HTTP requests.
- Combining CSS/JavaScript files when it is logically safe.
- Removing unnecessary third-party dependencies.
- Enabling Gzip or Brotli for text assets.
- Using HTTP/2 or HTTP/3 where available.
- Reducing redirects.
- Using CDN caching and appropriate `Cache-Control` headers.
- Reducing TTFB through backend/API optimization.
- Combining API calls when appropriate and avoiding redundant requests.
- Deferring noncritical data and loading the first useful content first.

## JavaScript and Rendering

Keep startup JavaScript small:
- Execute only essential code during launch.
- Use `async` or `defer` for noncritical scripts.
- Use dynamic imports and code splitting.
- Avoid long tasks on the main thread.
- Move heavy computation off the main thread when appropriate.
- Debounce or throttle expensive input and scroll handlers.
- Use `requestAnimationFrame` for visual updates.

For smooth rendering:
- Avoid synchronous layout reads/writes in scroll handlers.
- Avoid forced reflows from repeated `offsetTop`, `scrollHeight`, or layout property access.
- Render only visible or necessary content in large scrollable surfaces.
- Prefer transform-based animations over layout-changing properties such as `top`, `left`, or `width`.

## Web Workers

Use Web Workers for computationally heavy work that would block the main thread.

Vega guidance:
- Restrict worker count based on device cores.
- Conservative formula: `navigator.hardwareConcurrency - 2`.
- Upper guideline: `(2 * navigator.hardwareConcurrency) + 1`.
- Reduce data passed between workers and the main thread.
- Use transferable objects for large data.
- Terminate unneeded workers.
- Reuse workers or worker pools.
- Cache expensive results.
- Avoid worker floods during fast navigation or image preloading.

## WebGL

Vega WebView supports WebGL 2.0 and WASM. It does not currently support WebGPU.

Optimize WebGL by:
- Avoiding canvas video; use HTML video or web video player libraries instead.
- Reducing draw calls; keep below 500 draw calls per frame when possible.
- Drawing from `requestAnimationFrame`.
- Optimizing texture sizes, compressed formats, mipmaps, and texture atlases.
- Simplifying shaders and complex algorithms.
- Using LOD, frustum culling, or occlusion culling.
- Preallocating memory and reusing objects.
- Reducing state changes.
- Avoiding blocking calls like `getError()` and `getParameter()` on the main thread.

## Video and Hardware Decode

For media-heavy WebView apps:
- Use `video` elements with hardware-supported codecs.
- Prefer H.264, H.265, VP8, or VP9 where supported by the target device.
- Avoid software-only formats that increase CPU load.
- Avoid multiple simultaneous `video` elements.
- Reuse video elements where possible.
- For MSE, ensure `MediaSource.addSourceBuffer()` codec strings match hardware-supported formats.
- Use `MediaSource.isTypeSupported()` and `HTMLVideoElement.canPlayType()` before playback setup.
- Avoid heavy CSS/WebGL animations during playback.

## Validation

After a fix:
- Re-run the same KPI Visualizer command.
- Use Chrome DevTools Performance and Network tabs for detailed web hotspots.
- Test with realistic network and CPU restrictions when reproducing in Desktop Chrome.
- Confirm TTFF, TTFD, UI fluidity, memory, video fluidity, or TTFVF improved without regressing user-visible behavior.
