# Vega Shared Workspace Platform Dependencies

Implement Android TV and Apple TV support for a Vega shared workspace monorepo by replacing Vega-specific dependencies with Stock React Native equivalents.

## Prerequisites

- Completed Phase 1 analysis (see [PHASE1_ANALYSIS.md](PHASE1_ANALYSIS.md))
- Completed Phase 2 monorepo setup (see [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md))
- Vega build working in monorepo
- Root `tsconfig.json` exists

## Tools

| Tool | Version | Purpose |
|---|---|---|
| expo | ~52.0.0 | Expo SDK for TV builds |
| react-native-tvos | ~0.76.0-0 | React Native fork for TV |
| @react-native-tvos/config-tv | ~0.0.12 | TV configuration plugin |
| expo-build-properties | ~0.13.0 | Build configuration |

```bash
yarn expotv:prebuild    # Generate native projects
yarn expotv:android     # Run on Android TV
yarn expotv:ios         # Run on Apple TV
```

## Scaffold Expo TV Package

If `packages/expotv/` doesn't exist, create the structure and apply templates:

```bash
mkdir -p packages/expotv/{assets,components,constants,hooks,layouts}
mkdir -p packages/expotv/app/\(tabs\)
mkdir -p packages/expotv/assets/{fonts,images,tv_icons}
mkdir -p packages/expotv/components/navigation
mkdir -p packages/expotv/scripts
```

Apply templates from [assets/templates/](../assets/templates/):
- **package.json** — [Template](../assets/templates/expotv-package.json) | [Docs](../assets/templates/expotv-package.json.md)
- **app.json** — [Template](../assets/templates/expotv-app.json) | [Docs](../assets/templates/expotv-app.json.md)
- **metro.config.js** — [Template](../assets/templates/expotv-metro.config.js)

The expotv package typically uses a simple name (`mytvproject`) rather than scoped. Root package.json scripts reference it by package name:

```json
{
  "scripts": {
    "expotv": "yarn workspace mytvproject",
    "expotv:prebuild": "yarn workspace mytvproject run prebuild",
    "expotv:android": "yarn workspace mytvproject run android",
    "expotv:ios": "yarn workspace mytvproject run ios",
    "expotv:web": "yarn workspace mytvproject run web"
  }
}
```

The package uses Expo Router for file-based routing:
- `app/_layout.tsx` — Root layout with providers
- `app/(tabs)/_layout.tsx` — Tab navigation layout
- `app/(tabs)/index.tsx` — Home screen

## Dependency Replacements

Reference Phase 1 "Category C" dependencies. For each, find a replacement:

| Vega Package | Android/Expo Replacement | Notes |
|---|---|---|
| `@amazon-devices/react-native-kepler` | `react-native-tvos` + `@react-navigation/native` | Focus handling, TV navigation |
| `@amazon-devices/kepler-player-client` | `react-native-video` | Video playback |
| `@amazon-devices/react-native-w3cmedia` | `react-native-video` or `expo-av` | Media APIs |
| `@amazon-devices/kepler-ui-components` | Custom components | Rebuild with RN primitives |
| `@amazon-devices/kepler-file-system` | `expo-file-system` | File operations |
| `@amazon-devices/keplerscript-netmgr-lib` | `@react-native-community/netinfo` | Network state |
| `@amazon-devices/security-manager-lib` | `expo-secure-store` | Secure storage |

## Scaling Utility

Android TV renders at different resolutions than Vega (1920x1080). Add to shared package:

`packages/shared/src/utils/scaling.ts`:

```typescript
import { Dimensions, PixelRatio } from "react-native";

const { width: SCREEN_WIDTH } = Dimensions.get("window");
const BASE_WIDTH = 1920;
const WIDTH_SCALE = SCREEN_WIDTH / BASE_WIDTH;

export const scaleWidth = (size: number): number =>
  PixelRatio.roundToNearestPixel(WIDTH_SCALE * size);

export const scaleHeight = (size: number): number =>
  PixelRatio.roundToNearestPixel(WIDTH_SCALE * size);

export const scaleFontSize = (size: number): number =>
  PixelRatio.roundToNearestPixel(WIDTH_SCALE * size);
```

Export from `packages/shared/index.ts`:
```typescript
export { scaleWidth, scaleHeight, scaleFontSize } from "./src/utils/scaling";
```

On Vega (1920x1080), `WIDTH_SCALE` = 1.0 (no effect). On Android TV at 1280x720, `WIDTH_SCALE` ≈ 0.67.

Apply to all hardcoded pixel values in shared components:
```tsx
import { scaleWidth, scaleFontSize } from "@myapp/shared";

const styles = StyleSheet.create({
  card: { width: scaleWidth(320), height: scaleHeight(180), marginRight: scaleWidth(30) },
  title: { fontSize: scaleFontSize(32) },
});
```

The Expo TV package may also have its own `hooks/useScale.ts` with web support (`useScale.web.ts`).

**Reanimated limitation:** Scaling functions cannot be called inside `useAnimatedStyle` worklets. Pre-calculate scaled values outside the worklet.

## Focus State Handling

TV Focus APIs are largely the same across Vega and react-native-tvos:

| Vega Approach | Android TV Equivalent |
|---|---|
| `hasTVPreferredFocus` | Same in react-native-tvos |
| `FocusGuideView` | `TVFocusGuideView` from react-native-tvos |
| kepler-ui focus styling | `Pressable` `onFocus`/`onBlur` with state |

Example focus state pattern:
```tsx
const [isFocused, setIsFocused] = useState(false);

<Pressable
  onFocus={() => setIsFocused(true)}
  onBlur={() => setIsFocused(false)}
  style={[styles.card, isFocused && styles.cardFocused]}
>
```

## Platform Strategy Selection

| Scenario | Strategy |
|---|---|
| Significantly different implementations | File extensions (`.android.tsx`, `.kepler.tsx`) |
| Small styling differences | Inline `Platform.OS` conditionals |
| Heavy native dependencies | Screen Container pattern |

## Build Android TV

```bash
yarn expotv:prebuild
yarn expotv:android
```

## Build Apple TV

### Fix tvOS Deployment Target

`expo-build-properties` doesn't always update tvOS deployment targets. ExpoModulesCore requires tvOS 15.1+. Try building first — only apply this fix if you see deployment target errors.

Create `packages/expotv/scripts/fix-tvos-deployment.sh`:

```bash
#!/bin/bash
set -e
echo "🔧 Fixing tvOS deployment targets..."
cd "$(dirname "$0")/../ios"

APP_NAME=$(ls -d *.xcodeproj 2>/dev/null | head -1 | sed 's/.xcodeproj//')
if [ -z "$APP_NAME" ]; then
  echo "❌ No .xcodeproj found"; exit 1
fi

sed -i '' 's/TVOS_DEPLOYMENT_TARGET = 1[0-3]\.[0-4];/TVOS_DEPLOYMENT_TARGET = 15.1;/g' "${APP_NAME}.xcodeproj/project.pbxproj"
sed -i '' 's/TVOS_DEPLOYMENT_TARGET = 1[0-3]\.[0-4];/TVOS_DEPLOYMENT_TARGET = 15.1;/g' Pods/Pods.xcodeproj/project.pbxproj 2>/dev/null || true

echo "✅ tvOS deployment targets updated to 15.1"
```

```bash
chmod +x packages/expotv/scripts/fix-tvos-deployment.sh
yarn expotv:prebuild
yarn expotv:ios
```

The [expotv package.json template](../assets/templates/expotv-package.json) already chains this script into the `prebuild` command.

## Expo 52 Library Version Overrides

Some VMRP library versions must be overridden in `packages/expotv/package.json` to match Expo 52:

| Library | VMRP Version | Expo 52 Version |
|---|---|---|
| react-native-reanimated | 3.5.4 | ~3.16.1 |
| react-native-svg | 13.14.0 | ~15.8.0 |
| react-native-gesture-handler | 2.13.0 | ~2.20.2 |
| react-native-vector-icons | 9.2.0 | ^10.2.0 |
| lottie-react-native | 6.0.0-rc.1 | ^6.7.0 |
| @shopify/flash-list | 1.6.3 | ^1.7.2 |

The shared package uses standard imports. Vega resolves to its versions via VMRP, Expo TV uses the versions above.

## Verification Checklist

### Android TV
- [ ] All Vega dependencies have replacements identified
- [ ] Platform-specific files created where needed
- [ ] `yarn expotv:prebuild` succeeds
- [ ] App launches on Android TV emulator/device
- [ ] All screens render without crashes
- [ ] Navigation works
- [ ] Media playback works (if applicable)

### Apple TV
- [ ] tvOS deployment target set to 15.1+
- [ ] `yarn expotv:ios` launches on Apple TV simulator
- [ ] All screens render without crashes
- [ ] Navigation works
- [ ] Media playback works (if applicable)

## Common Issues

| Issue | Solution |
|---|---|
| Kotlin version mismatch | Add `expo-build-properties` with `kotlinVersion: "1.9.25"` |
| tvOS deployment target error | Run `fix-tvos-deployment.sh` script |
| Reanimated babel error | Add `react-native-reanimated/plugin` to babel.config.js |
| Missing icon | Create `./assets/icon.png` or update path in app.json |
| Library incompatibility | Use Expo 52 compatible versions from table above |
| Expo prebuild fails with workspace deps | Run `yarn install` from root before prebuild |
| iOS pod install fails in monorepo | Add node_modules paths to Podfile's `react_native_post_install` |

## Related Documents

- Analysis: [PHASE1_ANALYSIS.md](PHASE1_ANALYSIS.md)
- Monorepo conversion: [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)
- Templates: [assets/templates/](../assets/templates/)
