# React Native for Vega Performance

Use this reference for native React Native for Vega app surfaces.

Primary sources:
- App Performance Best Practices: https://developer.amazon.com/docs/vega/0.21/best_practices.html
- Concurrent Rendering: https://developer.amazon.com/docs/vega/0.21/concurrent-rendering.html
- Optimizing Flatlist Configuration: https://developer.amazon.com/docs/react-native-vega/0.72/optimizing-flatlist-configuration.html
- Investigate Component Re-rendering Issues: https://developer.amazon.com/docs/vega/0.21/investigate-component-re-render.html

## First Checks

Before changing code:
- Confirm this is a native React Native for Vega surface, not WebView content.
- Identify the user-visible symptom: launch, focus/D-pad lag, list scroll, rail navigation, animation, video, CPU, or memory.
- Measure the relevant KPI.
- Inspect React renders, JS thread, render thread, and memory before choosing a fix.

## Re-render Optimization

Use `memo`, `useCallback`, and `useMemo` when they reduce measured wasted renders.

Good candidates:
- List items.
- Buttons and tiles.
- Expensive computed props.
- Components with stable props.
- Children of screens that use concurrent rendering.

Avoid:
- Adding memoization everywhere without evidence.
- Omitting hook dependencies and creating stale closures.
- Passing inline functions, inline objects, or regenerated arrays into memoized children.

Tools:
- React DevTools Profiler with "Record why each component rendered" when available.
- `why-did-you-render` in development only. Do not ship it in production.

## Lists and Rails

Prefer virtualized lists for large rows, rails, and catalogs.

For `FlatList`:
- Tune `initialNumToRender` so the initial viewport is filled without extra work.
- Tune `maxToRenderPerBatch`; higher values reduce blanks but can block JavaScript event processing.
- Tune `windowSize`; larger values reduce blank areas but increase memory.
- Use `getItemLayout` when item size is fixed.
- Use `keyExtractor` or stable keys.
- Move `renderItem` out of JSX and wrap with `useCallback`.
- Keep item components basic and light.
- Use thumbnails/cropped assets for list items.

For `FlashList`:
- Vega supports Shopify FlashList as a performant alternative.
- Set `estimatedItemSize`.
- Account for item recycling; avoid item-local state that carries across recycled items.
- Remove unnecessary `key` props inside item components.
- Do not expect FlatList-only props such as `windowSize`, `getItemLayout`, or `maxToRenderPerBatch` to apply to FlashList.

## Images

React Native for Vega includes native caching mechanisms in its `Image` implementation.

Use:
- Cropped or thumbnail-sized images in lists and rails.
- Multiple asset sizes for different use cases.
- Detail-size images only on detail screens.

Avoid:
- Full-resolution artwork in list tiles.
- Excessive image effects in scrollable surfaces.
- Re-decoding large assets during D-pad navigation.

## Concurrent Rendering

Use React 18 concurrent rendering when heavy updates block urgent interactions.

Use `useTransition` when the component controls both urgent and non-urgent state, such as:
- Search input stays responsive while results update.
- Navigation stays responsive while a large screen update happens.
- Large list updates are lower priority than user input.

Use `useDeferredValue` when expensive work comes from props or external values that the component does not directly control.

Use `Suspense` and `lazy` for heavy components or screens that can be code-split.

Always pair concurrent rendering with memoization for expensive children, otherwise parent renders can erase the benefit.

## CPU and Memory

If CPU is high:
- Identify hot functions with Activity Monitor or CPU profiler.
- Look for repeated computations, unnecessary state updates, heavy effects, and large render trees.
- Reduce work on focus movement and D-pad handlers.

If memory is high:
- Check image sizes, mounted list window size, cached data, background state, and retained references.
- Measure foreground and background memory separately.

## Validation

After a fix:
- Re-run the same KPI command and scenario.
- Check UI fluidity stays at or above 99%.
- Re-test D-pad navigation and focus movement on the target device.
- Confirm memory did not regress.
- Capture before/after values and the code path changed.
